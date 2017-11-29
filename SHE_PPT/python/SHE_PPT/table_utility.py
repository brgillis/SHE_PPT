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
from astropy.io import fits
import numpy as np

def get_comments(table_format):
    """
        @brief Get the comments for the table format.
        
        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return zip(*table_format.comments.items())[1]

def get_dtypes(table_format):
    """
        @brief Get the data types for the table format, in the format for an astropy table.
        
        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return zip(*table_format.dtypes.items())[1]

def get_fits_dtypes(table_format):
    """
        @brief Get the data types for the table format, in the format for a fits table.
        
        @param table_format <...TableFormat>

        @return tuple<string>
    """

    return zip(*table_format.fits_dtypes.items())[1]

def get_lengths(table_format):
    """
        @brief Get the data lengths for the table format.
        
        @param table_format <...TableFormat>

        @return tuple<int>
    """

    return zip(*table_format.lengths.items())[1]

def is_in_format(table, table_format, strict=True):
    """
        @brief Checks if a table is in the given format
        
        @param table <astropy.table.Table>
        
        @param table_format <...TableFormat>
        
        @param strict <bool> If False, will allow the presence of extra columns
        
        @return <bool>
        
    """
    
    # Check that all required column names are present
    for colname in table_format.all_required:
        if colname not in table.colnames:
            return False
        
    # Check that no extra column names are present if strict==True, and each present column is of the right dtype
    for colname in table.colnames:
        if colname not in table_format.all:
            if strict:
                return False
        elif table.dtype[colname].newbyteorder('>') != np.dtype((table_format.dtypes[colname],
                                                               table_format.lengths[colname])):
            # Check if this is just an issue with lengths
            col_dtype = table.dtype[colname]
            if col_dtype.str[1]=='S':
                col_len = int(col_dtype.str[2:])
                if col_len<table_format.lengths[colname]:
                    # Length is shorter, likely due to saving as ascii. Allow it
                    pass
                else:
                    # Length is too long; so the format's invalid
                    return False
            else:
                return False
        
    # Check the metadata is correct
    if table.meta.keys() != table_format.m.all:
        return False
    
    # Check the format label is correct
    if table.meta[table_format.m.format] != table_format.m.table_format:
        return False
    
    # Check the version is correct
    if table.meta[table_format.m.version] != table_format.__version__:
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
    
    if output_format not in ('ascii','fits','both'):
        raise ValueError("Invalid output format: " + str(output_format))

    if ((output_format == 'ascii') or (output_format == 'both')):
        text_file_name = file_name_base + ".ecsv"
        otable.write(text_file_name, format='ascii.ecsv')

    if ((output_format == 'fits') or (output_format == 'both')):
        fits_file_name = file_name_base + ".fits"
        otable.write(fits_file_name, format='fits', overwrite=True)

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
    # Avoid circular imports
    from astropy.io.fits.connect import is_column_keyword, REMOVE_KEYWORDS
    from astropy.io.fits import BinTableHDU
    from astropy.units import Unit
    from astropy.units.format.fits import UnitScaleError

    # Not all tables with mixin columns are supported
    if table.has_mixin_columns:
        # Import is done here, in order to avoid it at build time as erfa is not
        # yet available then.
        from ...table.column import BaseColumn

        # Only those columns which are instances of BaseColumn or Quantity can be written
        unsupported_cols = table.columns.not_isinstance((BaseColumn, Quantity))
        if unsupported_cols:
            unsupported_names = [col.info.name for col in unsupported_cols]
            raise ValueError('cannot write table with mixin column(s) {0}'
                         .format(unsupported_names))

    # Create a new HDU object
    if table.masked:
        # float column's default mask value needs to be Nan
        for column in six.itervalues(table.columns):
            fill_value = column.get_fill_value()
            if column.dtype.kind == 'f' and np.allclose(fill_value, 1e20):
                column.set_fill_value(np.nan)

        table_hdu = BinTableHDU.from_columns(np.array(table.filled()))
        for col in table_hdu.columns:
            # Binary FITS tables support TNULL *only* for integer data columns
            # TODO: Determine a schema for handling non-integer masked columns
            # in FITS (if at all possible)
            int_formats = ('B', 'I', 'J', 'K')
            if not (col.format in int_formats or
                    col.format.p_format in int_formats):
                continue

            # The astype is necessary because if the string column is less
            # than one character, the fill value will be N/A by default which
            # is too long, and so no values will get masked.
            fill_value = table[col.name].get_fill_value()

            col.null = fill_value.astype(table[col.name].dtype)
    else:
        table_hdu = BinTableHDU.from_columns(np.array(table.filled()))

    # Set units for output HDU
    for col in table_hdu.columns:
        unit = table[col.name].unit
        if unit is not None:
            try:
                col.unit = unit.to_string(format='fits')
            except UnitScaleError:
                scale = unit.scale
                raise UnitScaleError(
                    "The column '{0}' could not be stored in FITS format "
                    "because it has a scale '({1})' that "
                    "is not recognized by the FITS standard. Either scale "
                    "the data or change the units.".format(col.name, str(scale)))
            except ValueError:
                warnings.warn(
                    "The unit '{0}' could not be saved to FITS format".format(
                        unit.to_string()), AstropyUserWarning)

            # Try creating a Unit to issue a warning if the unit is not FITS compliant
            Unit(col.unit, format='fits', parse_strict='warn')

    for key, value in table.meta.items():
        if is_column_keyword(key.upper()) or key.upper() in REMOVE_KEYWORDS:
            warnings.warn(
                "Meta-data keyword {0} will be ignored since it conflicts "
                "with a FITS reserved keyword".format(key), AstropyUserWarning)

        # Convert to FITS format
        if key == 'comments':
            key = 'comment'

        if isinstance(value, list):
            for item in value:
                try:
                    table_hdu.header.append((key, item))
                except ValueError:
                    warnings.warn(
                        "Attribute `{0}` of type {1} cannot be added to "
                        "FITS Header - skipping".format(key, type(value)),
                        AstropyUserWarning)
        else:
            try:
                table_hdu.header[key] = value
            except ValueError:
                warnings.warn(
                    "Attribute `{0}` of type {1} cannot be added to FITS "
                    "Header - skipping".format(key, type(value)),
                    AstropyUserWarning)
    return table_hdu