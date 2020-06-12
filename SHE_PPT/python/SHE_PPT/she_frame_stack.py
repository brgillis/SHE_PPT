"""
File: python/SHE_PPT/she_frame_stack.py

Created on: 05/03/18
"""

#
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
#

__updated__ = "2019-05-27"

from copy import deepcopy
from json.decoder import JSONDecodeError
import os.path

from SHE_PPT import logging
from SHE_PPT import magic_values as mv
from SHE_PPT import products
from SHE_PPT.file_io import read_listfile, read_xml_product, find_file
from SHE_PPT.she_frame import SHEFrame
from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_image_stack import SHEImageStack
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.utility import find_extension, load_wcs
from astropy import table
from astropy.io import fits
import numpy as np


logger = logging.getLogger(__name__)


class SHEFrameStack(object):
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
        self.stacked_image = stacked_image
        self.mer_final_catalog_catalogue = detections_catalogue

        # Might have to manually calculate this later
        self.stack_pixel_size_ratio = 1

        # Set the detections catalogue to index by ID
        if self.mer_final_catalog_catalogue is not None:
            self.mer_final_catalog_catalogue.add_index(detf.ID)

        return

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

    def __eq__(self, rhs):
        """Equality test for SHEFrame class.
        """

        def neq(lhs, rhs):
            try:
                return bool(lhs != rhs)
            except ValueError as _e:
                return (lhs != rhs).any()

        def list_neq(lhs, rhs):

            if lhs is None and rhs is None:
                return False
            elif (lhs is None) != (rhs is None):
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
        if neq(self.mer_final_catalog_catalogue, rhs.mer_final_catalog_catalogue):
            return False
        if neq(self.stack_pixel_size_ratio, rhs.stack_pixel_size_ratio):
            return False

        return True

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
            row = self.mer_final_catalog_catalogue.loc[gal_id]
        except ValueError as e:
            if not "Cannot create TableLoc object with no indices" in str(e):
                raise
            self.mer_final_catalog_catalogue.add_index(detf.ID)
            row = self.mer_final_catalog_catalogue.loc[gal_id]

        x_world = row[detf.gal_x_world]
        y_world = row[detf.gal_y_world]

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

    def extract_stamp_stack(self, x_world, y_world, width, height=None, x_buffer=0, y_buffer=0, keep_header=False,
                            none_if_out_of_bounds=False):
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

           Return
           ------
           stamp_stack : SHEImageStack
        """

        # Extract from the stacked image first

        if self.stacked_image is not None:
            stack_stamp_width = self.stack_pixel_size_ratio * width
            if height is None:
                stack_stamp_height = None
            else:
                stack_stamp_height = self.stack_pixel_size_ratio * height

            stacked_image_x, stacked_image_y = self.stacked_image.world2pix(
                x_world, y_world)

            stacked_image_stamp = self.stacked_image.extract_stamp(x=stacked_image_x,
                                                                   y=stacked_image_y,
                                                                   width=stack_stamp_width,
                                                                   height=stack_stamp_height,
                                                                   keep_header=keep_header,
                                                                   none_if_out_of_bounds=none_if_out_of_bounds)

            # Return None if none_if_out_of_bounds and out of bounds of stacked
            # image
            if none_if_out_of_bounds and stacked_image_stamp is None:
                return None
        else:
            stacked_image_stamp = None

        # Get the stamps for each exposure

        exposure_stamps = []
        for exposure in self.exposures:
            exposure_stamps.append(exposure.extract_stamp(x_world=x_world,
                                                          y_world=y_world,
                                                          width=width,
                                                          height=height,
                                                          x_buffer=x_buffer,
                                                          y_buffer=y_buffer,
                                                          keep_header=keep_header))

        # Create and return the stamp stack

        stamp_stack = SHEImageStack(stacked_image=stacked_image_stamp,
                                    exposures=exposure_stamps,
                                    x_world=x_world,
                                    y_world=y_world,
                                    parent_frame_stack=self)

        return stamp_stack

    def get_fov_coords(self, x_world, y_world, x_buffer=0, y_buffer=0, none_if_out_of_bounds=False):
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
                                                 y_buffer=y_buffer)
            if fov_coords is not None:
                found = True
            fov_coords_list.append(fov_coords)

        # Return the resulting list (or None if not found and desired)
        if none_if_out_of_bounds and not found:
            fov_coords_list = None
        return fov_coords_list

    @classmethod
    def _read_product_extension(cls, product_filename, tags=None, workdir=".", dtype=None,
                                filetype="science", **kwargs):

        product = read_xml_product(os.path.join(workdir, product_filename))

        # Check it's the right type if necessary
        if dtype is not None:
            if not isinstance(product, dtype):
                raise ValueError(
                    "Data image product from " + product_filename + " is invalid type.")

        if filetype == "science":
            qualified_filename = os.path.join(
                workdir, product.get_data_filename())
        elif filetype == "background":
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

        header = hdulist[0].header

        if tags is None:
            data = hdulist[0].data.transpose()
        else:
            data = []
            for tag in tags:
                extension = find_extension(hdulist, tag)
                data.append(hdulist[extension].data.transpose())

        return header, data

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

        Any kwargs are passed to the reading of the fits objects
        """

        # Read in the Object ID list if present
        if object_id_list_product_filename is not None:
            object_id_list_product = read_xml_product(find_file(object_id_list_product_filename, path=workdir))
            object_id_list = object_id_list_product.get_id_list()
        else:
            object_id_list = None

        # Load in the detections catalogues and combine them into a single catalogue
        if detections_listfile_filename is None:
            detections_catalogue = None
        else:
            try:
                detections_filenames = read_listfile(find_file(detections_listfile_filename, path=workdir))

                # Load each table in turn and combine them

                detections_catalogues = []

                for detections_product_filename in detections_filenames:

                    detections_product = read_xml_product(os.path.join(workdir, detections_product_filename))

                    detections_catalogue = table.Table.read(
                        os.path.join(workdir, detections_product.get_data_filename()))

                    detections_catalogues.append(detections_catalogue)

                if object_id_list is None:
                    # If we have no object id list, stack them all
                    detections_catalogue = table.vstack(detections_catalogues,
                                                        metadata_conflicts="silent")  # Conflicts are expected
                    prune_images = False
                else:
                    # If we do have an object id list, construct a new table with just the desired rows
                    rows_to_use = []

                    # loop over detections_catalog and make list of indices not in our object_id list
                    for cat in detections_catalogues:
                        for row in cat:
                            if row[detf.ID] in object_id_list:
                                rows_to_use.append(row)

                    detections_catalogue = table.Table(names=detections_catalogues[0].colnames,
                                                       dtype=[detections_catalogues[0].dtype[n] for n in detections_catalogues[0].colnames])

                    for row in rows_to_use:
                        detections_catalogue.add_row(row)

                    prune_images = True

                    logger.info("Finished pruning list of galaxy objects to loop over")

            except JSONDecodeError as e:
                logger.warning(str(e))

                # See if it's just a single catalogue, which we can handle
                detections_product = read_xml_product(
                    os.path.join(workdir, detections_listfile_filename))
                detections_catalogue = table.Table.read(
                    os.path.join(workdir, detections_product.Data.DataStorage.DataContainer.FileName))

        # Prune out duplicate object IDs from the detections table - FIXME?
        # after MER resolves this issue?
        if detections_catalogue is not None:
            pruned_detections_catalogue = table.unique(
                detections_catalogue, keys=detf.ID)
        else:
            pruned_detections_catalogue = None

        # Load in the exposures as SHEFrames first
        exposures = []

        def read_or_none(listfile_filename):
            if listfile_filename is None:
                return None
            else:
                return read_listfile(os.path.join(workdir, listfile_filename))

        def index_or_none(filenames, index):
            if filenames is None:
                return None
            else:
                return filenames[index]

        exposure_filenames = read_or_none(exposure_listfile_filename)
        seg_filenames = read_or_none(seg_listfile_filename)
        psf_filenames = read_or_none(psf_listfile_filename)

        for exposure_i in range(len(exposure_filenames)):

            exposure_filename = index_or_none(exposure_filenames, exposure_i)
            seg_filename = index_or_none(seg_filenames, exposure_i)
            psf_filename = index_or_none(psf_filenames, exposure_i)

            exposure = SHEFrame.read(frame_product_filename=exposure_filename,
                                     seg_product_filename=seg_filename,
                                     psf_product_filename=psf_filename,
                                     detections_catalogue=detections_catalogue,
                                     prune_images=prune_images,
                                     workdir=workdir,
                                     **kwargs)

            exposures.append(exposure)

        # Load in the stacked products now

        # Get the stacked image and background image
        if stacked_image_product_filename is None:
            stacked_image_header = None
            stacked_image_data = None
            stacked_rms_data = None
            stacked_mask_data = None
            stacked_bkg_data = None
        else:
            (stacked_image_header,
             stacked_data) = cls._read_product_extension(stacked_image_product_filename,
                                                         tags=(
                                                             mv.sci_tag, mv.noisemap_tag, mv.mask_tag),
                                                         workdir=workdir,
                                                         dtype=products.vis_stacked_frame.dpdVisStackedFrame,
                                                         **kwargs)

            stacked_image_data = stacked_data[0]
            stacked_rms_data = stacked_data[1]
            stacked_mask_data = stacked_data[2]

            _, stacked_bkg_data = cls._read_product_extension(stacked_image_product_filename,
                                                              workdir=workdir,
                                                              dtype=products.vis_stacked_frame.dpdVisStackedFrame,
                                                              filetype="background",
                                                              **kwargs)

        # Get the segmentation image
        if stacked_seg_product_filename is None:
            stacked_seg_data = None
        else:
            try:
                _, stacked_seg_data = cls._read_product_extension(stacked_seg_product_filename,
                                                                  workdir=workdir,
                                                                  dtype=products.stack_mosaic.DpdSheStackMosaicProduct,
                                                                  **kwargs)
            except FileNotFoundError as e:
                logger.warning(str(e))
                stacked_seg_data = None

        # Construct a SHEImage object for the stacked image
        if stacked_image_data is None:
            stacked_image = None
        else:
            stacked_image = SHEImage(data=stacked_image_data,
                                     mask=stacked_mask_data,
                                     noisemap=stacked_rms_data,
                                     background_map=stacked_bkg_data,
                                     segmentation_map=stacked_seg_data,
                                     header=stacked_image_header,
                                     wcs=load_wcs(stacked_image_header))

        # Construct and return a SHEFrameStack object
        return SHEFrameStack(exposures=exposures,
                             stacked_image=stacked_image,
                             detections_catalogue=pruned_detections_catalogue)
