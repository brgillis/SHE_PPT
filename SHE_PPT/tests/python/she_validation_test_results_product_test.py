""" @file she_validation_test_results_product_test.py

    Created 24 Nov 2020

    Unit tests for the she_validation_test_results data product.
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

__updated__ = "2020-11-24"

import os
import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products import she_validation_test_results as prod

mer_final_catalog_filename = "EUC_SHE_P-MER-FINAL-CAT_BUKRTILMXZI3ADHVZ_20200721T162818.092086Z_08.02.xml"
vis_calibrated_frame_filename = "EUC_SHE_GST-P-SCI-D1_BUKRTILMXZI3ADHVZ_20190429T165754.9Z_01.07.xml"
vis_stacked_frame_filename = "vis_stacked_image.xml"


class TestValidationTestResults(object):
    """A collection of tests for the she_validation_test_results data product.

    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):

        # Download the data stack files from WebDAV

        self.sync_datastack = DataSync("testdata/sync.conf", "testdata/test_data_stack.txt")
        self.sync_datastack.download()
        self.qualified_mer_final_catalog_filename = self.sync_datastack.absolutePath(
            "SHE_PPT_8_5/" + mer_final_catalog_filename)

        assert os.path.isfile(
            self.qualified_mer_final_catalog_filename), f"Cannot find file: {self.qualified_mer_final_catalog_filename}"

        # Get the workdir based on where the final catalog listfile is
        self.workdir = os.path.split(self.qualified_mer_final_catalog_filename)[0]

        return

    @classmethod
    def setup_class(cls):

        cls.filename = "she_validation_test_results.xml"
        cls.filename_zero = "she_validation_test_results_0.xml"
        cls.filename_three = "she_validation_test_results_3.xml"
        cls.filename_tile = "she_validation_test_results_tile.xml"
        cls.filename_exp = "she_validation_test_results_exp.xml"
        cls.filename_obs = "she_validation_test_results_obs.xml"

        cls.source_pipeline = "sheReconciliation"
        cls.observation_mode = "ScienceDeep"
        cls.num_exposures = 3

        return

    @classmethod
    def teardown_class(cls):
        return

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_validation_test_results()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self):

        # Create the product
        product = prod.create_dpd_she_validation_test_results(source_pipeline=self.source_pipeline,
                                                              observation_mode=self.observation_mode,
                                                              num_exposures=self.num_exposures)

        # Save the product in an xml file
        write_xml_product(product, self.filename, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename, workdir=self.workdir)

        # Check that it's the same
        assert loaded_product.Data.SourcePipeline == self.source_pipeline
        assert loaded_product.Data.ObservationMode == self.observation_mode
        assert loaded_product.Data.NumberExposures == self.num_exposures

        # Try with zero and multiple tests

        # Create the product
        product_zero = prod.create_dpd_she_validation_test_results(num_tests=0)

        # Save the product in an xml file
        write_xml_product(product_zero, self.filename_zero, workdir=self.workdir)

        # Read back the xml file
        loaded_product_zero = read_xml_product(self.filename_zero, workdir=self.workdir)

        assert len(loaded_product_zero.Data.ValidationTestList) == 0

        # Create the product
        product_three = prod.create_dpd_she_validation_test_results(num_tests=3)

        # Save the product in an xml file
        write_xml_product(product_three, self.filename_zero, workdir=self.workdir)

        # Read back the xml file
        loaded_product_three = read_xml_product(self.filename_zero, workdir=self.workdir)

        assert len(loaded_product_three.Data.ValidationTestList) == 3

        return

    def test_mer_final_catalog_reference(self):

        # Read the MER Final Catalog product
        mer_final_catalog_product = read_xml_product(mer_final_catalog_filename, workdir=self.workdir)

        # Create the product
        product = prod.create_dpd_she_validation_test_results(reference_product=mer_final_catalog_product)

        # Save the product in an xml file
        write_xml_product(product, self.filename_tile, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename_tile, workdir=self.workdir)

        assert loaded_product.Data.TileId == mer_final_catalog_product.Data.TileIndex

        return

    def test_vis_calibrated_frame_reference(self):

        # Read the MER Final Catalog product
        vis_calibrated_frame_product = read_xml_product(vis_calibrated_frame_filename, workdir=self.workdir)

        # Create the product
        product = prod.create_dpd_she_validation_test_results(reference_product=vis_calibrated_frame_product)

        # Save the product in an xml file
        write_xml_product(product, self.filename_exp, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename_exp, workdir=self.workdir)

        assert loaded_product.Data.ExposureProductId == vis_calibrated_frame_product.Header.ProductId
        assert loaded_product.Data.ObservationId == vis_calibrated_frame_product.Data.ObservationSequence.ObservationId

        return

    def test_vis_stacked_frame_reference(self):

        # Read the MER Final Catalog product
        vis_stacked_frame_product = read_xml_product(vis_stacked_frame_filename, workdir=self.workdir)

        # Create the product
        product = prod.create_dpd_she_validation_test_results(reference_product=vis_stacked_frame_product,
                                                              num_exposures=self.num_exposures)

        # Save the product in an xml file
        write_xml_product(product, self.filename_obs, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename_obs, workdir=self.workdir)

        assert loaded_product.Data.ObservationId == vis_stacked_frame_product.Data.ObservationId
        assert loaded_product.Data.NumberExposures == self.num_exposures

        return
