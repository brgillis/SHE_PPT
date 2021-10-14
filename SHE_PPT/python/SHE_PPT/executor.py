""" @file executor.py

    Created 14 Oct 2021

    Class to handle primary execution of SHE executables.
"""

__updated__ = "2021-10-14"

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
from argparse import Namespace
from logging import Logger
from typing import Any, Callable, Dict, Optional, Sequence, Set, Type

from dataclasses import dataclass

from EL_PythonUtils.utilities import get_arguments_string
from . import __version__
from .constants.config import ConfigKeys, GlobalConfigKeys
from .logging import getLogger
from .pipeline_utility import read_config
from .utility import default_init_if_none, empty_dict_if_none, empty_list_if_none, empty_set_if_none

S_DEFAULT_STORE_TRUE: Set[str] = {"debug", "dry_run", "hide", "profile", "test"}
S_DEFAULT_STORE_FALSE: Set[str] = set()


@dataclass
class LogOptions:
    """Dataclass for attributes controlling printing of the execution command and other logging.
    """
    executable_name: str
    project_name: str = "SHE_PPT"
    project_version: str = __version__
    s_store_true: Optional[Set[str]] = None
    s_store_false: Optional[Set[str]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init empty sets if None was provided
        self.s_store_true = empty_set_if_none(self.s_store_true, coerce = True)
        self.s_store_false = empty_set_if_none(self.s_store_false, coerce = True)

        # Make sure defaults are always included in store_true/false sets
        self.s_store_true.update(S_DEFAULT_STORE_TRUE)
        self.s_store_false.update(S_DEFAULT_STORE_FALSE)


@dataclass
class ReadConfigArgs:
    """Dataclass for kwargs to be passed to the read_config function.
    """
    d_config_defaults: Optional[Dict[ConfigKeys, Any]] = None
    d_config_types: Optional[Dict[ConfigKeys, Type]] = None
    d_config_cline_args: Optional[Dict[ConfigKeys, str]] = None
    s_config_keys_types: Optional[Set[Type]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init empty dicts if None was provided
        self.d_config_defaults = empty_dict_if_none(self.d_config_defaults)
        self.d_config_types = empty_dict_if_none(self.d_config_types)
        self.d_config_cline_args = empty_dict_if_none(self.d_config_cline_args)
        self.s_config_keys_types = empty_set_if_none(self.s_config_keys_types, coerce = True)


@dataclass
class RunArgs:
    """Dataclass for kwargs to be passed to the read_config function.
    """
    l_run_args: Optional[Sequence[Any]] = None
    d_run_kwargs: Optional[Dict[str, Any]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Init empty dicts if None was provided
        self.l_run_args = empty_list_if_none(self.l_run_args)
        self.d_run_kwargs = empty_dict_if_none(self.d_run_kwargs)


class SheExecutor:
    """ Class to handle primary execution of SHE executables. When run(args) is called, this performs the following
        tasks:

        - Logs the start of execution and a command to re-run this executable.
        - Reads in the pipeline configuration from the filename at args.pipeline_config and stores the dictionary
          in args.pipeline_config.
        - Determines from the pipeline configuration whether or not to profile the execution and logs this choice
        - Runs the primary executable either normally or via cProfile.
    """

    # Attributes which must be set at init
    run_from_args_function: Callable[..., None]
    log_options: LogOptions

    # Attributes which can be optionally set at init, or otherwise take default values
    config_args: ReadConfigArgs
    run_args: RunArgs

    # Attributes used during the run command
    _logger: Logger

    def __init__(self,
                 run_from_args_function: Callable[..., None],
                 log_options: LogOptions,
                 config_args: Optional[ReadConfigArgs] = None,
                 run_args: Optional[RunArgs] = None):
        """ Initializes the SheExecutor object.
        """

        # Store the attributes always set at init
        self.run_from_args_function = run_from_args_function
        self.log_options = log_options

        # Call private initialization functions for different types of attributes
        self.config_args = default_init_if_none(config_args, ReadConfigArgs)
        self.run_args = default_init_if_none(run_args, RunArgs)

    def run(self,
            args: Namespace,
            logger: Optional[Logger] = None,
            profile: Optional[bool] = None):

        # If a logger is provided, use that, otherwise construct one
        if logger is not None:
            self._logger = logger
        else:
            self._logger = getLogger(self.log_options.executable_name)

        self._logger.debug("#")
        self._logger.debug(f"# Entering {self.log_options.executable_name} mainMethod()")
        self._logger.debug("#")

        self.__log_exec_cmd(args)

        # load the pipeline config in
        # noinspection PyTypeChecker
        pipeline_config: Dict[ConfigKeys, Any] = read_config(args.pipeline_config,
                                                             workdir = args.workdir,
                                                             defaults = self.config_args.d_config_defaults,
                                                             d_cline_args = self.config_args.d_config_cline_args,
                                                             parsed_args = args,
                                                             config_keys = self.config_args.s_config_keys_types,
                                                             d_types = self.config_args.d_config_types)

        # set args.pipeline_config to the read-in pipeline_config
        args.pipeline_config = pipeline_config

        # check if profiling is to be enabled from the args, or else from the pipeline config
        if profile is not None:
            _profile: bool = profile
        else:
            _profile: bool = pipeline_config[GlobalConfigKeys.PIP_PROFILE]

        if _profile:
            self._logger.info("Profiling enabled")
            self.__run_with_profiling(args)
        else:
            self._logger.debug("Profiling disabled")
            self.run_from_args_function(args, *self.run_args.l_run_args, **self.run_args.d_run_kwargs)

        self._logger.info('#')
        self._logger.debug('Exiting SHE_Validation_ValidateShearBias mainMethod()')
        self._logger.info('#')

    def __run_with_profiling(self, args):
        """ Calls the run function with profiling enabled.
        """
        import cProfile

        profiling_filename: str = os.path.join(args.workdir, args.logdir, f"{self.log_options.executable_name}.prof")
        self._logger.info("Writing profiling data to %s", profiling_filename)

        cProfile.runctx("run_from_args_function(args)", {},
                        {"run_from_args_function": self.run_from_args_function,
                         "args"                  : args,
                         "l_run_args"            : self.run_args.l_run_args,
                         "d_run_kwargs"          : self.run_args.d_run_kwargs},
                        filename = "validate_shear_bias_from_args.prof")

    def __log_exec_cmd(self, args: Namespace) -> None:
        """ Construct the run command and log it at info level.
        """

        exec_cmd_base: str = (f"E-Run {self.log_options.project_name} {self.log_options.project_version} "
                              f"{self.log_options.executable_name}")

        exec_cmd: str = get_arguments_string(args,
                                             cmd = exec_cmd_base,
                                             store_true = self.log_options.s_store_true,
                                             store_false = self.log_options.s_store_false)

        self._logger.info('Execution command for this step:')
        self._logger.info(exec_cmd)
