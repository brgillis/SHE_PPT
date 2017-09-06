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

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT.utility import hash_any

class DetectionsTableMeta(object):
    """
        @brief A class defining the metadata for detections tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.2"
        
        # Table metadata labels
        
        self.version = "SS_VER"
        
        self.subtracted_sky_level = "S_SKYLV"
        self.unsubtracted_sky_level = "US_SKYLV"
        self.read_noise = "RD_NOISE"
        self.gain = "CCDGAIN"
        
        self.model_hash = "MHASH"
        self.model_seed = "MSEED"
        self.noise_seed = "NSEED"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.subtracted_sky_level, "ADU/arcsec**2"),
                                     (self.unsubtracted_sky_level, "ADU/arcsec**2"),
                                     (self.read_noise, "e-/pixel"),
                                     (self.gain, "e-/ADU"),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                   ))
        
        # A list of columns in the desired order
        self.all = self.comments.keys()

class DetectionsTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the detections_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    
    def __init__(self):
        
        # Get the metadata (contained within its own class)
        self.meta = DetectionsTableMeta()
        
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
        
        # Column names and info
        
        self.ID = "SOURCE_ID"
        set_column_properties(self.ID, dtype=">i8", fits_dtype="K")
        
        self.number = "NUMBER"
        set_column_properties(self.number, is_optional=True, dtype=">i8", fits_dtype="K")
        
        self.gal_x = "X_IMAGE"
        set_column_properties(self.gal_x, comment="pixel")
        
        self.gal_y = "Y_IMAGE"
        set_column_properties(self.gal_y, comment="pixel")
        
        self.psf_x = "PSF_X_IMAGE"
        set_column_properties(self.psf_x, is_optional=True, comment="pixel")
        
        self.psf_y = "PSF_Y_IMAGE"
        set_column_properties(self.psf_y, is_optional=True, comment="pixel")
        
        self.gal_a = "A_IMAGE"
        set_column_properties(self.gal_a, is_optional=True, comment="pixel")
        
        self.gal_b = "B_IMAGE"
        set_column_properties(self.gal_b, is_optional=True, comment="pixel")
        
        self.gal_theta = "THETA_IMAGE"
        set_column_properties(self.gal_theta, is_optional=True, comment="deg")
        
        self.gal_x2_err = "ERRX2_IMAGE"
        set_column_properties(self.gal_x2_err, comment="pixel**2")
        
        self.gal_y2_err = "ERRY2_IMAGE"
        set_column_properties(self.gal_y2_err, comment="pixel**2")
        
        self.gal_a_err = "ERRA_IMAGE"
        set_column_properties(self.gal_a_err, is_optional=True, comment="pixel")
        
        self.gal_b_err = "ERRB_IMAGE"
        set_column_properties(self.gal_b_err, is_optional=True, comment="pixel")
        
        self.gal_theta_err = "ERRTHETA_IMAGE"
        set_column_properties(self.gal_theta_err, is_optional=True, comment="deg")
        
        self.gal_x_world = "X_WORLD"
        set_column_properties(self.gal_x_world, is_optional=True, comment="deg")
        
        self.gal_y_world = "Y_WORLD"
        set_column_properties(self.gal_y_world, is_optional=True, comment="deg")
        
        self.gal_a_world = "A_WORLD"
        set_column_properties(self.gal_a_world, is_optional=True, comment="deg")
        
        self.gal_b_world = "B_WORLD"
        set_column_properties(self.gal_b_world, is_optional=True, comment="deg")
        
        self.gal_theta_world = "THETA_WORLD"
        set_column_properties(self.gal_theta_world, is_optional=True, comment="deg")
        
        self.gal_x2_world_err = "ERRX2_WORLD"
        set_column_properties(self.gal_x2_world_err, comment="deg**2")
        
        self.gal_y2_world_err = "ERRY2_WORLD"
        set_column_properties(self.gal_y2_world_err, comment="deg**2")
        
        self.gal_a_world_err = "ERRA_WORLD"
        set_column_properties(self.gal_a_world_err, is_optional=True, comment="deg")
        
        self.gal_b_world_err = "ERRB_WORLD"
        set_column_properties(self.gal_b_world_err, is_optional=True, comment="deg")
        
        self.gal_theta_world_err = "ERRTHETA_WORLD"
        set_column_properties(self.gal_theta_world_err, is_optional=True, comment="deg")
        
        self.gal_xwin_world = "XWIN_WORLD"
        set_column_properties(self.gal_xwin_world, is_optional=True, comment="deg")
        
        self.gal_ywin_world = "YWIN_WORLD"
        set_column_properties(self.gal_ywin_world, is_optional=True, comment="deg")
        
        self.gal_awin_world = "AWIN_WORLD"
        set_column_properties(self.gal_awin_world, is_optional=True, comment="deg")
        
        self.gal_bwin_world = "BWIN_WORLD"
        set_column_properties(self.gal_bwin_world, is_optional=True, comment="deg")
        
        self.gal_thetawin_world = "THETAWIN_WORLD"
        set_column_properties(self.gal_thetawin_world, is_optional=True, comment="deg")
        
        self.gal_x2win_world_err = "ERRX2WIN_WORLD"
        set_column_properties(self.gal_x2win_world_err, comment="deg**2")
        
        self.gal_y2win_world_err = "ERRY2WIN_WORLD"
        set_column_properties(self.gal_y2win_world_err, comment="deg**2")
        
        self.gal_awin_world_err = "ERRAWIN_WORLD"
        set_column_properties(self.gal_awin_world_err, is_optional=True, comment="deg")
        
        self.gal_bwin_world_err = "ERRBWIN_WORLD"
        set_column_properties(self.gal_bwin_world_err, is_optional=True, comment="deg")
        
        self.gal_thetawin_world_err = "ERRTHETAWIN_WORLD"
        set_column_properties(self.gal_thetawin_world_err, is_optional=True, comment="deg")
        
        self.gal_alpha = "ALPHA_J2000"
        set_column_properties(self.gal_alpha, is_optional=True, comment="deg")
        
        self.gal_delta = "DELTA_J2000"
        set_column_properties(self.gal_delta, is_optional=True, comment="deg")
        
        self.gal_theta = "THETA_J2000"
        set_column_properties(self.gal_theta, is_optional=True, comment="deg")
        
        self.gal_theta_err = "ERRTHETA_J2000"
        set_column_properties(self.gal_theta_err, is_optional=True, comment="deg")
        
        self.gal_flux = "FLUX_AUTO"
        set_column_properties(self.gal_flux, is_optional=True, comment="deg")
        
        self.gal_flux_err = "FLUXERR_AUTO"
        set_column_properties(self.gal_flux_err, is_optional=True, comment="deg")
        
        self.gal_mag = "MAG_AUTO"
        set_column_properties(self.gal_mag, is_optional=True, comment="VIS")
        
        self.gal_mag_err = "MAGERR_AUTO"
        set_column_properties(self.gal_mag_err, is_optional=True, comment="VIS")
        
        self.gal_hlr = "FLUX_RADIUS"
        set_column_properties(self.gal_hlr, is_optional=True, comment="pixel")
        
        self.gal_flags = "FLAGS"
        set_column_properties(self.gal_flags, is_optional=True, dtype=">i8", fits_dtype="K")
        
        # A list of columns in the desired order
        self.all = self.is_optional.keys()
        
        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported         
detections_table_format = DetectionsTableFormat()

# And a convient alias for it
tf = detections_table_format


def make_detections_table_header(subtracted_sky_level = None,
                                 unsubtracted_sky_level = None,
                                 read_noise = None,
                                 gain = None,
                                 model_hash = None,
                                 model_seed = None,
                                 noise_seed = None,):
    """
        @brief Generate a header for a detections table.
        
        @param subtracted_sky_level <float> Units of ADU/arcsec**2 (should we change this?)
        
        @param unsubtracted_sky_level <float> Units of ADU/arcsec**2 (should we change this?)
        
        @param read_noise <float> Units of e-/pixel
        
        @param gain <float> Units of e-/ADU
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <OrderedDict>
    """
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    
    header[tf.m.subtracted_sky_level] = subtracted_sky_level
    header[tf.m.unsubtracted_sky_level] = unsubtracted_sky_level
    header[tf.m.read_noise] = read_noise
    header[tf.m.gain] = gain
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_detections_table(image = None, options = None,
                                     optional_columns = None):
    """
        @brief Initialise a detections table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is psf_x and psf_y
        
        @return detections_table <astropy.Table>
    """
    
    if optional_columns is None:
        optional_columns = [tf.psf_x,tf.psf_y]
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
    
    detections_table = Table(init_cols, names=names,
                             dtype=dtypes)
    
    if image is None:
        subtracted_sky_level = None
        unsubtracted_sky_level = None
    else:
        subtracted_sky_level = image.get_param_value('subtracted_background')
        unsubtracted_sky_level = image.get_param_value('unsubtracted_background')
    
    if options is None:
        read_noise = None
        gain = None
        model_hash = None 
        model_seed = None
        noise_seed = None
    else:
        read_noise = options['read_noise']
        gain = options['gain']
        model_hash = hash_any(frozenset(options.items()),format="base64")
        model_seed = image.get_full_seed()
        noise_seed = options['noise_seed']
    
    detections_table.meta = make_detections_table_header(subtracted_sky_level = subtracted_sky_level,
                                                         unsubtracted_sky_level = unsubtracted_sky_level,
                                                         read_noise = read_noise,
                                                         gain = gain,
                                                         model_hash = model_hash,
                                                         model_seed = model_seed,
                                                         noise_seed = noise_seed,)
    
    return detections_table
