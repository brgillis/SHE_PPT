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
