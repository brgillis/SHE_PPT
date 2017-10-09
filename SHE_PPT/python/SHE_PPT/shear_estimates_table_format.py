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

from SHE_PPT.detections_table_format import tf as detf
from SHE_PPT.table_utility import is_in_format
from SHE_PPT import magic_values as mv

class ShearEstimatesTableMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1.7"
        self.table_format = "she.shearEstimates"
        
        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"
        
        self.extname = mv.extname_label
        
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, "#."+mv.shear_estimates_tag),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
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
            
            return name

        # Table column labels and properties
        
        self.ID = set_column_properties("SOURCE_ID", dtype=">i8", fits_dtype="K")
        
        self.g1 = set_column_properties("G1", dtype=">f8", fits_dtype="D")
        self.g2 = set_column_properties("G2", dtype=">f8", fits_dtype="D")
        self.g1_err = set_column_properties("G1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_err = set_column_properties("G2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1_err = set_column_properties("E1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_err = set_column_properties("E2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.flags = set_column_properties("FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties("FITCLASS", dtype=">i2", fits_dtype="I")
        
        self.g1_cal1 = set_column_properties("G1_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal1 = set_column_properties("G2_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b1_cal1 = set_column_properties("B1_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b2_cal1 = set_column_properties("B2_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g1_cal1_err = set_column_properties("G1_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal1_err = set_column_properties("G2_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1_cal1_err = set_column_properties("E1_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_cal1_err = set_column_properties("E2_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g1_cal2 = set_column_properties("G1_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal2 = set_column_properties("G2_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b1_cal2 = set_column_properties("B1_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b2_cal2 = set_column_properties("B2_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g1_cal2_err = set_column_properties("G1_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal2_err = set_column_properties("G2_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1_cal2_err = set_column_properties("E1_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_cal2_err = set_column_properties("E2_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.re = set_column_properties("RE", is_optional=True, comment="arcsec", dtype=">f8", fits_dtype="D")
        self.re_err = set_column_properties("RE_ERR", is_optional=True, comment="arcsec", dtype=">f8", fits_dtype="D")
        
        self.x = set_column_properties("X", is_optional=True, comment="pixels")
        self.y = set_column_properties("Y", is_optional=True, comment="pixels")
        self.x_err = set_column_properties("X_ERR", is_optional=True, comment="pixels")
        self.y_err = set_column_properties("Y_ERR", is_optional=True, comment="pixels")
        
        self.flux = set_column_properties("FLUX", is_optional=True, comment="ADU")
        self.flux_err = set_column_properties("FLUX_ERR", is_optional=True, comment="ADU")
        
        self.bulge_fraction = set_column_properties("BULGE_FRAC", is_optional=True)
        self.bulge_fraction_err = set_column_properties("BULGE_FRAC_ERR", is_optional=True)
        
        self.snr = set_column_properties("SNR", is_optional=True)
        self.snr_err = set_column_properties("SNR_ERR", is_optional=True)
        
        # A list of columns in the desired order
        self.all = self.is_optional.keys()
        
        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported         
shear_estimates_table_format = ShearEstimatesTableFormat()

# And a convient alias for it
tf = shear_estimates_table_format

def make_shear_estimates_table_header(detector = -1,
                                      model_hash = None,
                                      model_seed = None,
                                      noise_seed = None,):
    """
        @brief Generate a header for a shear estimates table.
        
        @param detector <int?> Detector for this image, if applicable
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <dict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.table_format
    
    header[tf.m.extname] = str(detector) + "." + mv.shear_estimates_tag
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_shear_estimates_table(detections_table = None,
                                     optional_columns = None):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns
        
        @param detections_table <astropy.table.Table>
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err
        
        @return shear_estimates_table <astropy.table.Table>
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
    
    shear_estimates_table = Table(init_cols, names=names, dtype=dtypes)
    
    if detections_table is None:
        detector = -1
        model_hash = None
        model_seed = None
        noise_seed = None
    else:
        detector = int(detections_table.meta[detf.m.extname].split(".")[0])
        model_hash = detections_table.meta[detf.m.model_hash]
        model_seed = detections_table.meta[detf.m.model_seed]
        noise_seed = detections_table.meta[detf.m.noise_seed]
    
    shear_estimates_table.meta = make_shear_estimates_table_header(detector = detector,
                                                                   model_hash = model_hash,
                                                                   model_seed = model_seed,
                                                                   noise_seed = noise_seed)
    
    return shear_estimates_table
