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

from astropy.table import Table

from SHE_PPT.table_utility import get_dtypes, get_names

detections_table_format_version = "0.1"

class DetectionsTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the detections_table_format
               instance of this should generally be accessed, and it should not be changed.
               
        @details Metadata (for the table header) is defined by a tuple of (label, comment).
        
                 Columns are defined by a tuple of (label, python_dtype, fits_dtype, comment).
                 
                 The column_data and meta_data members provide tuples of all metadata/columns.
    """
    
    def __init__(self):
        
        # Table metadata labels
        self.meta_version = ('SS_VER',None)
        self.meta_subtracted_sky_level = ("S_SKYLV","ADU/arcsec^2")
        self.meta_unsubtracted_sky_level = ("US_SKYLV","ADU/arcsec^2")
        self.meta_read_noise = ("RD_NOISE","e-/pixel")
        self.meta_gain = ("CCDGAIN","e-/ADU")
        
        self.meta_data = (self.meta_version,
                          self.meta_subtracted_sky_level,
                          self.meta_unsubtracted_sky_level,
                          self.meta_read_noise,
                          self.meta_gain,)

        # Table column labels
        self.ID = ('ID', 'i8', 'K', None)
        self.gal_x = ('x_center_pix', 'f4', 'E', "pixels")
        self.gal_y = ('y_center_pix', 'f4', 'E', "pixels")
        self.psf_x = ('psf_x_center_pix', 'f4', 'E', "pixels")
        self.psf_y = ('psf_y_center_pix', 'f4', 'E', "pixels")
        
        self.column_data = (self.ID,
                            self.gal_x,
                            self.gal_y,
                            self.psf_x,
                            self.psf_y,)
        
detections_table_format = DetectionsTableFormat()

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
        
        @return header <dict>
    """
    
    header = {}
    header[detections_table_format.meta_version[0]] = detections_table_format_version
    header[detections_table_format.meta_subtracted_sky_level[0]] = subtracted_sky_level
    header[detections_table_format.meta_unsubtracted_sky_level[0]] = unsubtracted_sky_level
    header[detections_table_format.meta_read_noise[0]] = read_noise
    header[detections_table_format.meta_gain[0]] = gain
    
    return header

def initialise_detections_table(image, options):
    """
        @brief Initialise a detections table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @return detections_table <astropy.Table>
    """
    
    init_cols = []
    for _ in xrange(len(detections_table_format.column_data)):
        init_cols.append([])
    
    detections_table = Table(init_cols, names=get_names(detections_table_format.column_data),
                          dtype=get_dtypes(detections_table_format.column_data))
    detections_table.meta[detections_table_format.meta_version[0]] = detections_table_format_version
    detections_table.meta[detections_table_format.meta_subtracted_sky_level[0]] = (image.get_param_value('subtracted_background'),
                                                                                  detections_table_format.meta_subtracted_sky_level[1])
    detections_table.meta[detections_table_format.meta_unsubtracted_sky_level[0]] = (image.get_param_value('unsubtracted_background'),
                                                                                     detections_table_format.meta_unsubtracted_sky_level[1])
    detections_table.meta[detections_table_format.meta_read_noise[0]] = (options['read_noise'],
                                                                         detections_table_format.meta_read_noise[1])
    detections_table.meta[detections_table_format.meta_gain[0]] = (options['gain'],
                                                                   detections_table_format.meta_gain[1])
    
    return detections_table
