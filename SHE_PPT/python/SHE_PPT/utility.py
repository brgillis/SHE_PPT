""" @file utility.py

    Created 25 Aug, 2017

    Miscellaneous utility functions

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

import hashlib

def hash_any(obj,max_length=None):
    """
        @brief Hashes any immutable object into a hex string of a given length. Unlike hash_any(),
               will be consistent in Python 3.0.
               
        @param obj
        
        @param max_length <int> Maximum length of hex string to return
        
        @return hash <str>
    """
    
    full_hash = hashlib.sha256(repr(obj)).hexdigest()
    
    if max_length is None or len(full_hash)<max_length:
        return full_hash
    else:
        return full_hash[-max_length:]
    