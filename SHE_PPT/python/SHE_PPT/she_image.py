#
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
#
"""
File: she_image.py

Created on: Aug 17, 2017
"""
# Avoid non-trivial "from" imports (as explicit is better than implicit)

from copy import deepcopy
import os

import galsim

from SHE_PPT.magic_values import segmap_unassigned_value
from SHE_PPT.mask import (as_bool, is_masked_bad,
                          is_masked_suspect_or_bad, masked_off_image)
from SHE_PPT.utility import load_wcs
import astropy.io.fits
import astropy.wcs
import numpy as np

from . import logging


allowed_int_dtypes = (
    np.int8, np.int16, np.int32, np.uint8, np.uint16, np.uint32)


logger = logging.getLogger(__name__)


# We need new-style classes for properties, hence inherit from object
class SHEImage(object):
    """Structure to hold an image together with a mask, a noisemap, and a header (for metadata).

    The structure can be written into a FITS file, and stamps can be extracted.
    The properties .data, .mask, .noisemap and .header are meant to be accessed directly:
      - .data is a numpy array
      - .mask is a numpy array
      - .noisemap is a numpy array
      - .segmentation_map is a numpy array
      - .header is an astropy.io.fits.Header object
          (for an intro to those, see http://docs.astropy.org/en/stable/io/fits/#working-with-fits-headers )

    Note that the shape (and size) of data, mask and noisemap cannot be modified once the object exists, as such a
    change would probably not be wanted. If you really want to change the size of a SHEImage, make a new object.
    """

    def __init__(self,
                 data,
                 mask=None,
                 noisemap=None,
                 segmentation_map=None,
                 background_map=None,
                 weight_map=None,
                 header=None,
                 offset=None,
                 wcs=None,):
        """Initiator

        Args:
            data: a 2D numpy float array, with indices [x,y], consistent with DS9 and SExtractor orientation conventions.
            mask: an int32 array of the same shape as data. Leaving None creates an empty mask.
            noisemap: a float array of the same shape as data. Leaving None creates a noisemap of ones.
            segmentation_map: an int32 array of the same shape as data. Leaving None creates an empty map
            header: an astropy.io.fits.Header object. Leaving None creates an empty header.
            offset: a 1D numpy float array with two values, corresponding to the x and y offsets
            wcs: An astropy.wcs.WCS object, containing WCS information for this image
        """

        self.data = data  # Note the tests done in the setter method
        self.mask = mask
        self.noisemap = noisemap
        self.segmentation_map = segmentation_map
        self.background_map = background_map
        self.weight_map = weight_map
        self.header = header
        self.offset = offset
        self.wcs = wcs

        self.galsim_wcs = None

        logger.debug("Created {}".format(str(self)))

    # We define properties of the SHEImage object, following
    # https://euclid.roe.ac.uk/projects/codeen-users/wiki/User_Cod_Std-pythonstandard-v1-0#PNAMA-020-m-Developer-SHOULD-use-properties-to-protect-the-service-from-the-implementation

    @property
    def data(self):
        """The image array"""
        return self._data

    @data.setter
    def data(self, data_array):
        # We test the dimensionality
        if data_array.ndim is not 2:
            raise ValueError("Data array of a SHEImage must have 2 dimensions")
        # We test that the shape is not modified by the setter, if a shape
        # already exists.
        try:
            existing_shape = self.shape
        except AttributeError:
            existing_shape = None
        if existing_shape:
            if data_array.shape != existing_shape:
                raise ValueError("Shape of a SHEImage can not be modified. Current is {}, new data is {}.".format(
                    existing_shape, data_array.shape
                ))
        # And perform the attribution
        self._data = data_array

    @data.deleter
    def data(self):
        del self._data

    @property
    def mask(self):
        """The pixel mask of the image"""
        return self._mask

    @mask.setter
    def mask(self, mask_array):
        if mask_array is None:
            self._mask = None
        else:
            if mask_array.ndim is not 2:
                raise ValueError("The mask array must have 2 dimensions")
            if mask_array.shape != self._data.shape:
                raise ValueError(
                    "The mask array must have the same size as the data {}".format(self._data.shape))
            # Quietly ignore if byte order is the only difference
            if not mask_array.dtype.newbyteorder('<') in allowed_int_dtypes:
                logger.warning(
                    "Received mask array of type '{}'. Attempting safe casting to np.int32.".format(mask_array.dtype))
                try:
                    mask_array = mask_array.astype(np.int32, casting='safe')
                except:
                    raise ValueError(
                        "The mask array must be of integer type (it is {})".format(mask_array.dtype))
            self._mask = mask_array

    @mask.deleter
    def mask(self):
        del self._mask

    @property
    def boolmask(self):
        """A boolean summary of the mask, cannot be set, only get"""
        if self.mask is None:
            return None
        else:
            return self.mask.astype(np.bool)

    @property
    def noisemap(self):
        """A noisemap of the image"""
        return self._noisemap

    @noisemap.setter
    def noisemap(self, noisemap_array):
        if noisemap_array is None:
            self._noisemap = None
        else:
            if noisemap_array.ndim is not 2:
                raise ValueError("The noisemap array must have 2 dimensions")
            if noisemap_array.shape != self._data.shape:
                raise ValueError(
                    "The noisemap array must have the same size as its data {}".format(self._data.shape))
            self._noisemap = noisemap_array

    @noisemap.deleter
    def noisemap(self):
        del self._noisemap

    @property
    def segmentation_map(self):
        """The segmentation map of the image"""
        return self._segmentation_map

    @segmentation_map.setter
    def segmentation_map(self, segmentation_map_array):
        if segmentation_map_array is None:
            self._segmentation_map = None
        else:
            if segmentation_map_array.ndim is not 2:
                raise ValueError(
                    "The segmentation map array must have 2 dimensions")
            if segmentation_map_array.shape != self._data.shape:
                raise ValueError(
                    "The segmentation map array must have the same size as the data {}".format(self._data.shape))
            if False:  # FIXME
                # Quietly ignore if byte order is the only difference
                if not segmentation_map_array.dtype.newbyteorder('<') in allowed_int_dtypes:
                    logger.warning("Received segmentation map array of type '{}'. Attempting safe casting to seg_dtype.".format(
                        segmentation_map_array.dtype))
                    try:
                        segmentation_map_array = segmentation_map_array.astype(
                            np.int32, casting='safe')
                    except:
                        raise ValueError("The segmentation array must be of np.int32 type (it is {})".format(
                            segmentation_map_array.dtype))
            self._segmentation_map = segmentation_map_array

    @segmentation_map.deleter
    def segmentation_map(self):
        del self._segmentation_map

    @property
    def background_map(self):
        """A background map of the image"""
        return self._background_map

    @background_map.setter
    def background_map(self, background_map_array):
        if background_map_array is None:
            self._background_map = None
        else:
            if background_map_array.ndim is not 2:
                raise ValueError(
                    "The background map array must have 2 dimensions")
            if background_map_array.shape != self._data.shape:
                raise ValueError(
                    "The background map array must have the same size as its data {}".format(self._data.shape))
            self._background_map = background_map_array

    @background_map.deleter
    def background_map(self):
        del self._background_map

    @property
    def weight_map(self):
        """A weight map of the image"""
        return self._weight_map

    @weight_map.setter
    def weight_map(self, weight_map_array):
        if weight_map_array is None:
            self._weight_map = None
        else:
            if weight_map_array.ndim is not 2:
                raise ValueError(
                    "The weight map array must have 2 dimensions")
            if weight_map_array.shape != self._data.shape:
                raise ValueError(
                    "The weight map array must have the same size as its data {}".format(self._data.shape))
            self._weight_map = weight_map_array

    @weight_map.deleter
    def weight_map(self):
        del self._weight_map

    @property
    def header(self):
        """An astropy.io.fits.Header to contain metadata"""
        return self._header

    @header.setter
    def header(self, header_object):
        """Setter for the header of this image. Note that since the offset is stored in the header,
           it's always deepcopied when set to avoid surprisingly changing the input.
        """
        if header_object is None:
            self._header = None
            # self._header = astropy.io.fits.Header()  # An empty header
        else:
            # Not very pythonic, but I suggest this to
            if isinstance(header_object, astropy.io.fits.Header):
                # to avoid misuse, which could lead to problems when writing
                # FITS files.

                if "SHEIOFX" in header_object and "SHEIOFY" in header_object:
                    # If offset is stored in the header, update the offset property
                    self._header = deepcopy(header_object)
                    self.offset = (self.header["SHEIOFX"], self.header["SHEIOFY"])

                elif ("SHEIOFX" in header_object) != ("SHEIOFY" in header_object):
                    # If only one is stored in the header, raise an exception
                    raise ValueError("Header passed to SHEImage.header setter has only one of SHEIOFX and " +
                                     "SHEIOFY keywords. Must have both or neither.")

                else:
                    # If no offset in the header, add it to that
                    self._header = deepcopy(header_object)
                    self._header["SHEIOFX"] = (self.offset[0], "SHEImage x offset in pixels")
                    self._header["SHEIOFY"] = (self.offset[1], "SHEImage y offset in pixels")
            else:
                raise ValueError("The header must be an astropy.io.fits.Header instance")

        return

    @header.deleter
    def header(self):
        del self._header
        if hasattr(self, "_galsim_wcs"):
            self._galsim_wcs = None

    @property
    def offset(self):
        """A [x_offset, y_offset] numpy array with 2 values, tracking the offset of extracted stamps
        """
        return self._offset

    @offset.setter
    def offset(self, offset_tuple):
        """Convenience setter of the offset values, which are stored in the header

        We only set these header values if the offset_tuple is not None.
        """
        if offset_tuple is None:
            self._offset = np.array([0., 0.], dtype=float)
        else:
            if len(offset_tuple) is not 2:
                raise ValueError("A SHEImage.offset must have 2 items")
            else:
                self._offset = np.array(offset_tuple, dtype=float)

        # Set the offset in the header if the header exists
        if self.header is not None:
            self.header["SHEIOFX"] = (self._offset[0], "SHEImage x offset in pixels")
            self.header["SHEIOFY"] = (self._offset[1], "SHEImage y offset in pixels")

    @property
    # Just a shortcut, defined as a property in case we need to change
    # implementation later
    def wcs(self):
        """The WCS of the images"""
        return self._wcs

    @wcs.setter
    def wcs(self, wcs):
        """Convenience setter of the WCS.
        """
        if not (isinstance(wcs, astropy.wcs.WCS) or (wcs is None)):
            raise TypeError("wcs must be of type astropy.wcs.WCS")
        self._wcs = wcs

        # Unload the galsim wcs
        self._galsim_wcs = None

    @wcs.deleter
    def wcs(self):
        del self._wcs
        if hasattr(self, "_galsim_wcs"):
            self._galsim_wcs = None

    @property
    def galsim_wcs(self):
        """Get a GalSim-style WCS, which has some functions that astropy's lacks"""

        # If not already loaded, load it
        if self._galsim_wcs is None:
            # Load from the header if possible
            if self.header is not None and len(self.header) > 0:
                self._galsim_wcs = galsim.wcs.readFromFitsHeader(self.header)[0]
            elif self.wcs is not None:
                self.galsim_wcs = galsim.wcs.readFromFitsHeader(self.wcs.to_header())[0]
            else:
                raise ValueError("SHEImage must have a WCS set up or a WCS in its header in order to get a GalSim WCS.")

        return self._galsim_wcs

    @galsim_wcs.setter
    def galsim_wcs(self, galsim_wcs):
        """Convenience setter of the GalSim WCS.
        """
        if not (isinstance(galsim_wcs, galsim.wcs.BaseWCS) or (galsim_wcs is None)):
            raise TypeError("wcs must be of type galsim.wcs.BaseWCS")
        self._galsim_wcs = galsim_wcs

    @galsim_wcs.deleter
    def galsim_wcs(self):
        del self._galsim_wcs

    @property
    # Just a shortcut, also to stress that all arrays (data, mask, noisemap)
    # have the same shape.
    def shape(self):
        """The shape of the image, equivalent to self.data.shape"""
        return self.data.shape

    def __str__(self):
        """A short string with size information and the percentage of masked pixels"""

        shape_str = "{}x{}".format(self.shape[0], self.shape[1])
        mask_str = "{}% masked".format(
            100.0 * float(np.sum(self.boolmask)) / float(np.size(self.data)))
        str_list = [shape_str, mask_str]
        if self._has_offset_in_header():
            offset_str = "offset [{}, {}]".format(*self.offset)
            str_list.append(offset_str)
        return "SHEImage(" + ", ".join(str_list) + ")"

    def __eq__(self, rhs):
        """Equality test for SHEImage class.
        """

        def neq(lhs, rhs):
            try:
                return bool(lhs != rhs)
            except ValueError as _e:
                return (lhs != rhs).any()

        if neq(self.data, rhs.data):
            return False
        if neq(self.mask, rhs.mask):
            return False
        if neq(self.noisemap, rhs.noisemap):
            return False
        if neq(self.background_map, rhs.background_map):
            return False
        if neq(self.segmentation_map, rhs.segmentation_map):
            return False
        if neq(self.weight_map, rhs.weight_map):
            return False
        if neq(self.header, rhs.header):
            return False
        if neq(self.offset, rhs.offset):
            return False
        if neq(self.wcs, rhs.wcs):
            try:
                if neq(self.wcs.to_header(), rhs.wcs.to_header()):
                    return False
            except AttributeError:
                # In this case, only one is None, so return False
                return False

        return True

    def get_object_mask(self, seg_id, mask_suspect=False, mask_unassigned=False):
        """Get a mask for pixels that are either bad (and optionally suspect)
        or don't belong to an object with a given ID.

        Arguments
        ---------
        seg_id: int
            Segmentation map ID of the object for which to generate a mask
        mask_suspect: bool
            If True, suspect pixels will also be masked True.
        mask_unassigned: bool
            If True, pixels which are not assigned to any object will also be
            masked True.

        Return
        ------
        object_mask: np.ndarray<bool>
            Mask for the desired object. Values of True correspond to masked
            pixels (bad(/suspect) or don't belong to this object).
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
                other_mask, (self.segmentation_map != segmap_unassigned_value))

        # Combine and return the masks
        object_mask = np.logical_or(pixel_mask, other_mask)

        return object_mask

    def write_to_fits(self, filepath, clobber=False, data_only=False, **kwargs):
        """Writes the image to disk, in form of a multi-extension FITS cube.

        The data is written in the primary HDU, the mask in the extension 'MASK' and the noisemap in the extensions 'NOISEMAP'.
        All the attributes of this image object are (should be ?) saved into the FITS file.

        Technical note: the function "transposes" all the arrays written into the FITS file, so that the arrays will
        get shown by DS9 using the convention that the pixel with index [0,0] is bottom left.

        Args:
            filepath: where the FITS file should be written
            clobber: if True, overwrites any existing file.
            data_only: if True, will only write the data image.
        """

        # Set up a fits header with the wcs
        if self.wcs is not None:
            wcs_header = self.wcs.to_header()
            full_header = deepcopy(self.header)
            for label in wcs_header:
                # Overwrite any coming from the WCS
                full_header[label] = (wcs_header[label], wcs_header.comments[label])
        elif self.header is None:
            full_header = astropy.io.fits.Header()  # An empty header
        else:
            full_header = self.header

        # Note that we transpose the numpy arrays, so to have the same pixel
        # convention as DS9 and SExtractor.
        datahdu = astropy.io.fits.PrimaryHDU(
            self.data.transpose(), header=full_header)

        hdulist = astropy.io.fits.HDUList([datahdu])

        if not data_only:

            if self.mask is not None:
                maskhdu = astropy.io.fits.ImageHDU(
                    data=self.mask.transpose(), name="MASK")
                hdulist.append(maskhdu)
            if self.mask is not None:
                noisemaphdu = astropy.io.fits.ImageHDU(
                    data=self.noisemap.transpose(), name="NOISEMAP")
                hdulist.append(noisemaphdu)
            if self.mask is not None:
                segmaphdu = astropy.io.fits.ImageHDU(
                    data=self.segmentation_map.transpose(), name="SEGMAP")
                hdulist.append(segmaphdu)
            if self.mask is not None:
                bkgmaphdu = astropy.io.fits.ImageHDU(
                    data=self.background_map.transpose(), name="BKGMAP")
                hdulist.append(bkgmaphdu)
            if self.weight_map is not None:
                wgtmaphdu = astropy.io.fits.ImageHDU(
                    data=self.weight_map.transpose(), name="WGTMAP")
                hdulist.append(wgtmaphdu)

        if clobber is True and os.path.exists(filepath):
            logger.debug("The output file exists and will get overwritten")

        hdulist.writeto(filepath, clobber=clobber)
        # Note that clobber is called overwrite in the latest astropy, but
        # backwards compatible.

        logger.debug("Wrote {} to the FITS file '{}'".format(str(self), filepath))

    @classmethod
    def read_from_fits(cls,
                       filepath,
                       data_ext='PRIMARY',
                       mask_ext='MASK',
                       noisemap_ext='NOISEMAP',
                       segmentation_map_ext='SEGMAP',
                       background_map_ext='BKGMAP',
                       weight_map_ext='WGTMAP',
                       mask_filepath=None,
                       noisemap_filepath=None,
                       segmentation_map_filepath=None,
                       background_map_filepath=None,
                       weight_map_filepath=None,
                       workdir=".",
                       apply_sc3_fix=False):
        """Reads an image from a FITS file, such as written by write_to_fits(), and returns it as a SHEImage object.

        This function can be used to read previously saved SHEImage objects (in this case, just give the filepath),
        or to import other "foreign" FITS images (then you'll need the optional keyword arguments).
        When reading from one or several of these foreign files, you can
          - specify a specific HDU to read the mask from, e.g., by setting mask_ext='FLAG'
          - specify a different file to read the mask from, e.g., mask_filepath='mask.fits', mask_ext=0
          - avoid reading-in a mask, by specifying both mask_ext=None and mask_filepath=None (results in a default zero mask)
        Idem for the noisemap and the segmap

        Technical note: all the arrays read from FITS get "transposed", so that the array-properties of SHEImage can be
        indexed with [x,y] using the same orientation-convention as DS9 and SExtractor uses, that is, [0,0] is bottom left.

        Parameters
        ----------
        filepath: str
            path to the FITS file containing the primary data and header to be read
        data_ext: str
            name or index of the primary HDU, containing the data and the header.
        mask_ext: str
            name or index of the extension HDU containing the mask.
            Set both mask_ext and mask_filepath to None to not read in any mask.
        noisemap_ext: str
            idem, for the noisemap
        segmentation_map_ext: str
            idem, for the segmentation_map
        background_map_ext: str
            idem, for the background_map
        weight_map_ext: str
            idem, for the weight_map
        mask_filepath: str
            a separate filepath to read the mask from.
            If you specify this, also set mask_ext accordingly (at least set it to 0 if the file has only one HDU).
        noisemap_filepath: str
            idem, for the noisemap
        segmentation_map_filepath: str
            idem, for the segmentation_map
        background_map_filepath: str
            idem, for the background_map
        weight_map_filepath: str
            idem, for the weight_map
        workdir: str
            The working directory, where files can be found
        apply_sc3_fix: bool
            Whether or not to apply fix for bad headers used in SC3 data

        """

        # Reading the primary extension, which also contains the header
        qualified_filepath = os.path.join(workdir, filepath)
        (data, header) = cls._get_specific_hdu_content_from_fits(
            qualified_filepath, ext=data_ext, return_header=True)

        # Set up the WCS before we clean the header
        try:
            wcs = load_wcs(header, apply_sc3_fix=apply_sc3_fix)
        except KeyError:
            # No WCS information
            wcs = None

        # Removing the mandatory cards (that were automatically added to the
        # header if write_to_fits was used)
        logger.debug("The raw primary header has {} keys".format(len(list(header.keys()))))
        for keyword in ["SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "EXTEND"]:
            if keyword in header:
                header.remove(keyword)
        if wcs is not None:
            for keyword in list(wcs.to_header().keys()):
                if keyword in header:
                    header.remove(keyword)

        logger.debug("The cleaned header has {} keys".format(len(list(header.keys()))))

        # Reading the mask
        if mask_filepath is not None:
            qualified_mask_filepath = os.path.join(workdir, mask_filepath)
        else:
            qualified_mask_filepath = None
        mask = cls._get_secondary_data_from_fits(
            qualified_filepath, qualified_mask_filepath, mask_ext)

        # Reading the noisemap
        if noisemap_filepath is not None:
            qualified_noisemap_filepath = os.path.join(
                workdir, noisemap_filepath)
        else:
            qualified_noisemap_filepath = None
        noisemap = cls._get_secondary_data_from_fits(
            qualified_filepath, qualified_noisemap_filepath, noisemap_ext)

        # Reading the segmentation map
        if segmentation_map_filepath is not None:
            qualified_segmentation_map_filepath = os.path.join(
                workdir, segmentation_map_filepath)
        else:
            qualified_segmentation_map_filepath = None
        segmentation_map = cls._get_secondary_data_from_fits(qualified_filepath, qualified_segmentation_map_filepath,
                                                             segmentation_map_ext)

        # Reading the background map
        if background_map_filepath is not None:
            qualified_background_map_filepath = os.path.join(
                workdir, background_map_filepath)
        else:
            qualified_background_map_filepath = None
        background_map = cls._get_secondary_data_from_fits(qualified_filepath, qualified_background_map_filepath,
                                                           background_map_ext)
        # Reading the weight map
        if weight_map_filepath is not None:
            qualified_weight_map_filepath = os.path.join(
                workdir, weight_map_filepath)
        else:
            qualified_weight_map_filepath = None
            weight_map = cls._get_secondary_data_from_fits(qualified_filepath, qualified_weight_map_filepath,
                                                           weight_map_ext)

        # Building and returning the new object
        newimg = SHEImage(data=data, mask=mask, noisemap=noisemap, segmentation_map=segmentation_map,
                          background_map=background_map, weight_map=weight_map,
                          header=header, wcs=wcs)

        logger.info("Read {} from the file '{}'".format(str(newimg), filepath))
        return newimg

    @classmethod
    def _get_secondary_data_from_fits(cls, primary_filepath, special_filepath, ext):
        """Private helper for getting mask or noisemap, defining the logic of the related keyword arguments

        This function might return None, if both special_filepath and ext are None, or if the extension doesn't
        exist in the file.
        """

        outarray = None

        if special_filepath is None:
            filepath = primary_filepath
        else:
            filepath = special_filepath

        try:
            outarray = cls._get_specific_hdu_content_from_fits(filepath, ext=ext)
        except KeyError:
            logger.debug("Extension " + str(ext) + " not found in fits file " + filepath + ".")
            return None

        return outarray

    @classmethod
    def _get_specific_hdu_content_from_fits(cls, filepath, ext=None, return_header=False):
        """Private helper to handle access to particular extensions of a FITS file

        This function either returns something not-None, or raises an exception.
        Note that this function also takes care of transposing the data.
        """

        logger.debug("Reading from file '{}'...".format(filepath))

        hdulist = astropy.io.fits.open(filepath)
        nhdu = len(hdulist)

        if ext is None:
            if nhdu > 1:  # Warn the user, as the situation is not clear
                logger.warning(
                    "File '{}' has several HDUs, but no extension was specified! Using primary HDU.".format(filepath))
            ext = "PRIMARY"

        logger.debug("Accessing extension '{}' out of {} available HDUs...".format(ext, nhdu))
        data = hdulist[ext].data.transpose()
        if not data.ndim == 2:
            raise ValueError("Primary HDU must contain a 2D image")
        header = hdulist[ext].header

        hdulist.close()

        if return_header:
            return (data, header)
        else:
            return data

    def extract_stamp(self, x, y, width, height=None, indexconv="numpy", keep_header=False,
                      none_if_out_of_bounds=False, force_all_properties=False):
        """Extracts a stamp and returns it as a new instance (using views of numpy arrays, i.e., without making a copy)

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

        Return
        ------
        SHEImage

        """

        # Should we extract a square stamp?
        if height is None:
            height = width

        # Checking stamp size
        width = int(round(width))
        height = int(round(height))
        if width < 1 or height < 1:
            raise ValueError("Stamp height and width must at least be 1")

        # Dealing with the indexing conventions
        indexconv_defs = {"numpy": 0.0, "sextractor": 0.5}
        if indexconv not in list(indexconv_defs.keys()):
            raise ValueError(
                "Argument indexconv must be among {}".format(list(indexconv_defs.keys())))

        # Identifying the numpy stamp boundaries
        xmin = int(round(x - width / 2.0 - indexconv_defs[indexconv]))
        ymin = int(round(y - height / 2.0 - indexconv_defs[indexconv]))
        xmax = xmin + width
        ymax = ymin + height

        # If we're returning None if out of bounds, check now so we can exit
        # early
        if none_if_out_of_bounds:
            # Check if it's out of bounds
            if ((xmax < 0) or (xmin >= self.shape[0]) or
                    (ymax < 0) or (ymin >= self.shape[1])):
                return None

        # And the header:
        if keep_header:
            new_header = self.header
        else:
            new_header = None

        # And defining the offset property of the stamp, taking into account
        # any current offset.
        new_offset = self.offset + np.array([xmin, ymin])

        # If these bounds are fully within the image range, the extraction is
        # easy.
        if xmin >= 0 and xmax < self.shape[0] and ymin >= 0 and ymax < self.shape[1]:
            # We are fully within ghe image
            logger.debug("Extracting stamp [{}:{},{}:{}] fully within image of shape {}".format(
                xmin, xmax, ymin, ymax, self.shape))

            if self.mask is None:
                new_mask = None
            else:
                new_mask = self.mask[xmin:xmax, ymin:ymax]

            if self.noisemap is None:
                new_noisemap = None
            else:
                new_noisemap = self.noisemap[xmin:xmax, ymin:ymax]

            if self.segmentation_map is None:
                new_segmentation_map = None
            else:
                new_segmentation_map = self.segmentation_map[xmin:xmax, ymin:ymax]

            if self.background_map is None:
                new_background_map = None
            else:
                new_background_map = self.background_map[xmin:xmax, ymin:ymax]

            if self.weight_map is None:
                new_weight_map = None
            else:
                new_weight_map = self.weight_map[xmin:xmax, ymin:ymax]

            newimg = SHEImage(
                data=self.data[xmin:xmax, ymin:ymax],
                mask=new_mask,
                noisemap=new_noisemap,
                segmentation_map=new_segmentation_map,
                background_map=new_background_map,
                weight_map=new_weight_map,
                header=new_header,
                offset=new_offset,
                wcs=self.wcs,
            )

        else:
            logger.debug("Extracting stamp [{}:{},{}:{}] not entirely within image of shape {}".format(
                xmin, xmax, ymin, ymax, self.shape))

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
            overlap_slice = (
                slice(overlap_xmin, overlap_xmax), slice(overlap_ymin, overlap_ymax))
            logger.debug("overlap_slice: {}".format(overlap_slice))

            # Compute the bounds of this same overlapping part in the new stamp
            # The indexes of the stamp are simply shifted with respect to those
            # of the orinigal image by (xmin, ymin)
            overlap_xmin_stamp = overlap_xmin - xmin
            overlap_xmax_stamp = overlap_xmax - xmin
            overlap_ymin_stamp = overlap_ymin - ymin
            overlap_ymax_stamp = overlap_ymax - ymin
            overlap_slice_stamp = (slice(overlap_xmin_stamp, overlap_xmax_stamp), slice(
                overlap_ymin_stamp, overlap_ymax_stamp))

            # We first create new stamps, and we will later fill part of them
            # with slices of the original.
            data_stamp = np.zeros((width, height), dtype=self.data.dtype)

            if self.mask is None:
                mask_stamp = None
            else:
                mask_stamp = np.ones((width, height), dtype=self.mask.dtype) * masked_off_image

            if self.noisemap is None:
                noisemap_stamp = None
            else:
                noisemap_stamp = np.zeros((width, height), dtype=self.noisemap.dtype)

            if self.segmentation_map is None:
                segmentation_map_stamp = None
            else:
                segmentation_map_stamp = np.ones(
                    (width, height), dtype=self.segmentation_map.dtype) * segmap_unassigned_value

            if self.background_map is None:
                background_map_stamp = None
            else:
                background_map_stamp = np.zeros((width, height), dtype=self.background_map.dtype)

            if self.weight_map is None:
                weight_map_stamp = None
            else:
                weight_map_stamp = np.zeros((width, height), dtype=self.weight_map.dtype)

            # Fill the stamp arrays:
            # If there is any overlap
            if (overlap_width > 0) and (overlap_height > 0):
                data_stamp[overlap_slice_stamp] = self.data[overlap_slice]
                if self.mask is not None:
                    mask_stamp[overlap_slice_stamp] = self.mask[overlap_slice]
                if self.noisemap is not None:
                    noisemap_stamp[overlap_slice_stamp] = self.noisemap[overlap_slice]
                if self.segmentation_map is not None:
                    segmentation_map_stamp[overlap_slice_stamp] = self.segmentation_map[overlap_slice]
                if self.background_map is not None:
                    background_map_stamp[overlap_slice_stamp] = self.background_map[overlap_slice]
                if self.weight_map is not None:
                    weight_map_stamp[overlap_slice_stamp] = self.weight_map[overlap_slice]

            # Create the new object
            newimg = SHEImage(
                data=data_stamp,
                mask=mask_stamp,
                noisemap=noisemap_stamp,
                segmentation_map=segmentation_map_stamp,
                background_map=background_map_stamp,
                weight_map=weight_map_stamp,
                header=new_header,
                offset=new_offset,
                wcs=self.wcs,
            )

            if overlap_width == 0 and overlap_height == 0:
                logger.warning("The extracted stamp is entirely outside of the image bounds!")

        assert newimg.shape == (width, height)

        # If we're forcing all properties, add defaults now
        newimg.add_default_mask(force=False)
        newimg.add_default_noisemap(force=False)
        newimg.add_default_segmentation_map(force=False)
        newimg.add_default_background_map(force=False)
        newimg.add_default_weight_map(force=False)
        newimg.add_default_header(force=False)
        newimg.add_default_wcs(force=False)

        return newimg

    def pix2world(self, x, y, origin=0):
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
            x += self.offset[0]
            y += self.offset[1]

        ra, dec = self.wcs.all_pix2world(x, y, origin)

        return ra, dec

    def world2pix(self, ra, dec, origin=0):
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
            x -= self.offset[0]
            y -= self.offset[1]

        return x, y

    def get_pix2world_transformation(self, x, y, dx=0.1, dy=0.1, spatial_ra=False, origin=0, norm=False):
        """Gets the local transformation matrix between pixel and world (ra/dec) coordinates at the specified location.

        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y
        dx : float
            Differential x step to use in calculating transformation matrix. Default 0.1 pixels
        dy : float
            idem for y
        spatial_ra : bool
            If True, will give a matrix for (-ra*cos(dec),dec) co-ordinates instead of (ra,dec) (default False)
        origin : int
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)
        norm : bool
            If True, will divide the result by the determinant, resulting in the area-free transformation (default False)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dx or dy is 0

        Returns
        -------
        pix2world_transformation : np.matrix
            Transformation matrix in the format [[  dra/dx ,  dra/dy ],
                                                 [ ddec/dx , ddec/dy ]]

        """

        if (dx == 0) or (dy == 0):
            raise ValueError("Differentials dx and dy must not be zero.")

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        ra_0, dec_0 = self.pix2world(x, y, origin=origin)
        ra_px, dec_px = self.pix2world(x + dx, y, origin=origin)
        ra_py, dec_py = self.pix2world(x, y + dy, origin=origin)

        if spatial_ra:
            ra_scale = -np.cos(dec_0 * np.pi / 180)
        else:
            ra_scale = 1

        d_ra_x = ra_scale * (ra_px - ra_0) / dx
        d_dec_x = (dec_px - dec_0) / dx

        d_ra_y = ra_scale * (ra_py - ra_0) / dy
        d_dec_y = (dec_py - dec_0) / dy

        pix2world_transformation = np.matrix([[d_ra_x, d_ra_y],
                                              [d_dec_x, d_dec_y]])

        if norm:
            det = np.linalg.det(pix2world_transformation)
            pix2world_transformation /= np.sqrt(np.sign(det) * det)

        return pix2world_transformation

    def get_world2pix_transformation(self, ra, dec, dra=0.01 / 3600, ddec=0.01 / 3600, spatial_ra=False, origin=0,
                                     norm=False):
        """Gets the local transformation matrix between world (ra/dec) and pixel coordinates at the specified location.

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
        spatial_ra : bool
            If True, will give a matrix for (-ra*cos(dec),dec) co-ordinates instead of (ra,dec) (default False)
        origin : int
            Unused for this method; left in to prevent user surprise
        norm : bool
            If True, will divide the result by the determinant, resulting in the area-free transformation (default False)

        Raises
        ------
        AttributeError
            This object does not have a wcs set up
        ValueError
            dra or ddec is 0

        Returns
        -------
        world2pix_transformation : np.matrix
            Transformation matrix in the format [[ dx/dra , dx/ddec ],
                                                 [ dy/dra , dy/ddec ]]

        """

        if (dra == 0) or (ddec == 0):
            raise ValueError("Differentials dra and ddec must not be zero.")

        if spatial_ra:
            ra_scale = -np.cos(dec * np.pi / 180)
        else:
            ra_scale = 1

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        x_0, y_0 = self.world2pix(ra, dec)
        x_pra, y_pra = self.world2pix(ra + dra, dec)
        x_pdec, y_pdec = self.world2pix(ra, dec + ddec)

        d_x_ra = (x_pra - x_0) / (dra * ra_scale)
        d_y_ra = (y_pra - y_0) / (dra * ra_scale)

        d_x_dec = (x_pdec - x_0) / ddec
        d_y_dec = (y_pdec - y_0) / ddec

        world2pix_transformation = np.matrix([[d_x_ra, d_x_dec],
                                              [d_y_ra, d_y_dec]])

        if norm:
            det = np.linalg.det(world2pix_transformation)
            world2pix_transformation /= np.sqrt(np.sign(det) * det)

        return world2pix_transformation

    def get_pix2world_rotation(self, x, y, dx=0.1, dy=0.1, origin=0):
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
        pix2world_rotation : np.matrix
            Transformation matrix in the format [[ cos(theta) , -sin(theta) ],
                                                 [ sin(theta) ,  cos(theta) ]]
            Note that due to the method of calculation, the matrix may differ very slightly from an ideal
            rotation matrix.
        """

        # dx and dy are checked in get_pix2world_transformation, so no need to check here
        # It also handles the addition of the offset to x and y

        pix2world_transformation = self.get_pix2world_transformation(
            x, y, dx, dy, spatial_ra=True, origin=origin)

        u, s, vh = np.linalg.svd(pix2world_transformation)

        pix2world_rotation = vh @ u

        return pix2world_rotation

    def get_world2pix_rotation(self, ra, dec, dra=0.01 / 3600, ddec=0.01 / 3600, origin=0):
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
        world2pix_rotation : np.matrix
            Transformation matrix in the format [[ cos(theta) , -sin(theta) ],
                                                 [ sin(theta) ,  cos(theta) ]]
            Note that due to the method of calculation, the matrix may differ very slightly from an ideal
            rotation matrix.

        """

        # dx and dy are checked in get_pix2world_transformation, so no need to
        # check here

        world2pix_transformation = self.get_world2pix_transformation(
            ra, dec, dra, ddec, spatial_ra=True)

        u, s, vh = np.linalg.svd(world2pix_transformation)

        world2pix_rotation = vh @ u

        return world2pix_rotation

    def get_pix2world_decomposition(self, x, y):
        """Gets the local WCS decomposition between image (x/y) and world (ra/dec) coordinates at the specified location.

        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y

        Raises
        ------
        AttributeError
            This object does not have a wcs set up

        Returns
        -------
        (scale, shear, theta, flip)
        scale : float
            Scale factor of the decomposition
        shear : galsim.Shear
        theta : galsim.Angle
        flip : bool

        Note 1: Since shear and rotation are noncommutative, the rotation operation must be applied before shear.

        Note 2: If testing against a galsim.wcs.ShearWCS class, note that the shear defined as input to that class
          is the world-to-pixel shear, while the scale is the pixel-to-world scale, which can lead to some confusion
          if decomposed.

        """

        local_wcs = self.galsim_wcs.jacobian(image_pos=galsim.PositionD(x, y))

        # We need to use the inverse of the local wcs to get the pix2world decomposition
        return local_wcs.getDecomposition()

    def get_world2pix_decomposition(self, ra, dec):
        """Gets the local WCS decomposition between world (ra/dec) and pixel coordinates at the specified location.

        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees
        dec : float
            Declination (Dec) world coordinate in degrees

        Raises
        ------
        AttributeError
            This object does not have a wcs set up

        Returns
        -------
        (scale, shear, theta, flip)
        scale : float
            Scale factor of the decomposition
        shear : galsim.Shear
        theta : galsim.Angle
        flip : bool

        Note 1: Since shear and rotation are noncommutative, the rotation operation must be applied before shear.

        Note 2: If testing against a galsim.wcs.ShearWCS class, note that the shear defined as input to that class
          is the world-to-pixel shear, while the scale is the pixel-to-world scale, which can lead to some confusion
          if decomposed.

        """

        if isinstance(self.galsim_wcs, galsim.wcs.CelestialWCS):
            world_pos = galsim.CelestialCoord(ra * galsim.degrees, dec * galsim.degrees)
        else:
            world_pos = galsim.PositionD(ra, dec)

        local_wcs = self.galsim_wcs.jacobian(world_pos=world_pos)

        return local_wcs.inverse().getDecomposition()

    def estimate_pix2world_rotation_angle(self, x, y, dx, dy, origin=0):
        """Estimates the local rotation angle between pixel and world (-ra/dec) coordinates at the specified location.
        Note that due to distortion in the transformation, this method is inaccurate and depends on the choice of dx
        and dy; get_pix2world_rotation should be used instead to provide the rotation matrix. This method is retained
        to aid testing of that method.

        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y
        dx : float
            Differential x step to use in calculating transformation matrix
        dy : float
            idem for y
        origin : int
            Coordinate in the upper left corner of the image.
            In FITS and Fortran standards, this is 1.
            In Numpy and C standards this is 0.
            (from astropy.wcs)

        Note: dx and dy are required here since, due to distortion in the transformation, we can't assume the
        rotation angle will be independent of them.

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

        if (dx == 0) and (dy == 0):
            raise ValueError("Differentials dx and dy must not both be zero.")

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        ra_0, dec_0 = self.pix2world(x, y, origin=origin)
        ra_1, dec_1 = self.pix2world(x + dx, y + dy, origin=origin)

        cosdec = np.cos(dec_0 * np.pi / 180)

        if cosdec <= 0.01:
            raise ValueError("Dec too close to pole for accurate calculation.")

        dra = -(ra_1 - ra_0)
        ddec = (dec_1 - dec_0)

        xy_angle = np.arctan2(dx, dy)
        radec_angle = np.arctan2(dra * cosdec, ddec)

        rotation_angle = radec_angle - xy_angle

        return rotation_angle

    def estimate_world2pix_rotation_angle(self, ra, dec, dra=0.01 / 3600, ddec=0.01 / 3600, origin=0):
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
            Differential ra step in degrees to use in calculating transformation matrix
        ddec : float
            idem for dec

        Note: dra and ddec are required here since, due to distortion in the transformation, we can't assume the
        rotation angle will be independent of them.

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

        cosdec = np.cos(dec * np.pi / 180)

        if cosdec <= 0.01:
            raise ValueError("Dec too close to pole for accurate calculation.")

        # We'll calculate the transformation empirically by using small steps
        # in x and y
        x_0, y_0 = self.world2pix(ra, dec)
        x_1, y_1 = self.world2pix(ra - dra, dec + ddec)

        dx = (x_1 - x_0)
        dy = (y_1 - y_0)

        xy_angle = np.arctan2(dx, dy)
        radec_angle = np.arctan2(dra * cosdec, ddec)

        rotation_angle = xy_angle - radec_angle

        return rotation_angle
