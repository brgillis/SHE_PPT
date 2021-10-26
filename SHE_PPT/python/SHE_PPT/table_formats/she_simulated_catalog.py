""" @file details.py

    Created 21 Aug 2017

    Format definition for galaxy details tables.
"""

__updated__ = "2021-08-12"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from collections import OrderedDict

from EL_PythonUtils.utilities import hash_any
from ..constants.fits import (FITS_DEF_LABEL, FITS_VERSION_LABEL, GAIN_LABEL, MODEL_HASH_LABEL, MODEL_SEED_LABEL,
                              NOISE_SEED_LABEL, )
from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format

UNIT_DEG = "[deg]"

fits_version = "8.0"
fits_def = "she.simulatedCatalog"

logger = getLogger(__name__)


class SheSimulatedCatalogMeta(SheTableMeta):
    """
        @brief A class defining the metadata for details tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    subtracted_sky_level: str = "S_SKYLV"
    unsubtracted_sky_level: str = "US_SKYLV"
    read_noise: str = "RD_NOISE"
    gain: str = GAIN_LABEL

    model_hash: str = MODEL_HASH_LABEL
    model_seed: str = MODEL_SEED_LABEL
    noise_seed: str = NOISE_SEED_LABEL

    def __init__(self):
        # Store the less-used comments in a dict
        super().__init__(comments = OrderedDict(((self.fits_version, None),
                                                 (self.fits_def, None),
                                                 (self.subtracted_sky_level,
                                                  "ADU/arcsec^2"),
                                                 (self.unsubtracted_sky_level,
                                                  "ADU/arcsec^2"),
                                                 (self.read_noise, "e-/pixel"),
                                                 (self.gain, "e-/ADU"),
                                                 (self.model_hash, None),
                                                 (self.model_seed, None),
                                                 (self.noise_seed, None),
                                                 )))


class SheSimulatedCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy details tables. Only the details_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheSimulatedCatalogMeta())

        # Table column labels
        self.ID = self.set_column_properties("OBJECT_ID", dtype = ">i8", fits_dtype = "K")

        self.group_ID = self.set_column_properties("GROUP_ID", dtype = ">i8", fits_dtype = "K")

        self.ra = self.set_column_properties("RIGHT_ASCENSION", comment = "ra (deg)")
        self.dec = self.set_column_properties("DECLINATION", comment = "dec (deg)")

        self.hlr_bulge = self.set_column_properties(
            "HLR_BULGE", comment = "arcsec")
        self.hlr_disk = self.set_column_properties(
            "HLR_DISK", comment = "arcsec")

        self.bulge_ellipticity = self.set_column_properties("BULGE_ELLIPTICITY")
        self.bulge_axis_ratio = self.set_column_properties("BULGE_AXIS_RATIO")
        self.bulge_fraction = self.set_column_properties("BULGE_FRACTION")
        self.disk_height_ratio = self.set_column_properties("DISK_HEIGHT_RATIO")

        self.z = self.set_column_properties("REDSHIFT")

        self.magnitude = self.set_column_properties("MAGNITUDE", comment = "VIS filter")

        self.snr = self.set_column_properties("SNR", comment = "Sum in quadrature over detections")

        self.sersic_index = self.set_column_properties("SERSIC_INDEX")

        self.rotation = self.set_column_properties("ROTATION", comment = UNIT_DEG)
        self.spin = self.set_column_properties("SPIN", comment = UNIT_DEG)
        self.tilt = self.set_column_properties("TILT", comment = UNIT_DEG)

        self.g1 = self.set_column_properties("G1_WORLD")
        self.g2 = self.set_column_properties("G2_WORLD")

        self.target_galaxy = self.set_column_properties("is_target_galaxy", dtype = "bool", fits_dtype = "L")

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_simulated_catalog(*args, **kwargs)


# Define an instance of this object that can be imported
details_table_format = SheSimulatedCatalogFormat()

# And a convenient alias for it
tf = details_table_format


def make_details_table_header(subtracted_sky_level = None,
                              unsubtracted_sky_level = None,
                              read_noise = None,
                              gain = None,
                              model_hash = None,
                              model_seed = None,
                              noise_seed = None):
    """
        @brief Generate a header for a galaxy details table.

        @param subtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)

        @param unsubtracted_sky_level <float> Units of ADU/arcsec^2 (should we change this?)

        @param read_noise <float> Units of e-/pixel

        @param gain <float> Units of e-/ADU

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    header[tf.m.subtracted_sky_level] = subtracted_sky_level
    header[tf.m.unsubtracted_sky_level] = unsubtracted_sky_level
    header[tf.m.read_noise] = read_noise
    header[tf.m.gain] = gain

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    return header


def initialise_simulated_catalog(image_group_phl = None,
                                 options = None,
                                 size = None,
                                 optional_columns = None,
                                 init_cols = None,
                                 subtracted_sky_level = None,
                                 unsubtracted_sky_level = None,
                                 read_noise = None,
                                 gain = None,
                                 model_hash = None,
                                 model_seed = None,
                                 noise_seed = None, ):
    """
        @brief Initialise a detections table.

        @param image_phl <SHE_SIM.Image>

        @param options <dict> Options dictionary

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is psf_x and psf_y

        @param detector <int?> Detector for this image, if applicable. Will override ID of image object if set

        @return details_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    details_table = init_table(tf, optional_columns = optional_columns, init_cols = init_cols, size = size)

    if image_group_phl is not None:

        # Get values from the image group object, unless they were passed
        # explicitly

        if subtracted_sky_level is None:
            subtracted_sky_level = image_group_phl.get_param_value(
                'subtracted_background')

        if unsubtracted_sky_level is None:
            unsubtracted_sky_level = image_group_phl.get_param_value(
                'unsubtracted_background')

        if model_seed is None:
            model_seed = image_group_phl.get_seed()

    if options is not None:

        # Get values from the options dict, unless they were passed explicitly

        if read_noise is None:
            read_noise = options['read_noise']
        if gain is None:
            gain = options['gain']
        if model_hash is None:
            model_hash = hash_any(options.items(), format = "base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']

    details_table.meta = make_details_table_header(subtracted_sky_level = subtracted_sky_level,
                                                   unsubtracted_sky_level = unsubtracted_sky_level,
                                                   read_noise = read_noise,
                                                   gain = gain,
                                                   model_hash = model_hash,
                                                   model_seed = model_seed,
                                                   noise_seed = noise_seed, )

    assert is_in_format(details_table, tf)

    return details_table
