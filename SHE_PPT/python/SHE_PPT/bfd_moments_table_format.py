""" @file bfd_moments_table_format.py

    Created September 7, 2017

    Format definition for BFD moments tables.

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

from SHE_PPT.detections_table_format import tf as detf
from SHE_PPT.table_utility import is_in_format

image_tail = ".fits"
shear_estimates_tail = "_bfd_moments.fits"

class BFDMomentsTableMeta(object):
    """
        @brief A class defining the metadata for bfd moments tables
    """
    
    def __init__(self):
        
        self.__version__ = "0.1.3"
        
        # Table metadata labels
        self.version = "SS_VER"
        
        self.model_hash = "MHASH"
        self.model_seed = "MSEED"
        self.noise_seed = "NSEED"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class BFDMomentsTableFormat(object):
    """
        @brief A class defining the format for BFD moments tables. Only the bfd_moments_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = BFDMomentsTableMeta()
        
        # And a quick alias for it
        self.m = self.meta
        
        # Get the version from the meta class
        self.__version__ = self.m.__version__
        
        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all
        
        # Dicts for less-used properties
        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()
        
        def set_column_properties( name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                   length=1):
            
            assert name not in self.is_optional
            
            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

        # Table column labels and properties
        
        self.ID = "ID"
        set_column_properties(self.ID, dtype=">i8", fits_dtype="K")

        self.moments_even = "MOM_EVEN"
        set_column_properties(self.moments_even,dtype="5F4",fits_dtype="5E")

        self.moments_odd = "MOM_ODD"
        set_column_properties(self.moments_odd,is_optional=True,dtype="2F4",fits_dtype="2E")

        self.deriv_moments_dg1 = "DM_DG1"
        set_column_properties(self.deriv_moments_dg1,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg2 = "DM_DG2"
        set_column_properties(self.deriv_moments_dg2,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dmu = "DM_DMU"
        set_column_properties(self.deriv_moments_dmu,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg1dg1 = "D2M_DG1DG1"
        set_column_properties(self.deriv_moments_dg1dg1,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg1dg2 = "D2M_DG1DG2"
        set_column_properties(self.deriv_moments_dg1dg2,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg2dg2 = "D2M_DG2DG2"
        set_column_properties(self.deriv_moments_dg2dg2,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg1dmu = "D2M_DG1DMU"
        set_column_properties(self.deriv_moments_dg1dmu,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dg2dmu = "D2M_DG2DMU"
        set_column_properties(self.deriv_moments_dg2dmu,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.deriv_moments_dmudmu = "D2M_DMUDMU"
        set_column_properties(self.deriv_moments_dmudmu,is_optional=True,dtype="7F4",fits_dtype="7E")

        self.x = "EST_X"
        set_column_properties(self.x, is_optional=True, comment="pixels")
        
        self.y = "EST_Y"
        set_column_properties(self.y, is_optional=True, comment="pixels")
        
        self.x_err = "EST_X_ERR"
        set_column_properties(self.x_err, is_optional=True, comment="pixels")
        
        self.y_err = "EST_Y_ERR"
        set_column_properties(self.y_err, is_optional=True, comment="pixels")
        
        self.flux = "FLUX"
        set_column_properties(self.flux, is_optional=True, comment="ADU")
        
        self.flux_err = "FLUX_ERR"
        set_column_properties(self.flux_err, is_optional=True, comment="ADU")
        
        self.bulge_fraction = "BULGE_FRAC"
        set_column_properties(self.bulge_fraction, is_optional=True)
        
        self.bulge_fraction_err = "BULGE_FRAC_ERR"
        set_column_properties(self.bulge_fraction_err, is_optional=True)
        
        self.snr = "SNR"
        set_column_properties(self.snr, is_optional=True)
        
        self.snr_err = "SNR_ERR"
        set_column_properties(self.snr_err, is_optional=True)
        
        # A list of columns in the desired order
        self.all = self.is_optional.keys()
        
        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported         
bfd_moments_table_format = BFDMomentsTableFormat()

# And a convient alias for it
tf = bfd_moments_table_format

def make_bfd_moments_table_header(model_hash = None,
                                  model_seed = None,
                                  noise_seed = None,):
    """
        @brief Generate a header for a bfd moments table
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <dict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_bfd_moments_table(detections_table = None,
                                 optional_columns = None):
    """
        @brief Initialise a bfd moments table based on a detections table, with the
               desired set of optional columns
        
        @param detections_table <astropy.table.Table>
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is MOM_EVEN
        
        @return bfd_moments_table <astropy.table.Table>
    """
    
    assert (detections_table is None) or (is_in_format(detections_table,detf))
    
    if optional_columns is None:
        optional_columns = [tf.e1_err,tf.e2_err]
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)
    
    names = []
    init_cols = []
    dtypes = []
    for colname in tf.all:
        if (colname in tf.all_required) or (colname in optional_columns):
            names.append(colname)
            init_cols.append([])
            dtypes.append((tf.dtypes[colname],tf.lengths[colname]))
    
    bfd_moments_table = Table(init_cols, names=names, dtype=dtypes)
    
    if detections_table is None:
        model_hash = None
        model_seed = None
        noise_seed = None
    else:
        model_hash = detections_table.meta[detf.m.model_hash]
        model_seed = detections_table.meta[detf.m.model_seed]
        noise_seed = detections_table.meta[detf.m.noise_seed]
    
    bfd_moments_table.meta = make_bfd_moments_table_header(model_hash = model_hash,
                                                           model_seed = model_seed,
                                                           noise_seed = noise_seed)
    
    return bfd_moments_table
