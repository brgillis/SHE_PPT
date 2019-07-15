""" @file bfd_bias_statistics.py

    Created 12 July 2019

    Format definition for tables containing shear bias statistics.
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

__updated__ = "2019-07-15"

from collections import OrderedDict

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressStatistics, BiasMeasurements
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table


logger = getLogger(mv.logger_name)


class BFDBiasStatisticsTableMeta(object):
    """
        @brief A class defining the metadata for BFD bias statistics tables.
    """

    def __init__(self):

        self.__version__ = "0.1"
        self.table_format = "she.BFDBiasStatistics"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        # Metadata specific to this table format

        self.ID = "ID"

        self.method = "METHOD"

        self.m1 = "BM_M1"
        self.m1_err = "BM_M1E"
        self.c1 = "BM_C1"
        self.c1_err = "BM_C1E"
        self.m1c1_covar = "BM_M1C1C"

        self.m2 = "BM_M2"
        self.m2_err = "BM_M2E"
        self.c2 = "BM_C2"
        self.c2_err = "BM_C2E"
        self.m2c2_covar = "BM_M2C2C"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.ID, None),
                                     (self.method, "Must be 'BFD'"),
                                     (self.m1, None),
                                     (self.m1_err, None),
                                     (self.c1, None),
                                     (self.c1_err, None),
                                     (self.m1c1_covar, None),
                                     (self.m2, None),
                                     (self.m2_err, None),
                                     (self.c2, None),
                                     (self.c2_err, None),
                                     (self.m2c2_covar, None),))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class BFDBiasStatisticsTableFormat(object):
    """
        @brief A class defining the format for bias statistics tables. Only the bfd_bias_statistics_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = BFDBiasStatisticsTableMeta()

        # And a quick alias for it
        self.m = self.meta

        # Get the version from the meta class
        self.__version__ = self.m.__version__

        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all

        # Dicts for less-used properties
        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Table column labels and properties

        self.ID = set_column_properties("RUN_ID", dtype="S", fits_dtype="A", length=20, is_optional=True)

        self.b1 = set_column_properties("B1", dtype=">f4", fits_dtype="E")
        self.b2 = set_column_properties("B2", dtype=">f4", fits_dtype="E")
        self.b3 = set_column_properties("B3", dtype=">f4", fits_dtype="E")
        self.b4 = set_column_properties("B4", dtype=">f4", fits_dtype="E")

        self.A11 = set_column_properties("A11", dtype=">f4", fits_dtype="E")
        self.A12 = set_column_properties("A12", dtype=">f4", fits_dtype="E")
        self.A13 = set_column_properties("A13", dtype=">f4", fits_dtype="E")
        self.A14 = set_column_properties("A14", dtype=">f4", fits_dtype="E")
        self.A22 = set_column_properties("A22", dtype=">f4", fits_dtype="E")
        self.A23 = set_column_properties("A23", dtype=">f4", fits_dtype="E")
        self.A24 = set_column_properties("A24", dtype=">f4", fits_dtype="E")
        self.A33 = set_column_properties("A33", dtype=">f4", fits_dtype="E")
        self.A34 = set_column_properties("A34", dtype=">f4", fits_dtype="E")
        self.A44 = set_column_properties("A44", dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
bfd_bias_statistics_table_format = BFDBiasStatisticsTableFormat()

# And a convient alias for it
tf = bfd_bias_statistics_table_format


def make_bfd_bias_statistics_table_header(ID=None,
                                          method='BFD',
                                          g1_bias_measurements=None,
                                          g2_bias_measurements=None):
    """
    Generate a header for a bias statistics table.

    Parameters
    ----------
    ID : str (max 20 characters)
        ID for this run
    method : str ('KSB', 'REGAUSS', 'MomentsML', or 'LensMC', or else 'Unspecified')
        The shear estimation method this table is for
    g1_bias_measurements : SHE_PPT.math.BiasMeasurements
        Bias measurements object for g1 component of shear
    g2_bias_measurements : SHE_PPT.math.BiasMeasurements
        Bias measurements object for g2 component of shear

    Return
    ------
    header : OrderedDict
    """

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.ID] = str(ID)
    if method == 'BFD':
        header[tf.m.method] = method
    else:
        raise TypeError("method must be 'BFD'")

    if g1_bias_measurements is None:
        header[tf.m.m1] = 0
        header[tf.m.m1_err] = 1e99
        header[tf.m.c1] = 0
        header[tf.m.c1_err] = 1e99
        header[tf.m.m1c1_covar] = 0
    elif isinstance(g1_bias_measurements, BiasMeasurements):
        header[tf.m.m1] = g1_bias_measurements.m
        header[tf.m.m1_err] = g1_bias_measurements.m_err
        header[tf.m.c1] = g1_bias_measurements.c
        header[tf.m.c1_err] = g1_bias_measurements.c_err
        header[tf.m.m1c1_covar] = g1_bias_measurements.mc_covar
    else:
        raise TypeError("g2_bias_measurements must be of type BiasMeasurements")

    if g2_bias_measurements is None:
        header[tf.m.m2] = 0
        header[tf.m.m2_err] = 1e99
        header[tf.m.c2] = 0
        header[tf.m.c2_err] = 1e99
        header[tf.m.m2c2_covar] = 0
    elif isinstance(g2_bias_measurements, BiasMeasurements):
        header[tf.m.m2] = g2_bias_measurements.m
        header[tf.m.m2_err] = g2_bias_measurements.m_err
        header[tf.m.c2] = g2_bias_measurements.c
        header[tf.m.c2_err] = g2_bias_measurements.c_err
        header[tf.m.m2c2_covar] = g2_bias_measurements.mc_covar
    else:
        raise TypeError("g2_bias_measurements must be of type BiasMeasurements")

    return header


