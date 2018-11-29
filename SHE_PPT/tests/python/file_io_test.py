""" @file file_io_test.py

    Created 25 Aug 2017

    Unit tests relating to I/O functions.
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

import os
import pytest
from time import sleep

from SHE_PPT.file_io import (get_allowed_filename,
                             write_listfile,
                             read_listfile,
                             replace_in_file,
                             replace_multiple_in_file,
                             type_name_maxlen,
                             instance_id_maxlen,
                             processing_function_maxlen,
                             find_aux_file,
                             update_xml_with_value,
                             read_xml_product)
from astropy.table import Table
import numpy as np


class TestIO:
    """


    """

    @classmethod
    def setup_class(cls):
        cls.listfile_name = "test_listfile.junk"
        cls.tuple_listfile_name = "test_listfile.junk"

    @classmethod
    def teardown_class(cls):

        if os.path.exists(cls.listfile_name):
            os.remove(cls.listfile_name)

        if os.path.exists(cls.tuple_listfile_name):
            os.remove(cls.tuple_listfile_name)

        del cls.listfile_name, cls.tuple_listfile_name

    def test_get_allowed_filename(self):

        instance_id = "instance"

        filename = get_allowed_filename("test", instance_id, extension=".junk", release="06.66", subdir="subdir")

        expect_filename_head = "subdir/EUC_SHE_TEST_INSTANCE_"
        expect_filename_tail = "Z_06.66.junk"

        # Check the beginning and end are correct
        assert filename[0:len(expect_filename_head)] == expect_filename_head
        assert filename[-len(expect_filename_tail):] == expect_filename_tail

        # Check that if we wait a tenth of a second, it will change
        sleep(0.1)
        new_filename = get_allowed_filename("test", instance_id, extension=".junk", release="06.66", subdir="subdir")
        assert new_filename != filename

        # Test that it raises when we expect it to

        # Test for forbidden character
        with pytest.raises(ValueError):
            get_allowed_filename("test*", instance_id, extension=".junk", release="06.66", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id + "/", extension=".junk", release="06.66", subdir="subdir")

        # Test for bad release
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.666", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.6a", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.", subdir="subdir")

        # Test for too long
        with pytest.raises(ValueError):
            get_allowed_filename("t" * (type_name_maxlen + 1), instance_id,
                                 extension=".junk", release="06.", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", "i" * (instance_id_maxlen + 1),
                                 extension=".junk", release=None, subdir="subdir", timestamp=False)
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.", subdir="subdir",
                                 processing_function="p" * (processing_function_maxlen + 1))

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
        from EuclidDmBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame

        test_filename = find_aux_file('SHE_PPT/sample_stacked_frame.xml')

        product = read_xml_product(test_filename)
        product.validateBinding()
        lines = open(test_filename).readlines()
        nLines = len(lines)
        lines = [line for ii, line in enumerate(lines) if not ('<Value>' in line and '<Key>' in lines[ii - 1])]
        if len(lines) < nLines:
            temp_test_filename = 'temp_test.xml'
            open(temp_test_filename, 'w').writelines(lines)

            update_xml_with_value(temp_test_filename)
            product = read_xml_product(temp_test_filename)
        product.validateBinding()
