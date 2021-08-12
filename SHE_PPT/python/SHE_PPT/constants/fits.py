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
fits_version_label = "FITS_VER"
fits_def_label = "FITS_DEF"
she_flag_version_label = "SFLAGVER"
gain_label = "CCDGAIN"
scale_label = "GS_SCALE"
stamp_size_label = "SSIZE"
model_hash_label = "MHASH"
model_seed_label = "MSEED"
noise_seed_label = "NSEED"
extname_label = "EXTNAME"
ccdid_label = "CCDID"
dither_dx_label = "DITHERDX"
dither_dy_label = "DITHERDY"
obs_id_label = "OBS_ID"
pnt_id_label = "PNT_ID"
obs_time_label = "DATE_OBS"
tile_id_label = "TILE_ID"
valid_label = "VALID"
psf_state_identity_label = "OPTID"

# Fits definitions
psf_field_param_def = "she.psfFieldParameters"
psf_calib_param_def = "she.psfCalibrationParameters"

# Tags for science image, noisemap, and mask
sci_tag = "SCI"
noisemap_tag = "RMS"
mask_tag = "FLG"
background_tag = "BKG"
weight_tag = "WGT"
segmentation_tag = "SEG"
details_tag = "DAL"
detections_tag = "DTC"
shear_estimates_tag = "SHM"
mcmc_chains_tag = "MCC"
psf_im_tag = "PSF"
bulge_psf_tag = "BPSF"
disk_psf_tag = "DPSF"
psf_cat_tag = "PSFC"
psf_dm_state_tag = "PSFDM"
psf_om_state_tag = "PSFOM"
psf_pd_state_tag = "PSFPD"
psf_tm_state_tag = "PSFTM"
psf_tml_state_tag = "PSFTL"
psf_zm_state_tag = "PSFZ"
