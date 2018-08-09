""" @file shear_estimates.py

    Created 22 Aug 2017

    Format definition for shear estimates tables.
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

from collections import OrderedDict

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table


logger = getLogger(mv.logger_name)

num_chains = 1
len_chain = 200


class ShearEstimatesTableMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = "0.4"
        self.table_format = "she.shearEstimates"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.extname = mv.extname_label

        self.num_chains = "NCHAIN"
        self.len_chain = "LCHAIN"

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        self.obs_time = mv.obs_time_label

        self.validated = "VALID"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname,
                                      "#." + mv.shear_estimates_tag),
                                     (self.num_chains, None),
                                     (self.len_chain, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.obs_time,
                                      "Mean of all stacked exposures."),
                                     (self.validated,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


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

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Table column labels and properties

        self.ID = set_column_properties(
            "SOURCE_ID", dtype=">i8", fits_dtype="K")

        # Measured values
        self.g1 = set_column_properties("G1", dtype=">f8", fits_dtype="D")
        self.g2 = set_column_properties("G2", dtype=">f8", fits_dtype="D")
        self.g1_err = set_column_properties(
            "G1_ERR", is_optional=False, dtype=">f8", fits_dtype="D")
        self.g2_err = set_column_properties(
            "G2_ERR", is_optional=False, dtype=">f8", fits_dtype="D")
        self.g1g2_covar = set_column_properties(
            "G1G2_COVAR", is_optional=False, dtype=">f8", fits_dtype="D")
        self.e1_err = set_column_properties(
            "E1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_err = set_column_properties(
            "E2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1e2_covar = set_column_properties(
            "E1E2_COVAR", is_optional=True, dtype=">f8", fits_dtype="D")

        self.flags = set_column_properties(
            "FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties(
            "FITCLASS", dtype=">i2", fits_dtype="I")

        self.re = set_column_properties(
            "RE", is_optional=False, comment="arcsec", dtype=">f4", fits_dtype="E")
        self.re_err = set_column_properties(
            "RE_ERR", is_optional=True, comment="arcsec", dtype=">f4", fits_dtype="E")

        self.x_world = set_column_properties(
            "X_WORLD_CORR", is_optional=False, comment="deg", dtype=">f8", fits_dtype="D")
        self.y_world = set_column_properties(
            "Y_WORLD_CORR", is_optional=False, comment="deg", dtype=">f8", fits_dtype="D")

        self.x_world_var = set_column_properties(
            "ERRX2_WORLD_CORR", is_optional=True, comment="deg**2", dtype=">f8", fits_dtype="D")
        self.y_world_var = set_column_properties(
            "ERRY2_WORLD_CORR", is_optional=True, comment="deg**2", dtype=">f8", fits_dtype="D")

        self.flux = set_column_properties(
            "FLUX", is_optional=True, comment="ADU")
        self.flux_err = set_column_properties(
            "FLUX_ERR", is_optional=True, comment="ADU")

        self.bulge_fraction = set_column_properties(
            "BULGE_FRAC", is_optional=True)
        self.bulge_fraction_err = set_column_properties(
            "BULGE_FRAC_ERR", is_optional=True)

        self.snr = set_column_properties("SNR", is_optional=False)
        self.snr_err = set_column_properties("SNR_ERR", is_optional=True)

        # Data needed for validation tests
        self.x_pix_stacked = set_column_properties(
            "X_PIX_STACKED", is_optional=True, comment="pixels in stacked frame")
        self.y_pix_stacked = set_column_properties(
            "Y_PIX_STACKED", is_optional=True, comment="pixels in stacked frame")
        self.color = set_column_properties(
            "COLOR", is_optional=True, comment="TBD which color to use")
        self.sky_bg = set_column_properties(
            "SKY_BG", is_optional=True, comment="ADU")

        # LensMC chains to describe PDFs of measurements
        self.g1_chain = set_column_properties(
            "G1_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=num_chains * len_chain)
        self.g2_chain = set_column_properties(
            "G2_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=num_chains * len_chain)
        self.re_chain = set_column_properties("RE_CHAIN", is_optional=True, comment="arcsec", dtype=">f4", fits_dtype="E",
                                              length=num_chains * len_chain)
        self.x_chain = set_column_properties(
            "X_CHAIN", is_optional=True, comment="deg", length=num_chains * len_chain)
        self.y_chain = set_column_properties(
            "Y_CHAIN", is_optional=True, comment="deg", length=num_chains * len_chain)

        self.flux_chain = set_column_properties(
            "FLUX_CHAIN", is_optional=True, comment="ADU", length=num_chains * len_chain)
        self.bulge_fraction_chain = set_column_properties(
            "BULGE_FRAC_CHAIN", is_optional=True, length=num_chains * len_chain)
        self.snr_chain = set_column_properties(
            "SNR_CHAIN", is_optional=True, length=num_chains * len_chain)

        self.lr1_chain = set_column_properties(
            "LR1_CHAIN", is_optional=True, length=num_chains * len_chain)
        self.lr2_chain = set_column_properties(
            "LR2_CHAIN", is_optional=True, length=num_chains * len_chain)

        # LensMC-specific calibrated data (will probably be deprecated once
        # this is folded into calib. pipeline)
        self.g1_cal1 = set_column_properties(
            "G1_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal1 = set_column_properties(
            "G2_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b1_cal1 = set_column_properties(
            "B1_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b2_cal1 = set_column_properties(
            "B2_CAL1", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g1_cal1_err = set_column_properties(
            "G1_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal1_err = set_column_properties(
            "G2_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1_cal1_err = set_column_properties(
            "E1_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_cal1_err = set_column_properties(
            "E2_CAL1_ERR", is_optional=True, dtype=">f8", fits_dtype="D")

        self.g1_cal2 = set_column_properties(
            "G1_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal2 = set_column_properties(
            "G2_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b1_cal2 = set_column_properties(
            "B1_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.b2_cal2 = set_column_properties(
            "B2_CAL2", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g1_cal2_err = set_column_properties(
            "G1_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.g2_cal2_err = set_column_properties(
            "G2_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e1_cal2_err = set_column_properties(
            "E1_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")
        self.e2_cal2_err = set_column_properties(
            "E2_CAL2_ERR", is_optional=True, dtype=">f8", fits_dtype="D")

        self.chi2 = set_column_properties(
            "CHI2", is_optional=True, dtype=">f8", fits_dtype="D")

        self.dof = set_column_properties(
            "DOF", is_optional=True, dtype=">i8", fits_dtype="K")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
shear_estimates_table_format = ShearEstimatesTableFormat()

# And a convient alias for it
tf = shear_estimates_table_format


def make_shear_estimates_table_header(detector_x=1,
                                      detector_y=1,
                                      model_hash=None,
                                      model_seed=None,
                                      noise_seed=None,
                                      obs_time=None,
                                      detector=None):
    """
        @brief Generate a header for a shear estimates table.

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @param obs_time <str> Mean observation time of the corresponding detections

        @param detector <str> Detector this table corresponds to

        @return header <dict>
    """

    if detector is not None:
        logger.warn(
            "'detector' argument for make_*_table_header is deprecated: Use detector_x and detector_y instead.")
        detector_x = detector % 6
        detector_y = detector // 6

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.extname] = dtc.get_id_string(
        detector_x, detector_y) + "." + mv.shear_estimates_tag

    header[tf.m.num_chains] = num_chains
    header[tf.m.len_chain] = len_chain

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    header[tf.m.obs_time] = obs_time

    header[tf.m.validated] = 0

    return header


def initialise_shear_estimates_table(detections_table=None,
                                     optional_columns=None,
                                     detector_x=None,
                                     detector_y=None,
                                     model_hash=None,
                                     model_seed=None,
                                     noise_seed=None,
                                     obs_time=None,
                                     detector=None):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param detections_table <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param obs_time <str> Mean observation time of the corresponding detections

        @param detector <str> Detector this table corresponds to

        @return shear_estimates_table <astropy.table.Table>
    """

    if detector is not None:
        detector_x, detector_y = dtc.resolve_detector_xy(detector)

    assert (detections_table is None) or (
        is_in_format(detections_table, detf, strict=False))

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

    shear_estimates_table = Table(init_cols, names=names, dtype=dtypes)

    if detections_table is not None:
        if model_hash is None and detf.m.model_hash in detections_table.meta:
            model_hash = detections_table.meta[detf.m.model_hash]
        if model_seed is None and detf.m.model_seed in detections_table.meta:
            model_seed = detections_table.meta[detf.m.model_seed]
        if noise_seed is None and detf.m.noise_seed in detections_table.meta:
            noise_seed = detections_table.meta[detf.m.noise_seed]

    if detector_x is None:
        detector_x = 1
    if detector_y is None:
        detector_y = 1

    shear_estimates_table.meta = make_shear_estimates_table_header(detector_x=detector_x,
                                                                   detector_y=detector_y,
                                                                   model_hash=model_hash,
                                                                   model_seed=model_seed,
                                                                   noise_seed=noise_seed,
                                                                   obs_time=obs_time)

    assert(is_in_format(shear_estimates_table, tf))

    return shear_estimates_table
