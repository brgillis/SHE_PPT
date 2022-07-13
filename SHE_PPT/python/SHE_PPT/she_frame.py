"""
File: python/SHE_PPT/she_frame.py

Created on: 02/03/18
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

import os.path
import weakref
from collections import namedtuple
from copy import deepcopy

import numpy as np
from astropy.io import fits
from astropy.io.fits import BinTableHDU, HDUList, ImageHDU, PrimaryHDU
from astropy.table import Table
from astropy.wcs import WCS

import EL_CoordsUtils.telescope_coords as tc
from EL_PythonUtils.utilities import run_only_once
from . import logging, products
from .constants.fits import (CCDID_LABEL, EXTNAME_LABEL, MASK_TAG, NOISEMAP_TAG, PSF_CAT_TAG, SCI_TAG, SEGMENTATION_TAG)
from .detector import get_id_string
from .file_io import read_xml_product
from .she_image import SHEImage
from .table_formats.mer_final_catalog import tf as mfc_tf
from .table_formats.she_psf_model_image import tf as pstf
from .table_utility import is_in_format
from .utility import find_extension

MSG_EXPECTED_EXTNAME = "Expected extname: "

MSG_INVALID_TYPE = "Data image product from %s is invalid type."

logger = logging.getLogger(__name__)


class SHEFrame(object):
    """Structure containing an array of SHEImageData objects, representing either an individual exposure or the
    stacked frame

    Attributes
    ----------
    detectors : 2D array (normally 1-indexed 6x6, but can be otherwise if needed) of SHEImage objects

    bulge_psf_image : SHEImage

    disk_psf_image : SHEImage

    psf_catalogue : astropy.table.Table
        Table linking galaxy IDs to the positions of their corresponding psfs
    bulge_stamp_size : int

    disk_stamp_size : int

    """

    # Data
    _detectors = None
    _psf_data_hdulist = None
    _psf_catalogue = None

    # Parent references
    _parent_frame_stack = None

    # Product references
    _exposure_product = None
    _psf_product = None
    _segmentation_product = None

    # File references and info
    _data_filename = None
    _d_data_hdus = {}

    _noisemap_filename = None
    _d_noisemap_hdus = {}

    _mask_filename = None
    _d_mask_hdus = {}

    _bkg_filename = None
    _d_bkg_hdus = {}

    _wgt_filename = None
    _d_wgt_hdus = {}

    _seg_filename = None
    _d_seg_hdus = {}

    # Options
    _images_loaded = False

    def __init__(self,
                 detectors,
                 psf_data_hdulist=None,
                 psf_catalogue=None,
                 parent_frame_stack=None, ):
        """
        Parameters
        ----------
        detectors : np.ndarray<SHE_PPT.she_image.SHEImage>
            2D array (normally 1-indexed 6x6, but can be otherwise if needed) of SHEImage objects
        psf_data_hdulist : astropy.fits.HDUList
            HDUList containing bulge and PSF HDUs
        psf_catalogue : astropy.table.Table
            Table linking galaxy IDs to the positions of their corresponding psfs
        parent_frame_stack : SHE_PPT.she_frame_stack.SHEFrameStack
            Reference to parent SHEFrameStack object if it exists; None otherwise
        """

        # References to parent objects
        self.parent_frame_stack = parent_frame_stack

        # Initialise directly
        self.detectors = detectors
        self.psf_data_hdulist = psf_data_hdulist
        self.psf_catalogue = psf_catalogue

        # Initialise product references as None
        self.exposure_product = None
        self.psf_product = None
        self.segmentation_product = None

        # Set the PSF catalogue to index by ID
        if self.psf_catalogue is not None:
            self.psf_catalogue.add_index(pstf.ID)

    @property
    def detectors(self):
        return self._detectors

    @detectors.setter
    def detectors(self, detectors):

        # We test the dimensionality
        if detectors.ndim != 2:
            raise ValueError("Detectors array of a SHEFrame must have 2 dimensions")

        # Check that the size is as expected
        if np.shape(detectors)[0] > 7 or np.shape(detectors)[1] > 7:
            raise ValueError("Detectors array can have maximum shape (7,7)")

        # Perform the attribution
        self._detectors = detectors

        # Set this as the parent for all detectors
        for detector in self._detectors.ravel():
            if detector is not None:
                detector.parent_frame = self
                detector.parent_frame_stack = self.parent_frame_stack

    @detectors.deleter
    def detectors(self):
        for detector in self._detectors.ravel():
            del detector
        self._detectors = None

    @property
    def parent_frame_stack(self):
        return self._parent_frame_stack()

    @parent_frame_stack.setter
    def parent_frame_stack(self, parent_frame_stack):

        if parent_frame_stack is None:
            self._parent_frame_stack = lambda: None
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_frame_stack = weakref.ref(parent_frame_stack)

    @parent_frame_stack.deleter
    def parent_frame_stack(self):
        self._parent_frame_stack = lambda: None

    @property
    def exposure_product(self):
        return self._exposure_product

    @exposure_product.setter
    def exposure_product(self, exposure_product):
        self._exposure_product = exposure_product

    @exposure_product.deleter
    def exposure_product(self):
        for exposure_product in self._exposure_product:
            del exposure_product
        del self._exposure_product

    @property
    def psf_product(self):
        return self._psf_product

    @psf_product.setter
    def psf_product(self, psf_product):
        self._psf_product = psf_product

    @psf_product.deleter
    def psf_product(self):
        for psf_product in self._psf_product:
            del psf_product
        del self._psf_product

    @property
    def segmentation_product(self):
        return self._segmentation_product

    @segmentation_product.setter
    def segmentation_product(self, segmentation_product):
        self._segmentation_product = segmentation_product

    @segmentation_product.deleter
    def segmentation_product(self):
        for segmentation_product in self._segmentation_product:
            del segmentation_product
        del self._segmentation_product

    def __eq__(self, rhs):
        """Equality test for SHEFrame class.
        """

        def neq(lhs, rhs):
            try:
                return bool(lhs != rhs)
            except ValueError as _e:
                return (lhs != rhs).any()

        def psf_hdulist_neq(lhs, rhs):

            if lhs is None and rhs is None:
                return False
            elif (lhs is None) != (rhs is None):
                return True

            if len(lhs) != len(rhs):
                return True
            try:
                for i in range(len(lhs)):
                    if (lhs[i].data is None) != (rhs[i].data is None):
                        return True
                    if lhs[i].data is not None and (lhs[i].data != rhs[i].data).any():
                        return True
                    if lhs[i].header != rhs[i].header:
                        return True
            except AttributeError as _e2:
                # At least one isn't the right type
                return True
            return False

        if neq(self.detectors, rhs.detectors):
            return False
        if neq(self.psf_catalogue, rhs.psf_catalogue):
            return False
        if psf_hdulist_neq(self.psf_data_hdulist, rhs.psf_data_hdulist):
            return False

        return True

    def _find_position(self, x_world, y_world, x_buffer=0, y_buffer=0):
        """ Finds the detector where a given position in world coordinates is.
        """

        # Loop over the detectors, and use the WCS of each to determine if it's
        # on it or not
        found = False

        num_x, num_y = np.shape(self.detectors)

        for x_i in range(num_x):
            for y_i in range(num_y):

                detector = self.detectors[x_i, y_i]
                if detector is None:
                    continue

                x, y = detector.world2pix(x_world, y_world)
                if ((x < 1 - x_buffer) or (x > detector.shape[0] + x_buffer) or
                        (y < 1 - y_buffer) or (y > detector.shape[1] + y_buffer)):
                    continue

                found = True

                break

            if found:
                break

        if not found:
            detector = None

        return detector, x, y, x_i, y_i

    def get_objects_in_exposure(self, object_coords):
        """Returns the indices of the input object coorinates that are found within this observation,
           along with lists of their x and y coordinates, and the detector they belong to"""

        num_x, num_y = np.shape(self.detectors)

        # get arrays/lists to hold all the objects and their attributes found in this exposure
        all_inds = np.empty(0, np.int64)
        all_xs = np.empty(0, np.float64)
        all_ys = np.empty(0, np.float64)
        detectors = []

        for x_i in range(num_x):
            for y_i in range(num_y):

                detector = self.detectors[x_i, y_i]

                if detector is None:
                    continue

                inds, xs, ys = detector.get_objects_in_dectector(object_coords)

                all_inds = np.concatenate((all_inds, inds))
                all_xs = np.concatenate((all_xs, xs))
                all_ys = np.concatenate((all_ys, ys))
                detectors += [(x_i, y_i) for i in range(len(inds))]

        n_objs = len(all_inds)
        logger.info(f"Found {n_objs} objects in exposure")

        detectors = np.asarray(detectors)

        return all_inds, all_xs, all_ys, detectors

    def extract_wcs_stamp(self, x_world, y_world):
        """ Extracts an "empty" stamp, which contains only information needed for WCS operations, having the
            interface of a standard SHEImage.

           Parameters
           ----------
           x_world : float
               The x sky co-ordinate (R.A.)
           y_world : float
               The y sky co-ordinate (Dec.)

           Return
           ------
           stamp : SHEImage or None
               The extracted stamp, or None if it was not found on any detector
        """

        detector, x, y, _, _ = self._find_position(x_world, y_world)

        # Return None if not found
        if detector is None:
            return None

        wcs_stamp = detector.extract_wcs_stamp(x=x,
                                               y=y, )

        return wcs_stamp

    def extract_stamp(self, x_world, y_world, width, height=None, x_buffer=0, y_buffer=0, keep_header=False):
        """Extracts a postage stamp centred on the provided sky co-ordinates, by using each detector's WCS
           to determine which (if any) it lies on. If x/y_buffer > 0, it will also extract from a detector if
           the position is within this many pixels of the edge of it.

           Parameters
           ----------
           x_world : float
               The x sky co-ordinate (R.A.)
           y_world : float
               The y sky co-ordinate (Dec.)
           width : int
               The desired width of the postage stamp in pixels
           height : int
               The desired height of the postage stamp in pixels (default = width)
           x_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, x-dimension
           y_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, y-dimension
           keep_header : bool
               If True, will copy the detector's header to the stamp's

           Return
           ------
           stamp : SHEImage or None
               The extracted stamp, or None if it was not found on any detector
        """

        detector, x, y, x_i, y_i = self._find_position(x_world=x_world,
                                                       y_world=y_world,
                                                       x_buffer=x_buffer,
                                                       y_buffer=y_buffer)

        # If not found on any detector, "detector" will be None, so return None for the stamp
        if detector is None:
            return None

        if self._images_loaded:
            stamp = detector.extract_stamp(x=x,
                                           y=y,
                                           width=width,
                                           height=height,
                                           keep_header=keep_header, )
        else:

            xy = (x_i, y_i)

            try:
                data_hdu = self._d_data_hdus[xy]
            except KeyError:
                data_hdu = None
            try:
                noisemap_hdu = self._d_noisemap_hdus[xy]
            except KeyError:
                noisemap_hdu = None
            try:
                mask_hdu = self._d_mask_hdus[xy]
            except KeyError:
                mask_hdu = None
            try:
                bkg_hdu = self._d_bkg_hdus[xy]
            except KeyError:
                bkg_hdu = None
            try:
                wgt_hdu = self._d_wgt_hdus[xy]
            except KeyError:
                wgt_hdu = None
            try:
                seg_hdu = self._d_seg_hdus[xy]
            except KeyError:
                seg_hdu = None

            stamp = detector.extract_stamp(x=x,
                                           y=y,
                                           width=width,
                                           height=height,
                                           keep_header=keep_header,
                                           data_filename=self._data_filename,
                                           data_hdu=data_hdu,
                                           noisemap_filename=self._noisemap_filename,
                                           noisemap_hdu=noisemap_hdu,
                                           mask_filename=self._mask_filename,
                                           mask_hdu=mask_hdu,
                                           bkg_filename=self._bkg_filename,
                                           bkg_hdu=bkg_hdu,
                                           wgt_filename=self._wgt_filename,
                                           wgt_hdu=wgt_hdu,
                                           seg_filename=self._seg_filename,
                                           seg_hdu=seg_hdu)

        # Keep the extname and CCDID even if not keeping the full header
        if stamp.header is None:
            stamp.add_default_header()
        if detector.header is not None:
            stamp.header[EXTNAME_LABEL] = detector.header[EXTNAME_LABEL]
            stamp.header[CCDID_LABEL] = detector.header[CCDID_LABEL]

        return stamp

    def extract_psf(self, gal_id, keep_header=False):
        """Extracts the bulge and disk psfs for a given galaxy.

        Parameters
        ----------
        gal_id : int
            ID of the galaxy
        keep_header : bool
            If True, the PSF image's header will be copied to the stamp's. Default False.

        Return
        ------
        bulge_psf_stamp : SHEImage

        disk_psf_stamp : SHEImage

        """

        try:
            row = self.psf_catalogue.loc[gal_id]
        except ValueError as e:
            if not str(e) == "Cannot create TableLoc object with no indices":
                raise
            self.psf_catalogue.add_index(pstf.ID)
            row = self.psf_catalogue.loc[gal_id]

        bulge_hdu = self.psf_data_hdulist[row[pstf.bulge_index]]
        bulge_psf_stamp = SHEImage(data=bulge_hdu.data.transpose(),
                                   header=bulge_hdu.header,
                                   parent_frame_stack=self.parent_frame_stack,
                                   parent_frame=self)

        disk_hdu = self.psf_data_hdulist[row[pstf.disk_index]]
        disk_psf_stamp = SHEImage(data=disk_hdu.data.transpose(),
                                  header=disk_hdu.header,
                                  parent_frame_stack=self.parent_frame_stack,
                                  parent_frame=self)

        return bulge_psf_stamp, disk_psf_stamp

    def get_fov_coords(self, x_world, y_world, x_buffer=0, y_buffer=0,
                       return_det_coords_too=False):
        """ Calculates the Field-of-View (FOV) co-ordinates of a given sky position, and returns a (fov_x, fov_y)
            tuple. If the position isn't present in the exposure, None will be returned instead.

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
            return_det_coords_too : bool
                If true return namedtuple of x_fov, y_fov, detno_x, detno_y, x_det, y_det

            Return
            ------
            fov_coords : tuple<float,float> or None
                A (fov_x, fov_y) tuple if present, or None if not present.
        """

        # Loop over the detectors, and use the WCS of each to determine if it's on it or not
        found = False

        num_x, num_y = np.shape(self.detectors)

        for x_i in range(num_x):
            for y_i in range(num_y):

                detector = self.detectors[x_i, y_i]
                if detector is None:
                    continue

                x, y = detector.world2pix(x_world, y_world)
                if (x < 1 - x_buffer) or (x > detector.shape[0] + x_buffer):
                    continue
                if (y < 1 - y_buffer) or (y > detector.shape[1] + y_buffer):
                    continue

                found = True

                break

            if found:
                break

        if (detector is None) or (not found):
            return None

        # Get the co-ordinates from the detector's method
        # @FIXME: no SHEImage.get_fov_coords() method...
        # fov_coords = detector.get_fov_coords(x=x, y=y,)
        # return fov_coords
        # @TODO: Return detector and x,y in namedtuple
        # return x,y
        # @TODO: orientation
        x_fov, y_fov = tc.get_fov_coords_from_detector(
            x, y, x_i, y_i, 'VIS')
        if return_det_coords_too:
            # Do as astropy Table
            CoordTuple = namedtuple("CoordTuple",
                                    "x_fov y_fov detno_x detno_y x_det y_det")
            return CoordTuple(*[x_fov, y_fov, x_i, y_i, x, y])
        else:
            return (x_fov, y_fov)

    @classmethod
    def read(cls,
             frame_product_filename=None,
             seg_product_filename=None,
             psf_product_filename=None,
             detections_catalogue=None,
             prune_images=False,
             workdir=".",
             x_max=6,
             y_max=6,
             save_products=False,
             load_images=True,
             **kwargs):
        """Reads a SHEFrame from disk

        Parameters
        ----------
        frame_product_filename : str
            Filename of the CalibratedFrame data product
        seg_product_filename : str
            Filename of the Mosaic (segmentation map) data product
        psf_product_filename : str
            Filename of the PSF Image data product
        detections_catalogue : astropy.table.Table
            The detections catalogue - only needed if prune_images=True
        prune_images : bool
            If True, will only load images where at least one object from the detections catalogue is present
        workdir : str
            Work directory
        x_max : int
            Maximum x-coordinate of detectors
        y_max : int
            Maximum y-coordinate of detectors
        save_products : bool
            If True, will save references to data products read in
        load_images : bool
            If set to False, image data will not be loaded, and filehandles will be closed.

        Any kwargs are passed to the reading of the fits data
        """

        # Check if we're pruning images that we have a detections catalogue, and if so, load in positions
        if not load_images:

            def check_for_objects(header, *_args, **_kwargs):
                wcs = WCS(header)
                return False, wcs

        elif prune_images:
            if detections_catalogue is None:
                raise TypeError("If prune_images==True, detections_catalogue must be supplied.")
            ra_list = detections_catalogue[mfc_tf.gal_x_world].data
            dec_list = detections_catalogue[mfc_tf.gal_y_world].data

            def check_for_objects(header, buffer=4):

                wcs = WCS(header)

                xp_max = header['NAXIS1'] - 1
                yp_max = header['NAXIS2'] - 1

                x_list, y_list = wcs.all_world2pix(ra_list, dec_list, 0)

                good_x = np.logical_and(x_list > -buffer, x_list < xp_max + buffer)
                good_y = np.logical_and(y_list > -buffer, y_list < yp_max + buffer)

                good_objs = np.logical_and(good_x, good_y)

                return good_objs.any(), wcs

        else:

            def check_for_objects(header, *_args, **_kwargs):
                wcs = WCS(header)
                return True, wcs

        if prune_images:

            def check_if_psf_needed(psf_cat, hdu_index):

                id_list = detections_catalogue[mfc_tf.ID].data

                need_psf = False
                for object_id in id_list:
                    row = psf_cat.loc[object_id]
                    if row[pstf.bulge_index] == hdu_index or row[pstf.disk_index] == hdu_index:
                        need_psf = True
                        break

                return need_psf

        else:

            def check_if_psf_needed(*_args, **_kwargs):
                return True

        def join_or_none(a, b):
            if a is None or b is None:
                return None
            else:
                return os.path.join(a, b)

        def open_or_none(filename, memmap=None):
            qualified_filename = join_or_none(workdir, filename)
            if qualified_filename is None:
                return None, None
            else:
                try:
                    tmp_kwargs = deepcopy(kwargs)
                    if memmap is not None:
                        tmp_kwargs["memmap"] = memmap
                    return fits.open(qualified_filename, **tmp_kwargs), qualified_filename
                except FileNotFoundError as e:
                    logger.warning(e)
                    return None, qualified_filename

        detectors = np.ndarray((x_max + 1, y_max + 1), dtype=SHEImage)

        # Load in the relevant fits files

        # Load in the data from the primary frame
        if frame_product_filename is not None:
            frame_prod = read_xml_product(
                os.path.join(workdir, frame_product_filename))
            if not isinstance(frame_prod, products.vis_calibrated_frame.dpdVisCalibratedFrame):
                raise ValueError(MSG_INVALID_TYPE % frame_product_filename)

            # Load in the data from the science, background, and weight frames
            frame_data_hdulist, qualified_data_filename = open_or_none(frame_prod.get_data_filename())
            bkg_data_hdulist, qualified_bkg_filename = open_or_none(frame_prod.get_bkg_filename())
            wgt_data_hdulist, qualified_wgt_filename = open_or_none(frame_prod.get_wgt_filename())
        else:
            frame_prod = None
            frame_data_hdulist = None
            qualified_data_filename = None
            bkg_data_hdulist = None
            qualified_bkg_filename = None
            wgt_data_hdulist = None
            qualified_wgt_filename = None

        # Load in the data from the segmentation frame
        if seg_product_filename is not None:

            seg_prod = read_xml_product(
                os.path.join(workdir, seg_product_filename))
            if not isinstance(seg_prod,
                              products.she_exposure_segmentation_map.dpdSheExposureReprojectedSegmentationMap):
                raise ValueError(MSG_INVALID_TYPE % seg_product_filename)

            seg_data_hdulist, qualified_seg_filename = open_or_none(seg_prod.get_data_filename())
        else:
            seg_prod = None
            seg_data_hdulist = None
            qualified_seg_filename = None

        d_data_hdus = {}
        d_noisemap_hdus = {}
        d_mask_hdus = {}
        d_bkg_hdus = {}
        d_wgt_hdus = {}
        d_seg_hdus = {}

        for x_i in np.linspace(1, x_max, x_max, dtype=np.int8):
            for y_i in np.linspace(1, y_max, y_max, dtype=np.int8):

                id_string = get_id_string(x_i, y_i)

                detector_shape = None

                if frame_data_hdulist is not None:

                    # Find the data HDU
                    sci_extname = id_string + "." + SCI_TAG
                    sci_i = find_extension(frame_data_hdulist, sci_extname)
                    if sci_i is None:
                        # Don't raise here; might be just using limited number
                        continue

                    d_data_hdus[(x_i, y_i)] = sci_i

                    detector_header = deepcopy(frame_data_hdulist[sci_i].header)

                    # Find the noisemap HDU
                    noisemap_extname = id_string + "." + NOISEMAP_TAG
                    noisemap_i = find_extension(
                        frame_data_hdulist, noisemap_extname)
                    if noisemap_i is None:
                        raise ValueError(
                            "No corresponding noisemap extension found in file " + frame_prod.get_data_filename() +
                            "." +
                            MSG_EXPECTED_EXTNAME + noisemap_extname)

                    d_noisemap_hdus[(x_i, y_i)] = noisemap_i

                    # Find the mask HDU
                    mask_extname = id_string + "." + MASK_TAG
                    mask_i = find_extension(frame_data_hdulist, mask_extname)
                    if mask_i is None:
                        raise ValueError(
                            "No corresponding mask extension found in file " + frame_prod.get_data_filename() + "." +
                            MSG_EXPECTED_EXTNAME + mask_extname)

                    d_mask_hdus[(x_i, y_i)] = mask_i

                    # Check for objects, and skip if none are on this detector
                    load_detector, detector_wcs = check_for_objects(detector_header)

                    if load_detector:

                        detector_data = frame_data_hdulist[sci_i].data.transpose()
                        detector_noisemap = frame_data_hdulist[noisemap_i].data.transpose()
                        try:
                            detector_mask = frame_data_hdulist[mask_i].data.transpose()
                        except ValueError as e:
                            if "Cannot load a memory-mapped image" not in str(e):
                                raise
                            warn_cannot_memmap(e)

                            detector_mask = None

                    else:
                        detector_data = None
                        detector_noisemap = None
                        detector_mask = None

                        # Need to read at least the shape for it if possible
                        if detector_header is not None:
                            detector_shape = (detector_header["NAXIS1"], detector_header["NAXIS2"])

                else:
                    detector_data = None
                    detector_header = None
                    detector_wcs = None
                    detector_noisemap = None
                    detector_mask = None

                if bkg_data_hdulist is not None:
                    bkg_extname = id_string  # Background has no tag
                    bkg_i = find_extension(bkg_data_hdulist, bkg_extname)
                    if bkg_i is None:
                        raise ValueError(
                            "No corresponding background extension found in file " + frame_prod.get_bkg_filename() +
                            "." +
                            MSG_EXPECTED_EXTNAME + bkg_extname)
                    d_bkg_hdus[(x_i, y_i)] = bkg_i
                    if load_detector:
                        detector_background = bkg_data_hdulist[bkg_i].data.transpose()
                    else:
                        detector_background = None
                else:
                    detector_background = None

                if wgt_data_hdulist is not None:
                    wgt_extname = id_string  # Background has no tag
                    wgt_ccdid = str(x_i) + str(y_i)
                    wgt_i = find_extension(wgt_data_hdulist, wgt_extname)
                    if wgt_i is None:
                        logger.warn(
                            "No corresponding weight extension found in file " + frame_prod.get_wgt_filename() + "." +
                            "\nExpected EXTNAME: " + wgt_extname)
                        # Try to find by CCDID
                        wgt_i = find_extension(wgt_data_hdulist, ccdid=wgt_ccdid)
                        if wgt_i is None:
                            raise ValueError(
                                "No corresponding weight extension found in file " + frame_prod.get_wgt_filename() +
                                "." +
                                "\nExpected CCDID: " + wgt_ccdid)
                    d_wgt_hdus[(x_i, y_i)] = wgt_i
                    if load_detector:
                        detector_weight = wgt_data_hdulist[wgt_i].data.transpose()
                    else:
                        detector_weight = None
                else:
                    detector_weight = None

                if seg_data_hdulist is not None:
                    seg_extname = id_string + "." + SEGMENTATION_TAG
                    seg_i = find_extension(seg_data_hdulist, seg_extname)
                    if seg_i is None:
                        raise ValueError(
                            "No corresponding segmentation extension found in file " + frame_prod.get_data_filename()
                            + "." +
                            MSG_EXPECTED_EXTNAME + seg_extname)
                    d_seg_hdus[(x_i, y_i)] = seg_i
                    if load_detector:
                        detector_seg_data = seg_data_hdulist[seg_i].data.transpose()
                    else:
                        detector_seg_data = None
                else:
                    detector_seg_data = None

                # Init an image for the detector
                detector = SHEImage(data=detector_data,
                                    mask=detector_mask,
                                    noisemap=detector_noisemap,
                                    background_map=detector_background,
                                    weight_map=detector_weight,
                                    segmentation_map=detector_seg_data,
                                    header=detector_header,
                                    wcs=detector_wcs)

                detector._images_loaded = load_images
                detector._shape = detector_shape

                detectors[x_i, y_i] = detector

        # Close filehandles if we aren't loading images
        if not load_images:
            del frame_data_hdulist, bkg_data_hdulist, wgt_data_hdulist, seg_data_hdulist

        # Load in the PSF data
        if psf_product_filename is not None:

            psf_prod = read_xml_product(
                os.path.join(workdir, psf_product_filename))
            if not isinstance(psf_prod, products.she_psf_model_image.dpdShePsfModelImage):
                raise ValueError(MSG_INVALID_TYPE % psf_product_filename)

            psf_data_filename = os.path.join(
                workdir, psf_prod.get_data_filename())

            qualified_psf_filename = os.path.join(workdir, psf_data_filename)

            input_psf_data_hdulist = fits.open(qualified_psf_filename, **kwargs)

            psf_cat_i = find_extension(input_psf_data_hdulist, PSF_CAT_TAG)
            psf_cat = Table.read(input_psf_data_hdulist[psf_cat_i])

            # Add the object ID as an index to the PSF catalog
            psf_cat.add_index(pstf.ID)

            psf_data_hdulist = HDUList()
            for i, hdu in enumerate(input_psf_data_hdulist):
                if i == 0:
                    psf_data_hdulist.append(PrimaryHDU())
                elif i == 1:
                    psf_data_hdulist.append(BinTableHDU(data=deepcopy(hdu.data),
                                                        header=deepcopy(hdu.header)))
                else:
                    if check_if_psf_needed(psf_cat, i):
                        # Add the PSF image if needed
                        psf_data_hdulist.append(ImageHDU(data=deepcopy(hdu.data),
                                                         header=deepcopy(hdu.header)))
                    else:
                        # Otherwise add a dummy HDU (to preserve file structure)
                        psf_data_hdulist.append(ImageHDU())

            # Clean up
            del input_psf_data_hdulist
            psf_cat.remove_indices(pstf.ID)

            if not is_in_format(psf_cat, pstf):
                raise ValueError(
                    "PSF table from " + qualified_psf_filename + " is in invalid format.")
        else:
            psf_prod = None
            psf_data_hdulist = None
            psf_cat = None

        # Construct a SHEFrame object
        new_frame = SHEFrame(detectors=detectors,
                             psf_data_hdulist=psf_data_hdulist,
                             psf_catalogue=psf_cat)

        # Fill out the product references
        if save_products:
            new_frame.exposure_product = frame_prod
            new_frame.psf_product = psf_prod
            new_frame.segmentation_product = seg_prod

        # File out file references
        new_frame._images_loaded = load_images

        if not load_images:
            new_frame._data_filename = qualified_data_filename
            new_frame._d_data_hdus = d_data_hdus

            new_frame._noisemap_filename = qualified_data_filename
            new_frame._d_noisemap_hdus = d_noisemap_hdus

            new_frame._mask_filename = qualified_data_filename
            new_frame._d_mask_hdus = d_mask_hdus

            new_frame._bkg_filename = qualified_bkg_filename
            new_frame._d_bkg_hdus = d_bkg_hdus

            new_frame._wgt_filename = qualified_wgt_filename
            new_frame._d_wgt_hdus = d_wgt_hdus

            new_frame._seg_filename = qualified_seg_filename
            new_frame._d_seg_hdus = d_seg_hdus

        # Return the created product
        return new_frame


@run_only_once
def warn_cannot_memmap(e):
    logger.warning(str(e))
