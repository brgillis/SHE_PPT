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

__updated__ = "2021-08-12"

from collections import OrderedDict


from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL
from ..table_utility import SheTableFormat, SheTableMeta


fits_version = "8.0"
fits_def = "she.galaxyPopulationPriors"


class SheGalaxyPopulationPriorsMeta(SheTableMeta):
    """
        @brief A class defining the metadata for PSF tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    cnd_field: str = "CNDFIELD"
    telescope: str = "TSCOPE"
    detector: str = "DETECTOR"
    date_hst: str = "DATE_HST"
    data_version: str = "DATA_VER"
    date_candels: str = "DATE_CND"
    data_release: str = "DATA_REL"


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
