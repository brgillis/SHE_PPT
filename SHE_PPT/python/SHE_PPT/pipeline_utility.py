""" @file pipeline_utility.py

    Created 9 Aug 2018

    Misc. utility functions for the pipeline.
"""

__updated__ = "2021-08-19"

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

import json.decoder
import os
from argparse import ArgumentParser
from enum import EnumMeta
from functools import lru_cache
from pickle import UnpicklingError
from shutil import copyfile
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from xml.sax import SAXParseException

import numpy as np

from .constants.config import (AnalysisConfigKeys, CTI_GAL_VALIDATION_HEAD, CalibrationConfigKeys, ConfigKeys,
                               GlobalConfigKeys, ReconciliationConfigKeys, SHEAR_BIAS_VALIDATION_HEAD,
                               ScalingExperimentsConfigKeys, VALIDATION_HEAD,
                               ValidationConfigKeys, )
from .file_io import find_file, read_listfile, read_xml_product
from .logging import getLogger
from .utility import AllowedEnum, is_any_type_of_none


@lru_cache(maxsize = None)
def task_value(global_enum, task_head):
    """ Given one of the global enums for config options, return the name for the task-specific option.
    """
    if isinstance(global_enum, str):
        value = global_enum
    else:
        value = global_enum.value
    return value.replace(VALIDATION_HEAD, task_head)


def cti_gal_value(global_enum):
    """ Given one of the global enums for config options, return the name for the CTI-Gal task-specific option.
    """
    return task_value(global_enum, SHEAR_BIAS_VALIDATION_HEAD)


def shear_bias_value(global_enum):
    """ Given one of the global enums for config options, return the name for the CTI-Gal task-specific option.
    """
    return task_value(global_enum, CTI_GAL_VALIDATION_HEAD)


@lru_cache(maxsize = None)
def global_value(task_value, task_head):
    """ Reverse of task_value, returning the value - gives the value for the global option given the task option.
    """
    return task_value.replace(task_head, VALIDATION_HEAD)


@lru_cache(maxsize = None)
def global_enum(task_value, task_head):
    """ Reverse of task_value, returning the enum - gives the enum for the global option given the task option.
    """
    return ValidationConfigKeys(global_value(task_value, task_head))


def archive_product(product_filename: str,
                    archive_dir: str,
                    workdir: str) -> None:
    """ Copies an already-written data product to an archive directory.

        Parameters
        ----------
        product_filename : string
            The (unqualified) name of the product to copy
        archive_dir : string
            The root of the archive directory (note, the most-specific part of the workdir path (normally "workspace")
            will be added after this to keep separate runs from conflicting).
        workdir : string
            The working directory for this task

    """

    logger = getLogger(__name__)

    # Start by figuring out the subdirectory to store it in, based off of the workdir we're using
    subdir = os.path.split(workdir)[1]
    full_archive_dir = os.path.join(archive_dir, subdir)

    # The filename will likely also contain a subdir, so figure that out
    product_subpath = os.path.split(product_filename)[0]

    # Make the directory to store it in
    full_archive_subdir = os.path.join(full_archive_dir, product_subpath)
    full_archive_datadir = os.path.join(full_archive_dir, "data")
    if not os.path.exists(full_archive_subdir):
        os.makedirs(full_archive_subdir)
    if not os.path.exists(full_archive_datadir):
        os.makedirs(full_archive_datadir)

    # Copy the file to the archive
    qualified_filename = os.path.join(workdir, product_filename)
    qualified_archive_product_filename = os.path.join(full_archive_dir, product_filename)
    copyfile(qualified_filename, qualified_archive_product_filename)

    # Copy any files it points to to the archive as well
    try:
        p = read_xml_product(qualified_filename)

        # Remove all files this points to
        if hasattr(p, "get_all_filenames"):
            data_filenames = p.get_all_filenames()
            for data_filename in data_filenames:
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

    except Exception as e:
        logger.warning(("Failsafe exception block triggered when trying to save statistics product "
                        "in archive. Exception was: %s"),
                       str(e))


def read_analysis_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """ Reads in a configuration file for the SHE Analysis pipeline to a dictionary.
    """

    return read_config(config_keys = AnalysisConfigKeys,
                       *args, **kwargs)


