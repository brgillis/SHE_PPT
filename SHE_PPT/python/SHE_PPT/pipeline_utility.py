""" @file pipeline_utility.py

    Created 9 Aug 2018

    Misc. utility functions for the pipeline.
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

__updated__ = "2020-07-22"

from enum import Enum
import json.decoder
import os
from pickle import UnpicklingError
from shutil import copyfile
from xml.sax._exceptions import SAXParseException

from SHE_PPT import magic_values as mv
from SHE_PPT import products
from SHE_PPT.file_io import read_xml_product, read_listfile, find_file
from SHE_PPT.logging import getLogger


class AnalysisConfigKeys(Enum):
    """ An Enum of all allowed keys for the SHE analysis pipelines.
    """

    # Options for SHE_MER_RemapMosaic

    remap_head = "SHE_MER_RemapMosaic_"

    REMAP_NUM_THREADS_EXP = remap_head + "num_threads_exposures"
    REMAP_NUM_SWARP_THREADS_EXP = remap_head + "num_swarp_threads_exposures"
    REMAP_NUM_THREADS_STACK = remap_head + "num_threads_stack"
    REMAP_NUM_SWARP_THREADS_STACK = remap_head + "num_swarp_threads_stack"

    # Options for SHE_CTE_ObjectIdSplit

    oid_head = "SHE_CTE_ObjectId_"

    OID_BATCH_SIZE = oid_head + "batch_size"
    OID_MAX_BATCHES = oid_head + "max_batches"
    OID_IDS = oid_head + "ids"

    # Options for SHE_CTE_EstimateShear

    es_head = "SHE_CTE_EstimateShear_"

    ES_METHODS = es_head + "methods"
    ES_CHAINS_METHOD = es_head + "chains_method"

    # Options for SHE_CTE_ShearEstimatesMerge

    sem_head = "SHE_CTE_ShearEstimatesMerge_"

    SEM_NUM_THREADS = sem_head + "number_threads"

    @classmethod
    def is_allowed_value(cls, value):
        return value in [item.value for item in cls]


class CalibrationConfigKeys(Enum):
    """ An Enum of all allowed keys for the SHE calibration pipelines.
    """

    # Options for SHE_CTE_CleanupBiasMeasurement

    cbm_head = "SHE_CTE_CleanupBiasMeasurement_"

    CBM_CLEANUP = cbm_head + "cleanup"

    # Options for SHE_CTE_EstimateShear

    ES_METHODS = AnalysisConfigKeys.ES_METHODS
    ES_CHAINS_METHOD = AnalysisConfigKeys.ES_CHAINS_METHOD

    # Options for SHE_CTE_MeasureBias

    mb_head = "SHE_CTE_MeasureBias_"

    MB_ARCHIVE_DIR = mb_head + "archive_dir"
    MB_NUM_THREADS = mb_head + "number_threads"
    MB_WEBDAV_ARCHIVE = mb_head + "webdav_archive"
    MB_WEBDAV_DIR = mb_head + "webdav_dir"

    # Options for SHE_CTE_MeasureStatistics

    ms_head = "SHE_CTE_MeasureStatistics_"

    MS_ARCHIVE_DIR = ms_head + "archive_dir"
    MS_WEBDAV_ARCHIVE = ms_head + "webdav_archive"
    MS_WEBDAV_DIR = ms_head + "webdav_dir"

    @classmethod
    def is_allowed_value(cls, value):
        return value in [item.value for item in cls]


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
            logger.warning("Product " + qualified_filename + " has no 'get_all_filenames' method.")

    except Exception as e:
        logger.warning("Failsafe exception block triggered when trying to save statistics product in archive. " +
                    "Exception was: " + str(e))

    return


def read_config(config_filename, workdir="."):
    """ Reads in a generic configuration file to a dictionary. Note that all arguments will be read as strings.

        Parameters
        ----------
        config_filename : string
            The workspace-relative name of the config file.
        workdir : string
            The working directory.
    """

    # Return None if input filename is None
    if config_filename is None or config_filename is "None" or config_filename is "":
        return {}

    qualified_config_filename = os.path.join(workdir, config_filename)

    try:

        filelist = read_listfile(qualified_config_filename)

        # If we get here, it is a listfile. If no files in it, return None. If one, return that. If more than one,
        # raise an exception
        if len(filelist) == 0:
            return {}
        elif len(filelist) == 1:
            return _read_config_product(filelist[0], workdir)
        else:
            raise ValueError("File " + qualified_config_filename + " is a listfile with more than one file listed, and " +
                             "is an invalid input to read_config.")

    except (json.decoder.JSONDecodeError, UnicodeDecodeError):

        # This isn't a listfile, so try to open and return it
        return _read_config_product(config_filename, workdir)


def _read_config_product(config_filename, workdir):

    # Try to read in as a data product
    try:
        p = read_xml_product(config_filename, workdir)

        config_data_filename = p.get_data_filename()

        return _read_config_file(find_file(config_data_filename, workdir))

    except (UnicodeDecodeError, SAXParseException, UnpicklingError) as _e:

        # Try to read it as a plain text file
        return _read_config_file(find_file(config_filename, workdir))


def _read_config_file(qualified_config_filename):

    config_dict = {}

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

            # Check that the key is allowed
            if not ConfigKeys.is_allowed_value(key):
                err_string = ("Invalid key found in pipeline config file " + qualified_config_filename + ": " +
                              key + ". Allowed keys are: ")
                for allowed_key in ConfigKeys:
                    err_string += "\n  " + allowed_key.value
                raise ValueError(err_string)

            # In case the value contains an = char
            value = noncomment_line.replace(equal_split_line[0] + '=', '').strip()

            config_dict[key] = value

        # End for config_line in config_file:

    # End with open(qualified_config_filename, 'r') as config_file:

    return config_dict


def write_config(config_dict, config_filename, workdir="."):
    """ Writes a dictionary to a configuration file.

        Parameters
        ----------
        config_dict : string
            The config dictionary to write out.
        config_filename : string
            The desired workspace-relative name of the config file.
        workdir : string
            The working directory.
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

            # Check that the key is allowed
            if not ConfigKeys.is_allowed_value(key):
                err_string = ("Invalid key found in pipeline config dict: " +
                              key + ". Allowed keys are: ")
                for allowed_key in ConfigKeys:
                    err_string += "\n--" + allowed_key.value
                raise ValueError(err_string)

            config_file.write(str(key) + " = " + str(config_dict[key]) + "\n")

    return


def get_conditional_product(filename, workdir="."):
    """ Returns None in all cases where a data product isn't provided, otherwise read and return the data
        product.
    """

    # First check for None
    if filename is None or filename is "None" or filename is "":
        return None

    # Find the file, and check if it's a listfile
    qualified_filename = find_file(filename, workdir)

    try:

        filelist = read_listfile(qualified_filename)

        # If we get here, it is a listfile. If no files in it, return None. If one, return that. If more than one,
        # raise an exception
        if len(filelist) == 0:
            return None
        elif len(filelist) == 1:
            return read_xml_product(filelist[0], workdir)
        else:
            raise ValueError("File " + qualified_filename + " is a listfile with more than one file listed, and " +
                             "is an invalid input to get_conditional_product.")

    except (json.decoder.JSONDecodeError, UnicodeDecodeError):

        # This isn't a listfile, so try to open and return it
        return read_xml_product(qualified_filename, workdir)
