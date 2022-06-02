""" @file pipeline_utility.py

    Created 9 Aug 2018

    Misc. utility functions used for pipeline-related tasks.
"""

__updated__ = "2022-06-02"

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
from enum import EnumMeta
from functools import lru_cache
from shutil import copyfile
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, TextIO, Tuple, Type, TypeVar, Union

import numpy as np

from .constants.classes import AllowedEnum
from .constants.config import (AnalysisConfigKeys, CTI_GAL_VALIDATION_HEAD, CalibrationConfigKeys, ConfigKeys,
                               GlobalConfigKeys, ReconciliationConfigKeys, SHEAR_BIAS_VALIDATION_HEAD,
                               ScalingExperimentsConfigKeys, VALIDATION_HEAD, ValidationConfigKeys, )
from .file_io import (DEFAULT_WORKDIR, SheFileReadError, find_file, get_qualified_filename, read_listfile,
                      read_xml_product, )
from .logging import getLogger
from .utility import is_any_type_of_none


@lru_cache(maxsize = None)
def get_task_value(global_enum: ConfigKeys,
                   task_head: str) -> str:
    """Given one of the global enums for a validation config option, return the value for the task-specific option.

    Parameters
    ----------
    global_enum : ConfigKeys
        The ConfigKeys enum for the global option, e.g. `ValidationConfigKeys.VAL_SNR_BIN_LIMITS`
    task_head : str
        The task-specific head to add to the option name, once it's been stripped of the global head,
        e.g. SHEAR_BIAS_VALIDATION_HEAD

    Returns
    -------
    str
        The value of the task-specific option.
    """
    if isinstance(global_enum, str):
        value = global_enum
    else:
        value = global_enum.value
    return value.replace(VALIDATION_HEAD, task_head)


def get_cti_gal_value(global_enum: ConfigKeys) -> str:
    """Given one of the global enums for a validation config option, return the value for the CTI-Gal task-specific
    option.

    Parameters
    ----------
    global_enum : ConfigKeys
        The ConfigKeys enum for the global option, e.g. `ValidationConfigKeys.VAL_SNR_BIN_LIMITS`

    Returns
    -------
    str
        The value of the CTI-Gal task-specific option.
    """
    return get_task_value(global_enum, CTI_GAL_VALIDATION_HEAD)


def get_shear_bias_value(global_enum: ConfigKeys) -> str:
    """Given one of the global enums for a validation config option, return the value for the Shear Bias task-specific
    option.

    Parameters
    ----------
    global_enum : ConfigKeys
        The ConfigKeys enum for the global option, e.g. `ValidationConfigKeys.VAL_SNR_BIN_LIMITS`

    Returns
    -------
    str
        The value of the Shear Bias task-specific option.
    """
    return get_task_value(global_enum, SHEAR_BIAS_VALIDATION_HEAD)


@lru_cache(maxsize = None)
def get_global_value(task_value: str,
                     task_head: str) -> str:
    """ Reverse of get_task_value, returning the value - gives the value for the global option given the task option.

    Parameters
    ----------
    task_value : str
        The ConfigKeys enum for the global option, e.g. `ValidationConfigKeys.VAL_SNR_BIN_LIMITS`
    task_head : str
        The task-specific head to remove from the option name, to be repalced with the global head,

    Returns
    -------
    str
        The value of the global option.
    """
    return task_value.replace(task_head, VALIDATION_HEAD)


@lru_cache(maxsize = None)
def get_global_enum(task_value: str,
                    task_head: str) -> ConfigKeys:
    """ Reverse of task_value, returning the enum - gives the enum for the global option given the task option.

    Parameters
    ----------
    task_value : str
        The ConfigKeys enum for the global option, e.g. `ValidationConfigKeys.VAL_SNR_BIN_LIMITS`
    task_head : str
        The task-specific head to remove from the option name, to be repalced with the global head,

    Returns
    -------
    ConfigKeys
        The enum of the global option.
    """
    return ValidationConfigKeys(get_global_value(task_value, task_head))


