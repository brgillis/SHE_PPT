""" @file argument_parser_test.py

    Created 30 May 2022

    Unit tests relating to argument parser classes and functions
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

from copy import deepcopy

from SHE_PPT.argument_parser import (CA_DATA_IMAGES, CA_DISABLE_FAILSAFE, CA_DRY_RUN, CA_LOGDIR, CA_MDB,
                                     CA_MER_CAT, CA_PIPELINE_CONFIG, CA_PROFILE,
                                     CA_SHE_MEAS, CA_SHE_STAR_CAT, CA_VIS_CAL_FRAME, CA_WORKDIR, SheArgumentParser, )
from SHE_PPT.testing.utility import SheTestCase


class TestArgumentParser(SheTestCase):
    """ Unit tests for functions and classes in the SHE_PPT.argument_parser module.
    """

    def post_setup(self):
        """Define a SheArgumentParser object to work with.
        """

        self.argument_parser = SheArgumentParser()

    def test_default_args(self):
        """Test that the argument parser is set up with all default arguments.
        """

        # Get the usage string from the argument parser, which is the easiest way to check that args have been set
        # without digging into its private attributes
        usage_str = self.argument_parser.format_usage()

        for cline_arg in (CA_PIPELINE_CONFIG, CA_WORKDIR, CA_LOGDIR, CA_PROFILE, CA_DRY_RUN):
            # Depending on whether it's set as store_true or not, it might be formatted as either
            # [--cline_arg CLINE_ARG] or [--cline_arg] in the usage string, so check both
            assert (f"[--{cline_arg} {cline_arg.upper()}]" in usage_str or
                    f"[--{cline_arg}]" in usage_str)

    def test_add_arg(self):
        """Test that we can add args with the various general methods.
        """

        # Make a copy of the argument_parser we can modify
        test_argument_parser = deepcopy(self.argument_parser)

        input_arg_str = "input_cline_arg"
        output_arg_str = "output_cline_arg"
        option_arg_str = "option_cline_arg"

        # Test adding an arg with each method
        test_argument_parser.add_input_arg(f"--{input_arg_str}", help = "This is an input arg")
        test_argument_parser.add_output_arg(f"--{output_arg_str}")
        test_argument_parser.add_option_arg(f"--{option_arg_str}", action = "store_true")

        # Get the usage string to check that args were set successfully
        usage_str = test_argument_parser.format_usage()

        assert f"[--{input_arg_str} {input_arg_str.upper()}]" in usage_str
        assert f"[--{output_arg_str} {output_arg_str.upper()}]" in usage_str
        assert f"[--{option_arg_str}]" in usage_str

    def test_predefined_add_arg(self):
        """Test that we can add args with the various predefined methods for specific arguments.
        """

        # Make a copy of the argument_parser we can modify
        test_argument_parser = deepcopy(self.argument_parser)

        # Test adding an arg with each method
        test_argument_parser.add_disable_failsafe_arg()
        test_argument_parser.add_mdb_arg()
        test_argument_parser.add_data_images_arg()
        test_argument_parser.add_measurements_arg()
        test_argument_parser.add_final_catalog_arg()
        test_argument_parser.add_calibrated_frame_arg()
        test_argument_parser.add_star_catalog_arg()

        # Get the usage string to check that args were set successfully
        usage_str = test_argument_parser.format_usage()

        assert f"[--{CA_DISABLE_FAILSAFE}]" in usage_str
        assert f"[--{CA_MDB} {CA_MDB.upper()}]" in usage_str
        assert f"[--{CA_DATA_IMAGES} {CA_DATA_IMAGES.upper()}]" in usage_str
        assert f"[--{CA_SHE_MEAS} {CA_SHE_MEAS.upper()}]" in usage_str
        assert f"[--{CA_MER_CAT} {CA_MER_CAT.upper()}]" in usage_str
        assert f"[--{CA_VIS_CAL_FRAME} {CA_VIS_CAL_FRAME.upper()}]" in usage_str
        assert f"[--{CA_SHE_STAR_CAT} {CA_SHE_STAR_CAT.upper()}]" in usage_str