def read_calibration_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """ Reads in a configuration file for the SHE Calibration pipeline to a dictionary.
    """

    return read_config(config_keys = CalibrationConfigKeys,
                       *args, **kwargs)


def read_reconciliation_config(*args, **kwargs) -> Dict[ConfigKeys, Any]:
    """ Reads in a configuration file for the SHE Reconciliation pipeline to a dictionary. Note that all arguments will
        be read as strings.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        parsed_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the parsed_args.
    """

    return read_config(config_keys = ReconciliationConfigKeys,
                       *args, **kwargs)


def read_scaling_config(*args, **kwargs):
    """ Reads in a configuration file for the SHE Scaling pipeline to a dictionary.
    """

    return read_config(config_keys = ScalingExperimentsConfigKeys, *args, **kwargs)


def read_config(config_filename: Optional[str],
                workdir: str = ".",
                config_keys: Union[EnumMeta, Tuple[EnumMeta, ...]] = (AnalysisConfigKeys,
                                                                      ValidationConfigKeys,
                                                                      ReconciliationConfigKeys,
                                                                      CalibrationConfigKeys),
                d_cline_args: Optional[Dict[ConfigKeys, str]] = None,
                parsed_args: Optional[ArgumentParser] = None,
                defaults: Optional[Dict[str, Any]] = None,
                task_head: Optional[str] = None,
                d_types: Optional[Dict[str, Type]] = None, ) -> Dict[ConfigKeys, Any]:
    """ Reads in a generic configuration file to a dictionary. Note that all arguments will be read as strings unless
        a cline_arg value is used.

        Parameters
        ----------
        config_filename : Optional[str]
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        config_keys : enum or iterable of enums
            ConfigKeys enum or iterable of enums listing allowed keys
        parsed_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the parsed_args.
        task_head: string
            Should only be set if reading configs for a Validation task. In this case, this refers to the "head" of
            the task-specific configuration keys. These task-specific arguments will be used to override the
            global arguments if set to anything other than None.
        d_types: Dict[str, Type]
            Dict of desired types to convert values in the config to. If not provided, all values will be left
            as strings.
    """

    # Use empty dicts for d_cline_args and defaults if None provided
    if d_cline_args is None:
        d_cline_args = {}
    if defaults is None:
        defaults = {}

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
                                                         d_cline_args = d_cline_args,
                                                         parsed_args = parsed_args,
                                                         defaults = defaults,
                                                         d_types = d_types)

    # Look in the workdir for the config filename if it isn't fully-qualified
    if not config_filename[0] == "/":
        qualified_config_filename = os.path.join(workdir, config_filename)
    else:
        qualified_config_filename = config_filename

    try:

        filelist = read_listfile(qualified_config_filename)

        # If we get here, it is a listfile. If no files in it, return an empty dict. If one, return that.
        # If more than one,raise an exception
        if len(filelist) == 0:
            return _make_config_from_cline_args_and_defaults(config_keys = config_keys,
                                                             d_cline_args = d_cline_args,
                                                             parsed_args = parsed_args,
                                                             defaults = defaults,
                                                             d_types = d_types, )
        if len(filelist) == 1:
            return _read_config_product(config_filename = filelist[0],
                                        workdir = workdir,
                                        config_keys = config_keys,
                                        d_cline_args = d_cline_args,
                                        parsed_args = parsed_args,
                                        defaults = defaults,
                                        task_head = task_head,
                                        d_types = d_types, )

        raise ValueError("File " + qualified_config_filename + " is a listfile with more than one file listed, and " +
                         "is an invalid input to read_config.")

    except (json.decoder.JSONDecodeError, UnicodeDecodeError):

        # This isn't a listfile, so try to open and return it
        return _read_config_product(config_filename = config_filename,
                                    workdir = workdir,
                                    config_keys = config_keys,
                                    d_cline_args = d_cline_args,
                                    parsed_args = parsed_args,
                                    defaults = defaults,
                                    task_head = task_head,
                                    d_types = d_types)


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

    except (UnicodeDecodeError, SAXParseException, UnpicklingError):

        # Try to read it as a plain text file
        return _read_config_file(qualified_config_filename = find_file(config_filename, workdir),
                                 *args, **kwargs)