def archive_product(product_filename: str,
                    archive_dir: str,
                    workdir: str) -> None:
    """Copies an already-written data product to an archive directory.

    Parameters
    ----------
    product_filename : str
        The workdir-relative name of the product to copy
    archive_dir : str
        The root of the archive directory (note, the most-specific part of the workdir path (normally "workspace")
        will be added after this to keep separate runs from conflicting).
    workdir : str
        The working directory for this task
    """

    logger = getLogger(__name__)

    # Start by figuring out the subdirectory to store it in, based off of the workdir we're using
    full_archive_dir = os.path.join(archive_dir, os.path.split(workdir)[1])

    # Make the directory to store it in
    # The filename will likely also contain a subdir, include that
    full_archive_subdir = os.path.join(full_archive_dir, os.path.split(product_filename)[0])
    full_archive_datadir = os.path.join(full_archive_dir, "data")
    if not os.path.exists(full_archive_subdir):
        os.makedirs(full_archive_subdir)
    if not os.path.exists(full_archive_datadir):
        os.makedirs(full_archive_datadir)

    # Copy the file to the archive
    qualified_filename = os.path.join(workdir, product_filename)
    copyfile(qualified_filename, os.path.join(full_archive_dir, product_filename))

    # Copy any files it points to to the archive as well
    try:
        p = read_xml_product(qualified_filename)

        # Copy all files this points to
        if hasattr(p, "get_all_filenames"):
            for data_filename in p.get_all_filenames():
                if data_filename is not None and data_filename != "default_filename.fits" and data_filename != "":
                    qualified_data_filename = os.path.join(workdir, data_filename)
                    qualified_archive_data_filename = os.path.join(full_archive_dir, data_filename)

                    # The filename will likely also contain a subdir, so figure that out
                    full_archive_data_subpath = os.path.split(qualified_archive_data_filename)[0]
                    if not os.path.exists(full_archive_data_subpath):
                        os.makedirs(full_archive_data_subpath)

                    copyfile(qualified_data_filename, qualified_archive_data_filename)

        else:
            logger.warning("Product %s has no 'get_all_filenames' method.", qualified_filename)

    except IOError as e:
        logger.warning(("Failsafe exception block triggered when trying to save product "
                        "in archive. Exception was: %s"), str(e))


def read_analysis_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """Reads in a configuration file for the SHE Analysis pipeline to a dictionary.

    Parameters
    ----------
    *args, **kwargs : Any
        Any position and keyword arguments to pass to `read_config`.

    Returns
    -------
    Dict[ConfigKeys, Any]
        A dictionary of the configuration options.
    """

    return read_config(*args, config_keys = AnalysisConfigKeys, **kwargs)


def read_calibration_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """ Reads in a configuration file for the SHE Calibration pipeline to a dictionary.

    Parameters
    ----------
    *args, **kwargs : Any
        Any position and keyword arguments to pass to `read_config`.

    Returns
    -------
    Dict[ConfigKeys, Any]
        A dictionary of the configuration options.
    """

    return read_config(*args, config_keys = CalibrationConfigKeys, **kwargs)


def read_reconciliation_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """Reads in a configuration file for the SHE Reconciliation pipeline to a dictionary.

    Parameters
    ----------
    *args, **kwargs : Any
        Any position and keyword arguments to pass to `read_config`.

    Returns
    -------
    Dict[ConfigKeys, Any]
        A dictionary of the configuration options.
    """

    return read_config(*args, config_keys = ReconciliationConfigKeys, **kwargs)


def read_scaling_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """Reads in a configuration file for the SHE Scaling pipeline to a dictionary.

    Parameters
    ----------
    *args, **kwargs : Any
        Any position and keyword arguments to pass to `read_config`.

    Returns
    -------
    Dict[ConfigKeys, Any]
        A dictionary of the configuration options.
    """

    return read_config(*args, config_keys = ScalingExperimentsConfigKeys, **kwargs)


