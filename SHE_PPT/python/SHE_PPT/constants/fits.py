""" @file test_data.py

    Created 12 Aug 2021

    Constants related to FITS files
"""

__updated__ = "2021-08-12"

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

# Header values for fits images
FITS_VERSION_LABEL = "FITS_VER"
FITS_DEF_LABEL = "FITS_DEF"
SHE_FLAG_VERSION_LABEL = "SFLAGVER"
GAIN_LABEL = "CCDGAIN"
SCALE_LABEL = "GS_SCALE"
STAMP_SIZE_LABEL = "SSIZE"
MODEL_HASH_LABEL = "MHASH"
MODEL_SEED_LABEL = "MSEED"
NOISE_SEED_LABEL = "NSEED"
EXTNAME_LABEL = "EXTNAME"
CCDID_LABEL = "CCDID"
DITHER_DX_LABEL = "DITHERDX"
DITHER_DY_LABEL = "DITHERDY"
OBS_ID_LABEL = "OBS_ID"
PNT_ID_LABEL = "PNT_ID"
OBS_TIME_LABEL = "DATE_OBS"
TILE_ID_LABEL = "TILE_ID"
VALID_LABEL = "VALID"

# Fits definitions
PSF_FIELD_PARAM_DEF = "she.psfFieldParameters"
PSF_CALIB_PARAM_DEF = "she.psfCalibrationParameters"

# Tags for science image, noisemap, and mask
SCI_TAG = "SCI"
NOISEMAP_TAG = "RMS"
MASK_TAG = "FLG"
BACKGROUND_TAG = "BKG"
WEIGHT_TAG = "WGT"
SEGMENTATION_TAG = "SEG"
DETAILS_TAG = "DAL"
DETECTIONS_TAG = "DTC"
SHEAR_ESTIMATES_TAG = "SHM"
MCMC_CHAINS_TAG = "MCC"
PSF_IM_TAG = "PSF"
BULGE_PSF_TAG = "BPSF"
DISK_PSF_TAG = "DPSF"
PSF_CAT_TAG = "PSFC"
PSF_DM_STATE_TAG = "PSFDM"
PSF_OM_STATE_TAG = "PSFOM"
PSF_PD_STATE_TAG = "PSFPD"
PSF_TM_STATE_TAG = "PSFTM"
PSF_TML_STATE_TAG = "PSFTL"
PSF_ZM_STATE_TAG = "PSFZ"
