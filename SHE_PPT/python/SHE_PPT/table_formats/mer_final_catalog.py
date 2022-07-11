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

__updated__ = "2021-08-26"

from ..constants.fits import EXTNAME_LABEL, FITS_DEF_LABEL, FITS_VERSION_LABEL
from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format

fits_version = "0.3"
fits_def = "mer.finalCatalog"

logger = getLogger(__name__)

filter_list_ext = ['G_EXT_DECAM', 'R_EXT_DECAM', 'I_EXT_DECAM', 'Z_EXT_DECAM',
                   'U_EXT_OMEGACAM', 'G_EXT_OMEGACAM', 'R_EXT_OMEGACAM', 'I_EXT_OMEGACAM',
                   'U_EXT_LSST', 'G_EXT_LSST', 'R_EXT_LSST', 'I_EXT_LSST', 'Z_EXT_LSST',
                   'U_EXT_MEGACAM', 'R_EXT_MEGACAM',
                   'G_EXT_JPCAM',
                   'I_EXT_PANSTARRS', 'Z_EXT_PANSTARRS',
                   'Z_EXT_HSC']

filter_list = ['VIS', 'Y', 'J', 'H']


class MerFinalCatalogMeta(SheTableMeta):
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


class MerFinalCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for detections tables. Only the mer_final_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """

    # Explicitly specify some of the columns we use from this table to suppress spurious IDE errors
    ID: str
    gal_x_world: str
    gal_y_world: str
    seg_ID: str
    vis_det: str
    FLUX_VIS_APER: str
    FLUXERR_VIS_APER: str
    FLUX_NISP_APER: str
    SHE_FLAG: str
    SEGMENTATION_AREA: str
    snr: str
    bg: str
    colour: str
    size: str
    epoch: str
    meta_type = MerFinalCatalogMeta

    def __init__(self):
        super().__init__()

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
        # Source barycenter RA coordinate
        setattr(self, "gal_x_world", self.set_column_properties(
            "RIGHT_ASCENSION", dtype = ">f8",
            fits_dtype = "D", comment = "deg", is_optional = False))
        # Source barycenter DEC coordinate
        setattr(self, "gal_y_world", self.set_column_properties("DECLINATION",
                                                                dtype = ">f8", fits_dtype = "D", comment = "deg",
                                                                is_optional = False))
        # Source ID in the associated segmentation map
        setattr(self, "seg_ID", self.set_column_properties("SEGMENTATION_MAP_ID",
                                                           dtype = ">i8", fits_dtype = "K", comment = "",
                                                           is_optional = False))
        # Flag to indicate if the source is detected in the VIS mosaic (1) or is only detected in the NIR mosaic (0)
        setattr(self, "vis_det", self.set_column_properties(
            "VIS_DET", dtype = ">i2", fits_dtype = "I",
            comment = "", is_optional = False))

        # Aperture fotometry on EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLUX_%s_APER" % filt, self.set_column_properties("FLUX_%s_APER" %
                                                                            filt, fits_dtype = "E", comment = "uJy",
                                                                            is_optional = False))
        # Aperture photometry error on EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLUXERR_%s_APER" % filt, self.set_column_properties("FLUXERR_%s_APER" %
                                                                               filt, fits_dtype = "E", comment = "uJy",
                                                                               is_optional = False))
        # Aperture photometry on NIR stack
        setattr(self, "FLUX_NIR_STACK_APER", self.set_column_properties(
            "FLUX_NIR_STACK_APER", fits_dtype = "E", comment = "uJy", is_optional = False))
        # Aperture photometry error on NIR stack
        setattr(self, "FLUXERR_NIR_STACK_APER", self.set_column_properties(
            "FLUXERR_NIR_STACK_APER", fits_dtype = "E", comment = "uJy", is_optional = False))
        # Fitting photometry (TPHOT) on EXT+VIS+NIR bands
        for filt in filter_list_ext + [f for f in filter_list if f != 'VIS']:
            setattr(self, "FLUX_%s_TOTAL" % filt, self.set_column_properties("FLUX_%s_TOTAL" %
                                                                             filt, fits_dtype = "E", comment = "uJy",
                                                                             is_optional = False))
        # Fitting photometry error (TPHOT) on EXTEXT+VIS+NIR bands
        for filt in filter_list_ext + [f for f in filter_list if f != 'VIS']:
            setattr(self, "FLUXERR_%s_TOTAL" % filt, self.set_column_properties(
                "FLUXERR_%s_TOTAL" % filt, fits_dtype = "E", comment = "uJy", is_optional = False))
        # psf fitting photometry on VIS
        setattr(self, "FLUX_VIS_PSF", self.set_column_properties(
            "FLUX_VIS_PSF", fits_dtype = "E", comment = "uJy", is_optional = False))
        # psf fitting photometry on VIS
        setattr(self, "FLUXERR_VIS_PSF", self.set_column_properties(
            "FLUXERR_VIS_PSF", fits_dtype = "E", comment = "uJy", is_optional = False))
        # ISOAREA flux
        setattr(self, "FLUX_SEGMENTATION", self.set_column_properties(
            "FLUX_SEGMENTATION", fits_dtype = "E", comment = "uJy", is_optional = False))
        # ISOAREA fluxerr
        setattr(self, "FLUXERR_SEGMENTATION", self.set_column_properties(
            "FLUXERR_SEGMENTATION", fits_dtype = "E", comment = "uJy", is_optional = False))
        # det fitting photometry on VIS
        setattr(self, "FLUX_DETECTION_TOTAL", self.set_column_properties(
            "FLUX_DETECTION_TOTAL", fits_dtype = "E", comment = "uJy", is_optional = False))
        # det fitting photometry on VIS
        setattr(self, "FLUXERR_DETECTION_TOTAL", self.set_column_properties(
            "FLUXERR_DETECTION_TOTAL", fits_dtype = "E", comment = "uJy", is_optional = False))
        # Object flag for EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLAG_%s" % filt, self.set_column_properties("FLAG_%s" %
                                                                       filt, dtype = ">i4", fits_dtype = "J",
                                                                       comment = "", is_optional = False))
        # Object flag for NIR stack
        setattr(self, "FLAG_NIR_STACK", self.set_column_properties(
            "FLAG_NIR_STACK", dtype = ">i4", fits_dtype = "J", comment = "", is_optional = False))
        # Average filter transmission curve wavelength of EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "AVG_TRANS_WAVE_%s" % filt, self.set_column_properties("AVG_TRANS_WAVE_%s" %
                                                                                 filt, fits_dtype = "E",
                                                                                 comment = "Angstrom",
                                                                                 is_optional = False))
        # Deblending flag
        setattr(self, "DEBLENDED_FLAG", self.set_column_properties(
            "DEBLENDED_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Blended associations
        setattr(self, "DEBLENDED_COMPANIONS", self.set_column_properties(
            "DEBLENDED_COMPANIONS", dtype = ">i8", length = 5, fits_dtype = "5K", comment = "", is_optional = False))
        # Blending probability
        setattr(self, "BLENDED_PROB", self.set_column_properties(
            "BLENDED_PROB", fits_dtype = "E", comment = "", is_optional = False))
        # Flag for objects SHE wants to remove
        setattr(self, "SHE_FLAG", self.set_column_properties("SHE_FLAG",
                                                             dtype = ">i2", fits_dtype = "I", comment = "",
                                                             is_optional = False))
        # Variability flag
        setattr(self, "VARIABLE_FLAG", self.set_column_properties(
            "VARIABLE_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Binary star flag
        setattr(self, "BINARY_FLAG", self.set_column_properties(
            "BINARY_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Point-like flag
        setattr(self, "POINT_LIKE_FLAG", self.set_column_properties(
            "POINT_LIKE_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Point-like probability
        setattr(self, "POINT_LIKE_PROB", self.set_column_properties(
            "POINT_LIKE_PROB", fits_dtype = "E", comment = "", is_optional = False))
        # Extended flag
        setattr(self, "EXTENDED_FLAG", self.set_column_properties(
            "EXTENDED_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Extended prob
        setattr(self, "EXTENDED_PROB", self.set_column_properties(
            "EXTENDED_PROB", fits_dtype = "E", comment = "", is_optional = False))
        # Spurious flag
        setattr(self, "SPURIOUS_FLAG", self.set_column_properties(
            "SPURIOUS_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # Spurious prob
        setattr(self, "SPURIOUS_PROB", self.set_column_properties(
            "SPURIOUS_PROB", fits_dtype = "E", comment = "", is_optional = False))
        # Magnitude used to compute the star probability (old MAG_AUTO)
        setattr(self, "MAG_STARGAL_SEP", self.set_column_properties(
            "MAG_STARGAL_SEP", fits_dtype = "E", comment = "mag", is_optional = False))
        # Possible corruption of MAG_STARGAL_SEP flags
        setattr(self, "DET_QUALITY_FLAG", self.set_column_properties(
            "DET_QUALITY_FLAG", dtype = ">i2", fits_dtype = "I", comment = "", is_optional = False))
        # MU_MAX values
        setattr(self, "MU_MAX", self.set_column_properties("MU_MAX",
                                                           fits_dtype = "E", comment = "mag/arcsec2",
                                                           is_optional = False))
        # MU_MAX - MAG values
        setattr(self, "MUMAX_MINUS_MAG", self.set_column_properties(
            "MUMAX_MINUS_MAG", fits_dtype = "E", comment = "mag/arcsec2", is_optional = False))
        # Isophotal area
        setattr(self, "SEGMENTATION_AREA", self.set_column_properties(
            "SEGMENTATION_AREA", dtype = ">i4", fits_dtype = "J", comment = "pix", is_optional = False))
        # Semimajor axis
        setattr(self, "A_IMAGE", self.set_column_properties("A_IMAGE", fits_dtype = "E", comment = "pix",
                                                            is_optional = False))
        # Position angle
        setattr(self, "POSITION_ANGLE", self.set_column_properties(
            "POSITION_ANGLE", fits_dtype = "E", comment = "deg", is_optional = False))
        # Ellipticity
        setattr(self, "ELLIPTICITY", self.set_column_properties(
            "ELLIPTICITY", fits_dtype = "E", comment = "", is_optional = False))
        # Concentration
        setattr(self, "CONCENTRATION", self.set_column_properties(
            "CONCENTRATION", fits_dtype = "E", comment = "", is_optional = False))
        # Asymmetry
        setattr(self, "ASYMMETRY", self.set_column_properties(
            "ASYMMETRY", fits_dtype = "E", comment = "", is_optional = False))
        # Smoothness
        setattr(self, "SMOOTHNESS", self.set_column_properties(
            "SMOOTHNESS", fits_dtype = "E", comment = "", is_optional = False))
        # Gini
        setattr(self, "GINI", self.set_column_properties("GINI", fits_dtype = "E", comment = "", is_optional = False))
        # Moment_20
        setattr(self, "MOMENT_20", self.set_column_properties(
            "MOMENT_20", fits_dtype = "E", comment = "", is_optional = False))
        # Isoarea error
        setattr(self, "A_IMAGE_ERR", self.set_column_properties(
            "A_IMAGE_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Position angle error
        setattr(self, "POSITION_ANGLE_ERR", self.set_column_properties(
            "POSITION_ANGLE_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Ellipticity error
        setattr(self, "ELLIPTICITY_ERR", self.set_column_properties(
            "ELLIPTICITY_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Concentration error
        setattr(self, "CONCENTRATION_ERR", self.set_column_properties(
            "CONCENTRATION_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Asymmetry error
        setattr(self, "ASYMMETRY_ERR", self.set_column_properties(
            "ASYMMETRY_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Smoothness error
        setattr(self, "SMOOTHNESS_ERR", self.set_column_properties(
            "SMOOTHNESS_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Gini error
        setattr(self, "GINI_ERR", self.set_column_properties("GINI_ERR", fits_dtype = "E", comment = "",
                                                             is_optional = False))
        # Moment_20 error
        setattr(self, "MOMENT_20_ERR", self.set_column_properties(
            "MOMENT_20_ERR", fits_dtype = "E", comment = "", is_optional = False))
        # Galactic E(V-B)
        setattr(self, "GAL_EBV", self.set_column_properties("GAL_EBV", fits_dtype = "E", comment = "mag",
                                                            is_optional = False))
        # Galactic E(V-B) error
        setattr(self, "GAL_EBV_ERR", self.set_column_properties(
            "GAL_EBV_ERR", fits_dtype = "E", comment = "mag", is_optional = False))

        # Optional columns

        # Group ID (for potential blends)
        setattr(self, "GROUP_ID", self.set_column_properties(
            "GROUP_ID", fits_dtype = "K", dtype = ">i8", comment = "", is_optional = True))

        for bin_parameter in ("snr", "bg", "colour", "size", "epoch",):
            setattr(self, bin_parameter, self.set_column_properties(
                bin_parameter.upper(), is_optional = True, ))

        # Tile ID
        setattr(self, "tile_ID", self.set_column_properties("TILE_ID", dtype = ">i8", fits_dtype = "K",
                                                            comment = "", is_optional = True))

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_mer_final_catalog(*args, **kwargs)


# Define an instance of this object that can be imported
mer_final_catalog_format = MerFinalCatalogFormat()

# And a convenient alias for it
tf = mer_final_catalog_format


def initialise_mer_final_catalog(image_group_phl = None,
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

        @return mer_final_catalog <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    mer_final_catalog = init_table(tf, optional_columns = optional_columns, init_cols = init_cols, size = size)

    mer_final_catalog.meta = tf.m.init_meta()

    assert is_in_format(mer_final_catalog, tf)

    return mer_final_catalog