def read_config(config_filename: Optional[str] = None,
                workdir: str = DEFAULT_WORKDIR,
                config_keys: Union[EnumMeta, Sequence[EnumMeta]] = (AnalysisConfigKeys,
                                                                    ValidationConfigKeys,
                                                                    ReconciliationConfigKeys,
                                                                    CalibrationConfigKeys),
                d_cline_args: Optional[Dict[ConfigKeys, str]] = None,
                d_defaults: Optional[Dict[ConfigKeys, Any]] = None,
                d_types: Optional[Dict[ConfigKeys, Type]] = None,
                parsed_args: Optional[Union[Namespace, Dict[str, Any]]] = None,
                task_head: Optional[str] = None) -> Dict[ConfigKeys, Any]:
    """Reads in a generic configuration file to a dictionary. Note that all arguments will be read as strings unless
    a cline_arg value is used.

    Parameters
    ----------
    config_filename : Optional[str], default=None
        The workspace-relative name of the config file.
    workdir : str, default="."
        The working directory.
    config_keys : Union[EnumMeta, Sequence[EnumMeta]], default=(AnalysisConfigKeys, ValidationConfigKeys,
    ReconciliationConfigKeys, CalibrationConfigKeys)
        ConfigKeys enum or iterable of enums listing allowed keys.
    d_cline_args: Optional[Dict[ConfigKeys, str]], default=None
        Dict listing cline-args which can override each config value in the config file.
    d_defaults : Optional[Dict[ConfigKeys, Any]], default=None
        Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
        supplied in the parsed_args.
    d_types: OptionalDict[ConfigKeys, Type]], default=None
        Dict of desired types to convert values in the config to. If not provided, all values will be left
        as strings.
    parsed_args : Optional[Union[Namespace, Dict[str, Any]]], default=None
        Namespace or dict giving values passed at the command line. If these aren't None, they will override
        values in the config file
    task_head: Optional[str], default=None
        Should only be set if reading configs for a Validation task. In this case, this refers to the "head" of
        the task-specific configuration keys. These task-specific arguments will be used to override the
        global arguments if set to anything other than None.

    Returns
    -------
    Dict[ConfigKeys, Any]
        A dictionary of the configuration options.
    """

    # Make sure we have a dictionary of parsed arguments
    d_args = _coerce_parsed_args_to_dict(parsed_args)

    # Use empty dicts for d_cline_args and defaults if None provided
    if d_cline_args is None:
        d_cline_args = {}
    if d_defaults is None:
        d_defaults = {}

    # Check for validity of use of task_head
    if task_head is not None and not issubclass(config_keys, ValidationConfigKeys):
        raise ValueError("task_head should only be set for read_config if config_keys is ValidationConfigKeys "
                         "or a subclass of it (and not a list of ConfigKeys).")

    # Silently coerce config_keys into iterable if just one enum is supplied, and also include GlobalConfigKeys
    # in the list
    try:
        if issubclass(config_keys, ConfigKeys):
            config_keys = (config_keys, GlobalConfigKeys)
    except TypeError:
        config_keys = (*config_keys, GlobalConfigKeys)

    # Return None if input filename is None
    if is_any_type_of_none(config_filename):
        return _make_config_from_cline_args_and_defaults(config_keys = config_keys,
                                                         d_args = d_args,
                                                         d_cline_args = d_cline_args,
                                                         d_defaults = d_defaults,
                                                         d_types = d_types)

    # Get the qualified filename of the config file
    qualified_config_filename = get_qualified_filename(config_filename, workdir = workdir)

    try:

        l_filenames = read_listfile(qualified_config_filename)

        # If we get here, it is a listfile. If no files in it, return an empty dict. If one, return that.
        # If more than one,raise an exception
        if len(l_filenames) == 0:
            d_config = _make_config_from_cline_args_and_defaults(config_keys = config_keys,
                                                                 d_args = d_args,
                                                                 d_cline_args = d_cline_args,
                                                                 d_defaults = d_defaults,
                                                                 d_types = d_types, )
        elif len(l_filenames) == 1:
            d_config = _read_config_product(config_filename = l_filenames[0],
                                            workdir = workdir,
                                            config_keys = config_keys,
                                            d_args = d_args,
                                            d_cline_args = d_cline_args,
                                            d_defaults = d_defaults,
                                            d_types = d_types,
                                            task_head = task_head, )
        else:
            raise ValueError(
                "File " + qualified_config_filename + " is a listfile with more than one file listed, and " +
                "is an invalid input to read_config.")

    except SheFileReadError:

        # This isn't a listfile, so try to open and return it
        d_config = _read_config_product(config_filename = config_filename,
                                        workdir = workdir,
                                        config_keys = config_keys,
                                        d_args = d_args,
                                        d_cline_args = d_cline_args,
                                        d_defaults = d_defaults,
                                        d_types = d_types,
                                        task_head = task_head)

    return d_config


def _coerce_parsed_args_to_dict(parsed_args: Optional[Union[Namespace, Dict[str, Any]]]) -> Dict[str, Any]:
    """Private function to coerce a parsed arguments object into a dict.
    """
    d_args: Dict[str, Any]
    if parsed_args is None:
        d_args = {}
    elif isinstance(parsed_args, dict):
        d_args = parsed_args
    else:
        # Assume parsed_args is a Namespace or similar
        d_args = vars(parsed_args)
    return d_args


