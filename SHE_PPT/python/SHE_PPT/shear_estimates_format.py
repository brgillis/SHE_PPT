""" @file shear_estimates_format.py

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

from astropy.table import Table

from SHE_PPT.table_utility import get_dtypes, get_names

image_tail = ".fits"
shear_estimates_tail = "_shear_measurements.fits"

class ShearEstimatesTableFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the shear_estimates_table_format
               instance of this should generally be accessed, and it should not be changed.
               
        @details Metadata (for the table header) is defined by a tuple of (label, comment).
        
                 Columns are defined by a tuple of (label, python_dtype, fits_dtype, comment).
                 
                 The column_data and meta_data members provide tuples of all metadata/columns.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1"
        
        # Table metadata labels
        self.meta_version = ('SS_VER',None)
        
        self.meta_data = (self.meta_version,)

        # Table column labels
        self.ID = ('ID', 'i8', 'K', None)
        self.gal_x = ('GAL_X', 'f4', 'E', "pixels")
        self.gal_y = ('GAL_Y', 'f4', 'E', "pixels")
        self.gal_g1 = ('GAL_EST_G1', 'f4', 'E', None)
        self.gal_g2 = ('GAL_EST_G2', 'f4', 'E', None)
        self.gal_g1_err = ('GAL_G1_ERR', 'f4', 'E', None)
        self.gal_g2_err = ('GAL_G2_ERR', 'f4', 'E', None)
        self.gal_e1_err = ('GAL_E1_ERR', 'f4', 'E', None)
        self.gal_e2_err = ('GAL_E2_ERR', 'f4', 'E', None)
        
        self.column_data = (self.ID,
                            self.gal_x,
                            self.gal_y,
                            self.gal_g1,
                            self.gal_g2,
                            self.gal_g1_err,
                            self.gal_g2_err,
                            self.gal_e1_err,
                            self.gal_e2_err,)
        
shear_estimates_table_format = ShearEstimatesTableFormat()

def make_shear_estimates_table_header():
    """
        @brief Generate a header for a shear estimates table.
        
        @return header <dict>
    """
    
    header = {}
    header[shear_estimates_table_format.meta_version[0]] = shear_estimates_table_format.__version__
    
    return header

def initialise_shear_estimates_table():
    """
        @brief Initialise a shear estimates table.
        
        @return shear_estimates_table <astropy.Table>
    """
    
    init_cols = []
    for _ in xrange(len(detections_table_format.column_data)):
        init_cols.append([])
    
    shear_estimates_table = Table(init_cols, names=get_names(shear_estimates_table_format.column_data),
                          dtype=get_dtypes(shear_estimates_table_format.column_data))
    shear_estimates_table.meta[shear_estimates_table_format.meta_version[0]] = shear_estimates_table_format.__version__
    
    return shear_estimates_table