def _read_config_file(qualified_config_filename: str,
                      config_keys: Tuple[EnumMeta, ...],
                      d_cline_args: Optional[Dict[ConfigKeys, str]],
                      parsed_args: Optional[ArgumentParser],
                      defaults: Dict[ConfigKeys, Any],
                      task_head: Optional[str] = None,
                      d_types: Optional[Dict[str, Type]] = None, ) -> Dict[ConfigKeys, Any]:
    """ Reads in a configuration text file.
    """

    # Start with a config generated from defaults
    config_dict = _make_config_from_defaults(config_keys = config_keys,
                                             defaults = defaults)

    with open(qualified_config_filename, 'r') as config_file:

        # Keep a set of any keys we want to block from being able to overwrite
        blocked_keys = set()

        # Read in the file, except for comment lines
        for config_line in config_file:

            stripped_line = config_line.strip()

            # Ignore comment or empty lines
            if config_line[0] == '#' or len(stripped_line) == 0:
                continue

            # Ignore comment portion
            noncomment_line = config_line.split('#')[0]

            # Get the key and value from the line
            equal_split_line = noncomment_line.split('=')

            key_string = equal_split_line[0].strip()
            if key_string in blocked_keys:
                continue
            try:
                enum_key = _check_key_is_valid(key_string, config_keys)
            except ValueError as e:

                # If we're allowing task-specific keys, check if that's the case
                if task_head is None:
                    raise

                # Check if this is a valid task-specific key
                global_key_string = global_value(key_string, task_head)
                try:
                    enum_key = _check_key_is_valid(global_key_string, config_keys)
                except Exception:
                    # The global key isn't valid, so raise the original exception
                    raise e

                # If we get here, this is a valid task-specific key, so set it to the dict in
                # place of the global key
                key_string = global_key_string

                # Add it to the blocked_keys set, so if we encounter the global key later, we
                # won't override this for this task
                blocked_keys.update(key_string)

            # In case the value contains an = char
            value = noncomment_line.replace(equal_split_line[0] + '=', '').strip()

            # If the value is None or equivalent, don't set it (use the default)
            if not (is_any_type_of_none(value) and enum_key in defaults):
                config_dict[enum_key] = value

        # End for config_line in config_file:

    # End with open(qualified_config_filename, 'r') as config_file:

    # If we're provided with any cline-args, override values from the config with them
    for enum_key in d_cline_args:
        if d_cline_args[enum_key] is None:
            continue
        _check_enum_key_is_valid(enum_key, config_keys)
        val_from_cline_args = getattr(parsed_args, d_cline_args[enum_key])
        if not is_any_type_of_none(val_from_cline_args):
            config_dict[enum_key] = getattr(parsed_args, d_cline_args[enum_key])

    # Convert the types in the config as desired
    config_dict = convert_config_types(config_dict, d_types)

    return config_dict


def _make_config_from_defaults(config_keys: Tuple[EnumMeta, ...],
                               defaults: Dict[ConfigKeys, Any],
                               d_types: Optional[Dict[ConfigKeys, Type]] = None) -> Dict[ConfigKeys, Any]:
    """ Make a pipeline config dict from just the defaults.
    """

    config_dict = {}

    for enum_key in defaults:
        _check_enum_key_is_valid(enum_key, config_keys)
        config_dict[enum_key] = defaults[enum_key]

    # Convert the types in the config as desired
    config_dict = convert_config_types(config_dict, d_types)

    return config_dict


def _make_config_from_cline_args_and_defaults(config_keys: Tuple[EnumMeta, ...],
                                              d_cline_args: Dict[ConfigKeys, str],
                                              parsed_args: ArgumentParser,
                                              defaults: Dict[ConfigKeys, Any],
                                              d_types: Optional[Dict[ConfigKeys, Type]] = None) -> Dict[
    ConfigKeys, Any]:
    """ Make a pipeline config dict from the cline-args and defaults, preferring
        the cline-args if they're available.
    """
    # Start with a config generated from defaults
    config_dict = _make_config_from_defaults(config_keys = config_keys,
                                             defaults = defaults)

    # Return if we don't have any parsed_args to deal with
    if not (d_cline_args or parsed_args):
        return config_dict

    for enum_key in d_cline_args:
        if d_cline_args[enum_key] is None:
            continue
        _check_enum_key_is_valid(enum_key, config_keys)
        val_from_cline_args = getattr(parsed_args, d_cline_args[enum_key])
        if not is_any_type_of_none(val_from_cline_args):
            config_dict[enum_key] = getattr(parsed_args, d_cline_args[enum_key])

    # Convert the types in the config as desired
    config_dict = convert_config_types(config_dict, d_types)

    return config_dict