def _read_config_product(config_filename: str,
                         workdir: str,
                         *args, **kwargs) -> Dict[ConfigKeys, Any]:
    """Reads in a configuration data product.
    """

    # Try to read in as a data product
    try:
        p = read_xml_product(config_filename, workdir)

        config_data_filename = p.get_data_filename()

        return _read_config_file(qualified_config_filename = find_file(config_data_filename, workdir),
                                 *args, **kwargs)

    except SheFileReadError:

        # Try to read it as a plain text file
        return _read_config_file(qualified_config_filename = find_file(config_filename, workdir),
                                 *args, **kwargs)


def _read_config_file(qualified_config_filename: str,
                      config_keys: Sequence[EnumMeta],
                      d_args: Dict[str, Any],
                      d_cline_args: Dict[ConfigKeys, str],
                      d_defaults: Dict[ConfigKeys, Any],
                      d_types: Optional[Dict[str, Type]] = None,
                      task_head: Optional[str] = None, ) -> Dict[ConfigKeys, Any]:
    """ Private implementation of reading in a configuration text file.
    """

    with open(qualified_config_filename, 'r') as config_file:

        config_dict = _read_config_dict_from_file(config_filehandle = config_file,
                                                  config_keys = config_keys,
                                                  d_defaults = d_defaults,
                                                  task_head = task_head, )

    # End with open(qualified_config_filename, 'r') as config_file:

    # If we're provided with any cline-args, override values from the config with them
    for enum_key in d_cline_args:
        if d_cline_args[enum_key] is None:
            continue
        _check_enum_key_is_valid(enum_key, config_keys)
        try:
            val_from_cline_args = d_args[d_cline_args[enum_key]]
        except KeyError:
            # If its not present, treat as None and skip
            continue
        if not is_any_type_of_none(val_from_cline_args):
            config_dict[enum_key] = val_from_cline_args

    # Convert the types in the config as desired
    config_dict = _convert_config_types(config_dict, d_types)

    return config_dict


def _read_config_dict_from_file(config_filehandle: TextIO,
                                config_keys: Sequence[EnumMeta],
                                d_defaults: Dict[ConfigKeys, Any],
                                task_head: Optional[str] = None, ) -> Dict[ConfigKeys, Any]:
    """Private implementation of reading in a config dict from a file.
    """

    # Make a config dict from defaults
    d_default_config = _make_config_from_defaults(config_keys = config_keys,
                                                  d_defaults = d_defaults)

    config_dict: Dict[ConfigKeys, Any] = {}

    # Keep a dict relating global and task keys, so we can sync them at the end
    d_global_task_keys: Dict[ConfigKeys, ConfigKeys] = {}

    # Read in the file, except for comment lines
    for config_line in config_filehandle:

        _read_config_line(config_line = config_line,
                          config_dict = config_dict,
                          config_keys = config_keys,
                          d_defaults = d_defaults,
                          d_global_task_keys = d_global_task_keys,
                          task_head = task_head, )

    # Fill in any missing keys with defaults
    for enum_key in d_default_config:
        if not (enum_key in config_dict and not is_any_type_of_none(config_dict[enum_key])):
            config_dict[enum_key] = d_default_config[enum_key]

    # If we're using a task_head, update the d_global_task_keys dict using the defaults
    if task_head is not None:
        for enum_key in d_default_config:
            if not enum_key.value.startswith(task_head):
                continue
            try:
                global_enum_key = get_global_enum(enum_key.value, task_head)
            except ValueError:
                # Continue if it's a key unique to the task
                continue
            d_global_task_keys[global_enum_key] = enum_key

    # Sync the global and task keys
    for global_enum_key, local_enum_key in d_global_task_keys.items():
        config_dict[local_enum_key] = config_dict[global_enum_key]

    return config_dict


def _read_config_line(config_line: str,
                      config_dict: Dict[ConfigKeys, Any],
                      config_keys: Sequence[EnumMeta],
                      d_defaults: Dict[ConfigKeys, Any],
                      d_global_task_keys: Dict[ConfigKeys, ConfigKeys],
                      task_head: Optional[str], ) -> None:
    """Private implementation of reading a single line of a config file and updating the config dict.
    """

    stripped_line = config_line.strip()

    # Ignore comment or empty lines
    if config_line[0] == '#' or len(stripped_line) == 0:
        return

    # Ignore comment portion
    non_comment_line = config_line.split('#')[0]

    # Get the key and value from the line
    equal_split_line = non_comment_line.split('=')
    key_string = equal_split_line[0].strip()

    enum_key = _check_key_is_valid(key_string, config_keys)

    # Skip if this key has already been set by its task version
    if ((enum_key in d_global_task_keys) and (enum_key in config_dict) and not is_any_type_of_none(
            config_dict[enum_key])):
        return

    # In case the value contains an = char
    value = non_comment_line.replace(equal_split_line[0] + '=', '').strip()

    # If we're allowing task-specific keys, check if that's the case
    if task_head is not None:

        enum_key = _check_for_task_key(config_keys = config_keys,
                                       d_global_task_keys = d_global_task_keys,
                                       enum_key = enum_key,
                                       key_string = key_string,
                                       task_head = task_head, )

    # If the value is None or equivalent, don't set it (use the default or the global value)
    if not (is_any_type_of_none(value) and (enum_key in d_defaults or task_head is not None)):
        config_dict[enum_key] = value


