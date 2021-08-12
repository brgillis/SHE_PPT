""" @file table_formats_test.py

    Created 24 Aug 2017

    Unit tests relating to table formats.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from astropy.table import Column, Table
import pytest

from SHE_PPT.constants.fits import PSF_CAT_TAG
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_bias_statistics import tf as bs_tf
from SHE_PPT.table_formats.she_common_calibration import tf as cc_tf
from SHE_PPT.table_formats.she_galaxy_population_priors import tf as gpp_tf
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf
from SHE_PPT.table_formats.she_ksb_training import tf as ksbt_tf
from SHE_PPT.table_formats.she_ksb_tu_matched import tf as ksbtm_tf
from SHE_PPT.table_formats.she_lensmc_chains import tf as lmcc_tf, len_chain
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf
from SHE_PPT.table_formats.she_lensmc_tu_matched import tf as lmctm_tf
from SHE_PPT.table_formats.she_measurements import tf as sm_tf
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf
from SHE_PPT.table_formats.she_momentsml_tu_matched import tf as mmltm_tf
from SHE_PPT.table_formats.she_p_of_e import tf as poe_tf
from SHE_PPT.table_formats.she_psf_dm_state import tff as psfdmf_tf, tfc as psfdmc_tf
from SHE_PPT.table_formats.she_psf_model_image import tf as psfm_tf
from SHE_PPT.table_formats.she_psf_om_state import tff as psfomf_tf, tfc as psfomc_tf
from SHE_PPT.table_formats.she_psf_pd_state import tff as psfpdf_tf, tfc as psfpdc_tf
from SHE_PPT.table_formats.she_psf_tm_state import tff as psftmf_tf, tfc as psftmc_tf
from SHE_PPT.table_formats.she_psf_tml_state import tff as psftmlf_tf, tfc as psftmlc_tf
from SHE_PPT.table_formats.she_psf_zm_state import tff as psfzmf_tf, tfc as psfzmc_tf
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf
from SHE_PPT.table_formats.she_regauss_training import tf as regt_tf
from SHE_PPT.table_formats.she_regauss_tu_matched import tf as regtm_tf
from SHE_PPT.table_formats.she_simulated_catalog import tf as simc_tf
from SHE_PPT.table_formats.she_simulation_plan import tf as simp_tf
from SHE_PPT.table_formats.she_star_catalog import tf as sc_tf
from SHE_PPT.table_formats.she_tu_matched import tf as tum_tf
from SHE_PPT.table_testing import _test_is_in_format
from SHE_PPT.table_utility import is_in_format, add_row
import numpy as np


class TestTableFormats:
    """


    """

    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats = [bs_tf,
                       cc_tf,
                       gpp_tf,
                       ksbm_tf,
                       ksbtm_tf,
                       ksbt_tf,
                       lmcc_tf,
                       lmcm_tf,
                       lmctm_tf,
                       mfc_tf,
                       mmlm_tf,
                       mmltm_tf,
                       poe_tf,
                       psfdmf_tf,
                       psfdmc_tf,
                       psfm_tf,
                       psfomf_tf,
                       psfomc_tf,
                       psfpdf_tf,
                       psfpdc_tf,
                       psftmf_tf,
                       psftmc_tf,
                       psftmlf_tf,
                       psftmlc_tf,
                       psfzmf_tf,
                       psfzmc_tf,
                       regm_tf,
                       regtm_tf,
                       regt_tf,
                       simc_tf,
                       simp_tf,
                       sc_tf,
                       ]

        cls.parent_format = sm_tf
        cls.child_initializers = [ksbm_tf.init_table,
                                  lmcm_tf.init_table,
                                  mmlm_tf.init_table,
                                  regm_tf.init_table,
                                  ]

        cls.filename_base = "test_table"

        cls.filenames = [cls.filename_base + ".ecsv", cls.filename_base + ".fits"]

    @classmethod
    def teardown_class(cls):
        del cls.formats

        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)

    def test_extra_data(self):
        # Check that the keys are assigned correctly for all extra data (eg. comments)

        # Loop over all formats
        for tf in self.formats:

            # Check metadata comments
            assert list(tf.m.comments.keys()) == tf.m.all

            # Check column comments
            assert list(tf.comments.keys()) == tf.all

            # Check column dtypes
            assert list(tf.dtypes.keys()) == tf.all

            # Check column fits dtypes
            assert list(tf.fits_dtypes.keys()) == tf.all

            # Check column lengths
            assert list(tf.lengths.keys()) == tf.all

    def test_is_in_format(self):

        # Call the test stored in the table_testing module (to re-use code with other projects)
        _test_is_in_format(self)

    def test_base_is_in_format(self):

        # is_in_format behaves as expected when testing with a base format

        empty_tables = []

        for init in self.child_initializers:
            empty_tables.append(init())

        for i in range(len(self.child_initializers)):

            # Try non-strict test
            if not is_in_format(empty_tables[i], self.parent_format, strict=False, verbose=True):
                raise ValueError("Table format " + self.parent_format.m.table_format +
                                 " doesn't match initialized child table " + str(i) + ".")

    def test_add_row(self):
        # Test that we can add a row through kwargs

        tab = initialise_mer_final_catalog()

        add_row(tab, **{mfc_tf.ID: 0, mfc_tf.gal_x_world: 0, mfc_tf.gal_y_world: 1})

        assert tab[mfc_tf.ID][0] == 0
        assert tab[mfc_tf.gal_x_world][0] == 0.
        assert tab[mfc_tf.gal_y_world][0] == 1.

    def test_init(self):

        model_hash = -1235
        model_seed = 4422
        noise_seed = 11015

        # Test initialization methods

        mer_final_catalog = mfc_tf.init_table(model_hash=model_hash,
                                              model_seed=model_seed,
                                              noise_seed=noise_seed)

        _ = simc_tf.init_table(model_hash=model_hash,
                               model_seed=model_seed,
                               noise_seed=noise_seed)

        psf_table = psfm_tf.init_table()

        assert(psf_table.meta[psfm_tf.m.extname] == PSF_CAT_TAG)

        # Try to initialize the shear estimates table based on the detections table

        _ = lmcm_tf.init_table(mer_final_catalog)

        shear_chains_table = lmcc_tf.init_table(mer_final_catalog)

        assert(shear_chains_table.meta[lmcc_tf.m.len_chain] == len_chain)
