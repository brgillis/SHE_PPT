""" @file psf_table_format.py

    Created 29 Sep 2017

    Format definition for PSF table. This is based on Chris's description in the DPDD.
"""

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

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT.utility import hash_any
from SHE_PPT import magic_values as mv

class PSFTableMeta(object):
    """
        @brief A class defining the metadata for PSF tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1.0"
        self.table_format = "she.psfTable"
        
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
                                     (self.extname, "#."+mv.psf_cat_tag),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class PSFTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the detections_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = PSFTableMeta()
        
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
        
        # Column names and info
        
        self.ID = set_column_properties("Object ID", dtype=">i8", fits_dtype="K")
        
        self.template = set_column_properties("SED template", dtype=">i8", fits_dtype="K", comment="TBD")
        
        self.stamp_x = set_column_properties("Image X", dtype=">i2", fits_dtype="I", comment="pixel")
        self.stamp_y = set_column_properties("Image Y", dtype=">i2", fits_dtype="I", comment="pixel")
        
        self.psf_x = set_column_properties("PSF X", dtype=">f4", fits_dtype="E", comment="pixel")
        self.psf_y = set_column_properties("PSF Y", dtype=">f4", fits_dtype="E", comment="pixel")
        
        self.cal_time = set_column_properties("PSF Calibration Timestamp", dtype="S", fits_dtype="A", length=20)
        self.field_time = set_column_properties("PSF Field Timestamp", dtype="S", fits_dtype="A", length=20)
        
        # A list of columns in the desired order
        self.all = self.is_optional.keys()
        
        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported         
psf_table_format = PSFTableFormat()

# And a convient alias for it
tf = psf_table_format


def make_psf_table_header(detector = -1,
                          model_hash = None,
                          model_seed = None,
                          noise_seed = None,):
    """
        @brief Generate a header for a PSF table.
        
        @param detector <int?> Detector for this image, if applicable
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <OrderedDict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format
    
    header[tf.m.extname] = str(detector) + "." + mv.psf_cat_tag
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_psf_table(image = None,
                         options = None,
                         optional_columns = None,
                         detector = None):
    """
        @brief Initialise a PSF table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is psf_x and psf_y
        
        @param detector <int?> Detector for this image, if applicable. Will override ID of image object if set
        
        @return detections_table <astropy.Table>
    """
    
    if optional_columns is None:
        optional_columns = []
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
    
    psf_table = Table(init_cols, names=names, dtype=dtypes)
    
    if (image is not None) and (detector is None):
        detector = image.get_local_ID()
    
    if options is None:
        model_hash = None 
        model_seed = None
        noise_seed = None
    else:
        model_hash = hash_any(frozenset(options.items()),format="base64")
        model_seed = image.get_full_seed()
        noise_seed = options['noise_seed']
    
    psf_table.meta = make_psf_table_header(detector = detector,
                                           model_hash = model_hash,
                                           model_seed = model_seed,
                                           noise_seed = noise_seed,)
    
    return psf_table
