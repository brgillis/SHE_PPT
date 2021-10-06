""" @file bias_statistics.py

    Created 12 July 2019

    Format definition for tables containing shear bias statistics.
"""

__updated__ = "2021-08-13"

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

import numpy as np

from ..constants.classes import ShearEstimationMethods
from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL
from ..logging import getLogger
from ..math import LinregressStatistics, LinregressResults, BiasMeasurements
from ..table_utility import is_in_format, init_table, SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.biasStatistics"

logger = getLogger(__name__)


class SheBiasStatisticsMeta(SheTableMeta):
    """
        @brief A class defining the metadata for bias statistics tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    ID: str = "ID"

    method: str = "METHOD"

    m1: str = "BM_M1"
    m1_err: str = "BM_M1E"
    c1: str = "BM_C1"
    c1_err: str = "BM_C1E"
    m1c1_covar: str = "BM_M1C1C"

    m2: str = "BM_M2"
    m2_err: str = "BM_M2E"
    c2: str = "BM_C2"
    c2_err: str = "BM_C2E"
    m2c2_covar: str = "BM_M2C2C"

    def __init__(self):
        # Store the less-used comments in a dict
        super().__init__(comments = OrderedDict(((self.fits_version, None),
                                                 (self.fits_def, None),
                                                 (self.ID, None),
                                                 (self.method,
                                                  "One of 'KSB', 'REGAUSS', 'MomentsML', or 'LensMC', "
                                                  "or else 'Unspecified'."),
                                                 (self.m1, None),
                                                 (self.m1_err, None),
                                                 (self.c1, None),
                                                 (self.c1_err, None),
                                                 (self.m1c1_covar, None),
                                                 (self.m2, None),
                                                 (self.m2_err, None),
                                                 (self.c2, None),
                                                 (self.c2_err, None),
                                                 (self.m2c2_covar, None),)))


class SheBiasStatisticsFormat(SheTableFormat):
    """
        @brief A class defining the format for bias statistics tables. Only the bias_statistics_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheBiasStatisticsMeta())

        # Table column labels and properties

        self.ID = self.set_column_properties("RUN_ID", dtype = "str", fits_dtype = "A", length = 20, is_optional = True)

        self.w1 = self.set_column_properties("W1", dtype = ">f4", fits_dtype = "E")
        self.xm1 = self.set_column_properties("XM1", dtype = ">f4", fits_dtype = "E")
        self.x2m1 = self.set_column_properties("X2M1", dtype = ">f4", fits_dtype = "E")
        self.ym1 = self.set_column_properties("YM1", dtype = ">f4", fits_dtype = "E")
        self.xym1 = self.set_column_properties("XY1", dtype = ">f4", fits_dtype = "E")

        self.w2 = self.set_column_properties("W2", dtype = ">f4", fits_dtype = "E")
        self.xm2 = self.set_column_properties("XM2", dtype = ">f4", fits_dtype = "E")
        self.x2m2 = self.set_column_properties("X2M2", dtype = ">f4", fits_dtype = "E")
        self.ym2 = self.set_column_properties("YM2", dtype = ">f4", fits_dtype = "E")
        self.xym2 = self.set_column_properties("XY2", dtype = ">f4", fits_dtype = "E")

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_bias_statistics_table(*args, **kwargs)


# Define an instance of this object that can be imported
bias_statistics_table_format = SheBiasStatisticsFormat()

# And a convenient alias for it
tf = bias_statistics_table_format


