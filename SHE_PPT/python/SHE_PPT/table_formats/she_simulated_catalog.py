""" @file details.py

    Created 21 Aug 2017

    Format definition for galaxy details tables.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2020-06-23"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.flags import she_flag_version
from SHE_PPT.utility import hash_any

fits_version = "8.0"
fits_def = "she.simulatedCatalog"

logger = getLogger(mv.logger_name)


class DetailsTableMeta(object):
    """
        @brief A class defining the metadata for details tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.subtracted_sky_level = "S_SKYLV"
        self.unsubtracted_sky_level = "US_SKYLV"
        self.read_noise = "RD_NOISE"
        self.gain = mv.gain_label

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
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
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class DetailsTableFormat(object):
    """
        @brief A class defining the format for galaxy details tables. Only the details_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = DetailsTableMeta()

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

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Table column labels
        self.ID = set_column_properties("OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.group_ID = set_column_properties("GROUP_ID", dtype=">i8", fits_dtype="K")

        self.ra = set_column_properties("RIGHT_ASCENSION", comment="ra (deg)")
        self.dec = set_column_properties("DECLINATION", comment="dec (deg)")

        self.hlr_bulge = set_column_properties(
            "HLR_BULGE", comment="arcsec")
        self.hlr_disk = set_column_properties(
            "HLR_DISK", comment="arcsec")

        self.bulge_ellipticity = set_column_properties("BULGE_ELLIPTICITY")
        self.bulge_axis_ratio = set_column_properties("BULGE_AXIS_RATIO")
        self.bulge_fraction = set_column_properties("BULGE_FRACTION")
        self.disk_height_ratio = set_column_properties("DISK_HEIGHT_RATIO")

        self.z = set_column_properties("REDSHIFT")

        self.magnitude = set_column_properties("MAGNITUDE", comment="VIS filter")

        self.snr = set_column_properties("SNR", comment="Sum in quadrature over detections")

        self.sersic_index = set_column_properties("SERSIC_INDEX")

        self.rotation = set_column_properties("ROTATION", comment="[deg]")
        self.spin = set_column_properties("SPIN", comment="[deg]")
        self.tilt = set_column_properties("TILT", comment="[deg]")

        self.g1 = set_column_properties("G1_WORLD")
        self.g2 = set_column_properties("G2_WORLD")

        self.target_galaxy = set_column_properties("is_target_galaxy", dtype="bool", fits_dtype="L")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
details_table_format = DetailsTableFormat()

# And a convient alias for it
tf = details_table_format


def make_details_table_header(subtracted_sky_level=None,
                              unsubtracted_sky_level=None,
                              read_noise=None,
                              gain=None,
                              model_hash=None,
                              model_seed=None,
                              noise_seed=None):
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


def initialise_details_table(image_group_phl=None,
                             options=None,
                             optional_columns=None,
                             subtracted_sky_level=None,
                             unsubtracted_sky_level=None,
                             read_noise=None,
                             gain=None,
                             model_hash=None,
                             model_seed=None,
                             noise_seed=None,):
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

    names = []
    init_cols = []
    dtypes = []
    for colname in tf.all:
        if (colname in tf.all_required) or (colname in optional_columns):
            names.append(colname)
            init_cols.append([])
            dtypes.append((tf.dtypes[colname], tf.lengths[colname]))

    details_table = Table(init_cols, names=names,
                          dtype=dtypes)

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
            model_hash = hash_any(options.items(), format="base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']

    details_table.meta = make_details_table_header(subtracted_sky_level=subtracted_sky_level,
                                                   unsubtracted_sky_level=unsubtracted_sky_level,
                                                   read_noise=read_noise,
                                                   gain=gain,
                                                   model_hash=model_hash,
                                                   model_seed=model_seed,
                                                   noise_seed=noise_seed,)

    assert(is_in_format(details_table, tf))

    return details_table
