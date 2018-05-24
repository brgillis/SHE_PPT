""" @file tables.py

    Created 21 Aug 2017

    Functions related to output of details and detections tables.
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

import subprocess

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from astropy.io import fits
import numpy as np


logger = getLogger(mv.logger_name)

def get_comments(table_format):
    """
        @brief Get the comments for the table format.

        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return list(zip(*list(table_format.comments.items())))[1]

def get_dtypes(table_format):
    """
        @brief Get the data types for the table format, in the format for an astropy table.

        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return list(zip(*list(table_format.dtypes.items())))[1]

def get_fits_dtypes(table_format):
    """
        @brief Get the data types for the table format, in the format for a fits table.

        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return list(zip(*list(table_format.fits_dtypes.items())))[1]

def get_lengths(table_format):
    """
        @brief Get the data lengths for the table format.

        @param table_format <...TableFormat>

        @return tuple<int>
    """

    return list(zip(*list(table_format.lengths.items())))[1]

def is_in_format(table, table_format, ignore_metadata = False, strict = True):
    """
        @brief Checks if a table is in the given format

        @param table <astropy.table.Table>

        @param table_format <...TableFormat>

        @param ignore_metadata <bool> If True, will not do any comparisons on metadata (useful if loading a table
                   provided by another PF)

        @param strict <bool> If False, will allow the presence of extra columns

        @return <bool>

    """

    # Check that all required column names are present
    for colname in table_format.all_required:
        if colname not in table.colnames:
            logger.info("Table not in correct format due to absence of required column: " + colname)
            return False

    # Check that no extra column names are present if strict==True, and each present column is of the right dtype
    for colname in table.colnames:
        if colname not in table_format.all:
            if strict:
                logger.info("Table not in correct format due to presence of extra column: " + colname)
                return False
            else:
                logger.info("Table not in correct format due to presence of extra column: " + colname + ", but not failing " +
                            "check due to strict==False.")
        elif table.dtype[colname].newbyteorder('>') != np.dtype((table_format.dtypes[colname],
                                                               table_format.lengths[colname])).newbyteorder('>'):
            # Check if this is just an issue with lengths
            col_dtype = table.dtype[colname]
            if col_dtype.str[1] == 'U':
                col_len = int(col_dtype.str[2:])
                if col_len < table_format.lengths[colname]:
                    # Length is shorter, likely due to saving as ascii. Allow it
                    pass
                elif col_len > table_format.lengths[colname]:
                    logger.info("Table not in correct format due to wrong length for column '" + colname + "'\n" +
                                "Expected: " + str(table_format.lengths[colname]) + "\n" +
                                "Got: " + str(col_len))
                    return False
            else:
                logger.info("Table not in correct format due to wrong type for column '" + colname + "'\n" +
                            "Expected: " + str(np.dtype((table_format.dtypes[colname],
                                                               table_format.lengths[colname])).newbyteorder('>')) + "\n" +
                            "Got: " + str(table.dtype[colname].newbyteorder('>')))
                return False

    if not ignore_metadata:
        # Check the metadata is correct
        if list(table.meta.keys()) != table_format.m.all:
            logger.info("Table not in correct format due to wrong metadata keys.\n" +
                        "Expected: " + str(table_format.m.all) + "\n" +
                        "Got: " + str(list(table.meta.keys())))
            return False

        # Check the format label is correct
        if table.meta[table_format.m.format] != table_format.m.table_format:
            logger.info("Table not in correct format due to wrong table format label.\n" +
                        "Expected: " + table_format.m.table_format + "\n" +
                        "Got: " + table.meta[table_format.m.format])
            return False

        # Check the version is correct
        if table.meta[table_format.m.version] != table_format.__version__:
            logger.info("Table not in correct format due to wrong table format label.\n" +
                        "Expected: " + table_format.__version__ + "\n" +
                        "Got: " + table.meta[table_format.m.version])
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


    table.add_row(vals = kwargs)
    return

def output_tables(otable, file_name_base, output_format):

    if output_format not in ('ascii', 'fits', 'both'):
        raise ValueError("Invalid output format: " + str(output_format))

    if ((output_format == 'ascii') or (output_format == 'both')):
        text_file_name = file_name_base + ".ecsv"
        otable.write(text_file_name, format = 'ascii.ecsv')

    if ((output_format == 'fits') or (output_format == 'both')):
        fits_file_name = file_name_base + ".fits"
        otable.write(fits_file_name, format = 'fits', overwrite = True)

    return

def table_to_hdu(table):
    """
    Convert an `~astropy.table.Table` object to a FITS
    `~astropy.io.fits.BinTableHDU`. This is copied from the astropy source, since it
    isn't available in earlier versions.

    Parameters
    ----------
    table : astropy.table.Table
        The table to convert.

    Returns
    -------
    table_hdu : `~astropy.io.fits.BinTableHDU`
        The FITS binary table HDU.
    """
    
    logger.warn("Using deprecated table_to_hdu function. Use astropy.io.fits.table_to_hdu instead.")
    
    return fits.table_to_hdu(table)