def _check_enum_key_is_valid(enum_key: ConfigKeys,
                             config_keys: Tuple[EnumMeta, ...]) -> EnumMeta:
    """Checks if a enum key a valid member of one of the config_keys Enums. If so, returns the EnumMeta it's found in.
    """

    found = False
    for config_key_enum_meta in config_keys:
        if enum_key in config_key_enum_meta:
            found = True
            break

    if not found:
        err_string = f"{enum_key} is not a valid member of any of the EnumMetas: {config_keys}. Allowed keys are:\n"
        for config_key_enum_meta in config_keys:
            for enum_key in config_key_enum_meta:
                err_string += f"{enum_key}"
        raise ValueError(err_string)

    return config_key_enum_meta


def _check_key_is_valid(key: str,
                        config_keys: Tuple[EnumMeta, ...]) -> ConfigKeys:
    """ Checks if a pipeline config key is valid by searching for it in the provided config keys Enums. If found,
        returns the Enum for it.
    """

    enum = None
    for config_key_enum in config_keys:
        enum = config_key_enum.find_value(key)
        if enum:
            break

    if not enum:
        err_string = (f"Invalid pipeline config key found: {key}. Allowed keys are: ")
        for config_key_enum in config_keys:
            for allowed_key in config_key_enum:
                err_string += "\n  " + allowed_key.value
        raise ValueError(err_string)

    return enum


def write_analysis_config(config_dict: Dict[ConfigKeys, Any],
                          config_filename: str,
                          workdir: str = ".", ) -> None:
    """ Writes a dictionary to an Analysis configuration file.

        Parameters
        ----------
        config_dict : Dict[ConfigKeys, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict = config_dict,
                        config_filename = config_filename,
                        workdir = workdir,
                        config_keys = AnalysisConfigKeys)


def write_reconciliation_config(config_dict: Dict[ConfigKeys, Any],
                                config_filename: str,
                                workdir: str = ".", ) -> None:
    """ Writes a dictionary to an Reconciliation configuration file.

        Parameters
        ----------
        config_dict : Dict[ConfigKeys, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict = config_dict,
                        config_filename = config_filename,
                        workdir = workdir,
                        config_keys = ReconciliationConfigKeys)


def write_calibration_config(config_dict: Dict[ConfigKeys, Any],
                             config_filename: str,
                             workdir: str = ".", ) -> None:
    """ Writes a dictionary to an Calibration configuration file.

        Parameters
        ----------
        config_dict : Dict[ConfigKeys, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict = config_dict,
                        config_filename = config_filename,
                        workdir = workdir,
                        config_keys = CalibrationConfigKeys)


def write_scaling_config(config_dict: Dict[ConfigKeys, Any],
                         config_filename: str,
                         workdir: str = ".", ) -> None:
    """ Writes a dictionary to an ScalingExperiments configuration file.

        Parameters
        ----------
        config_dict : Dict[ConfigKeys, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict = config_dict,
                        config_filename = config_filename,
                        workdir = workdir,
                        config_keys = ScalingExperimentsConfigKeys)


def write_config(config_dict: Dict[ConfigKeys, Any],
                 config_filename: str,
                 workdir: str = ".",
                 config_keys: EnumMeta = ConfigKeys, ) -> None:
    """ Writes a dictionary to a configuration file.

        Parameters
        ----------
        config_dict : Dict[ConfigKeys, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
        config_keys : EnumMeta
            ConfigKeys EnumMeta listing allowed keys
    """

    # Silently coerce config_keys into iterable if just one enum is supplied, and also include GlobalConfigKeys
    # in the list
    if issubclass(config_keys, ConfigKeys):
        config_keys = (config_keys, GlobalConfigKeys)
    elif GlobalConfigKeys not in config_keys:
        config_keys = (*config_keys, GlobalConfigKeys)

    # Silently return if dict and filename are None
    if config_dict is None and config_filename is None:
        return

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

            config_file.write(f"{enum_key.value} = {value}\n")


