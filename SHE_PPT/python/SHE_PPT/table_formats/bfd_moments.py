""" @file bfd_moments.py

    Created 6 Dec 2017

    Format definition for BFD moments tables.
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

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table


logger = getLogger(mv.logger_name)

class BFDMomentsTableMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = "0.3"
        self.table_format = "she.bfdShearEstimates"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.extname = mv.extname_label

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        self.obs_time = mv.obs_time_label

        self.bfd_nlost = "NLOST"
        self.bfd_wt_n = "WT_N"
        self.bfd_wt_sigma = "WT_SIGMA"
        self.bfd_tmpl_snmin = "T_SNMIN"
        self.bfd_tmpl_sigma_xy = "T_SIGXY"
        self.bfd_tmpl_sigma_flux = "T_SIGFLX"
        self.bfd_tmpl_sigma_step = "T_SIGSTP"
        self.bfd_tmpl_sigma_max = "T_SIGMAX"
        self.bfd_tmpl_xy_max = "T_XYMAX"

        self.validated = "VALID"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, "#." + mv.shear_estimates_tag),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.obs_time, None),
                                     (self.bfd_nlost, None),
                                     (self.bfd_wt_n, None),
                                     (self.bfd_wt_sigma, None),
                                     (self.bfd_tmpl_snmin, None),
                                     (self.bfd_tmpl_sigma_xy, None),
                                     (self.bfd_tmpl_sigma_flux, None),
                                     (self.bfd_tmpl_sigma_step, None),
                                     (self.bfd_tmpl_sigma_max, None),
                                     (self.bfd_tmpl_xy_max, None),
                                     (self.validated, "0: Not tested; 1: Pass; -1: Fail")
                                     ))


        # A list of columns in the desired order
        self.all = list(self.comments.keys())

class BFDMomentsTableFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the bfd_moments_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = BFDMomentsTableMeta()

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

        def set_column_properties(name, is_optional = False, comment = None, dtype = ">f4", fits_dtype = "E",
                                   length = 1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Table column labels and properties

        self.ID = set_column_properties("SOURCE_ID", dtype = ">i8", fits_dtype = "K")

        self.flags = set_column_properties("FLAGS", dtype = ">i8", fits_dtype = "K")
        self.fit_class = set_column_properties("FITCLASS", dtype = ">i2", fits_dtype = "I")

        self.x_world = set_column_properties("X_WORLD_CORR", is_optional = False, comment = "deg")
        self.y_world = set_column_properties("Y_WORLD_CORR", is_optional = False, comment = "deg")

        self.x_world_var = set_column_properties("ERRX2_WORLD_CORR", is_optional = True, comment = "deg**2")
        self.y_world_var = set_column_properties("ERRY2_WORLD_CORR", is_optional = True, comment = "deg**2")

        # BFD specific columns
        self.bfd_moments = set_column_properties("BFD_MOMENTS", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_deriv_moments_dg1 = set_column_properties("BFD_DM_DG1", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_deriv_moments_dg2 = set_column_properties("BFD_DM_DG2", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_deriv_moments_dmu = set_column_properties("BFD_DM_DMU", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dg1dg1 = set_column_properties("BFD_D2M_DG1DG1", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dg1dg2 = set_column_properties("BFD_D2M_DG1DG2", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dg2dg2 = set_column_properties("BFD_D2M_DG2DG2", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dg1dmu = set_column_properties("BFD_D2M_DG1DMU", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dg2dmu = set_column_properties("BFD_D2M_DG2DMU", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_2ndderiv_moments_dmudmu = set_column_properties("BFD_D2M_DMUDMU", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 7)
        self.bfd_template_weight = set_column_properties("BFD_TMPL_WEIGHT", is_optional = True, dtype = ">F8", fits_dtype = "D")
        self.bfd_jsuppress = set_column_properties("BFD_JSUPPRESS", is_optional = True, dtype = ">F8", fits_dtype = "D")
        self.bfd_pqr = set_column_properties("BFD_PQR", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 6)

        self.bfd_cov_even = set_column_properties("BFD_COV_EVEN", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 15)
        self.bfd_cov_odd = set_column_properties("BFD_COV_ODD", is_optional = True, dtype = ">F8", fits_dtype = "D", length = 3)

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported
bfd_moments_table_format = BFDMomentsTableFormat()

# And a convient alias for it
tf = bfd_moments_table_format

def make_bfd_moments_table_header(detector_x = 1,
                                      detector_y = 1,
                                      model_hash = None,
                                      model_seed = None,
                                      noise_seed = None,
                                      detector = None,
                                      obs_time = None,
                                      bfd_nlost = None,
                                      bfd_wt_n = None,
                                      bfd_wt_sigma = None,
                                      bfd_tmpl_snmin = None,
                                      bfd_tmpl_sigma_xy = None,
                                      bfd_tmpl_sigma_flux = None,
                                      bfd_tmpl_sigma_step = None,
                                      bfd_tmpl_sigma_max = None,
                                      bfd_tmpl_xy_max = None,):
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
        logger.warn("'detector' argument for make_*_table_header is deprecated: Use detector_x and detector_y instead.")
        detector_x = detector % 6
        detector_y = detector // 6

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.extname] = dtc.get_id_string(detector_x, detector_y) + "." + mv.shear_estimates_tag

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    header[tf.m.obs_time] = obs_time

    header[tf.m.bfd_nlost] = bfd_nlost
    header[tf.m.bfd_wt_n] = bfd_wt_n
    header[tf.m.bfd_wt_sigma] = bfd_wt_sigma
    header[tf.m.bfd_tmpl_snmin] = bfd_tmpl_snmin
    header[tf.m.bfd_tmpl_sigma_xy] = bfd_tmpl_sigma_xy
    header[tf.m.bfd_tmpl_sigma_flux] = bfd_tmpl_sigma_flux
    header[tf.m.bfd_tmpl_sigma_step] = bfd_tmpl_sigma_step
    header[tf.m.bfd_tmpl_sigma_max] = bfd_tmpl_sigma_max
    header[tf.m.bfd_tmpl_xy_max] = bfd_tmpl_xy_max

    header[tf.m.validated] = 0

    return header

def initialise_bfd_moments_table(detections_table = None,
                                     optional_columns = None,
                                     detector_x = None,
                                     detector_y = None,
                                     model_hash = None,
                                     model_seed = None,
                                     noise_seed = None,
                                     detector = None,
                                     obs_time = None,
                                     bfd_nlost = None,
                                     bfd_wt_n = None,
                                     bfd_wt_sigma = None,
                                     bfd_tmpl_snmin = None,
                                     bfd_tmpl_sigma_xy = None,
                                     bfd_tmpl_sigma_flux = None,
                                     bfd_tmpl_sigma_step = None,
                                     bfd_tmpl_sigma_max = None,
                                     bfd_tmpl_xy_max = None,):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param detections_table <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param detector <int?> Detector this table corresponds to

        @return bfd_moments_table <astropy.table.Table>
    """

    if detector is not None:
        detector_x, detector_y = dtc.resolve_detector_xy(detector)

    assert (detections_table is None) or (is_in_format(detections_table, detf, strict = False))

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

    bfd_moments_table = Table(init_cols, names = names, dtype = dtypes)

    if detections_table is not None:
        if detector_x is None or detector_y is None:
            detector_x, detector_y = dtc.get_detector_xy(detections_table.meta[detf.m.extname])
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

    bfd_moments_table.meta = make_bfd_moments_table_header(detector_x = detector_x,
                                                                   detector_y = detector_y,
                                                                   model_hash = model_hash,
                                                                   model_seed = model_seed,
                                                                   noise_seed = noise_seed,
                                                                   obs_time = obs_time,
                                                                   bfd_nlost = bfd_nlost,
                                                                   bfd_wt_n = bfd_wt_n,
                                                                   bfd_wt_sigma = bfd_wt_sigma,
                                                                   bfd_tmpl_snmin = bfd_tmpl_snmin,
                                                                   bfd_tmpl_sigma_xy = bfd_tmpl_sigma_xy,
                                                                   bfd_tmpl_sigma_flux = bfd_tmpl_sigma_flux,
                                                                   bfd_tmpl_sigma_step = bfd_tmpl_sigma_step,
                                                                   bfd_tmpl_sigma_max = bfd_tmpl_sigma_max,
                                                                   bfd_tmpl_xy_max = bfd_tmpl_xy_max,)

    assert(is_in_format(bfd_moments_table, tf))

    return bfd_moments_table
