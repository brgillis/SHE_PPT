""" @file mosaic_product_test.py

    Created 10 Oct 2017

    Unit tests for the mosaic data product.
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

from astropy.io import fits
import numpy as np
import pytest

from SHE_PPT import mosaic_product as prod
from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT import detector as dtc
import SHE_PPT.magic_values as mv

class TestMosaicProduct(object):
    """A collection of tests for the mosaic data product.

    """ 

    def test_validation(self):
        
        # Create the product
        product = prod.create_dpd_mer_mosaic(instrument_name="VIS",
                                              filter="VIS",
                                              wcs_params=None,
                                              zeropoint=0,
                                              data_filename="junk",)

        # Check that it validates the schema
        product.validateBinding()
        
        pass

    def test_xml_writing_and_reading(self, tmpdir):
        
        prod.init()
        
        # Create the product
        product = prod.create_dpd_mer_mosaic(instrument_name="VIS",
                                              filter="VIS",
                                              wcs_params=None,
                                              zeropoint=0,
                                              data_filename="junk",)

        # Change the fits file names
        data_filename = "test_file_data.fits" 
        product.set_data_filename(data_filename)
        rms_filename = "test_file_rms.fits" 
        product.set_rms_filename(rms_filename)
        flag_filename = "test_file_flag.fits" 
        product.set_flag_filename(flag_filename)
        psf_model_filename = "test_file_psf_model.fits" 
        product.set_psf_model_filename(psf_model_filename)

        # Save the product in an xml file
        filename = tmpdir.join("mer_mosaic.xml")
        listfilename = tmpdir.join("mer_mosaic.json")
        write_pickled_product(product, filename, listfilename)

        # Read back the xml file
        loaded_product = read_pickled_product(filename, listfilename)

        # Check that it's the same
        assert loaded_product.get_data_filename() == data_filename
        assert loaded_product.get_rms_filename() == rms_filename
        assert loaded_product.get_flag_filename() == flag_filename
        assert loaded_product.get_psf_model_filename() == psf_model_filename
        
        pass 

    def test_pickle_writing_and_reading(self, tmpdir):
        
        prod.init()
        
        # Create the product
        product = prod.create_dpd_mer_mosaic(instrument_name="VIS",
                                              filter="VIS",
                                              wcs_params=None,
                                              zeropoint=0,
                                              data_filename="junk",)

        # Change the fits file names
        data_filename = "test_file_data.fits" 
        product.set_data_filename(data_filename)
        rms_filename = "test_file_rms.fits" 
        product.set_rms_filename(rms_filename)
        flag_filename = "test_file_flag.fits" 
        product.set_flag_filename(flag_filename)
        psf_model_filename = "test_file_psf_model.fits" 
        product.set_psf_model_filename(psf_model_filename)

        # Save the product in a pickled file
        filename = tmpdir.join("mer_mosaic.bin")
        listfilename = tmpdir.join("mer_mosaic.json")
        write_pickled_product(product, filename, listfilename)

        # Read back the pickled file
        loaded_product = read_pickled_product(filename, listfilename)

        # Check that it's the same
        assert loaded_product.get_data_filename() == data_filename
        assert loaded_product.get_rms_filename() == rms_filename
        assert loaded_product.get_flag_filename() == flag_filename
        assert loaded_product.get_psf_model_filename() == psf_model_filename
        
        pass
    
    def test_load_mosaic_hdu(self, tmpdir):
        
        prod.init()
        
        # Create and save the product with a junk filename first
        product = prod.create_dpd_mer_mosaic(instrument_name="VIS",
                                              filter="VIS",
                                              wcs_params=None,
                                              zeropoint=0,
                                              data_filename="junk",)

        filename = str(tmpdir.join("mer_mosaic.bin"))
        listfilename = str(tmpdir.join("mer_mosaic.json"))
        write_pickled_product(product, filename, listfilename)
        
        # Check that it raises a ValueError when expected
        
        with pytest.raises(IOError):
            mosaic_hdu = prod.load_mosaic_hdu(filename="bad_filename.junk",
                                              listfile_filename=listfilename)
        with pytest.raises(IOError):
            mosaic_hdu = prod.load_mosaic_hdu(filename=filename,
                                              listfile_filename="bad_filename.junk")
        with pytest.raises(IOError):
            mosaic_hdu = prod.load_mosaic_hdu(filename=filename,
                                              listfile_filename=listfilename)
            
        # Now save it pointing to an existing fits file and check that it works
        
        test_array = np.zeros((10,20))
        test_array[0,0] = 1
        detector_x = 2
        detector_y = 3
        
        phdu = fits.PrimaryHDU(data=test_array,
                               header=fits.header.Header((("EXTNAME",dtc.get_id_string(detector_x,detector_y)
                                                           +"."+mv.segmentation_tag),)))
        
        data_filename = str(tmpdir.join("mosaic_data.fits"))
        phdu.writeto(data_filename, clobber=True)
        
        product.set_data_filename(data_filename)
        write_pickled_product(product, filename, listfilename)
        
        loaded_hdu = prod.load_mosaic_hdu(filename=filename,
                                          listfile_filename=listfilename,
                                          detector_x=detector_x,
                                          detector_y=detector_y)
        
        assert (loaded_hdu.data == test_array).all()
        
        # Now test with a multi-HDU data image
        
        test_array2 = np.zeros((20,40))
        test_array2[0,0] = 2
        detector_x2 = 4
        detector_y2 = 5
        
        hdu2 = fits.ImageHDU(data=test_array2,
                             header=fits.header.Header((("EXTNAME",dtc.get_id_string(detector_x2,detector_y2)
                                                         +"."+mv.segmentation_tag),)))
        
        hdulist = fits.HDUList([phdu,hdu2])
        hdulist.writeto(data_filename, clobber=True)
        
        loaded_hdu1 = prod.load_mosaic_hdu(filename=filename,
                                           listfile_filename=listfilename,
                                           hdu=0)
        
        assert (loaded_hdu1.data == test_array).all()
        
        loaded_hdu2 = prod.load_mosaic_hdu(filename=filename,
                                           listfile_filename=listfilename,
                                           hdu=1)
        
        assert (loaded_hdu2.data == test_array2).all()
        
        loaded_hdu1 = prod.load_mosaic_hdu(filename=filename,
                                           listfile_filename=listfilename,
                                           detector_x=detector_x,
                                           detector_y=detector_y)
        
        assert (loaded_hdu1.data == test_array).all()
        
        loaded_hdu2 = prod.load_mosaic_hdu(filename=filename,
                                           listfile_filename=listfilename,
                                           detector_x=detector_x2,
                                           detector_y=detector_y2)
        
        assert (loaded_hdu2.data == test_array2).all()
        
        pass
        