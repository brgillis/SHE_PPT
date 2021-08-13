""" @file she_reconciliation_config.py

    Created 22 July 2020

    Functions to create and output a reconciliation_config data product.

    Origin: OU-SHE - Input to Reconciliation pipeline; must be persistent in archive.
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

__updated__ = "2021-06-10"


import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.reconciliationconfig_stub import dpdSheReconciliationConfig

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_reconciliation_config.xml"


def init():
    """
        Initialisers for LensMC training
    """

    binding_class = dpdSheReconciliationConfig

    # Add the data file name methods

    binding_class.set_filename = _set_filename
    binding_class.get_filename = _get_filename
    binding_class.set_data_filename = _set_filename
    binding_class.get_data_filename = _get_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.has_files = False



def _set_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def _get_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def _get_all_filenames(self):

    all_filenames = [self.get_filename()]

    return all_filenames


def create_dpd_she_reconciliation_config(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_reconciliation_config = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_reconciliation_config.Header = HeaderProvider.create_generic_header("DpdSheReconciliationConfig")

    if filename:
        _set_filename(dpd_she_reconciliation_config, filename)
    return dpd_she_reconciliation_config


# Add a useful alias
create_reconciliation_config_data_product = create_dpd_she_reconciliation_config