def make_bias_statistics_table_header(ID = None,
                                      method = 'Unspecified',
                                      g1_bias_measurements = None,
                                      g2_bias_measurements = None):
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

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    header[tf.m.ID] = str(ID)
    if method in ShearEstimationMethods:
        header[tf.m.method] = method.value
    elif method == 'Unspecified':
        header[tf.m.method] = method
    else:
        raise TypeError("method must be in ShearEstimationMethods, or else 'Unspecified'")

    if g1_bias_measurements is None:
        header[tf.m.m1] = ""
        header[tf.m.m1_err] = ""
        header[tf.m.c1] = ""
        header[tf.m.c1_err] = ""
        header[tf.m.m1c1_covar] = ""
    elif isinstance(g1_bias_measurements, BiasMeasurements):
        for key, val in ((tf.m.m1, g1_bias_measurements.m),
                         (tf.m.m1_err, g1_bias_measurements.m_err),
                         (tf.m.c1, g1_bias_measurements.c),
                         (tf.m.c1_err, g1_bias_measurements.c_err),
                         (tf.m.m1c1_covar, g1_bias_measurements.mc_covar),):
            if np.isinf(val):
                header[key] = "Inf"
            elif np.isnan(val):
                header[key] = "NaN"
            else:
                header[key] = val
    else:
        raise TypeError("g1_bias_measurements must be of type BiasMeasurements")

    if g2_bias_measurements is None:
        header[tf.m.m2] = ""
        header[tf.m.m2_err] = ""
        header[tf.m.c2] = ""
        header[tf.m.c2_err] = ""
        header[tf.m.m2c2_covar] = ""
    elif isinstance(g2_bias_measurements, BiasMeasurements):
        for key, val in ((tf.m.m2, g2_bias_measurements.m),
                         (tf.m.m2_err, g2_bias_measurements.m_err),
                         (tf.m.c2, g2_bias_measurements.c),
                         (tf.m.c2_err, g2_bias_measurements.c_err),
                         (tf.m.m2c2_covar, g2_bias_measurements.mc_covar),):
            if np.isinf(val):
                header[key] = "Inf"
            elif np.isnan(val):
                header[key] = "NaN"
            else:
                header[key] = val
    else:
        raise TypeError("g2_bias_measurements must be of type BiasMeasurements")

    return header


