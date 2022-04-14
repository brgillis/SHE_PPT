""" @file file_io_test.py

    Created 25 Aug 2017

    Unit tests relating to I/O functions.
"""

__updated__ = "2021-08-20"

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
import logging
import os
import subprocess
from time import sleep

import pytest

import SHE_PPT
from SHE_PPT.file_io import (DATA_SUBDIR, DEFAULT_FILE_EXTENSION, DEFAULT_FILE_SUBDIR, DEFAULT_INSTANCE_ID,
                             DEFAULT_TYPE_NAME, SheFileNamer, find_aux_file, get_allowed_filename, instance_id_maxlen,
                             processing_function_maxlen, read_listfile, read_product_and_table, read_xml_product,
                             tar_files, type_name_maxlen, update_xml_with_value, write_listfile,
                             write_product_and_table, )
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.table_formats.mer_final_catalog import MerFinalCatalogFormat
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from ST_DataModelBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame


class TestIO:
    """


    """

    listfile_name: str = "test_listfile.junk"
    tuple_listfile_name: str = "test_listfile.junk"

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):

        if os.path.exists(cls.listfile_name):
            os.remove(cls.listfile_name)

        if os.path.exists(cls.tuple_listfile_name):
            os.remove(cls.tuple_listfile_name)

    @pytest.fixture(autouse = True)
    def setup(self, tmpdir):

        self.workdir = tmpdir.strpath
        os.makedirs(os.path.join(self.workdir, DATA_SUBDIR))

        # Set log level to debug to make sure there aren't any issues with logging strings
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

    def test_get_allowed_filename(self):

        instance_id = "instance"

        filename = get_allowed_filename("test", instance_id, extension = ".junk", release = "06.66", subdir = "subdir")

        expect_filename_head = "subdir/EUC_SHE_TEST_INSTANCE_"
        expect_filename_tail = "Z_06.66.junk"

        # Check the beginning and end are correct
        assert filename[0:len(expect_filename_head)] == expect_filename_head
        assert filename[-len(expect_filename_tail):] == expect_filename_tail

        # Check that if we wait a tenth of a second, it will change
        sleep(0.1)
        new_filename = get_allowed_filename("test", instance_id, extension = ".junk", release = "06.66",
                                            subdir = "subdir")
        assert new_filename != filename

        # Test that it raises when we expect it to

        # Test for forbidden character
        with pytest.raises(ValueError):
            get_allowed_filename("test*", instance_id, extension = ".junk", release = "06.66", subdir = "subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id + "/", extension = ".junk", release = "06.66", subdir = "subdir")

        # Test for bad release
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension = ".junk", release = "06.666", subdir = "subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension = ".junk", release = "06.6a", subdir = "subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension = ".junk", release = "06.", subdir = "subdir")

        # Test for too long
        with pytest.raises(ValueError):
            get_allowed_filename("t" * (type_name_maxlen + 1), instance_id,
                                 extension = ".junk", release = "06.66", subdir = "subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", "i" * (instance_id_maxlen + 3),
                                 extension = ".junk", release = "06.66", subdir = "subdir", timestamp = True)
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension = ".junk", release = "06.66", subdir = "subdir",
                                 processing_function = "p" * (processing_function_maxlen + 1))

    def test_read_xml_product(self):
        """ Tests of the read_xml_product function."""

        test_filename = find_aux_file('SHE_PPT/sample_vis_stacked_frame.xml')
        ex_type = dpdVisStackedFrame
        non_ex_type = dpdVisCalibratedFrame

        # Test that we can read it successfully, both type checking and not
        p1 = read_xml_product(test_filename)
        p1.validateBinding()

        p2 = read_xml_product(test_filename, product_type = ex_type)
        p2.validateBinding()

        assert type(p1) == type(p2)

        # Test that if we specify the wrong type, a TypeError is raised
        with pytest.raises(TypeError):
            _ = read_xml_product(test_filename, product_type = non_ex_type)

    def test_rw_listfile(self):

        simple_list = ["file1.ext", "file2.ext", "file3.ext"]
        tuple_list = [("file1a.ext", "file1b.ext"), ("file2a.ext", "file2b.ext"), ("file2a.ext", "file2b.ext")]

        write_listfile(self.listfile_name, simple_list)
        assert read_listfile(self.listfile_name) == simple_list
        os.remove(self.listfile_name)

        write_listfile(self.tuple_listfile_name, tuple_list)
        assert read_listfile(self.tuple_listfile_name) == tuple_list
        os.remove(self.tuple_listfile_name)

    # TODO: Tests for replace_(multiple_)in_file

    def test_update_xml_with_value(self):
        """ Creates simple xml file
        Updates with <Value>

        """

        test_filename = find_aux_file('SHE_PPT/sample_vis_stacked_frame.xml')

        product = read_xml_product(test_filename)
        lines = open(test_filename).readlines()
        num_lines = len(lines)
        lines = [line for ii, line in enumerate(lines) if not ('<Value>' in line and '<Key>' in lines[ii - 1])]
        if len(lines) < num_lines:
            temp_test_filename = 'temp_test.xml'
            open(temp_test_filename, 'w').writelines(lines)

            update_xml_with_value(temp_test_filename)
            product = read_xml_product(temp_test_filename)
        product.validateBinding()

    def test_tar_files(self):
        """ Runs test of tarring files.
        """

        # Set up the files

        filenames = ["a.txt", "b.txt"]
        texts = ["foo/n", "bar/n"]

        for filename, text in zip(filenames, texts):
            with open(os.path.join(self.workdir, filename), "w") as fo:
                fo.write(text)

        tarball_filename = "tarball.tar"

        # Check everything is set up as expected
        assert os.path.isfile(os.path.join(self.workdir, filenames[0]))
        assert os.path.isfile(os.path.join(self.workdir, filenames[1]))

        tar_files(tarball_filename = tarball_filename,
                  l_filenames = filenames,
                  workdir = self.workdir,
                  delete_files = True)

        # Check things have been tarred up
        assert not os.path.isfile(os.path.join(self.workdir, filenames[0]))
        assert not os.path.isfile(os.path.join(self.workdir, filenames[1]))
        assert os.path.isfile(os.path.join(self.workdir, tarball_filename))

        # Check that we can untar and retrieve the data
        subprocess.call(f"cd {self.workdir} && tar xf {tarball_filename}", shell = True)

        assert os.path.isfile(os.path.join(self.workdir, filenames[0]))
        assert os.path.isfile(os.path.join(self.workdir, filenames[1]))

        for filename, text in zip(filenames, texts):
            with open(os.path.join(self.workdir, filename), "r") as fi:
                read_text = fi.read()
                assert read_text == text

    def test_rw_product_and_table(self):
        """ Test reading and writing a product and table together with utility functions.
        """

        # Create sample product and table
        p = create_dpd_mer_final_catalog()
        t = MerFinalCatalogFormat.init_table(size = 2)

        # Write them out together

        product_filename = SheFileNamer(type_name = "TESTPROD",
                                        instance_id = "0",
                                        workdir = self.workdir,
                                        subdir = "",
                                        version = SHE_PPT.__version__).filename

        # Try first without specifying a table filename
        write_product_and_table(product = p,
                                product_filename = product_filename,
                                table = t,
                                workdir = self.workdir)

        table_filename = p.get_data_filename()

        # Check that the default filename generated is as expected
        assert DEFAULT_TYPE_NAME in table_filename
        assert DEFAULT_INSTANCE_ID in table_filename
        assert DEFAULT_FILE_SUBDIR in table_filename
        assert DEFAULT_FILE_EXTENSION in table_filename

        # Check that the files have been written out
        assert os.path.exists(os.path.join(self.workdir, product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_filename))

        # Read the product and table back in
        p2, t2 = read_product_and_table(product_filename, workdir = self.workdir)

        # Check that they're the same as was written out
        assert p2.Header.ProductId.value() == p.Header.ProductId.value()
        assert p2.get_data_filename() == p.get_data_filename()
        assert (t2 == t).all()

        # Now try while specifying the table filename
        input_table_filename = get_allowed_filename(type_name = "TABLE", instance_id = "1",
                                                    version = SHE_PPT.__version__)
        write_product_and_table(product = p,
                                product_filename = product_filename,
                                table = t,
                                table_filename = input_table_filename,
                                workdir = self.workdir)

        # Check that the files have been written out
        output_table_filename = p.get_data_filename()
        assert output_table_filename == input_table_filename
        assert os.path.exists(os.path.join(self.workdir, output_table_filename))

        # Read the product and table back in
        p3, t3 = read_product_and_table(product_filename, workdir = self.workdir)

        # Check that they're the same as was written out
        assert p3.Header.ProductId.value() == p.Header.ProductId.value()
        assert p3.get_data_filename() == p.get_data_filename()
        assert (t3 == t).all()
