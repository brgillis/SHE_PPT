""" @file mdb.py

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

from from MdbUtils.Mdb import Mdb as _Mdb

_initialised = False
_not_inited_exception = RuntimeError("")

mdb = {}

def init(mdb_files):
    
    full_dict = _Mdb(mdb_files).get_all()
    
    mdb.update(full_dict)
    
    _initialised = True
    
    return

def get_mdb_value(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Value']

def get_mdb_description(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Description']

def get_mdb_source(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Source']

def get_mdb_release(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Release']

def get_mdb_expression(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Expression']

def get_mdb_unit(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['unit']

def get_mdb_title(key):
    
    if not _initialised:
        raise _not_inited_exception
    
    return mdb[key]['Title']

