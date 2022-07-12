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

from SHE_PPT.logging import getLogger

ACT_STORE_TRUE = 'store_true'
ACT_STORE_FALSE = 'store_true'

# Constant strings for command-line arguments

# Input filename cline-args

CA_MDB = "mdb"
CA_DATA_IMAGES = "data_images"
CA_VIS_CAL_FRAME = "vis_calibrated_frame_listfile"  # TODO: Fix duplication here
CA_SHE_MEAS = "she_validated_measurements_product"
CA_MER_CAT = "mer_final_catalog_listfile"
CA_SHE_STAR_CAT = "star_catalog_product"

# Options cline-args
CA_PIPELINE_CONFIG = "pipeline_config"
CA_WORKDIR = "workdir"
CA_LOGDIR = "logdir"
CA_PROFILE = "profile"
CA_DISABLE_FAILSAFE = "disable_failsafe"
CA_DRY_RUN = "dry_run"

logger = getLogger(__name__)


# Enum for specifying how the cline-arg is used
class ClineArgType(Enum):
    # Input - used as filename of input data product
    INPUT = "INPUT"

    # Output - used as filename of output data product
    OUTPUT = "OUTPUT"

    # Option - other options (not usable within a pipeline run, so must have valid default)
    OPTION = "OPTION"


