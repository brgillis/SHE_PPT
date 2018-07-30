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
                             replace_multiple_in_file, get_instance_id)
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

        filename = get_allowed_filename("TEST", instance_id, extension=".junk", release="06.66", subdir="subdir")

        expect_filename_head = "subdir/EUC-SHE-TEST-instance-"
        expect_filename_tail = "Z-06.66.junk"

        # Check the beginning and end are correct
        assert filename[0:len(expect_filename_head)] == expect_filename_head
        assert filename[-len(expect_filename_tail):] == expect_filename_tail

        # Check that if we wait a tenth of a second, it will change
        sleep(0.1)
        new_filename = get_allowed_filename("TEST", instance_id, extension=".junk", release="06.66")
        assert new_filename != filename

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
