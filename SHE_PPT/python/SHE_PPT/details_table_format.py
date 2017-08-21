""" @file details_table_format.py

    Created 21 Aug 2017

    Format for galaxy details tables.

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

from SHE_PPT import magic_values as mv
from SHE_PPT.table_utility import get_dtypes, get_names

class DetailsTableFormat(object):
    
    def __init__(self):
        
        # Table metadata labels
        self.meta_version = ('SS_VER',None)
        self.meta_subtracted_sky_level = ("S_SKYLV","ADU/arcsec^2")
        self.meta_unsubtracted_sky_level = ("US_SKYLV","ADU/arcsec^2")
        self.meta_read_noise = ("RD_NOISE","e-/pixel")
        self.meta_gain = ("CCDGAIN","e-/ADU")

        # Table column labels
        self.ID = ('ID', 'i8', 'K', None)
        self.gal_x = ('x_center_pix', 'f4', 'E', "pixels")
        self.gal_y = ('y_center_pix', 'f4', 'E', "pixels")
        self.psf_x = ('psf_x_center_pix', 'f4', 'E', "pixels")
        self.psf_y = ('psf_y_center_pix', 'f4', 'E', "pixels")
        self.hlr_bulge = ('hlr_bulge_arcsec', 'f4', 'E', "arcsec")
        self.hlr_disk = ('hlr_disk_arcsec', 'f4', 'E', "arcsec")
        self.bulge_ellipticity = ('bulge_ellipticity', 'f4', 'E', None)
        self.bulge_axis_ratio = ('bulge_axis_ratio', 'f4', 'E', None)
        self.bulge_fraction = ('bulge_fraction', 'f4', 'E', None)
        self.disk_height_ratio = ('disk_height_ratio', 'f4', 'E', None)
        self.magnitude = ('magnitude', 'f4', 'E', "VIS")
        self.sersic_index = ('sersic_index', 'f4', 'E', None)
        self.rotation = ('rotation', 'f4', 'E', "degrees")
        self.spin = ('spin', 'f4', 'E', "degrees")
        self.tilt = ('tilt', 'f4', 'E', "degrees")
        self.shear_magnitude = ('shear_magnitude', 'f4', 'E', None)
        self.shear_angle = ('shear_angle', 'f4', 'E', "degrees")
        self.target_galaxy = ('is_target_galaxy', 'b1', 'L', None)
        
        self.column_data = (self.ID ,
                            self.gal_x ,
                            self.gal_y ,
                            self.psf_x ,
                            self.psf_y ,
                            self.hlr_bulge ,
                            self.hlr_disk ,
                            self.bulge_ellipticity ,
                            self.bulge_axis_ratio ,
                            self.bulge_fraction ,
                            self.disk_height_ratio ,
                            self.magnitude ,
                            self.sersic_index ,
                            self.rotation ,
                            self.spin ,
                            self.tilt ,
                            self.shear_magnitude ,
                            self.shear_angle ,
                            self.target_galaxy ,)
        
details_table_format = DetailsTableFormat()

def make_details_table_header(subtracted_sky_level,
                              unsubtracted_sky_level,
                              read_noise,
                              gain,):
    header = {}
    header[details_table_format.meta_version[0]] = mv.version_str
    header[details_table_format.meta_subtracted_sky_level[0]] = subtracted_sky_level
    header[details_table_format.meta_unsubtracted_sky_level[0]] = unsubtracted_sky_level
    header[details_table_format.meta_read_noise[0]] = read_noise
    header[details_table_format.meta_gain[0]] = gain
    
    return header

def initialise_details_table(image, options):
    
    init_cols = []
    for _ in xrange(len(details_table_format.column_data)):
        init_cols.append([])
    
    details_table = Table(init_cols, names=get_names(details_table_format.column_data),
                          dtype=get_dtypes(details_table_format.column_data))
    details_table.meta[details_table_format.meta_version[0]] = mv.version_str
    details_table.meta[details_table_format.meta_subtracted_sky_level[0]] = (image.get_param_value('subtracted_background'),
                                                                             details_table_format.meta_subtracted_sky_level[1])
    details_table.meta[details_table_format.meta_unsubtracted_sky_level[0]] = (image.get_param_value('unsubtracted_background'),
                                                                               details_table_format.meta_unsubtracted_sky_level[1])
    details_table.meta[details_table_format.meta_read_noise[0]] = (options['read_noise'],
                                                                   details_table_format.meta_read_noise[1])
    details_table.meta[details_table_format.meta_gain[0]] = (options['gain'],
                                                             details_table_format.meta_gain[1])
    
    return details_table
