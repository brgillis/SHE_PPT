""" @mer_final_catalog.py

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
fits_def = "phz.physicalParametersCatalog"

logger = getLogger(__name__)


phys_param_list1 = ['Z', 'LOG_STELLARMASS', 'LOG_MASS', 'SFR']
phys_param_list2 = [ 'STELLAR_AGE','A_V', 'DUST_LAW_SLOPE', 'DUST_LAW_WIDTH', 'DUST_LAW_HEIGHT',
                    'STELLAR_MET','GAS_MET']
phys_param_list2+= ['MAGABS_'+band for band in [
                    'FUV','NUV','U_JKC','B_JKC','V_JKC','R','VIS_EUCLID',
                    'I_JKC','Z','Y_EUCLID','J_EUCLID','H_EUCLID','Ks']]
phys_param_list2+= ['LUMFRAC','AGN_EBV','AGN_LBOL']

class PhzPhysicalParametersCatalogMeta(SheTableMeta):
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


class PhzPhysicalParametersCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for detections tables. Only the mer_final_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """

    # Explicitly specify some of the columns we use from this table to suppress spurious IDE errors
    ID: str
    

    def __init__(self):
        super().__init__(PhzPhysicalParametersCatalogMeta())

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
        # PHYS PARAM_FLAGS
        setattr(self, "phys_param_flags", self.set_column_properties("PHYS_PARAM_FLAGS", fits_dtype = "K", dtype = ">i8", comment = "",
                                                       is_optional = False))
        
        for nn_param in ['ID','WEIGHT','SCALE']:
            col_name = 'PHZ_PDF_NN_%s' % nn_param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False, length=100))
        
        # PHZ MEDIAN
        setattr(self, "qual_flag", self.set_column_properties("QUALITY_FLAG", fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
         
        
        # PHZ_FLAGS
        setattr(self, "galaxy_class", self.set_column_properties("GALAXY_CLASS", fits_dtype = "K", dtype = ">i8", comment = "",
                                                       is_optional = False))
        
        
        # @TODO: replace with a for loop....
        for param in phys_param_list1:
            # FLUX_U_EXT_LSST_TOTAL_UNIF" unit="uJy" format="E" />
            col_name = "PHZ_PP_MEDIAN_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
            col_name = "PHZ_PP_MODE_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
            col_name = "PHZ_PP_68_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
        setattr(self, "PHZ_PP_SFH_TYPE", self.set_column_properties("PHZ_PP_SFH_TYPE", fits_dtype = "K", dtype = ">i8", comment = "",
                                                       is_optional = False))
        
        setattr(self, "PHZ_PP_SFH_TAU", self.set_column_properties("PHZ_PP_SFH_TAU", fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
        for param in phys_param_list2:
            # FLUX_U_EXT_LSST_TOTAL_UNIF" unit="uJy" format="E" />
            col_name = "PHZ_PP_MEDIAN_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
            col_name = "PHZ_PP_MODE_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
            col_name = "PHZ_PP_68_%s" % param
            setattr(self, col_name, self.set_column_properties(col_name, fits_dtype = "E", dtype = ">f4", comment = "",
                                                       is_optional = False))
        
          
        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_phz_physical_parameters_catalog(*args, **kwargs)


# Define an instance of this object that can be imported
phz_physical_parameters_catalog_format = PhzPhysicalParametersCatalogFormat()

# And a convenient alias for it
tf = phz_physical_parameters_catalog_format


def initialise_phz_physical_parameters_catalog(image_group_phl = None,
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

        @return phz_physical_parameters_catalog <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    phz_physical_parameters_catalog = init_table(tf, optional_columns = optional_columns, init_cols = init_cols, size = size)

    phz_physical_parameters_catalog.meta = tf.m.init_meta()

    assert is_in_format(phz_physical_parameters_catalog, tf)

    return phz_physical_parameters_catalog
