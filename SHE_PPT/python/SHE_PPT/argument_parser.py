""" @file argument_parser.py

    Created 29 July 2021

    Base class for an argument parser for OU-SHE executables.
"""

__updated__ = "2021-08-27"

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

from argparse import ArgumentParser


class SheArgumentParser(ArgumentParser):
    """ Argument parser specialized for OU-SHE executables.
    """

    def __init__(self):
        super().__init__()

        # Input filenames
        self.add_argument('--pipeline_config', type = str, default = None,
                          help = 'INPUT: Pipeline configuration file (.xml data product or .json listfile of 0-1 such '
                                 'data products.')

        # Arguments needed by the pipeline runner
        self.add_argument('--workdir', type = str, default = ".")
        self.add_argument('--logdir', type = str, default = ".")

        # Optional arguments (can't be used with pipeline runner)
        self.add_argument('--profile', action = 'store_true',
                          help = 'OPTION: Store profiling data for execution.')
        self.add_argument('--dry_run', action = 'store_true',
                          help = 'OPTION: Skip processing and just output dummy data.')