def _check_for_task_key(config_keys: Sequence[EnumMeta],
                        d_global_task_keys: Dict[ConfigKeys, ConfigKeys],
                        enum_key: ConfigKeys,
                        key_string: str,
                        task_head: str) -> ConfigKeys:
    """Private function to handle sorting out overriding of a global key with a task-specific key when reading in a
       pipeline config.
    """
    # Check if this is a valid task-specific key
    global_key_string = get_global_value(key_string, task_head)
    if global_key_string != key_string:

        # This is a possible task-specific key
        local_enum_key = enum_key

        try:

            enum_key = _check_key_is_valid(global_key_string, config_keys)

            # Add it to the dict relating known global and task keys
            d_global_task_keys[enum_key] = local_enum_key

        except ValueError:
            # This is a key unique to the task, so don't override and block the global key,
            # and use what we thought might have been the local key instead
            enum_key = local_enum_key

    return enum_key


def _make_config_from_defaults(config_keys: Sequence[EnumMeta],
                               d_defaults: Dict[ConfigKeys, Any],
                               d_types: Optional[Dict[ConfigKeys, Type]] = None) -> Dict[ConfigKeys, Any]:
    """Make a pipeline config dict from just the defaults.
    """

    config_dict = {}

    for enum_key in d_defaults:
        _check_enum_key_is_valid(enum_key, config_keys)
        config_dict[enum_key] = d_defaults[enum_key]

    # Convert the types in the config as desired
    config_dict = _convert_config_types(config_dict, d_types)

    return config_dict


def _make_config_from_cline_args_and_defaults(config_keys: Sequence[EnumMeta],
                                              d_args: Dict[str, Any],
                                              d_cline_args: Dict[ConfigKeys, str],
                                              d_defaults: Dict[ConfigKeys, Any],
                                              d_types: Optional[Dict[ConfigKeys, Type]] = None) -> \
        Dict[ConfigKeys, Any]:
    """Make a pipeline config dict from the cline-args and defaults, preferring
    the cline-args if they're available.
    """

    # Start with a config generated from defaults
    config_dict = _make_config_from_defaults(config_keys = config_keys,
                                             d_defaults = d_defaults)

    # Return if we don't have any parsed_args to deal with
    if not (d_cline_args or d_args):
        return config_dict

    for enum_key in d_cline_args:
        if d_cline_args[enum_key] is None:
            continue
        _check_enum_key_is_valid(enum_key, config_keys)

        # If attribute isn't present, treat as None
        try:
            val_from_cline_args = d_args[d_cline_args[enum_key]]
        except KeyError:
            val_from_cline_args = None

        if not is_any_type_of_none(val_from_cline_args):
            config_dict[enum_key] = val_from_cline_args

    # Convert the types in the config as desired
    config_dict = _convert_config_types(config_dict, d_types)

    return config_dict


def _check_enum_key_is_valid(enum_key: ConfigKeys,
                             config_keys: Iterable[EnumMeta]) -> EnumMeta:
    """Checks if a enum key a valid member of one of the config_keys Enums. If so, returns the EnumMeta it's found in.
    """

    found = False
    config_key_enum_meta: Optional[EnumMeta] = None
    for config_key_enum_meta in config_keys:
        if enum_key in config_key_enum_meta:
            found = True
            break

    if not found:
        err_string = f"{enum_key} is not a valid member of any of the EnumMetas: {config_keys}. Allowed keys are:\n"
        for config_key_enum_meta in config_keys:
            for possible_enum_key in config_key_enum_meta:
                err_string += f"{possible_enum_key}"
        raise ValueError(err_string)

    return config_key_enum_meta