def initialise_bfd_bias_statistics_table(optional_columns=None,
                                         ID=None,
                                         method='BFD',
                                         g1_bias_measurements=None,
                                         g2_bias_measurements=None,
                                         run_IDs=None,
                                         bfd_bias_statistics=None,
                                         ):
    """
    Initialise a bias statistics table.

    Parameters
    ----------
    ID : str (max 20 characters)
        ID for this run
    method : str ('KSB', 'REGAUSS', 'MomentsML', or 'LensMC', or else 'Unspecified')
        The shear estimation method this table is for
    g1_bias_measurements : SHE_PPT.math.BiasMeasurements
        Bias measurements object for g1 component of shear
    g2_bias_measurements : SHE_PPT.math.BiasMeasurements
        Bias measurements object for g2 component of shear
    ID : iterable<str (max 20 characters)>
        List (or otherwise) of IDs associated with each shear statistics object
    bfd_bias_statistics : iterable<SHE_PPT.math.BFDSumStatistics>
        List (or otherwise) of BFDSumStatistics objects for BFD bias statistics

    Return
    ------
    bfd_bias_statistics_table : astropy.table.Table
    """

    # Rename internal representation of bfd_bias_statistics to l_bfd_bias_statistics for consistency
    l_bfd_bias_statistics = bfd_bias_statistics
    del bfd_bias_statistics

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    names = []
    init_cols = []
    dtypes = []
    for colname in tf.all:
        if (colname in tf.all_required) or (colname in optional_columns):
            names.append(colname)
            init_cols.append([])
            dtypes.append((tf.dtypes[colname], tf.lengths[colname]))

    # Create the table
    bfd_bias_statistics_table = Table(init_cols, names=names, dtype=dtypes)

    # Create the table's header
    bfd_bias_statistics_table.meta = make_bfd_bias_statistics_table_header(ID=ID,
                                                                           method=method,
                                                                           g1_bias_measurements=g1_bias_measurements,
                                                                           g2_bias_measurements=g2_bias_measurements,)

    # Check validity of initial values

    if run_IDs is None:
        run_IDs = []
        len_run_IDs = 0
    else:
        try:
            len_run_IDs = len(run_IDs)
        except TypeError:
            # If it isn't iterable, silently coerce into a list
            run_IDs = [run_IDs]
            len_run_IDs = 1

    if l_bfd_bias_statistics is None:
        l_bfd_bias_statistics = []
        len_bfd_bias_statistics = 0
    else:
        try:
            len_bfd_bias_statistics = len(l_bfd_bias_statistics)
        except TypeError:
            # If it isn't iterable, silently coerce into a list
            l_bfd_bias_statistics = [l_bfd_bias_statistics]
            len_bfd_bias_statistics = 1

    if len_bfd_bias_statistics > 0:
        if tf.ID in names:
            if len_run_IDs == 1:
                run_IDs *= len_bfd_bias_statistics
            elif not len_run_IDs == len_bfd_bias_statistics:
                raise ValueError("run_IDs different length from bias statistics")
        elif not len_run_IDs == 0:
            raise ValueError("run_IDs supplied, but not in optional columns")

    # Add a row for each statistics object
    for row_index in range(len_bfd_bias_statistics):
        bfd_bias_statistics = l_bfd_bias_statistics[row_index]

        new_row = {tf.b1: bfd_bias_statistics.b1,
                   tf.b2: bfd_bias_statistics.b2,
                   tf.b3: bfd_bias_statistics.b3,
                   tf.b4: bfd_bias_statistics.b4,
                   tf.A11: bfd_bias_statistics.A11,
                   tf.A12: bfd_bias_statistics.A12,
                   tf.A13: bfd_bias_statistics.A13,
                   tf.A14: bfd_bias_statistics.A14,
                   tf.A22: bfd_bias_statistics.A22,
                   tf.A23: bfd_bias_statistics.A23,
                   tf.A24: bfd_bias_statistics.A24,
                   tf.A33: bfd_bias_statistics.A33,
                   tf.A34: bfd_bias_statistics.A34,
                   tf.A44: bfd_bias_statistics.A44,
                   }

        if not len_run_IDs == 0:
            new_row[tf.ID] = run_IDs[row_index]

        bfd_bias_statistics_table.add_row(vals=new_row)

    # Check we meet the requirements of the table format
    assert(is_in_format(bfd_bias_statistics_table, tf, verbose=True))

    return bfd_bias_statistics_table


