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
        
        self.__version__ = "0.1.4"
        
        # Table metadata labels
        self.version = "SS_VER"
        
        self.extname = mv.extname_label
        
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
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

        # Table column labels and properties
        
        self.ID = "ID"
        set_column_properties(self.ID, dtype=">i8", fits_dtype="K")
        
        self.g1 = "EST_G1"
        set_column_properties(self.g1, dtype=">f8", fits_dtype="D")
        
        self.g2 = "EST_G2"
        set_column_properties(self.g2, dtype=">f8", fits_dtype="D")
        
        self.g1_err = "G1_ERR"
        set_column_properties(self.g1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g2_err = "G2_ERR"
        set_column_properties(self.g2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e1_err = "E1_ERR"
        set_column_properties(self.e1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e2_err = "E2_ERR"
        set_column_properties(self.e2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.star_flag = "STAR_FLAG"
        set_column_properties(self.star_flag, is_optional=True, dtype="bool", fits_dtype="L")
        
        self.fit_class = "FITCLASS"
        set_column_properties(self.fit_class, is_optional=True, dtype=">i2", fits_dtype="I")
        
        self.g1_cal1 = "EST_G1_CAL1"
        set_column_properties(self.g1_cal1, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g2_cal1 = "EST_G2_CAL1"
        set_column_properties(self.g2_cal1, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.b1_cal1 = "B1_CAL1"
        set_column_properties(self.b1_cal1, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.b2_cal1 = "B2_CAL1"
        set_column_properties(self.b2_cal1, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g1_cal1_err = "G1_CAL1_ERR"
        set_column_properties(self.g1_cal1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g2_cal1_err = "G2_CAL1_ERR"
        set_column_properties(self.g2_cal1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e1_cal1_err = "E1_CAL1_ERR"
        set_column_properties(self.e1_cal1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e2_cal1_err = "E2_CAL1_ERR"
        set_column_properties(self.e2_cal1_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g1_cal2 = "EST_G1_CAL2"
        set_column_properties(self.g1_cal2, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g2_cal2 = "EST_G2_CAL2"
        set_column_properties(self.g2_cal2, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.b1_cal2 = "B1_CAL2"
        set_column_properties(self.b1_cal2, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.b2_cal2 = "B2_CAL2"
        set_column_properties(self.b2_cal2, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g1_cal2_err = "G1_CAL2_ERR"
        set_column_properties(self.g1_cal2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.g2_cal2_err = "G2_CAL2_ERR"
        set_column_properties(self.g2_cal2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e1_cal2_err = "E1_CAL2_ERR"
        set_column_properties(self.e1_cal2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.e2_cal2_err = "E2_CAL2_ERR"
        set_column_properties(self.e2_cal2_err, is_optional=True, dtype=">f8", fits_dtype="D")
        
        self.re = "EST_RE"
        set_column_properties(self.re, is_optional=True, comment="arcsec", dtype=">f8", fits_dtype="D")
        
        self.re_err = "EST_RE_ERR"
        set_column_properties(self.re_err, is_optional=True, comment="arcsec", dtype=">f8", fits_dtype="D")
        
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
