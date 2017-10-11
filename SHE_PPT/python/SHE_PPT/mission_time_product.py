""" @file mission_time_product.py

    Created 10 Oct 2017

    Functions to create and output an mission_time data product.

    ---------------------------------------------------------------------

    Copyright (C) 2012-2020 Euclid Science Ground Segment      
       
    This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General    
    Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)    
    any later version.    
       
    This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied    
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more    
    details.    
       
    You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to    
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

import pickle

def init():
    """
        Adds some extra functionality to the DpdSheMissionTime product
    """
    
    # binding_class = she_dpd.DpdSheMissionTimeProduct # @FIXME
    binding_class = DpdSheMissionTimeProduct

    # Add needed methods here
    pass

class DpdSheMissionTimeProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheMissionTimeProduct: # @FIXME
    def __init__(self):
        pass

def create_dpd_she_mission_time():
    """
        @TODO fill in docstring
    """
    
    # dpd_she_mission_time = she_dpd.DpdSheMissionTimeProduct() # @FIXME
    dpd_she_mission_time = DpdSheMissionTimeProduct()
    
    # dpd_she_mission_time.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_mission_time.Header = "SHE"
    
    dpd_she_mission_time.Data = create_she_mission_time()
    
    return dpd_she_mission_time

def create_she_mission_time():
    """
        @TODO fill in docstring
    """
    
    # she_mission_time = she_dpd.SheMissionTimeProduct() # @FIXME
    she_mission_time = SheMissionTimeProduct()
    
    return she_mission_time
