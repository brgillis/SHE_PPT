""" convert_sim_catalog.py

    Created: 2019/02/26

    Run with a command such as:

    E-Run SHE_PPT 0.9 python3 /home/brg/Work/Projects/SHE_PPT/SHE_PPT/scripts/convert_sim_catalog.py
    EUC_SIM_TUGALCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --star_cat
    EUC_SIM_TUSTARCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --source_dir
    /mnt/cephfs/share/SC456/SIM-VIS/vis_science_T2/intermediate/TU/data --max_mag_vis 25.5 --obj_cat obj_cat.xml
    --dest_dir .

"""
import argparse
import os

import ST_DM_DmUtils.DmUtils as dm_utils
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
import ST_DataModelBindings.dpd.she.exposurereprojectedsegmentationmap_stub as expsegm_stub
import ST_DataModelBindings.dpd.she.stackreprojectedsegmentationmap_stub as stacksegm_stub
import ST_DataModelBindings.pro.she_stub as she_dict
from SHE_PPT.file_io import write_xml_product

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
    parser.add_argument('--segm_type', default = None, type = str,
                        help = "Type exposure/stack")
    # Output arguments
    parser.add_argument('--dest_dir', default = '.', type = str,
                        help = "Directory in which output xml files are contained (default '.').")
    parser.add_argument('--out_segm_filename', default = "obj_cat.xml", type = str,
                        help = "Target Final xml  product to be created (default psf_model_image.xml)")

    args = parser.parse_args()

    # Read in the galaxy (and optionally star) catalogues
    if args.segm_type is None:
        raise ValueError("Segmentation type must be provided via the --psf_image argument.")

    # Need to convert current FITS file....Start from XML?
    is_stack = args.segm_type == 'stack'

    if is_stack:
        dp = stacksegm_stub.DpdSheStackReprojectedSegmentationMap()
    else:
        dp = expsegm_stub.DpdSheExposureReprojectedSegmentationMap()

    dp.Header = HeaderProvider.create_generic_header(
        dp.__class__.__name__)
    dp.Header.Curator = 'SHE'

    # Add the data element to the data product
    data_prod = (she_dict.sheStackReprojectedSegmentationMap if is_stack else
                 she_dict.sheExposureReprojectedSegmentationMap)
    dp.Data = dm_utils.create_image(data_prod)

    # Add the general MER metadata
    _add_general_segm_metadata(dp.Data)

    if not is_stack:
        detector_id_list = [range(1, 37)]
        dp.Data.DetectorList = _create_detector_list(detector_id_list)

    # Add the filter list
    # dp.Data.FilterList = dm_utils.create_filter_list(filter_names)

    # Add the WCS
    if is_stack:
        dp.Data.WCS = dm_utils.create_wcs(False)

    # Add the Image spatial footprint
    dp.Data.ImgSpatialFootprint = dm_utils.create_spatial_footprint()

    # Add the DataStorage
    data_prod = (she_dict.sheStackReprojectedSegmentationMapFile if is_stack
                 else she_dict.sheExposureReprojectedSegmentationMapFile)
    dp.Data.DataStorage = dm_utils.create_fits_storage(
        data_prod, 'None',
        "she.%sReprojectedSegmentationMap" % (args.segm_type), "8.0")

    # Add the quality parameters
    # dp.Data.QualityParams = dqc_utils.create_quality_parameters(
    #    she_dict.sheStackReprojectedSegmentationMapDqc)

    # Add the quality flags
    # dp.QualityFlags = dqc_utils.create_quality_flags(
    #    merdqc_dict.sqfDpdMerSegmentationMap)

    output_filename = os.path.join(args.dest_dir, args.out_segm_filename)
    write_xml_product(dp, output_filename, allow_pickled = False)


def _add_general_segm_metadata(data_binding):
    """Adds the general metadata included in MER data products.

    Parameters
    ----------
    data_binding: object
        A MER data product Data binding.

    """
    # Add the ObservationId
    data_binding.ObservationId = 101

    # Add the ProductId
    data_binding.StackProductId = "101"

    # Add the TileList
    data_binding.TileList = _create_tile_list([(101, "101")])


def _create_tile_list(tile_list):
    """Creates a list of tile ids binding.

    Parameters
    ----------
    tile_list: list
        A list with the tile index and productIDs

    Returns
    -------
    object
        The SHE list of tile ids binding.

    """
    # Remove duplications and None values

    # Create the list of tile ids binding
    she_list_of_tiles = []

    # Add the tile ids
    unique_tile_idx = list(set([
        tile_idx for tile_idx, tile_prod_id in tile_list
        if tile_idx is not None and tile_prod_id is not None]))
    for tile_index in unique_tile_idx:
        tile_prod_id = [tile_prod_id
                        for tile_idx, tile_prod_id in tile_list
                        if tile_idx == tile_index and tile_prod_id is not None].pop()
        tile_prod = she_dict.sheListOfTiles()
        tile_prod.TileIndex = tile_index
        tile_prod.TileProductId = tile_prod_id
        she_list_of_tiles.append(tile_prod)
    return she_list_of_tiles


def _create_detector_list(detector_id_list):
    """Creates a list of detector ids binding.

    Parameters
    ----------
    detector_id_list: list
        A list with the detector ids.

    Returns
    -------
    object
        The SHE list of detectors binding.

    """
    she_list_of_detectors = []
    for det_id in detector_id_list:
        det_prod = she_dict.sheListOfDetectors()
        det_prod.DetectorID = 'CCDID %s' % det_id
        det_prod.WCS = dm_utils.create_wcs(False)
        det_prod.Zeropoint = 25.
        det_prod.Saturation = 10000.

        she_list_of_detectors.append(det_prod)

    return she_list_of_detectors


if __name__ == "__main__":
    main()
