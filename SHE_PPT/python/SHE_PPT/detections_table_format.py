""" @file detections_table_format.py

    Created 22 Aug 2017

    Format definition for detections table.

    ---------------------------------------------------------------------

    Copyright (C) 2012-2020 Euclid Science Ground Segment      
       
    This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General    
    Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)    
    any later version.    
       
    This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied    
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more    
    details.    
       
    You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to    
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT.table_utility import get_dtypes

class DetectionsTableMeta(object):
    """
        @brief A class defining the metadata for detections tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1"
        
        # Table metadata labels
        self.version = "SS_VER"
        self.subtracted_sky_level = "S_SKYLV"
        self.unsubtracted_sky_level = "US_SKYLV"
        self.read_noise = "RD_NOISE"
        self.gain = "CCDGAIN"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                    (self.subtracted_sky_level, "ADU/arcsec^2"),
                                    (self.unsubtracted_sky_level, "ADU/arcsec^2"),
                                    (self.read_noise, "e-/pixel"),
                                    (self.gain, "e-/ADU"),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class DetectionsTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the detections_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = DetectionsTableMeta()
        
        # And a quick alias for it
        self.m = meta
        
        # Get the version from the meta class
        self.__version__ = m.__version__
        
        # Direct alias for a tuple of all metadata
        self.meta_data = m.all
        
        # Column names
        self.ID = "ID"
        self.gal_x = "x_center_pix"
        self.gal_y = "y_center_pix"
        self.psf_x = "psf_x_center_pix"
        self.psf_y = "psf_y_center_pix"
        
        # Store the less-used comments, dtypes, and fits_dtypes in dicts
        self.comments = OrderedDict(((self.ID, None),
                                    (self.gal_x, "pixels"),
                                    (self.gal_y, "pixels"),
                                    (self.psf_x, "pixels"),
                                    (self.psf_y, "pixels"),
                                   )) 
        
        self.dtypes = OrderedDict(((self.ID, "i8"),
                                  (self.gal_x, "f4"),
                                  (self.gal_y, "f4"),
                                  (self.psf_x, "f4"),
                                  (self.psf_y, "f4"),
                                 ))
        
        self.fits_dtypes = OrderedDict(((self.ID, "K"),
                                       (self.gal_x, "E"),
                                       (self.gal_y, "E"),
                                       (self.psf_x, "E"),
                                       (self.psf_y, "E"),
                                      ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()
        
        # TODO: Write unit test to ensure self.comments.keys() == self.dtypes.keys(), etc.

# Define an instance of this object that can be imported         
detections_table_format = DetectionsTableFormat()

# And a convient alias for it
tf = detections_table_format


def make_detections_table_header(subtracted_sky_level,
                                 unsubtracted_sky_level,
                                 read_noise,
                                 gain):
    """
        @brief Generate a header for a detections table.
        
        @param subtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)
        
        @param unsubtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)
        
        @param read_noise <float> Units of e-/pixel
        
        @param gain <float> Units of e-/ADU
        
        @return header <OrderedDict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    header[tf.m.subtracted_sky_level] = (subtracted_sky_level, tf.m.comments[tf.m.subtracted_sky_level])
    header[tf.m.unsubtracted_sky_level] = (unsubtracted_sky_level, tf.m.comments[tf.m.unsubtracted_sky_level])
    header[tf.m.read_noise] = (read_noise, tf.m.comments[tf.m.read_noise])
    header[tf.m.gain] = (gain, tf.m.comments[tf.m.gain])
    
    return header

def initialise_detections_table(image, options):
    """
        @brief Initialise a detections table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @return detections_table <astropy.Table>
    """
    
    init_cols = []
    for _ in range(len(tf.all)):
        init_cols.append([])
    
    detections_table = Table(init_cols, names=tf.all,
                          dtype=get_dtypes(tf))
    
    detections_table.meta = make_detections_table_header(subtracted_sky_level = image.get_param_value('subtracted_background'),
                                                         unsubtracted_sky_level = image.get_param_value('unsubtracted_background'),
                                                         read_noise = options['read_noise'],
                                                         gain = options['gain'])
    
    return detections_table