def _check_key_is_valid(key: str,
                        config_keys: Sequence[EnumMeta]) -> ConfigKeys:
    """Checks if a pipeline config key is valid by searching for it in the provided config keys Enums. If found,
    returns the Enum for it.
    """

    enum = None
    for config_key_enum in config_keys:
        enum = config_key_enum.find_value(key)
        if enum:
            break

    if not enum:
        err_string = f"Invalid pipeline config key found: {key}. Allowed keys are: "
        for config_key_enum in config_keys:
            for allowed_key in config_key_enum:
                err_string += "\n  " + allowed_key.value
        raise ValueError(err_string)

    return enum


def write_analysis_config(config_dict: Dict[ConfigKeys, Any],
                          config_filename: str,
                          workdir: str = DEFAULT_WORKDIR, ) -> None:
    """Writes a dictionary to an Analysis configuration file.

    Parameters
    ----------
    config_dict : Dict[ConfigKeys, Any]
        The config dictionary to write out.
    config_filename : str
        The desired workspace-relative name of the config file.
    workdir : str, default='.'
        The working directory.
    """

    write_config(config_dict = config_dict,
                 config_filename = config_filename,
                 workdir = workdir,
                 config_keys = AnalysisConfigKeys)


def write_reconciliation_config(config_dict: Dict[ConfigKeys, Any],
                                config_filename: str,
                                workdir: str = DEFAULT_WORKDIR, ) -> None:
    """Writes a dictionary to an Reconciliation configuration file.

    Parameters
    ----------
    config_dict : Dict[ConfigKeys, Any]
        The config dictionary to write out.
    config_filename : str
        The desired workspace-relative name of the config file.
    workdir : str, default='.'
        The working directory.
    """

    write_config(config_dict = config_dict,
                 config_filename = config_filename,
                 workdir = workdir,
                 config_keys = ReconciliationConfigKeys)


def write_calibration_config(config_dict: Dict[ConfigKeys, Any],
                             config_filename: str,
                             workdir: str = DEFAULT_WORKDIR, ) -> None:
    """Writes a dictionary to an Calibration configuration file.

    Parameters
    ----------
    config_dict : Dict[ConfigKeys, Any]
        The config dictionary to write out.
    config_filename : str
        The desired workspace-relative name of the config file.
    workdir : str, default='.'
        The working directory.
    """

    write_config(config_dict = config_dict,
                 config_filename = config_filename,
                 workdir = workdir,
                 config_keys = CalibrationConfigKeys)


def write_scaling_config(config_dict: Dict[ConfigKeys, Any],
                         config_filename: str,
                         workdir: str = DEFAULT_WORKDIR, ) -> None:
    """Writes a dictionary to an ScalingExperiments configuration file.

    Parameters
    ----------
    config_dict : Dict[ConfigKeys, Any]
        The config dictionary to write out.
    config_filename : str
        The desired workspace-relative name of the config file.
    workdir : str, default='.'
        The working directory.
    """

    write_config(config_dict = config_dict,
                 config_filename = config_filename,
                 workdir = workdir,
                 config_keys = ScalingExperimentsConfigKeys)


def write_config(config_dict: Dict[ConfigKeys, Any],
                 config_filename: str,
                 workdir: str = DEFAULT_WORKDIR,
                 config_keys: Union[EnumMeta, Sequence[EnumMeta]] = ConfigKeys, ) -> None:
    """Writes a dictionary to a configuration file.

    Parameters
    ----------
    config_dict : Dict[ConfigKeys, Any]
        The config dictionary to write out.
    config_filename : str
        The desired workspace-relative name of the config file.
    workdir : str, default='.'
        The working directory.
    config_keys : EnumMeta, default=ConfigKeys
        ConfigKeys EnumMeta listing allowed keys
    """

    # Silently coerce config_keys into iterable if just one enum is supplied, and also include GlobalConfigKeys
    # in the list
    try:
        if issubclass(config_keys, ConfigKeys):
            config_keys = (config_keys, GlobalConfigKeys)
    except TypeError:
        config_keys = (*config_keys, GlobalConfigKeys)

    qualified_config_filename = os.path.join(workdir, config_filename)

    if os.path.exists(qualified_config_filename):
        os.remove(qualified_config_filename)

    with open(qualified_config_filename, 'w') as config_file:

        # Write out each entry in a line
        for enum_key in config_dict:
            _check_enum_key_is_valid(enum_key, config_keys)

            # Get the value, and check if it's an enum. If so, print the value instead of the string repr
            value = config_dict[enum_key]
            try:
                value = value.value
            except AttributeError:
                pass

            # Now check if it's a list
            try:
                if not isinstance(value, str):
                    value = " ".join(map(str, value))
            except TypeError:
                pass

            config_file.write(f"{enum_key.value} = {value}\n")


