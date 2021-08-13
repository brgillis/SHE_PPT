""" @file she_psf_model_image_product.py

    Created 17 Nov 2017

    Functions to create and output a she_psf_model_image data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines
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

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.psfmodelimage_stub import dpdShePsfModelImage

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_just_datastorage


sample_file_name = "SHE_PPT/sample_psf_model_image.xml"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdShePsfModelImage)


def create_dpd_she_psf_model_image(filename="None"):
    """
        @TODO fill in docstring
    """

    dpd_she_psf_model_image = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_psf_model_image.Header = HeaderProvider.create_generic_header("DpdShePsfModelImage")

    if filename:
        dpd_she_psf_model_image.set_filename(filename)

    return dpd_she_psf_model_image


# Add a useful alias
create_psf_model_image_product = create_dpd_she_psf_model_image
