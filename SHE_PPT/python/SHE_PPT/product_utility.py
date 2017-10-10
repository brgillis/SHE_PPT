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

import pickle

def save_xml_product(product, xml_file_name):
    with open(str(xml_file_name), "w") as f:
        f.write(product.toDOM().toprettyxml(encoding="utf-8").decode("utf-8"))

def read_xml_product(xml_file_name):
    # Read the xml file as a string
    with open(str(xml_file_name), "r") as f:
        xml_string = f.read()

    # Create a new SHE product instance using the SHE data product dictionary
    product = she_dpd.CreateFromDocument(xml_string)

    return product

def save_pickled_product(product, pickled_file_name):
    with open(str(pickled_file_name), "wb") as f:
        pickle.dump(product,f)

def read_pickled_product(pickled_file_name):
    with open(str(pickled_file_name), "rb") as f:
        product = pickle.load(f)
    return product
