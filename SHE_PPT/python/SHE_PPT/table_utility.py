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

__updated__ = "2020-07-08"

from collections import OrderedDict

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

    # If the table format is a base class, ensure that strict=False
    if table_format.is_base and strict:
        logger.warn("Table format " + table_format.m.table_format + " is a base format. Enforcing strict=False.")
        strict = False

    # Check that all required column names are present
    if not table_format.is_base:
        # Simple check if not comparing to a base class
        for colname in table_format.all_required:
            if colname not in table.colnames:
                if verbose:
                    logger.info("Table not in correct format due to absence of required column: " + colname)
                return False
    else:
        # More careful check if comparing to a base class
        child_label = None
        for parent_colname in table_format.all_required:
            if child_label is None:
                found = False
                for child_colname in table.colnames:
                    if parent_colname == child_colname:
                        found = True
                        break
                    elif len(parent_colname) < len(child_colname) and child_colname[-len(parent_colname):] == parent_colname:
                        child_label = child_colname[0:-len(parent_colname)]
                        found = True
                        break
                if not found:
                    if verbose:
                        logger.info("Table not in correct format due to absence of required column: " + parent_colname)
                    return False
            else:
                # Once we've figured out what the child_label is, we can be a bit more efficient
                if parent_colname not in table.colnames and child_label + parent_colname not in table.columns:
                    if verbose:
                        logger.info("Table not in correct format due to absence of required column: " + colname)
                    return False

    # Check that no extra column names are present if strict==True, and each
    # present column is of the right dtype
    for colname in table.colnames:

        if table_format.is_base and child_label is not None and colname[:len(child_label)] == child_label:
            child_colname = colname
            parent_colname = colname[len(child_label):]
        else:
            child_colname = colname
            parent_colname = colname

        col_dtype = table.dtype[child_colname].newbyteorder('>')
        try:
            length = table_format.lengths[parent_colname]
            if length == 1:
                ex_dtype = np.dtype((table_format.dtypes[parent_colname])).newbyteorder('>')
            else:
                ex_dtype = np.dtype((table_format.dtypes[parent_colname], length)).newbyteorder('>')
        except Exception:
            ex_dtype = None

        if parent_colname not in table_format.all:
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
                if col_len < table_format.lengths[parent_colname]:
                    # Length is shorter, likely due to saving as ascii. Allow it
                    pass
                elif col_len > table_format.lengths[parent_colname]:
                    if verbose:
                        logger.info("Table not in correct format due to wrong length for column '" + parent_colname + "'\n" +
                                    "Expected: " + str(table_format.lengths[parent_colname]) + "\n" +
                                    "Got: " + str(col_len))
                    if strict:
                        return False
                    elif verbose:
                        logger.info("Not failing check due to strict==False.")
            # Is it an issue with a bool column being read as a string?
            elif col_dtype.str[1] == 'U' and ex_dtype.str == '|b1':
                if fix_bool:
                    col = Column(data=np.empty_like(table[child_colname].data, dtype=bool))
                    for i in range(len(col)):
                        col[i] = (table[child_colname] == "True" or table[child_colname] == "true" or table[child_colname] == "1")
                    table.replace_column(colname, col)
                else:
                    if verbose:
                        logger.info("Table not in correct format due to wrong type for column '" + parent_colname + "'\n" +
                                    "Expected: " + ex_dtype + "\n" +
                                    "Got: " + str(table.dtype[child_colname].newbyteorder('>')))
                    return False
            # Is it an issue with int or float size?
            elif strict == True:
                if verbose:
                    logger.info("Table not in correct format due to wrong type for column '" + child_colname + "'\n" +
                                "Expected: " + ex_dtype + "\n" +
                                "Got: " + str(table.dtype[child_colname].newbyteorder('>')))
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
        if not table_format.is_base and table.meta[table_format.m.fits_def] != table_format.m.table_format:
            if verbose:
                logger.info("Table not in correct format due to wrong table format label.\n" +
                            "Expected: " + str(table_format.m.table_format) + "\n" +
                            "Got: " + str(table.meta[table_format.m.fits_def]))
            return False

        # Check the version is correct
        if not table_format.is_base and  table.meta[table_format.m.fits_version] != table_format.__version__:
            if verbose:
                logger.info("Table not in correct format due to wrong table format label.\n" +
                            "Expected: " + str(table_format.__version__) + "\n" +
                            "Got: " + str(table.meta[table_format.m.fits_version]))
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


def set_column_properties(self, name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                          length=1):

    assert name not in self.is_optional

    self.is_optional[name] = is_optional
    self.comments[name] = comment
    self.dtypes[name] = dtype
    self.fits_dtypes[name] = fits_dtype
    self.lengths[name] = length

    return name


def setup_table_format(self):

    # And a quick alias for it
    self.m = self.meta

    # Get the version from the meta class
    self.__version__ = self.m.__version__

    # Direct alias for a tuple of all metadata
    self.meta_data = self.m.all

    self.is_base = False

    self.is_optional = OrderedDict()
    self.comments = OrderedDict()
    self.dtypes = OrderedDict()
    self.fits_dtypes = OrderedDict()
    self.lengths = OrderedDict()

    self.set_column_properties = set_column_properties

    return


def setup_child_table_format(self, child_label, unlabelled_columns=None):

    if unlabelled_columns is None:
        unlabelled_columns = []

    # And a quick alias for it
    self.m = self.meta

    # Get the version from the meta class
    self.__version__ = self.m.__version__
    self.child_label = child_label

    # Direct alias for a tuple of all metadata
    self.meta_data = self.m.all

    self.is_base = False

    self.parent_is_optional = self.is_optional
    self.parent_comments = self.comments
    self.parent_dtypes = self.dtypes
    self.parent_fits_dtypes = self.fits_dtypes
    self.parent_lengths = self.lengths
    self.parent_all = self.all
    self.parent_all_required = self.all_required

    self.is_optional = OrderedDict()
    self.comments = OrderedDict()
    self.dtypes = OrderedDict()
    self.fits_dtypes = OrderedDict()
    self.lengths = OrderedDict()

    changed_column_names = {}

    for parent_name in self.parent_all:
        if parent_name in unlabelled_columns:
            name = parent_name
        else:
            name = child_label + parent_name
            changed_column_names[parent_name] = name

        self.is_optional[name] = self.parent_is_optional[parent_name]
        self.comments[name] = self.parent_comments[parent_name]
        self.dtypes[name] = self.parent_dtypes[parent_name]
        self.fits_dtypes[name] = self.parent_fits_dtypes[parent_name]
        self.lengths[name] = self.parent_lengths[parent_name]

    # Update existing column names inherited from parent
    for key, val in self.__dict__.items():
        if isinstance(val, str) and val in changed_column_names:
            setattr(self, key, changed_column_names[val])

    self.set_column_properties = set_column_properties

    return
