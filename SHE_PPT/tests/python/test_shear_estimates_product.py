""" @file test_shear_estimates_product.py

    Created 9 Oct 2017

    Unit tests for the shear estimates data product.

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
"""

from SHE_PPT import shear_estimates_product as prod
from SHE_PPT.product_utility import (read_xml_product, write_xml_product,
                                     read_pickled_product, write_pickled_product)

class TestShearEstimatesProduct(object):
    """A collection of tests for the shear estimates data product.

    """ 

    def test_validation(self):
        
        # Create the product
        product = prod.create_dpd_shear_estimates()

        # Check that it validates the schema
        product.validateBinding()
        
        pass

    def test_xml_writing_and_reading(self, tmpdir):
        
        prod.init()
        
        # Create the product
        product = prod.create_dpd_shear_estimates()

        # Change the BFDShearEstimates fits file name
        fits_file_name = "test_file.fits" 
        product.set_BFD_file_name(fits_file_name)

        # Save the product in an XML file
        file_name = tmpdir.join("she_shear_estimates.xml")
        write_xml_product(product, file_name)

        # Read back the XML file
        loaded_product = read_xml_product(file_name)

        # Check that the BFDShearEstimates fits file name coincides
        assert loaded_product.get_BFD_file_name() == fits_file_name
        
        pass

    def test_pickle_writing_and_reading(self, tmpdir):
        
        prod.init()
        
        # Create the product
        product = prod.create_dpd_shear_estimates()

        # Change the BFDShearEstimates fits file name
        fits_file_name = "test_file.fits" 
        product.set_BFD_file_name(fits_file_name)

        # Save the product in a pickled file
        file_name = tmpdir.join("she_shear_estimates.bin")
        write_pickled_product(product, file_name)

        # Read back the pickled file
        loaded_product = read_pickled_product(file_name)

        # Check that the BFDShearEstimates fits file name coincides
        assert loaded_product.get_BFD_file_name() == fits_file_name
        
        pass