""" @file stack_segmentation_product.py

    Created 26 Oct 2017

    Functions to create and output a stack_segmentation data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/she_stack_segmentation.html

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines. This version is
    converted from MER's version, so we need a separate product for it.
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

__updated__ = "2019-08-15"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import os
import pickle

from astropy.io import fits

from ST_DataModelBindings.dpd.she.stackreprojectedsegmentationmap_stub import DpdSheStackReprojectedSegmentationMap
import ST_DataModelBindings.pro.she_stub as she_dict
import ST_DM_DmUtils.DmUtils as dm_utils
import ST_DM_DmUtils.DqcDmUtils as dqc_utils


import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT import detector as dtc
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product
import SHE_PPT.magic_values as mv
from SHE_PPT.utility import find_extension


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdSheShearValidationStatsProduct # @FIXME
    binding_class = DpdSheStackReprojectedSegmentationMapProduct

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename)


def __get_data_filename(self):
    return get_data_filename_from_product(self)


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


class DpdSheStackReprojectedSegmentationMapProduct:

    def __init__(self):
        self.Header = None
        self.Data = None
        self.QualityFlags = None
        
    def validateBinding(self):
        return False    

class SheStackReprojectedSegmentationMapProduct:

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
def create_stack_reprojected_segmentation_map(data_filename,filter_names=[]):
    """Creates a SHE_MER stack reprojected segmentation map binding.

    Parameters
    ----------
    file_name: str
        Name of the fits image file containing the segmentation map
    filter_names: list
        A list with all the filter names that were used to produce the
        segmentation map.

    Returns
    -------
    object
        The MER segmentation map binding.

    """
    # Create the appropriate data product binding
    dp = DpdSheStackReprojectedSegmentationMapProduct()

    # Add the generic header to the data product
    dp.Header = HeaderProvider.create_generic_header(
        dp.__class__.__name__)

    # Add the data element to the data product
    dp.Data = dm_utils.create_image(she_dict.sheStackReprojectedSegmentationMap)

    # Add the general MER metadata
    __add_general_segm_metadata(dp.Data)

    # Add the filter list
    dp.Data.FilterList = dm_utils.create_filter_list(filter_names)

    # Add the WCS
    dp.Data.WCS = dm_utils.create_wcs(False)

    # Add the Image spatial footprint
    dp.Data.ImgSpatialFootprint = dm_utils.create_spatial_footprint()

    # Add the DataStorage
    dp.Data.DataStorage = dm_utils.create_fits_storage(
        she_dict.sheStackReprojectedSegmentationMapFile, data_filename,
        "she.stackReprojectedSegmentationMap", "8.0")

    # Add the quality parameters
    #dp.Data.QualityParams = dqc_utils.create_quality_parameters(
    #    she_dict.sheStackReprojectedSegmentationMapDqc)

    # Add the quality flags
    #dp.QualityFlags = dqc_utils.create_quality_flags(
    #    merdqc_dict.sqfDpdMerSegmentationMap)

    return dp


def __add_general_segm_metadata(data_binding):
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
    data_binding.TileList = __create_tile_list([(101,"101")])

def __create_tile_list(tile_list):
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
        tile_idx for tile_idx,tile_prod_id in tile_list 
        if tile_idx is not None and tile_prod_id is not None]))
    for tile_index in unique_tile_idx:
        tile_prod_id=[tile_prod_id 
            for tile_idx,tile_prod_id in tile_list 
            if tile_idx==tile_index and tile_prod_id is not None].pop()
        tile_prod=she_dict.sheListOfTiles()
        tile_prod.TileIndex=tile_index
        tile_prod.TileProductId=tile_prod_id
        she_list_of_tiles.append(tile_prod)
    return she_list_of_tiles

def __create_detector_list(detector_id_list):
    """Creates a list of detector ids binding.

    Parameters
    ----------
    detector_id_list: list
        A list with the detector ids.

    Returns
    -------
    object
        The SHE list of detector ids binding.

    """
    # Remove duplications and None values
    if detector_id_list is None:
        clean_detector_id_list = []
    else:
        clean_detector_id_list = set(detector_id_list)
        clean_detector_id_list.discard(None)
        clean_detector_id_list = list(clean_detector_id_list)
        clean_detector_id_list.sort()

    # Create the list of detector ids binding
    she_list_of_detectors = she_dict.sheListOfDetectors()

    # Add the detector ids
    for detector_id in clean_detector_id_list:
        she_list_of_detectors.append(detector_id)

    return she_list_of_detectors
    
