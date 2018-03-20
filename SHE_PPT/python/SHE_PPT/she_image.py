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


import os

from SHE_PPT.magic_values import segmap_unassigned_value
from SHE_PPT.mask import ( as_bool, is_masked_bad,
                          is_masked_suspect_or_bad, masked_off_image )
import astropy.io.fits  # Avoid non-trivial "from" imports (as explicit is better than implicit)
import SHE_PPT.wcsutil
import numpy as np

from . import logging

mask_dtype = np.int32
seg_dtype = np.int32


logger = logging.getLogger( __name__ )



class SHEImage( object ):  # We need new-style classes for properties, hence inherit from object
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

    def __init__( self,
                 data,
                 mask = None,
                 noisemap = None,
                 segmentation_map = None,
                 background_map = None,
                 header = None,
                 offset = None,
                 wcs = None ):
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
        self.mask = mask  # Note that we translate None in the setter method
        self.noisemap = noisemap
        self.segmentation_map = segmentation_map
        self.background_map = background_map
        self.header = header
        self.offset = offset
        self.wcs = wcs

        logger.debug( "Created {}".format( str( self ) ) )


    # We define properties of the SHEImage object, following
    # https://euclid.roe.ac.uk/projects/codeen-users/wiki/User_Cod_Std-pythonstandard-v1-0#PNAMA-020-m-Developer-SHOULD-use-properties-to-protect-the-service-from-the-implementation

    @property
    def data( self ):
        """The image array"""
        return self._data
    @data.setter
    def data( self, data_array ):
        # We test the dimensionality
        if data_array.ndim is not 2:
            raise ValueError( "Data array of a SHEImage must have 2 dimensions" )
        # We test that the shape is not modified by the setter, if a shape already exists.
        try:
            existing_shape = self.shape
        except AttributeError:
            existing_shape = None
        if existing_shape:
            if data_array.shape != existing_shape:
                raise ValueError( "Shape of a SHEImage can not be modified. Current is {}, new data is {}.".format( 
                    existing_shape, data_array.shape
                    ) )
        # And perform the attribution
        self._data = data_array
    @data.deleter
    def data( self ):
        del self._data


    @property
    def mask( self ):
        """The pixel mask of the image"""
        return self._mask
    @mask.setter
    def mask( self, mask_array ):
        if mask_array is None:
            # Then we create an empty mask (0 means False means not masked)
            self._mask = np.zeros( self._data.shape, dtype = mask_dtype )
        else:
            if mask_array.ndim is not 2:
                raise ValueError( "The mask array must have 2 dimensions" )
            if mask_array.shape != self._data.shape:
                raise ValueError( "The mask array must have the same size as the data {}".format( self._data.shape ) )
            if not mask_array.dtype.newbyteorder( '<' ) == mask_dtype:  # Quietly ignore if byte order is the only difference
                logger.warning( "Received mask array of type '{}'. Attempting safe casting to mask_dtype.".format( mask_array.dtype ) )
                try:
                    mask_array = mask_array.astype( mask_dtype, casting = 'safe' )
                except:
                    raise ValueError( "The mask array must be of np.uint32 type (it is {})".format( mask_array.dtype ) )
            self._mask = mask_array
    @mask.deleter
    def mask( self ):
        del self._mask
    @property
    def boolmask( self ):
        """A boolean summary of the mask, cannot be set, only get"""
        return self._mask.astype( np.bool )

    @property
    def noisemap( self ):
        """A noisemap of the image"""
        return self._noisemap
    @noisemap.setter
    def noisemap( self, noisemap_array ):
        if noisemap_array is None:
            # Then we create a flat noisemap
            self._noisemap = np.ones( self._data.shape, dtype = float )
        else:
            if noisemap_array.ndim is not 2:
                raise ValueError( "The noisemap array must have 2 dimensions" )
            if noisemap_array.shape != self._data.shape:
                raise ValueError( "The noisemap array must have the same size as its data {}".format( self._data.shape ) )
            self._noisemap = noisemap_array
    @noisemap.deleter
    def noisemap( self ):
        del self._noisemap


    @property
    def segmentation_map( self ):
        """The segmentation map of the image"""
        return self._segmentation_map
    @segmentation_map.setter
    def segmentation_map( self, segmentation_map_array ):
        if segmentation_map_array is None:
            # Then we create an empty segmentation map (-1 means unassigned)
            self._segmentation_map = segmap_unassigned_value * np.ones( self._data.shape, dtype = seg_dtype )
        else:
            if segmentation_map_array.ndim is not 2:
                raise ValueError( "The segmentation map array must have 2 dimensions" )
            if segmentation_map_array.shape != self._data.shape:
                raise ValueError( "The segmentation map array must have the same size as the data {}".format( self._data.shape ) )
            if False: # FIXME
                if not segmentation_map_array.dtype.newbyteorder( '<' ) == seg_dtype:  # Quietly ignore if byte order is the only difference
                    logger.warning( "Received segmentation map array of type '{}'. Attempting safe casting to seg_dtype.".format( segmentation_map_array.dtype ) )
                    try:
                        segmentation_map_array = segmentation_map_array.astype( seg_dtype, casting = 'safe' )
                    except:
                        raise ValueError( "The segmentation array must be of np.int32 type (it is {})".format( segmentation_map_array.dtype ) )
            self._segmentation_map = segmentation_map_array
    @segmentation_map.deleter
    def segmentation_map( self ):
        del self._segmentation_map

    @property
    def background_map( self ):
        """A background map of the image"""
        return self._background_map
    @background_map.setter
    def background_map( self, background_map_array ):
        if background_map_array is None:
            # Then we create a flat, zero background map
            self._background_map = np.zeros( self._data.shape, dtype = float )
        else:
            if background_map_array.ndim is not 2:
                raise ValueError( "The background map array must have 2 dimensions" )
            if background_map_array.shape != self._data.shape:
                raise ValueError( "The background map array must have the same size as its data {}".format( self._data.shape ) )
            self._background_map = background_map_array
    @background_map.deleter
    def background_map( self ):
        del self._background_map


    @property
    def header( self ):
        """An astropy.io.fits.Header to contain metadata"""
        return self._header
    @header.setter
    def header( self, header_object ):
        if header_object is None:
            self._header = astropy.io.fits.Header()  # An empty header
        else:
            if isinstance( header_object, astropy.io.fits.Header ):  # Not very pythonic, but I suggest this to
                # to avoid misuse, which could lead to problems when writing FITS files.
                self._header = header_object
            else:
                raise ValueError( "The header must be an astropy.io.fits.Header instance" )
    @header.deleter
    def header( self ):
        del self._header

    @property
    def offset( self ):
        """A [x_offset, y_offset] numpy array with 2 values, tracking the offset of extracted stamps
        
        Note that internally, this offset is stored in the header, so that it is conserved by FITS i/o.
        """
        if self._has_offset_in_header():
            return np.array( ( self.header["SHEIOFX"], self.header["SHEIOFY"] ) )
        else:
            return np.array( [0, 0] )
    @offset.setter
    def offset( self, offset_tuple ):
        """Convenience setter of the offset values, which are stored in the header
        
        We only set these header values if the offset_tuple is not None.
        """
        if offset_tuple is not None:
            if len( offset_tuple ) is not 2:
                raise ValueError( "A SHEImage.offset must have 2 items" )
            self.header["SHEIOFX"] = ( offset_tuple[0], "SHEImage x offset in pixels" )
            self.header["SHEIOFY"] = ( offset_tuple[1], "SHEImage y offset in pixels" )

    def _has_offset_in_header( self ):
        """Tests if the header contains the offset keywords"""
        if "SHEIOFX" in list( self.header.keys() ) and "SHEIOFY" in list( self.header.keys() ):
            return True
        else:
            return False

    @property
    def wcs( self ):  # Just a shortcut, defined as a property in case we need to change implementation later
        """The WCS of the images"""
        return self._wcs
    @wcs.setter
    def wcs( self, wcs ):
        """Convenience setter of the WCS.
        """
        if not ( isinstance( wcs, SHE_PPT.wcsutil.WCS ) or ( wcs is None ) ):
            raise TypeError( "wcs must be of type SHE_PPT.wcsutil.WCS" )
        self._wcs = wcs


    @property
    def shape( self ):  # Just a shortcut, also to stress that all arrays (data, mask, noisemap) have the same shape.
        """The shape of the image, equivalent to self.data.shape"""
        return self.data.shape

    def __str__( self ):
        """A short string with size information and the percentage of masked pixels"""

        shape_str = "{}x{}".format( self.shape[0], self.shape[1] )
        mask_str = "{}% masked".format( 100.0 * float( np.sum( self.boolmask ) ) / float( np.size( self.data ) ) )
        str_list = [shape_str, mask_str]
        if self._has_offset_in_header():
            offset_str = "offset [{}, {}]".format( *self.offset )
            str_list.append( offset_str )
        return "SHEImage(" + ", ".join( str_list ) + ")"


    def get_object_mask( self, ID, mask_suspect = False, mask_unassigned = False ):
        """Get a mask for pixels that are either bad (and optionally suspect)
        or don't belong to an object with a given ID.
           
        Arguments
        ---------
        ID: int
            ID of the object for which to generate a mask
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
        # First get the boolean version of the mask for suspect/bad pixels
        if mask_suspect:
            pixel_mask = as_bool( is_masked_suspect_or_bad( self._mask ) )
        else:
            pixel_mask = as_bool( is_masked_bad( self._mask ) )

        # Now get mask for other objects
        other_mask = ( self._segmentation_map != ID )
        if not mask_unassigned:
            other_mask = np.logical_and( other_mask, ( self._segmentation_map != segmap_unassigned_value ) )

        # Combine and return the masks
        object_mask = np.logical_or( pixel_mask, other_mask )

        return object_mask

    def write_to_fits( self, filepath, clobber = False, data_only = True, **kwargs ):
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
            full_header = self.wcs.header
            for label in self.header:
                full_header[label] = ( self.header[label], self.header.comments[label] )
        else:
            full_header = self.header

        # Note that we transpose the numpy arrays, so to have the same pixel convention as DS9 and SExtractor.
        datahdu = astropy.io.fits.PrimaryHDU( self.data.transpose(), header = full_header )
        if not data_only:
            maskhdu = astropy.io.fits.ImageHDU( data = self.mask.transpose().astype( mask_dtype ), name = "MASK" )
            noisemaphdu = astropy.io.fits.ImageHDU( data = self.noisemap.transpose(), name = "NOISEMAP" )
            segmaphdu = astropy.io.fits.ImageHDU( data = self.segmentation_map.transpose().astype( seg_dtype ), name = "SEGMAP" )
            bkgmaphdu = astropy.io.fits.ImageHDU( data = self.background_map.transpose(), name = "BKGMAP" )

            hdulist = astropy.io.fits.HDUList( [datahdu, maskhdu, noisemaphdu, segmaphdu, bkgmaphdu] )
            
        else:
            hdulist = astropy.io.fits.HDUList( [datahdu] )

        if clobber is True and os.path.exists( filepath ):
            logger.info( "The output file exists and will get overwritten" )

        hdulist.writeto( filepath, clobber = clobber )
        # Note that clobber is called overwrite in the latest astropy, but backwards compatible.

        logger.info( "Wrote {} to the FITS file '{}'".format( str( self ), filepath ) )


    @classmethod
    def read_from_fits( cls,
                        filepath,
                        data_ext = 'PRIMARY',
                        mask_ext = 'MASK',
                        noisemap_ext = 'NOISEMAP',
                        segmentation_map_ext = 'SEGMAP',
                        background_map_ext = 'BKGMAP',
                        mask_filepath = None,
                        noisemap_filepath = None,
                        segmentation_map_filepath = None,
                        background_map_filepath = None,
                        workdir = "." ):
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
         
        Args:
            filepath: path to the FITS file containing the primary data and header to be read
            data_ext: name or index of the primary HDU, containing the data and the header.
            mask_ext: name or index of the extension HDU containing the mask.
                Set both mask_ext and mask_filepath to None to not read in any mask.
            noisemap_ext: idem, for the noisemap
            segmentation_map_ext: idem, for the segmentation_map
            background_map_ext: idem, for the background_map
            mask_filepath: a separate filepath to read the mask from.
                If you specify this, also set mask_ext accordingly (at least set it to 0 if the file has only one HDU).
            noisemap_filepath: idem, for the noisemap
            segmentation_map_filepath: idem, for the segmentation_map
            background_map_filepath: idem, for the background_map
            workdir: The working directory, where files can be found
      
        """

        # Reading the primary extension, which also contains the header
        qualified_filepath = os.path.join( workdir, filepath )
        ( data, header ) = cls._get_specific_hdu_content_from_fits( qualified_filepath, ext = data_ext, return_header = True )

        # Set up the WCS before we clean the header
        wcs = astropy.wcs.WCS( header )

        # Removing the mandatory cards (that were automatically added to the header if write_to_fits was used)
        logger.debug( "The raw primary header has {} keys".format( len( list( header.keys() ) ) ) )
        for keyword in ["SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "EXTEND"]:
            if keyword in header:
                header.remove( keyword )
        for keyword in list( wcs.header.keys() ):
            if keyword in header:
                header.remove( keyword )

        logger.debug( "The cleaned header has {} keys".format( len( list( header.keys() ) ) ) )

        # Reading the mask
        qualified_mask_filepath = os.path.join( workdir, filepath )
        mask = cls._get_secondary_data_from_fits( qualified_filepath, qualified_mask_filepath, mask_ext )

        # Reading the noisemap
        qualified_noisemap_filepath = os.path.join( workdir, filepath )
        noisemap = cls._get_secondary_data_from_fits( qualified_filepath, qualified_noisemap_filepath, noisemap_ext )

        # Reading the segmentation map
        qualified_segmentation_map_filepath = os.path.join( workdir, filepath )
        segmentation_map = cls._get_secondary_data_from_fits( qualified_filepath, qualified_segmentation_map_filepath,
                                                             segmentation_map_ext )

        # Reading the background map
        qualified_background_map_filepath = os.path.join( workdir, filepath )
        background_map = cls._get_secondary_data_from_fits( qualified_filepath, qualified_background_map_filepath,
                                                             background_map_ext )

        # Building and returning the new object
        newimg = SHEImage( data = data, mask = mask, noisemap = noisemap, segmentation_map = segmentation_map,
                           background_map = background_map, header = header,
                           wcs = wcs )

        logger.info( "Read {} from the file '{}'".format( str( newimg ), filepath ) )
        return newimg


    @classmethod
    def _get_secondary_data_from_fits( cls, primary_filepath, special_filepath, ext ):
        """Private helper for getting mask or noisemap, defining the logic of the related keyword arguments
        
        This function might return None, if both special_filepath and ext are None.
        """

        outarray = None
        if special_filepath is None:
            if ext is not None:
                outarray = cls._get_specific_hdu_content_from_fits( primary_filepath, ext = ext )
        else:
            outarray = cls._get_specific_hdu_content_from_fits( special_filepath, ext = ext )

        return outarray


    @classmethod
    def _get_specific_hdu_content_from_fits( cls, filepath, ext = None, return_header = False ):
        """Private helper to handle access to particular extensions of a FITS file
        
        This function either returns something not-None, or raises an exception.
        Note that this function also takes care of transposing the data.
        """

        logger.debug( "Reading from file '{}'...".format( filepath ) )

        hdulist = astropy.io.fits.open( filepath )
        nhdu = len( hdulist )

        if ext is None:
            if nhdu > 1:  # Warn the user, as the situation is not clear
                logger.warning( "File '{}' has several HDUs, but no extension was specified! Using primary HDU.".format( filepath ) )
            ext = "PRIMARY"

        logger.debug( "Accessing extension '{}' out of {} available HDUs...".format( ext, nhdu ) )
        data = hdulist[ext].data.transpose()
        if not data.ndim == 2:
            raise ValueError( "Primary HDU must contain a 2D image" )
        header = hdulist[ext].header

        hdulist.close()

        if return_header:
            return ( data, header )
        else:
            return data



    def extract_stamp( self, x, y, width, height = None, indexconv = "numpy", keep_header = False,
                       none_if_out_of_bounds = False ):
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
        
        Bottomline: if SExtractor told you that there is a galaxy at a certain position, you can use this position directly
        to extract a statistically-well-centered stamp as long as you set indexconv="sextractor".
        
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
            Set this to True if you want this method to return None if the stamp is entirely out of bounds of the image.
            By default, this is set to False, which means it will instead return an entirely masked image in that case.
            
        Return
        ------
        SHEImage
            
        """

        # Should we extract a square stamp?
        if height is None:
            height = width

        # Checking stamp size
        width = int( round( width ) )
        height = int( round( height ) )
        if width < 1 or height < 1:
            raise ValueError( "Stamp height and width must at least be 1" )

        # Dealing with the indexing conventions
        indexconv_defs = {"numpy":0.0, "sextractor":0.5}
        if indexconv not in list( indexconv_defs.keys() ):
            raise ValueError( "Argument indexconv must be among {}".format( list( indexconv_defs.keys() ) ) )


        # Identifying the numpy stamp boundaries
        xmin = int( round( x - width / 2.0 - indexconv_defs[indexconv] ) )
        ymin = int( round( y - height / 2.0 - indexconv_defs[indexconv] ) )
        xmax = xmin + width
        ymax = ymin + height
        
        # If we're returning None if out of bounds, check now so we can exit early
        if none_if_out_of_bounds:
            # Check if it's out of bounds
            if ((xmax < 0) or (xmin >= self.shape[0]) or
                (ymax < 0) or (ymin >= self.shape[1])):
                return None

        # And the header:
        if keep_header:
            newheader = self.header
        else:
            newheader = None

        # And defining the offset property of the stamp, taking into account any current offset.
        newoffset = self.offset + np.array( [xmin, ymin] )


        # If these bounds are fully within the image range, the extraction is easy.
        if xmin >= 0 and xmax < self.shape[0] and ymin >= 0 and ymax < self.shape[1]:
            # We are fully within ghe image
            logger.debug( "Extracting stamp [{}:{},{}:{}] fully within image of shape {}".format( xmin, xmax, ymin, ymax, self.shape ) )

            newimg = SHEImage( 
                data = self.data[xmin:xmax, ymin:ymax],
                mask = self.mask[xmin:xmax, ymin:ymax],
                noisemap = self.noisemap[xmin:xmax, ymin:ymax],
                segmentation_map = self.segmentation_map[xmin:xmax, ymin:ymax],
                background_map = self.background_map[xmin:xmax, ymin:ymax],
                header = newheader,
                offset = newoffset
            )

        else:
            logger.debug( "Extracting stamp [{}:{},{}:{}] not entirely within image of shape {}".format( xmin, xmax, ymin, ymax, self.shape ) )

            # One solution would be to pad the image and extract, but that would need a lot of memory.
            # So instead we go for the more explicit bound computations.

            # We first create new stamps, and we will later fill part of them with slices of the original.
            data_stamp = np.zeros( ( width, height ), dtype = self.data.dtype )
            mask_stamp = np.ones( ( width, height ), dtype = self.mask.dtype ) * masked_off_image
            noisemap_stamp = np.zeros( ( width, height ), dtype = self.noisemap.dtype )
            segmentation_map_stamp = np.ones( ( width, height ), dtype = self.segmentation_map.dtype ) * segmap_unassigned_value
            background_map_stamp = np.zeros( ( width, height ), dtype = self.background_map.dtype )

            # Compute the bounds of the overlapping part of the stamp in the original image
            overlap_xmin = max( xmin, 0 )
            overlap_ymin = max( ymin, 0 )
            overlap_xmax = min( xmax, self.shape[0] )
            overlap_ymax = min( ymax, self.shape[1] )
            overlap_width = overlap_xmax - overlap_xmin
            overlap_height = overlap_ymax - overlap_ymin
            overlap_slice = ( slice( overlap_xmin, overlap_xmax ), slice( overlap_ymin, overlap_ymax ) )
            logger.debug( "overlap_slice: {}".format( overlap_slice ) )

            # Compute the bounds of this same overlapping part in the new stamp
            # The indexes of the stamp are simply shifted with respect to those of the orinigal image by (xmin, ymin)
            overlap_xmin_stamp = overlap_xmin - xmin
            overlap_xmax_stamp = overlap_xmax - xmin
            overlap_ymin_stamp = overlap_ymin - ymin
            overlap_ymax_stamp = overlap_ymax - ymin
            overlap_slice_stamp = ( slice( overlap_xmin_stamp, overlap_xmax_stamp ), slice( overlap_ymin_stamp, overlap_ymax_stamp ) )


            # Fill the stamp arrays:
            if (overlap_width > 0) and (overlap_height > 0): # If there is any overlap
                data_stamp[overlap_slice_stamp] = self.data[overlap_slice]
                mask_stamp[overlap_slice_stamp] = self.mask[overlap_slice]
                noisemap_stamp[overlap_slice_stamp] = self.noisemap[overlap_slice]
                segmentation_map_stamp[overlap_slice_stamp] = self.segmentation_map[overlap_slice]
                background_map_stamp[overlap_slice_stamp] = self.background_map[overlap_slice]

            # Create the new object
            newimg = SHEImage( 
                data = data_stamp,
                mask = mask_stamp,
                noisemap = noisemap_stamp,
                segmentation_map = segmentation_map_stamp,
                background_map = background_map_stamp,
                header = newheader,
                offset = newoffset
            )

            if overlap_width == 0 and overlap_height == 0:
                logger.warning( "The extracted stamp is entirely outside of the image bounds!" )


        assert newimg.shape == ( width, height )
        return newimg

    def pix2world( self, x, y, distort=True ):
        """Converts x and y pixel coordinates to ra and dec world coordinates.
              
        Parameters
        ----------
        x : float
            x pixel coordinate
        y : float
            idem for y
        distort : bool
            Use the distortion model if present
            
        Raises
        ------
        AttributeError : if this object does not have a wcs set up
        
        Returns
        -------
        ra : float (in degrees)
        dec : float (in degrees)
        
        """

        if self.wcs is None:
            raise AttributeError( "pix2world called by SHEImage object that doesn't have a WCS set up. " +
                                 "Note that WCS isn't currently passed when extract_stamp is used, so this might be the issue." )

        ra, dec = self.wcs.image2sky( x, y, distort=distort )

        return ra, dec

    def world2pix( self, ra, dec, distort=True, find=True ):
        """Converts ra and dec world coordinates to x and y pixel coordinates
              
        Parameters
        ----------
        ra : float
            Right Ascension (RA) world coordinate in degrees
        dec : float
            Declination (Dec) world coordinate in degrees
        distort : bool
            Use the distortion model if present (default True)
        find : bool
            If using the distortion model, more accurately but more slowly solve the polynomial eq. (default True)
            
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
            raise AttributeError( "world2pix called by SHEImage object that doesn't have a WCS set up. " +
                                 "Note that WCS isn't currently passed when extract_stamp is used, so this might be the issue." )

        x, y = self.wcs.sky2image( ra, dec, distort=distort, find=find )

        return x, y

    def get_pix2world_transformation( self, x, y, dx = 0.1, dy = 0.1 ):
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

        if ( dx == 0 ) or ( dy == 0 ):
            raise ValueError( "Differentials dx and dy must not be zero." )

        # We'll calculate the transformation empirically by using small steps in x and y
        ra_0, dec_0 = self.pix2world( x, y )
        ra_px, dec_px = self.pix2world( x + dx, y )
        ra_py, dec_py = self.pix2world( x, y + dy )

        d_ra_x = ( ra_px - ra_0 ) / dx
        d_dec_x = ( dec_px - dec_0 ) / dx

        d_ra_y = ( ra_py - ra_0 ) / dy
        d_dec_y = ( dec_py - dec_0 ) / dy

        pix2world_transformation = np.matrix( [[  d_ra_x , d_ra_y ],
                                               [ d_dec_x , d_dec_y ]] )

        return pix2world_transformation

    def get_world2pix_transformation( self, ra, dec, dra = 0.01 / 3600, ddec = 0.01 / 3600 ):
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

        if ( dra == 0 ) or ( dra == 0 ):
            raise ValueError( "Differentials dra and ddec must not be zero." )

        # We'll calculate the transformation empirically by using small steps in x and y
        x_0, y_0 = self.world2pix( ra, dec )
        x_pra, y_pra = self.world2pix( ra + dra, dec )
        x_pdec, y_pdec = self.world2pix( ra, dec + ddec )

        d_x_ra = ( x_pra - x_0 ) / dra
        d_y_ra = ( y_pra - y_0 ) / dra

        d_x_dec = ( x_pdec - x_0 ) / ddec
        d_y_dec = ( y_pdec - y_0 ) / ddec

        world2pix_transformation = np.matrix( [[ d_x_ra , d_x_dec ],
                                               [ d_y_ra , d_y_dec ]] )

        return world2pix_transformation
