""" @file file_io.py

    Created 29 Aug 2017

    Various functions for input/output
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

import json
import os
from os.path import join, isfile
import pickle
import time
from xml.sax._exceptions import SAXParseException

import EuclidDmBindings.dpd.she_stub as she_dpd
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.utility import time_to_timestamp
from astropy.io import fits

logger = getLogger(mv.logger_name)

type_name_maxlen = 41
instance_id_maxlen = 55

def get_allowed_filename(type_name, instance_id, extension = ".fits", release = "00.00"):
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
                         str(type_name_maxlen) + " characters.")
    if len(instance_id) > instance_id_maxlen:
        raise ValueError("instance_id (" + type_name + ") is too long. Maximum length is " +
                         str(instance_id_maxlen) + " characters.")

    # Check that $release is in the correct format
    good_release = True
    if len(release) != 5 or release[2] != ".":
        good_release = False
    # Check each value is an integer 0-9
    if good_release:
        for i in (0, 1, 3, 4):
            try:
                _ = int(release[i])
            except ValueError:
                good_release = False

    if not good_release:
        raise ValueError("release (" + release + ") is in incorrect format. Required format is " +
                         "XX.XX, where each X is 0-9.")

    tnow = time.gmtime()

    creation_date = time_to_timestamp(tnow)

    filename = "EUC_SHE_" + type_name + "_" + instance_id + "_" + creation_date + "_" + release + extension

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

    with open(listfile_name, 'r') as f:
        listobject = json.load(f)
        if len(listobject) == 0:
            return listobject
        if isinstance(listobject[0], list):
            return [tuple(el) for el in listobject]
        else:
            return listobject

def replace_in_file(input_filename, output_filename, input_string, output_string):
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

def replace_multiple_in_file(input_filename, output_filename, input_strings, output_strings):
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

def write_xml_product(product, xml_file_name):
    try:
        with open(str(xml_file_name), "w") as f:
            f.write(product.toDOM().toprettyxml(encoding = "utf-8").decode("utf-8"))
    except AttributeError as e:
        if not "object has no attribute 'toDOM'" in str(e):
            raise
        logger.warn("XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, xml_file_name)

def read_xml_product(xml_file_name, allow_pickled=True):

    # Read the xml file as a string
    try:
        with open(str(xml_file_name), "r") as f:
            xml_string = f.read()
    except UnicodeDecodeError as _e:
        # Not actually saved as xml
        if allow_pickled:
            # Revert to pickled product
            return read_pickled_product(xml_file_name)
        else:
            raise

    # Create a new product instance using the proper data product dictionary
    product = she_dpd.CreateFromDocument(xml_string)

    return product

def write_pickled_product(product, pickled_file_name):

    with open(str(pickled_file_name), "wb") as f:
        pickle.dump(product, f)

def read_pickled_product(pickled_file_name):

    with open(str(pickled_file_name), "rb") as f:
        product = pickle.load(f)

    return product

def append_hdu(filename, hdu):

    f = fits.open(filename, mode = 'append')
    try:
        f.append(hdu)
    finally:
        f.close()

def find_file_in_path(filename, path):
    """
        Searches through a colon-separated path for a file and returns the qualified name of it if found,
        None otherwise.
    """

    colon_separated_path = path.split(":")

    qualified_filename = None

    for test_path in colon_separated_path:

        test_filename = join(test_path, filename)

        if isfile(test_filename):
            qualified_filename = test_filename
            break

    if qualified_filename is None:
        raise RuntimeError("File " + str(filename) + " could not be found in path " + str(path) + ".")

    return qualified_filename

def find_aux_file(filename):
    """
        Searches the auxiliary directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_AUX_PATH'])

def find_conf_file(filename):
    """
        Searches the conf directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_CONF_PATH'])

def find_file(filename, path = None):
    """
        Locates a file based on the presence/absence of an AUX/ or CONF/ prefix, searching in the aux or conf
        directories respectively for it, or else the work directory if supplied.
    """

    if filename[0:4] == "AUX/":
        return find_aux_file(filename[4:])
    elif filename[0:5] == "CONF/":
        return find_conf_file(filename[5:])
    elif path is not None:
        return find_file_in_path(filename, path)
    else:
        raise ValueError("path must be supplied if filename doesn't start with AUX/ or CONF/")

def first_in_path(path):
    """
        Gets the first directory listed in the path.
    """

    return path.split(":")[0]

def first_writable_in_path(path):
    """
        Gets the first directory listed in the path which we have write access for.
    """

    colon_separated_path = path.split(":")

    first_writable_dir = None

    for test_path in colon_separated_path:

        if os.access(test_path, os.W_OK):
            first_writable_dir = test_path
            break

    return first_writable_dir

def get_data_filename(filename,workdir="."):
    """ Given the unqualified name of a file and the work directory, determine if it's an XML data
        product or not, and get the filename of its DataContainer if so; otherwise, just return
        the input filename. In either case, the unqualified filename is returned.
        
        This script is intended to help smooth the transition from using raw data files as
        input/output to data products.
    """
    
    # First, see if we can open this as an XML data product
    try:
        prod = read_xml_product(filename,allow_pickled=False)
        
        # If we get here, it is indeed an XML data product. Has it been monkey-patched
        # to have a get_filename method?
        
        if hasattr(prod, "get_filename"):
            return prod.get_filename()
        elif hasattr(prod, "get_data_filename"): # or a get_data_filename method?
            return prod.get_data_filename()
        
        # Check if the filename exists in the default location
        try:
            return prod.Data.DataStorage.DataContainer.FileName
        except AttributeError as _e:
            raise AttributeError("Data product does not have filename stored in the expected " +
                                 "location (self.Data.DataStorage.DataContainer.FileName. " +
                                 "In order to use get_data_filename with this product, the " +
                                 "product's class must be monkey-patched to have a get_filename " +
                                 "or get_data_filename method.")
        
    except UnicodeDecodeError as _e:
        # Not an XML file - so presumably it's a raw data file; return the input filename
        return filename
    except SAXParseException as _e:
        # Not an XML file - so presumably it's a raw data file; return the input filename
        return filename


