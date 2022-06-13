""" @file she_image.py

    Created 17 Aug 2017

    Defines a class for an image object with multiple data types (i.e. science, background, etc.).
"""

from __future__ import annotations

__updated__ = "2021-08-13"

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import weakref
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional, Sequence, TYPE_CHECKING, Tuple, Type, Union

import astropy.io.fits
import astropy.wcs
import fitsio
import galsim
import numpy as np
from astropy.io.fits import Header
from coord import Angle
from galsim import Shear

from EL_PythonUtils.utilities import run_only_once
from . import logging, mdb
from .constants.fits import BACKGROUND_TAG, CCDID_LABEL, MASK_TAG, NOISEMAP_TAG, SCI_TAG, SEGMENTATION_TAG, WEIGHT_TAG
from .constants.misc import SEGMAP_UNASSIGNED_VALUE
from .file_io import DEFAULT_WORKDIR, write_fits
from .mask import as_bool, is_masked_bad, is_masked_suspect_or_bad
from .utility import neq

if TYPE_CHECKING:
    from .she_frame_stack import SHEFrameStack
    from .she_frame import SHEFrame
    from .she_image_stack import SHEImageStack

# Define various constants used in this module

PRIMARY_TAG = "PRIMARY"

KEY_X_OFFSET = "SHEIOFX"
KEY_Y_OFFSET = "SHEIOFY"

DETECTOR_SHAPE = np.array((4096, 4136), dtype = int)
DEFAULT_STAMP_SIZE = 384

D_INDEXCONV_DEFS = {"numpy"     : 0.0,
                    "sextractor": 0.5}

D_ATTR_CONVERSIONS = {SCI_TAG         : "data",
                      MASK_TAG        : "mask",
                      NOISEMAP_TAG    : "noisemap",
                      SEGMENTATION_TAG: "segmentation_map",
                      BACKGROUND_TAG  : "background_map",
                      WEIGHT_TAG      : "weight_map", }
D_DEFAULT_IMAGE_VALUES = {SCI_TAG         : 0,
                          MASK_TAG        : 1,
                          NOISEMAP_TAG    : 0,
                          SEGMENTATION_TAG: SEGMAP_UNASSIGNED_VALUE,
                          BACKGROUND_TAG  : 0,
                          WEIGHT_TAG      : 0, }

NOISEMAP_DTYPE = np.float32
MASK_DTYPE = np.int32
BKG_DTYPE = np.float32
WGT_DTYPE = np.float32
SEG_DTYPE = np.int64
D_IMAGE_DTYPES: Dict[str, Optional[Type]] = {SCI_TAG         : None,
                                             MASK_TAG        : MASK_DTYPE,
                                             NOISEMAP_TAG    : NOISEMAP_DTYPE,
                                             SEGMENTATION_TAG: SEG_DTYPE,
                                             BACKGROUND_TAG  : BKG_DTYPE,
                                             WEIGHT_TAG      : WGT_DTYPE, }

logger = logging.getLogger(__name__)


@lru_cache(maxsize = 50)
def _get_fits_handle(qualified_filename: str) -> fitsio.FITS:
    """Private function to open a FITS file handle from a filename. Uses caching to limit number of open
    FITS file handles to 50.
    """
    f = fitsio.FITS(qualified_filename)
    return f


@lru_cache(maxsize = 50)
def _get_hdu_handle(qualified_filename: str,
                    hdu_i: Union[int, str]) -> fitsio.hdu.base.HDUBase:
    """Private function to open a FITS HDU file handle from a filename and HDU index. Uses caching to limit number of
    open HDU file handles to 50.
    """
    h = _get_fits_handle(qualified_filename)[hdu_i]
    return h


@lru_cache(maxsize = 2000)
def _read_stamp(xmin: int,
                ymin: int,
                xmax: int,
                ymax: int,
                qualified_filename: str,
                hdu_i: Union[int, str]) -> np.ndarray:
    """Private function to read a stamp from a FITS file. Uses caching to limit number of stamps in memory to 2000.
    """
    data = _get_hdu_handle(qualified_filename, hdu_i)[ymin:ymax, xmin:xmax].transpose()
    return data


def _return_none() -> None:
    """A private function which does nothing and returns None. This is used to be bound in place of a weak reference
    if no object is referenced.
    """
    return None


