""" @file pipeline_utility.py

    Created 9 Aug 2018

    Misc. utility functions for the pipeline.
"""

__updated__ = "2021-03-01"

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
from pickle import UnpicklingError
from shutil import copyfile
from typing import Any, Dict, Tuple, Union
from xml.sax._exceptions import SAXParseException

from . import magic_values as mv
from .file_io import read_xml_product, read_listfile, find_file
from .logging import getLogger
from .utility import AllowedEnum, is_any_type_of_none


# Derived class for ConfigKeys, to allow more precise type-checking
class ConfigKeys(AllowedEnum):
    pass


# Task names for Analysis pipeline
REMAP_HEAD = "SHE_MER_RemapMosaic_"
OBJECT_ID_SPLIT_HEAD = "SHE_CTE_ObjectIdSplit_"
ESTIMATE_SHEAR_HEAD = "SHE_CTE_EstimateShear_"
SHEAR_ESTIMATES_MERGE_HEAD = "SHE_CTE_ShearEstimatesMerge_"
CTI_GAL_VALIDATION_HEAD = "SHE_Validation_ValidateCTIGal_"


class AnalysisConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE analysis pipelines.
    """

    # Options for SHE_MER_RemapMosaic

    REMAP_NUM_THREADS_EXP = REMAP_HEAD + "num_threads_exposures"
    REMAP_NUM_SWARP_THREADS_EXP = REMAP_HEAD + "num_swarp_threads_exposures"
    REMAP_NUM_THREADS_STACK = REMAP_HEAD + "num_threads_stack"
    REMAP_NUM_SWARP_THREADS_STACK = REMAP_HEAD + "num_swarp_threads_stack"

    # Options for SHE_CTE_ObjectIdSplit

    OID_BATCH_SIZE = OBJECT_ID_SPLIT_HEAD + "batch_size"
    OID_MAX_BATCHES = OBJECT_ID_SPLIT_HEAD + "max_batches"
    OID_IDS = OBJECT_ID_SPLIT_HEAD + "ids"

    # Options for SHE_CTE_EstimateShear

    ES_METHODS = ESTIMATE_SHEAR_HEAD + "methods"
    ES_CHAINS_METHOD = ESTIMATE_SHEAR_HEAD + "chains_method"

    # Options for SHE_CTE_ShearEstimatesMerge

    SEM_NUM_THREADS = SHEAR_ESTIMATES_MERGE_HEAD + "number_threads"

    # Options for SHE_Validation_ValidateCTIGal

    CGV_SLOPE_FAIL_SIGMA = CTI_GAL_VALIDATION_HEAD + "slope_fail_sigma"
    CGV_INTERCEPT_FAIL_SIGMA = CTI_GAL_VALIDATION_HEAD + "intercept_fail_sigma"
    CGV_FAIL_SIGMA_SCALING = CTI_GAL_VALIDATION_HEAD + "fail_sigma_scaling"

    CGV_SNR_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "snr_bin_limits"
    CGV_BG_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "bg_bin_limits"
    CGV_COLOUR_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "colour_bin_limits"
    CGV_SIZE_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "size_bin_limits"


# Task names for Reconciliation pipeline
RECONCILE_MEASUREMENTS_HEAD = "SHE_CTE_ReconcileMeasurements_"


class ReconciliationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE reconciliation pipeline.
    """

    # Options for SHE_CTE_CleanupBiasMeasurement

    REC_METHOD = RECONCILE_MEASUREMENTS_HEAD + "method"
    CHAINS_REC_METHOD = RECONCILE_MEASUREMENTS_HEAD + "chains_method"

# Task names for Calibration pipeline


CLEANUP_BIAS_MEASUREMENTS_HEAD = "SHE_CTE_CleanupBiasMeasurement_"
MEASURE_BIAS_HEAD = "SHE_CTE_MeasureBias_"
MEASURE_STATISTICS_HEAD = "SHE_CTE_MeasureStatistics_"


class CalibrationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE calibration pipelines.
    """

    # Options for SHE_CTE_CleanupBiasMeasurement

    CBM_CLEANUP = CLEANUP_BIAS_MEASUREMENTS_HEAD + "cleanup"

    # Options for SHE_CTE_EstimateShear - copy these from the other enum

    ES_METHODS = AnalysisConfigKeys.ES_METHODS.value
    ES_CHAINS_METHOD = AnalysisConfigKeys.ES_CHAINS_METHOD.value

    # Options for SHE_CTE_MeasureBias

    MB_ARCHIVE_DIR = MEASURE_BIAS_HEAD + "archive_dir"
    MB_NUM_THREADS = MEASURE_BIAS_HEAD + "number_threads"
    MB_WEBDAV_ARCHIVE = MEASURE_BIAS_HEAD + "webdav_archive"
    MB_WEBDAV_DIR = MEASURE_BIAS_HEAD + "webdav_dir"

    # Options for SHE_CTE_MeasureStatistics

    MS_ARCHIVE_DIR = MEASURE_STATISTICS_HEAD + "archive_dir"
    MS_WEBDAV_ARCHIVE = MEASURE_STATISTICS_HEAD + "webdav_archive"
    MS_WEBDAV_DIR = MEASURE_STATISTICS_HEAD + "webdav_dir"


def archive_product(product_filename, archive_dir, workdir):
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

    logger = getLogger(mv.logger_name)

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
            logger.warning("Product %s has no 'get_all_filenames' method.",qualified_filename)

    except Exception as e:
        logger.warning("Failsafe exception block triggered when trying to save statistics product in archive. " +
                       "Exception was: %s",str(e))



def read_analysis_config(config_filename: str,
                         workdir: str=".",
                         cline_args: Dict[str, Any]=None,
                         defaults: Dict[str, Any]=None) -> Dict[str, Any]:
    """ Reads in a configuration file for the SHE Analysis pipeline to a dictionary. Note that all arguments will
        be read as strings.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        cline_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the cline_args.
    """

    return read_config(config_filename=config_filename,
                       workdir=workdir,
                       config_keys=AnalysisConfigKeys,
                       cline_args=cline_args,
                       defaults=defaults)


def read_calibration_config(config_filename: str,
                            workdir: str=".",
                            cline_args: Dict[str, Any]=None,
                            defaults: Dict[str, Any]=None) -> Dict[str, Any]:
    """ Reads in a configuration file for the SHE Calibration pipeline to a dictionary. Note that all arguments will
        be read as strings.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        cline_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the cline_args.
    """

    return read_config(config_filename=config_filename,
                       workdir=workdir,
                       config_keys=CalibrationConfigKeys,
                       cline_args=cline_args,
                       defaults=defaults)


def read_reconciliation_config(config_filename: str,
                               workdir: str=".",
                               cline_args: Dict[str, Any]=None,
                               defaults: Dict[str, Any]=None) -> Dict[str, Any]:
    """ Reads in a configuration file for the SHE Reconciliation pipeline to a dictionary. Note that all arguments will
        be read as strings.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        cline_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the cline_args.
    """

    return read_config(config_filename=config_filename,
                       workdir=workdir,
                       config_keys=ReconciliationConfigKeys,
                       cline_args=cline_args,
                       defaults=defaults)


def read_config(config_filename: str,
                workdir: str=".",
                config_keys: Union[ConfigKeys, Tuple[ConfigKeys, ...]]=(AnalysisConfigKeys,
                                                                          ReconciliationConfigKeys,
                                                                          CalibrationConfigKeys),
                cline_args: Dict[str, Any]=None,
                defaults: Dict[str, Any]=None) -> Dict[str, Any]:
    """ Reads in a generic configuration file to a dictionary. Note that all arguments will be read as strings unless
        a cline_arg value is used.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
        config_keys : enum or iterable of enums
            ConfigKeys enum or iterable of enums listing allowed keys
        cline_args : Dict[str, Any]
            Dict of config keys giving values passed at the command line. If these aren't None, they will override
            values in the config file
        defaults : Dict[str, Any]
            Dict of default values to use if no value (or None) is supplied in the config and no value (or None) is
            supplied in the cline_args.
    """

    # Use empty dicts for cline_args and defaults if None provided
    if cline_args is None:
        cline_args = {}
    if defaults is None:
        defaults = {}

    # Return None if input filename is None
    if is_any_type_of_none(config_filename):
        return _make_config_from_cline_args_and_defaults(config_keys=config_keys,
                                                         cline_args=cline_args,
                                                         defaults=defaults,)

    # Silently coerce config_keys into iterable if just one enum is supplied
    if isinstance(config_keys, ConfigKeys):
        config_keys = (config_keys,)

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
            return _make_config_from_cline_args_and_defaults(config_keys=config_keys,
                                                             cline_args=cline_args,
                                                             defaults=defaults,)
        if len(filelist) == 1:
            return _read_config_product(config_filename=filelist[0],
                                        workdir=workdir,
                                        config_keys=config_keys,
                                        cline_args=cline_args,
                                        defaults=defaults)

        raise ValueError("File " + qualified_config_filename + " is a listfile with more than one file listed, and " +
                             "is an invalid input to read_config.")

    except (json.decoder.JSONDecodeError, UnicodeDecodeError):

        # This isn't a listfile, so try to open and return it
        return _read_config_product(config_filename=config_filename,
                                    workdir=workdir,
                                    config_keys=config_keys,
                                    cline_args=cline_args,
                                    defaults=defaults)


def _read_config_product(config_filename: str,
                         workdir: str,
                         config_keys: Tuple[ConfigKeys, ...],
                         cline_args: Dict[str, Any],
                         defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Reads in a configuration data product.
    """

    # Try to read in as a data product
    try:
        p = read_xml_product(config_filename, workdir)

        config_data_filename = p.get_data_filename()

        return _read_config_file(qualified_config_filename=find_file(config_data_filename, workdir),
                                 config_keys=config_keys,
                                 cline_args=cline_args,
                                 defaults=defaults)

    except (UnicodeDecodeError, SAXParseException, UnpicklingError):

        # Try to read it as a plain text file
        return _read_config_file(qualified_config_filename=find_file(config_filename, workdir),
                                 config_keys=config_keys,
                                 cline_args=cline_args,
                                 defaults=defaults)


