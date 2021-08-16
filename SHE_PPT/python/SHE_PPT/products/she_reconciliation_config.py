""" @file she_reconciliation_config.py

    Created 22 July 2020

    Functions to create and output a reconciliation_config data product.

    Origin: OU-SHE - Input to Reconciliation pipeline; must be persistent in archive.
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

from ST_DataModelBindings.dpd.she.reconciliationconfig_stub import dpdSheReconciliationConfig

from ..product_utility import init_just_datastorage, create_product_from_template


sample_file_name = "SHE_PPT/sample_reconciliation_config.xml"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdSheReconciliationConfig,
                          init_function=create_dpd_she_reconciliation_config)


def create_dpd_she_reconciliation_config(filename=None,
                                         data_filename=None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename=sample_file_name,
                                        product_type_name="DpdSheReconciliationConfig",
                                        filename=filename,
                                        data_filename=data_filename)


# Add a useful alias
create_reconciliation_config_data_product = create_dpd_she_reconciliation_config
