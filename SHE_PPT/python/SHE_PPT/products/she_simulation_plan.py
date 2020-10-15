""" @file she_simulation_plant.py

    Created 17 Nov 2017

    Functions to create and output a she_simulation_plan data product.
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

__updated__ = "2020-06-25"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME
from SHE_PPT.file_io import read_xml_product, find_aux_file
from SHE_PPT.product_utility import get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        ????

    """

    # binding_class = she_dpd.DpdSheSimulationPlan # @FIXME
    binding_class = DpdSheSimulationPlan

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

    all_filenames = []

    return all_filenames


class DpdSheSimulationPlan:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheSimulationPlan:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_simulation_plan(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_simulation_plan = she_dpd.DpdSheSimulationPlan() # FIXME
    dpd_she_simulation_plan = DpdSheSimulationPlan()

    # dpd_she_simulation_plan.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    dpd_she_simulation_plan.Header = "SHE"

    dpd_she_simulation_plan.Data = create_she_simulation_plan(filename)

    return dpd_she_simulation_plan


# Add a useful alias
create_simulation_plan_product = create_dpd_she_simulation_plan


def create_she_simulation_plan(filename=None):
    """
        @TODO fill in docstring
    """

    # she_simulation_plan = she_dpd.SheSimulationPlan() # @FIXME
    she_simulation_plan = SheSimulationPlan()

    she_simulation_plan.format = "UNDEFINED"
    she_simulation_plan.version = "0.0"

    she_simulation_plan.DataContainer = DataContainer()
    she_simulation_plan.DataContainer.FileName = filename
    she_simulation_plan.DataContainer.filestatus = "PROPOSED"

    return she_simulation_plan
