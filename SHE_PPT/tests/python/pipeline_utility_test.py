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

__updated__ = "2019-02-27"

import os
import pytest

from SHE_PPT.pipeline_utility import read_config, write_config


class TestUtility:
    """


    """

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath

    def test_rw_config(self):

        # Test we get out of the file what we put in

        test_dict = {"foo": "bar", "foobar": "barfoo"}
        test1_filename = "test1.txt"

        write_config(test_dict, test1_filename, workdir=self.workdir)

        read_dict1 = read_config(test1_filename, workdir=self.workdir)

        assert read_dict1["foo"] == "bar"
        assert read_dict1["foobar"] == "barfoo"

        # Test that we can parse a more complicated file
        test2_filename = "test2.txt"
        with open(os.path.join(self.workdir, test2_filename), "w") as fo:
            fo.write("foo = bar\n" +
                     "foobar = barfoo\n" +
                     "boo = far # nope\n" +
                     "# ignore this = ignore\n" +
                     "bah=gah\n" +
                     "fah=too=three\n")

        read_dict2 = read_config(test2_filename, workdir=self.workdir)

        assert read_dict2["foo"] == "bar"
        assert read_dict2["foobar"] == "barfoo"
        assert read_dict2["boo"] == "far"
        assert read_dict2["bah"] == "gah"
        assert read_dict2["fah"] == "too=three"
        assert "ignore this" not in read_dict2

        return
