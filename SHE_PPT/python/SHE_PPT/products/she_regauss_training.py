""" @file she_regauss_training.py

    Created 24 Nov 2017

    Functions to create and output a regauss_training_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
"""

__updated__ = "2021-08-16"

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

from ST_DataModelBindings.dpd.she.regausstraining_stub import dpdSheRegaussTraining
from ..product_utility import create_product_from_template, init_just_datastorage

sample_file_name = 'SHE_PPT/sample_regauss_training.xml'
product_type_name = "DpdSheRegaussTraining"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdSheRegaussTraining,
                          init_function=create_dpd_she_regauss_training)


def create_dpd_she_regauss_training(filename = None,
                                    data_filename = None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename=sample_file_name,
                                        product_type_name=product_type_name,
                                        filename=filename,
                                        data_filename=data_filename)


# Add a useful alias
create_regauss_training_data_product = create_dpd_she_regauss_training
