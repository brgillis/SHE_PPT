""" @phz_sed_catalog.py

    Created 22 Aug 2017

    Format definition for detections table.
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

__updated__ = "2021-11-18"

from ..constants.fits import EXTNAME_LABEL, FITS_DEF_LABEL, FITS_VERSION_LABEL
from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format

fits_version = "0.9"
fits_def = "phz.sedCatalog"

logger = getLogger(__name__)


int_band_list = [427,464,484,505,527,574,624,679,709,738,767,827]


class PhzSedCatalogMeta(SheTableMeta):
    """
        @brief A class defining the metadata for detections tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    extname: str = EXTNAME_LABEL
    tileid: str = "TILEID"
    objsel: str = "OBJSEL"

    def init_meta(self, **kwargs: str):
        return super().init_meta(extname = "N/A",
                                 **kwargs)


class PhzSedCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for detections tables. Only the mer_final_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """

    # Explicitly specify some of the columns we use from this table to suppress spurious IDE errors
    ID: str
    

    def __init__(self):
        super().__init__(PhzSedCatalogMeta())

        # To keep this up to date, copy from https://gitlab.euclid-sgs.uk/PF-MER/MER_CatalogAssembly/blob/develop
        # /MER_CatalogAssembly/python/MER_CatalogAssembly/dm_template.py,
        # then replace the regex columns\.append\(fits\.Column\(name='([%0-9A-Za-z_]+)'(%filt)?, format='([
        # 0-9A-Z]+)'(?:, unit='([A-Za-z/0-9]+)')?.*\)
        # with setattr(self, "$1"$2, set_column_properties(self, "$1"$2, fits_dtype="$3", comment="$4",
        # is_optional=False))
        # Then finally go in and fix length for arrays, special names we want to keep, and datatypes that aren't 'E'

        # Column names and info

        # Euclid unique source identifier
        setattr(self, "ID", self.set_column_properties("OBJECT_ID", fits_dtype = "K", dtype = ">i8", comment = "",
                                                       is_optional = False))
        
        for int_band in int_band_list:
            col_name = "FLUX_IA%d" % int_band
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
            col_name = "ERR_IA%d" % int_band
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
        # PHZ_FLAGS
        setattr(self, "phz_flags", self.set_column_properties("PHZ_FLAGS", fits_dtype = "K", dtype = ">i8", comment = "",
                                                       is_optional = False))
        

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_phz_sed_catalog(*args, **kwargs)


# Define an instance of this object that can be imported
phz_sed_catalog_format = PhzSedCatalogFormat()

# And a convenient alias for it
tf = phz_sed_catalog_format


def initialise_phz_sed_catalog(image_group_phl = None,
                                 options = None,
                                 size = None,
                                 optional_columns = None,
                                 init_cols = None,
                                 model_hash = None,
                                 model_seed = None,
                                 noise_seed = None):
    """
        @brief Initialise a detections table.

        @param image_group_phl <SHE_SIM.ImageGroup>

        @param options <dict> Options dictionary

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is none

        @return phz_sed_catalog <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    phz_sed_catalog = init_table(tf, optional_columns=optional_columns, 
                                 init_cols=init_cols, size=size)

    phz_sed_catalog.meta = tf.m.init_meta()

    assert is_in_format(phz_sed_catalog, tf)

    return phz_sed_catalog
