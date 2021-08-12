""" @file tables.py

    Created 21 Aug 2017

    Functions related to output of details and detections tables.
"""

__updated__ = "2021-08-12"

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

from collections import OrderedDict
from copy import deepcopy
from typing import Dict, List, Optional

from astropy.table import Column, Table

from SHE_PPT.constants.fits import FITS_DEF_LABEL, FITS_VERSION_LABEL
import numpy as np

from .logging import getLogger


logger = getLogger(__name__)


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
        logger.warn("Table format %s is a base format. Enforcing strict=False.", table_format.m.table_format)
        strict = False

    # Check that all required column names are present
    if not table_format.is_base:
        # Simple check if not comparing to a base class
        for colname in table_format.all_required:
            if colname not in table.colnames:
                if verbose:
                    logger.info("Table not in correct format due to absence of required column: %s", colname)
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
                    elif len(parent_colname) < len(child_colname) \
                            and child_colname[-len(parent_colname):] == parent_colname:
                        child_label = child_colname[0:-len(parent_colname)]
                        found = True
                        break
                if not found:
                    if verbose:
                        logger.info("Table not in correct format due to absence of required column: %s",
                                    parent_colname)
                    return False
            else:
                # Once we've figured out what the child_label is, we can be a bit more efficient
                if parent_colname not in table.colnames and child_label + parent_colname not in table.columns:
                    if verbose:
                        logger.info("Table not in correct format due to absence of required column: %s", colname)
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
                    "Table not in correct format due to presence of extra column: %s", colname)
                return False
            if verbose:
                logger.info("Table not in correct format due to presence of extra column: %s, but not failing "
                            "check due to strict==False.", colname)

        elif col_dtype != ex_dtype:

            # Check if this is just an issue with lengths
            if col_dtype.str[1] == 'U' and ex_dtype.str[1] == 'U':
                col_len = int(col_dtype.str[2:])
                if col_len < table_format.lengths[parent_colname]:
                    # Length is shorter, likely due to saving as ascii. Allow it
                    pass
                elif col_len > table_format.lengths[parent_colname]:
                    if verbose:
                        logger.info("Table not in correct format due to wrong length for column '%s'\n"
                                    "Expected: %d\nGot: %d",
                                    parent_colname, table_format.lengths[parent_colname], col_len)
                    if strict:
                        return False
                    logger.info("Not failing check due to strict==False.")
            # Is it an issue with a bool column being read as a string?
            elif col_dtype.str[1] == 'U' and ex_dtype.str == '|b1':
                if fix_bool:
                    col = Column(data=np.empty_like(table[child_colname].data, dtype=bool))
                    for i in range(len(col)):
                        col[i] = (table[child_colname] == "True" or table[child_colname]
                                  == "true" or table[child_colname] == "1")
                    table.replace_column(colname, col)
                else:
                    if verbose:
                        logger.info("Table not in correct format due to wrong type for column '%s'\n"
                                    "Expected: %s\n"
                                    "Got: %s",
                                    parent_colname,
                                    ex_dtype,
                                    table.dtype[child_colname].newbyteorder('>'))
                    return False
            # Is it an issue with int or float size?
            elif strict is True:
                if verbose:
                    logger.info("Table not in correct format due to wrong type for column '%s'\n"
                                "Expected: %s\n"
                                "Got: %s",
                                child_colname,
                                ex_dtype,
                                table.dtype[child_colname].newbyteorder('>'))
                return False

    if not ignore_metadata:
        # Check the metadata is correct
        keys_in_table = deepcopy(list(table.meta.keys()))
        keys_in_table_format = deepcopy(table_format.m.all)
        if keys_in_table.sort() != keys_in_table_format.sort():
            if verbose:
                logger.info("Table not in correct format due to wrong metadata keys.\n"
                            "Expected: %s\n"
                            "Got: %s",
                            table_format.m.all,
                            list(table.meta.keys()))
            return False

        # Check the format label is correct
        if (table_format.m.fits_def in table.meta and not table_format.is_base
                and table.meta[table_format.m.fits_def] != table_format.m.table_format):
            if verbose:
                logger.info("Table not in correct format due to wrong table format label.\n"
                            "Expected: %s\n"
                            "Got: %s",
                            table_format.m.table_format,
                            table.meta[table_format.m.fits_def])
            return False

        # Check the version is correct
        if (table_format.m.fits_version in table.meta and not table_format.is_base and
                table.meta[table_format.m.fits_version] != table_format.__version__):
            if verbose:
                logger.info("Table not in correct format due to wrong table format label.\n"
                            "Expected: %s\n"
                            "Got: %s",
                            table_format.__version__,
                            table.meta[table_format.m.fits_version])
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


def output_tables(otable, file_name_base, output_format):

    if output_format not in ('ascii', 'fits', 'both'):
        raise ValueError("Invalid output format: " + str(output_format))

    if output_format in ('ascii', "both"):
        text_file_name = file_name_base + ".ecsv"
        otable.write(text_file_name, format='ascii.ecsv')

    if output_format in ('fits', 'both'):
        fits_file_name = file_name_base + ".fits"
        otable.write(fits_file_name, format='fits', overwrite=True)


