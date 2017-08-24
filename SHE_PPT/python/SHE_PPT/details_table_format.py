""" @file details_table_format.py

    Created 21 Aug 2017

    Format definition for galaxy details tables.

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

from SHE_PPT.table_utility import get_dtypes, get_names

class DetailsTableMeta(object):
    """
        @brief A class defining the metadata for details tables.
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
        self.comments = OrderedDict((self.version, None),
                                    (self.subtracted_sky_level, "ADU/arcsec^2"),
                                    (self.unsubtracted_sky_level, "ADU/arcsec^2"),
                                    (self.read_noise, "e-/pixel"),
                                    (self.gain, "e-/ADU"),
                                   )
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class DetailsTableFormat(object):
    """
        @brief A class defining the format for galaxy details tables. Only the details_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        meta = DetailsTableMeta()
        
        # And a quick alias for it
        m = meta
        
        # Get the version from the meta class
        self.__version__ = m.__version__
        
        # Direct alias for a tuple of all metadata
        self.meta_data = m.all
        
        # Store the less-used comments, dtypes, and fits_dtypes in dicts
        self.comments = OrderedDict((self.ID, None),
                                    (self.gal_x, "pixels"),
                                    (self.gal_y, "pixels"),
                                    (self.psf_x, "pixels"),
                                    (self.psf_y, "pixels"),
                                   ) 

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
        
        # Store the less-used comments, dtypes, and fits_dtypes in dicts
        self.comments = OrderedDict((self.ID, None),
                                    (self.gal_x, "pixels"),
                                    (self.gal_y, "pixels"),
                                    (self.psf_x, "pixels"),
                                    (self.psf_y, "pixels"),
                                    (self.hlr_bulge, "arcsec"),
                                    (self.hlr_disk, "arcsec"),
                                    (self.bulge_ellipticity, None),
                                    (self.bulge_axis_ratio, None),
                                    (self.bulge_fraction, None),
                                    (self.disk_height_ratio, None),
                                    (self.magnitude, "VIS"),
                                    (self.sersic_index, None),
                                    (self.rotation, "degrees"),
                                    (self.spin, "degrees"),
                                    (self.tilt, "degrees"),
                                    (self.shear_magnitude, None),
                                    (self.shear_angle, "degrees"),
                                    (self.target_galaxy, None),
                                   ) 
        
        self.dtypes = OrderedDict((self.ID, "i8"),
                                    (self.gal_x, "f4"),
                                    (self.gal_y, "f4"),
                                    (self.psf_x, "f4"),
                                    (self.psf_y, "f4"),
                                    (self.hlr_bulge, "f4"),
                                    (self.hlr_disk, "f4"),
                                    (self.bulge_ellipticity, "f4"),
                                    (self.bulge_axis_ratio, "f4"),
                                    (self.bulge_fraction, "f4"),
                                    (self.disk_height_ratio, "f4"),
                                    (self.magnitude, "f4"),
                                    (self.sersic_index, "f4"),
                                    (self.rotation, "f4"),
                                    (self.spin, "f4"),
                                    (self.tilt, "f4"),
                                    (self.shear_magnitude, "f4"),
                                    (self.shear_angle, "f4"),
                                    (self.target_galaxy, "b1"),
                                   ) 
        
        self.fits_dtypes = OrderedDict((self.ID, "K"),
                                    (self.gal_x, "E"),
                                    (self.gal_y, "E"),
                                    (self.psf_x, "E"),
                                    (self.psf_y, "E"),
                                    (self.hlr_bulge, "E"),
                                    (self.hlr_disk, "E"),
                                    (self.bulge_ellipticity, "E"),
                                    (self.bulge_axis_ratio, "E"),
                                    (self.bulge_fraction, "E"),
                                    (self.disk_height_ratio, "E"),
                                    (self.magnitude, "E"),
                                    (self.sersic_index, "E"),
                                    (self.rotation, "E"),
                                    (self.spin, "E"),
                                    (self.tilt, "E"),
                                    (self.shear_magnitude, "E"),
                                    (self.shear_angle, "E"),
                                    (self.target_galaxy, "L"),
                                   ) 
        
        # A list of columns in the desired order
        self.all = self.comments.keys()
        
        # TODO: Write unit test to ensure self.comments.keys() == self.dtypes.keys(), etc.
        
# Define an instance of this object that can be imported 
details_table_format = DetailsTableFormat()

# And a convient alias for it
tf = details_table_format

def make_details_table_header(subtracted_sky_level,
                              unsubtracted_sky_level,
                              read_noise,
                              gain,):
    """
        @brief Generate a header for a galaxy details table.
        
        @param subtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)
        
        @param unsubtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)
        
        @param read_noise <float> Units of e-/pixel
        
        @param gain <float> Units of e-/ADU
        
        @return header <dict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    header[tf.m.subtracted_sky_level] = (subtracted_sky_level, tf.m.comments[tf.m.subtracted_sky_level])
    header[tf.m.unsubtracted_sky_level] = (unsubtracted_sky_level, tf.m.comments[tf.m.unsubtracted_sky_level])
    header[tf.m.read_noise] = (read_noise, tf.m.comments[tf.m.read_noise])
    header[tf.m.gain] = (gain, tf.m.comments[tf.m.gain])
    
    return header

def initialise_details_table(image, options):
    """
        @brief Initialise a detections table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @return details_table <astropy.Table>
    """
    
    init_cols = []
    for _ in xrange(len(details_table_format.column_data)):
        init_cols.append([])
    
    details_table = Table(init_cols, names=get_names(details_table_format.column_data),
                          dtype=get_dtypes(details_table_format.column_data))
    
    details_table.meta = make_details_table_header(subtracted_sky_level = image.get_param_value('subtracted_background'),
                                                   unsubtracted_sky_level = image.get_param_value('unsubtracted_background'),
                                                   read_noise = options['read_noise'],
                                                   gain = options['gain'])
    
    return details_table
