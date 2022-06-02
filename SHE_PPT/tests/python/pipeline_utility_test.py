""" @file pipeline_utility_test.py

    Created 9 Aug 2018

    Unit tests relating to pipeline utility functions.
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

__updated__ = "2021-08-12"

import os
import shutil
from argparse import Namespace
from typing import Any, Dict

import numpy as np
import pytest

from SHE_PPT import products
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.config import (AnalysisConfigKeys, CTI_GAL_VALIDATION_HEAD, CalibrationConfigKeys,
                                      GlobalConfigKeys,
                                      ReconciliationConfigKeys, SHEAR_BIAS_VALIDATION_HEAD, ValidationConfigKeys, )
from SHE_PPT.file_io import write_listfile, write_xml_product
from SHE_PPT.pipeline_utility import (_coerce_parsed_args_to_dict, _convert_config_types, archive_product,
                                      get_conditional_product,
                                      get_cti_gal_value,
                                      get_global_enum, get_global_value, get_shear_bias_value, get_task_value,
                                      read_analysis_config, read_calibration_config, read_config,
                                      read_reconciliation_config,
                                      read_scaling_config, write_analysis_config,
                                      write_calibration_config, write_config, write_reconciliation_config, )
from SHE_PPT.products.she_analysis_config import create_dpd_she_analysis_config
from SHE_PPT.testing.mock_mer_final_cat import MockMFCGalaxyTableGenerator
from SHE_PPT.testing.utility import SheTestCase


class TestUtility(SheTestCase):
    """Unit tests for the SHE_PPT.pipeline_utility module.
    """

    def post_setup(self):
        """Set up data used for multiple unit tests.
        """
        pass

    def test_get_task_value(self):
        """Unit test of the `get_task_value` function and its specialized versions.
        """

        # Test with providing the enum
        assert get_task_value(global_enum = ValidationConfigKeys.VAL_SNR_BIN_LIMITS,
                              task_head = CTI_GAL_VALIDATION_HEAD) == ValidationConfigKeys.CG_SNR_BIN_LIMITS.value

        # Test with providing the enum's value
        assert get_task_value(global_enum = ValidationConfigKeys.VAL_SNR_BIN_LIMITS.value,
                              task_head = CTI_GAL_VALIDATION_HEAD) == ValidationConfigKeys.CG_SNR_BIN_LIMITS.value

        # Test with specialized functions
        assert (get_cti_gal_value(global_enum = ValidationConfigKeys.VAL_SNR_BIN_LIMITS.value) ==
                ValidationConfigKeys.CG_SNR_BIN_LIMITS.value)
        assert (get_shear_bias_value(global_enum = ValidationConfigKeys.VAL_SNR_BIN_LIMITS.value) ==
                ValidationConfigKeys.SBV_SNR_BIN_LIMITS.value)

    def test_get_global_enum_value(self):
        """Unit test of the `get_global_enum` and `get_global_value` functions
        """

        # Test with providing the enum
        assert get_global_enum(task_value = ValidationConfigKeys.CG_SNR_BIN_LIMITS.value,
                               task_head = CTI_GAL_VALIDATION_HEAD) == ValidationConfigKeys.VAL_SNR_BIN_LIMITS

        # Test with providing the enum's value
        assert get_global_value(task_value = ValidationConfigKeys.CG_SNR_BIN_LIMITS.value,
                                task_head = CTI_GAL_VALIDATION_HEAD) == ValidationConfigKeys.VAL_SNR_BIN_LIMITS.value

    def test_archive_product(self):
        """Unit test of the `archive_product` function
        """

        # We'll set up some test files to work with, using a MER Final Catalog table and product

        mfc_table_gen = MockMFCGalaxyTableGenerator(workdir = self.workdir,
                                                    num_test_points = 2, )

        mfc_table_gen.write_mock_product()

        product_filename = mfc_table_gen.product_filename
        table_filename = mfc_table_gen.table_filename

        base_subdir_name = "archive_dir"
        qualified_base_subdir_name = os.path.join(self.workdir, base_subdir_name)
        qualified_subdir_name = os.path.join(qualified_base_subdir_name, os.path.split(self.workdir)[-1])

        # Delete the subdir if it already exists in the workdir, so that we can test it's properly created
        if os.path.exists(qualified_base_subdir_name):
            shutil.rmtree(qualified_base_subdir_name)

        # Test archiving the product
        archive_product(product_filename = product_filename,
                        archive_dir = qualified_base_subdir_name,
                        workdir = self.workdir)

        # Check that the product and table were copied to the archive directory
        assert os.path.exists(os.path.join(qualified_subdir_name, product_filename))
        assert os.path.exists(os.path.join(qualified_subdir_name, table_filename))

        # Check that we can also copy a non-product, getting only a warning
        table_filename_2 = "test_table_2.fits"
        shutil.copy(os.path.join(self.workdir, table_filename),
                    os.path.join(self.workdir, table_filename_2))
        archive_product(product_filename = table_filename_2,
                        archive_dir = qualified_base_subdir_name,
                        workdir = self.workdir)
        assert os.path.exists(os.path.join(qualified_subdir_name, table_filename_2))

    def test_rw_config(self):

        # Set up files to test reading in
        test1_filename = "data/test1.txt"
        product_filename = "test_product.xml"

        lf0_filename = "empty_listfile.json"
        lf1_filename = "one_listfile.json"
        lf2_filename = "two_listfile.json"

        # Test we get out of the file what we put in, for each type of configuration file

        test_analysis_dict = {AnalysisConfigKeys.ES_METHODS     : ShearEstimationMethods.KSB,
                              AnalysisConfigKeys.OID_BATCH_SIZE : "26",
                              AnalysisConfigKeys.OID_MAX_BATCHES: "3",
                              GlobalConfigKeys.PIP_PROFILE      : "T"}

        test_analysis_type_dict = {AnalysisConfigKeys.ES_METHODS     : (list, ShearEstimationMethods),
                                   AnalysisConfigKeys.OID_BATCH_SIZE : int,
                                   AnalysisConfigKeys.OID_MAX_BATCHES: int,
                                   GlobalConfigKeys.PIP_PROFILE      : bool}

        test_analysis_cline_args_dict = {AnalysisConfigKeys.ES_METHODS     : "methods",
                                         AnalysisConfigKeys.OID_BATCH_SIZE : "batch_size",
                                         AnalysisConfigKeys.OID_MAX_BATCHES: None}

        write_analysis_config(test_analysis_dict, test1_filename, workdir = self.workdir)
        analysis_config_product = create_dpd_she_analysis_config(test1_filename)
        write_xml_product(analysis_config_product, product_filename, workdir = self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [product_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, product_filename])

        read_dict1 = read_analysis_config(test1_filename,
                                          workdir = self.workdir,
                                          d_types = test_analysis_type_dict)

        # Check it's been read in correctly
        assert read_dict1[AnalysisConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict1[AnalysisConfigKeys.OID_BATCH_SIZE] == 26
        assert read_dict1[AnalysisConfigKeys.OID_MAX_BATCHES] == 3
        assert read_dict1[GlobalConfigKeys.PIP_PROFILE] is True

        # Check we get expected results from trying to read in other variants

        assert read_analysis_config(None, workdir = self.workdir) == {}
        assert read_analysis_config("", workdir = self.workdir) == {}
        assert read_analysis_config("None", workdir = self.workdir) == {}

        assert read_analysis_config(lf0_filename, workdir = self.workdir) == {}
        assert read_analysis_config(lf1_filename,
                                    workdir = self.workdir,
                                    d_types = test_analysis_type_dict) == read_dict1
        with pytest.raises(ValueError):
            read_analysis_config(lf2_filename, workdir = self.workdir)

        # Check that cline_args properly override values in the config dict
        read_dict_with_cline_args = read_analysis_config(lf1_filename,
                                                         workdir = self.workdir,
                                                         d_cline_args = test_analysis_cline_args_dict,
                                                         parsed_args = {"batch_size": "10",
                                                                        "methods"   : None},
                                                         d_types = test_analysis_type_dict)
        assert read_dict_with_cline_args[AnalysisConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict_with_cline_args[AnalysisConfigKeys.OID_BATCH_SIZE] == 10
        assert read_dict_with_cline_args[AnalysisConfigKeys.OID_MAX_BATCHES] == 3
        assert read_dict_with_cline_args[GlobalConfigKeys.PIP_PROFILE] is True

        # Test we get out of the file what we put in, for each type of configuration file

        test_reconciliation_dict = {ReconciliationConfigKeys.REC_METHOD: "Best"}

        write_reconciliation_config(test_reconciliation_dict, test1_filename, workdir = self.workdir)

        read_dict1 = read_reconciliation_config(test1_filename, workdir = self.workdir)

        # Check it's been read in correctly
        assert read_dict1[ReconciliationConfigKeys.REC_METHOD] == "Best"

        # Check we get expected results from trying to read in other variants

        assert read_reconciliation_config(lf1_filename, workdir = self.workdir) == read_dict1

        with pytest.raises(ValueError):
            read_reconciliation_config(lf2_filename, workdir = self.workdir)

        # Test we get out of the file what we put in, for each type of configuration file

        test_calibration_dict = {CalibrationConfigKeys.ES_METHODS : ShearEstimationMethods.KSB,
                                 CalibrationConfigKeys.CBM_CLEANUP: False}

        test_calibration_type_dict = {CalibrationConfigKeys.ES_METHODS : (list, ShearEstimationMethods),
                                      CalibrationConfigKeys.CBM_CLEANUP: bool}

        write_calibration_config(test_calibration_dict, test1_filename, workdir = self.workdir)

        read_dict1 = read_calibration_config(test1_filename,
                                             workdir = self.workdir,
                                             d_types = test_calibration_type_dict)

        # Check it's been read in correctly
        assert read_dict1[CalibrationConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict1[CalibrationConfigKeys.CBM_CLEANUP] == False

        # Check we get expected results from trying to read in other variants

        assert read_calibration_config(lf1_filename,
                                       workdir = self.workdir,
                                       d_types = test_calibration_type_dict) == read_dict1
        with pytest.raises(ValueError):
            read_calibration_config(lf2_filename, workdir = self.workdir)

        # Test that we can parse a more complicated file
        test2_filename = "test2.txt"
        with open(os.path.join(self.workdir, test2_filename), "w") as fo:
            fo.write(f"{AnalysisConfigKeys.ES_METHODS.value} = KSB\n"
                     f"{AnalysisConfigKeys.OID_BATCH_SIZE.value} = 26\n"
                     f"{AnalysisConfigKeys.REMAP_NUM_THREADS_EXP.value} = 8 # nope\n"
                     f"# ignore this = ignore\n"
                     f"\n"
                     f"{AnalysisConfigKeys.REMAP_NUM_SWARP_THREADS_EXP.value}=4 #==2\n")

        read_dict2 = read_analysis_config(test2_filename, workdir = self.workdir,
                                          d_types = {AnalysisConfigKeys.ES_METHODS          : (
                                              list, ShearEstimationMethods),
                                              AnalysisConfigKeys.OID_BATCH_SIZE             : int,
                                              AnalysisConfigKeys.REMAP_NUM_THREADS_EXP      : int,
                                              AnalysisConfigKeys.REMAP_NUM_SWARP_THREADS_EXP: int, })

        assert read_dict2[AnalysisConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict2[AnalysisConfigKeys.OID_BATCH_SIZE] == 26
        assert read_dict2[AnalysisConfigKeys.REMAP_NUM_THREADS_EXP] == 8
        assert read_dict2[AnalysisConfigKeys.REMAP_NUM_SWARP_THREADS_EXP] == 4
        assert "ignore this" not in read_dict2

        # Test the `read_scaling_config` function simply - the more complicated paths are covered by other tests above
        assert read_scaling_config(None, workdir = self.workdir) == {}

    def test_read_validation_config(self):
        """Unit tests of read_config, focused on special handling for the validation config keys.
        """

        # Test the ValidationConfigKeys can be read in, using task_head for overriding keys

        test_validation_dict = {ValidationConfigKeys.CG_SNR_BIN_LIMITS    : "0 2 4",
                                ValidationConfigKeys.CG_BG_BIN_LIMITS     : None,
                                ValidationConfigKeys.SBV_SNR_BIN_LIMITS   : "0 3 6",
                                ValidationConfigKeys.SBV_BG_BIN_LIMITS    : None,
                                ValidationConfigKeys.VAL_SNR_BIN_LIMITS   : "0 1 2",
                                ValidationConfigKeys.VAL_BG_BIN_LIMITS    : "1 2 3",
                                ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS: "2 3 4",
                                }

        test_validation_types_dict = {ValidationConfigKeys.CG_SNR_BIN_LIMITS    : np.ndarray,
                                      ValidationConfigKeys.CG_BG_BIN_LIMITS     : np.ndarray,
                                      ValidationConfigKeys.CG_COLOUR_BIN_LIMITS : np.ndarray,
                                      ValidationConfigKeys.SBV_SNR_BIN_LIMITS   : np.ndarray,
                                      ValidationConfigKeys.SBV_BG_BIN_LIMITS    : np.ndarray,
                                      ValidationConfigKeys.SBV_COLOUR_BIN_LIMITS: np.ndarray,
                                      ValidationConfigKeys.VAL_SNR_BIN_LIMITS   : np.ndarray,
                                      ValidationConfigKeys.VAL_BG_BIN_LIMITS    : np.ndarray,
                                      ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS: np.ndarray,
                                      }

        test_validation_defaults_dict = {ValidationConfigKeys.CG_SNR_BIN_LIMITS    : np.array([0, 20, 40]),
                                         ValidationConfigKeys.CG_BG_BIN_LIMITS     : np.array([20, 40, 60]),
                                         ValidationConfigKeys.CG_COLOUR_BIN_LIMITS : np.array([40, 60, 80]),
                                         ValidationConfigKeys.CG_SIZE_BIN_LIMITS   : np.array([60, 80, 100]),
                                         ValidationConfigKeys.SBV_SNR_BIN_LIMITS   : np.array([0, 30, 60]),
                                         ValidationConfigKeys.SBV_BG_BIN_LIMITS    : np.array([30, 60, 90]),
                                         ValidationConfigKeys.SBV_COLOUR_BIN_LIMITS: np.array([60, 90, 120]),
                                         ValidationConfigKeys.SBV_SIZE_BIN_LIMITS  : np.array([90, 120, 150]),
                                         ValidationConfigKeys.VAL_SNR_BIN_LIMITS   : np.array([0, 10, 20]),
                                         ValidationConfigKeys.VAL_BG_BIN_LIMITS    : np.array([10, 20, 30]),
                                         ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS: np.array([20, 30, 40]),
                                         ValidationConfigKeys.VAL_SIZE_BIN_LIMITS  : np.array([30, 40, 50]),
                                         }

        write_config(test_validation_dict, test1_filename, workdir = self.workdir, config_keys = ValidationConfigKeys)

        # Read in and test with no task head
        read_dict_no_task_head = read_config(test1_filename,
                                             workdir = self.workdir,
                                             config_keys = ValidationConfigKeys,
                                             d_types = test_validation_types_dict,
                                             d_defaults = test_validation_defaults_dict)
        assert np.all(read_dict_no_task_head[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] == np.array([0, 1, 2]))
        assert np.all(read_dict_no_task_head[ValidationConfigKeys.VAL_BG_BIN_LIMITS] == np.array([1, 2, 3]))
        assert np.all(read_dict_no_task_head[ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS] == np.array([2, 3, 4]))
        assert np.all(read_dict_no_task_head[ValidationConfigKeys.VAL_SIZE_BIN_LIMITS] == np.array([30, 40, 50]))

        # Read in and test with CTI-Gal task head
        read_dict_cti_gal = read_config(test1_filename,
                                        workdir = self.workdir,
                                        config_keys = ValidationConfigKeys,
                                        d_types = test_validation_types_dict,
                                        d_defaults = test_validation_defaults_dict,
                                        task_head = CTI_GAL_VALIDATION_HEAD)
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] == np.array([0, 2, 4]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.VAL_BG_BIN_LIMITS] == np.array([1, 2, 3]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS] == np.array([2, 3, 4]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.VAL_SIZE_BIN_LIMITS] == np.array([30, 40, 50]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.CG_SNR_BIN_LIMITS] == np.array([0, 2, 4]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.CG_BG_BIN_LIMITS] == np.array([1, 2, 3]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.CG_COLOUR_BIN_LIMITS] == np.array([2, 3, 4]))
        assert np.all(read_dict_cti_gal[ValidationConfigKeys.CG_SIZE_BIN_LIMITS] == np.array([30, 40, 50]))

        # Read in and test with Shear Bias Validation task head
        read_dict_sbv = read_config(test1_filename,
                                    workdir = self.workdir,
                                    config_keys = ValidationConfigKeys,
                                    d_types = test_validation_types_dict,
                                    d_defaults = test_validation_defaults_dict,
                                    task_head = SHEAR_BIAS_VALIDATION_HEAD)
        assert np.all(read_dict_sbv[ValidationConfigKeys.VAL_SNR_BIN_LIMITS] == np.array([0, 3, 6]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.VAL_BG_BIN_LIMITS] == np.array([1, 2, 3]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.VAL_COLOUR_BIN_LIMITS] == np.array([2, 3, 4]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.VAL_SIZE_BIN_LIMITS] == np.array([30, 40, 50]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.SBV_SNR_BIN_LIMITS] == np.array([0, 3, 6]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.SBV_BG_BIN_LIMITS] == np.array([1, 2, 3]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.SBV_COLOUR_BIN_LIMITS] == np.array([2, 3, 4]))
        assert np.all(read_dict_sbv[ValidationConfigKeys.SBV_SIZE_BIN_LIMITS] == np.array([30, 40, 50]))

        # Test that we get a ValueError if providing task_head for the wrong pipeline type
        with pytest.raises(ValueError):
            _ = read_config(None,
                            workdir = self.workdir,
                            config_keys = ReconciliationConfigKeys,
                            task_head = CTI_GAL_VALIDATION_HEAD)

        # Check that it handles a list of config_keys fine
        assert read_config(None,
                           workdir = self.workdir,
                           config_keys = (ReconciliationConfigKeys, ValidationConfigKeys)) == {}

    def test_coerce_parsed_args_to_dict(self):
        """Unit test of the `coerce_parsed_args_to_dict` function.
        """

        # Test None
        assert _coerce_parsed_args_to_dict(None) == {}

        # Test dict
        test_dict = {"a": 1, "b": 2}
        assert _coerce_parsed_args_to_dict(test_dict) == test_dict

        # Test Namespace
        test_namespace = Namespace(**test_dict)
        assert _coerce_parsed_args_to_dict(test_namespace) == test_dict

    def test_get_conditional_product(self):
        # We'll set up some test files to work with, using the object_id_list product

        product_filename = "object_id_list.xml"
        lf0_filename = "empty_listfile.json"
        lf1_filename = "one_listfile.json"
        lf2_filename = "two_listfile.json"

        object_ids = [1, 2]

        product = products.she_object_id_list.create_object_id_list_product(object_ids)
        write_xml_product(product, product_filename, workdir = self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [product_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [product_filename, product_filename])

        # Test that we get the expected result in each case

        assert get_conditional_product(None, workdir = self.workdir) is None
        assert get_conditional_product("", workdir = self.workdir) is None
        assert get_conditional_product("None", workdir = self.workdir) is None

        assert get_conditional_product(product_filename, workdir = self.workdir).get_id_list() == object_ids

        assert get_conditional_product(lf0_filename, workdir = self.workdir) is None
        assert get_conditional_product(lf1_filename, workdir = self.workdir).get_id_list() == object_ids
        with pytest.raises(ValueError):
            get_conditional_product(lf2_filename, workdir = self.workdir)

    def test_convert_config_types(self):
        """Runs tests of the convert_config_typesfunction.
        """

        # Make mock input data
        config = {"want_float"                          : "0.",
                  "want_array"                          : "0. 1",
                  "want_true"                           : "True",
                  "want_false"                          : "False",
                  "want_enum"                           : GlobalConfigKeys.PIP_PROFILE.value.upper(),
                  "want_int_list"                       : "0 1 7",
                  "want_float_list"                     : "0 10 4.5",
                  "want_int_from_int_or_int_list"       : "17",
                  "want_int_list_from_int_or_int_list"  : "4 1",
                  "want_ndarray_from_ndarray_or_str"    : "1 2 3",
                  "want_str_from_ndarray_or_str"        : "auto",
                  "want_enum_list_from_enum_list_or_str": (f"{GlobalConfigKeys.PIP_PLACEHOLDER_0.value.upper()} "
                                                           f"{GlobalConfigKeys.PIP_PLACEHOLDER_1.value.upper()}"),
                  "want_str_from_enum_list_or_str"      : "N/A"}
        d_types = {"want_float"                          : float,
                   "want_array"                          : np.ndarray,
                   "want_true"                           : bool,
                   "want_false"                          : bool,
                   "want_enum"                           : GlobalConfigKeys,
                   "want_int_list"                       : (list, int),
                   "want_float_list"                     : (list, float),
                   "want_int_from_int_or_int_list"       : (int, (list, int)),
                   "want_int_list_from_int_or_int_list"  : (int, (list, int)),
                   "want_ndarray_from_ndarray_or_str"    : (np.ndarray, str),
                   "want_str_from_ndarray_or_str"        : (np.ndarray, str),
                   "want_enum_list_from_enum_list_or_str": ((list, GlobalConfigKeys), str),
                   "want_str_from_enum_list_or_str"      : ((list, GlobalConfigKeys), str)}

        # Run the function
        new_config: Dict[str, Any] = _convert_config_types(pipeline_config = config,
                                                           d_types = d_types)

        # Check the results
        assert np.isclose(new_config["want_float"], 0.)
        assert np.allclose(new_config["want_array"], np.array([0., 1.]))
        assert new_config["want_true"] == True
        assert new_config["want_false"] == False
        assert new_config["want_enum"] == GlobalConfigKeys.PIP_PROFILE

        assert new_config["want_int_list"] == [0, 1, 7]
        assert np.allclose(new_config["want_float_list"], [0., 10., 4.5])

        assert new_config["want_int_from_int_or_int_list"] == 17
        assert new_config["want_int_list_from_int_or_int_list"] == [4, 1]

        assert np.all(new_config["want_ndarray_from_ndarray_or_str"] == np.array([1, 2, 3]))
        assert new_config["want_str_from_ndarray_or_str"] == "auto"

        assert new_config["want_enum_list_from_enum_list_or_str"] == [GlobalConfigKeys.PIP_PLACEHOLDER_0,
                                                                      GlobalConfigKeys.PIP_PLACEHOLDER_1]
        assert new_config["want_str_from_enum_list_or_str"] == "N/A"
