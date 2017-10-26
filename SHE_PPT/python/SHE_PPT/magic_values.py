""" @file output_shear_estimates.py

    Created 1 Sep 2017

    Various magic values used by the SHE PF.

    ---------------------------------------------------------------------

    Copyright (C) 2012-2020 Euclid Science Ground Segment      
       
    This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General    
    Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)    
    any later version.    
       
    This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied    
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more    
    details.    
       
    You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to    
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Header values for fits images
gain_label = "CCDGAIN"
scale_label = "PX_SCALE"
stamp_size_label = "SSIZE"
model_hash_label = "MHASH"
model_seed_label = "MSEED"
noise_seed_label = "NSEED"
extname_label = "EXTNAME"
dither_dx_label = "DITHERDX"
dither_dy_label = "DITHERDY"

# Tags for science image, noisemap, and mask
sci_tag = "SCI"
noisemap_tag = "RMS"
mask_tag = "FLG"
segmentation_tag = "SEG"
details_tag = "DAL"
detections_tag = "DTC"
shear_estimates_tag = "SHM"
mcmc_chains_tag = "MCC"
bulge_psf_tag = "BPSF"
disk_psf_tag = "DPSF"
psf_cat_tag = "PSFC"

# Miscellaneous
segmap_unnasigned_value = -1
