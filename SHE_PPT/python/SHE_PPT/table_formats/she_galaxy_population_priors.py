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

__updated__ = "2020-08-07"

from collections import OrderedDict


from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL, EXTNAME_LABEL
from ..table_utility import is_in_format, init_table, SheTableFormat


fits_version = "8.0"
fits_def = "she.galaxyPopulationPriors"


class SheGalaxyPopulationPriorsMeta():
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = FITS_VERSION_LABEL
        self.fits_def = FITS_DEF_LABEL

        self.cnd_field = "CNDFIELD"
        self.telescope = "TSCOPE"
        self.detector = "DETECTOR"
        self.date_hst = "DATE_HST"
        self.data_version = "DATA_VER"
        self.date_candels = "DATE_CND"
        self.data_release = "DATA_REL"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.cnd_field, None),
                                     (self.telescope, None),
                                     (self.detector, None),
                                     (self.date_hst, None),
                                     (self.data_version, None),
                                     (self.date_candels, None),
                                     (self.data_release, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheGalaxyPopulationPriorsFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the galaxy_population_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheGalaxyPopulationPriorsMeta())

        # Column names and info

        self.ID = self.set_column_properties(
                                        "SHE_GALPOP_OBJECT_ID", dtype=">a20", fits_dtype="PA(20)")

        self.ra = self.set_column_properties(
                                        "SHE_GALPOP_RA", comment="deg", dtype=">f8", fits_dtype="D")
        self.dec = self.set_column_properties(
                                         "SHE_GALPOP_DEC", comment="deg", dtype=">f8", fits_dtype="D")

        self.zp = self.set_column_properties(
                                        "SHE_GALPOP_Z_PHOT")
        self.zs = self.set_column_properties(
                                        "SHE_GALPOP_Z_SPEC")

        self.iab = self.set_column_properties(
                                         "SHE_GALPOP_I_AB", comment="mag",
                                         dtype=">f4", fits_dtype="E")

        self.vab = self.set_column_properties(
                                         "SHE_GALPOP_V_AB", comment="mag",
                                         dtype=">f4", fits_dtype="E")

        self.beta_0 = self.set_column_properties(
                                            "SHE_GALPOP_BETA_0", comment="mag",
                                            dtype=">f4", fits_dtype="E")
        self.e_bulge = self.set_column_properties(
                                             "SHE_GALPOP_E_BULGE", comment="mag",
                                             dtype=">f4", fits_dtype="E")
        self.e_disk = self.set_column_properties(
                                            "SHE_GALPOP_E_DISK", comment="mag",
                                            dtype=">f4", fits_dtype="E")
        self.e_galaxy = self.set_column_properties(
                                              "SHE_GALPOP_E_GALAXY", comment="mag",
                                              dtype=">f4", fits_dtype="E")

        self.sers_sing_fit = self.set_column_properties(
                                                   "SHE_GALPOP_N_SERSIC_SINGLE_FIT",
                                                   dtype=">f4", fits_dtype="E")
        self.sers_two_fit = self.set_column_properties(
                                                  "SHE_GALPOP_N_SERSIC_BULGE_TWO_COMP_FIT",
                                                  dtype=">f4", fits_dtype="E")
        self.disk_length = self.set_column_properties(
                                                 "SHE_GALPOP_H_DISK_ARCSEC", comment="arcsec",
                                                 dtype=">f4", fits_dtype="E")
        self.bulge_hlr = self.set_column_properties(
                                               "SHE_GALPOP_REFF_BULGE",
                                               dtype=">f4", fits_dtype="E")
        self.tau_b_rst = self.set_column_properties(
                                               "SHE_GALPOP_TAU_B_REST",
                                               dtype=">f4", fits_dtype="E")
        self.x = self.set_column_properties(
                                       "SHE_GALPOP_X_CENTRE_PIXEL",
                                       dtype=">f4", fits_dtype="E")
        self.y = self.set_column_properties(
                                       "SHE_GALPOP_Y_CENTRE_PIXEL",
                                       dtype=">f4", fits_dtype="E")
        self.tilt = self.set_column_properties(
                                          "SHE_GALPOP_THETA_DEG", comment="deg",
                                          dtype=">f4", fits_dtype="E")
        self.rotation = self.set_column_properties(
                                              "SHE_GALPOP_POS_ANGLE_DEG", comment="deg",
                                              dtype=">f4", fits_dtype="E")
        self.one_component_chi2 = self.set_column_properties(
                                                        "SHE_GALPOP_CHI2_SINGE_FIT",
                                                        dtype=">f4", fits_dtype="E")
        self.two_component_chi2 = self.set_column_properties(
                                                        "SHE_GALPOP_CHI2_TWO_COMP_FIT",
                                                        dtype=">f4", fits_dtype="E")
        self.two_component_dof = self.set_column_properties(
                                                       "SHE_GALPOP_NDEG_TWO_COMP_FIT",
                                                       dtype=">i8", fits_dtype="K")
        self.bulge_fd_f435w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F435W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f435w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F435W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f606w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F606W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f606w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F606W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f775w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F775W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f775w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F775W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f814w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F814W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f814w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F814W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f850lp = self.set_column_properties(
                                                     "SHE_GALPOP_FLUX_BULGE_NJY_F850LP", comment="nJy",
                                                     dtype=">f4", fits_dtype="E")
        self.bulge_fd_f850lp_err = self.set_column_properties(
                                                         "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F850LP", comment="nJy",
                                                         dtype=">f4", fits_dtype="E")
        self.bulge_fd_f105w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F105W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f105w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F105W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f125w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F125W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f125w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F125W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.bulge_fd_f160w = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_BULGE_NJY_F160W", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.bulge_fd_f160w_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_BULGE_NJY_F160W", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.disk_fd_f435w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F435W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f435w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F435W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f606w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F606W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f606w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F606W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f775w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F775W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f775w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F775W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f814w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F814W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f814w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F814W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f850lp = self.set_column_properties(
                                                    "SHE_GALPOP_FLUX_DISK_NJY_F850LP", comment="nJy",
                                                    dtype=">f4", fits_dtype="E")
        self.disk_fd_f850lp_err = self.set_column_properties(
                                                        "SHE_GALPOP_FLUX_ERR_DISK_NJY_F850LP", comment="nJy",
                                                        dtype=">f4", fits_dtype="E")
        self.disk_fd_f105w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F105W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f105w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F105W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f125w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F125W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f125w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F125W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")
        self.disk_fd_f160w = self.set_column_properties(
                                                   "SHE_GALPOP_FLUX_DISK_NJY_F160W", comment="nJy",
                                                   dtype=">f4", fits_dtype="E")
        self.disk_fd_f160w_err = self.set_column_properties(
                                                       "SHE_GALPOP_FLUX_ERR_DISK_NJY_F160W", comment="nJy",
                                                       dtype=">f4", fits_dtype="E")

        self._finalize_init()