class SHEImage:
    """Structure to hold a representation of a science image and associated images (background, weight, etc.),
    and supply various useful methods.

    All image attributes are stored as 2D numpy arrays, indexed as (x,y), consistent with DS9, SExtractor,
    and GalSim orientation conventions, and NOT consistent with the astropy (y,x) convention (which arises from
    the fact that image data in FITS files is stored in column-major order, but astropy reads it in as row-major).
    If an image is needed with the astropy convention, use the array's `transpose()` method to convert it - this
    returns a view of the array with the (x,y) axes swapped (not a copy).

    Attributes
    ----------
    data : np.ndarray[float]
    mask : Optional[np.ndarray[np.int64]]
    noisemap : Optional[np.ndarray[float]]
    segmentation_map : Optional[np.ndarray[np.int64]]
    background_map : Optional[np.ndarray[float]]
    weight_map : Optional[np.ndarray[float]]
    header : Header
    offset : Tuple[float,float]
    wcs : Optional[astropy.wcs.WCS]
    galsim_wcs : Optional[galsim.wcs.BaseWCS]
    shape : np.ndarray[int]
    det_ix : int
    det_iy : int
    parent_frame_stack : Optional[SHEFrameStack]
    parent_frame : Optional[SHEFrame]
    parent_image_stack : Optional[SHEImageStack]
    parent_image : Optional[SHEImage]
    """

    # Class attributes

    # Images
    _data = None
    _mask = None
    _noisemap = None
    _segmentation_map = None
    _background_map = None
    _weight_map = None

    # Misc. public values
    _header = None
    _offset = np.array([0., 0.], dtype = float)
    _wcs = None
    _shape: np.ndarray[int]
    _galsim_wcs = None

    # Parent references
    _parent_frame_stack = None
    _parent_frame = None
    _parent_image_stack = None
    _parent_image = None

    # Private values
    _images_loaded = True

    def __init__(self,
                 data: Optional[np.ndarray[float]],
                 mask: Optional[np.ndarray[np.int64]] = None,
                 noisemap: Optional[np.ndarray[float]] = None,
                 segmentation_map: Optional[np.ndarray[np.int64]] = None,
                 background_map: Optional[np.ndarray[float]] = None,
                 weight_map: Optional[np.ndarray[float]] = None,
                 header: Optional[Header] = None,
                 offset: Optional[Tuple[float, float]] = None,
                 wcs: Optional[astropy.wcs.WCS] = None,
                 parent_frame_stack: Optional[SHEFrameStack] = None,
                 parent_frame: Optional[SHEFrame] = None,
                 parent_image_stack: Optional[SHEImageStack] = None,
                 parent_image: Optional[SHEImage] = None):
        """Initializer for a SHEImage object

        Parameters
        ----------
        data : Optional[np.ndarray[float][
            The science image. If None is provided, will be stored as a 0x0 array.
        mask : Optional[np.ndarray[np.int64]]
            The mask image, of the same shape as the science image.
        noisemap : Optional[np.ndarray[float]]
            The noise image (for only background noise, not including source noise), of the same shape as the
            science image.
        segmentation_map : Optional[np.ndarray[np.int64]]
            The segmentation map image (associating pixels with objects), of the same shape as the science image.
        background_map : Optional[np.ndarray[float]]
            The background map, of the same shape as the science image.
        weight_map : Optional[np.ndarray[float]]
            The weight map, of the same shape as the science image.
        header : Optional[astropy.io.fits.Header]
            The image header, typically copied from the science image's HDU's header.
        offset : Optional[Tuple[float,float]]
            The offset of this image relative to the image (if any) it was extracted from, indexed as (x_offset,
            y_offset).
        wcs : Optional[astropy.wcs.WCS]
            An astropy WCS object for this image.
        parent_frame_stack : Optional[SHEFrameStack]
            Reference to the parent SHEFrameStack, if it exists; None otherwise.
        parent_frame : Optional[SHEFrame]
            Reference to the parent SHEFrame, if it exists; None otherwise.
        parent_image_stack : Optional[SHEImageStack]
            Reference to the parent SHEImageStack, if it exists; None otherwise.
        parent_image : Optional[SHEImage]
            Reference to the parent SHEImage, if it exists; None otherwise.
        """

        # References to parent objects
        self.parent_frame_stack = parent_frame_stack
        self.parent_frame = parent_frame
        self.parent_image_stack = parent_image_stack
        self.parent_image = parent_image

        # Public values - Note the tests done in the setter methods
        self._shape = data.shape if data is not None else np.array([0., 0.], dtype = int)
        self.data = data
        self.mask = mask

        if self.data is not None and self.mask is None:
            self.add_default_mask()

        self.noisemap = noisemap
        self.segmentation_map = segmentation_map
        self.background_map = background_map
        self.weight_map = weight_map
        self.header = header
        self.offset = offset
        self.wcs = wcs

        # If no WCS is provided, try to set one up from the header
        if self.wcs is None and self.header is not None:
            self.wcs = astropy.wcs.WCS(self.header)

    # Properties

    @property
    def data(self) -> np.ndarray[float]:
        """The primary science image.

        Returns
        -------
        data : np.ndarray[float]
            The science image.
        """
        return self._data

    @data.setter
    def data(self,
             data: Optional[np.ndarray[float]]) -> None:
        """Setter for the primary science image, doing some validity checks on the input.

        Parameters
        ----------
        data : Optional[np.ndarray[float]]
            The science image.
        """

        # If setting data as None, set as a dim-0 array for interface safety
        if data is None:
            data = np.ndarray((0, 0), dtype = float)

        # Ensure we have a 2-dimensional array
        if data.ndim != 2:
            raise ValueError("Data array of a SHEImage must have 2 dimensions")

        # Also test that the shape isn't modified by the setter
        try:
            existing_shape: Optional[np.ndarray[int]] = self.shape
        except AttributeError:
            existing_shape = None

        if existing_shape is not None and np.any(data.shape != existing_shape):
            raise ValueError(f"Shape of a SHEImage can not be modified. Current is {existing_shape}, new data is "
                             f"{data.shape}.")

        # Finally, perform the attribution
        self._data = data

    @data.deleter
    def data(self) -> None:
        """Simple deleter for the `data` attribute.
        """
        del self._data

    @property
    def mask(self) -> Optional[np.ndarray[np.int32]]:
        """The pixel mask of the image, if present; None otherwise.

        Returns
        -------
        mask : Optional[np.ndarray[np.int32]]
            The pixel mask of the image, if present; None otherwise.
        """
        return self._mask

    @mask.setter
    def mask(self,
             mask: Optional[np.ndarray[int]]) -> None:
        """Setter for the pixel mask of the image, doing some validity checks on the input.

        Parameters
        ----------
        mask : Optional[np.ndarray[int]]
            The pixel mask of the image.
        """

        # We use safe casting for the mask, since we could lose very relevant data if we cast e.g. an int64 to an int32
        self.__set_array_attr(array = mask,
                              name = MASK_TAG,
                              casting = "safe")

    @mask.deleter
    def mask(self) -> None:
        """Simple deleter for the `mask` attribute.
        """
        del self._mask

    @property
    def boolmask(self) -> np.ndarray[np.bool]:
        """A boolean summary of the mask, cannot be set, only get.

        Returns
        -------
        boolmask : np.ndarray[np.bool]
            A boolean summary of the mask.
        """
        if self.mask is None:
            return None
        return self.mask.astype(np.bool)

    @property
    def noisemap(self) -> Optional[np.ndarray[np.float32]]:
        """The noisemap (for only background noise, not including source noise) for the image

        Returns
        -------
        noisemap : Optional[np.ndarray[float]]
            The noise map, if present; None otherwise.
        """
        return self._noisemap

    @noisemap.setter
    def noisemap(self,
                 noisemap: Optional[np.ndarray[float]]) -> None:
        """Setter for the noise map, doing some validity checks on the input.

        Parameters
        ----------
        noisemap : Optional[np.ndarray[float]]
            The noise map.
        """

        self.__set_array_attr(array = noisemap,
                              name = NOISEMAP_TAG)

    @noisemap.deleter
    def noisemap(self):
        """Simple deleter for the `noisemap` attribute.
        """
        del self._noisemap

    @property
    def segmentation_map(self) -> Optional[np.ndarray[np.int64]]:
        """The segmentation map of the image, which details which pixels correspond to which objects.

        Returns
        -------
        segmentation_map : Optional[np.ndarray[int]]
            The segmentation map of the image, if present; None otherwise.
        """
        return self._segmentation_map

    @segmentation_map.setter
    def segmentation_map(self,
                         segmentation_map: Optional[np.ndarray[int]]) -> None:

        # We use safe casting for the segmentation map, since we could lose very relevant data if we cast e.g. an
        # int64 to an int32
        self.__set_array_attr(array = segmentation_map,
                              name = SEGMENTATION_TAG,
                              casting = "safe")

    @segmentation_map.deleter
    def segmentation_map(self) -> None:
        del self._segmentation_map

    @property
    def background_map(self) -> Optional[np.ndarray[np.float32]]:
        """A background map of the image.

        Returns
        -------
        background_map : Optional[np.ndarray[float]]
            The background map, if present; None otherwise.
        """
        return self._background_map

    @background_map.setter
    def background_map(self, background_map: Optional[np.ndarray[float]]) -> None:
        """Setter for the background map, doing some validity checks on the input.

        Parameters
        ----------
        background_map : Optional[np.ndarray[float]]
            The background map.
        """

        self.__set_array_attr(array = background_map,
                              name = BACKGROUND_TAG)

    @background_map.deleter
    def background_map(self) -> None:
        """Simple deleter for the `background_map` attribute.
        """
        del self._background_map

    @property
    def weight_map(self) -> Optional[np.ndarray[np.float32]]:
        """The weight map of the image.

        Returns
        -------
        weight_map : Optional[np.ndarray[np.float32]]
            The weight map, if present; None otherwise.
        """
        return self._weight_map

    @weight_map.setter
    def weight_map(self, weight_map: Optional[np.ndarray[float]]) -> None:
        """Setter for the weight map, doing some validity checks on the input.

        Parameters
        ----------
        weight_map : Optional[np.ndarray[float]]
            The weight map.
        """

        self.__set_array_attr(array = weight_map,
                              name = WEIGHT_TAG)

    @weight_map.deleter
    def weight_map(self):
        """Simple deleter for the `weight_map` attribute.
        """
        del self._weight_map

    @property
    def header(self) -> Optional[Header]:
        """An astropy header to contain metadata.

        Returns
        -------
        header : Optional[Header]
            The header, if present; None otherwise.
        """
        return self._header

    @header.setter
    def header(self, header: Optional[Header]) -> None:
        """Setter for the header of this image. Note that since the offset is stored in the header,
        it's always deepcopied when set to avoid surprisingly changing the input.

        Parameters
        ----------
        header : Header
            The header to set.
        """

        # Not very pythonic, but to avoid misuse, which could lead to problems when writing to
        # FITS files.
        if not (header is None or isinstance(header, Header)):
            raise ValueError("The header must be an astropy.io.fits.Header instance")

        self._header = header

    @header.deleter
    def header(self):
        """Simple deleter for the `header` attribute.
        """
        del self._header
        self._galsim_wcs = None

    @property
    def offset(self) -> np.ndarray[float]:
        """An (x_offset, y_offset) tuple, tracking the offset of extracted stamps compared to the base image they
        were originally extracted from (that is, the most-distant parent SHEImage).

        Returns
        -------
        offset : np.ndarray[float]
            The (x_offset, y_offset) values, represented as a 1D, 2-element numpy array.
        """
        return self._offset

    @offset.setter
    def offset(self, offset: Optional[Sequence[float]]) -> None:
        """Setter for the offset attribute, which stores it as (0, 0) if None is set.

        Parameters
        ----------
        offset : Optional[Sequence[float]]
            The offset to set. This must have exactly 2 elements, in the order (x_offset, y_offset). If provided as
            None, the offset will be stored as (0,0).
        """
        if offset is None:
            self._offset = np.array([0., 0.], dtype = float)
            return

        if len(offset) != 2:
            raise ValueError("A `SHEImage.offset` must have exactly 2 items")

        self._offset = np.asarray(offset, dtype = float)

    @property
    def wcs(self) -> Optional[astropy.wcs.WCS]:
        """The WCS of the images.

        Returns
        -------
        wcs : Optional[astropy.wcs.WCS]
            The WCS of the images, if present; None otherwise.
        """
        return self._wcs

    @wcs.setter
    def wcs(self, wcs: Optional[astropy.wcs.WCS]) -> None:
        """Convenience setter of the WCS.

        Parameters
        ----------
        wcs : Optional[astropy.wcs.WCS]
            The WCS of the images.
        """
        if not (isinstance(wcs, astropy.wcs.WCS) or (wcs is None)):
            raise TypeError("`wcs` must be None or an instance of `astropy.wcs.WCS`")
        self._wcs = wcs

        # Unload the galsim wcs
        self._galsim_wcs = None

    @wcs.deleter
    def wcs(self) -> None:
        """Simple deleter for the `wcs` attribute.
        """
        del self._wcs
        self._galsim_wcs = None

    @property
    def galsim_wcs(self) -> Optional[galsim.wcs.BaseWCS]:
        """Property to provide a GalSim-style WCS, which has some functions that astropy's lacks.

        Returns
        -------
        galsim_wcs : Optional[galsim.wcs.BaseWCS]
            The WCS, converted to an appropriate GalSim WCS class, if present; None otherwise.
        """

        # If not already loaded, load it
        if self._galsim_wcs is None:
            # Load from the header if possible
            if self.wcs is not None:
                self._galsim_wcs = galsim.wcs.readFromFitsHeader(self.wcs.to_header())[0]
            elif self.header is not None and len(self.header) > 0:
                self._galsim_wcs = galsim.wcs.readFromFitsHeader(self.header)[0]
            else:
                raise ValueError(
                    "`SHEImage` must have a WCS set up or a WCS in its header in order to get a GalSim WCS.")

        return self._galsim_wcs

    @galsim_wcs.setter
    def galsim_wcs(self, galsim_wcs: Optional[galsim.wcs.BaseWCS]):
        """Convenience setter of the GalSim WCS.

        Parameters
        ----------
        galsim_wcs : Optional[galsim.wcs.BaseWCS]
            The GalSim-style WCS to be set.
        """
        if not (isinstance(galsim_wcs, galsim.wcs.BaseWCS) or (galsim_wcs is None)):
            raise TypeError("`galsim_wcs` must be None or an instance of `galsim.wcs.BaseWCS`")
        self._galsim_wcs = galsim_wcs

    @galsim_wcs.deleter
    def galsim_wcs(self):
        """Simple deleter for the `galsim_wcs` attribute.
        """
        del self._galsim_wcs

    @property
    def shape(self) -> np.ndarray[int]:
        """The shape of the image, equivalent to `self.data.shape`.

        Returns
        -------
        shape : np.ndarray[int]
            The shape of the image, as (x_len,y_len)
        """
        return self._shape

    @property
    def det_ix(self) -> int:
        """The x-position of the detector for this image. Will be a value between 1 and 6 inclusive.

        Returns
        -------
        det_ix : int
            The x-position of the detector for this image.
        """
        if self._det_ix is None:
            self.__determine_det_ixy()
        return self._det_ix

    @property
    def det_iy(self):
        """The y-position of the detector for this image. Will be a value between 1 and 6 inclusive.

        Returns
        -------
        det_iy : int
            The y-position of the detector for this image.
        """
        if self._det_iy is None:
            self.__determine_det_ixy()
        return self._det_iy

    @property
    def parent_frame_stack(self) -> Optional[SHEFrameStack]:
        """Reference to the parent `SHEFrameStack`, if it exists; None otherwise. This is stored internally as a weak
        reference to prevent a reference circle which would prevent garbage collection. This means that if the parent
        goes out of scope, this may become None even if previously set to reference the parent.

        Returns
        -------
        parent_frame_stack : Optional[SHEFrameStack]
            This object's parent `SHEFrameStack`, if it exists; None otherwise.
        """
        return self._parent_frame_stack()

    @parent_frame_stack.setter
    def parent_frame_stack(self, parent_frame_stack: Optional[SHEFrameStack]) -> None:
        """Setter for parent_frame_stack, storing the input as a weak reference.

        Parameters
        ----------
        parent_frame_stack : Optional[SHEFrameStack]
            The `SHEFrameStack` object to be referenced as this object's parent.
        """

        if parent_frame_stack is None:
            self._parent_frame_stack = _return_none
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_frame_stack = weakref.ref(parent_frame_stack)

    @parent_frame_stack.deleter
    def parent_frame_stack(self) -> None:
        """Deleter for parent_frame_stack, setting it to return None.
        """
        self._parent_frame_stack = _return_none

    @property
    def parent_frame(self) -> Optional[SHEFrame]:
        """Reference to the parent `SHEFrame`, if it exists; None otherwise. This is stored internally as a weak
        reference to prevent a reference circle which would prevent garbage collection. This means that if the parent
        goes out of scope, this may become None even if previously set to reference the parent.

        Returns
        -------
        parent_frame : Optional[SHEFrame]
            This object's parent `SHEFrame`, if it exists; None otherwise.
        """
        return self._parent_frame()

    @parent_frame.setter
    def parent_frame(self, parent_frame: Optional[SHEFrame]) -> None:
        """Setter for parent_frame, storing the input as a weak reference.

        Parameters
        ----------
        parent_frame : Optional[SHEFrame]
            The `SHEFrame` object to be referenced as this object's parent.
        """

        if parent_frame is None:
            self._parent_frame = _return_none
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_frame = weakref.ref(parent_frame)

    @parent_frame.deleter
    def parent_frame(self) -> None:
        """Deleter for parent_frame, setting it to return None.
        """
        self._parent_frame = _return_none

    @property
    def parent_image_stack(self) -> Optional[SHEImageStack]:
        """Reference to the parent `SHEImageStack`, if it exists; None otherwise. This is stored internally as a weak
        reference to prevent a reference circle which would prevent garbage collection. This means that if the parent
        goes out of scope, this may become None even if previously set to reference the parent.

        Returns
        -------
        parent_image_stack : Optional[SHEImageStack]
            This object's parent `SHEImageStack`, if it exists; None otherwise.
        """
        return self._parent_image_stack()

    @parent_image_stack.setter
    def parent_image_stack(self, parent_image_stack: Optional[SHEImageStack]) -> None:
        """Setter for parent_image_stack, storing the input as a weak reference.

        Parameters
        ----------
        parent_image_stack : Optional[SHEImageStack]
            The `SHEImageStack` object to be referenced as this object's parent.
        """

        if parent_image_stack is None:
            self._parent_image_stack = _return_none
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_image_stack = weakref.ref(parent_image_stack)

    @parent_image_stack.deleter
    def parent_image_stack(self) -> None:
        """Deleter for parent_image_stack, setting it to return None.
        """
        self._parent_image_stack = _return_none

    @property
    def parent_image(self) -> Optional[SHEImage]:
        """Reference to the immediate parent `SHEImage`, if it exists; None otherwise. This is stored internally as a
        weak reference to prevent a reference circle which would prevent garbage collection. This means that
        if the parent goes out of scope, this may become None even if previously set to reference the parent.

        It is possible for a `SHEImage` to have an indefinite chain of parent SHEImage through repeated stamp
        extraction. This attribute stores only the reference to the most-immediate parent SHEImage.

        Returns
        -------
        parent_image : Optional[SHEImage]
            This object's most-immediate parent `SHEImage`, if it exists; None otherwise.
        """
        return self._parent_image()

    @parent_image.setter
    def parent_image(self, parent_image: Optional[SHEImage]) -> None:
        """Setter for parent_image, storing the input as a weak reference.

        Parameters
        ----------
        parent_image : Optional[SHEImage]
            The `SHEImage` object to be referenced as this object's parent.
        """

        if parent_image is None:
            self._parent_image = _return_none
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_image = weakref.ref(parent_image)

    @parent_image.deleter
    def parent_image(self) -> None:
        """Deleter for parent_image, setting it to return None.
        """
        self._parent_image = _return_none

    # Public methods

    def get_object_mask(self,
                        seg_id: int,
                        mask_suspect: bool = False,
                        mask_unassigned: bool = False) -> np.ndarray[np.bool]:
        """Get a mask for pixels that are either bad (and optionally suspect) or don't belong to an object with a
        given ID. The returned mask follows the convention that 0/False = good, 1/True = bad.

        Parameters
        ----------
        seg_id : int
            Segmentation map ID of the object for which to generate a mask. Note that this is generally different
            from the object ID.
        mask_suspect : bool
            If True, suspect pixels will also be masked True.
        mask_unassigned : bool
            If True, pixels which are not assigned to any object will also be masked True.

        Returns
        -------
        object_mask: np.ndarray[np.bool]
            Mask for the desired object. Values of True correspond to masked pixels (bad(/suspect) or don't belong to
            this object).
        """
        # Raise an exception if the mask or segmentation map is None
        if self.mask is None:
            raise ValueError("Cannot get an object mask when mask is None")
        if self.segmentation_map is None:
            raise ValueError("Cannot get an object mask when segmentation_map is None")

        # First get the boolean version of the mask for suspect/bad pixels
        if mask_suspect:
            pixel_mask = as_bool(is_masked_suspect_or_bad(self.mask))
        else:
            pixel_mask = as_bool(is_masked_bad(self.mask))

        # Now get mask for other objects
        other_mask = (self.segmentation_map != seg_id)
        if not mask_unassigned:
            other_mask = np.logical_and(
                other_mask, (self.segmentation_map != SEGMAP_UNASSIGNED_VALUE))

        # Combine and return the masks
        object_mask = np.logical_or(pixel_mask, other_mask)

        return object_mask

    def write_to_fits(self,
                      filepath: str,
                      data_only: bool = False,
                      **kwargs: Any) -> None:
        """Writes the image to disk, in the form of a multi-extension FITS cube.

        The data is written in the primary HDU, and the ancillary data to following HDUs.

        Technical note: the function "transposes" all the arrays written into the FITS file, so that the arrays will
        get shown by DS9 using the convention that the pixel with index [0,0] is bottom left.

        Parameters
        ----------
        filepath : str
            The qualified filename where the file should be written.
        data_only:  bool
            If True, only the science image (`data` attribute) will be written to disk.
        **kwargs : Any
            Additional keyword arguments are passed to the `astropy.io.fits.writeto` function.
        """

        # Set up a fits header with the wcs
        if self.wcs is not None:
            wcs_header = self.wcs.to_header()
            full_header = deepcopy(self.header)
            for label in wcs_header:
                # Overwrite any coming from the WCS
                full_header[label] = (wcs_header[label], wcs_header.comments[label])
        elif self.header is None:
            # An empty header
            full_header = Header()
        else:
            full_header = deepcopy(self.header)

        # Add offset data to the header
        full_header[KEY_X_OFFSET] = self.offset[0]
        full_header[KEY_Y_OFFSET] = self.offset[1]

        # Note that we transpose the numpy arrays, so to have the same pixel
        # convention as DS9 and SExtractor.
        data_hdu = astropy.io.fits.PrimaryHDU(self.data.transpose(), header = full_header)

        hdu_list = astropy.io.fits.HDUList([data_hdu])

        if not data_only:

            for name, attr in D_ATTR_CONVERSIONS.items():
                if name == SCI_TAG:
                    continue
                if getattr(self, attr) is not None:
                    hdu = astropy.io.fits.ImageHDU(getattr(self, attr).transpose(), name = name)
                    hdu_list.append(hdu)

        write_fits(hdu_list = hdu_list,
                   filename = filepath,
                   **kwargs)

    @classmethod
    def read_from_fits(cls,
                       filepath: str,
                       workdir: str = DEFAULT_WORKDIR,
                       **kwargs: Optional[str]) -> SHEImage:
        """Reads an image from a FITS file, such as written by write_to_fits(), and returns it as a SHEImage object.

        This function can be used to read previously saved SHEImage objects (in this case, just give the filepath),
        or to import other "foreign" FITS images (then you'll need the optional keyword arguments).
        When reading from one or several of these foreign files, you can
          - specify a specific HDU to read the mask from, e.g., by setting mask_ext='FLAG'
          - specify a different file to read the mask from, e.g., mask_filepath='mask.fits', mask_ext=0
          - avoid reading-in a mask, by specifying both mask_ext=None and mask_filepath=None
            (results in a default zero mask)
        Idem for the noisemap and the segmap

        Technical note: all the arrays read from FITS get "transposed", so that the array-properties of SHEImage can be
        indexed with [x,y] using the same orientation-convention as DS9 and SExtractor uses, that is,
        [0,0] is bottom left.

        Parameters
        ----------
        filepath : str
            path to the FITS file containing the primary data and header to be read
        workdir : str
            The working directory, where files can be found
        **kwargs : str
            Deprecated keyword arguments, maintained for now to avoid breaking existing interfaces.

        Returns
        -------
        image : SHEImage
            The image object read from the FITS file.
        """

        # Get the HDU name of the `data` attribute from the kwargs
        data_hdu = cls.__get_hdu_kwarg(attr_name = SCI_TAG,
                                       kwargs = kwargs,
                                       default_value = PRIMARY_TAG)

        # Reading the primary extension, which also contains the header
        qualified_filepath = os.path.join(workdir, filepath)
        (data, header) = cls._get_specific_hdu_content_from_fits(
            qualified_filepath, ext = data_hdu, return_header = True)

        # Set up the WCS before we clean the header
        try:
            wcs = astropy.wcs.WCS(header)
        except KeyError:
            # No WCS information
            wcs = None

        # Removing the mandatory cards (that were automatically added to the
        # header if write_to_fits was used)
        logger.debug("The raw primary header has %d keys", len(list(header.keys())))
        cls.__remove_header_keywords(header = header,
                                     l_keywords_to_remove = ["SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "EXTEND"])
        if wcs is not None:
            cls.__remove_header_keywords(header = header,
                                         l_keywords_to_remove = list(wcs.to_header().keys()))

        logger.debug("The cleaned header has %d keys", len(list(header.keys())))

        # Read in each attr
        d_attrs: Dict[str, Optional[np.ndarray]] = {}
        for name, attr in D_ATTR_CONVERSIONS.items():
            if name == SCI_TAG:
                continue
            special_filepath = cls.__get_filename_kwarg(attr_name = name,
                                                        kwargs = kwargs,
                                                        default_value = None)
            ext = cls.__get_hdu_kwarg(attr_name = name,
                                      kwargs = kwargs,
                                      default_value = name)
            d_attrs[attr] = cls._get_secondary_data_from_fits(primary_filepath = qualified_filepath,
                                                              special_filepath = special_filepath,
                                                              ext = ext)

        # Getting the offset from the header
        if KEY_X_OFFSET not in header or KEY_Y_OFFSET not in header:
            offset = np.array([0., 0.])
        else:
            offset = np.array([header[KEY_X_OFFSET], header[KEY_Y_OFFSET]])
            header.remove(KEY_X_OFFSET)
            header.remove(KEY_Y_OFFSET)

        # Building and returning the new object
        new_image = SHEImage(data = data,
                             **d_attrs,
                             header = header,
                             offset = offset,
                             wcs = wcs)

        logger.info("Read %s from the file '%s'", str(new_image), filepath)
        return new_image

    @staticmethod
    def __remove_header_keywords(header: Header,
                                 l_keywords_to_remove: Iterable[str], ):
        """Private method to remove a list of keywords from a FITS header.
        """
        for keyword in l_keywords_to_remove:
            if keyword in header:
                header.remove(keyword)

    @classmethod
    def _get_secondary_data_from_fits(cls, primary_filepath, special_filepath, ext):
        """Private helper for getting mask or noisemap, defining the logic of the related keyword arguments

        This function might return None, if both special_filepath and ext are None, or if the extension doesn't
        exist in the file.
        """

        if special_filepath is None:
            filepath = primary_filepath
        else:
            filepath = special_filepath

        try:
            return cls._get_specific_hdu_content_from_fits(filepath, ext = ext)
        except KeyError:
            logger.debug("Extension %s not found in fits file %s", ext, filepath)
            return None

    @classmethod
    def _get_specific_hdu_content_from_fits(cls, filepath, ext = None, return_header = False):
        """Private helper to handle access to particular extensions of a FITS file

        This function either returns something not-None, or raises an exception.
        Note that this function also takes care of transposing the data.
        """

        logger.debug("Reading from file '%s'...", filepath)

        hdulist = astropy.io.fits.open(filepath)
        num_hdus = len(hdulist)

        if ext is None:
            # Warn the user, as the situation is not clear
            if num_hdus > 1:
                logger.warning(
                    "File '%s' has several HDUs, but no extension was specified! Using primary HDU.",
                    filepath)
            ext = PRIMARY_TAG

        logger.debug("Accessing extension '%s' out of %d available HDUs...", ext, num_hdus)
        data = hdulist[ext].data.transpose()
        if not data.ndim == 2:
            raise ValueError("Primary HDU must contain a 2D image")
        header = hdulist[ext].header

        hdulist.close()

        if return_header:
            return data, header
        return data

    def _extract_attr_stamp(self, xmin, ymin, xmax, ymax, attr_name, filename, hdu_i):
        if (xmax - xmin) <= 0 or (ymax - ymin) <= 0:
            return None
        a = getattr(self, D_ATTR_CONVERSIONS[attr_name])
        if a is not None and a.shape[0] > 0 and a.shape[1] > 0:
            out = a[xmin:xmax, ymin:ymax]
        elif filename is not None and hdu_i is not None:
            out = _read_stamp(xmin, ymin, xmax, ymax, filename, hdu_i)
        else:
            out = None
        return out

    def extract_wcs_stamp(self, x, y, none_if_out_of_bounds = False):
        """ Extracts an "empty" stamp, which contains only information needed for WCS operations, having the
            interface of a standard SHEImage.
        """

        # If we're returning None if out of bounds, check now so we can exit
        # early
        if none_if_out_of_bounds and ((x < 0) or (x >= self.shape[0]) or
                                      (x < 0) or (x >= self.shape[1])):
            return None

        new_offset = self.offset + np.array([x, y])

        new_image = SHEImage(
            data = np.ndarray(shape = (0, 0), dtype = float),
            mask = None,
            noisemap = None,
            segmentation_map = None,
            background_map = None,
            weight_map = None,
            header = self.header,
            offset = new_offset,
            wcs = self.wcs,
            parent_image = self,
            )

        return new_image

    def extract_stamp(self,
                      x: float,
                      y: float,
                      width: int = DEFAULT_STAMP_SIZE,
                      height: Optional[int] = None,
                      indexconv: str = "numpy",
                      keep_header: bool = False,
                      none_if_out_of_bounds: bool = False,
                      force_all_properties: bool = False,
                      **kwargs):
        """Extracts a stamp and returns it as a new None (using views of numpy arrays, i.e., without making a copy)

        The extracted stamp is centered on the given (x,y) coordinates and has shape (width, height).
        To define this center, two alternative indexing-conventions are implemented, which differ by a small shift:
            - "numpy" follows the natural indexing of numpy arrays extended to floating-point axes.
                The bottom-left pixel spreads from (x,y) = (0.0, 0.0) to (1.0,1.0).
                Therefore, this pixel is centered on (0.5, 0.5), and you would
                use extract_stamp(x=0.5, y=0.5, w=1) to extract this pixel.
                Note the difference to the usual numpy integer array indexing, where this pixel would be a[0,0]
            - "sextractor" follows the convention from SExtractor and (identically) DS9, where the bottom-left pixel
                spreads from (0.5, 0.5) to (1.5, 1.5), and is therefore centered on (1.0, 1.0).

        Bottom line: if SExtractor told you that there is a galaxy at a certain position, you can use this position
        directly to extract a statistically-well-centered stamp as long as you set indexconv="sextractor".

        The stamp can be partially (or even completely) outside of the image. Pixels of the stamp outside of the image
        will be set to zero, and masked.


        Parameters
        ----------
        x : float
            x pixel coordinate on which to center the stamp.
        y : float
            idem for y
        width : int
            the width of the stamp to extract
        height : int
            the height. If left to None, a square stamp (width x width) will get extracted.
        indexconv : {"numpy", "sextractor"}
            Selects the indexing convention to use to interpret the position (x,y). See text above.
        keep_header : bool
            Set this to True if you want the stamp to get the header of the original image.
            By default (False), the stamp gets an empty header.
        none_if_out_of_bounds : bool
            Set this to True if you want this method to return None if the stamp is entirely out of bounds of the
            image. By default, this is set to False, which means it will instead return an entirely masked image in
            that case.
        force_all_properties : bool
            Set this to True if you want to ensure that all properties of the stamp exist, even if they don't for
            the parent. This will fill them in with default values.
        **kwargs : Dict
            (Deprecated and to be removed soon; do not use.)

        Return
        ------
        SHEImage
            The extracted stamp.

        """

        width, height = self._validate_read_stamp_input(width = width,
                                                        height = height,
                                                        indexconv = indexconv)

        # Identify the numpy stamp boundaries
        xmin = int(round(x - width / 2.0 - D_INDEXCONV_DEFS[indexconv]))
        ymin = int(round(y - height / 2.0 - D_INDEXCONV_DEFS[indexconv]))
        xmax = xmin + width
        ymax = ymin + height

        # If we're returning None if out of bounds, check now so we can exit
        # early
        if none_if_out_of_bounds and ((xmax < 0) or (xmin >= self.shape[0]) or
                                      (ymax < 0) or (ymin >= self.shape[1])):
            return None

        # Get the header we'll use for the new stamp
        new_header = self.header if keep_header else None

        # And defining the offset property of the stamp, taking into account
        # any current offset.
        new_offset = self.offset + np.array([xmin, ymin])

        # If these bounds are fully within the image range, the extraction is
        # easy.
        if xmin >= 0 and xmax < self.shape[0] and ymin >= 0 and ymax < self.shape[1]:

            new_stamps = self._extract_stamp_in_bounds(xmin, xmax,
                                                       ymin, ymax,
                                                       **kwargs)

        else:

            new_stamps = self._extract_stamp_not_in_bounds(xmin, xmax,
                                                           ymin, ymax,
                                                           **kwargs)

        # Create the new object
        new_image = SHEImage(
            data = new_stamps[SCI_TAG],
            mask = new_stamps[MASK_TAG],
            noisemap = new_stamps[NOISEMAP_TAG],
            segmentation_map = new_stamps[SEGMENTATION_TAG],
            background_map = new_stamps[BACKGROUND_TAG],
            weight_map = new_stamps[WEIGHT_TAG],
            header = new_header,
            offset = new_offset,
            wcs = self.wcs,
            parent_image = self,
            parent_frame = self.parent_frame,
            parent_frame_stack = self.parent_frame_stack,
            )

        assert new_image.shape == (width, height)

        # If we're forcing all properties, add defaults now
        if force_all_properties:
            new_image.add_default_mask(force = False)
            new_image.add_default_noisemap(force = False)
            new_image.add_default_segmentation_map(force = False)
            new_image.add_default_background_map(force = False)
            new_image.add_default_weight_map(force = False)
            new_image.add_default_header(force = False)
            new_image.add_default_wcs(force = False)

        return new_image

    def _extract_stamp_in_bounds(self,
                                 xmin, xmax,
                                 ymin, ymax,
                                 **kwargs):
        """Private method to handle extraction of a postage stamp when we know it's entirely within bounds.
        """

        new_stamps = {}

        # We are fully within the image
        logger.debug("Extracting stamp [%d:%d,%d:%d] fully within image of shape (%d,%d)",
                     xmin, xmax, ymin, ymax, self.shape[0], self.shape[1])
        for attr_name in D_ATTR_CONVERSIONS:

            filename = self.__get_filename_kwarg(attr_name, kwargs)
            hdu = self.__get_hdu_kwarg(attr_name, kwargs)

            new_stamps[attr_name] = self._extract_attr_stamp(xmin, ymin, xmax, ymax, attr_name, filename,
                                                             hdu)

        return new_stamps

    def _extract_stamp_not_in_bounds(self, xmin, xmax, ymin, ymax, **kwargs):
        """Private method to handle extraction of a postage stamp when we know it's not entirely within bounds.
        """

        new_stamps = {}

        # We are not fully within the image
        logger.debug("Extracting stamp [%d:%d,%d:%d] not entirely within image of shape (%d,%d)",
                     xmin, xmax, ymin, ymax, self.shape[0], self.shape[1])

        # One solution would be to pad the image and extract, but that would need a lot of memory.
        # So instead we go for the more explicit bound computations.

        # Compute the bounds of the overlapping part of the stamp in the
        # original image
        overlap_xmin = max(xmin, 0)
        overlap_ymin = max(ymin, 0)
        overlap_xmax = min(xmax, self.shape[0])
        overlap_ymax = min(ymax, self.shape[1])
        overlap_width = overlap_xmax - overlap_xmin
        overlap_height = overlap_ymax - overlap_ymin
        overlap_slice = (slice(overlap_xmin, overlap_xmax),
                         slice(overlap_ymin, overlap_ymax))
        logger.debug("overlap_slice: %s", str(overlap_slice))

        # Check if we have any actual overlap
        overlap_exists = overlap_width > 0 and overlap_height > 0
        if not overlap_exists:
            logger.warning("The extracted stamp is entirely outside of the image bounds!")

        # Compute the bounds of this same overlapping part in the new stamp
        # The indexes of the stamp are simply shifted with respect to those
        # of the original image by (xmin, ymin)
        overlap_xmin_stamp = overlap_xmin - xmin
        overlap_xmax_stamp = overlap_xmax - xmin
        overlap_ymin_stamp = overlap_ymin - ymin
        overlap_ymax_stamp = overlap_ymax - ymin
        overlap_slice_stamp = (slice(overlap_xmin_stamp, overlap_xmax_stamp),
                               slice(overlap_ymin_stamp, overlap_ymax_stamp))

        # Read in the overlap data
        for attr_name in D_ATTR_CONVERSIONS:

            filename = self.__get_filename_kwarg(attr_name, kwargs)
            hdu = self.__get_hdu_kwarg(attr_name, kwargs)

            # We first create new stamps, and we will later fill part of them
            # with slices of the original.
            base_image = getattr(self, D_ATTR_CONVERSIONS[attr_name])
            if base_image is None and filename is None:
                new_stamps[attr_name] = None
            else:
                # Get the data type for this image
                new_dtype = D_IMAGE_DTYPES[attr_name] if D_IMAGE_DTYPES[attr_name] is not None else base_image.dtype

                # Construct a base image filled with the default value
                new_stamps[attr_name] = D_DEFAULT_IMAGE_VALUES[attr_name] * np.ones((xmax - xmin, ymax - ymin),
                                                                                    dtype = new_dtype)

            extracted_stamp = self._extract_attr_stamp(overlap_xmin,
                                                       overlap_ymin,
                                                       overlap_xmax,
                                                       overlap_ymax,
                                                       attr_name,
                                                       filename,
                                                       hdu)

            # Fill the stamp arrays:
            # If there is any overlap
            if overlap_exists and extracted_stamp is not None:
                new_stamps[attr_name][overlap_slice_stamp] = extracted_stamp

        return new_stamps

    @staticmethod
    def _validate_read_stamp_input(width: float,
                                   height: Optional[float],
                                   indexconv: str) -> Tuple[int, int]:
        """Validates input to the `read_stamp` method, and adjusts height and width as appropriate.

        """
        # Should we extract a square stamp?
        if height is None:
            height = width

        # Silently coerce width and height to integers
        width = int(round(width))
        height = int(round(height))

        # Check stamp size
        if width < 1 or height < 1:
            raise ValueError("Stamp height and width must at least be 1")
        # Dealing with the indexing conventions
        if indexconv not in D_INDEXCONV_DEFS:
            raise ValueError("Argument indexconv must be among {}".format(list(D_INDEXCONV_DEFS.keys())))

        return width, height

    def add_default_mask(self, force = False):
        """Adds a default mask to this object (all unmasked). If force=True, will overwrite an existing mask.
        """

        if self.mask is not None:
            if force is True:
                logger.debug("Overwriting existing mask with default.")
            else:
                logger.debug("Not overwriting existing mask with default.")
                return

        self.mask = np.zeros_like(self.data, dtype = np.int32)

    def add_default_noisemap(self, force = False, suppress_warnings = False):
        """Adds a default noisemap to this object (all 0.). If force=True, will overwrite an existing noisemap.
        """

        if self.noisemap is not None:
            if force is True:
                logger.debug("Overwriting existing noisemap with default.")
            else:
                logger.debug("Not overwriting existing noisemap with default.")
                return

        # Try to calculate the noisemap

        # Get the gain and read_noise from the MDB if possible
        try:
            gain = mdb.get_gain(suppress_warnings = suppress_warnings)
            read_noise = mdb.get_read_noise(suppress_warnings = suppress_warnings)
        except RuntimeError as e:
            if "mdb module must be initialised with MDB xml object before use." not in str(e):
                raise
            warn_mdb_not_loaded()
            # Use default values for gain and read_noise
            gain = 3.1
            read_noise = 4.5

        # Start by setting to the read noise level
        self.noisemap = read_noise / gain * np.ones_like(self.data, dtype = float)

        # Check if we have a background map
        if self.background_map is not None:
            self.noisemap += np.sqrt(self.background_map / gain)

    def add_default_segmentation_map(self, force = False):
        """Adds a default segmentation_map to this object (all unassigned). If force=True, will overwrite an existing
        segmentation_map.
        """

        if self.segmentation_map is not None:
            if force is True:
                logger.debug("Overwriting existing segmentation_map with default.")
            else:
                logger.debug("Not overwriting existing segmentation_map with default.")
                return

        self.segmentation_map = SEGMAP_UNASSIGNED_VALUE * np.ones_like(self.data, dtype = np.int32)

    def add_default_background_map(self, force = False):
        """Adds a default background_map to this object (all 0.). If force=True, will overwrite an existing
        background_map.
        """

        if self.background_map is not None:
            if force is True:
                logger.debug("Overwriting existing background_map with default.")
            else:
                logger.debug("Not overwriting existing background_map with default.")
                return

        self.background_map = np.zeros_like(self.data, dtype = float)

    def add_default_weight_map(self, force = False):
        """Adds a default weight_map to this object (all 0.). If force=True, will overwrite an existing
        weight_map.
        """

        if self.weight_map is not None:
            if force is True:
                logger.debug("Overwriting existing weight_map with default.")
            else:
                logger.debug("Not overwriting existing weight_map with default.")
                return

        self.weight_map = np.ones_like(self.data, dtype = float)

    def add_default_header(self, force = False):
        """Adds a default header to this object (only required values). If force=True, will overwrite an existing
        header.
        """

        if self.header is not None:
            if force is True:
                logger.debug("Overwriting existing header with default.")
            else:
                logger.debug("Not overwriting existing header with default.")
                return

        self.header = Header()

    def add_default_wcs(self, force = False):
        """Adds a default wcs to this object (pixel scale 1.0). If force=True, will overwrite an existing wcs.
        """

        if self.wcs is not None:
            if force is True:
                logger.debug("Overwriting existing wcs with default.")
            else:
                logger.debug("Not overwriting existing wcs with default.")
                return

        self.wcs = astropy.wcs.WCS(Header())

    def pix2world(self, x, y, origin = 0):
        """Converts x and y pixel coordinates to ra and dec world coordinates.

        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y
        origin : int
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)

        Raises
        ------
        AttributeError : if this object does not have a wcs set up

        Returns
        -------
        ra : float (in degrees)
        dec : float (in degrees)

        """

        if self.wcs is None:
            raise AttributeError(
                "pix2world called by SHEImage object that doesn't have a WCS set up.")

        # Correct for offset if applicable
        if self.offset is not None:
            x = x + self.offset[0]
            y = y + self.offset[1]

        ra, dec = self.wcs.all_pix2world(x, y, origin)

        # If input was scalars, output scalars
        if (not hasattr(x, '__len__')) and (not hasattr(y, '__len__')):
            ra = float(ra)
            dec = float(dec)

        return ra, dec

    def world2pix(self, ra, dec, origin = 0):
        """Converts ra and dec world coordinates to x and y pixel coordinates

        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees
        dec : float
            Declination (Dec) world coordinate in degrees
        origin : int
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up

        Returns
        -------
        x : float
        y : float

        """

        if self.wcs is None:
            raise AttributeError(
                "world2pix called by SHEImage object that doesn't have a WCS set up.")

        x, y = self.wcs.all_world2pix(ra, dec, origin)

        # Correct for offset if applicable
        if self.offset is not None:
            x = x - self.offset[0]
            y = y - self.offset[1]

        # If input was scalars, output scalars
        if (not hasattr(ra, '__len__')) and (not hasattr(dec, '__len__')):
            x = float(x)
            y = float(y)

        return x, y

    def get_pix2world_transformation(self,
                                     x: Optional[float] = None,
                                     y: Optional[float] = None,
                                     dx: float = 0.1,
                                     dy: float = 0.1,
                                     spatial_ra: bool = False,
                                     origin: {0, 1} = 0,
                                     norm: bool = False) -> np.ndarray:
        """Gets the local transformation matrix between pixel and world (ra/dec) coordinates at the specified location.

        Parameters
        ----------
        x : Optional[float]
            x pixel coordinate. If not provided, will use centre of image
        y : Optional[float]
            idem for y
        dx : float
            Differential x step to use in calculating transformation matrix. Default 0.1 pixels
        dy : float
            idem for y
        spatial_ra : bool
            If True, will give a matrix for (-ra*cos(dec),dec) co-ordinates instead of (ra,dec) (default False)
        origin : {0,1}
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)
        norm : bool
            If True, will divide the result by the determinant, resulting in the area-free
            transformation (default False)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dx or dy is 0

        Returns
        -------
        pix2world_transformation : np.array
            Transformation matrix in the format [[  dra/dx ,  dra/dy ],
                                                 [ ddec/dx , ddec/dy ]]

        """

        if (dx == 0) or (dy == 0):
            raise ValueError("Differentials dx and dy must not be zero.")

        # If x or y isn't provided, use the centre of the image
        if x is None:
            x = (self.shape[0] - 1) / 2.
        if y is None:
            y = (self.shape[1] - 1) / 2.

        # Correct for offset if applicable
        if self.offset is not None:
            x = x + self.offset[0]
            y = y + self.offset[1]

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        ra_0, dec_0 = self.pix2world(x, y, origin = origin)
        ra_px, dec_px = self.pix2world(x + dx, y, origin = origin)
        ra_py, dec_py = self.pix2world(x, y + dy, origin = origin)

        if spatial_ra:
            ra_scale = -np.cos(dec_0 * np.pi / 180)
        else:
            ra_scale = 1

        d_ra_x = ra_scale * (ra_px - ra_0) / dx
        d_dec_x = (dec_px - dec_0) / dx

        d_ra_y = ra_scale * (ra_py - ra_0) / dy
        d_dec_y = (dec_py - dec_0) / dy

        pix2world_transformation = np.array([[d_ra_x, d_ra_y],
                                             [d_dec_x, d_dec_y]])

        if norm:
            det = np.linalg.det(pix2world_transformation)
            pix2world_transformation /= np.sqrt(np.sign(det) * det)

        return pix2world_transformation

    def get_world2pix_transformation(self, ra = None, dec = None, dra = 0.01 / 3600, ddec = 0.01 / 3600,
                                     spatial_ra = False,
                                     origin = 0, norm = False):
        """Gets the local transformation matrix between world (ra/dec) and pixel coordinates at the specified location.

        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees. If both this and dec are None, will default to centre of
            image
        dec : float
            Declination (Dec) world coordinate in degrees. If both this and ra are None, will default to centre of
            image
        dra : float
            Differential ra step in degrees to use in calculating transformation matrix. Default 0.01 arcsec
        ddec : float
            idem for dec
        spatial_ra : bool
            If True, will give a matrix for (-ra*cos(dec),dec) co-ordinates instead of (ra,dec) (default False)
        origin : int
            Unused for this method; left in to prevent user surprise
        norm : bool
            If True, will divide the result by the determinant, resulting in the area-free transformation
            (default False)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dra or ddec is 0

        Returns
        -------
        world2pix_transformation : np.array
            Transformation matrix in the format [[ dx/dra , dx/ddec ],
                                                 [ dy/dra , dy/ddec ]]

        """

        if (dra == 0) or (ddec == 0):
            raise ValueError("Differentials dra and ddec must not be zero.")

        if ra is None and dec is None:
            x = (self.shape[0] - 1) / 2.
            y = (self.shape[1] - 1) / 2.

            ra, dec = self.pix2world(x, y, origin = 0)
        elif (ra is None) != (dec is None):
            raise ValueError("In get_world2pix_transformation, either both ra and dec must be specified or both " +
                             "must be None/unspecified.")

        if spatial_ra:
            ra_scale = -np.cos(dec * np.pi / 180)
        else:
            ra_scale = 1

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        x_0, y_0 = self.world2pix(ra, dec, origin = origin)
        x_p_ra, y_p_ra = self.world2pix(ra + dra, dec, origin = origin)
        x_p_dec, y_p_dec = self.world2pix(ra, dec + ddec, origin = origin)

        d_x_ra = (x_p_ra - x_0) / (dra * ra_scale)
        d_y_ra = (y_p_ra - y_0) / (dra * ra_scale)

        d_x_dec = (x_p_dec - x_0) / ddec
        d_y_dec = (y_p_dec - y_0) / ddec

        world2pix_transformation = np.array([[d_x_ra, d_x_dec],
                                             [d_y_ra, d_y_dec]])

        if norm:
            det = np.linalg.det(world2pix_transformation)
            world2pix_transformation /= np.sqrt(np.sign(det) * det)

        return world2pix_transformation

    def get_pix2world_rotation(self, x, y, dx = 0.1, dy = 0.1, origin = 0):
        """Gets the local rotation matrix between pixel and world (ra/dec) coordinates at the specified location.
        Note that this doesn't provide the full transformation since it lacks scaling and shearing terms.

        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y
        dx : float
            Differential x step to use in calculating rotation matrix. Default 0.1 pixels
        dy : float
            idem for y
        origin : int
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dx or dy is 0

        Returns
        -------
        pix2world_rotation : np.array
            Transformation matrix in the format [[ cos(theta) , -sin(theta) ],
                                                 [ sin(theta) ,  cos(theta) ]]
            Note that due to the method of calculation, the matrix may differ very slightly from an ideal
            rotation matrix.
        """

        # dx and dy are checked in get_pix2world_transformation, so no need to check here
        # It also handles the addition of the offset to x and y

        pix2world_transformation = self.get_pix2world_transformation(
            x, y, dx, dy, spatial_ra = True, origin = origin)

        u, _, vh = np.linalg.svd(pix2world_transformation)

        pix2world_rotation = vh @ u

        return pix2world_rotation

    def get_world2pix_rotation(self, ra, dec, dra = 0.01 / 3600, ddec = 0.01 / 3600, origin = 0):
        """Gets the local rotation matrix between world (ra/dec) and pixel coordinates at the specified location.
        Note that this doesn't provide the full transformation since it lacks scaling and shearing terms.

        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees
        dec : float
            Declination (Dec) world coordinate in degrees
        dra : float
            Differential ra step in degrees to use in calculating transformation matrix. Default 0.01 arcsec
        ddec : float
            idem for dec
        origin : int
            Unused for this method; left in to prevent user surprise

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dra or ddec is 0

        Returns
        -------
        world2pix_rotation : np.array
            Transformation matrix in the format [[ cos(theta) , -sin(theta) ],
                                                 [ sin(theta) ,  cos(theta) ]]
            Note that due to the method of calculation, the matrix may differ very slightly from an ideal
            rotation matrix.

        """

        # dx and dy are checked in get_pix2world_transformation, so no need to
        # check here

        world2pix_transformation = self.get_world2pix_transformation(
            ra, dec, dra, ddec, spatial_ra = True, origin = origin)

        u, _, vh = np.linalg.svd(world2pix_transformation)

        world2pix_rotation = vh @ u

        return world2pix_rotation

    def get_pix2world_decomposition(self,
                                    x: Optional[float] = None,
                                    y: Optional[float] = None) -> Tuple[float,
                                                                        Shear,
                                                                        Angle,
                                                                        bool]:
        """Gets the local WCS decomposition between image (x/y) and world (ra/dec) coordinates at the specified
        location.

        Note 1: Since shear and rotation are non-commutative, the rotation operation must be applied before shear.

        Note 2: If testing against a galsim.wcs.ShearWCS class, note that the shear defined as input to that class
          is the world-to-pixel shear, while the scale is the pixel-to-world scale, which can lead to some confusion
          if decomposed.

        Parameters
        ----------
        x : float
            x pixel coordinate. If None, will use centre
        y : float
            idem for y

        Raises
        ------
        AttributeError
            This object does not have a wcs set up

        Returns
        -------
        scale : float
            Scale factor of the decomposition
        shear : galsim.Shear
        theta : coord.Angle
        flip : bool

        """

        # If x or y isn't provided, use the centre of the image
        if x is None:
            x = (self.shape[0] - 1) / 2.
        if y is None:
            y = (self.shape[1] - 1) / 2.

        # Correct for offset if applicable
        if self.offset is not None:
            x = x + self.offset[0]
            y = y + self.offset[1]

        local_wcs: galsim.wcs.JacobianWCS = self.galsim_wcs.jacobian(image_pos = galsim.PositionD(x, y))

        return local_wcs.getDecomposition()

    def get_world2pix_decomposition(self,
                                    ra: Optional[float] = None,
                                    dec: Optional[float] = None) -> Tuple[float,
                                                                          Shear,
                                                                          Angle,
                                                                          bool]:
        """Gets the local WCS decomposition between world (ra/dec) and pixel coordinates at the specified location.

        Note 1: Since shear and rotation are non-commutative, the rotation operation must be applied before shear.

        Note 2: If testing against a galsim.wcs.ShearWCS class, note that the shear defined as input to that class
          is the world-to-pixel shear, while the scale is the pixel-to-world scale, which can lead to some confusion
          if decomposed.

        Parameters
        ----------
        ra : Optional[float]
            Right Ascension (RA) world coordinate in degrees. If both ra and dec are None, will use the centre of the
            image
        dec : Optional[float]
            Declination (Dec) world coordinate in degrees. If both ra and dec are None, will use the centre of the image


        Raises
        ------
        AttributeError
            This object does not have a wcs set up

        Returns
        -------
        scale : float
            Scale factor of the decomposition
        shear : galsim.Shear
        theta : galsim.Angle
        flip : bool

        """

        if ra is None and dec is None:
            x = (self.shape[0] - 1) / 2.
            y = (self.shape[1] - 1) / 2.

            ra, dec = self.pix2world(x, y, origin = 0)
        elif (ra is None) != (dec is None):
            raise ValueError("In get_world2pix_transformation, either both ra and dec must be specified or both " +
                             "must be None/unspecified.")

        world_pos: Union[galsim.PositionD, galsim.CelestialCoord]
        if isinstance(self.galsim_wcs, galsim.wcs.CelestialWCS):
            world_pos = galsim.CelestialCoord(ra * galsim.degrees, dec * galsim.degrees)
        else:
            world_pos = galsim.PositionD(ra, dec)

        try:

            local_wcs: galsim.wcs.JacobianWCS = self.galsim_wcs.jacobian(world_pos = world_pos)

        except ValueError as e:

            if "WCS does not have longitude type" not in str(e) or len(self.header) == 0:
                raise

            self._apply_galsim_bug_workaround()

            local_wcs: galsim.wcs.JacobianWCS = self.galsim_wcs.jacobian(world_pos = world_pos)

        # We need to use the inverse of the local wcs to get the pix2world decomposition

        return local_wcs.inverse().getDecomposition()

    def _apply_galsim_bug_workaround(self):
        """Workaround for a bug with GalSim WCS, by reading WCS directly from the header.
        """

        warn_galsim_wcs_bug_workaround()

        self._galsim_wcs = galsim.wcs.readFromFitsHeader(self.header)[0]

        if hasattr(self.galsim_wcs, "scale") and np.isclose(self.galsim_wcs.scale, 1.0):

            # Don't have the information in this stamp's header - check for a parent image
            if self.parent_image is not None:
                self._galsim_wcs = galsim.wcs.readFromFitsHeader(self.parent_image.header)[0]
                if self.galsim_wcs.isPixelScale() and np.isclose(self.galsim_wcs.scale, 1.0):
                    raise ValueError("Galsim WCS seems to not have been loaded correctly.")
            else:
                raise ValueError("Galsim WCS seems to not have been loaded correctly.")

    def estimate_pix2world_rotation_angle(self, x, y, dx, dy, origin = 0):
        """Estimates the local rotation angle between pixel and world (-ra/dec) coordinates at the specified location.
        Note that due to distortion in the transformation, this method is inaccurate and depends on the choice of dx
        and dy; get_pix2world_rotation should be used instead to provide the rotation matrix. This method is retained
        to aid testing of that method.

        Parameters
        ----------
        x : float
            x pixel coordinate. Note: dx and dy are required here since, due to distortion in the transformation,
            we can't assume the rotation angle will be independent of them.
        y : float
            idem for y
        dx : float
            Differential x step to use in calculating transformation matrix
        dy : float
            idem for y
        origin : {0,1}
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dx and dy are 0, or dec is too close to pole

        Returns
        -------
        rotation_angle : float
            Rotation angle from pixel coords to world coords in radians

        """

        # Correct for offset if applicable
        if self.offset is not None:
            x = x + self.offset[0]
            y = y + self.offset[1]

        if (dx == 0) and (dy == 0):
            raise ValueError("Differentials dx and dy must not both be zero.")

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        ra_0, dec_0 = self.pix2world(x, y, origin = origin)
        ra_1, dec_1 = self.pix2world(x + dx, y + dy, origin = origin)

        cos_dec = np.cos(dec_0 * np.pi / 180)

        if cos_dec <= 0.01:
            raise ValueError("Dec too close to pole for accurate calculation.")

        dra = -(ra_1 - ra_0)
        ddec = (dec_1 - dec_0)

        x_y_angle = np.arctan2(dx, dy)
        ra_dec_angle = np.arctan2(dra * cos_dec, ddec)

        rotation_angle = ra_dec_angle - x_y_angle

        return rotation_angle

    def estimate_world2pix_rotation_angle(self,
                                          ra: float,
                                          dec: float,
                                          dra: float = 0.01 / 3600,
                                          ddec: float = 0.01 / 3600,
                                          origin: {0, 1} = 0) -> float:
        """Gets the local rotation angle between world (-ra/dec) and pixel coordinates at the specified location.
        Note that due to distortion in the transformation, this method is inaccurate and depends on the choice of dra
        and ddec; get_world2pix_rotation should be used instead to provide the rotation matrix. This method is retained
        to aid testing of that method.

        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees
        dec : float
            Declination (Dec) world coordinate in degrees
        dra : float
            Differential ra step in degrees to use in calculating transformation matrix. Note: dra and ddec are
            required here since, due to distortion in the transformation, we can't assume the rotation angle will be
            independent of them.
        ddec : float
            idem for dec
        origin : {0,1}
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)



        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dra and ddec are 0, or dec is too close to pole

        Returns
        -------
        rotation_angle : float
            Rotation angle from world coords to pixel coords in radians

        """

        if (dra == 0) and (ddec == 0):
            raise ValueError("Differentials dx and dy must not both be zero.")

        cos_dec = np.cos(dec * np.pi / 180)

        if cos_dec <= 0.01:
            raise ValueError("Dec too close to pole for accurate calculation.")

        # We'll calculate the transformation empirically by using small steps in x and y
        x_0, y_0 = self.world2pix(ra, dec, origin = origin)
        x_1, y_1 = self.world2pix(ra - dra, dec + ddec, origin = origin)

        dx = (x_1 - x_0)
        dy = (y_1 - y_0)

        x_y_angle = np.arctan2(dx, dy)
        ra_dec_angle = np.arctan2(dra * cos_dec, ddec)

        rotation_angle = x_y_angle - ra_dec_angle

        return rotation_angle

    def get_objects_in_detector(self, objects_coords, x_buffer = 0., y_buffer = 0.):
        """Returns an array containing the indices of the objects in the detector, and arrays of the x and y pixel
        coordinates for these objects"""

        wcs = self.wcs

        nx = float(self.shape[0])
        ny = float(self.shape[1])

        # Get the sky coordinates of the centre pixels in the detector
        x_centre, y_centre = nx / 2, ny / 2
        centre_coords = wcs.pixel_to_world(x_centre, y_centre)

        # now get the sky coords for the 4 corners of the image
        x_corners = [1, nx, nx, 1]
        y_corners = [1, 1, ny, ny]
        corners_coords = wcs.pixel_to_world(x_corners, y_corners)

        # now measure the angular distance between the corners and the image centre, and get the maximum distance (
        # plus a 5% tolerance) away from the centre
        corners_distance = corners_coords.separation(centre_coords).deg
        max_dist = corners_distance.max() * 1.05

        # get the distances of all objects from the centre pixel of the detector
        all_distances = objects_coords.separation(centre_coords).deg

        # we consider objects only closer to the centre than max_dist as candidates for being in the image
        candidate_indices = np.where(all_distances <= max_dist)[0]

        # For these candidates, get their sky coords and convert them into pixel coordinates
        candidate_coords = objects_coords[candidate_indices]
        x_candidates, y_candidates = wcs.world_to_pixel(candidate_coords)

        # now check if these pixel coordinates are in the image, and construct a list of these "good" objects'
        # indices and x,y positions
        indices_confirmed = []
        x_confirmed = []
        y_confirmed = []
        for i in range(len(x_candidates)):
            x, y = x_candidates[i], y_candidates[i]

            if 1. - x_buffer <= x <= nx + x_buffer and 1. - y_buffer <= y <= ny + y_buffer:

                indices_confirmed.append(candidate_indices[i])
                x_confirmed.append(x)
                y_confirmed.append(y)

        return np.asarray(indices_confirmed), np.asarray(x_confirmed), np.asarray(y_confirmed)

    # Operator overloads

    def __str__(self):
        """A short string with size information and the percentage of masked pixels"""

        shape_str = "{}x{}".format(self.shape[0], self.shape[1])
        str_list = [shape_str]

        if self.mask is not None:
            mask_str = "{}% masked".format(
                100.0 * float(np.sum(self.boolmask)) / float(np.size(self.data)))
            str_list.append(mask_str)

        offset_str = "offset [{}, {}]".format(*self.offset)
        str_list.append(offset_str)

        return "SHEImage(" + ", ".join(str_list) + ")"

    def __eq__(self, rhs: SHEImage) -> bool:
        """Equality test for SHEImage class.
        """

        # Identity implies equality
        if self is rhs:
            return True

        res: bool = True

        # Check that all the data is the same
        for attr in [*D_ATTR_CONVERSIONS.values(), "header", "offset"]:
            if neq(getattr(self, attr), getattr(rhs, attr)):
                res = False
                break
        else:
            # Check WCS if everything else passes
            if neq(self.wcs, rhs.wcs):

                # Special test for WCS, comparing them as headers if not equal, since they can be a bit finicky
                try:
                    if neq(self.wcs.to_header(), rhs.wcs.to_header()):
                        res = False
                        logger.debug(f"In SHEImage.__eq__, WCS is not equal. Values were: %s, %s",
                                     str(self.wcs.to_header()), str(rhs.wcs.to_header()))
                except AttributeError:
                    # In this case, only one is None, so return False
                    res = False

        return res

    # Private methods

    def __determine_det_ixy(self) -> None:
        """Private method to determine detector x and y position from the header.
        """

        if self.header is None or CCDID_LABEL not in self.header:
            # If no header, assume we're using detector 1-1
            self._det_ix = 1
            self._det_iy = 1
        else:
            try:
                self._det_iy = int(self.header[CCDID_LABEL][0])
                self._det_ix = int(self.header[CCDID_LABEL][2])
            except ValueError:
                # Check after "CCDID "
                self._det_iy = int(self.header[CCDID_LABEL][6])
                self._det_ix = int(self.header[CCDID_LABEL][8])

    def __set_array_attr(self,
                         array: Optional[np.ndarray],
                         name: str,
                         casting: str = "unsafe"):
        """Private method to handle setting one of the various data arrays other than `data`.
        """

        attr_name: str = D_ATTR_CONVERSIONS[name]

        # Set simply if input is None
        if array is None:
            setattr(self, f"_{attr_name}", None)
            return

        # Validate number of dimensions
        if array.ndim != 2:
            raise ValueError(f"The {attr_name} array must have 2 dimensions")

        # Validate shape
        if array.shape != self._data.shape:
            raise ValueError(f"The {attr_name} array must have the same size as its data {self.shape}")

        # Convert to expected type, ignoring byte order
        attr_dtype = D_IMAGE_DTYPES[name]
        if array.dtype.newbyteorder('<') != attr_dtype:
            logger.warning(f"Received {attr_name} array of type {array.dtype}. "
                           f"Attempting safe casting to {attr_dtype}.")
            array = array.astype(attr_dtype, casting = casting)
        setattr(self, f"_{attr_name}", array)

    @staticmethod
    def __get_kwarg(attr_name: str,
                    kwarg_tail: str,
                    kwargs: Dict[str, Any],
                    default_value: Optional[Union[str, int]] = None) -> Optional[Union[str, int]]:
        """Private method to get the filename keyword argument for a given attribute.
        """

        filename = kwargs.get(f"{attr_name.lower()}_{kwarg_tail}", None)
        if filename is None:
            # Fall back to the attribute itself
            filename = kwargs.get(f"{D_ATTR_CONVERSIONS[attr_name]}_{kwarg_tail}")
        if filename is None:
            # Return the default if we didn't find it in either format
            return default_value
        return filename

    @staticmethod
    def __get_filename_kwarg(attr_name: str,
                             kwargs: Dict[str, Any],
                             default_value: Optional[Union[str, int]] = None) -> Optional[str]:
        """Private method to get the filename keyword argument for a given attribute.
        """

        # The kwarg could be called either "filename" or "filepath", so try both
        for kwarg_tail in ("filename", "filepath"):
            filename = SHEImage.__get_kwarg(attr_name = attr_name,
                                            kwarg_tail = kwarg_tail,
                                            kwargs = kwargs,
                                            default_value = None)
            if filename is not None:
                return filename
        return default_value

    @staticmethod
    def __get_hdu_kwarg(attr_name: str,
                        kwargs: Dict[str, Any],
                        default_value: Optional[Union[str, int]] = None) -> Optional[Union[str, int]]:
        """Private method to get the HDU keyword argument for a given attribute.
        """

        # The kwarg could be called either "hdu" or "ext", so try both
        for kwarg_tail in ("hdu", "ext"):
            filename = SHEImage.__get_kwarg(attr_name = attr_name,
                                            kwarg_tail = kwarg_tail,
                                            kwargs = kwargs,
                                            default_value = None)
            if filename is not None:
                return filename
        return default_value


@run_only_once
def warn_mdb_not_loaded():
    logger.warning("MDB is not loaded, so default values will be assumed in calculating a noisemap.")


@run_only_once
def warn_galsim_wcs_bug_workaround():
    logger.warning("Hit bug with GalSim WCS. Applying workaround.")
