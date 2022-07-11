""" @file she_galaxy_population_priors.py

    Created 17 Nov 2017

    Functions to create and output a galaxy_population_priors priors data product.

    Origin: OU-SHE - Input to Calibration pipeline; needs to be implemented in data model.
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

from ST_DataModelBindings.dpd.she.galaxypopulationpriors_stub import dpdSheGalaxyPopulationPriors
from ..product_utility import (create_product_from_template, get_data_filename_from_product, init_binding_class,
                               set_data_filename_of_product, )

sample_file_name = "SHE_PPT/sample_galaxy_population_priors.xml"
product_type_name = "DpdSheGalaxyPopulationPriors"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    binding_class = dpdSheGalaxyPopulationPriors

    if not init_binding_class(binding_class = binding_class,
                              init_function = create_dpd_she_galaxy_population_priors):
        return

    # Add the data file name methods

    binding_class.set_filename = _set_data_filename
    binding_class.get_filename = _get_data_filename
    binding_class.set_data_filename = _set_data_filename
    binding_class.get_data_filename = _get_data_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.has_files = True


def _set_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorageList[0]")


def _get_data_filename(self):
    return get_data_filename_from_product(self, "DataStorageList[0]")


def _get_all_filenames(self):

    all_filenames = []
    for data_storage in self.Data.DataStorageList:
        all_filenames.append(data_storage.DataContainer.FileName)

    return all_filenames


def create_dpd_she_galaxy_population_priors(filename = None,
                                            data_filename = None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename = sample_file_name,
                                        product_type_name = product_type_name,
                                        filename = filename,
                                        data_filename = data_filename)


# Add a useful alias
create_galaxy_population_priors_product = create_dpd_she_galaxy_population_priors
