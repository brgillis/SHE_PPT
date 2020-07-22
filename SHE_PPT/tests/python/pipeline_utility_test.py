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

__updated__ = "2020-07-22"

import os
import pytest

from SHE_PPT import products
from SHE_PPT.file_io import write_xml_product, read_xml_product, write_listfile
from SHE_PPT.pipeline_utility import (read_analysis_config, write_analysis_config,
                                      read_reconciliation_config, write_reconciliation_config,
                                      read_calibration_config, write_calibration_config,
                                      get_conditional_product)


class TestUtility:
    """


    """

    @classmethod
    def setup_class(cls):
        return

    @classmethod
    def teardown_class(cls):
        return

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath

    def test_rw_config(self):

        test1_filename = "test1.txt"

        lf0_filename = "empty_listfile.json"
        lf1_filename = "one_listfile.json"
        lf2_filename = "two_listfile.json"

        # Test we get out of the file what we put in, for each type of configuration file

        test_analysis_dict = {"SHE_CTE_EstimateShear_methods": "KSB", "SHE_CTE_ObjectIdSplit_batch_size": "26"}

        write_analysis_config(test_analysis_dict, test1_filename, workdir=self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_analysis_config(test1_filename, workdir=self.workdir)

        # Check it's been read in correctly
        assert read_dict1["SHE_CTE_EstimateShear_methods"] == "KSB"
        assert read_dict1["SHE_CTE_ObjectIdSplit_batch_size"] == "26"

        # Check we get expected results from trying to read in other variants

        assert read_analysis_config(None, workdir=self.workdir) == {}
        assert read_analysis_config("", workdir=self.workdir) == {}
        assert read_analysis_config("None", workdir=self.workdir) == {}

        assert read_analysis_config(lf0_filename, workdir=self.workdir) == {}
        assert read_analysis_config(lf1_filename, workdir=self.workdir) == read_dict1
        with pytest.raises(ValueError):
            read_analysis_config(lf2_filename, workdir=self.workdir)

        # Test we get out of the file what we put in, for each type of configuration file

        test_reconciliation_dict = {"SHE_CTE_ReconcileMeasurements_method": "Best"}

        write_reconciliation_config(test_reconciliation_dict, test1_filename, workdir=self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_reconciliation_config(test1_filename, workdir=self.workdir)

        # Check it's been read in correctly
        assert read_dict1["SHE_CTE_ReconcileMeasurements_method"] == "Best"

        # Check we get expected results from trying to read in other variants

        assert read_reconciliation_config(None, workdir=self.workdir) == {}
        assert read_reconciliation_config("", workdir=self.workdir) == {}
        assert read_reconciliation_config("None", workdir=self.workdir) == {}

        assert read_reconciliation_config(lf0_filename, workdir=self.workdir) == {}
        assert read_reconciliation_config(lf1_filename, workdir=self.workdir) == read_dict1
        with pytest.raises(ValueError):
            read_reconciliation_config(lf2_filename, workdir=self.workdir)

        # Test we get out of the file what we put in, for each type of configuration file

        test_calibration_dict = {"SHE_CTE_EstimateShear_methods": "KSB", "SHE_CTE_CleanupBiasMeasurement_cleanup": "False"}

        write_calibration_config(test_calibration_dict, test1_filename, workdir=self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [test1_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [test1_filename, test1_filename])

        read_dict1 = read_calibration_config(test1_filename, workdir=self.workdir)

        # Check it's been read in correctly
        assert read_dict1["SHE_CTE_EstimateShear_methods"] == "KSB"
        assert read_dict1["SHE_CTE_CleanupBiasMeasurement_cleanup"] == "False"

        # Check we get expected results from trying to read in other variants

        assert read_calibration_config(None, workdir=self.workdir) == {}
        assert read_calibration_config("", workdir=self.workdir) == {}
        assert read_calibration_config("None", workdir=self.workdir) == {}

        assert read_calibration_config(lf0_filename, workdir=self.workdir) == {}
        assert read_calibration_config(lf1_filename, workdir=self.workdir) == read_dict1
        with pytest.raises(ValueError):
            read_calibration_config(lf2_filename, workdir=self.workdir)

        # Test that we can parse a more complicated file
        test2_filename = "test2.txt"
        with open(os.path.join(self.workdir, test2_filename), "w") as fo:
            fo.write("SHE_CTE_EstimateShear_methods = KSB\n" +
                     "SHE_CTE_ObjectIdSplit_batch_size = 26\n" +
                     "SHE_MER_RemapMosaic_num_threads_exposures = 8 # nope\n" +
                     "# ignore this = ignore\n" +
                     "\n" +
                     "SHE_MER_RemapMosaic_num_swarp_threads_exposures=4 #==2\n")

        read_dict2 = read_analysis_config(test2_filename, workdir=self.workdir)

        assert read_dict2["SHE_CTE_EstimateShear_methods"] == "KSB"
        assert read_dict2["SHE_CTE_ObjectIdSplit_batch_size"] == "26"
        assert read_dict2["SHE_MER_RemapMosaic_num_threads_exposures"] == "8"
        assert read_dict2["SHE_MER_RemapMosaic_num_swarp_threads_exposures"] == "4"
        assert "ignore this" not in read_dict2

        return

    def test_get_conditional_product(self):

        # We'll set up some test files to work with, using the object_id_list product

        product_filename = "object_id_list.xml"
        lf0_filename = "empty_listfile.json"
        lf1_filename = "one_listfile.json"
        lf2_filename = "two_listfile.json"

        object_ids = [1, 2]

        product = products.she_object_id_list.create_object_id_list_product(object_ids)
        write_xml_product(product, product_filename, workdir=self.workdir)

        write_listfile(os.path.join(self.workdir, lf0_filename), [])
        write_listfile(os.path.join(self.workdir, lf1_filename), [product_filename])
        write_listfile(os.path.join(self.workdir, lf2_filename), [product_filename, product_filename])

        # Test that we get the expected result in each case

        assert get_conditional_product(None, workdir=self.workdir) is None
        assert get_conditional_product("", workdir=self.workdir) is None
        assert get_conditional_product("None", workdir=self.workdir) is None

        assert get_conditional_product(product_filename, workdir=self.workdir).get_id_list() == object_ids

        assert get_conditional_product(lf0_filename, workdir=self.workdir) is None
        assert get_conditional_product(lf1_filename, workdir=self.workdir).get_id_list() == object_ids
        with pytest.raises(ValueError):
            get_conditional_product(lf2_filename, workdir=self.workdir)

        return
