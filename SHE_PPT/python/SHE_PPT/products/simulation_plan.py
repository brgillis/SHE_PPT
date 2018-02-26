""" @file simulation_plan_product.py

    Created 17 Nov 2017

    Functions to create and output a simulation_plan data product.
    
    Origin: OU-SHE - Needs to be implemented in data model.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """
    
    # binding_class = she_dpd.DpdSheSimulationPlanProduct # @FIXME
    binding_class = DpdSheSimulationPlanProduct

    # Add the data file name methods
    
    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = False
    
    return

def __set_filename(self, filename):
    self.Data.DataContainer.FileName = filename

def __get_filename(self):
    return self.Data.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = []
    
    return all_filenames

class DpdSheSimulationPlanProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheSimulationPlanProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

def create_dpd_she_simulation_plan(filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_simulation_plan = she_dpd.DpdSheSimulationPlanProduct() # FIXME
    dpd_she_simulation_plan = DpdSheSimulationPlanProduct()
    
    # dpd_she_simulation_plan.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_simulation_plan.Header = "SHE"
    
    dpd_she_simulation_plan.Data = create_she_simulation_plan(filename)
    
    return dpd_she_simulation_plan

# Add a useful alias
create_simulation_plan_product = create_dpd_she_simulation_plan

def create_she_simulation_plan(filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_simulation_plan = she_dpd.SheSimulationPlanProduct() # @FIXME
    she_simulation_plan = SheSimulationPlanProduct()
    
    she_simulation_plan.format = "UNDEFINED"
    she_simulation_plan.version = "0.0"
    
    she_simulation_plan.DataContainer = DataContainer()
    she_simulation_plan.DataContainer.FileName = filename
    she_simulation_plan.DataContainer.filestatus = "PROPOSED"
    
    return she_simulation_plan
