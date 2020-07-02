""" convert_sim_catalog.py

    Created: 2019/02/26

    Run with a command such as:
    
    E-Run SHE_PPT 0.9 python3 /home/brg/Work/Projects/SHE_PPT/SHE_PPT/scripts/convert_sim_catalog.py EUC_SIM_TUGALCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --star_cat EUC_SIM_TUSTARCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --source_dir /mnt/cephfs/share/SC456/SIM-VIS/vis_science_T2/intermediate/TU/data --max_mag_vis 25.5 --obj_cat obj_cat.xml --dest_dir .

"""

__updated__ = "2019-06-24"

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

import argparse
import os

from SHE_PPT import products
from SHE_PPT.file_io import find_file, get_allowed_filename, write_xml_product
from SHE_PPT.table_formats.psf import initialise_psf_table
from SHE_PPT.table_formats.psf import tf as pstf
from astropy.table import Table
from astropy.io import fits
import numpy as np


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = argparse.ArgumentParser()

    # Input arguments
    parser.add_argument('--psf_image', default=None, type=str,
                        help="pre-SC8 psf-image file")
    parser.add_argument('--source_dir', default='.', type=str,
                        help="Directory in which psf-images are contained (default '.').")
    
    # Output arguments
    parser.add_argument('--dest_dir', default='.', type=str,
                        help="Directory in which output psf-images are contained (default '.').")
    parser.add_argument('--out_psf_image', default="obj_cat.xml", type=str,
                        help="Target Final PSF image product to be created (default psf_model_image.xml)")
    
    args = parser.parse_args()

    # Read in the galaxy (and optionally star) catalogues
    if args.psf_image is None:
        raise ValueError("PSF image must be provided via the --psf_image argument.")

    # Need to convert current FITS file....Start from XML?
    
    psf_image_filename=find_file(args.psf_image, path=args.source_dir)
    hdulist = fits.open(psf_image_filename)
    sim_psf_image = Table.read(psf_image_filename)

    
    num_gals = len(sim_psf_image['Object ID'])
    
    
    stringArray = np.array(['TT' for _ii in range(num_gals)])
    # Initialize the output table with the desired columns
    obj_psf_image = initialise_psf_table(init_columns={pstf.ID: sim_psf_image['Object ID'],
                                                    pstf.template: sim_psf_image['SED template'],
                                                    pstf.bulge_idx: sim_psf_image['Bulge Index'],
                                                    pstf.disk_idx: sim_psf_image['Disk Index'],
                                                    pstf.image_x:np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                  dtype=pstf.dtypes[pstf.image_x]),
                                                    pstf.image_y:np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                  dtype=pstf.dtypes[pstf.image_y]),
                                                    pstf.x:np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                  dtype=pstf.dtypes[pstf.x]),
                                                    pstf.y:np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                  dtype=pstf.dtypes[pstf.y]),
                                                    pstf.cal_time:stringArray,
                                                    pstf.field_time:stringArray})

    # Create a data product for the output
    psf_image_output_filename = os.path.join(args.dest_dir, os.path.basename(psf_image_filename))
    
    obj_cat_prod = products.she_psf_model_image.create_psf_image_product(os.path.join('data',os.path.basename(psf_image_output_filename)))

    out_psf_image= psf_image_output_filename.replace('PSF','P-PSF').replace('.fits','.xml')
    write_xml_product(obj_cat_prod, out_psf_image, workdir=args.dest_dir)
    # Write out the table
    out_hdulist=fits.HDUList([hdulist[0],
                    fits.table_to_hdu(obj_psf_image),hdulist[2],hdulist[3]])
    out_hdulist.info()
    out_hdulist.writeto(psf_image_output_filename, overwrite=True)

    return


if __name__ == "__main__":
    main()