def init_table(tf: "SheTableFormat",
               size: Optional[int] = None,
               optional_columns: Optional[List[str]] = None,
               init_cols: Optional[List[Column]] = None,
               **kwargs: str):
    """ Initializes a table with a given format, without any metadata.
    """

    if optional_columns is None:
        optional_columns = []

    if init_cols is None:
        init_cols = {}
    else:
        for a in init_cols.values():
            if size is None:
                size = len(a)
            elif size != len(a):
                raise ValueError("Inconsistent size of input columns for initialising table.")

    if size is None:
        size = 0

    names = []
    full_init_cols = []
    dtypes = []

    # Check for any array columns, which prevent all but empty initialisation
    must_init_empty = False

    for colname in tf.all:
        if tf.lengths[colname] > 0 and tf.dtypes[colname] != str:
            must_init_empty = True

    for colname in tf.all:
        if not ((colname in tf.all_required) or (colname in optional_columns)):
            continue
        names.append(colname)

        col_dtype = tf.dtypes[colname]
        col_length = tf.lengths[colname]

        if col_length == 1 and col_dtype != "str":
            dtype = col_dtype
        else:
            dtype = (col_dtype, col_length)

        dtypes.append(dtype)

        if colname in init_cols.keys():
            col = init_cols[colname]
            full_init_cols.append(init_cols[colname])
            if size == 0 and len(col) > 0:
                size = len(col)
        else:
            col = Column(name=colname, data=np.zeros(size, dtype=dtype))

            full_init_cols.append(col)

    if must_init_empty:

        # We have to use a bit of a workaround if the table has any array columns, due to a bug in astropy

        t_template = Table(names=names, dtype=dtypes)

        t_data = np.zeros((size,), dtype=t_template.dtype)

        t = Table(t_data, meta=t_template.meta)

        for colname in tf.all:
            if colname in init_cols.keys():
                t[colname] = init_cols[colname]

    else:
        t = Table(full_init_cols, names=names, dtype=dtypes)

    return t


_NON_HEADER_ATTRS = ["table_format", "comments", "all", "init_meta"]


class SheTableMeta():
    """ Base class for table format metadata.
    """

    # Required attributes which aren't stored in the FITS header
    table_format: str
    __version__: str
    comments: Dict[str, Optional[str]]
    all: List[str]

    # Required attributes which correspond to keys in the FITS header
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    def __init__(self,
                 comments: Optional[Dict[str, Optional[str]]] = None):

        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None)))
        if comments:
            for key in comments:
                self.comments[key] = comments[key]

        # Check that there's an entry for all attrs in comments, and add an empty comment if not
        for attr in dir(self):
            # Skip private attributes, and those we explicitly don't want listed
            if attr in _NON_HEADER_ATTRS or attr[1] == "_":
                continue
            self.comments[getattr(self, attr)] = None

        # Set self.all as a list of columns in the desired order
        self.all = list(self.comments.keys())

    def init_meta(self,
                  **kwargs: str):
        """ Initializes a metadata object for a table as an OrderedDict, passing the kwargs to this function
            to the header values corresponding to the attributes of this class.
        """

        m = OrderedDict()

        # First initialise all header values empty
        for attr in dir(self):
            # Skip private attributes, and those we explicitly don't want listed
            if attr in _NON_HEADER_ATTRS or attr[1] == "_":
                continue
            m[getattr(self, attr)] = None

        # Fill in fits version and def
        m[self.fits_version] = self.__version__
        m[self.fits_def] = self.table_format

        # Fill in any values passed from arguments
        for attr in kwargs:
            try:
                m[getattr(self, attr)] = kwargs[attr]
            except AttributeError:
                raise ValueError("kwargs passed to init_meta must be of the format {attr}={value}, where {attr} is "
                                 "an attribute of the table format meta class.")

        return m


class SheTableFormat():

    # Attributes set directly at init
    meta: SheTableMeta

    # Attributes determined at init
    m: SheTableMeta
    __version__: str

    # Attributes initialised empty at init
    is_optional: Dict[str, bool]
    comments: Dict[str, str]
    dtypes: Dict[str, str]
    fits_dtypes: Dict[str, bool]
    lengths: Dict[str, int]

    # Fixed attributes (can be changed in derived classes)
    is_base: bool = False
    unlabelled_columns: Optional[List[str]] = None

    def __init__(self,
                 meta: SheTableMeta,
                 finalize: bool = False):

        self.meta = meta
        self.m = self.meta

        # Get the version from the meta class
        self.__version__ = self.m.__version__

        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all

        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        if self.unlabelled_columns is None:
            self.unlabelled_columns = []

        if finalize:
            self._finalize_init()

    def _finalize_init(self):
        """ A method to call at the end of any derived init, once all columns have been set up.
        """

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

    def set_column_properties(self, name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                              length=1, unlabelled=False):

        assert name not in self.is_optional

        self.is_optional[name] = is_optional
        self.comments[name] = comment
        self.dtypes[name] = dtype
        self.fits_dtypes[name] = fits_dtype
        self.lengths[name] = length

        if unlabelled:
            self.unlabelled_columns.append(name)

        return name

    def setup_child_table_format(self, child_label):

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
        self.parent_all = list(self.is_optional.keys())

        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        changed_column_names = {}

        for parent_name in self.parent_all:
            if parent_name in self.unlabelled_columns:
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

    def init_table(self,
                   size: Optional[int] = None,
                   optional_columns: Optional[List[str]] = None,
                   init_cols: Optional[List[Column]] = None,
                   **kwargs):
        """ Initializes a table with a given format. Any extra kwargs are assumed to refer to values to set in the header,
            with the kwarg being the attribute of the table's meta class.
        """

        t = init_table(tf=self,
                       size=size,
                       optional_columns=optional_columns,
                       init_cols=init_cols)

        t.meta = self.m.init_meta(**kwargs)

        assert is_in_format(t, self, verbose=True)

        return t