def _read_config_file(qualified_config_filename: str,
                      config_keys: Tuple[ConfigKeys, ...],
                      cline_args: Dict[str, Any],
                      defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Reads in a configuration text file.
    """

    config_dict = _make_config_from_defaults(config_keys=config_keys,
                                             defaults=defaults)

    with open(qualified_config_filename, 'r') as config_file:

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

            key = equal_split_line[0].strip()
            _check_key_is_valid(key, config_keys)

            # In case the value contains an = char
            value = noncomment_line.replace(equal_split_line[0] + '=', '').strip()

            # If the value is None or equivalent, don't set it (use the default)
            if not (is_any_type_of_none(value) and key in defaults):
                config_dict[key] = value

        # End for config_line in config_file:

    # End with open(qualified_config_filename, 'r') as config_file:

    # If we're provided with any cline-args, override values from the config with them
    for key in cline_args:
        _check_key_is_valid(key, config_keys)
        value = cline_args[key]

        # Don't overwrite if we're given None
        if is_any_type_of_none(value):
            continue

        config_dict[key] = cline_args[key]

    return config_dict


def _make_config_from_defaults(config_keys: Tuple[ConfigKeys, ...],
                               defaults: Dict[str, Any]) -> Dict[str, Any]:
    """ Make a pipeline config dict from just the defaults.
    """

    config_dict = {}

    for key in defaults:
        _check_key_is_valid(key, config_keys)
        config_dict[key] = defaults[key]

    return config_dict


def _make_config_from_cline_args_and_defaults(config_keys: Tuple[ConfigKeys, ...],
                                              cline_args: Dict[str, Any],
                                              defaults: Dict[str, Any]) -> Dict[str, Any]:
    """ Make a pipeline config dict from the cline-args and defaults, preferring
        the cline-args if they're available.
    """

    config_dict = _make_config_from_defaults(config_keys=config_keys,
                                             defaults=defaults)

    for key in cline_args:
        _check_key_is_valid(key, config_keys)
        config_dict[key] = cline_args[key]

    return config_dict


def _check_key_is_valid(key: str,
                        config_keys: Tuple[ConfigKeys, ...]):
    """Checks if a pipeline config key is valid by searching for it in the provided config keys Enums.
    """

    allowed = False
    for config_key_enum in config_keys:
        if config_key_enum.is_allowed_value(key):
            allowed = True
            break

    if not allowed:
        err_string = ("Invalid pipeline config key found: " +
                      key + ". Allowed keys are: ")
        for config_key_enum in config_keys:
            for allowed_key in config_key_enum:
                err_string += "\n  " + allowed_key.value
        raise ValueError(err_string)

    return True


def write_analysis_config(config_dict: Dict[str, Any],
                          config_filename: str,
                          workdir: str=".",):
    """ Writes a dictionary to an Analysis configuration file.

        Parameters
        ----------
        config_dict : Dict[str, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict=config_dict,
                        config_filename=config_filename,
                        workdir=workdir,
                        config_keys=AnalysisConfigKeys)


def write_reconciliation_config(config_dict: Dict[str, Any],
                                config_filename: str,
                                workdir: str=".",):
    """ Writes a dictionary to an Reconciliation configuration file.

        Parameters
        ----------
        config_dict : Dict[str, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict=config_dict,
                        config_filename=config_filename,
                        workdir=workdir,
                        config_keys=ReconciliationConfigKeys)


def write_calibration_config(config_dict: Dict[str, Any],
                             config_filename: str,
                             workdir: str=".",):
    """ Writes a dictionary to an Calibration configuration file.

        Parameters
        ----------
        config_dict : Dict[str, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
    """

    return write_config(config_dict=config_dict,
                        config_filename=config_filename,
                        workdir=workdir,
                        config_keys=CalibrationConfigKeys)


def write_config(config_dict: Dict[str, Any],
                 config_filename: str,
                 workdir: str=".",
                 config_keys: ConfigKeys=AnalysisConfigKeys,):
    """ Writes a dictionary to a configuration file.

        Parameters
        ----------
        config_dict : Dict[str, Any]
            The config dictionary to write out.
        config_filename : str
            The desired workspace-relative name of the config file.
        workdir : str
            The working directory.
        config_keys : ConfigKeys
            ConfigKeys Enum listing allowed keys
    """

    # Silently return if dict and filename are None
    if config_dict is None and config_filename is None:
        return

    qualified_config_filename = os.path.join(workdir, config_filename)

    if os.path.exists(qualified_config_filename):
        os.remove(qualified_config_filename)

    with open(qualified_config_filename, 'w') as config_file:

        # Write out each entry in a line
        for key in config_dict:
            _check_key_is_valid(key, (config_keys,))
            config_file.write(str(key) + " = " + str(config_dict[key]) + "\n")

    return


def get_conditional_product(filename: str,
                            workdir: str="."):
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
