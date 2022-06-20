""" @file lensmc_measurements_table_format_test.py

    Created 07 July 2020

    Unit tests for the LensMC table format, to confirm it behaves as expected.
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

__updated__ = "2021-02-09"

from SHE_PPT.table_formats.she_lensmc_measurements import initialise_lensmc_measurements_table, tf as tf
from SHE_PPT.testing.utility import SheTestCase


class TestLensMcMeasurementsTableFormat(SheTestCase):
    """ Unit tests class for LensMC Measurements Table Format
    """

    def post_setup(self):
        # Define a list of the table formats we'll be testing
        self.table = initialise_lensmc_measurements_table(optional_columns = [tf.m1_ical,
                                                                              tf.m2_ical,
                                                                              tf.shape_weight,
                                                                              tf.shape_weight_uncal])

    def test_meta(self):
        # Run through all the meta variables and check that they exist in the table format and table
        _ = self.table.meta[tf.m.fits_version]
        _ = self.table.meta[tf.m.fits_def]
        _ = self.table.meta[tf.m.she_flag_version]
        _ = self.table.meta[tf.m.model_hash]
        _ = self.table.meta[tf.m.model_seed]
        _ = self.table.meta[tf.m.noise_seed]
        _ = self.table.meta[tf.m.observation_id]
        _ = self.table.meta[tf.m.pointing_id]
        _ = self.table.meta[tf.m.observation_time]
        _ = self.table.meta[tf.m.tile_id]

        return

    def test_columns(self):
        # Run through all the column name variables and check that they exist in the table format and table
        _ = self.table[tf.ID]

        _ = self.table[tf.fit_flags]
        _ = self.table[tf.val_flags]
        _ = self.table[tf.fit_class]
        _ = self.table[tf.nexp]
        _ = self.table[tf.unmasked_fraction]
        _ = self.table[tf.rec_flags]

        _ = self.table[tf.g1]
        _ = self.table[tf.g1_err]
        _ = self.table[tf.e1_err]
        _ = self.table[tf.g2]
        _ = self.table[tf.g2_err]
        _ = self.table[tf.e2_err]
        _ = self.table[tf.g1g2_covar]
        _ = self.table[tf.e1e2_covar]
        _ = self.table[tf.weight]
        _ = self.table[tf.shape_weight]
        _ = self.table[tf.g1_uncal]
        _ = self.table[tf.g1_uncal_err]
        _ = self.table[tf.e1_uncal_err]
        _ = self.table[tf.g2_uncal]
        _ = self.table[tf.g2_uncal_err]
        _ = self.table[tf.e2_uncal_err]
        _ = self.table[tf.g1g2_uncal_covar]
        _ = self.table[tf.e1e2_uncal_covar]
        _ = self.table[tf.weight_uncal]
        _ = self.table[tf.shape_weight_uncal]

        _ = self.table[tf.ra]
        _ = self.table[tf.ra_err]
        _ = self.table[tf.dec]
        _ = self.table[tf.dec_err]

        _ = self.table[tf.re]
        _ = self.table[tf.re_err]
        _ = self.table[tf.flux]
        _ = self.table[tf.flux_err]
        _ = self.table[tf.snr]
        _ = self.table[tf.snr_err]
        _ = self.table[tf.bulge_frac]
        _ = self.table[tf.bulge_frac_err]
        _ = self.table[tf.gal_pvalue]
        _ = self.table[tf.chi2]
        _ = self.table[tf.dof]
        _ = self.table[tf.acc]
        _ = self.table[tf.m1_ical]
        _ = self.table[tf.m2_ical]

        return
