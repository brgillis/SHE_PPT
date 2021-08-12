""" @file mer_segmentation_map.py

    Created 26 Oct 2017

    Functions to create and output a mosaic data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_mosaic.html

    Origin: OU-MER - Input to Analysis pipeline
"""

__updated__ = "2021-08-12"

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

import os

from astropy.io import fits

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.mer.raw.segmentationmap_stub import dpdMerSegmentationMap

from .. import detector as dtc
from ..constants.fits import segmentation_tag
from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product
from ..utility import find_extension


sample_file_name = "SHE_PPT/sample_mer_segmentation_map.xml"


# Convenience function to easily load the actual map
def load_mosaic_hdu(filename, dir=None, hdu=0, detector_x=None, detector_y=None, **kwargs):
    """Directly loads the mosaic image from the filename of the data product.

    Parameters
    ----------
    filename : str
        Filename of the mosaic data product. If `dir` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `dir` is
        supplied, `filename` should be only the local name of the file.
    dir : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    hdu : int
        Index of the HDU to load. If `detector` is supplied, this is ignored.
    detector : int
        ID of the detector whose HDU should be loaded. Overrides `hdu` if
        supplied.
    **kwargs
        Keyword arguments to pass to fits.open.

    Returns
    -------
    mosaic_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the mosaic image and its header.

    Raises
    ------
    IOError
        Will raise an IOError if either no such file as `filename` exists or
        if the filename of the mosaic data contained within the product does
        not exist.
    """

    init()

    if dir is None:
        dir = ""

    mosaic_product = read_xml_product(
        xml_filename=os.path.join(dir, filename))

    data_filename = mosaic_product.get_data_filename()

    mosaic_hdulist = fits.open(data_filename, **kwargs)

    if detector_x is not None and detector_y is not None:
        hdu = find_extension(mosaic_hdulist, extname=dtc.get_id_string(
            detector_x, detector_y) + "." + segmentation_tag)

    mosaic_hdu = mosaic_hdulist[hdu]

    return mosaic_hdu

# Initialisation function, to add methods to an imported XML class


def init():
    """
        Adds some extra functionality to the DpdMerSegmentationMap product
    """

    binding_class = dpdMerSegmentationMap

    if not hasattr(binding_class, "initialised"):
        binding_class.initialised = True
    else:
        return

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

    all_filenames = [self.get_data_filename(), ]

    return all_filenames


def create_dpd_mer_mosaic(data_filename="",
                          ):
    """
        @TODO fill in docstring
    """

    dpd_mer_mosaic = read_xml_product(
        find_aux_file(sample_file_name))

    dpd_mer_mosaic.Header = HeaderProvider.create_generic_header("DpdMerSegmentationMap")

    __set_data_filename(dpd_mer_mosaic, data_filename)

    return dpd_mer_mosaic


# Add a useful alias
create_mosaic_product = create_dpd_mer_mosaic
