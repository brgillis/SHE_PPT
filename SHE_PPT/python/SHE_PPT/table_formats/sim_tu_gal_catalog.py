#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
:file: python/SHE_PPT/table_formats/sim_tu_gal_catalog.py

:date: 29/07/22
:author: Gordon Gibb

"""

from SHE_PPT.table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format


fits_version = "0.1"
fits_def = "sim.tuGalaxyCatalog"


class SimTuGalaxyCatalogMeta(SheTableMeta):

    """
    Class that defines the TU Galaxy catalog metadata
    """

    __version__ = fits_version
    table_format = fits_def

    def init_meta(self, **kwargs):
        return super().init_meta(**kwargs)


class SimTuGalaxyCatalogFormat(SheTableFormat):
    """
    class defining the TU galaxy catalogue table format
    """

    meta_type = SimTuGalaxyCatalogMeta

    def __init__(self):
        super().__init__()

        self.SOURCE_ID = self.set_column_properties(name="SOURCE_ID", dtype=">i8")
        self.HALO_ID = self.set_column_properties(name="HALO_ID", dtype=">i8")
        self.KIND = self.set_column_properties(name="KIND", dtype=">i2")

        self.RA = self.set_column_properties(name="RA", dtype=">f8")
        self.DEC = self.set_column_properties(name="DEC", dtype=">f8")
        self.RA_MAG = self.set_column_properties(name="RA_MAG", dtype=">f8")
        self.DEC_MAG = self.set_column_properties(name="DEC_MAG", dtype=">f8")

        self.Z_OBS = self.set_column_properties(name="Z_OBS", dtype=">f4")

        self.REF_MAG_ABS = self.set_column_properties(name="REF_MAG_ABS", dtype=">f4")
        self.REF_MAG = self.set_column_properties(name="REF_MAG", dtype=">f4")

        self.BULGE_FRACTION = self.set_column_properties(name="BULGE_FRACTION", dtype=">f4")
        self.BULGE_R50 = self.set_column_properties(name="BULGE_R50", dtype=">f4")
        self.DISK_R50 = self.set_column_properties(name="DISK_R50", dtype=">f4")
        self.BULGE_NSERSIC = self.set_column_properties(name="BULGE_NSERSIC", dtype=">f4")
        self.BULGE_AXIS_RATIO = self.set_column_properties(name="BULGE_AXIS_RATIO", dtype=">f4")
        self.INCLINATION_ANGLE = self.set_column_properties(name="INCLINATION_ANGLE", dtype=">f4")
        self.DISK_ANGLE = self.set_column_properties(name="DISK_ANGLE", dtype=">f4")

        self.KAPPA = self.set_column_properties(name="KAPPA", dtype=">f4")
        self.GAMMA1 = self.set_column_properties(name="GAMMA1", dtype=">f4")
        self.GAMMA2 = self.set_column_properties(name="GAMMA2", dtype=">f4")

        # flagship 2 params for for first and second components
        self.SED_TEMPLATE_1 = self.set_column_properties(name="SED_TEMPLATE_1", dtype=">f4")
        self.EXT_LAW_1 = self.set_column_properties(name="EXT_LAW_1", dtype=">i2")
        self.EBV_1 = self.set_column_properties(name="EBV_1", dtype=">f4")
        self.SED_FRACTION_1 = self.set_column_properties(name="SED_FRACTION_1", dtype=">f4")
        self.SED_TEMPLATE_2 = self.set_column_properties(name="SED_TEMPLATE_2", dtype=">f4")
        self.EXT_LAW_2 = self.set_column_properties(name="EXT_LAW_2", dtype=">i2")
        self.EBV_2 = self.set_column_properties(name="EBV_2", dtype=">f4")

        self.HALPHA_LOGFLAM_EXT_MAG = self.set_column_properties(name="HALPHA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.HBETA_LOGFLAM_EXT_MAG = self.set_column_properties(name="HBETA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.HGAMMA_LOGFLAM_EXT_MAG = self.set_column_properties(name="HGAMMA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.HDELTA_LOGFLAM_EXT_MAG = self.set_column_properties(name="HDELTA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.HEPSILON_LOGFLAM_EXT_MAG = self.set_column_properties(name="HEPSILON_LOGFLAM_EXT_MAG", dtype=">f4")
        self.PBETA_LOGFLAM_EXT_MAG = self.set_column_properties(name="PBETA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.PGAMMA_LOGFLAM_EXT_MAG = self.set_column_properties(name="PGAMMA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.PDELTA_LOGFLAM_EXT_MAG = self.set_column_properties(name="PDELTA_LOGFLAM_EXT_MAG", dtype=">f4")
        self.PEPSILON_LOGFLAM_EXT_MAG = self.set_column_properties(name="PEPSILON_LOGFLAM_EXT_MAG", dtype=">f4")

        self.O2_LOGFLAM_EXT_MAG = self.set_column_properties(name="O2_LOGFLAM_EXT_MAG", dtype=">f4")
        self.O3_LOGFLAM_EXT_MAG = self.set_column_properties(name="O3_LOGFLAM_EXT_MAG", dtype=">f4")
        self.N2_LOGFLAM_EXT_MAG = self.set_column_properties(name="N2_LOGFLAM_EXT_MAG", dtype=">f4")
        self.S2_LOGFLAM_EXT_MAG = self.set_column_properties(name="S2_LOGFLAM_EXT_MAG", dtype=">f4")
        self.S3_LOGFLAM_EXT_MAG = self.set_column_properties(name="S3_LOGFLAM_EXT_MAG", dtype=">f4")

        self.AV = self.set_column_properties(name="AV", dtype=">f4")

        self.TU_FNU_VIS_MAG = self.set_column_properties(name="TU_FNU_VIS_MAG", dtype=">f4")

        self.TU_FNU_Y_NISP_MAG = self.set_column_properties(name="TU_FNU_Y_NISP_MAG", dtype=">f4")
        self.TU_FNU_J_NISP_MAG = self.set_column_properties(name="TU_FNU_J_NISP_MAG", dtype=">f4")
        self.TU_FNU_H_NISP_MAG = self.set_column_properties(name="TU_FNU_H_NISP_MAG", dtype=">f4")

        self.TU_FNU_G_DECAM_MAG = self.set_column_properties(name="TU_FNU_G_DECAM_MAG", dtype=">f4")
        self.TU_FNU_R_DECAM_MAG = self.set_column_properties(name="TU_FNU_R_DECAM_MAG", dtype=">f4")
        self.TU_FNU_I_DECAM_MAG = self.set_column_properties(name="TU_FNU_I_DECAM_MAG", dtype=">f4")
        self.TU_FNU_Z_DECAM_MAG = self.set_column_properties(name="TU_FNU_Z_DECAM_MAG", dtype=">f4")

        self.TU_FNU_U_MEGACAM_MAG = self.set_column_properties(name="TU_FNU_U_MEGACAM_MAG", dtype=">f4")
        self.TU_FNU_R_MEGACAM_MAG = self.set_column_properties(name="TU_FNU_R_MEGACAM_MAG", dtype=">f4")

        self.TU_FNU_G_JPCAM_MAG = self.set_column_properties(name="TU_FNU_G_JPCAM_MAG", dtype=">f4")

        self.TU_FNU_I_PANSTARRS_MAG = self.set_column_properties(name="TU_FNU_I_PANSTARRS_MAG", dtype=">f4")
        self.TU_FNU_Z_PANSTARRS_MAG = self.set_column_properties(name="TU_FNU_Z_PANSTARRS_MAG", dtype=">f4")

        self.TU_FNU_G_HSC_MAG = self.set_column_properties(name="TU_FNU_G_HSC_MAG", dtype=">f4")
        self.TU_FNU_Z_HSC_MAG = self.set_column_properties(name="TU_FNU_Z_HSC_MAG", dtype=">f4")

        self.TU_FNU_G_GAIA_MAG = self.set_column_properties(name="TU_FNU_G_GAIA_MAG", dtype=">f4")
        self.TU_FNU_BP_GAIA_MAG = self.set_column_properties(name="TU_FNU_BP_GAIA_MAG", dtype=">f4")
        self.TU_FNU_RP_GAIA_MAG = self.set_column_properties(name="TU_FNU_RP_GAIA_MAG", dtype=">f4")

        self.TU_FNU_U_LSST_MAG = self.set_column_properties(name="TU_FNU_U_LSST_MAG", dtype=">f4")
        self.TU_FNU_G_LSST_MAG = self.set_column_properties(name="TU_FNU_G_LSST_MAG", dtype=">f4")
        self.TU_FNU_R_LSST_MAG = self.set_column_properties(name="TU_FNU_R_LSST_MAG", dtype=">f4")
        self.TU_FNU_I_LSST_MAG = self.set_column_properties(name="TU_FNU_I_LSST_MAG", dtype=">f4")
        self.TU_FNU_Z_LSST_MAG = self.set_column_properties(name="TU_FNU_Z_LSST_MAG", dtype=">f4")
        self.TU_FNU_Y_LSST_MAG = self.set_column_properties(name="TU_FNU_Y_LSST_MAG", dtype=">f4")

        self.TU_FNU_J_2MASS_MAG = self.set_column_properties(name="TU_FNU_J_2MASS_MAG", dtype=">f4")
        self.TU_FNU_H_2MASS_MAG = self.set_column_properties(name="TU_FNU_H_2MASS_MAG", dtype=">f4")
        self.TU_FNU_KS_2MASS_MAG = self.set_column_properties(name="TU_FNU_KS_2MASS_MAG", dtype=">f4")

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """Bound alias to the free table initialisation function, using this table format."""

        return initialise_sim_tu_galaxy_catalog(*args, **kwargs)


# Define an instance of this object that can be imported
sim_tu_galaxy_catalog_format = SimTuGalaxyCatalogFormat()

# And a convenient alias for it
tf = sim_tu_galaxy_catalog_format


def initialise_sim_tu_galaxy_catalog(size=None, optional_columns=None, init_cols=None):
    """
    Initialise a Sim tu galaxy catalog table
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    t = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    t.meta = tf.m.init_meta()

    assert is_in_format(t, tf)

    return t