class SheArgumentParser(ArgumentParser):
    """ Argument parser specialized for OU-SHE executables. This child class adds various methods to conveniently add
    cline-args formatted in the SHE standard way, and methods to add various common cline-args.

    This class also automatically adds all cline-args which are used in all OU-SHE executables:

    * --pipeline_config
    * --workdir
    * --logdir
    * --profile
    * --dry_run
    """

    def __init__(self, *args, **kwargs):
        """Initializes an instance of a SheArgumentParser object.

        Parameters
        ----------
        *args, **kwargs : Any
            Any additional args and kwargs are forwarded to the parent-class initializer.
        """

        super().__init__(*args, **kwargs)

        # Input filenames
        self.add_input_arg(f'--{CA_PIPELINE_CONFIG}', type=str, default=None,
                           help='Pipeline configuration file (.xml data product or .json listfile of 0-1 '
                                'such data products.')

        # Arguments needed by the pipeline runner
        self.add_option_arg(f'--{CA_WORKDIR}', type=str, default=".",
                            help=f'Work directory, where input data is stored and output data will be created. '
                                 f'Should be fully-qualified.')
        self.add_option_arg(f'--{CA_LOGDIR}', type=str, default=".",
                            help=f"Logging directory (relative to work directory.")

        # Optional arguments (can't be used with pipeline runner)
        self.add_option_arg(f'--{CA_PROFILE}', action=ACT_STORE_TRUE,
                            help=f'Store profiling data for execution.')
        self.add_option_arg(f'--{CA_DRY_RUN}', action=ACT_STORE_TRUE,
                            help=f'Skip processing and just output dummy data.')

    # Public functions

    def add_input_arg(self,
                      *args,
                      help: Optional[str] = None,
                      **kwargs) -> Action:
        """Adds a cline-arg to this parser, with the help text formatted to specify that it's an input argument.

        Parameters
        ----------
        help : Optional[str], default=None
            The desired help text for this cline-arg.
        *args, **kwargs : Any
            Any additional arguments are forwarded to the call to the self.add_arg_with_type method. This method
            recognizes the `suppress_warnings` kwarg, and forwards any other args and kwargs to its call to the
            parent-class's `add_argument` method.

        Returns
        -------
        Action
            The constructed Action for this cline-arg.
        """
        return self.add_arg_with_type(*args, arg_type=ClineArgType.INPUT, help=help, **kwargs)

    def add_output_arg(self,
                       *args,
                       help: Optional[str] = None,
                       **kwargs) -> Action:
        """Adds a cline-arg to this parser, with the help text formatted to specify that it's an output argument.

        Parameters
        ----------
        help : Optional[str], default=None
            The desired help text for this cline-arg.
        *args, **kwargs : Any
            Any additional arguments are forwarded to the call to the self.add_arg_with_type method. This method
            recognizes the `suppress_warnings` kwarg, and forwards any other args and kwargs to its call to the
            parent-class's `add_argument` method.

        Returns
        -------
        Action
            The constructed Action for this cline-arg.
        """
        return self.add_arg_with_type(*args, arg_type=ClineArgType.OUTPUT, help=help, **kwargs)

    def add_option_arg(self,
                       *args,
                       help: Optional[str] = None,
                       **kwargs) -> Action:
        """Adds a cline-arg to this parser, with the help text formatted to specify that it's an input argument.

        Parameters
        ----------
        help : Optional[str], default=None
            The desired help text for this cline-arg.
        *args, **kwargs : Any
            Any additional arguments are forwarded to the call to the self.add_arg_with_type method. This method
            recognizes the `suppress_warnings` kwarg, and forwards any other args and kwargs to its call to the
            parent-class's `add_argument` method.

        Returns
        -------
        Action
            The constructed Action for this cline-arg.
        """
        return self.add_arg_with_type(*args, arg_type=ClineArgType.OPTION, help=help, **kwargs)

    def add_arg_with_type(self,
                          *args,
                          arg_type: ClineArgType = ClineArgType.INPUT,
                          help: Optional[str] = None,
                          suppress_warnings: bool = False,
                          **kwargs) -> Action:
        """Adds a cline-arg to this parser, with help formatted to specify the type of argument it is.

        Parameters
        ----------
        arg_type : ClineArgType, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum. Possibilities are:
            * ClineArgType.INPUT (default)
            * ClineArgType.OUTPUT
            * ClineArgType.OPTION
        help : Optional[str], default=None
            The desired help text for this cline-arg.
        suppress_warnings : bool, default=False
            If `True`, will not warn if a default value is set for a cline-arg with a `store_true` or `store_false`
            action.
        *args, **kwargs : Any
            Any additional arguments are forwarded to the call to the parent-class's `add_argument` method.

        Returns
        -------
        Action
            The constructed Action for this cline-arg.
        """

        formatted_help: Optional[str] = None
        if help is not None:
            formatted_help = f"{arg_type.value}: {help}"

        # Check for store_true and store_false actions, and set default to None if found
        if "action" in kwargs and (kwargs["action"] == "store_true" or kwargs["action"] == "store_false"):
            logger.debug(f"Overriding default to be None for cline-arg {args[0]}, since it's set as store_true or "
                         "store_false")
            kwargs["default"] = None

        # Warn if the default is set to anything other than None
        if "default" in kwargs and kwargs["default"] is not None and not suppress_warnings:
            logger.warning(f"Default for cline-arg {args[0]} attempted to be set to {kwargs['default']}."
                           "When setting a cline-arg for a SheArgumentParser, the default should usually be set to "
                           "None, as it will normally be overridden by the defaults provided to the read_config "
                           "function. If this is an exceptional case and you wish to suppress this warning, set "
                           "suppress_warnings=True in the call to add_*_arg or add_arg_with_type.")

        logger.debug(f"Adding cline-arg {args[0]} to SheArgumentParser.")

        return self.add_argument(*args, **kwargs, help=formatted_help)

    # Convenience methods to add option args

    def add_disable_failsafe_arg(self):
        """Adds a command-line argument to disable failsafe blocks, `--disable_failsafe`. This is added as a
        `store_true` option cline-arg.
        """
        self.add_option_arg(f'--{CA_DISABLE_FAILSAFE}', action=ACT_STORE_TRUE,
                            help=f'Disable any failsafe blocks in the code. If this is set and such a block is hit, '
                                 f'any exception will be re-raised.')

    # Convenience functions to add input filename cline-args

    def add_mdb_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a Mission Database (MDB) file.

        Parameters
        ----------
        arg_type : ClineArgType, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum. Possibilities are:
            * ClineArgType.INPUT (default)
            * ClineArgType.OUTPUT
        """
        self.add_arg_with_type(f'--{CA_MDB}', type=str, default=None, arg_type=arg_type,
                               help='Mission Database .xml file')

    def add_data_images_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a listfile of VIS Calibrated Frame data products,
        `--data_images`.

        Parameters
        ----------
        arg_type : {ClineArgType.INPUT, ClineArgType.OUTPUT}, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum.
        """
        self.add_arg_with_type(f'--{CA_DATA_IMAGES}', type=str, default=None, arg_type=arg_type,
                               help='.json listfile containing filenames of data image products. Only'
                                    ' needs to be set if adding bin columns.')

    def add_measurements_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a validated shear measurements data product,
        `--she_validated_measurements_product`.

        Parameters
        ----------
        arg_type : {ClineArgType.INPUT, ClineArgType.OUTPUT}, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum.
        """
        self.add_arg_with_type(f'--{CA_SHE_MEAS}', type=str, arg_type=arg_type,
                               help='Filename of the validated shear measurements .xml data product.')

    def add_final_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a listfile of MER Final Catalog data products,
        `--mer_final_catalog_listfile`.

        Parameters
        ----------
        arg_type : {ClineArgType.INPUT, ClineArgType.OUTPUT}, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum.
        """
        self.add_arg_with_type(f'--{CA_MER_CAT}', type=str, arg_type=arg_type,
                               help='.json listfile containing filenames of mer final catalogs.')

    def add_calibrated_frame_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a listfile of VIS Calibrated Frame data products,
        `--vis_calibrated_frame_listfile`.

        Parameters
        ----------
        arg_type : {ClineArgType.INPUT, ClineArgType.OUTPUT}, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum.
        """
        self.add_arg_with_type(f'--{CA_VIS_CAL_FRAME}', type=str, arg_type=arg_type,
                               help='.json listfile containing filenames of exposure image products.')

    def add_star_catalog_arg(self, arg_type: ClineArgType = ClineArgType.INPUT):
        """Adds a command-line argument for a SHE Star Catalog data product,
        `--star_catalog_product`.

        Parameters
        ----------
        arg_type : {ClineArgType.INPUT, ClineArgType.OUTPUT}, default=ClineArgType.INPUT
            The type of cline-arg this is, specified as an element of the `ClineArgType` Enum.
        """
        self.add_arg_with_type(f"--{CA_SHE_STAR_CAT}", type=str, arg_type=arg_type,
                               help=".xml data product for SHE star catalog for an observation.")
