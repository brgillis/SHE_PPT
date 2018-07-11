""" @file utility_test.py

    Created 25 Aug 2017

    Unit tests relating to utility functions.
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

from astropy.table import Table

from SHE_PPT.utility import hash_any, get_arguments_string
import numpy as np


class TestUtility:
    """


    """

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_hash_any(self):

        test_str = "my_string"
        test_obj = ("this_is_my_tuple", 1)

        # Check that maximum length is enforced properly
        max_length = 16
        assert len(hash_any(test_str, max_length = max_length)) == max_length
        assert len(hash_any(test_obj, max_length = max_length)) == max_length
        assert len(hash_any(test_obj, format = "base64", max_length = max_length)) == max_length

        smaller_max_length = 8
        assert hash_any(test_str, max_length = max_length)[:max_length - smaller_max_length] == hash_any(test_str, max_length = smaller_max_length)
        assert hash_any(test_obj, max_length = max_length)[:max_length - smaller_max_length] == hash_any(test_obj, max_length = smaller_max_length)
        assert (hash_any(test_obj, max_length = max_length, format = "base64")[:max_length - smaller_max_length] ==
                hash_any(test_obj, max_length = smaller_max_length, format = "base64"))

        # Check that base64 encoding is working as expected - should be shorter than hex encoding
        assert len(hash_any(test_str, format = "hex")) > len(hash_any(test_str, format = "base64"))
        assert len(hash_any(test_obj, format = "hex")) > len(hash_any(test_obj, format = "base64"))
        
    def test_get_arguments_string(self):
        
        # Set up a mock arguments object
        class TestArgs(object):
            def __init__(self):
                self.foo = "bar"
                self.foobar = "barfoo " # Test it strips this
                return
            
        test_args = TestArgs()
        
        # Test with no command string
        arg_string = get_arguments_string(test_args)
        
        # Have to test both possible orders of arguments since it's indeterminate
        assert ((arg_string == "--foo bar --foobar barfoo") or
                (arg_string == "--foobar barfoo --foo bar"))
        
        # Test with a command string
        cmd_string = get_arguments_string(test_args, cmd="run")
        assert ((cmd_string == "run --foo bar --foobar barfoo") or
                (cmd_string == "run --foobar barfoo --foo bar"))
        
        # Test it strips the command string properly
        cmd_string2 = get_arguments_string(test_args, cmd="run ")
        assert ((cmd_string2 == "run --foo bar --foobar barfoo") or
                (cmd_string2 == "run --foobar barfoo --foo bar"))
        
        return


