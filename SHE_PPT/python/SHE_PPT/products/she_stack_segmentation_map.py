""" @file she_stack_segmentation_product.py

    Created 26 Oct 2017

    Functions to create and output a stack_segmentation data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/she_stack_segmentation.html

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines. This version is
    converted from MER's version, so we need a separate product for it.
"""

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

import os

from astropy.io import fits

from ST_DataModelBindings.dpd.she.stackreprojectedsegmentationmap_stub import dpdSheStackReprojectedSegmentationMap

from ..file_io import read_xml_product
from ..product_utility import init_just_datastorage, create_product_from_template


sample_file_name = "SHE_PPT/sample_stack_reprojected_segmentation_map.xml"


# Convenience function to easily load the actual map
def load_stack_segmentation_map(filename, dir=None, **kwargs):
    """Directly loads the stack_segmentation_map image from the filename of the data product.

    Parameters
    ----------
    filename : str
        Filename of the stack_segmentation_map data product. If `dir` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `dir` is
        supplied, `filename` should be only the local name of the file.
    dir : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    **kwargs
        Keyword arguments to pass to fits.open.

    Returns
    -------
    stack_segmentation_map_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the stack_segmentation_map image and its header.

    Raises
    ------
    IOError
        Will raise an IOError if either no such file as `filename` exists or
        if the filename of the stack_segmentation_map data contained within the product does
        not exist.
    """

    init()

    if dir is None:
        dir = ""

    stack_segmentation_map_product = read_xml_product(
        xml_filename=os.path.join(dir, filename))

    data_filename = stack_segmentation_map_product.get_data_filename()

    stack_segmentation_map_hdulist = fits.open(data_filename, **kwargs)

    return stack_segmentation_map_hdulist[0]

# Initialisation function, to add methods to an imported XML class


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdSheStackReprojectedSegmentationMap)


def create_dpd_she_stack_segmentation_map(filename=None,
                                          data_filename=None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename=sample_file_name,
                                        product_name="DpdSheStackReprojectedSegmentationMap",
                                        filename=filename,
                                        data_filename=data_filename)


# Add a useful alias
create_stack_segmentation_map_product = create_dpd_she_stack_segmentation_map
