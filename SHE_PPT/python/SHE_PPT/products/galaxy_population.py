""" @file galaxy_population_product.py

    Created 17 Nov 2017

    Functions to create and output a galaxy_population data product.

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

__updated__ = "2019-08-15"


# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import pickle
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        ?????
    """

    # binding_class = she_dpd.DpdSheGalaxyPopulationProduct # @FIXME
    binding_class = DpdSheGalaxyPopulationProduct

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename
    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename)


def __get_data_filename(self):
    return get_data_filename_from_product(self)


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename(), ]

    return all_filenames


class DpdSheGalaxyPopulationProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheGalaxyPopulationProduct:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_galaxy_population(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_galaxy_population = she_dpd.DpdSheGalaxyPopulationProduct() #
    # FIXME
    dpd_she_galaxy_population = DpdSheGalaxyPopulationProduct()

    # dpd_she_galaxy_population.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    dpd_she_galaxy_population.Header = "SHE"

    dpd_she_galaxy_population.Data = create_she_galaxy_population(filename)

    return dpd_she_galaxy_population


# Add a useful alias
create_galaxy_population_product = create_dpd_she_galaxy_population


def create_she_galaxy_population(filename=None):
    """
        @TODO fill in docstring
    """

    # she_galaxy_population = she_dpd.SheGalaxyPopulationProduct() # @FIXME
    she_galaxy_population = SheGalaxyPopulationProduct()

    she_galaxy_population.format = "UNDEFINED"
    she_galaxy_population.version = "0.0"

    she_galaxy_population.DataContainer = DataContainer()
    she_galaxy_population.DataContainer.FileName = filename
    she_galaxy_population.DataContainer.filestatus = "PROPOSED"

    return she_galaxy_population
