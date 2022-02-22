""" convert_sim_catalog.py

    Created: 2019/02/26

    Run with a command such as:
    
    E-Run SHE_PPT 0.9 python3 /home/brg/Work/Projects/SHE_PPT/SHE_PPT/scripts/convert_sim_catalog.py EUC_SIM_TUGALCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --star_cat EUC_SIM_TUSTARCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --source_dir /mnt/cephfs/share/SC456/SIM-VIS/vis_science_T2/intermediate/TU/data --max_mag_vis 25.5 --obj_cat obj_cat.xml --dest_dir .

"""
import argparse
import os
from   collections import namedtuple

from SHE_PPT import products
from SHE_PPT.file_io import find_file, get_allowed_filename, write_xml_product
from SHE_PPT.products import mer_final_catalog as mpd

__updated__ = "2021-08-13"

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


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = argparse.ArgumentParser()

    # Input arguments
    parser.add_argument('--input_dir', default=None, type=str,
                        help="Directory containing existing MER final data")
    # Output arguments
    parser.add_argument('--dest_dir', default='.', type=str,
                        help="Directory in which output xml files are contained (default '.').")
    
    args = parser.parse_args()

    input_xml_list = [fname for fname in os.listdir(args.input_dir) 
                      if fname.endswith('.xml')]
    for xml_file in input_xml_list:
        xml_info = get_xml_info(os.path.join(args.input_dir,xml_file))
        mer_cat_fitsfile = xml_info.mer_cat_fits
        cutouts_fitsfile = xml_info.cutout_fits
        print("XML: ",xml_file,xml_info,mer_cat_fitsfile)
        mer_final_prod = mpd.create_dpd_she_detections(mer_cat_fitsfile)
        #mer_final_prod.Data.CutoutsCatalogStorage.DataContainer.Filename=cutouts_fitsfile
        #mer_final_prod.Data.TileIndex=int(xml_info.TileIndex)
        mer_final_prod.Data.ObservationIdList=xml_info.ObservationIdList
        mer_final_prod.Header.SoftwareName='MER_IAL_Pipeline'
        mer_final_prod.Header.SoftwareRelease='9.0.0'
        mer_final_prod.Header.ProductId=xml_info.ProductId
        output_xml_file = os.path.join(args.dest_dir,xml_file)
        write_xml_product(mer_final_prod,output_xml_file)
        
        
def get_xml_info(filename):
    """
    """
    lines = open(filename).readlines()
    mer_upd_tup = namedtuple('MerUpdate','mer_cat_fits cutout_fits TileIndex ObservationIdList '
                             'ProductId')
    key_list= ['DataStorage.DataContainer.FileName','CutoutsCatalogStorage.DataContainer.FileName',
                 'TileIndex','ObservationIdList','ProductId']
    x_info_val_list=[]
    for key in key_list:
        x_value = find_value(key,lines)
        x_info_val_list.append(x_value)
    return mer_upd_tup(*x_info_val_list) 

def find_value(key,lines):
    """
    """
    if '.' in key:
        parts = key.split('.')
    else:
        parts=[key]

    print("KY: ",key, parts)    
    line_no = None
    exist_line_no = None
    for jj,prt in enumerate(parts):
        print("PT: ",jj,prt,exist_line_no,line_no)
        if line_no:
            exist_line_no = line_no
            match = False
            line_no = exist_line_no+1
            while not match:
                if '<'+prt in lines[line_no]:
                    match=True
        else:
            for ii,line in enumerate(lines):
                if '<'+prt in line:
                    line_no=ii
        print("PT2: ",line_no)
    print("LN: ",lines[line_no])
    return lines[line_no].split('>')[1].split('<')[0]
    
if __name__ == "__main__":
    main()
