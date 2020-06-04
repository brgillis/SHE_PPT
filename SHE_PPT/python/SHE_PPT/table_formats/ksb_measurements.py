""" @file ksb_measurements.py

    Created 6 Dec 2017

    Format definition for ksb measurements tables.
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

__updated__ = "2019-02-27"

from collections import OrderedDict

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table


logger = getLogger(mv.logger_name)


class ksbMeasurementsTableMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = "8.0"
        self.table_format = "she.ksbMeasurements"

        # Table metadata labels
        self.fits_vers = "FITS_VER"
        #self.format = "SS_FMT"
        self.fits_def = "FITS_DEF"
        #self.extname = mv.extname_label
        self.sflagvers="SFLAGVERS"
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        self.obs_id = 0
        self.date_obs = mv.obs_time_label
        self.tile_id = 0
        
        self.validated = "VALID"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_vers, None),
                                     (self.fits_def, None),
                                     (self.sflagvers,None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.obs_id,None),
                                     (self.date_obs, None),
                                     (self.tile_id, None),
                                     (self.validated,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class ksbMeasurementsTableFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the ksb_measurements_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = ksbMeasurementsTableMeta()

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
            "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.fit_flags = set_column_properties(
            "SHE_KSB_FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = set_column_properties(
            "SHE_KSB_VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties(
            "SHE_KSB_FIT_CLASS", dtype=">i2", fits_dtype="I")
        
        self.ksb_g1 = set_column_properties(
            "SHE_KSB_G1", dtype=">f4", fits_dtype="E")
        self.ksb_g1_err = set_column_properties(
            "SHE_KSB_G1_ERR", dtype=">f4", fits_dtype="E")
        self.ksb_g2 = set_column_properties(
            "SHE_KSB_G2", dtype=">f4", fits_dtype="E")
        self.ksb_g2_err = set_column_properties(
            "SHE_KSB_G2_ERR", dtype=">f4", fits_dtype="E")
        self.ksb_g1g2_cov = set_column_properties(
            "SHE_KSB_G1G2_COVAR", dtype=">f4", fits_dtype="E")
        self.ksb_wgt = set_column_properties(
            "SHE_KSB_WEIGHT", dtype=">f4", fits_dtype="E")
        self.ksb_g1_unc = set_column_properties(
            "SHE_KSB_G1_UNCAL", dtype=">f4", fits_dtype="E")
        self.ksb_g1_unc_err = set_column_properties(
            "SHE_KSB_G1_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.ksb_g2_unc = set_column_properties(
            "SHE_KSB_G2_UNCAL", dtype=">f4", fits_dtype="E")
        self.ksb_g2_unc_err = set_column_properties(
            "SHE_KSB_G2_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.ksb_g1g2_unc_cov = set_column_properties(
            "SHE_KSB_G1G2_UNCAL_COVAR", dtype=">f4", fits_dtype="E")
        self.ksb_wgt_unc = set_column_properties(
            "SHE_KSB_WEIGHT_UNCAL", dtype=">f4", fits_dtype="E")
    
        self.updated_ra = set_column_properties(
            "SHE_KSB_UPDATED_RA", is_optional=False, comment="deg")
        self.updated_ra_err = set_column_properties(
            "SHE_KSB_UPDATED_RA_ERR", is_optional=False, comment="deg")
        self.updated_dec = set_column_properties(
            "SHE_KSB_UPDATED_DEC", is_optional=True, comment="deg")
        self.updated_dec_err = set_column_properties(
            "SHE_KSB_UPDATED_DEC_ERR", is_optional=True, comment="deg")

        # ksb specific columns
        self.ksb_re = set_column_properties(
            "SHE_KSB_RE", is_optional=True, dtype=">f4", fits_dtype="E")
        self.ksb_re_err = set_column_properties(
            "SHE_KSB_RE_ERR", is_optional=True, dtype=">f4", fits_dtype="E")
        self.ksb_flux = set_column_properties(
            "SHE_KSB_FLUX", is_optional=True, dtype=">f4", fits_dtype="E")
        self.ksb_flux_err = set_column_properties(
            "SHE_KSB_FLUX_ERR", is_optional=True, dtype=">f4", fits_dtype="E")
        self.ksb_snr = set_column_properties(
            "SHE_KSB_SNR", is_optional=True, dtype=">f4", fits_dtype="E")
        self.ksb_snr_err = set_column_properties(
            "SHE_KSB_SNR_ERR", is_optional=True, dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
ksb_measurements_table_format = ksbmeasurementsTableFormat()

# And a convient alias for it
tf = ksb_measurements_table_format


def make_ksb_measurements_table_header(detector_x=1,
                                  detector_y=1,
                                  detector=None,
                                  fits_ver=None,
                                  fits_def=None,
                                  sflagvers=None,
                                  model_hash=None,
                                  model_seed=None,
                                  noise_seed=None,
                                  obs_id=None,
                                  date_obs=None,
                                  tile_id=None,):
    """
        @brief Generate a header for a shear estimates table.

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @return header <dict>
    """

    if detector is not None:
        logger.warning(
            "'detector' argument for make_*_table_header is deprecated: Use detector_x and detector_y instead.")
        detector_x = detector % 6
        detector_y = detector // 6

    header = OrderedDict()

    header[tf.m.fits_vers] = tf.__version__
    header[tf.m.fits_def] = fits_def
    header[tf.m.sflagvers] = sflagvers
    
    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed
    
    header[tf.m.obs_id] = obs_id
    header[tf.m.date_obs] = date_obs
    header[tf.m.tile_id] = tile_id
    
    header[tf.m.validated] = 0

    return header


def initialise_ksb_measurements_table(detections_table=None,
                                 optional_columns=None,
                                 detector_x=None,
                                 detector_y=None,
                                 detector=None,
                                 fits_def=None,
                                 sflagvers=None,
                                 model_hash=None,
                                 model_seed=None,
                                 noise_seed=None,
                                 obs_id=None,
                                 date_obs=None,
                                 tile_id=None,
                                 ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param detections_table <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param detector <int?> Detector this table corresponds to

        @return ksb_measurements_table <astropy.table.Table>
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

    ksb_measurements_table = Table(init_cols, names=names, dtype=dtypes)

    if detections_table is not None:
        if detector_x is None or detector_y is None:
            detector_x, detector_y = dtc.get_detector_xy(
                detections_table.meta[detf.m.extname])
        if model_hash is None:
            model_hash = detections_table.meta[detf.m.model_hash]
        if model_seed is None:
            model_seed = detections_table.meta[detf.m.model_seed]
        if noise_seed is None:
            noise_seed = detections_table.meta[detf.m.noise_seed]

    if detector_x is None:
        detector_x = 1
    if detector_y is None:
        detector_y = 1

    ksb_measurements_table.meta = make_ksb_measurements_table_header(detector_x=detector_x,
                                                           detector_y=detector_y,
                                                           detector=detector,
                                                           fits_def=fits_def,
                                                           sflagvers=sflagvers,
                                                           model_hash=model_hash,
                                                           model_seed=model_seed,
                                                           noise_seed=noise_seed,
                                                           obs_id=obs_id,
                                                           date_obs=date_obs,
                                                           tile_id=tile_id)
                     
    assert(is_in_format(ksb_measurements_table, tf))

    return ksb_measurements_table