def _get_converted_enum_type(value: str, enum_type: EnumMeta):
    """ Gets and retuns the value converted to a desired type of Enum, assuming it's originally the string value of
        that Enum.
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


def _get_converted_type(value: str, desired_type: Type):
    """ Gets and retuns the value converted to a desired type.
    """

    # Check if it's already been converted
    if not isinstance(value, str):
        if isinstance(value, desired_type):
            return value
        try:
            return desired_type(value)
        except TypeError:
            raise TypeError(f"Value {value} cannot be converted to type {desired_type}.")

    # Special handling for certain types
    if desired_type is bool:
        # Booleans will always convert a string to True unless it's empty, so we check the value of the string here
        converted_value = value.lower() in ['true', 't']

    elif desired_type is np.ndarray:
        # Convert space-separated lists into arrays of floats
        values_list = list(map(float, value.strip().split()))
        converted_value = np.array(values_list, dtype = float)

    else:
        converted_value = desired_type(value)

    return converted_value


def _convert_tuple_type(pipeline_config: Dict[ConfigKeys, Any],
                        enum_key: ConfigKeys,
                        tuple_type: Tuple[Type, Type]) -> None:
    """ Converts a type expressed as a tuple. Currently the only format accepted is where index 0 is list
        and index 1 is the type of the list elements.
    """

    # Skip if not present in the config
    if not enum_key in pipeline_config or pipeline_config[enum_key] is None:
        return

    if not tuple_type[0] == list:
        raise ValueError("Type conversion only accepts list as the first argument to tuple types at present.")

    # Get the type to convert to, and the function to handle conversion
    desired_type: Type = tuple_type[1]
    if issubclass(desired_type, AllowedEnum):
        convert_func = _get_converted_enum_type
    else:
        convert_func = _get_converted_type

    # Split the list by whitespace
    l_str_values: List[str] = pipeline_config[enum_key].strip().split()

    # Convert each item in the list in turn
    l_values: Any = [None] * len(l_str_values)
    for i in range(len(l_str_values)):
        l_values[i] = convert_func(l_str_values[i], desired_type)

    # Update the pipeline config
    pipeline_config[enum_key] = l_values


def _convert_enum_type(pipeline_config: Dict[ConfigKeys, Any],
                       enum_key: ConfigKeys,
                       enum_type: EnumMeta) -> None:
    """ Checks that the value in the pipeline_config is properly a value of the given enum_type,
        and sets the entry in the pipeline_config to the proper enum.
    """

    # Skip if not present in the config
    if enum_key not in pipeline_config:
        return

    # Check that the value is in the enum (silently convert to lower case)
    value = pipeline_config[enum_key]

    enum_value = _get_converted_enum_type(value, enum_type)

    # Set enum_value
    pipeline_config[enum_key] = enum_value


def _convert_type(pipeline_config: Dict[ConfigKeys, Any],
                  enum_key: ConfigKeys,
                  desired_type: Type) -> None:
    """ Checks if a key is in the pipeline_config. If so, converts the value to the desired type.
    """

    if not enum_key in pipeline_config:
        return

    value = pipeline_config[enum_key]

    converted_value = _get_converted_type(value, desired_type)

    pipeline_config[enum_key] = converted_value


def convert_config_types(pipeline_config: Dict[ConfigKeys, str],
                         d_types: Dict[ConfigKeys, Type] = None) -> Dict[ConfigKeys, Any]:
    """ Converts values in the pipeline config to the proper types.
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


def get_conditional_product(filename: str,
                            workdir: str = ".") -> Optional[Any]:
    """ Returns None in all cases where a data product isn't provided, otherwise read and return the data
        product.
    """

    # First check for None
    if filename is None or filename == "None" or filename == "":
        return None

    # Find the file, and check if it's a listfile
    qualified_filename = find_file(filename, workdir)

    try:

        filelist = read_listfile(qualified_filename)

        # If we get here, it is a listfile. If no files in it, return None. If one, return that. If more than one,
        # raise an exception
        if len(filelist) == 0:
            return None
        if len(filelist) == 1:
            return read_xml_product(filelist[0], workdir)

        raise ValueError("File " + qualified_filename + " is a listfile with more than one file listed, and " +
                         "is an invalid input to get_conditional_product.")

    except (json.decoder.JSONDecodeError, UnicodeDecodeError):

        # This isn't a listfile, so try to open and return it
        return read_xml_product(qualified_filename, workdir)
