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
from typing import Any, Dict

import numpy as np
import pytest

from SHE_PPT import products
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.file_io import write_listfile, write_xml_product
from SHE_PPT.pipeline_utility import (AnalysisConfigKeys, CalibrationConfigKeys, GlobalConfigKeys,
                                      ReconciliationConfigKeys, _convert_config_types, get_conditional_product,
                                      read_analysis_config, read_calibration_config, read_reconciliation_config,
                                      write_analysis_config, write_calibration_config, write_reconciliation_config, )


class TestUtility:
    """


    """

    @classmethod
    def setup_class(cls):
        return

    @classmethod
    def teardown_class(cls):
        return

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath

    def test_rw_config(self):
        test1_filename = "test1.txt"

        lf0_filename = "empty_listfile.json"
        lf1_filename = "one_listfile.json"
        lf2_filename = "two_listfile.json"

        # Test we get out of the file what we put in, for each type of configuration file

        test_analysis_dict = {AnalysisConfigKeys.ES_METHODS    : ShearEstimationMethods.KSB,
                              AnalysisConfigKeys.OID_BATCH_SIZE: "26"}

        test_analysis_type_dict = {AnalysisConfigKeys.ES_METHODS    : (list, ShearEstimationMethods),
                                   AnalysisConfigKeys.OID_BATCH_SIZE: int}

        write_analysis_config(test_analysis_dict, test1_filename, workdir = self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_analysis_config(test1_filename,
                                          workdir = self.workdir,
                                          d_types = test_analysis_type_dict)

        # Check it's been read in correctly
        assert read_dict1[AnalysisConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict1[AnalysisConfigKeys.OID_BATCH_SIZE] == 26

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

        # Test we get out of the file what we put in, for each type of configuration file

        test_reconciliation_dict = {ReconciliationConfigKeys.REC_METHOD: "Best"}

        write_reconciliation_config(test_reconciliation_dict, test1_filename, workdir = self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_reconciliation_config(test1_filename, workdir = self.workdir)

        # Check it's been read in correctly
        assert read_dict1[ReconciliationConfigKeys.REC_METHOD] == "Best"

        # Check we get expected results from trying to read in other variants

        assert read_reconciliation_config(None, workdir = self.workdir) == {}
        assert read_reconciliation_config("", workdir = self.workdir) == {}
        assert read_reconciliation_config("None", workdir = self.workdir) == {}

        assert read_reconciliation_config(lf0_filename, workdir = self.workdir) == {}
        assert read_reconciliation_config(lf1_filename, workdir = self.workdir) == read_dict1
        with pytest.raises(ValueError):
            read_reconciliation_config(lf2_filename, workdir = self.workdir)

        # Test we get out of the file what we put in, for each type of configuration file

        test_calibration_dict = {CalibrationConfigKeys.ES_METHODS : ShearEstimationMethods.KSB,
                                 CalibrationConfigKeys.CBM_CLEANUP: False}

        test_calibration_type_dict = {CalibrationConfigKeys.ES_METHODS : (list, ShearEstimationMethods),
                                      CalibrationConfigKeys.CBM_CLEANUP: bool}

        write_calibration_config(test_calibration_dict, test1_filename, workdir = self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_calibration_config(test1_filename,
                                             workdir = self.workdir,
                                             d_types = test_calibration_type_dict)

        # Check it's been read in correctly
        assert read_dict1[CalibrationConfigKeys.ES_METHODS] == [ShearEstimationMethods.KSB]
        assert read_dict1[CalibrationConfigKeys.CBM_CLEANUP] == False

        # Check we get expected results from trying to read in other variants

        assert read_calibration_config(None, workdir = self.workdir) == {}
        assert read_calibration_config("", workdir = self.workdir) == {}
        assert read_calibration_config("None", workdir = self.workdir) == {}

        assert read_calibration_config(lf0_filename, workdir = self.workdir) == {}
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
        """ Runs tests of the convert_config_types function.
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