# Define an instance of this object that can be imported
galaxy_population_table_format = SheGalaxyPopulationPriorsFormat()

# And a convient alias for it
tf = galaxy_population_table_format


def make_galaxy_population_table_header(cnd_field=None,
                                        telescope=None,
                                        detector=None,
                                        date_hst=None,
                                        data_version=None,
                                        date_candels=None,
                                        data_release=None):
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def
    header[tf.m.cnd_field] = cnd_field
    header[tf.m.telescope] = telescope
    header[tf.m.detector] = detector
    header[tf.m.date_hst] = date_hst
    header[tf.m.data_version] = data_version
    header[tf.m.date_candels] = date_candels
    header[tf.m.data_release] = data_release
    return header


def initialise_galaxy_population_priors_table(size=None,
                                              optional_columns=None,
                                              init_cols=None,
                                              cnd_field=None,
                                              telescope=None,
                                              detector=None,
                                              date_hst=None,
                                              data_version=None,
                                              date_candels=None,
                                              data_release=None):
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

    galaxy_population_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    galaxy_population_table.meta = make_galaxy_population_table_header(
        cnd_field=cnd_field, telescope=telescope, detector=detector,
        date_hst=date_hst, data_version=data_version, date_candels=date_candels,
        data_release=data_release)

    assert is_in_format(galaxy_population_table, tf, verbose=True)

    return galaxy_population_table
