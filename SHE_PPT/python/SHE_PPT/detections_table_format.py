""" @file detections_table_format.py

    Created 22 Aug 2017

    Format definition for detections table.
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
from SHE_PPT.detector import get_id_string
from SHE_PPT.logging import getLogger

logger = getLogger(mv.logger_name)

class DetectionsTableMeta(object):
    """
        @brief A class defining the metadata for detections tables.
    """
    
    def __init__(self):
        
        self.__version__ = "0.3"
        self.table_format = "she.shearDetections"
        
        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"
        
        self.extname = mv.extname_label
        
        self.subtracted_sky_level = "S_SKYLV"
        self.unsubtracted_sky_level = "US_SKYLV"
        self.read_noise = "RD_NOISE"
        self.gain = mv.gain_label
        
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, "#."+mv.detections_tag),
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
            
            return name
        
        # Column names and info
        
        self.ID = set_column_properties("SOURCE_ID", dtype=">i8", fits_dtype="K")
        self.number = set_column_properties("NUMBER", is_optional=True, dtype=">i8", fits_dtype="K")
        
        self.gal_x = set_column_properties("X_IMAGE", is_optional=True, comment="pixel")
        self.gal_y = set_column_properties("Y_IMAGE", is_optional=True, comment="pixel")
        self.gal_a = set_column_properties("A_IMAGE", is_optional=True, comment="pixel")
        self.gal_b = set_column_properties("B_IMAGE", is_optional=True, comment="pixel")
        self.gal_theta = set_column_properties("THETA_IMAGE", is_optional=True, comment="deg")
        
        self.gal_x2_err = set_column_properties("ERRX2_IMAGE", is_optional=True, comment="pixel**2")
        self.gal_y2_err = set_column_properties("ERRY2_IMAGE", is_optional=True, comment="pixel**2")
        self.gal_a_err = set_column_properties("ERRA_IMAGE", is_optional=True, comment="pixel")
        self.gal_b_err = set_column_properties("ERRB_IMAGE", is_optional=True, comment="pixel")
        self.gal_theta_err = set_column_properties("ERRTHETA_IMAGE", is_optional=True, comment="deg")
        
        self.gal_x_world = set_column_properties("X_WORLD", is_optional=False, comment="deg")
        self.gal_y_world = set_column_properties("Y_WORLD", is_optional=False, comment="deg")
        self.gal_a_world = set_column_properties("A_WORLD", is_optional=True, comment="deg")
        self.gal_b_world = set_column_properties("B_WORLD", is_optional=True, comment="deg")
        self.gal_theta_world = set_column_properties("THETA_WORLD", is_optional=True, comment="deg")
        
        self.gal_x2_world_err = set_column_properties("ERRX2_WORLD", is_optional=True, comment="deg**2")
        self.gal_y2_world_err = set_column_properties("ERRY2_WORLD", is_optional=True, comment="deg**2")
        self.gal_a_world_err = set_column_properties("ERRA_WORLD", is_optional=True, comment="deg")
        self.gal_b_world_err = set_column_properties("ERRB_WORLD", is_optional=True, comment="deg")
        self.gal_theta_world_err = set_column_properties("ERRTHETA_WORLD", is_optional=True, comment="deg")
        
        self.gal_xwin_world = set_column_properties("XWIN_WORLD", is_optional=True, comment="deg")
        self.gal_ywin_world = set_column_properties("YWIN_WORLD", is_optional=True, comment="deg")
        self.gal_awin_world = set_column_properties("AWIN_WORLD", is_optional=True, comment="deg")
        self.gal_bwin_world = set_column_properties("BWIN_WORLD", is_optional=True, comment="deg")
        self.gal_thetawin_world = set_column_properties("THETAWIN_WORLD", is_optional=True, comment="deg")
        
        self.gal_x2win_world_err = set_column_properties("ERRX2WIN_WORLD", is_optional=True, comment="deg**2")
        self.gal_y2win_world_err = set_column_properties("ERRY2WIN_WORLD", is_optional=True, comment="deg**2")
        self.gal_awin_world_err = set_column_properties("ERRAWIN_WORLD", is_optional=True, comment="deg")
        self.gal_bwin_world_err = set_column_properties("ERRBWIN_WORLD", is_optional=True, comment="deg")
        self.gal_thetawin_world_err = set_column_properties("ERRTHETAWIN_WORLD", is_optional=True, comment="deg")
        
        self.gal_alpha = set_column_properties("ALPHA_J2000", is_optional=True, comment="deg")
        self.gal_delta = set_column_properties("DELTA_J2000", is_optional=True, comment="deg")
        self.gal_theta = set_column_properties("THETA_J2000", is_optional=True, comment="deg")
        self.gal_theta_err = set_column_properties("ERRTHETA_J2000", is_optional=True, comment="deg")
        
        self.gal_flux = set_column_properties("FLUX_AUTO", is_optional=True, comment="deg")
        self.gal_flux_err = set_column_properties("FLUXERR_AUTO", is_optional=True, comment="deg")
        
        self.gal_mag = set_column_properties("MAG_AUTO", is_optional=True, comment="VIS")
        self.gal_mag_err = set_column_properties("MAGERR_AUTO", is_optional=True, comment="VIS")
        
        self.gal_hlr = set_column_properties("FLUX_RADIUS", is_optional=True, comment="pixel")
        
        self.gal_flags = set_column_properties("FLAGS", is_optional=True, dtype=">i8", fits_dtype="K")
        
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


def make_detections_table_header(detector_x = 1,
                                 detector_y = 1,
                                 subtracted_sky_level = None,
                                 unsubtracted_sky_level = None,
                                 read_noise = None,
                                 gain = None,
                                 model_hash = None,
                                 model_seed = None,
                                 noise_seed = None,
                                 detector = None):
    """
        @brief Generate a header for a detections table.
        
        @param detector <int?> Detector for this image, if applicable
        
        @param subtracted_sky_level <float> Units of ADU/arcsec**2 (should we change this?)
        
        @param unsubtracted_sky_level <float> Units of ADU/arcsec**2 (should we change this?)
        
        @param read_noise <float> Units of e-/pixel
        
        @param gain <float> Units of e-/ADU
        
        @param model_hash <int> Hash of the physical model options dictionary
        
        @param model_seed <int> Full seed used for the physical model for this image
        
        @param noise_seed <int> Seed used for generating noise for this image
        
        @return header <OrderedDict>
    """
    
    if detector is not None:
        logger.warn("'detector' argument for make_*_table_header is deprecated: Use detector_x and detector_y instead.")
        detector_x = detector % 6
        detector_y = detector // 6
    
    header = OrderedDict()
    
    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format
    
    header[tf.m.extname] = get_id_string(detector_x,detector_y) + "." + mv.detections_tag
    
    header[tf.m.subtracted_sky_level] = subtracted_sky_level
    header[tf.m.unsubtracted_sky_level] = unsubtracted_sky_level
    header[tf.m.read_noise] = read_noise
    header[tf.m.gain] = gain
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    return header

def initialise_detections_table(image = None,
                                options = None,
                                optional_columns = None,
                                detector_x = 1,
                                detector_y = 1,
                                subtracted_sky_level = None,
                                unsubtracted_sky_level = None,
                                read_noise = None,
                                gain = None,
                                model_hash = None,
                                model_seed = None,
                                noise_seed = None,
                                detector = None):
    """
        @brief Initialise a detections table.
        
        @param image <SHE_SIM.Image> 
        
        @param options <dict> Options dictionary
        
        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is none
        
        @param detector <int?> Detector for this image, if applicable. Will override ID of image object if set
        
        @return detections_table <astropy.Table>
    """
    
    if detector is not None:
        logger.warn("'detector' argument for initialise_*_table is deprecated: Use detector_x and detector_y instead.")
        detector_x = detector % 6 + 1
        detector_y = detector // 6 + 1
    
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
    
    detections_table = Table(init_cols, names=names,
                             dtype=dtypes)
    
    if image is not None:
        
        # Get values from the image object, unless they were passed explicitly
        
        if detector_x or detector_y is None:
            detector_x = image.get_local_ID() % 6 + 1
            detector_y = image.get_local_ID() // 6 + 1
        
        if subtracted_sky_level is None:
            subtracted_sky_level = image.get_param_value('subtracted_background')
            
        if unsubtracted_sky_level is None:
            unsubtracted_sky_level = image.get_param_value('unsubtracted_background')
            
        if model_seed is None:
            model_seed = image.get_full_seed()
            
    if detector_x is None:
        detector_x = 1
    if detector_y is None:
        detector_y = 1
    
    if options is not None:
        
        # Get values from the options dict, unless they were passed explicitly
        
        if read_noise is None:
            read_noise = options['read_noise']
        if gain is None:
            gain = options['gain']
        if model_hash is None:
            model_hash = hash_any(frozenset(options.items()),format="base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']
    
    detections_table.meta = make_detections_table_header(detector_x = detector_x,
                                                         detector_y = detector_y,
                                                         subtracted_sky_level = subtracted_sky_level,
                                                         unsubtracted_sky_level = unsubtracted_sky_level,
                                                         read_noise = read_noise,
                                                         gain = gain,
                                                         model_hash = model_hash,
                                                         model_seed = model_seed,
                                                         noise_seed = noise_seed,)
    
    return detections_table