def _get_converted_enum_type(value: str, enum_type: EnumMeta):
    """Private function to get and return the value converted to a desired type of Enum, assuming it's originally
    the string value of that Enum.
    """

    # Check if it's already been converted to the proper type
    if isinstance(value, enum_type):
        return value

    value_lower = value.lower()
    enum_value = enum_type.find_lower_value(value_lower)
    if not enum_value:
        err_string = f"Config option {value} for is not recognized as type {enum_type}. Allowed options are:"
        for allowed_option in enum_type:
            err_string += "\n  " + allowed_option.value

        raise ValueError(err_string)
    return enum_value


def _get_converted_list_type(value: str,
                             list_type: Tuple[Type[list], Type]):
    """Private function to get and return the value converted to a list of the desired type.
    """
    item_type = list_type[1]

    # Get the function to handle conversion
    convert_func = _get_convert_func(item_type)

    # Split the list by whitespace
    if isinstance(value, list) and isinstance(value[0], str):
        l_str_values: List[str] = value
    elif isinstance(value, str):
        l_str_values: List[str] = value.strip().split()
    else:
        raise TypeError(f"Unrecognized type for pipeline_config[enum_key]: {type(value)}")

    # Convert each item in the list in turn
    l_values: Any = [None] * len(l_str_values)
    for i, str_value in enumerate(l_str_values):
        l_values[i] = convert_func(str_value, item_type)

    return l_values


def _get_converted_type(value: str, desired_type: Type):
    """Private function to get and return the value converted to a desired type.
    """

    # Check if it's already been converted
    if not isinstance(value, str):
        if isinstance(value, desired_type):
            return value
        try:
            return desired_type(value)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Value {value} cannot be converted to type {desired_type}.")

    # Special handling for certain types
    if desired_type is bool:
        # Booleans will always convert a string to True unless it's empty, so we check the value of the string here
        converted_value = value.lower() in ['true', 't', '1', 1]

    elif desired_type is np.ndarray:
        # Check first if the value is None
        if is_any_type_of_none(value):
            converted_value = np.array([])
        else:
            # Convert space-separated lists into arrays of floats
            values_list = list(map(float, value.strip().split()))
            converted_value = np.array(values_list, dtype = float)

    else:
        converted_value = desired_type(value)

    return converted_value


PrimaryType = TypeVar("PrimaryType")
BackupType = TypeVar("BackupType")


def _convert_tuple_type(pipeline_config: Dict[ConfigKeys, Any],
                        enum_key: ConfigKeys,
                        tuple_type: Tuple[Union[Type[List], PrimaryType], Union[Type, BackupType]]) -> None:
    """Private function to convert a type expressed as a tuple. The formats currently accepted are:
        * Element 0 is "list" and Element 1 is the type of item in the list
        * Element 0 is the primary desired type, and Element 1 is the backup desired type, if it cannot be
          converted to the primary desired type. In this case, Element 0 cannot simply be "list" - if a list is
          desired, Element 0 should instead be a tuple of "list" and the desired item type.
    """

    # Skip if not present in the config or already converted
    # noinspection PyTypeHints
    if ((enum_key not in pipeline_config or pipeline_config[enum_key] is None) or
            (not isinstance(pipeline_config[enum_key], str))):
        return

    # Forward to appropriate method for the type of conversion appropriate for the tuple type provided
    if tuple_type[0] == list:
        _convert_list_type(pipeline_config = pipeline_config,
                           enum_key = enum_key,
                           item_type = tuple_type[1])
    else:
        _convert_with_backup_type(pipeline_config = pipeline_config,
                                  enum_key = enum_key,
                                  primary_type = tuple_type[0],
                                  backup_type = tuple_type[1])


def _convert_list_type(pipeline_config: Dict[ConfigKeys, Any],
                       enum_key: ConfigKeys,
                       item_type: Type) -> None:
    """Private function to convert a config item into a list of the desired type.
    """

    value = pipeline_config[enum_key]

    try:
        pipeline_config[enum_key] = _get_converted_list_type(value, (list, item_type))
    except (TypeError, ValueError) as e:
        raise type(e)(f"Value {value} provided with key {enum_key} in the pipeline config cannot be converted "
                      f"to a list of type {item_type}.") from e


