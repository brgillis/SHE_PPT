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

__updated__ = "2020-07-19"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format, setup_table_format, set_column_properties, init_table
from SHE_PPT.utility import hash_any

fits_version = "0.3"
fits_def = "mer.finalCatalog"

logger = getLogger(mv.logger_name)


class MerFinalCatalogMeta(object):
    """
        @brief A class defining the metadata for detections tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label
        self.extname = mv.extname_label

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class MerFinalCatalogFormat(object):
    """
        @brief A class defining the format for detections tables. Only the mer_final_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = MerFinalCatalogMeta()

        setup_table_format(self)

        # To keep this up to date, copy from https://gitlab.euclid-sgs.uk/PF-MER/MER_CatalogAssembly/blob/develop/MER_CatalogAssembly/python/MER_CatalogAssembly/dm_template.py,
        # then replace the regex columns\.append\(fits\.Column\(name='([%0-9A-Za-z_]+)'(%filt)?, format='([0-9A-Z]+)'(?:, unit='([A-Za-z/0-9]+)')?.*\)
        # with setattr(self, "$1"$2, set_column_properties(self, "$1"$2, fits_dtype="$3", comment="$4", is_optional=False))
        # Then finally go in and fix length for arrays, special names we want to keep, and datatypes that aren't 'E'

        filter_list_ext = ['G_EXT_DECAM', 'R_EXT_DECAM', 'I_EXT_DECAM', 'Z_EXT_DECAM',
                           'U_EXT_OMEGACAM', 'G_EXT_OMEGACAM', 'R_EXT_OMEGACAM', 'I_EXT_OMEGACAM',
                           'U_EXT_LSST', 'G_EXT_LSST', 'R_EXT_LSST', 'I_EXT_LSST', 'Z_EXT_LSST']
        filter_list = ['VIS', 'Y', 'J', 'H']

        # Column names and info

        # Euclid unique source identifier
        setattr(self, "ID", set_column_properties(self, "OBJECT_ID", fits_dtype="K", dtype=">i8", comment="",
                                                  is_optional=False))
        # Source barycenter RA coordinate
        setattr(self, "gal_x_world", set_column_properties(self,
            "RIGHT_ASCENSION", dtype=">f8", fits_dtype="D", comment="deg", is_optional=False))
        # Source barycenter DEC coordinate
        setattr(self, "gal_y_world", set_column_properties(self, "DECLINATION",
                                                           dtype=">f8", fits_dtype="D", comment="deg",
                                                           is_optional=False))
        # Source ID in the associated segmentation map
        setattr(self, "seg_ID", set_column_properties(self, "SEGMENTATION_MAP_ID",
                                                      dtype=">i8", fits_dtype="K", comment="", is_optional=False))
        # Flag to indicate if the source is detected in the VIS mosaic (1) or is only detected in the NIR mosaic (0)
        setattr(self, "vis_det", set_column_properties(self,
            "VIS_DET", dtype=">i2", fits_dtype="I", comment="", is_optional=False))
        # Aperture fotometry on EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLUX_%s_APER" % filt, set_column_properties(self,
                "FLUX_%s_APER" % filt, fits_dtype="E", comment="uJy", is_optional=True))
        # Aperture photometry error on EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLUXERR_%s_APER" % filt, set_column_properties(self,
                "FLUXERR_%s_APER" % filt, fits_dtype="E", comment="uJy", is_optional=True))
        # Aperture photometry on NIR stack
        setattr(self, "FLUX_NIR_STACK_APER", set_column_properties(self,
            "FLUX_NIR_STACK_APER", fits_dtype="E", comment="uJy", is_optional=True))
        # Aperture photometry error on NIR stack
        setattr(self, "FLUXERR_NIR_STACK_APER", set_column_properties(self,
            "FLUXERR_NIR_STACK_APER", fits_dtype="E", comment="uJy", is_optional=True))
        # Fitting photometry (TPHOT) on EXT+VIS+NIR bands
        for filt in filter_list_ext + [f for f in filter_list if f != 'VIS']:
            setattr(self, "FLUX_%s_TOTAL" % filt, set_column_properties(self,
                "FLUX_%s_TOTAL" % filt, fits_dtype="E", comment="uJy", is_optional=True))
        # Fitting photometry error (TPHOT) on EXTEXT+VIS+NIR bands
        for filt in filter_list_ext + [f for f in filter_list if f != 'VIS']:
            setattr(self, "FLUXERR_%s_TOTAL" % filt, set_column_properties(self,
                "FLUXERR_%s_TOTAL" % filt, fits_dtype="E", comment="uJy", is_optional=True))
        # psf fitting photometry on VIS
        setattr(self, "FLUX_VIS_PSF", set_column_properties(self,
            "FLUX_VIS_PSF", fits_dtype="E", comment="uJy", is_optional=True))
        # psf fitting photometry on VIS
        setattr(self, "FLUXERR_VIS_PSF", set_column_properties(self,
            "FLUXERR_VIS_PSF", fits_dtype="E", comment="uJy", is_optional=True))
        # det fitting photometry on VIS
        setattr(self, "FLUX_DETECTION_TOTAL", set_column_properties(self,
            "FLUX_DETECTION_TOTAL", fits_dtype="E", comment="uJy", is_optional=True))
        # det fitting photometry on VIS
        setattr(self, "FLUXERR_DETECTION_TOTAL", set_column_properties(self,
            "FLUXERR_DETECTION_TOTAL", fits_dtype="E", comment="uJy", is_optional=True))
        # Object flag for EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "FLAG_%s" % filt, set_column_properties(self, "FLAG_%s" %
                                                                  filt, dtype=">i4", fits_dtype="J", comment="", is_optional=True))
        # Object flag for NIR stack
        setattr(self, "FLAG_NIR_STACK", set_column_properties(self,
            "FLAG_NIR_STACK", dtype=">i4", fits_dtype="J", comment="", is_optional=True))
        # Average filter transmission curve wavelength of EXT+VIS+NIR bands
        for filt in filter_list_ext + filter_list:
            setattr(self, "AVG_TRANS_WAVE_%s" % filt, set_column_properties(self,
                "AVG_TRANS_WAVE_%s" % filt, fits_dtype="E", comment="Angstrom", is_optional=True))
        # Deblending flag
        setattr(self, "DEBLENDING_FLAG", set_column_properties(self,
            "DEBLENDING_FLAG", dtype=">i4", fits_dtype="J", comment="", is_optional=True))
        # Blending probability
        setattr(self, "BLENDED_OBJECT_PROB", set_column_properties(self,
            "BLENDED_OBJECT_PROB", fits_dtype="E", comment="", is_optional=True))
        # Blended associations
        setattr(self, "BLENDED_ASSOCIATIONS", set_column_properties(self,
            "BLENDED_ASSOCIATIONS", dtype=">i8", length=5, fits_dtype="5K", comment="", is_optional=True))
        # Flag for objects SHE wants to remove
        setattr(self, "SHE_FLAG", set_column_properties(self,
            "SHE_FLAG", dtype=">i2", fits_dtype="I", comment="", is_optional=True))
        # Variability flag
        setattr(self, "VARIABILITY_FLAG", set_column_properties(self,
            "VARIABILITY_FLAG", dtype=">i2", fits_dtype="I", comment="", is_optional=True))
        # Binary star flag
        setattr(self, "BINARY_FLAG", set_column_properties(self,
            "BINARY_FLAG", dtype=">i2", fits_dtype="I", comment="", is_optional=True))
        # Star flag
        setattr(self, "STAR_FLAG", set_column_properties(self, "STAR_FLAG",
                                                         dtype=">i2", fits_dtype="I", comment="", is_optional=True))
        # Star probability
        setattr(self, "STAR_PROB", set_column_properties(self, "STAR_PROB", fits_dtype="E", comment="", is_optional=True))
        # Magnitude used to compute the star probability (old MAG_AUTO)
        setattr(self, "MAG_STARGAL_SEP", set_column_properties(self,
            "MAG_STARGAL_SEP", fits_dtype="E", comment="mag", is_optional=True))
        # Possible corruption of MAG_STARGAL_SEP flags
        setattr(self, "DET_QUALITY_FLAG", set_column_properties(self,
            "DET_QUALITY_FLAG", dtype=">i2", fits_dtype="I", comment="", is_optional=True))
        # Semimajo axis
        setattr(self, "A_IMAGE", set_column_properties(self, "A_IMAGE", fits_dtype="E", comment="pix", is_optional=True))
        # MU_MAX values
        setattr(self, "MU_MAX", set_column_properties(self, "MU_MAX", fits_dtype="E", comment="mag/arcsec2", is_optional=True))
        # Isophotal area
        setattr(self, "ISOAREA", set_column_properties(self,
            "ISOAREA", dtype=">i4", fits_dtype="J", comment="pix", is_optional=True))
        # Position angle
        setattr(self, "POSITION_ANGLE", set_column_properties(self,
            "POSITION_ANGLE", fits_dtype="E", comment="deg", is_optional=True))
        # Ellipticity
        setattr(self, "ELLIPTICITY", set_column_properties(self,
            "ELLIPTICITY", fits_dtype="E", comment="", is_optional=True))
        # Concentration
        setattr(self, "CONCENTRATION", set_column_properties(self,
            "CONCENTRATION", fits_dtype="E", comment="", is_optional=True))
        # Asymmetry
        setattr(self, "ASYMMETRY", set_column_properties(self, "ASYMMETRY", fits_dtype="E", comment="", is_optional=True))
        # Smoothness
        setattr(self, "SMOOTHNESS", set_column_properties(self, "SMOOTHNESS", fits_dtype="E", comment="", is_optional=True))
        # Gini
        setattr(self, "GINI", set_column_properties(self, "GINI", fits_dtype="E", comment="", is_optional=True))
        # Moment_20
        setattr(self, "MOMENT_20", set_column_properties(self, "MOMENT_20", fits_dtype="E", comment="", is_optional=True))
        # Isoarea error
        setattr(self, "A_IMAGE_ERR", set_column_properties(self,
            "A_IMAGE_ERR", fits_dtype="E", comment="", is_optional=True))
        # Isoarea error
        setattr(self, "ISOAREA_ERR", set_column_properties(self,
            "ISOAREA_ERR", dtype=">i4", fits_dtype="J", comment="", is_optional=True))
        # Position angle error
        setattr(self, "POSITION_ANGLE_ERR", set_column_properties(self,
            "POSITION_ANGLE_ERR", fits_dtype="E", comment="", is_optional=True))
        # Ellipticity error
        setattr(self, "ELLIPTICITY_ERR", set_column_properties(self,
            "ELLIPTICITY_ERR", fits_dtype="E", comment="", is_optional=True))
        # Concentration error
        setattr(self, "CONCENTRATION_ERR", set_column_properties(self,
            "CONCENTRATION_ERR", fits_dtype="E", comment="", is_optional=True))
        # Asymmetry error
        setattr(self, "ASYMMETRY_ERR", set_column_properties(self,
            "ASYMMETRY_ERR", fits_dtype="E", comment="", is_optional=True))
        # Smoothness error
        setattr(self, "SMOOTHNESS_ERR", set_column_properties(self,
            "SMOOTHNESS_ERR", fits_dtype="E", comment="", is_optional=True))
        # Gini error
        setattr(self, "GINI_ERR", set_column_properties(self, "GINI_ERR", fits_dtype="E", comment="", is_optional=True))
        # Moment_20 error
        setattr(self, "MOMENT_20_ERR", set_column_properties(self,
            "MOMENT_20_ERR", fits_dtype="E", comment="", is_optional=True))
        # Galactic E(V-B)
        setattr(self, "GAL_EBV", set_column_properties(self, "GAL_EBV", fits_dtype="E", comment="mag", is_optional=True))
        # Galactic E(V-B) error
        setattr(self, "GAL_EBV_ERR", set_column_properties(self,
            "GAL_EBV_ERR", fits_dtype="E", comment="mag", is_optional=True))

        # Half-light radius
        setattr(self, "hlr", set_column_properties(self,
            "hlr", dtype=">f4", fits_dtype="E", comment="arcsec", is_optional=True))

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
mer_final_catalog_format = MerFinalCatalogFormat()

# And a convient alias for it
tf = mer_final_catalog_format


def make_mer_final_catalog_header(model_hash=None,
                                 model_seed=None,
                                 noise_seed=None):
    """
        @brief Generate a header for a detections table.

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    return header


def initialise_mer_final_catalog(image_group_phl=None,
                                options=None,
                                size=None,
                                 optional_columns=None,
                                 init_cols=None,
                                model_hash=None,
                                model_seed=None,
                                noise_seed=None,
                                init_cols=None):
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

    mer_final_catalog = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    if image_group_phl is not None:

        # Get values from the image object, unless they were passed explicitly

        if model_seed is None:
            model_seed = image_group_phl.get_seed()

    if options is not None:

        # Get values from the options dict, unless they were passed explicitly

        if model_hash is None:
            model_hash = hash_any(options.items(), format="base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']

    mer_final_catalog.meta = make_mer_final_catalog_header(model_hash=model_hash,
                                                         model_seed=model_seed,
                                                         noise_seed=noise_seed)

    assert(is_in_format(mer_final_catalog, tf))

    return mer_final_catalog
