"""
File: python/SHE_PPT/she_frame_stack.py

Created on: 05/03/18
"""

__updated__ = "2021-08-13"

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from copy import deepcopy
import os.path

from astropy import table
from astropy.io import fits
import astropy.wcs

import numpy as np

from . import logging
from . import products
from .constants.fits import MASK_TAG, SCI_TAG, NOISEMAP_TAG
from .file_io import read_listfile, read_xml_product, find_file, SheFileReadError
from .she_frame import SHEFrame
from .she_image import SHEImage
from .she_image_stack import SHEImageStack
from .table_formats.mer_final_catalog import tf as mfc_tf, initialise_mer_final_catalog
from .utility import find_extension


logger = logging.getLogger(__name__)


class SHEFrameStack():
    """Structure containing all needed data shape measurement, represented as a list of SHEFrames for
    detector image data, a stacked image, a list of PSF images and catalogues, and a detections
    catalogue.

    Attributes
    ----------
    exposures : list<SHEImage>
        List of SHEImage objects representing the different exposures
    stacked_image : SHEImage
        The stacked image
    bulge_psf_images : list<SHEImage>
        List of bulge PSF images
    disk_psf_images : list<SHEImage>
        List of disk PSF images
    psf_catalogues : list<astropy.table.Table>
        List of PSF catalogues
    detections_catalogues : astropy.table.Table
        Detections catalogue, provided by MER

    """

    exposures = None
    exposure_products = None
    psf_products = None

    stacked_image = None
    stacked_image_product = None

    detections_catalogue = None
    detections_catalogue_products = None

    object_id_list_product = None

    stack_pixel_size_ratio = 1

    # File references and info
    _stacked_data_filename = None
    _stacked_data_hdu = None

    _stacked_noisemap_filename = None
    _stacked_noisemap_hdu = None

    _stacked_mask_filename = None
    _stacked_mask_hdu = None

    _stacked_bkg_filename = None
    _stacked_bkg_hdu = None

    _stacked_wgt_filename = None
    _stacked_wgt_hdu = None

    _stacked_seg_filename = None
    _stacked_seg_hdu = None

    # Options
    _images_loaded = False

    def __init__(self, exposures, stacked_image, detections_catalogue):
        """
        Parameters
        ----------
        exposures : list<SHEImage>
            List of SHEImage objects representing the different exposures
        stacked_image : SHEImage
            The stacked image
        detections_catalogue : astropy.table.Table
            Detections catalogue, provided by MER

        """

        self.exposures = exposures
        self.exposure_products = None
        self.psf_products = None

        self.stacked_image = stacked_image
        self.stacked_image_product = None

        self.detections_catalogue = detections_catalogue
        self.detections_catalogue_products = None

        self.object_id_list_product = None

        # Might have to manually calculate this later
        self.stack_pixel_size_ratio = 1

        # Set the detections catalogue to index by ID
        if self.detections_catalogue is not None:
            self.detections_catalogue.add_index(mfc_tf.ID)

    @property
    def exposures(self):
        return self._exposures

    @exposures.setter
    def exposures(self, exposures):
        self._exposures = exposures

        # Set this as the parent frame stack for each exposure
        for exposure in self._exposures:
            if exposure is not None:
                exposure.parent_frame_stack = self

    @exposures.deleter
    def exposures(self):
        for exposure in self._exposures:
            del exposure
        del self._exposures

    @property
    def exposure_products(self):
        return self._exposure_products

    @exposure_products.setter
    def exposure_products(self, exposure_products):
        self._exposure_products = exposure_products

    @exposure_products.deleter
    def exposure_products(self):
        for exposure in self._exposure_products:
            del exposure
        del self._exposure_products

    @property
    def psf_products(self):
        return self._psf_products

    @psf_products.setter
    def psf_products(self, psf_products):
        self._psf_products = psf_products

    @psf_products.deleter
    def psf_products(self):
        for exposure in self._psf_products:
            del exposure
        del self._psf_products

    @property
    def exposure_segmentation_products(self):
        return self._exposure_segmentation_products

    @exposure_segmentation_products.setter
    def exposure_segmentation_products(self, exposure_segmentation_products):
        self._exposure_segmentation_products = exposure_segmentation_products

    @exposure_segmentation_products.deleter
    def exposure_segmentation_products(self):
        for exposure in self._exposure_segmentation_products:
            del exposure
        del self._exposure_segmentation_products

    @property
    def stacked_image(self):
        return self._stacked_image

    @stacked_image.setter
    def stacked_image(self, stacked_image):
        self._stacked_image = stacked_image

        if self._stacked_image is not None:
            # Set this as the parent frame stack for the stacked image
            self._stacked_image.parent_frame_stack = self
            self._stacked_image.parent_frame = None

    @stacked_image.deleter
    def stacked_image(self):
        del self._stacked_image

    @property
    def stacked_image_product(self):
        return self._stacked_image_product

    @stacked_image_product.setter
    def stacked_image_product(self, stacked_image_product):
        self._stacked_image_product = stacked_image_product

    @stacked_image_product.deleter
    def stacked_image_product(self):
        del self._stacked_image_product

    @property
    def stacked_segmentation_product(self):
        return self._stacked_segmentation_product

    @stacked_segmentation_product.setter
    def stacked_segmentation_product(self, stacked_segmentation_product):
        self._stacked_segmentation_product = stacked_segmentation_product

    @stacked_segmentation_product.deleter
    def stacked_segmentation_product(self):
        del self._stacked_segmentation_product

    @property
    def detections_catalogue(self):
        return self._detections_catalogue

    @detections_catalogue.setter
    def detections_catalogue(self, detections_catalogue):
        self._detections_catalogue = detections_catalogue

    @detections_catalogue.deleter
    def detections_catalogue(self):
        del self._detections_catalogue

    @property
    def detections_catalogue_products(self):
        return self._detections_catalogue_products

    @detections_catalogue_products.setter
    def detections_catalogue_products(self, detections_catalogue_products):
        self._detections_catalogue_products = detections_catalogue_products

    @detections_catalogue_products.deleter
    def detections_catalogue_products(self):
        for detections_catalogue_product in self._detections_catalogue_products:
            del detections_catalogue_product
        del self._detections_catalogue_products

    @property
    def object_id_list_product(self):
        return self._object_id_list_product

    @object_id_list_product.setter
    def object_id_list_product(self, object_id_list_product):
        self._object_id_list_product = object_id_list_product

    @object_id_list_product.deleter
    def object_id_list_product(self):
        del self._object_id_list_product

    def __eq__(self, rhs):
        """Equality test for SHEFrame class.
        """

        def neq(lhs, rhs):
            try:
                return bool(lhs != rhs)
            except ValueError:
                return (lhs != rhs).any()

        def list_neq(lhs, rhs):

            if lhs is None and rhs is None:
                return False
            if (lhs is None) != (rhs is None):
                return True

            if len(lhs) != len(rhs):
                return True
            for i in range(len(lhs)):
                if lhs[i] != rhs[i]:
                    return True
            return False

        if list_neq(self.exposures, rhs.exposures):
            return False
        if neq(self.stacked_image, rhs.stacked_image):
            return False
        if neq(self.detections_catalogue, rhs.detections_catalogue):
            return False
        if neq(self.stack_pixel_size_ratio, rhs.stack_pixel_size_ratio):
            return False

        return True

    def extract_galaxy_wcs_stack(self, gal_id, *args, **kwargs):
        """Extracts a WCS-only postage stamp centred on a given galaxy in the detections tables, indexed by its ID.

           Parameters
           ----------
           gal_id : int
               The galaxy's unique ID
           *args, **kwargs
               Other arguments and keyword arguments are forwarded to extract_stamp_stack()

            Return
           ------
           stamp_stack : SHEImageStack
        """

        # Need to put this in a try block in case the index wasn't properly set
        try:
            row = self.detections_catalogue.loc[gal_id]
        except ValueError as e:
            if "Cannot create TableLoc object with no indices" not in str(e):
                raise
            self.detections_catalogue.add_index(mfc_tf.ID)
            row = self.detections_catalogue.loc[gal_id]

        x_world = row[mfc_tf.gal_x_world]
        y_world = row[mfc_tf.gal_y_world]

        return self.extract_wcs_stamp_stack(x_world, y_world, *args, **kwargs)

    def extract_galaxy_stack(self, gal_id, width, *args, **kwargs):
        """Extracts a postage stamp centred on a given galaxy in the detections tables, indexed by its ID.

           Parameters
           ----------
           gal_id : int
               The galaxy's unique ID
           width : int
               The desired width of the postage stamp in pixels of the exposures
           *args, **kwargs
               Other arguments and keyword arguments are forwarded to extract_stamp_stack()

            Return
           ------
           stamp_stack : SHEImageStack
        """

        # Need to put this in a try block in case the index wasn't properly set
        try:
            row = self.detections_catalogue.loc[gal_id]
        except ValueError as e:
            if "Cannot create TableLoc object with no indices" not in str(e):
                raise
            self.detections_catalogue.add_index(mfc_tf.ID)
            row = self.detections_catalogue.loc[gal_id]

        x_world = row[mfc_tf.gal_x_world]
        y_world = row[mfc_tf.gal_y_world]

        return self.extract_stamp_stack(x_world, y_world, width, *args, **kwargs)

    def extract_psf_stacks(self, gal_id, make_stacked_psf=False, keep_header=False):
        """Extracts bulge and disk PSF stacks for a given galaxy in the detections catalogue.

           Parameters
           ----------
           gal_id : int
               The galaxy's unique ID
           make_stacked_psf : bool
               If True, will create a stacked PSF through simple summation. Default False.
           keep_header : bool
               If True, the PSF images' headers will be copied to the stamps. Default False.

            Return
           ------
           bulge_psf_stack : SHEImageStack
           disk_psf_stack : SHEImageStack
        """

        bulge_psf_stamps = []
        disk_psf_stamps = []

        for exposure in self.exposures:

            bulge_psf_stamp, disk_psf_stamp = exposure.extract_psf(
                gal_id, keep_header=keep_header)

            bulge_psf_stamps.append(bulge_psf_stamp)
            disk_psf_stamps.append(disk_psf_stamp)

        stacked_bulge_psf = None
        stacked_disk_psf = None

        # Make the stack if desired
        if make_stacked_psf:

            for x in range(len(self.exposures)):

                bulge_psf_stamp = bulge_psf_stamps[x]
                disk_psf_stamp = disk_psf_stamps[x]

                if bulge_psf_stamp is not None:

                    if stacked_bulge_psf is None:
                        stacked_bulge_psf = deepcopy(bulge_psf_stamp)
                    else:
                        stacked_bulge_psf.data += bulge_psf_stamp.data

                    if stacked_disk_psf is None:
                        stacked_disk_psf = deepcopy(disk_psf_stamp)
                    else:
                        stacked_disk_psf.data += disk_psf_stamp.data

            # Normalize stacked PSFs
            if stacked_bulge_psf is not None:
                stacked_bulge_psf.data /= stacked_bulge_psf.data.sum()
            if stacked_disk_psf is not None:
                stacked_disk_psf.data /= stacked_disk_psf.data.sum()

        # Construct the stacks
        bulge_psf_stack = SHEImageStack(stacked_image=stacked_bulge_psf,
                                        exposures=bulge_psf_stamps,
                                        parent_frame_stack=self)
        disk_psf_stack = SHEImageStack(stacked_image=stacked_disk_psf,
                                       exposures=disk_psf_stamps,
                                       parent_frame_stack=self)

        return bulge_psf_stack, disk_psf_stack

    def extract_wcs_stamp_stack(self, x_world, y_world, none_if_out_of_bounds=False, extract_stacked_stamp=True,
                                extract_exposure_stamps=True):
        """Extracts an "empty" postage stamp centred on the provided sky co-ordinates, which only contains WCS
           information but otherwise has the same interface as a SHEImage, for each exposure and the stacked
           image.

           Parameters
           ----------
           x_world : float
               The x sky co-ordinate (R.A.)
           y_world : float
               The y sky co-ordinate (Dec.)
           none_if_out_of_bounds : bool
               Set this to True if you want this method to return None if the stamp is entirely out of bounds of the image.
               By default, this is set to False, which means it will instead return an entirely masked stack in that case.
           extract_stacked_stamp : bool
               If set to False, the stamp from the stacked image won't be extracted (and will be set to None)
           extract_exposure_stamps : bool
               If set to False, the stamps from the exposure images won't be extracted (and will all be set to None)

           Return
           ------
           stamp_stack : SHEImageStack
        """

        # Extract from the stacked image first

        if extract_stacked_stamp and self.stacked_image is not None:

            stacked_image_x, stacked_image_y = self.stacked_image.world2pix(
                x_world, y_world)

            stacked_image_wcs_stamp = self.stacked_image.extract_wcs_stamp(x=stacked_image_x,
                                                                           y=stacked_image_y,
                                                                           none_if_out_of_bounds=none_if_out_of_bounds)

            # Return None if none_if_out_of_bounds and out of bounds of stacked
            # image
            if none_if_out_of_bounds and stacked_image_wcs_stamp is None:
                return None
        else:
            stacked_image_wcs_stamp = None

        # Get the stamps for each exposure

        exposure_wcs_stamps = []
        for exposure in self.exposures:
            if extract_exposure_stamps and exposure is not None:
                exposure_wcs_stamps.append(exposure.extract_wcs_stamp(x_world=x_world,
                                                                      y_world=y_world,))
            else:
                exposure_wcs_stamps.append(None)

        # Create and return the stamp stack

        stamp_stack = SHEImageStack(stacked_image=stacked_image_wcs_stamp,
                                    exposures=exposure_wcs_stamps,
                                    x_world=x_world,
                                    y_world=y_world,
                                    parent_frame_stack=self)

        return stamp_stack

    def extract_stamp_stack(self, x_world, y_world, width, height=None, x_buffer=0, y_buffer=0, keep_header=False,
                            none_if_out_of_bounds=False, extract_stacked_stamp=True, extract_exposure_stamps=True):
        """Extracts a postage stamp centred on the provided sky co-ordinates, by using each detector's WCS
           to determine which (if any) it lies on. If x/y_buffer >0, it will also extract from a detector if
           the position is within this many pixels of the edge of it.

           Parameters
           ----------
           x_world : float
               The x sky co-ordinate (R.A.)
           y_world : float
               The y sky co-ordinate (Dec.)
           width : int
               The desired width of the postage stamp in pixels of the exposures
           height : int
               The desired height of the postage stamp in pixels of the exposures (default = width)
           x_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, x-dimension
           y_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, y-dimension
           keep_header : bool
               If True, will copy the detector's header to each stamp's
           none_if_out_of_bounds : bool
               Set this to True if you want this method to return None if the stamp is entirely out of bounds of the image.
               By default, this is set to False, which means it will instead return an entirely masked stack in that case.
           extract_stacked_stamp : bool
               If set to False, the stamp from the stacked image won't be extracted (and will be set to None)
           extract_exposure_stamps : bool
               If set to False, the stamps from the exposure images won't be extracted (and will all be set to None)

           Return
           ------
           stamp_stack : SHEImageStack
        """

        # Extract from the stacked image first

        if extract_stacked_stamp and self.stacked_image is not None:
            stack_stamp_width = self.stack_pixel_size_ratio * width
            if height is None:
                stack_stamp_height = None
            else:
                stack_stamp_height = self.stack_pixel_size_ratio * height

            stacked_image_x, stacked_image_y = self.stacked_image.world2pix(
                x_world, y_world)

            if self._images_loaded:
                stacked_image_stamp = self.stacked_image.extract_stamp(x=stacked_image_x,
                                                                       y=stacked_image_y,
                                                                       width=stack_stamp_width,
                                                                       height=stack_stamp_height,
                                                                       keep_header=keep_header,
                                                                       none_if_out_of_bounds=none_if_out_of_bounds)
            else:
                stacked_image_stamp = self.stacked_image.extract_stamp(x=stacked_image_x,
                                                                       y=stacked_image_y,
                                                                       width=stack_stamp_width,
                                                                       height=stack_stamp_height,
                                                                       keep_header=keep_header,
                                                                       none_if_out_of_bounds=none_if_out_of_bounds,
                                                                       data_filename=self._stacked_data_filename,
                                                                       data_hdu=self._stacked_data_hdu,
                                                                       noisemap_filename=self._stacked_noisemap_filename,
                                                                       noisemap_hdu=self._stacked_noisemap_hdu,
                                                                       mask_filename=self._stacked_mask_filename,
                                                                       mask_hdu=self._stacked_mask_hdu,
                                                                       bkg_filename=self._stacked_bkg_filename,
                                                                       bkg_hdu=self._stacked_bkg_hdu,
                                                                       wgt_filename=self._stacked_wgt_filename,
                                                                       wgt_hdu=self._stacked_wgt_hdu,
                                                                       seg_filename=self._stacked_seg_filename,
                                                                       seg_hdu=self._stacked_seg_hdu)

            # Return None if none_if_out_of_bounds and out of bounds of stacked
            # image
            if none_if_out_of_bounds and stacked_image_stamp is None:
                return None
        else:
            stacked_image_stamp = None

        # Get the stamps for each exposure

        exposure_stamps = []
        for exposure in self.exposures:
            if extract_exposure_stamps and exposure is not None:
                exposure_stamps.append(exposure.extract_stamp(x_world=x_world,
                                                              y_world=y_world,
                                                              width=width,
                                                              height=height,
                                                              x_buffer=x_buffer,
                                                              y_buffer=y_buffer,
                                                              keep_header=keep_header))
            else:
                exposure_stamps.append(None)

        # Create and return the stamp stack

        stamp_stack = SHEImageStack(stacked_image=stacked_image_stamp,
                                    exposures=exposure_stamps,
                                    x_world=x_world,
                                    y_world=y_world,
                                    parent_frame_stack=self)

        return stamp_stack

    def get_fov_coords(self, x_world, y_world, x_buffer=0, y_buffer=0, none_if_out_of_bounds=False,
                       return_det_coords_too=False):
        """ Calculates the Field-of-View (FOV) co-ordinates of a given sky position for each exposure, and
            returns a list of (fov_x, fov_y) tuples. If the position isn't present in a given exposure, None will be
            returned in that list index.

            Parameters
            ----------
            x_world : float
                The x sky co-ordinate (R.A.)
            y_world : float
                The y sky co-ordinate (Dec.)
            x_buffer : int
                The size of the buffer region in pixels around a detector to get the co-ordinate from, x-dimension
            y_buffer : int
                The size of the buffer region in pixels around a detector to get the co-ordinate from, y-dimension
            none_if_out_of_bounds : bool
                Set this to True if you want this method to return None if the position is entirely out of bounds of
                the image. By default, this is set to False, which means it will instead return a list of Nones in
                that case instead.
            return_det_coords_too : bool
                If true return namedtuple of x_fov, y_fov, detno_x, detno_y, x_det, y_det


            Return
            ------
            fov_coords_list : list<tuple<float,float> or None>
                A list of (fov_x, fov_y) tuples if present in an exposure, or None if not present.
        """

        # Get the positions for each exposure
        found = False
        fov_coords_list = []
        for exposure in self.exposures:
            fov_coords = exposure.get_fov_coords(x_world=x_world,
                                                 y_world=y_world,
                                                 x_buffer=x_buffer,
                                                 y_buffer=y_buffer,
                                                 return_det_coords_too=return_det_coords_too)
            if fov_coords is not None:
                found = True
            fov_coords_list.append(fov_coords)

        # Return the resulting list (or None if not found and desired)
        if none_if_out_of_bounds and not found:
            fov_coords_list = None
        return fov_coords_list

    @classmethod
    def _read_product_extension(cls, product_filename, tags=None, workdir=".", dtype=None,
                                filetype="science", load_images=True, **kwargs):

        product = read_xml_product(os.path.join(workdir, product_filename))

        # Check it's the right type if necessary
        if dtype is not None and not isinstance(product, dtype):
            raise ValueError(
                "Data image product from " + product_filename + " is invalid type.")

        if filetype == "background":
            qualified_filename = os.path.join(
                workdir, product.get_bkg_filename())
        elif filetype == "weight":
            qualified_filename = os.path.join(
                workdir, product.get_psf_filename())
        else:
            qualified_filename = os.path.join(
                workdir, product.get_data_filename())
        hdulist = fits.open(
            qualified_filename, **kwargs)

        if tags is None:

            header = hdulist[0].header

            if load_images:
                data = hdulist[0].data.transpose()
            else:
                data = None
            hdu_indices = 0
        else:
            if load_images:
                data = []
            else:
                data = None
            hdu_indices = []
            for tag in tags:
                extension = find_extension(hdulist, tag)
                if load_images:
                    data.append(hdulist[extension].data.transpose())
                hdu_indices.append(extension)
            # Return the header for the first HDU in the tags
            header = hdulist[hdu_indices[0]].header

        return product, header, data, qualified_filename, hdu_indices

    @classmethod
    def _read_file_extension(cls, filename, tags=None, workdir=".", dtype=None, **kwargs):

        hdulist = fits.open(
            os.path.join(workdir, filename), **kwargs)

        header = hdulist[0].header

        if tags is None:
            data = hdulist[0].data.transpose()
        else:
            data = []
            for tag in tags:
                extension = find_extension(hdulist, tag)
                data.append(hdulist[extension].data.transpose())

        return header, data

    @staticmethod
    def __load_detections_catalogue(detections_listfile_filename, workdir, save_products, object_id_list):
        try:
            detections_catalogue_products = None
            detections_filenames = read_listfile(find_file(detections_listfile_filename, path=workdir))
            # Load each table in turn and combine them
            detections_catalogues = []
            if save_products:
                detections_catalogue_products = []
            for detections_product_filename in detections_filenames:
                detections_product = read_xml_product(os.path.join(workdir, detections_product_filename))
                if save_products:
                    detections_catalogue_products.append(detections_product)
                logger.debug("DP: %s, %s, %s",
                             workdir,
                             detections_product_filename,
                             detections_product.get_data_filename())
                detections_catalogue = table.Table.read(
                    os.path.join(workdir, detections_product.get_data_filename()))
                detections_catalogues.append(detections_catalogue)
            if object_id_list is None:
                # If we have no object id list, stack them all
                # Conflicts are expected
                detections_catalogue = table.vstack(detections_catalogues,
                                                    metadata_conflicts="silent")
            else:
                rows_to_use = []
                # loop over detections_catalog and make list of indices not in our object_id list
                for cat in detections_catalogues:
                    for row in cat:
                        if row[mfc_tf.ID] in object_id_list:
                            rows_to_use.append(row)

                detections_catalogue = initialise_mer_final_catalog()
                for key in detections_catalogues[0].meta:
                    if key in detections_catalogue.meta:
                        detections_catalogue.meta[key] = detections_catalogues[0].meta[key]

                for row in rows_to_use:
                    detections_catalogue.add_row()
                    new_row = detections_catalogue[-1]
                    for key in row.colnames:
                        if key in new_row.colnames:
                            try:
                                new_row[key] = row[key]
                            except np.ma.core.MaskError as e:
                                logger.warning("Masked element for column %s cannot be added "
                                               "to table; default value will be used.", str(key))
                # If we do have an object id list, construct a new table with just the desired rows
                logger.info("Finished pruning list of galaxy objects to loop over")
        except SheFileReadError as e:
            logger.warning(str(e))
            # See if it's just a single catalogue, which we can handle
            detections_product = read_xml_product(os.path.join(workdir, detections_listfile_filename))
            detections_catalogue = table.Table.read(
                os.path.join(workdir, detections_product.Data.DataStorage.DataContainer.FileName))
        return detections_catalogue, detections_catalogue_products

    @staticmethod
    def read_or_none(listfile_filename, workdir):
        if listfile_filename is None:
            return None
        return read_listfile(os.path.join(workdir, listfile_filename))

    @staticmethod
    def index_or_none(filenames, index):
        if filenames is None:
            return None
        return filenames[index]

    @classmethod
    def read(cls,
             exposure_listfile_filename=None,
             seg_listfile_filename=None,
             stacked_image_product_filename=None,
             stacked_seg_product_filename=None,
             psf_listfile_filename=None,
             detections_listfile_filename=None,
             object_id_list_product_filename=None,
             workdir=".",
             save_products=False,
             load_images=True,
             prune_images=None,
             **kwargs):
        """Reads a SHEFrameStack from relevant data products.


        Parameters
        ----------
        exposure_listfile_filename : str
            Filename of the listfile pointing to the exposure image data products
        bkg_listfile_filename : str
            Filename of the listfile pointing to the exposure background data products
        seg_listfile_filename : str
            Filename of the listfile pointing to the exposure segmentation map files
        stacked_image_product_filename :frame_prod str
            Filename of the stacked image data product
        stacked_bkg_product_filename : str
            Filename of the stacked background data product
        stacked_seg_filename : str
            Filename of the stacked segmentation map file
        psf_listfile_filename : str
            Filename of the listfile pointing to the psf data products
        detections_listfile_filename : str
            Filename of the listfile pointing to the detections catalog data products
        object_id_list_product_filename : str
            Filename of the product containing the object IDs we want to process. If provided, the detections table
            will be pruned to only contain these objects, and only detectors with at least one object in from the
            list in them will be loaded.
        workdir : str
            Work directory
        save_products : bool
            If set to True, will save references to data products. Otherwise these references will be None
        load_images : bool
            If set to False, image data will not be loaded, and filehandles will be closed.

        Any kwargs are passed to the reading of the fits objects
        """

        # Read in the Object ID list if present
        if object_id_list_product_filename is not None:
            object_id_list_product = read_xml_product(find_file(object_id_list_product_filename, path=workdir))
            object_id_list = object_id_list_product.get_id_list()
        else:
            object_id_list_product = None
            object_id_list = None

        # Determine whether to prune based on presence/absence of object_id_list
        if prune_images == None:
            if object_id_list is None:
                prune_images = False
            else:
                prune_images = True

        # Load in the detections catalogues and combine them into a single catalogue
        if detections_listfile_filename is None:
            detections_catalogue = None
            detections_catalogue_products = None
        else:
            try:
                detections_filenames = read_listfile(find_file(detections_listfile_filename, path=workdir))

                # Load each table in turn and combine them

                detections_catalogues = []
                if save_products:
                    detections_catalogue_products = []

                for detections_product_filename in detections_filenames:

                    detections_product = read_xml_product(os.path.join(workdir, detections_product_filename))
                    if save_products:
                        detections_catalogue_products.append(detections_product)

                    logger.debug("DP: %s, %s, %s",
                                 workdir,
                                 detections_product_filename,
                                 detections_product.get_data_filename())
                    detections_catalogue = table.Table.read(
                        os.path.join(workdir, detections_product.get_data_filename()))

                    detections_catalogues.append(detections_catalogue)

                if object_id_list is None:
                    # If we have no object id list, stack them all
                    detections_catalogue = table.vstack(detections_catalogues,
                                                        metadata_conflicts="silent")  # Conflicts are expected
                else:
                    # If we do have an object id list, construct a new table with just the desired rows
                    rows_to_use = []

                    # loop over detections_catalog and make list of indices not in our object_id list
                    for cat in detections_catalogues:
                        for row in cat:
                            if row[mfc_tf.ID] in object_id_list:
                                rows_to_use.append(row)

                    detections_catalogue = initialise_mer_final_catalog()

                    for key in detections_catalogues[0].meta:
                        if key in detections_catalogue.meta:
                            detections_catalogue.meta[key] = detections_catalogues[0].meta[key]

                    for row in rows_to_use:
                        detections_catalogue.add_row()
                        new_row = detections_catalogue[-1]
                        for key in row.colnames:
                            if key in new_row.colnames:
                                try:
                                    new_row[key] = row[key]
                                except np.ma.core.MaskError as e:
                                    logger.warning(("Masked element for column %s"
                                                    " cannot be added to table; default value will be used."), key)

                    logger.info("Finished pruning list of galaxy objects to loop over")

            except SheFileReadError as e:
                logger.warning(str(e))

                # See if it's just a single catalogue, which we can handle
                detections_product = read_xml_product(
                    os.path.join(workdir, detections_listfile_filename))
                detections_catalogue = table.Table.read(
                    os.path.join(workdir, detections_product.get_data_filename()))

                detections_catalogue_products = [detections_product]

        # Prune out duplicate object IDs from the detections table - FIXME?
        # after MER resolves this issue?
        if detections_catalogue is not None:
            pruned_detections_catalogue = table.unique(
                detections_catalogue, keys=mfc_tf.ID)
        else:
            pruned_detections_catalogue = None

        # Load in the exposures as SHEFrames first
        exposures = []
        if save_products:
            exposure_products = []
            psf_products = []
            exposure_segmentation_products = []

        exposure_filenames = cls.read_or_none(exposure_listfile_filename, workdir)
        seg_filenames = cls.read_or_none(seg_listfile_filename, workdir)
        psf_filenames = cls.read_or_none(psf_listfile_filename, workdir)

        for exposure_i in range(len(exposure_filenames)):

            exposure_filename = cls.index_or_none(exposure_filenames, exposure_i)
            seg_filename = cls.index_or_none(seg_filenames, exposure_i)
            psf_filename = cls.index_or_none(psf_filenames, exposure_i)

            exposure = SHEFrame.read(frame_product_filename=exposure_filename,
                                     seg_product_filename=seg_filename,
                                     psf_product_filename=psf_filename,
                                     detections_catalogue=detections_catalogue,
                                     prune_images=prune_images,
                                     workdir=workdir,
                                     save_products=save_products,
                                     load_images=load_images,
                                     **kwargs)

            exposures.append(exposure)
            if save_products:
                exposure_products.append(exposure.exposure_product)
                psf_products.append(exposure.psf_product)
                exposure_segmentation_products.append(exposure.segmentation_product)

        # Load in the stacked products now

        # Get the stacked image and background image

        stacked_image_shape = None

        qualified_data_filename = None
        data_hdu_indices = (None, None, None)

        qualified_bkg_filename = None
        bkg_hdu_index = None

        qualified_seg_filename = None
        seg_hdu_index = None

        if stacked_image_product_filename is None:
            stacked_image_product = None
            stacked_image_header = None
            stacked_image_data = None
            stacked_rms_data = None
            stacked_mask_data = None
            stacked_bkg_data = None
        else:
            (stacked_image_product,
             stacked_image_header,
             stacked_data,
             qualified_data_filename,
             data_hdu_indices) = cls._read_product_extension(stacked_image_product_filename,
                                                             tags=(SCI_TAG,
                                                                   NOISEMAP_TAG,
                                                                   MASK_TAG),
                                                             workdir=workdir,
                                                             dtype=products.vis_stacked_frame.dpdVisStackedFrame,
                                                             load_images=load_images,
                                                             **kwargs)

            if load_images:
                stacked_image_data = stacked_data[0]
                stacked_rms_data = stacked_data[1]
                stacked_mask_data = stacked_data[2]
            else:
                stacked_image_data = None
                stacked_rms_data = None
                stacked_mask_data = None
                if stacked_image_header is not None:
                    stacked_image_shape = (stacked_image_header["NAXIS1"], stacked_image_header["NAXIS2"])

            (_, _, stacked_bkg_data,
             qualified_bkg_filename,
             bkg_hdu_index) = cls._read_product_extension(stacked_image_product_filename,
                                                          workdir=workdir,
                                                          dtype=products.vis_stacked_frame.dpdVisStackedFrame,
                                                          filetype="background",
                                                          load_images=load_images,
                                                          **kwargs)

        # Get the segmentation image
        if stacked_seg_product_filename is None:
            stacked_segmentation_product = None
            stacked_seg_data = None
        else:
            try:
                (stacked_segmentation_product,
                 _,
                 stacked_seg_data,
                 qualified_seg_filename,
                 seg_hdu_index) = cls._read_product_extension(stacked_seg_product_filename,
                                                              workdir=workdir,
                                                              dtype=products.she_stack_segmentation_map.dpdSheStackReprojectedSegmentationMap,
                                                              load_images=load_images,
                                                              **kwargs)
            except FileNotFoundError as e:
                logger.warning(str(e))
                stacked_segmentation_product = None
                stacked_seg_data = None

        # Construct a SHEImage object for the stacked image
        if stacked_image_product_filename is None:
            stacked_image = None
        else:
            stacked_image = SHEImage(data=stacked_image_data,
                                     mask=stacked_mask_data,
                                     noisemap=stacked_rms_data,
                                     background_map=stacked_bkg_data,
                                     segmentation_map=stacked_seg_data,
                                     header=stacked_image_header,
                                     wcs=astropy.wcs.WCS(stacked_image_header))

            stacked_image._images_loaded = load_images
            stacked_image._shape = stacked_image_shape

        # Construct a SHEFrameStack object
        new_frame_stack = SHEFrameStack(exposures=exposures,
                                        stacked_image=stacked_image,
                                        detections_catalogue=pruned_detections_catalogue)

        # If we're saving products, add in those references
        if save_products:

            new_frame_stack.exposure_products = exposure_products
            new_frame_stack.psf_products = psf_products
            new_frame_stack.exposure_segmentation_products = exposure_segmentation_products

            new_frame_stack.stacked_image_product = stacked_image_product
            new_frame_stack.stacked_segmentation_product = stacked_segmentation_product

            new_frame_stack.detections_catalogue_products = detections_catalogue_products

            new_frame_stack.object_id_list_product = object_id_list_product

        new_frame_stack._images_loaded = load_images

        if not load_images:

            new_frame_stack._stacked_data_filename = qualified_data_filename
            new_frame_stack._stacked_data_hdu = data_hdu_indices[0]

            new_frame_stack._stacked_noisemap_filename = qualified_data_filename
            new_frame_stack._stacked_noisemap_hdu = data_hdu_indices[1]

            new_frame_stack._stacked_mask_filename = qualified_data_filename
            new_frame_stack._stacked_mask_hdu = data_hdu_indices[2]

            new_frame_stack._stacked_bkg_filename = qualified_bkg_filename
            new_frame_stack._stacked_bkg_hdu = bkg_hdu_index

            new_frame_stack._stacked_seg_filename = qualified_seg_filename
            new_frame_stack._stacked_seg_hdu = seg_hdu_index

        # Return the constructed product
        return new_frame_stack
