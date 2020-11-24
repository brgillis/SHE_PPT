""" @file she_validation_test_results.py

    Created 24 Nov 2020

    Functions to create and output a she_validation_test_results data product.

    Origin: OU-SHE - Output from various pipelines.
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

__updated__ = "2020-11-24"


from SHE_PPT.file_io import read_xml_product, find_aux_file
from SHE_PPT.product_utility import get_data_filename_from_product, set_data_filename_of_product
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults

sample_file_name = "SHE_PPT/sample_validation_test_results.xml"


def init():
    """
        Initialisers for SHE Validation Test Results data product
    """

    binding_class = dpdSheValidationTestResults

    # Add the data file name methods

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


def create_dpd_she_validation_test_results():
    """
        @TODO fill in docstring
    """

    dpd_she_validation_test_results = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_validation_test_results.Header = HeaderProvider.create_generic_header("SHE")

    return dpd_she_validation_test_results


# Add a useful alias
create_validation_test_results_product = create_dpd_she_validation_test_results
