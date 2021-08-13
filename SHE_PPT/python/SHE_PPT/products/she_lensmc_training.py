""" @file she_lensmc_training.py

    Created 24 Nov 2017

    Functions to create and output a lensmc_training_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
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
from ST_DataModelBindings.dpd.she.lensmctraining_stub import dpdSheLensMcTraining

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_just_datastorage


sample_file_name = "SHE_PPT/sample_lensmc_training.xml"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdSheLensMcTraining)


def create_dpd_she_lensmc_training(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_lensmc_training = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_lensmc_training.Header = HeaderProvider.create_generic_header("DpdSheLensMcTraining")

    if filename:
        dpd_she_lensmc_training.set_filename(filename)
    return dpd_she_lensmc_training


# Add a useful alias
create_lensmc_training_data_product = create_dpd_she_lensmc_training
