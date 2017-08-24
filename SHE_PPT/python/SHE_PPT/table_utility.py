""" @file tables.py

    Created 21 Aug 2017

    Functions related to output of details and detections tables.

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

import subprocess
from astropy.io import fits
import numpy as np

def get_comments(table_format):
    """
        @brief Get the comments for the table format.

        @return tuple<string>
    """

    return zip(*table_format.comments.items())[1]

def get_dtypes(table_format):
    """
        @brief Get the data types for the table format, in the format for an astropy table.

        @return tuple<string>
    """

    return zip(*table_format.dtypes.items())[1]

def get_fits_dtypes(names_and_dtypes):
    """
        @brief Get the data types for the table format, in the format for a fits table.

        @return tuple<string>
    """

    return zip(*table_format.fits_dtypes.items())[1]

def is_in_format(table, table_format):
    """
        @brief Checks if a table is in the given format
        
        @param table <astropy.table.Table>
        
        @param table_format <...TableFormat>
        
        @return <bool>
        
    """
    
    # Check that the column names are correct
    if table.colnames != table_format.all:
        return False
    
    # Check the data types are correct
    desired_dtypes = get_dtypes(table_format)
    for i in range(len(table.colnames)):
        if table.dtype[i] != np.dtype(desired_dtypes):
            return False
        
    # Check the metadata is correct
    if table.meta.keys() != table_format.m.all:
        return False
    
    # Check the version is correct
    if table.meta[table_format.m.version] != table.__version__:
        return False
    
    return True

def add_row(table, **kwargs):
    """ Add a row to a table by packing the keyword arguments and passing them as a
        dict to its 'vals' keyword argument.

        Requires: table <astropy.tables.Table> (table to add the row to)
                  **kwargs <...> (one or more keyword arguments corresponding to columns
                                  in the table)

        Returns: (nothing)

        Side-effects: Row is appended to end of table.
    """


    table.add_row(vals=kwargs)
    return

def output_tables(otable, file_name_base, table_tail, output_format):

    if ((output_format == 'ascii') or (output_format == 'both')):
        text_file_name = file_name_base + table_tail + ".dat"
        otable.write(text_file_name, format='ascii.ecsv')

    if ((output_format == 'fits') or (output_format == 'both')):
        fits_file_name = file_name_base + table_tail + ".fits"
        otable.write(fits_file_name, format='fits', overwrite=True)

    return

def output_table_as_fits(table, filename, table_format, header=None):
    """
        @brief Output an astropy table as a fits binary table.

        @param table <astropy.table.Table> Table to be output
        @param filename <string> Name of file to output this table to
        @param table_format <...TableFormat> Table format of the table
        @param header <dict<string>> Values to add to the output table's header

        Returns: (nothing)

        Side-effects: Overwrites the file at 'filename'

    """
    
    if header is None:
        header = {}
        
    fits_cols = []
    for name in table_format.all:
        fits_cols.append(fits.Column(name=name,
                                     format=table_format.dtype[name],
                                     array=table[name]))

    # Set up the binary extension HDU with the correct data and filenames
    my_bin_hdu = fits.BinTableHDU.from_columns(fits_cols)

    # Set up the header
    
    if not table_format.version in header:
        my_bin_hdu.header[table_format.version] = table_format.__version__
    
    for item in header:
        my_bin_hdu.header[header] = header[item]
        

    # Output it to the desired filename
    my_bin_hdu.writeto(filename, clobber=True)

    return