""" @file file_io.py

    Created 29 Aug 2017

    Various functions for input/output

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

try:
    import EuclidDmBindings.she.she_stub as she_dpd
    have_she_dpd = True
except ImportError as _e:
    have_she_dpd = False
    
from astropy.io import fits
    
import py
import pickle
import json
import time

type_name_maxlen = 41
instance_id_maxlen = 55

def get_allowed_filename( type_name, instance_id, extension=".fits", release = "00.00"):
    """
        @brief Gets a filename in the required Euclid format.
        
        @param type_name <string> Label for what type of object this is. Maximum 41 characters.
        
        @param instance_id <string> Label for the instance of this object. Maximum 55 characters.
        
        @param extension <string> File extension (eg. ".fits").
        
        @param release_date <string> Software/data release version, in format "XX.XX" where each
                                     X is a digit 0-9.
    """
    
    # Check that the labels aren't too long
    if len(type_name) > type_name_maxlen:
        raise ValueError("type_name (" + type_name + ") is too long. Maximum length is " + 
                         str(type_name_max_len) + " characters.")
    if len(instance_id) > instance_id_maxlen:
        raise ValueError("instance_id (" + type_name + ") is too long. Maximum length is " + 
                         str(instance_id_maxlen) + " characters.")
        
    # Check that $release is in the correct format
    good_release = True
    if len(release) != 5 or release[2] != ".":
        good_release = False
    # Check each value is an integer 0-9
    if good_release:
        for i in (0,1,3,4):
            try:
                _ = int(release[i])
            except ValueError:
                good_release = False
                
    if not good_release:
        raise ValueError("release (" + release + ") is in incorrect format. Required format is " +
                         "XX.XX, where each X is 0-9.")
    
    tnow = time.gmtime()
    
    creation_date = (str(tnow.tm_year) + str(tnow.tm_mon) + str(tnow.tm_mday) + "T" +
                     str(tnow.tm_hour) + str(tnow.tm_min) + str(tnow.tm_sec)+ ".0Z")
    
    filename = "EUC_SHE_"+type_name+"_"+instance_id+"_"+creation_date+"_"+release+extension
    
    return filename

def write_listfile(listfile_name, filenames):
    """
        @brief Writes a listfile in json format.
        
        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files
        
        @param listfile_name <str> Name of the listfile to be output.
        
        @param filenames <list<str>> List of filenames (or tuples of filenames) to be put in the listfile.
    """
    
    with open(listfile_name, 'w') as listfile:
        paths_json = json.dumps(filenames)
        listfile.write(paths_json)
        
    return

def read_listfile(listfile_name):
    """
        @brief Reads a json listfile and returns a list of filenames.
        
        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files
        
        @param listfile_name <str> Name of the listfile to be read.
        
        @return filenames <list<str>> List of filenames (or tuples of filenames) read in.
    """
    
    with open(listfile_name,'r') as f:
        listobject = json.load(f)
        if len(listobject) == 0:
            return listobject
        if isinstance(listobject[0], list):
            return [tuple(el) for el in listobject] 
        else:
            return listobject

def replace_in_file( input_filename, output_filename, input_string, output_string ):
    """ 
        @brief Replaces every occurence of $input_string in $input_filename with $output_string
               and prints the results to $output_filename.
        
        @param input_filename <string>
        
        @param output_filename <string>
        
        @param input_string <string>
        
        @param output_string <string>
    """
    
    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                fout.write(line.replace(input_string, output_string))

def replace_multiple_in_file( input_filename, output_filename, input_strings, output_strings ):
    """ 
        @brief Replaces every occurence of an input_string in input_filename with the corresponding
               output string and prints the results to $output_filename.
        
        @param input_filename <string>
        
        @param output_filename <string>
        
        @param input_strings <iterable of string>
        
        @param output_strings <iterable of string>
    """
    
    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                new_line = line
                for input_string, output_string in zip(input_strings, output_strings):
                    new_line = new_line.replace(input_string, output_string)
                fout.write(new_line)

def write_xml_product(product, xml_file_name, listfile_file_name=None):
    try:
        with open(str(xml_file_name), "w") as f:
            f.write(product.toDOM().toprettyxml(encoding="utf-8").decode("utf-8"))
    except AttributeError as e:
        if not "instance has no attribute 'toDOM'" in str(e):
            raise
        print("WARNING: XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, xml_file_name, listfile_file_name)

def read_xml_product(xml_file_name, listfile_file_name=None):
    
    if have_she_dpd:
        
        # Read the xml file as a string
        with open(str(xml_file_name), "r") as f:
            xml_string = f.read()
    
        # Create a new SHE product instance using the SHE data product dictionary
        product = she_dpd.CreateFromDocument(xml_string)
        
    else:
        # Try reading it as a pickled product, since that's probable what it is #FIXME
        product = read_pickled_product(xml_file_name, listfile_file_name)

    return product

def write_pickled_product(product, pickled_file_name, listfile_file_name=None):
    
    if not hasattr(product,"has_files"):
        raise ValueError("Associated init() must be called for a data product before write_pickled_product can be used.")
    
    if product.has_files:
        if listfile_file_name is None:
            raise ValueError("listfile_file_name is required for products that point to files.")
        else:
            write_listfile(str(listfile_file_name), product.get_all_filenames())
    elif listfile_file_name is not None:
        raise ValueError("listfile_file_name cannot be supplied for products that do not point to files")
    
    with open(str(pickled_file_name), "wb") as f:
        pickle.dump(product,f)

def read_pickled_product(pickled_file_name, filenames=None):
    
    with open(str(pickled_file_name), "rb") as f:
        product = pickle.load(f)
    
    if not hasattr(product,"has_files"):
        raise ValueError("Associated init() must be called for a data product before read_pickled_product can be used.")
    
    if product.has_files:
        if filenames is None:
            raise ValueError("'filenames' argument is required for products that point to files.")
        else:
            if isinstance(filenames, str):
                listfile_filenames = read_listfile(filenames)
            elif isinstance(filenames, py.path.local):
                listfile_filenames = read_listfile(str(filenames))
            else:
                listfile_filenames = filenames
    elif filenames is not None:
        raise ValueError("filenames cannot be supplied for products that do not point to files")
    else:
        listfile_filenames = []
        
    # Check that the files in the listfile match those in the product
    if listfile_filenames != product.get_all_filenames():
        raise Exception("Filenames in " + listfile_filenames + "do not match those in " + pickled_file_name + ".")
    
    return product
    
def append_hdu(filename, hdu):
    
    f = fits.open(filename, mode='append')
    try:
        f.append(hdu)
    finally:
        f.close()
