""" @file mcmc_chains_table_format.py

    Created 4 Sep 2017

    Format definition for MCMC chains table.

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

from SHE_PPT.detections_table_format import tf as detf
from astropy.table import Table
from SHE_PPT import magic_values as mv

num_chains = 10
len_chain = 200

class MCMCChainsTableMeta(object):
    """
        @brief A class defining the metadata for MCMC chains tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.1.2"
        
        # Table metadata labels
        self.version = "SS_VER"
        
        self.extname = mv.extname_label
        
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        
        self.num_chains = "NCHAIN"
        self.len_chain = "LCHAIN"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.extname, "#."+mv.mcmc_chains_tag),
                                     (self.num_chains, None),
                                     (self.len_chain, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class MCMCChainsTableFormat(object):
    """
        @brief A class defining the format for MCMC chains tables. Only the
               mcmc_chains_table_format instance of this should generally be accessed,
               and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = MCMCChainsTableMeta()
        
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
        
        # Column names
        self.ID = "ID"
        set_column_properties(self.ID, dtype=">i8", fits_dtype="K")
        
        self.gal_g1 = "GAL_EST_G1"
        set_column_properties(self.gal_g1, dtype=">f4", fits_dtype="E", length=num_chains*len_chain)
        
        self.gal_g2 = "GAL_EST_G2"
        set_column_properties(self.gal_g2, dtype=">f4", fits_dtype="E", length=num_chains*len_chain)
        
        self.gal_re = "GAL_EST_RE"
        set_column_properties(self.gal_re, comment="arcsec", dtype=">f4", fits_dtype="E",
                              length=num_chains*len_chain)
        
        self.gal_x = "GAL_EST_X"
        set_column_properties(self.gal_x, comment="pixels", length=num_chains*len_chain)
        
        self.gal_y = "GAL_EST_Y"
        set_column_properties(self.gal_y, comment="pixels", length=num_chains*len_chain)
        
        self.gal_flux = "GAL_FLUX"
        set_column_properties(self.gal_flux, comment="ADU", length=num_chains*len_chain)
        
        self.gal_bulge_fraction = "GAL_BULGE_FRAC"
        set_column_properties(self.gal_bulge_fraction, length=num_chains*len_chain)
        
        self.gal_snr = "GAL_SNR"
        set_column_properties(self.gal_snr, length=num_chains*len_chain)
        
        self.gal_lr1 = "GAL_LR1"
        set_column_properties(self.gal_lr1, length=num_chains*len_chain)
        
        self.gal_lr2 = "GAL_LR2"
        set_column_properties(self.gal_lr2, length=num_chains*len_chain)
        
        # A list of columns in the desired order
        self.all = self.is_optional.keys()
        
        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported         
mcmc_chains_table_format = MCMCChainsTableFormat()

# And a convient alias for it
tf = mcmc_chains_table_format


def make_mcmc_chains_table_header(detector = -1,
                                  model_hash = None,
                                  model_seed = None,
                                  noise_seed = None,):
    """
        @brief Generate a header for an MCMC chains table.
        
        @param detector <int?> Detector for this image, if applicable
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <OrderedDict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    
    header[tf.m.extname] = str(detector) + "." + mv.mcmc_chains_tag
    
    header[tf.m.num_chains] = num_chains
    header[tf.m.len_chain] = len_chain
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_mcmc_chains_table(detections_table = None,
                                optional_columns = None):
    """
        @brief Initialise an mcmc chains table based on a detections table, with the
               desired set of optional columns
        
        @param detections_table <astropy.table.Table>
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is none
        
        @return mcmc_chains_table <astropy.Table>
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
    
    mcmc_chains_table = Table(init_cols, names=names,
                             dtype=dtypes)
    
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
    
    mcmc_chains_table.meta = make_mcmc_chains_table_header(detector = detector,
                                                           model_hash = model_hash,
                                                           model_seed = model_seed,
                                                           noise_seed = noise_seed)
    
    return mcmc_chains_table
