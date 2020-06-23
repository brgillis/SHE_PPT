""" @file galaxy_population.py

    Created 10 Oct 2017

    Format definition for galaxy population table.
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

fits_version = "8.0"
fits_def = "she.galaxyPopulationPriors"


class GalaxyPopulationPriorsTableMeta(object):
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.cnd_field = "CNDFIELD"
        self.tscope = "TSCOPE"
        self.detect = "DETECTOR"
        self.date_hst = "DATE_HST"
        self.data_ver = "DATA_VER"
        self.date_cnd = "DATE_CND"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.cnd_field, None),
                                     (self.tscope, None),
                                     (self.detect, None),
                                     (self.date_hst, None),
                                     (self.data_ver, None),
                                     (self.date_cnd, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class GalaxyPopulationPriorsTableFormat(object):
    """
        @brief A class defining the format for galaxy population priors tables. Only the galaxy_population_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = GalaxyPopulationPriorsTableMeta()

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

        # Column names and info

        self.ID = set_column_properties(
            "SHE_GALPOP_OBJECT_ID", dtype=">a20", fits_dtype="PA(20)")

        self.ra = set_column_properties(
            "SHE_GALPOP_RA", comment="deg", dtype=">f8", fits_dtype="D")
        self.dec = set_column_properties(
            "SHE_GALPOP_DEC", comment="deg", dtype=">f8", fits_dtype="D")

        self.zp = set_column_properties(
            "SHE_GALPOP_Z_PHOT")
        self.zs = set_column_properties(
            "SHE_GALPOP_Z_SPEC")

        self.iab = set_column_properties(
            "SHE_GALPOP_I_AB", comment="mag", dtype=">f4", fits_dtype="E")

        self.vab = set_column_properties(
            "SHE_GALPOP_V_AB", comment="mag", dtype=">f4", fits_dtype="E")

        self.sers_sing_fit = set_column_properties(
            "SHE_GALPOP_N_SERSIC_SINGLE_FIT", dtype=">f4", fits_dtype="E")
        self.sers_two_fit = set_column_properties(
            "SHE_GALPOP_N_SERSIC_BULGE_TWO_COMP_FIT", dtype=">f4", fits_dtype="E")
        self.disk_length = set_column_properties(
            "SHE_GALPOP_H_DISK_ARCSEC", comment="arcsec", dtype=">f4", fits_dtype="E")
        self.bulge_hlr = set_column_properties(
            "SHE_GALPOP_REFF_BULGE", dtype=">f4", fits_dtype="E")
        self.tau_b_rst = set_column_properties(
            "SHE_GALPOP_TAU_B_REST", dtype=">f4", fits_dtype="E")
        self.x = set_column_properties(
            "SHE_GALPOP_X_CENTRE_PIXEL", dtype=">f4", fits_dtype="E")
        self.y = set_column_properties(
            "SHE_GALPOP_Y_CENTRE_PIXEL", dtype=">f4", fits_dtype="E")
        self.tilt = set_column_properties(
            "SHE_GALPOP_THETA_DEG", comment="deg", dtype=">f4", fits_dtype="E")
        self.rotation = set_column_properties(
            "SHE_GALPOP_POS_ANGLE_DEG", comment="deg", dtype=">f4", fits_dtype="E")
        self.one_component_chi2 = set_column_properties(
            "SHE_GALPOP_CHI2_SINGE_FIT", dtype=">f4", fits_dtype="E")
        self.two_component_chi2 = set_column_properties(
            "SHE_GALPOP_CHI2_TWO_COMP_FIT", dtype=">f4", fits_dtype="E")
        self.two_component_dof = set_column_properties(
            "SHE_GALPOP_NDEG_TWO_COMP_FIT", dtype=">i8", fits_dtype="K")
        self.bulge_fd_f435w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F435W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f435w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F435W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f606w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F606W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f606w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F606W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f775w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F775W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f775w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F775W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f814w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F814W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f814w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F814W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f850lp = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F850LP", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f850lp_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F850LP", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f105w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F105W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f105w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F105W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f125w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F125W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f125w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F125W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f160w = set_column_properties(
            "SHE_GALPOP_FLUX_BULGE_NJY_F160W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.bulge_fd_f160w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F160W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f435w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F435W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f435w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F435W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f606w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F606W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f606w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F606W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f775w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F775W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f775w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F775W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f814w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F814W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f814w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F814W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f850lp = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F850LP", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f850lp_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F850LP", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f105w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F105W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f105w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F105W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f125w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F125W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f125w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F125W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f160w = set_column_properties(
            "SHE_GALPOP_FLUX_DISK_NJY_F160W", comment="nJy", dtype=">f4", fits_dtype="E")
        self.disk_fd_f160w_err = set_column_properties(
            "SHE_GALPOP_FLUX_ERR_DISK_NJY_F160W", comment="nJy", dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
galaxy_population_table_format = GalaxyPopulationPriorsTableFormat()

# And a convient alias for it
tf = galaxy_population_table_format


def make_galaxy_population_table_header(cnd_field=None,
                                        tscope=None,
                                        detect=None,
                                        date_hst=None,
                                        data_ver=None,
                                        date_cnd=None):
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def
    header[tf.m.cnd_field] = cnd_field
    header[tf.m.tscope] = tscope
    header[tf.m.detect] = detect
    header[tf.m.date_hst] = date_hst
    header[tf.m.data_ver] = data_ver
    header[tf.m.date_cnd] = date_cnd
    return header


def initialise_galaxy_population_table(optional_columns=None,
                                       cnd_field=None,
                                       tscope=None,
                                       detect=None,
                                       date_hst=None,
                                       data_ver=None,
                                       date_cnd=None):
    """
        @brief Initialise a galaxy population table.

        @return galaxy_population_table <astropy.Table>
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

    galaxy_population_table = Table(init_cols, names=names, dtype=dtypes)

    galaxy_population_table.meta = make_galaxy_population_table_header(
        cnd_field=cnd_field, tscope=tscope, detect=detect,
        date_hst=date_hst, data_ver=data_ver, date_cnd=date_cnd)

    assert(is_in_format(galaxy_population_table, tf))

    return galaxy_population_table
