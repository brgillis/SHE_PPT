""" @file full_mdb.py

    Created 15 Feb 2018

    Functions to get needed information from the MDB.
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

from MdbUtils.Mdb import Mdb as _Mdb

from SHE_PPT.file_io import find_file

_not_inited_exception = RuntimeError("mdb module must be initialised with MDB xml object before use.")

full_mdb = {}

def init(mdb_files,path=None):
    """Initialises module by loading MDB data from file(s).
    
    Arguments
    ---------
    mdb_files: string or list of strings
        MDB filename(s)
    
    Return
    ------
    None
    
    """
    
    # Resolve the filename (or list of files) to find their qualified paths
    if isinstance(mdb_files, str):
        qualified_mdb_files = find_file(mdb_files,path)
    elif isinstance(mdb_files, list) or isinstance(object, tuple):
        qualified_mdb_files = []
        for mdb_file in mdb_files:
            qualified_mdb_file = find_file(mdb_file,path)
            qualified_mdb_files.append(qualified_mdb_file)
        
    # Get and store the data in a dictionary
    full_dict = _Mdb(qualified_mdb_files).get_all()
    full_mdb.clear()
    full_mdb.update(full_dict)
    
    return

def reset():
    """Resets the MDB dictionary.
    
    Arguments
    ---------
    None
    
    Return
    ------
    None
    """
    
    full_mdb.clear()

def get_mdb_value(key):
    """Gets an item's value from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    value: (type dependent on key)
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['Value']

def get_mdb_description(key):
    """Gets an item's description from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    description: str
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['Description']

def get_mdb_source(key):
    """Gets an item's source from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    source: str
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['Source']

def get_mdb_release(key):
    """Gets an item's release version from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    release: str
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['Release']

def get_mdb_expression(key):
    """Gets an item's expression from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    expression: str
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['Expression']

def get_mdb_unit(key):
    """Gets an item's unit from the MDB from its key (aka title).
    
    Arguments
    ---------
    key: str
        key for this item in the MDB
    
    Return
    ------
    unit: str
    
    """
    
    if len(full_mdb)==0:
        raise _not_inited_exception
    
    return full_mdb[key]['unit']

