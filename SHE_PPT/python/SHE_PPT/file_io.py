""" @file io.py

    Created 15 Sep 2015

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

def get_allowed_filename( type_name, instance_id, extension=".fits", release_date = "00.00"):
    
    tnow = time.gmtime()
    
    creation_date = (str(tnow.tm_year) + str(tnow.tm_mon) + str(tnow.tm_mday) + "T" +
                     str(tnow.tm_hour) + str(tnow.tm_min) + str(tnow.tm_sec)+ ".0Z")
    
    filename = "EUC_SHE_CTE-"+type_name+"_"+instance_id+"_"+creation_date+"_"+release_date+extension
    
    return filename

def write_listfile(listfile_name, filenames):
    """
        @brief Writes a listfile in json format.
        
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

def replace_in_file(input_filename,output_filename,input_string,output_string):
    """ Replaces every occurence of $input_string in $input_filename with $output_string
        and prints the results to $output_filename.
        
        Requires: input_filename <string>
                  output_filename <string>
                  input_string <string>
                  output_string <string>
                  
        Returns: None
        Side-effects: $output_filename is created/overwritten
    """
    
    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                fout.write(line.replace(input_string, output_string))

def replace_multiple_in_file(input_filename,output_filename,input_strings,output_strings):
    """ Replaces every occurence of an input_string in input_filename with the corresponding
        output string and prints the results to $output_filename.
        
        Requires: input_filename <string>
                  output_filename <string>
                  input_strings <iterable of strings>
                  output_strings <iterable of strings>
                  
        Returns: None
        Side-effects: $output_filename is created/overwritten
    """
    
    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                new_line = line
                for input_string, output_string in zip(input_strings, output_strings):
                    new_line = new_line.replace(input_string, output_string)
                fout.write(new_line)
