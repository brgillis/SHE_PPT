""" @file mock_tables_test.py

    Created 24 March 2022

    Unit tests of making mock tables, which also demonstrate how to use this functionality for creating mock tables.
"""

__updated__ = "2021-08-16"

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

from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.file_io import read_listfile, read_xml_product
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.testing.mock_measurements_cat import (EST_KSB_TABLE_FILENAME, EST_LENSMC_TABLE_FILENAME,
                                                   MockShearEstimateTableGenerator,
                                                   write_mock_measurements_tables, )
from SHE_PPT.testing.mock_mer_final_cat import MockMFCGalaxyTableGenerator
from SHE_PPT.testing.mock_she_star_cat import MockStarCatTableGenerator
from SHE_PPT.testing.mock_tu_galaxy_cat import MockTUGalaxyTableGenerator
from SHE_PPT.testing.mock_tum_cat import (MockTUMatchedTableGenerator, TUM_KSB_TABLE_FILENAME,
                                          TUM_LENSMC_TABLE_FILENAME,
                                          write_mock_tum_tables, )
from SHE_PPT.testing.utility import SheTestCase

TEST_LEN = 102


class TestMockTables(SheTestCase):
    """ Test case for PSF-Res validation test code.
    """

    def post_setup(self):
        """ In the parent SheTestCase class, this method does nothing, and is performed after normal setup tasks
            (e.g. setting up a tmpdir as the workdir). So we override this in order to demonstrate how mock tables
            can be written in the setup of a test class.
        """

        # Normally, we would have something like the below to write a table in the setup:
        # MockMFCGalaxyTableGenerator(workdir=self.workdir).write_mock_listfile()
        # But here, we actually want to test the writing of tables, so we do that in the actual tests

        return

    def test_write_and_cleanup(self):
        """ Test generating and writing catalogs in the general case
        """

        # Create a table generator to test
        table_generator = MockMFCGalaxyTableGenerator(num_test_points=TEST_LEN,
                                                      workdir=self.workdir)

        # Make sure nothing exists beforehand
        table_generator.cleanup()
        assert not os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))

        # Call each method, and check that the expected files exist and others don't
        table_generator.write_mock_table()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        table_generator.write_mock_product()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        table_generator.write_mock_listfile()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        assert not os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert not os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))

        # Do some basic tests on the generated table to make sure it's as expected
        t = table_generator.get_mock_table()

        assert len(t) == TEST_LEN
        assert is_in_format(t, table_generator.tf, verbose=True)

    def test_filenames(self):
        """ Test that filenames in written products and listfiles are correct.
        """

        # Create a table generator to test
        table_generator = MockMFCGalaxyTableGenerator(workdir=self.workdir)

        # Test the results of write_mock_product
        table_generator.write_mock_product()

        p = read_xml_product(table_generator.product_filename, workdir=self.workdir)
        assert p.get_data_filename() == table_generator.table_filename

        table_generator.cleanup()

        # Test the results of write_mock_listfile
        table_generator.write_mock_listfile()

        l_table_filenames = read_listfile(os.path.join(self.workdir, table_generator.listfile_filename))
        assert l_table_filenames[0] == table_generator.product_filename

        p = read_xml_product(l_table_filenames[0], workdir=self.workdir)
        assert p.get_data_filename() == table_generator.table_filename

        table_generator.cleanup()

    def test_mock_star_cat(self):
        """ Test creating a mock star catalog.
        """

        # Create a table generator to test
        table_generator = MockStarCatTableGenerator(num_test_points=TEST_LEN,
                                                    workdir=self.workdir)

        table_generator.write_mock_listfile()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        # Do some basic tests on the generated table to make sure it's as expected
        t = table_generator.get_mock_table()

        assert len(t) == TEST_LEN
        assert is_in_format(t, table_generator.tf, verbose=True)

    def test_mock_tu_gal_cat(self):
        """ Test creating a mock TU galaxy catalog.
        """

        # Create a table generator to test
        table_generator = MockTUGalaxyTableGenerator(num_test_points=TEST_LEN,
                                                     workdir=self.workdir)

        # We don't have a product creator for this set up, so just test writing the table
        table_generator.write_mock_table()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        table_generator.cleanup()

        # Do some basic tests on the generated table to make sure it's as expected
        t = table_generator.get_mock_table()

        assert len(t) == TEST_LEN
        assert is_in_format(t, table_generator.tf, verbose=True)

    def test_mock_measurements_cat(self):
        """ Test creating a mock shear estimates catalog.
        """

        # Create a table generator to test
        table_generator = MockShearEstimateTableGenerator(num_test_points=TEST_LEN,
                                                          workdir=self.workdir,
                                                          method=ShearEstimationMethods.LENSMC)

        table_generator.write_mock_listfile()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        # Do some basic tests on the generated table to make sure it's as expected
        t = table_generator.get_mock_table()

        assert len(t) == TEST_LEN
        assert is_in_format(t, table_generator.tf, verbose=True)

        # Test the convenience method to create both LensMC and KSB tables
        p_filename = write_mock_measurements_tables(workdir=self.workdir)
        assert os.path.exists(os.path.join(self.workdir, EST_LENSMC_TABLE_FILENAME))
        assert os.path.exists(os.path.join(self.workdir, EST_KSB_TABLE_FILENAME))

        p = read_xml_product(p_filename, workdir=self.workdir)
        assert p.get_LensMC_filename() == EST_LENSMC_TABLE_FILENAME
        assert p.get_KSB_filename() == EST_KSB_TABLE_FILENAME

    def test_mock_tum_cat(self):
        """ Test creating a mock star catalog.
        """

        # Create a table generator to test
        table_generator = MockTUMatchedTableGenerator(num_test_points=TEST_LEN,
                                                      workdir=self.workdir,
                                                      method=ShearEstimationMethods.LENSMC)

        table_generator.write_mock_listfile()
        assert os.path.exists(os.path.join(self.workdir, table_generator.table_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_generator.listfile_filename))
        table_generator.cleanup()

        # Do some basic tests on the generated table to make sure it's as expected
        t = table_generator.get_mock_table()

        assert len(t) == TEST_LEN
        assert is_in_format(t, table_generator.tf, verbose=True)

        # Test the convenience method to create both LensMC and KSB tables
        p_filename = write_mock_tum_tables(workdir=self.workdir)
        assert os.path.exists(os.path.join(self.workdir, TUM_LENSMC_TABLE_FILENAME))
        assert os.path.exists(os.path.join(self.workdir, TUM_KSB_TABLE_FILENAME))

        p = read_xml_product(p_filename, workdir=self.workdir)
        assert p.get_LensMC_filename() == TUM_LENSMC_TABLE_FILENAME
        assert p.get_KSB_filename() == TUM_KSB_TABLE_FILENAME
