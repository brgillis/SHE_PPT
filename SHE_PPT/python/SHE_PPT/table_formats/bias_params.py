#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
:file: python/SHE_PPT/table_formats/bias_params.py

:date: 24/04/2023
:author: Gordon Gibb

"""

from SHE_PPT.table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format


fits_version = "9.0"
fits_def = "she.biasParams"


class BiasParamsMeta(SheTableMeta):

    """
    Class that defines the bias params metadata
    """

    __version__ = fits_version

    table_format = fits_def
    fits_version = fits_version

    method = "METHOD"
    model = "MODEL"

    def init_meta(self, **kwargs):
        return super().init_meta(**kwargs)


class BiasParamsFormat(SheTableFormat):
    """
    class defining the phz catalogue table format
    """

    meta_type = BiasParamsMeta

    def __init__(self):
        super().__init__()

        self.tom_bin_id = self.set_column_properties(name="TOM_BIN_ID", dtype=">i4")
        self.num_objs = self.set_column_properties(name="NUM_OBJECTS", dtype=">i4")
        # NOTE: spin and linear models have 4 params so this format ddescribes these.
        # The multi model has 6 params, so the table format is invalid for this method.
        # The multi method is not expected to be used in production however
        self.params = self.set_column_properties(name="PARAMS", dtype=">f8", length=4)
        self.param_covars = self.set_column_properties(name="PARAM_COVARS", dtype=">f8", length=16)

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """Bound alias to the free table initialisation function, using this table format."""

        return initialise_bias_params(*args, **kwargs)


# Define an instance of this object that can be imported
bias_params_format = BiasParamsFormat()

# And a convenient alias for it
tf = bias_params_format


def initialise_bias_params(size=None, optional_columns=None, init_cols=None):
    """
    Initialise a bias params table
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    t = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    t.meta = tf.m.init_meta()

    assert is_in_format(t, tf)

    return t
