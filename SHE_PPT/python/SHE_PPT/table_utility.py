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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2020-06-09"

from astropy.io.fits import table_to_hdu as astropy_table_to_hdu
from astropy.table import Column

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.utility import run_only_once
import numpy as np

logger = getLogger(mv.logger_name)


def is_in_format(table, table_format, ignore_metadata=False, strict=True, verbose=False,
                 fix_bool=True):
    """
        @brief Checks if a table is in the given format

        @param table <astropy.table.Table>

        @param table_format <...TableFormat>

        @param ignore_metadata <bool> If True, will not do any comparisons on metadata (useful if loading a table
                   provided by another PF)

        @param strict <bool> If False, will allow the presence of extra columns

        @param verbose <bool> If True, will specify reasons tables fail the format check.

        @param fix_bool <bool> If True, will fix any bool columns that were read incorrectly as strings

        @return <bool>

    """

    # Check that all required column names are present
    for colname in table_format.all_required:
        if colname not in table.colnames:
            if verbose:
                logger.info(
                    "Table not in correct format due to absence of required column: " + colname)
            return False

    # Check that no extra column names are present if strict==True, and each
    # present column is of the right dtype
    for colname in table.colnames:

        col_dtype = table.dtype[colname].newbyteorder('>')
        try:
            ex_dtype = np.dtype((table_format.dtypes[colname], (table_format.lengths[colname],))).newbyteorder('>')
        except Exception:
            pass

        if colname not in table_format.all:
            if strict:
                logger.info(
                    "Table not in correct format due to presence of extra column: " + colname)
                return False
            else:
                if verbose:
                    logger.info("Table not in correct format due to presence of extra column: " + colname + ", but not failing " +
                                "check due to strict==False.")

        elif col_dtype != ex_dtype:

            # Check if this is just an issue with lengths
            if col_dtype.str[1] == 'U' and ex_dtype.str[1] == 'U':
                col_len = int(col_dtype.str[2:])
                if col_len < table_format.lengths[colname]:
                    # Length is shorter, likely due to saving as ascii. Allow it
                    pass
                elif col_len > table_format.lengths[colname]:
                    if verbose:
                        logger.info("Table not in correct format due to wrong length for column '" + colname + "'\n" +
                                    "Expected: " + str(table_format.lengths[colname]) + "\n" +
                                    "Got: " + str(col_len))
                    if strict:
                        return False
                    elif verbose:
                        logger.info("Not failing check due to strict==False.")
            # Is it an issue with a bool column being read as a string?
            elif col_dtype.str[1] == 'U' and ex_dtype.str == '|b1':
                if fix_bool:
                    col = Column(data=np.empty_like(table[colname].data, dtype=bool))
                    for i in range(len(col)):
                        col[i] = (table[colname] == "True" or table[colname] == "true" or table[colname] == "1")
                    table.replace_column(colname, col)
                else:
                    if verbose:
                        logger.info("Table not in correct format due to wrong type for column '" + colname + "'\n" +
                                    "Expected: " + str(np.dtype((table_format.dtypes[colname],
                                                                 (table_format.lengths[colname],))).newbyteorder('>')) + "\n" +
                                    "Got: " + str(table.dtype[colname].newbyteorder('>')))
                    return False
            # Is it an issue with int or float size?
            elif strict == False:
                if col_dtype.str[1] == ex_dtype.str[1] and (col_dtype.str[1] == 'i' or col_dtype.str[1] == 'f'):
                    pass
            else:
                if verbose:
                    logger.info("Table not in correct format due to wrong type for column '" + colname + "'\n" +
                                "Expected: " + str(np.dtype((table_format.dtypes[colname],
                                                             (table_format.lengths[colname],))).newbyteorder('>')) + "\n" +
                                "Got: " + str(table.dtype[colname].newbyteorder('>')))
                return False

    if not ignore_metadata:
        # Check the metadata is correct
        if list(table.meta.keys()) != table_format.m.all:
            if verbose:
                logger.info("Table not in correct format due to wrong metadata keys.\n" +
                            "Expected: " + str(table_format.m.all) + "\n" +
                            "Got: " + str(list(table.meta.keys())))
            return False

        # Check the format label is correct
        if table.meta[table_format.m.format] != table_format.m.table_format:
            if verbose:
                logger.info("Table not in correct format due to wrong table format label.\n" +
                            "Expected: " + table_format.m.table_format + "\n" +
                            "Got: " + table.meta[table_format.m.format])
            return False

        # Check the version is correct
        if table.meta[table_format.m.version] != table_format.__version__:
            if verbose:
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

    table.add_row(vals=kwargs)
    return


def output_tables(otable, file_name_base, output_format):

    if output_format not in ('ascii', 'fits', 'both'):
        raise ValueError("Invalid output format: " + str(output_format))

    if ((output_format == 'ascii') or (output_format == 'both')):
        text_file_name = file_name_base + ".ecsv"
        otable.write(text_file_name, format='ascii.ecsv')

    if ((output_format == 'fits') or (output_format == 'both')):
        fits_file_name = file_name_base + ".fits"
        otable.write(fits_file_name, format='fits', overwrite=True)

    return


@run_only_once
def warn_deprecated_table_to_hdu():
    logger.warning("SHE_PPT.table_to_hdu is now deprecated. Please use astropy.io.fits.table_to_hdu instead")


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
    warn_deprecated_table_to_hdu()
    return astropy_table_to_hdu(table)
