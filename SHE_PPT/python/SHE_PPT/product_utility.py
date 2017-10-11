""" @file product_utility.py

    Created 10 Oct 2017

    Utility functions for data products

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
try:
    import EuclidDmBindings.she.she_stub as she_dpd
    have_she_dpd = True
except ImportError as _e:
    have_she_dpd = False
    
import pickle

from SHE_PPT.file_io import write_listfile, read_listfile

def write_xml_product(product, xml_file_name):
    try:
        with open(str(xml_file_name), "w") as f:
            f.write(product.toDOM().toprettyxml(encoding="utf-8").decode("utf-8"))
    except AttributeError as e:
        if not "instance has no attribute 'toDOM'" in str(e):
            raise
        print("WARNING: XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, xml_file_name)

def read_xml_product(xml_file_name):
    
    if have_she_dpd:
        
        # Read the xml file as a string
        with open(str(xml_file_name), "r") as f:
            xml_string = f.read()
    
        # Create a new SHE product instance using the SHE data product dictionary
        product = she_dpd.CreateFromDocument(xml_string)
        
    else:
        # Try reading it as a pickled product, since that's probable what it is #FIXME
        product = read_pickled_product(xml_file_name)

    return product

def write_pickled_product(product, pickled_file_name, listfile_file_name=None):
    
    if not hasattr(product,"has_files"):
        raise ValueError("Associated init() must be called for a data product before write_pickled_product can be used.")
    
    if product.has_files:
        if listfile_file_name is None:
            raise ArgumentError("listfile_file_name is required for products that point to files.")
        else:
            write_listfile(listfile_file_name, product.get_all_filenames())
    elif listfile_file_name is not None:
        raise ArgumentError("listfile_file_name cannot be supplied for products that do not point to files")
    
    with open(str(pickled_file_name), "wb") as f:
        pickle.dump(product,f)

def read_pickled_product(pickled_file_name, listfile_file_name=None):
    
    if not hasattr(product,"has_files"):
        raise ValueError("Associated init() must be called for a data product before read_pickled_product can be used.")
    
    if product.has_files:
        if listfile_file_name is None:
            raise ArgumentError("listfile_file_name is required for products that point to files.")
        else:
            listfile_filenames = read_listfile(listfile_file_name)
    elif listfile_file_name is not None:
        raise ArgumentError("listfile_file_name cannot be supplied for products that do not point to files")
    
    with open(str(pickled_file_name), "rb") as f:
        product = pickle.load(f)
        
    # Check that the files in the listfile match those in the product
    if listfile_filenames != product.get_all_filenames():
        raise Exception("Filenames in " + listfile_file_name + "do not match those in " + pickled_file_name + ".")
    
    return product
