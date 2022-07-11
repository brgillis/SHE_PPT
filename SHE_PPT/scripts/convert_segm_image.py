""" convert_sim_catalog.py

    Created: 2019/02/26

    Run with a command such as:

    E-Run SHE_PPT 0.9 python3 /home/brg/Work/Projects/SHE_PPT/SHE_PPT/scripts/convert_sim_catalog.py
    EUC_SIM_TUGALCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --star_cat
    EUC_SIM_TUSTARCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --source_dir
    /mnt/cephfs/share/SC456/SIM-VIS/vis_science_T2/intermediate/TU/data --max_mag_vis 25.5 --obj_cat obj_cat.xml
    --dest_dir .

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
from operator import itemgetter

from SHE_PPT import products
from SHE_PPT.file_io import (find_file, get_data_filename_from_product, read_xml_product, write_xml_product)


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = argparse.ArgumentParser()

    # Input arguments
    parser.add_argument('--segm_image', default = None, type = str,
                        help = "pre-SC8 segmentation image file")
    parser.add_argument('--segm_type', default = None, type = str,
                        help = "segmentation type: stack, exposure, mer")
    parser.add_argument('--source_dir', default = '.', type = str,
                        help = "Directory in which segm-images are contained (default '.').")
    parser.add_argument('--datadir', default = 'data', type = str,
                        help = 'subdir containing fits image')
    # Output arguments
    parser.add_argument('--dest_dir', default = '.', type = str,
                        help = "Directory in which output segm-images are contained (default '.').")
    parser.add_argument('--out_segm_image', default = "obj_cat.xml", type = str,
                        help = "Target Final PSF image product to be created (default segm_model_image.xml)")

    args = parser.parse_args()

    # Read in the galaxy (and optionally star) catalogues
    if args.segm_image is None:
        raise ValueError("Segmentation image must be provided via the --segm_image argument.")

    old_xml_file = find_file(os.path.join(args.source_dir, args.segm_image))

    # Find old FITS file

    datadir = args.datadir
    fits_file_name = find_fits_file(old_xml_file, datadir)
    if args.segm_type == 'exposure':
        prod = products.she_exposure_segmentation_map.create_dpd_she_exposure_segmentation_map(fits_file_name)
    elif args.segm_type == 'stack':
        prod = products.she_stack_segmentation_map.create_dpd_she_stack_segmentation_map(fits_file_name)
    elif args.segm_type == 'mer':
        prod = products.mer_segmentation_map.create_dpd_mer_mosaic(fits_file_name)
    else:
        raise Exception("%s is not a valid segm_type, it should be exposure,stack or mer" % args.segm_type)

    # Create a data product for the output
    # Updates to xml?
    # E.g. WCS?

    write_xml_product(prod, args.out_segm_image, workdir = args.dest_dir)

    return


def find_fits_file(xml_file_name, datadir):
    """
    """
    fits_file = None
    try:
        prod = read_xml_product(xml_file_name)
        try:
            fits_file = get_data_filename_from_product(prod)
        except:
            fits_file = get_data_filename_from_product(prod, "DataStorage")
    except:

        file_list = os.listdir(os.path.join(os.path.dirname(xml_file_name), datadir))

        metric_list = []
        for file_name in file_list:
            if file_name.endswith('.fits') and 'SEG' in file_name.upper():
                # Find matches in name...
                metric = calc_match_name(file_name, xml_file_name)
                metric_list.append((file_name, metric))
        metric_list = sorted(metric_list, key = itemgetter(1))
        if metric_list[-1][1] > 0:
            fits_file = metric_list[-1][0]
        elif 'STACK' in xml_file_name.upper():
            poss_files = [file_name for file_name, _met in metric_list if 'STACK' in file_name.upper()]
            if len(poss_files) == 1:
                fits_file = poss_files[0]
            else:
                print("No definite match")
        else:
            print("No good match")
    print("FITS: ", fits_file)
    return fits_file


def calc_match_name(file_name, xml_file):
    """
    """
    metric = 0.
    fits_parts = os.path.basename(file_name.replace('.fits', '')).split('_')
    xml_parts = os.path.basename(xml_file.replace('.xml', '')).split('_')
    print("CMP: ", file_name, xml_file)
    for ii, part in enumerate(fits_parts):
        if ii < len(xml_parts):
            print("MET: ", ii, part, xml_parts[ii], metric)
            if part == xml_parts[ii]:
                metric += 1.
            elif '-' in part:
                fits_sub_parts = part.split('-')
                xml_sub_parts = xml_parts[ii].split('-')
                metric += len([spt for spt in fits_sub_parts if spt in xml_sub_parts]) / len(xml_sub_parts)
    return metric


if __name__ == "__main__":
    main()