# Utility functions related to this table format

def get_bfd_bias_statistics(table, compress=False):
    """

    Gets the bias statistics from a table, in the format of a list of BFDSumStatistics objects.

    Parameters
    ----------
    table : astropy.table.Table (in bfd_bias_statistics format)
    compress : bool
        If True and if table has only one row, will return result as object, not list

    Return
    ------
    list<BFDSumStatistics> : list of BFDSumStatistics objects

    """

    if not is_in_format(table, tf, ignore_metadata=True, strict=False):
        raise ValueError("table must be in bfd_bias_statistics format for get_bfd_bias_statistics method")

    l_bfd_bias_statistics = []

    for row in table:

        # Get g1 stats

        bfd_bias_statistics = LinregressStatistics()

        bfd_bias_statistics.b1 = row[tf.b1]
        bfd_bias_statistics.b2 = row[tf.b2]
        bfd_bias_statistics.b3 = row[tf.b3]
        bfd_bias_statistics.b4 = row[tf.b4]
        bfd_bias_statistics.A11 = row[tf.A11]
        bfd_bias_statistics.A12 = row[tf.A12]
        bfd_bias_statistics.A13 = row[tf.A13]
        bfd_bias_statistics.A14 = row[tf.A14]
        bfd_bias_statistics.A22 = row[tf.A22]
        bfd_bias_statistics.A23 = row[tf.A23]
        bfd_bias_statistics.A24 = row[tf.A24]
        bfd_bias_statistics.A33 = row[tf.A33]
        bfd_bias_statistics.A34 = row[tf.A34]
        bfd_bias_statistics.A44 = row[tf.A44]

        l_bfd_bias_statistics.append(bfd_bias_statistics)

    # Compress if desired
    if compress and len(l_bfd_bias_statistics) == 1:
        return l_bfd_bias_statistics[0]

    return l_bfd_bias_statistics
