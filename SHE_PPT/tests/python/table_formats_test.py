""" @file table_formats_test.py

    Created 24 Aug 2017

    Unit tests relating to table formats.
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

__updated__ = "2020-06-24"

import os

from astropy.table import Column, Table
import pytest

from SHE_PPT import magic_values as mv
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf, initialise_mer_final_catalog
from SHE_PPT.table_formats.she_bfd_bias_statistics import tf as bfdb_tf, initialise_bfd_bias_statistics_table
from SHE_PPT.table_formats.she_bfd_moments import tf as bfdm_tf, initialise_bfd_moments_table
from SHE_PPT.table_formats.she_bfd_training import tf as bfdt_tf, initialise_bfd_training_table
from SHE_PPT.table_formats.she_bias_statistics import tf as bs_tf, initialise_bias_statistics_table
from SHE_PPT.table_formats.she_common_calibration import tf as cc_tf, initialise_common_calibration_table
from SHE_PPT.table_formats.she_galaxy_population_priors import tf as gpp_tf, initialise_galaxy_population_priors_table
from SHE_PPT.table_formats.she_ksb_measurements import tf as ksbm_tf, initialise_ksb_measurements_table
from SHE_PPT.table_formats.she_ksb_training import tf as ksbt_tf, initialise_ksb_training_table
from SHE_PPT.table_formats.she_lensmc_chains import tf as lmcc_tf, initialise_lensmc_chains_table, len_chain
from SHE_PPT.table_formats.she_lensmc_measurements import tf as lmcm_tf, initialise_lensmc_measurements_table
from SHE_PPT.table_formats.she_momentsml_measurements import tf as mmlm_tf, initialise_momentsml_measurements_table
from SHE_PPT.table_formats.she_p_of_e import tf as poe_tf, initialise_p_of_e_table
from SHE_PPT.table_formats.she_psf_dm_state import tff as psfdmf_tf, tfc as dmtc, initialise_psf_dm_state_table
from SHE_PPT.table_formats.she_psf_model_image import tf as psfm_tf, initialise_psf_table
from SHE_PPT.table_formats.she_psf_om_state import tff as psfomf_tf, tfc as omtc_tf, initialise_psf_om_state_table
from SHE_PPT.table_formats.she_psf_pd_state import tff as psfpdf_tf, tfc as pdtc_tf, initialise_psf_pd_state_table
from SHE_PPT.table_formats.she_psf_tm_state import tff as psftmf_tf, tfc as tmtc_tf, initialise_psf_tm_state_table
from SHE_PPT.table_formats.she_psf_zm_state import tff as psfzmf_tf, tfc as psfzmc_tf, initialise_psf_zm_state_table
from SHE_PPT.table_formats.she_regauss_measurements import tf as regm_tf, initialise_regauss_measurements_table
from SHE_PPT.table_formats.she_regauss_training import tf as regt_tf, initialise_regauss_training_table
from SHE_PPT.table_formats.she_simulated_catalog import tf as simc_tf, initialise_simulated_catalog
from SHE_PPT.table_formats.she_simulation_plan import tf as simp_tf, initialise_simulation_plan_table
from SHE_PPT.table_formats.she_star_catalog import tf as sc_tf, initialise_star_catalog
from SHE_PPT.table_utility import is_in_format, add_row
import numpy as np


class TestTableFormats:
    """


    """

    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats_and_initializers = [(bfdb_tf, initialise_bfd_bias_statistics_table),
                                        (bfdm_tf, initialise_bfd_moments_table),
                                        (bfdt_tf, initialise_bfd_training_table),
                                        (bs_tf, initialise_bias_statistics_table),
                                        (cc_tf, initialise_common_calibration_table),
                                        (gpp_tf, initialise_galaxy_population_priors_table),
                                        (ksbm_tf, initialise_ksb_measurements_table),
                                        (ksbt_tf, initialise_ksb_training_table),
                                        (lmcc_tf, initialise_lensmc_chains_table),
                                        (lmcm_tf, initialise_lensmc_measurements_table),
                                        (mfc_tf, initialise_mer_final_catalog),
                                        (mmlm_tf, initialise_momentsml_measurements_table),
                                        (poe_tf, initialise_p_of_e_table),
                                        (psfdmf_tf, initialise_psf_dm_state_table),
                                        (psfm_tf, initialise_psf_table),
                                        (psfomf_tf, initialise_psf_om_state_table),
                                        (psfpdf_tf, initialise_psf_pd_state_table),
                                        (psftmf_tf, initialise_psf_tm_state_table),
                                        (psfzmf_tf, initialise_psf_zm_state_table),
                                        (regm_tf, initialise_regauss_measurements_table),
                                        (regt_tf, initialise_regauss_training_table),
                                        (simc_tf, initialise_simulated_catalog),
                                        (simp_tf, initialise_simulation_plan_table),
                                        (sc_tf, initialise_star_catalog),
                                        ]
                                        # (, ),

        cls.formats, cls.initializers = zip(*cls.formats_and_initializers)

        cls.filename_base = "test_table"

        cls.filenames = [cls.filename_base + ".ecsv", cls.filename_base + ".fits"]

        return

    @classmethod
    def teardown_class(cls):
        del cls.formats, cls.initializers

        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)

        return

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

        return

    def test_is_in_format(self):
        # Test each format is detected correctly

        empty_tables = []

        for init in self.initializers:
            empty_tables.append(init())

        assert len(self.initializers) == len(self.formats)

        for i in range(len(self.initializers)):

            # Try strict test
            for j in range((len(self.formats))):
                if i == j and not is_in_format(empty_tables[i], self.formats[j], strict=True):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " doesn't initialize a valid table" +
                                    " in strict test.")
                elif i != j and is_in_format(empty_tables[i], self.formats[j], strict=True):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " resolves true for tables of format " + self.formats[i].m.table_format +
                                    " in strict test.")

            # Try non-strict version now
            empty_tables[i].add_column(Column(name='new_column', data=np.zeros((0,))))
            for j in range((len(self.formats))):
                if i == j and not is_in_format(empty_tables[i], self.formats[j], strict=False):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " doesn't initialize a valid table" +
                                    " in non-strict test.")
                elif i != j and is_in_format(empty_tables[i], self.formats[j], strict=False):
                    raise Exception("Table format " + self.formats[j].m.table_format +
                                    " resolves true for tables of format " + self.formats[i].m.table_format +
                                    " in non-strict test.")

        return

    def test_add_row(self):
        # Test that we can add a row through kwargs

        tab = initialise_mer_final_catalog()

        add_row(tab, **{mfc_tf.ID: 0, mfc_tf.gal_x_world: 0, mfc_tf.gal_y_world: 1})

        assert tab[mfc_tf.ID][0] == 0
        assert tab[mfc_tf.gal_x_world][0] == 0.
        assert tab[mfc_tf.gal_y_world][0] == 1.

        return

    def test_init(self):

        model_hash = -1235
        model_seed = 4422
        noise_seed = 11015

        # Test initialization methods

        mer_final_catalog = initialise_mer_final_catalog(model_hash=model_hash,
                                                       model_seed=model_seed,
                                                       noise_seed=noise_seed)

        assert(mer_final_catalog.meta[mfc_tf.m.model_hash] == model_hash)
        assert(mer_final_catalog.meta[mfc_tf.m.model_seed] == model_seed)
        assert(mer_final_catalog.meta[mfc_tf.m.noise_seed] == noise_seed)

        _details_table = initialise_simulated_catalog(model_hash=model_hash,
                                                  model_seed=model_seed,
                                                  noise_seed=noise_seed)

        psf_table = initialise_psf_table()

        assert(psf_table.meta[psfm_tf.m.extname] == mv.psf_cat_tag)

        # Try to initialize the shear estimates table based on the detections table

        mer_final_catalog.meta[mfc_tf.m.model_hash] = model_hash
        mer_final_catalog.meta[mfc_tf.m.model_seed] = model_seed
        mer_final_catalog.meta[mfc_tf.m.noise_seed] = noise_seed

        shear_estimates_table = initialise_lensmc_measurements_table(mer_final_catalog)

        assert(shear_estimates_table.meta[lmcm_tf.m.model_hash] == model_hash)
        assert(shear_estimates_table.meta[lmcm_tf.m.model_seed] == model_seed)
        assert(shear_estimates_table.meta[lmcm_tf.m.noise_seed] == noise_seed)

        shear_chains_table = initialise_lensmc_chains_table(mer_final_catalog)

        assert(shear_chains_table.meta[lmcm_tf.m.model_hash] == model_hash)
        assert(shear_chains_table.meta[lmcm_tf.m.model_seed] == model_seed)
        assert(shear_chains_table.meta[lmcm_tf.m.noise_seed] == noise_seed)

        assert(shear_chains_table.meta[lmcc_tf.m.len_chain] == len_chain)

        return
