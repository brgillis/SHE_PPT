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

""" @file detector.py

    Created 8 Nov 2017

    Magic values and functions related to detector IDs in FITS headers.
"""

import numpy as np

__all__ = ["get_id_string","id_strings"]

id_template = "CCDID $X-$Y"

def get_id_string(x,y):
    """Gets a detector ID string for a given x/y position.
    
    Parameters
    ----------
    x : int
        Detector position in the x dimension. Accepted values: 1-6
    y : int
        idem for y
    """
    
    # Check for valid values
    for v in x,y:
        if not isintance( v, int ):
            raise TypeError("Values passed to get_id_string must be int type: " + str(v))
        elif (v<1) or (v>6):
            raise ValueError("Invalid value passed to get_id_string: " + str(v))
        
    return _get_id_string(x,y)

def _get_id_string(x,y):
    """Gets a detector ID string for a given x/y position, without checking
       for valid values.
    
    Parameters
    ----------
    x : int
        Detector position in the x dimension. Accepted values: 1-6
    y : int
        idem for y
    """
    
    return id_template.replace("$X",str(int(x))).replace("$Y",str(int(y)))

# id_strings is a zero-indexed array of all possible id strings, useful for iteration
id_strings = np.fromfunction(np.vectorize(_get_id_string), (7,7))[1:,1:]