def _convert_with_backup_type(pipeline_config: Dict[ConfigKeys, Any],
                              enum_key: ConfigKeys,
                              primary_type: Type[PrimaryType],
                              backup_type: Type[BackupType]) -> None:
    """Private function to convert a config item into the primary type if possible, or the backup type if not.
    """

    value = pipeline_config[enum_key]
    converted_value: Union[PrimaryType, BackupType]
    # Return if the value is already is one of the desired types (with an exception if the backup type is str, since
    # values are initially parsed as strings, and we don't know if it's an unconverted string or not)
    if isinstance(value, primary_type) or (backup_type != str and isinstance(value, backup_type)):
        return

    primary_convert_func = _get_convert_func(primary_type)
    try:
        converted_value = primary_convert_func(value, primary_type)
    except (TypeError, ValueError):
        try:
            backup_convert_func = _get_convert_func(backup_type)
            converted_value = backup_convert_func(value, backup_type)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Value {value} provided with key {enum_key} in the pipeline config cannot be converted "
                          f"to either type {primary_type} or {backup_type}.") from e

    pipeline_config[enum_key] = converted_value


def _get_convert_func(item_type: Union[Type, Tuple[Type[list], Type]]) -> Callable:
    """Private function to get the proper function to handle conversion to the desired type.
    """
    if isinstance(item_type, tuple) and item_type[0] == list:
        return _get_converted_list_type
    if issubclass(item_type, AllowedEnum):
        return _get_converted_enum_type
    return _get_converted_type


def _convert_enum_type(pipeline_config: Dict[ConfigKeys, Any],
                       enum_key: ConfigKeys,
                       enum_type: EnumMeta) -> None:
    """Private function to check that the value in the pipeline_config is properly a value of the given enum_type,
    and sets the entry in the pipeline_config to the proper enum.
    """

    # Check that the value is in the enum (silently convert to lower case)
    value = pipeline_config[enum_key]

    enum_value = _get_converted_enum_type(value, enum_type)

    # Set enum_value
    pipeline_config[enum_key] = enum_value


def _convert_type(pipeline_config: Dict[ConfigKeys, Any],
                  enum_key: ConfigKeys,
                  desired_type: Type) -> None:
    """Private function to check if a key is in the pipeline_config. If so, converts the value to the desired type.
    """

    if enum_key not in pipeline_config:
        return

    value = pipeline_config[enum_key]

    converted_value = _get_converted_type(value, desired_type)

    pipeline_config[enum_key] = converted_value


def _convert_config_types(pipeline_config: Dict[ConfigKeys, str],
                          d_types: Dict[ConfigKeys, Type] = None) -> Dict[ConfigKeys, Any]:
    """Private function to convert values in the pipeline config to the proper types.
    """

    # If d_types is None, return without making any changes
    if d_types is None:
        return pipeline_config

    # Convert values
    for key, desired_type in d_types.items():
        # Use special handling for types expressed as tuples and enum types
        if isinstance(desired_type, tuple):
            _convert_tuple_type(pipeline_config, key, desired_type)
        elif issubclass(desired_type, AllowedEnum):
            _convert_enum_type(pipeline_config, key, desired_type)
        else:
            _convert_type(pipeline_config, key, desired_type)

    return pipeline_config


def get_conditional_product(filename: Optional[str],
                            workdir: str = ".") -> Optional[Any]:
    """Returns None in all cases where a data product isn't provided, otherwise read and return the data
    product.

    Parameters
    ----------
    filename : Optional[str],
        The filename of the data product to read.
    workdir : str, default='.'
        The directory to read the data product from.

    Returns
    -------
    Optional[Any]
        The data product, or None if the data product is not provided.
    """

    # First check for None
    if is_any_type_of_none(filename):
        return None

    # Find the file, and check if it's a listfile
    qualified_filename = find_file(filename, workdir)

    p: Any

    try:

        l_filenames = read_listfile(qualified_filename)

        # If we get here, it is a listfile. If no files in it, return None. If one, return that. If more than one,
        # raise an exception
        if len(l_filenames) == 0:
            p = None
        elif len(l_filenames) == 1:
            p = read_xml_product(l_filenames[0], workdir)
        else:
            raise ValueError("File " + qualified_filename + " is a listfile with more than one file listed, and " +
                             "is an invalid input to get_conditional_product.")

    except SheFileReadError:

        # This isn't a listfile, so try to open and return it
        p = read_xml_product(qualified_filename, workdir)

    return p
