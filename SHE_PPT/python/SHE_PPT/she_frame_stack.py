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

"""
File: python/SHE_PPT/she_frame_stack.py

Created on: 05/03/18
"""

from copy import deepcopy
import os.path

from SHE_PPT import logging
from SHE_PPT import magic_values as mv
from SHE_PPT import products
from SHE_PPT.file_io import read_listfile, read_xml_product
from SHE_PPT.she_frame import SHEFrame
from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_image_stack import SHEImageStack
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import find_extension, load_wcs
from astropy import table
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np


products.calibrated_frame.init()
products.detections.init()
products.stacked_frame.init()

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
        self.detections_catalogue = detections_catalogue

        self.stack_pixel_size_ratio = 1  # Might have to manually calculate this later

        # Set the detections catalogue to index by ID
        if self.detections_catalogue is not None:
            self.detections_catalogue.add_index(detf.ID)

        return

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

        row = self.detections_catalogue.loc[gal_id]

        x_world = row[detf.gal_x_world]
        y_world = row[detf.gal_y_world]

        return self.extract_stamp_stack(x_world, y_world, width, *args, **kwargs)

    def extract_psf_stacks(self, gal_id, make_stacked_psf = False, keep_header = False):
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

            bulge_psf_stamp, disk_psf_stamp = exposure.extract_psf(gal_id, keep_header = keep_header)

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
        bulge_psf_stack = SHEImageStack(stacked_image = stacked_bulge_psf,
                                         exposures = bulge_psf_stamps,)
        disk_psf_stack = SHEImageStack(stacked_image = stacked_disk_psf,
                                         exposures = disk_psf_stamps,)

        return bulge_psf_stack, disk_psf_stack


    def extract_stamp_stack(self, x_world, y_world, width, height = None, x_buffer = 0, y_buffer = 0, keep_header = False,
                             none_if_out_of_bounds = False):
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

            stacked_image_x, stacked_image_y = self.stacked_image.world2pix(x_world, y_world)

            stacked_image_stamp = self.stacked_image.extract_stamp(x = stacked_image_x,
                                                                    y = stacked_image_y,
                                                                    width = stack_stamp_width,
                                                                    height = stack_stamp_height,
                                                                    keep_header = keep_header,
                                                                    none_if_out_of_bounds = none_if_out_of_bounds)

            # Return None if none_if_out_of_bounds and out of bounds of stacked image
            if none_if_out_of_bounds and stacked_image_stamp is None:
                return None
        else:
            stacked_image_stamp = None

        # Get the stamps for each exposure

        exposure_stamps = []
        for exposure in self.exposures:
            exposure_stamps.append(exposure.extract_stamp(x_world = x_world,
                                                            y_world = y_world,
                                                            width = width,
                                                            height = height,
                                                            x_buffer = x_buffer,
                                                            y_buffer = y_buffer,
                                                            keep_header = keep_header))

        # Create and return the stamp stack

        stamp_stack = SHEImageStack(stacked_image = stacked_image_stamp,
                                     exposures = exposure_stamps,
                                     x_world = x_world,
                                     y_world = y_world)

        return stamp_stack

    @classmethod
    def _read_product_extension(cls, product_filename, tags = None, workdir = ".", dtype = None,
                        filetype = "science", **kwargs):

        product = read_xml_product(os.path.join(workdir, product_filename))

        # Check it's the right type if necessary
        if dtype is not None:
            if not isinstance(product, dtype):
                raise ValueError("Data image product from " + product_filename + " is invalid type.")

        if filetype == "science":
            qualified_filename = os.path.join(workdir, product.get_data_filename())
        elif filetype == "background":
            qualified_filename = os.path.join(workdir, product.get_bkg_filename())
        elif filetype == "weight":
            qualified_filename = os.path.join(workdir, product.get_psf_filename())
        else:
            raise ValueError("Invalid filetype: " + filetype)
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
    def _read_file_extension(cls, filename, tags = None, workdir = ".", dtype = None, **kwargs):

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
              exposure_listfile_filename = None,
              seg_listfile_filename = None,
              stacked_image_product_filename = None,
              stacked_seg_filename = None,
              psf_listfile_filename = None,
              detections_listfile_filename = None,
              workdir = ".",
              clean_detections = False,
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
        workdir : str
            Work directory

        Any kwargs are passed to the reading of the fits objects
        """

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

            exposure = SHEFrame.read(frame_product_filename = exposure_filename,
                                      seg_filename = seg_filename,
                                      psf_filename = psf_filename,
                                      workdir = workdir,
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
                                                           tags = (mv.sci_tag, mv.noisemap_tag, mv.mask_tag),
                                                           workdir = workdir,
                                                           dtype = products.stacked_frame.vis_dpd.dpdVisStackedFrame)

            stacked_image_data = stacked_data[0]
            stacked_rms_data = stacked_data[1]
            stacked_mask_data = stacked_data[2]

            _, stacked_bkg_data = cls._read_product_extension(stacked_image_product_filename,
                                                               workdir = workdir,
                                                               dtype = products.stacked_frame.vis_dpd.dpdVisStackedFrame,
                                                               filetype = "background")

        # Get the segmentation image
        if stacked_seg_filename is None:
            stacked_seg_data = None
        else:
            try:
                _, stacked_seg_data = cls._read_file_extension(stacked_seg_filename,
                                                               workdir = workdir)
            except FileNotFoundError as e:
                logger.warn(str(e))
                stacked_seg_data = None

        # Construct a SHEImage object for the stacked image
        if stacked_image_data is None:
            stacked_image = None
        else:
            stacked_image = SHEImage(data = stacked_image_data,
                                      mask = stacked_mask_data,
                                      noisemap = stacked_rms_data,
                                      background_map = stacked_bkg_data,
                                      segmentation_map = stacked_seg_data,
                                      header = stacked_image_header,
                                      wcs = load_wcs(stacked_image_header))

        # Load in the detections catalogues and combine them into a single catalogue
        if detections_listfile_filename is None:
            detections_catalogue = None
        else:
            detections_filenames = read_listfile(os.path.join(workdir, detections_listfile_filename))

            # Load each table in turn and combine them

            detections_catalogues = []

            for detections_product_filename in detections_filenames:

                detections_product = read_xml_product(os.path.join(workdir, detections_product_filename))
#                 if not isinstance( detections_product, products.detections.DpdSheDetectionsProduct ):
#                     raise ValueError( "Detections product from " +
#                                       detections_product_filename + " is invalid type." )

                detections_catalogue = table.Table.read(os.path.join(workdir, detections_product.Data.DataStorage.DataContainer.FileName))
#                 if not is_in_format( detections_catalogue, detf ):
#                     raise ValueError( "Detections table from " +
#                                       detections_product.get_filename() + " is invalid type." )

                detections_catalogues.append(detections_catalogue)

            detections_catalogue = table.vstack(detections_catalogues,
                                                 metadata_conflicts = "silent")  # Conflicts are expected

        # Clean the detections table if desired
        if clean_detections:

            # First, get the limits of the frame. Use the stacked image if available
            if stacked_image is not None:
                test_xps = np.array((0, 0, stacked_image.shape[0] + 1, stacked_image.shape[0] + 1))
                test_yps = np.array((0, stacked_image.shape[1] + 1, 0, stacked_image.shape[1] + 1))

                test_x_worlds, test_y_worlds = stacked_image.pix2world(test_xps, test_yps)

                x_world_min = test_x_worlds.min()
                x_world_max = test_x_worlds.max()
                y_world_min = test_y_worlds.min()
                y_world_max = test_y_worlds.max()
            else:
                # We'll have to get the test values from the detectors of each frame

                x_world_min = 1e99
                x_world_max = -1e99
                y_world_min = 1e99
                y_world_max = -1e99

                for exposure in exposures:
                    if exposure is None:
                        continue
                    # Only bother with detectors on the corners
                    for ex_x in (1, 6):
                        for ex_y in (1, 6):

                            detector = exposure.detectors[ex_x, ex_y]

                            if detector is None:
                                continue  # FIXME What if just a corner detector fails?

                            test_xps = np.array((0, 0, detector.shape[0] + 1, detector.shape[0] + 1))
                            test_yps = np.array((0, detector.shape[1] + 1, 0, detector.shape[1] + 1))

                            test_x_worlds, test_y_worlds = detector.pix2world(test_xps, test_yps)

                            x_world_min = np.min((x_world_min, test_x_worlds.min()))
                            x_world_max = np.max((x_world_max, test_x_worlds.max()))
                            y_world_min = np.min((y_world_min, test_y_worlds.min()))
                            y_world_max = np.max((y_world_max, test_y_worlds.max()))

            # We have the outermost limits; now prune any values outside of them
            bad_x_world = np.logical_or(detections_catalogue[detf.gal_x_world] < x_world_min,
                                         detections_catalogue[detf.gal_x_world] > x_world_max)
            bad_y_world = np.logical_or(detections_catalogue[detf.gal_y_world] < y_world_min,
                                        detections_catalogue[detf.gal_y_world] > y_world_max)

            bad_pos = np.logical_or(bad_x_world, bad_y_world)

            detections_catalogue.remove_rows(bad_pos)

        # Prune out duplicate object IDs from the detections table - FIXME? after MER resolves this issue?
        if detections_catalogue is not None:
            pruned_detections_catalogue = table.unique(detections_catalogue, keys = detf.ID)
        else:
            pruned_detections_catalogue = None

        # Construct and return a SHEFrameStack object
        return SHEFrameStack(exposures = exposures,
                              stacked_image = stacked_image,
                              detections_catalogue = pruned_detections_catalogue)

