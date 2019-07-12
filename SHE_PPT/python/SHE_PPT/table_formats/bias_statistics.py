""" @file bias_statistics.py

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

__updated__ = "2019-07-12"

from collections import OrderedDict

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.math import LinregressStatistics, BiasMeasurements
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table
import numpy as np


logger = getLogger(mv.logger_name)


class BiasStatisticsTableMeta(object):
    """
        @brief A class defining the metadata for bias statistics tables.
    """

    def __init__(self):

        self.__version__ = "0.1"
        self.table_format = "she.biasStatistics"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        # Metadata specific to this table format

        self.ID = "Unspecified"

        self.method = "Unspecified"

        self.m1 = np.NaN
        self.m1_err = np.NaN
        self.c1 = np.NaN
        self.c1_err = np.NaN
        self.m1c1_covar = np.NaN

        self.m2 = np.NaN
        self.m2_err = np.NaN
        self.c2 = np.NaN
        self.c2_err = np.NaN
        self.m2c2_covar = np.NaN

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.method, "One of 'KSB', 'REGAUSS', 'MomentsML', or 'LensMC', or else 'Unspecified'.")))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class BiasStatisticsTableFormat(object):
    """
        @brief A class defining the format for bias statistics tables. Only the bias_statistics_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = BiasStatisticsTableMeta()

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

        self.w1 = set_column_properties("W1", dtype=">f4", fits_dtype="E")
        self.xm1 = set_column_properties("XM1", dtype=">f4", fits_dtype="E")
        self.x2m1 = set_column_properties("X2M1", dtype=">f4", fits_dtype="E")
        self.ym1 = set_column_properties("YM1", dtype=">f4", fits_dtype="E")
        self.xym1 = set_column_properties("XY1", dtype=">f4", fits_dtype="E")

        self.w2 = set_column_properties("W2", dtype=">f4", fits_dtype="E")
        self.xm2 = set_column_properties("XM2", dtype=">f4", fits_dtype="E")
        self.x2m2 = set_column_properties("X2M2", dtype=">f4", fits_dtype="E")
        self.ym2 = set_column_properties("YM2", dtype=">f4", fits_dtype="E")
        self.xym2 = set_column_properties("XY2", dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
bias_statistics_table_format = BiasStatisticsTableFormat()

# And a convient alias for it
tf = bias_statistics_table_format


def make_bias_statistics_table_header(ID=None,
                                      method='Unspecified',
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
    if method in ('KSB', 'REGAUSS', 'MomentsML', 'LensMC', 'Unspecified'):
        header[tf.m.method] = method
    else:
        raise TypeError("method must be 'KSB', 'REGAUSS', 'MomentsML', or 'LensMC', or else 'Unspecified'")

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
        raise TypeError("g1_bias_measurements must be of type BiasMeasurements")

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


def initialise_bias_statistics_table(optional_columns=None,
                                     ID=None,
                                     method='Unspecified',
                                     g1_bias_measurements=None,
                                     g2_bias_measurements=None,
                                     run_IDs=None,
                                     g1_bias_statistics=None,
                                     g2_bias_statistics=None,
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
    g1_bias_statistics : iterable<SHE_PPT.math.LinregressStatistics>
        List (or otherwise) of LinregressStatistics objects for g1 bias statistics
    g2_bias_statistics : iterable<SHE_PPT.math.LinregressStatistics>
        List (or otherwise) of LinregressStatistics objects for g2 bias statistics

    Return
    ------
    bias_statistics_table : astropy.table.Table
    """

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
    bias_statistics_table = Table(init_cols, names=names, dtype=dtypes)

    # Create the table's header
    bias_statistics_table.meta = make_bias_statistics_table_header(ID=ID,
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

    if g1_bias_statistics is None:
        g1_bias_statistics = []
        len_g1_bias_statistics = 0
    else:
        try:
            len_g1_bias_statistics = len(g1_bias_statistics)
        except TypeError:
            # If it isn't iterable, silently coerce into a list
            g1_bias_statistics = [g1_bias_statistics]
            len_g1_bias_statistics = 1

    if g2_bias_statistics is None:
        g2_bias_statistics = []
        len_g2_bias_statistics = 0
    else:
        try:
            len_g2_bias_statistics = len(g2_bias_statistics)
        except TypeError:
            # If it isn't iterable, silently coerce into a list
            g2_bias_statistics = [g2_bias_statistics]
            len_g2_bias_statistics = 1

    # Check lengths are sensible
    if not len_g1_bias_statistics == len_g2_bias_statistics:
        raise ValueError("g1_bias_statistics and g2_bias_statistics must have the same length")
    else:
        num_rows = len_g1_bias_statistics

    if num_rows > 0:
        if tf.ID in names:
            if len_run_IDs == 1:
                run_IDs *= num_rows
            elif not len_run_IDs == num_rows:
                raise ValueError("run_IDs different length from bias statistics")
        elif not len_run_IDs == 0:
            raise ValueError("run_IDs supplied, but not in optional columns")

    # Add a row for each statistics object
    for row_index in range(num_rows):
        g1_bias_stats = g1_bias_statistics[row_index]
        g2_bias_stats = g2_bias_statistics[row_index]

        new_row = {tf.w1: g1_bias_stats.w,
                   tf.xm1: g1_bias_stats.xm,
                   tf.x2m1: g1_bias_stats.x2m,
                   tf.ym1: g1_bias_stats.ym,
                   tf.xym1: g1_bias_stats.xym,
                   tf.w2: g2_bias_stats.w,
                   tf.xm2: g2_bias_stats.xm,
                   tf.x2m2: g2_bias_stats.x2m,
                   tf.ym2: g2_bias_stats.ym,
                   tf.xym2: g2_bias_stats.xym, }

        if not len_run_IDs == 0:
            new_row[tf.ID] = run_IDs[row_index]

        bias_statistics_table.add_row(vals=new_row)

    # Check we meet the requirements of the table format
    assert(is_in_format(bias_statistics_table, tf))

    return bias_statistics_table

# Utility functions related to this table format


def get_bias_statistics(table, compress=False):
    """

    Gets the bias statistics from a table, in the format of a pair of lists of LinregressStatistics objects.

    Parameters
    ----------
    table : astropy.table.Table (in bias_statistics format)
    compress : bool
        If True and if table has only one row, will return results as objects, not lists

    Return
    ------
    tuple<list<LinregressStatistics>,list<LinregressStatistics>> : tuple of g1, g2 bias statistics lists

    """

    if not is_in_format(table, tf, ignore_metadata=True, strict=False):
        raise ValueError("table must be in bias_statistics format for get_bias_statistics method")

    l_g1_bias_statistics = []
    l_g2_bias_statistics = []

    for row in table:

        # Get g1 stats

        g1_bias_statistics = LinregressStatistics()

        g1_bias_statistics.w = row[tf.w1]
        g1_bias_statistics.xm = row[tf.xm1]
        g1_bias_statistics.x2m = row[tf.x2m1]
        g1_bias_statistics.ym = row[tf.ym1]
        g1_bias_statistics.y2m = row[tf.y2m1]

        l_g1_bias_statistics.append(g1_bias_statistics)

        # Get g2 stats

        g2_bias_statistics = LinregressStatistics()

        g2_bias_statistics.w = row[tf.w2]
        g2_bias_statistics.xm = row[tf.xm2]
        g2_bias_statistics.x2m = row[tf.x2m2]
        g2_bias_statistics.ym = row[tf.ym2]
        g2_bias_statistics.y2m = row[tf.y2m2]

        l_g2_bias_statistics.append(g1_bias_statistics)

    # Compress if desired
    if compress and len(l_g1_bias_statistics) == 1:
        return l_g1_bias_statistics[0], l_g2_bias_statistics[0]

    return l_g1_bias_statistics, l_g2_bias_statistics