def initialise_bias_statistics_table(size = None,
                                     optional_columns = None,
                                     init_cols = None,
                                     ID = None,
                                     method = 'Unspecified',
                                     g1_bias_measurements = None,
                                     g2_bias_measurements = None,
                                     run_IDs = None,
                                     g1_bias_statistics = None,
                                     g2_bias_statistics = None,
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

    bias_statistics_table = init_table(tf, optional_columns = optional_columns, init_cols = init_cols, size = size)

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

    num_rows = len_g1_bias_statistics

    if num_rows > 0:
        if tf.ID in optional_columns:
            if len_run_IDs == 1:
                run_IDs *= num_rows
            elif not len_run_IDs == num_rows:
                raise ValueError("run_IDs different length from bias statistics")
        elif not len_run_IDs == 0:
            raise ValueError("run_IDs supplied, but not in optional columns")

    # If we weren't given specific bias measurements, calculate them from the statistics
    if g1_bias_measurements is None and len(g1_bias_statistics) > 0:
        g1_bias_measurements = BiasMeasurements(LinregressResults(g1_bias_statistics))
    if g2_bias_measurements is None and len(g2_bias_statistics) > 0:
        g2_bias_measurements = BiasMeasurements(LinregressResults(g2_bias_statistics))

    # Create the table's header
    bias_statistics_table.meta = make_bias_statistics_table_header(ID = ID,
                                                                   method = method,
                                                                   g1_bias_measurements = g1_bias_measurements,
                                                                   g2_bias_measurements = g2_bias_measurements, )

    # Add a row for each statistics object
    for row_index in range(num_rows):
        g1_bias_stats = g1_bias_statistics[row_index]
        g2_bias_stats = g2_bias_statistics[row_index]

        new_row = {tf.w1  : g1_bias_stats.w,
                   tf.xm1 : g1_bias_stats.xm,
                   tf.x2m1: g1_bias_stats.x2m,
                   tf.ym1 : g1_bias_stats.ym,
                   tf.xym1: g1_bias_stats.xym,
                   tf.w2  : g2_bias_stats.w,
                   tf.xm2 : g2_bias_stats.xm,
                   tf.x2m2: g2_bias_stats.x2m,
                   tf.ym2 : g2_bias_stats.ym,
                   tf.xym2: g2_bias_stats.xym, }

        if not len_run_IDs == 0:
            new_row[tf.ID] = run_IDs[row_index]

        bias_statistics_table.add_row(vals = new_row)

    # Check we meet the requirements of the table format
    assert is_in_format(bias_statistics_table, tf, verbose = True)

    return bias_statistics_table


# Utility functions related to this table format


def get_bias_statistics(table, compress = False):
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

    if not is_in_format(table, tf, ignore_metadata = True, strict = False):
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
        g1_bias_statistics.xym = row[tf.xym1]

        l_g1_bias_statistics.append(g1_bias_statistics)

        # Get g2 stats

        g2_bias_statistics = LinregressStatistics()

        g2_bias_statistics.w = row[tf.w2]
        g2_bias_statistics.xm = row[tf.xm2]
        g2_bias_statistics.x2m = row[tf.x2m2]
        g2_bias_statistics.ym = row[tf.ym2]
        g2_bias_statistics.xym = row[tf.xym2]

        l_g2_bias_statistics.append(g2_bias_statistics)

    # Compress if desired
    if compress and len(l_g1_bias_statistics) == 1:
        return l_g1_bias_statistics[0], l_g2_bias_statistics[0]

    return l_g1_bias_statistics, l_g2_bias_statistics


def calculate_bias_measurements(table, update = False):
    """

    Calculates the bias measurements from the data in a table and returns them in the format of a pair of
    BiasMeasurements objects.

    Parameters
    ----------
    table : astropy.table.Table (in bias_statistics format)
    update : If True, will update the values in the table's header to the new measurements (default False)

    Return
    ------
    tuple<BiasMeasurements,BiasMeasurements> : tuple of g1, g2 bias measurements

    """

    g1_bias_statistics, g2_bias_statistics = get_bias_statistics(table)

    g1_bias_measurements = BiasMeasurements(LinregressResults(g1_bias_statistics))
    g2_bias_measurements = BiasMeasurements(LinregressResults(g2_bias_statistics))

    if update:

        table.meta[tf.m.m1] = g1_bias_measurements.m
        table.meta[tf.m.m1_err] = g1_bias_measurements.m_err
        table.meta[tf.m.c1] = g1_bias_measurements.c
        table.meta[tf.m.c1_err] = g1_bias_measurements.c_err
        table.meta[tf.m.m1c1_covar] = g1_bias_measurements.mc_covar

        table.meta[tf.m.m2] = g2_bias_measurements.m
        table.meta[tf.m.m2_err] = g2_bias_measurements.m_err
        table.meta[tf.m.c2] = g2_bias_measurements.c
        table.meta[tf.m.c2_err] = g2_bias_measurements.c_err
        table.meta[tf.m.m2c2_covar] = g2_bias_measurements.mc_covar

    return g1_bias_measurements, g2_bias_measurements


def get_bias_measurements(table):
    """

    Gets the bias measurements from a table's header, in the format of a pair of BiasMeasurements objects.

    Parameters
    ----------
    table : astropy.table.Table (in bias_statistics format)

    Return
    ------
    tuple<BiasMeasurements,BiasMeasurements> : tuple of g1, g2 bias measurements

    """

    if not (is_in_format(table, tf, ignore_metadata = True, strict = False)):
        raise ValueError(
            "table must be in bias_statistics format for get_bias_measurements method")

    # Get g1 bias measurements

    g1_bias_measurements = BiasMeasurements()

    g1_bias_measurements.m = table.meta[tf.m.m1]
    g1_bias_measurements.m_err = table.meta[tf.m.m1_err]
    g1_bias_measurements.c = table.meta[tf.m.c1]
    g1_bias_measurements.c_err = table.meta[tf.m.c1_err]
    g1_bias_measurements.mc_covar = table.meta[tf.m.m1c1_covar]

    # Get g2 bias measurements

    g2_bias_measurements = BiasMeasurements()

    g2_bias_measurements.m = table.meta[tf.m.m2]
    g2_bias_measurements.m_err = table.meta[tf.m.m2_err]
    g2_bias_measurements.c = table.meta[tf.m.c2]
    g2_bias_measurements.c_err = table.meta[tf.m.c2_err]
    g2_bias_measurements.mc_covar = table.meta[tf.m.m2c2_covar]

    return g1_bias_measurements, g2_bias_measurements
