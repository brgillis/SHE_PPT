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
from SHE_PPT.file_io import find_file, get_allowed_filename, read_xml_product,write_xml_product
from SHE_PPT.table_formats.she_psf_model_image import initialise_psf_table
from SHE_PPT.table_formats.she_psf_model_image import tf as pstf
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
    parser.add_argument('--source_dir', default='.', type=str,
                        help="Directory in which psf-images are contained (default '.').")
    parser.add_argument('--mer_catalogue',type=str,
                        help="Mer catalogue")
    
    # Output arguments
    parser.add_argument('--dest_dir', default='.', type=str,
                        help="Directory in which output psf-images are contained (default '.').")
    parser.add_argument('--out_psf_image', default="obj_cat.xml", type=str,
                        help="Target Final PSF image product to be created (default psf_model_image.xml)")
    
    args = parser.parse_args()

    # Read in the galaxy (and optionally star) catalogues
    psf_tables = []
    
    
    # Read in mer final catalogue
    mer_cat_prod=read_xml_product(os.path.join(args.source_dir,args.mer_catalogue))
        
    mer_cat_fitsfile = mer_cat_prod.Data.DataStorage.DataContainer.FileName
    
    catalogue = Table.read(os.path.join(args.source_dir,'data',mer_cat_fitsfile))
   
    filename = 'TEST_PSF.fits'

    hdulist = fits.HDUList([fits.PrimaryHDU()])  # Start with an empty primary HDU

    # Initialize table with null values
    num_rows = 2
    
    # Initialise without any columns
    psfc = initialise_psf_table()
    # Add rows separately 
    for row in range(num_rows):
        psfc.add_row([catalogue.field('OBJECT_ID')[row],-1,-1,-1,-1,-1,-1.0,-1.0,'NONE','NONE'])

    print("PSF TAB: ",psfc)
    # Add the table to the HDU list
    psfc_hdu = fits.table_to_hdu(psfc)
    print("PSFC NR: ",psfc_hdu.data.size)
    hdulist.append(psfc_hdu)

    psf_tables.append(psfc)  # Keep a copy of the table
    psf_tables[0].remove_indices(pstf.ID)  # Necessary for bug workaround in astropy
    psf_tables[0].add_index(pstf.ID)  # Allow it to be indexed by galaxy ID

        # Write out the table
    hdulist.writeto(os.path.join(args.source_dir,'data',filename), overwrite=True)
    
    return


if __name__ == "__main__":
    main()
