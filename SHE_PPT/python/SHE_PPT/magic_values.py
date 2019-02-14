""" @file output_shear_estimates.py

    Created 1 Sep 2017

    Various magic values used by the SHE PF.
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

logger_name = "SHE_PPT"

# Header values for fits images
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
obs_time_label = "DATE-OBS"
field_id_label = "FIELDID"
psf_state_identity_label = "OPTID"

# Special values for tables
psf_zm_identity = "zfit"
psf_tm_identity = "tmfit"

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
psf_zm_state_tag = "PSFZS"
psf_tm_state_tag = "PSFTS"

# Miscellaneous
segmap_unassigned_value = 0
segmap_other_value = -1
short_instance_id_maxlen = 17

# mag_vis_zeropoint = 25.50087633632 # From ETC
# mag_vis_zeropoint = 25.4534 # From Sami's sims' config file
mag_vis_zeropoint = 25.6527  # From Lance's code
mag_i_zeropoint = 25.3884  # From Lance's code

# Information about test data
test_datadir = "/tmp"
