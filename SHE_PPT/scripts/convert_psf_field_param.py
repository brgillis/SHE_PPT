""" convert_psf_field_param.py

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

from astropy.io import fits
from astropy.table import Table

from SHE_PPT import products
from SHE_PPT.file_io import (find_file, get_allowed_filename,
                             write_xml_product, read_xml_product)
import SHE_PPT.table_formats.she_psf_dm_state as dm
import SHE_PPT.table_formats.she_psf_om_state as om
import SHE_PPT.table_formats.she_psf_tm_state as tm
import SHE_PPT.table_formats.she_psf_zm_state as zm
import numpy as np


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = argparse.ArgumentParser()

    # Input arguments
    parser.add_argument('--workdir', default='.', type=str,
                        help="Work directory")

    args = parser.parse_args()

    # Need to convert current FITS file....Start from XML?

    field_param_filenames_list = [os.path.join(args.workdir, fname) for fname in os.listdir(args.workdir)
                                  if fname.endswith('.xml') and 'FIELDPARAM' in fname]

    for field_params_filename in field_param_filenames_list:

        # Read in xml and get FITS filename
        field_param_prod = read_xml_product(field_params_filename)

        tel_mode_params_filename = field_param_prod.get_filename()
        if (os.path.dirname(tel_mode_params_filename) == 'data'
                and not os.path.exists(os.path.join(args.workdir, 'data'))):
            tel_mode_params_filename = os.path.basename(tel_mode_params_filename)

        hdulist = fits.open(os.path.join(args.workdir, tel_mode_params_filename))
        # Add Zernike modes
        zern_mode_table = zm.initialise_psf_field_zm_state_table()
        zern_mode_hdu = fits.BinTableHDU(zern_mode_table)
        hdulist.append(zern_mode_hdu)
        # Add Other modes
        oth_mode_table = om.initialise_psf_field_om_state_table()
        oth_mode_hdu = fits.BinTableHDU(oth_mode_table)
        hdulist.append(oth_mode_hdu)
        # Add diagnostic
        diag_mode_table = dm.initialise_psf_field_dm_state_table()
        diag_mode_hdu = fits.BinTableHDU(diag_mode_table)
        hdulist.append(diag_mode_hdu)

        # Add time stamp from orig filename to header...
        time_stamp = get_timestamp(tel_mode_params_filename)
        hdulist[0].header['DATE_OBS'] = time_stamp

        psf_field_param_fits_filename = get_allowed_filename('PSF-FIELD-PARAMS', time_stamp, release='8.0')

        field_param_prod.set_filename(psf_field_param_fits_filename)

        if (os.path.dirname(psf_field_param_fits_filename) == 'data'
                and not os.path.exists(os.path.join(args.workdir, 'data'))):
            psf_field_param_fits_filename = os.path.basename(psf_field_param_fits_filename)

        hdulist.writeto(os.path.join(args.workdir, psf_field_param_fits_filename), overwrite=True)
        write_xml_product(field_param_prod, field_params_filename, allow_pickled=False)
        print("Updated %s with new FITS file %s" % (field_params_filename, psf_field_param_fits_filename))
    return


def get_timestamp(filename):
    """
    """
    parts = filename.split('_')
    time_stamp = [part for part in parts if part.endswith('Z') and
                  part.startswith('20') and 'T' in part]
    if time_stamp:
        return time_stamp.pop()
    else:
        raise Exception("No time stamp")


if __name__ == "__main__":
    main()
