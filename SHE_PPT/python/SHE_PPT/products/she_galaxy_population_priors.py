""" @file she_galaxy_population_priors.py

    Created 17 Nov 2017

    Functions to create and output a galaxy_population_priors priors data product.

    Origin: OU-SHE - Input to Calibration pipeline; needs to be implemented in data model.
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

__updated__ = "2020-06-30"

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.galaxypopulationpriors_stub import dpdSheGalaxyPopulationPriors

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_galaxy_population_priors.xml"


def init():
    """
        ?????
    """

    binding_class = dpdSheGalaxyPopulationPriors

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename
    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True



def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorageList[0]")


def __get_data_filename(self):
    return get_data_filename_from_product(self, "DataStorageList[0]")


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename(), ]

    return all_filenames


def create_dpd_she_galaxy_population_priors(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_galaxy_population_priors = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_galaxy_population_priors.Header = HeaderProvider.create_generic_header("SHE")

    if filename:
        __set_filename(dpd_galaxy_population_priors, filename)

    return dpd_she_galaxy_population_priors


# Add a useful alias
create_galaxy_population_priors_product = create_dpd_she_galaxy_population_priors


def create_she_galaxy_population_priors(filename=None):
    """
        @TODO fill in docstring
    """

    she_galaxy_population_priors = SheGalaxyPopulationPriors()

    she_galaxy_population_priors.format = "she.galaxyPopulationPriors"
    she_galaxy_population_priors.version = "8.0"

    she_galaxy_population_priors.DataContainer = DataContainer()
    she_galaxy_population_priors.DataContainer.FileName = filename
    she_galaxy_population_priors.DataContainer.filestatus = "PROPOSED"


    return she_galaxy_population_priors
