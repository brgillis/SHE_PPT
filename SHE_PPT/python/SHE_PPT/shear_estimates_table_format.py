""" @file shear_estimates_table_format.py

    Created 22 Aug 2017

    Format definition for shear estimates tables.

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

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT.table_utility import get_dtypes

image_tail = ".fits"
shear_estimates_tail = "_shear_measurements.fits"

class ShearEstimatesTableMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1"
        
        # Table metadata labels
        self.version = "SS_VER"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class ShearEstimatesTableFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the shear_estimates_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = ShearEstimatesTableMeta()
        
        # And a quick alias for it
        self.m = meta
        
        # Get the version from the meta class
        self.__version__ = m.__version__
        
        # Direct alias for a tuple of all metadata
        self.meta_data = m.all

        # Table column labels
        self.ID = "ID"
        self.gal_x = "GAL_X"
        self.gal_y = "GAL_Y"
        self.gal_g1 = "GAL_EST_G1"
        self.gal_g2 = "GAL_EST_G2"
        self.gal_g1_err = "GAL_G1_ERR"
        self.gal_g2_err = "GAL_G2_ERR"
        self.gal_e1_err = "GAL_E1_ERR"
        self.gal_e2_err = "GAL_E2_ERR"
        
        # Store the less-used comments, dtypes, and fits_dtypes in dicts
        self.comments = OrderedDict(((self.ID, None),
                                    (self.gal_x, "pixels"),
                                    (self.gal_y, "pixels"),
                                    (self.gal_g1, None),
                                    (self.gal_g2, None),
                                    (self.gal_g1_err, None),
                                    (self.gal_g2_err, None),
                                    (self.gal_e1_err, None),
                                    (self.gal_e2_err, None),
                                   )) 
        
        self.dtypes = OrderedDict(((self.ID, "i8"),
                                  (self.gal_x, "f4"),
                                  (self.gal_y, "f4"),
                                  (self.gal_g1, "f4"),
                                  (self.gal_g2, "f4"),
                                  (self.gal_g1_err, "f4"),
                                  (self.gal_g2_err, "f4"),
                                  (self.gal_e1_err, "f4"),
                                  (self.gal_e2_err, "f4"),
                                 ))
        
        self.fits_dtypes = OrderedDict(((self.ID, "K"),
                                       (self.gal_x, "E"),
                                       (self.gal_y, "E"),
                                       (self.gal_g1, "E"),
                                       (self.gal_g2, "E"),
                                       (self.gal_g1_err, "E"),
                                       (self.gal_g2_err, "E"),
                                       (self.gal_e1_err, "E"),
                                       (self.gal_e2_err, "E"),
                                      ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()
        
        # TODO: Write unit test to ensure self.comments.keys() == self.dtypes.keys(), etc.

# Define an instance of this object that can be imported         
shear_estimates_table_format = ShearEstimatesTableFormat()

# And a convient alias for it
tf = shear_estimates_table_format

def make_shear_estimates_table_header():
    """
        @brief Generate a header for a shear estimates table.
        
        @return header <dict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    
    return header

def initialise_shear_estimates_table():
    """
        @brief Initialise a shear estimates table.
        
        @return shear_estimates_table <astropy.Table>
    """
    
    init_cols = []
    for _ in range(len(tf.column_data)):
        init_cols.append([])
    
    shear_estimates_table = Table(init_cols, names=tf.all,
                          dtype=get_dtypes(tf))
    shear_estimates_table.meta[tf.m.version] = tf.__version__
    
    return shear_estimates_table
