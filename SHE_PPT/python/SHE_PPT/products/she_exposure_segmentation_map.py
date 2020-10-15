""" @file she_exposure_segmentation_product.py

    Created 26 Oct 2017

    Functions to create and output a exposure_segmentation data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/she_exposure_segmentation.html

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
from astropy.io import fits

from ST_DataModelBindings.dpd.she.exposurereprojectedsegmentationmap_stub import dpdSheExposureReprojectedSegmentationMap

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT import detector as dtc
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product
import SHE_PPT.magic_values as mv
from SHE_PPT.utility import find_extension

sample_file_name = "SHE_PPT/sample_exposure_reprojected_segmentation_map.xml"


# Convenience function to easily load the actual map
def load_she_exposure_segmentation_map(filename, directory=None, **kwargs):
    """Directly loads the she_exposure_segmentation_map image from the filename of the data product.

    Parameters
    ----------
    filename : str
        Filename of the she_exposure_segmentation_map data product. If `directory` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `directory` is
        supplied, `filename` should be only the local name of the file.
    directory : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    **kwargs
        Keyword arguments to pass to fits.open.

    Returns
    -------
    she_exposure_segmentation_map_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the she_exposure_segmentation_map image and its header.

    Raises
    ------
    IOError
        Will raise an IOError if either no such file as `filename` exists or
        if the filename of the she_exposure_segmentation_map data contained within the product does
        not exist.
    """

    init()

    if directory is None:
        directory = ""

    she_exposure_segmentation_map_product = read_xml_product(
        xml_filename=os.path.join(directory, filename))

    data_filename = she_exposure_segmentation_map_product.get_data_filename()

    she_exposure_segmentation_map_hdulist = fits.open(data_filename, **kwargs)

    return she_exposure_segmentation_map_hdulist[0]

# Initialisation function, to add methods to an imported XML class


def init():
    """
        Adds some extra functionality to the DpdSheExposureReprojectedSegmentationMap product
    """

    # binding_class = she_dpd.DpdSheShearValidationStatsProduct # @FIXME
    binding_class = dpdSheExposureReprojectedSegmentationMap

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def __get_data_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename()]

    return all_filenames


def create_dpd_she_exposure_segmentation_map(data_filename="None"):
    """Creates a SHE_MER exposure reprojected segmentation map binding.

    Parameters
    ----------
    file_name: str
        Name of the fits image file containing the segmentation map

    Returns
    -------
    object
        The SHE_MER exposure segmentation map binding.

    """
    dpd_she_exposure_reproj_seg_map_data = read_xml_product(
        find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_exposure_reproj_seg_map_data.Header = HeaderProvider.create_generic_header("SHE")

    __set_data_filename(dpd_she_exposure_reproj_seg_map_data, data_filename)

    # dpd_she_exposure_reproj_seg_map_data.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    # dpd_she_exposure_reproj_seg_map_data.Header = "SHE"

    # dpd_she_exposure_reproj_seg_map_data.Data = create_she_exposure_reproj_seg_map_data(filename)

    return dpd_she_exposure_reproj_seg_map_data

# Add a useful alias


create_she_exposure_segmentation_map_product = create_dpd_she_exposure_segmentation_map

