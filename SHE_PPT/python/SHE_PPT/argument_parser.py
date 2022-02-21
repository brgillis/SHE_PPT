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

from argparse import Action, ArgumentParser

from enum import Enum
from typing import Optional

ACT_STORE_TRUE = 'store_true'
ACT_STORE_FALSE = 'store_true'

# Constant strings for command-line arguments

# Input filename cline-args

CA_MDB = "mdb"
CA_DATA_IMAGES = "data_images"
CA_VIS_CAL_FRAME = "vis_calibrated_frame_listfile"  # TODO: Fix duplication here
CA_SHE_MEAS = "she_validated_measurements_product"
CA_MER_CAT = "mer_final_catalog_listfile"
CA_SHE_STAR_CAT = "star_catalog_listfile"

# Options cline-args
CA_PIPELINE_CONFIG = "pipeline_config"
CA_WORKDIR = "workdir"
CA_LOGDIR = "logdir"
CA_PROFILE = "profile"
CA_DRY_RUN = "dry_run"


# Enum for specifying how the cline-arg is used
class ClineArgType(Enum):
    # Input - used as filename of input data product
    INPUT = "INPUT"

    # Output - used as filename of output data product
    OUTPUT = "OUTPUT"

    # Option - other options (not usable within a pipeline run, so must have valid default)
    OPTION = "OPTION"


class SheArgumentParser(ArgumentParser):
    """ Argument parser specialized for OU-SHE executables.
    """

    def __init__(self):
        super().__init__()

        # Input filenames
        self.add_input_arg(f'--{CA_PIPELINE_CONFIG}', type = str, default = None,
                           help = 'Pipeline configuration file (.xml data product or .json listfile of 0-1 '
                                  'such data products.')

        # Arguments needed by the pipeline runner
        self.add_option_arg(f'--{CA_WORKDIR}', type = str, default = ".",
                            help = f'Work directory, where input data is stored and output data will be created. '
                                   f'Should be fully-qualified.')
        self.add_option_arg(f'--{CA_LOGDIR}', type = str, default = ".",
                            help = f"Logging directory (relative to work directory.")

        # Optional arguments (can't be used with pipeline runner)
        self.add_option_arg(f'--{CA_PROFILE}', action = ACT_STORE_TRUE,
                            help = f'Store profiling data for execution.')
        self.add_option_arg(f'--{CA_DRY_RUN}', action = ACT_STORE_TRUE,
                            help = f'Skip processing and just output dummy data.')

    # Public functions

    def add_input_arg(self,
                      *args,
                      help: Optional[str] = None,
                      **kwargs) -> Action:
        return self.add_arg_with_type(*args, arg_type = ClineArgType.INPUT, help = help, **kwargs)

    def add_output_arg(self,
                       *args,
                       help: Optional[str] = None,
                       **kwargs) -> Action:
        return self.add_arg_with_type(*args, arg_type = ClineArgType.OUTPUT, help = help, **kwargs)

    def add_option_arg(self,
                       *args,
                       help: Optional[str] = None,
                       **kwargs) -> Action:
        return self.add_arg_with_type(*args, arg_type = ClineArgType.OPTION, help = help, **kwargs)

    def add_arg_with_type(self,
                          *args,
                          arg_type: ClineArgType = ClineArgType.INPUT,
                          help: Optional[str] = None,
                          **kwargs) -> Action:
        """ Function to add an argument with help formatted depending on the argument type.
        """

        formatted_help: Optional[str] = None
        if help is not None:
            formatted_help = f"{arg_type.value}: {help}"

        # Check for store_true and store_false actions, and set default to None if found
        if "action" in kwargs and (kwargs["action"] == "store_true" or kwargs["action"] == "store_false"):
            kwargs["default"] = None

        return self.add_argument(*args, **kwargs, help = formatted_help)

    # Convenience functions to add input filename cline-args

    def add_mdb_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_MDB}', type = str, default = None, arg_type = arg_type,
                               help = 'Mission Database .xml file')

    def add_data_images_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_DATA_IMAGES}', type = str, default = None, arg_type = arg_type,
                               help = '.json listfile containing filenames of data image products. Only'
                                      ' needs to be set if adding bin columns.')

    def add_measurements_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_SHE_MEAS}', type = str, arg_type = arg_type,
                               help = 'Filename of the cross-validated shear measurements .xml data product.')

    def add_final_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_MER_CAT}', type = str, arg_type = arg_type,
                               help = '.json listfile containing filenames of mer final catalogs.')

    def add_calibrated_frame_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f'--{CA_VIS_CAL_FRAME}', type = str, arg_type = arg_type,
                               help = '.json listfile containing filenames of exposure image products.')

    def add_star_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        self.add_arg_with_type(f"--{CA_SHE_STAR_CAT}", type = str, arg_type = arg_type,
                               help = ".json listfile containing filenames of .xml data products for SHE star "
                                      "catalogs for each exposure.")
