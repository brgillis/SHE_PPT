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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from collections import OrderedDict

from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import hash_any
from astropy.table import Table


class GalaxyPopulationTableMeta(object):
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = "0.1.0"
        self.table_format = "she.galpopTable"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                   ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())

class GalaxyPopulationTableFormat(object):
    """
        @brief A class defining the format for galaxy population priors tables. Only the galaxy_population_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = GalaxyPopulationTableMeta()

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

        # Column names and info

        self.ID = set_column_properties("ID", dtype = ">i8", fits_dtype = "K")

        self.ra = set_column_properties("RA", comment = "deg")
        self.dec = set_column_properties("DEC", comment = "deg")

        self.zp = set_column_properties("Z_PHOT")
        self.zs = set_column_properties("Z_SPEC")

        self.bulge_sersic_index = set_column_properties("SI_BULGE")
        self.full_sersic_index = set_column_properties("SI_FULL")

        self.two_component_chi2 = set_column_properties("CHI2_1C")
        self.one_component_chi2 = set_column_properties("CHI2_2C")

        self.two_component_dof = set_column_properties("DOF_1C")
        self.two_component_dof = set_column_properties("DOF_2C")

        self.bulge_hlr = set_column_properties("HLR_BULGE", comment = "arcsec")
        self.disk_length = set_column_properties("RS_DISK", comment = "arcsec")

        self.x = set_column_properties("X_IMAGE", comment = "pixel")
        self.y = set_column_properties("Y_IMAGE", comment = "pixel")

        self.tilt = set_column_properties("INC_ANGLE", comment = "radians")
        self.rotation = set_column_properties("POS_ANGLE", comment = "radians")

        self.e1 = set_column_properties("E1", is_optional = True)
        self.e2 = set_column_properties("E2", is_optional = True)

        self.bulge_fd_B = set_column_properties("BULGE_FLUXDENS_B", comment = "nJy")
        self.bulge_fd_B_err = set_column_properties("BULGE_FLUXDENS_B_ERR", comment = "nJy")
        self.bulge_fd_V = set_column_properties("BULGE_FLUXDENS_V", comment = "nJy")
        self.bulge_fd_V_err = set_column_properties("BULGE_FLUXDENS_V_ERR", comment = "nJy")
        self.bulge_fd_I = set_column_properties("BULGE_FLUXDENS_I", comment = "nJy")
        self.bulge_fd_I_err = set_column_properties("BULGE_FLUXDENS_I_ERR", comment = "nJy")
        self.bulge_fd_Z = set_column_properties("BULGE_FLUXDENS_Z", comment = "nJy")
        self.bulge_fd_Z_err = set_column_properties("BULGE_FLUXDENS_Z_ERR", comment = "nJy")
        self.bulge_fd_Y = set_column_properties("BULGE_FLUXDENS_Y", comment = "nJy")
        self.bulge_fd_Y_err = set_column_properties("BULGE_FLUXDENS_Y_ERR", comment = "nJy")
        self.bulge_fd_J = set_column_properties("BULGE_FLUXDENS_J", comment = "nJy")
        self.bulge_fd_J_err = set_column_properties("BULGE_FLUXDENS_J_ERR", comment = "nJy")
        self.bulge_fd_H = set_column_properties("BULGE_FLUXDENS_H", comment = "nJy")
        self.bulge_fd_H_err = set_column_properties("BULGE_FLUXDENS_H_ERR", comment = "nJy")

        self.disk_fd_B = set_column_properties("DISK_FLUXDENS_B", comment = "nJy")
        self.disk_fd_B_err = set_column_properties("DISK_FLUXDENS_B_ERR", comment = "nJy")
        self.disk_fd_V = set_column_properties("DISK_FLUXDENS_V", comment = "nJy")
        self.disk_fd_V_err = set_column_properties("DISK_FLUXDENS_V_ERR", comment = "nJy")
        self.disk_fd_I = set_column_properties("DISK_FLUXDENS_I", comment = "nJy")
        self.disk_fd_I_err = set_column_properties("DISK_FLUXDENS_I_ERR", comment = "nJy")
        self.disk_fd_Z = set_column_properties("DISK_FLUXDENS_Z", comment = "nJy")
        self.disk_fd_Z_err = set_column_properties("DISK_FLUXDENS_Z_ERR", comment = "nJy")
        self.disk_fd_Y = set_column_properties("DISK_FLUXDENS_Y", comment = "nJy")
        self.disk_fd_Y_err = set_column_properties("DISK_FLUXDENS_Y_ERR", comment = "nJy")
        self.disk_fd_J = set_column_properties("DISK_FLUXDENS_J", comment = "nJy")
        self.disk_fd_J_err = set_column_properties("DISK_FLUXDENS_J_ERR", comment = "nJy")
        self.disk_fd_H = set_column_properties("DISK_FLUXDENS_H", comment = "nJy")
        self.disk_fd_H_err = set_column_properties("DISK_FLUXDENS_H_ERR", comment = "nJy")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported
galaxy_population_table_format = GalaxyPopulationTableFormat()

# And a convient alias for it
tf = galaxy_population_table_format


def make_galaxy_population_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    return header

def initialise_galaxy_population_table(optional_columns = None):
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

    galaxy_population_table = Table(init_cols, names = names, dtype = dtypes)

    galaxy_population_table.meta = make_galaxy_population_table_header()

    assert(is_in_format(galaxy_population_table, tf))

    return galaxy_population_table
