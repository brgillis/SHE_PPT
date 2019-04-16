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

__updated__ = "2019-04-16"

from enum import Enum
import os
from shutil import copyfile

from SHE_PPT import magic_values as mv
from SHE_PPT.file_io import read_xml_product
from SHE_PPT.logging import getLogger


class ConfigKeys(Enum):
    """ An Enum of all allowed keys for pipeline_config files.
    """

    ES_METHODS = "SHE_CTE_EstimateShear_methods"

    OID_BATCH_SIZE = "SHE_CTE_ObjectIdSplit_batch_size"

    REMAP_MAX_THREADS = "SHE_MER_RemapMosaic_max_threads"

    CBM_CLEANUP = "SHE_CTE_CleanupBiasMeasurement_cleanup"

    MB_ARCHIVE_DIR = "SHE_CTE_MeasureBias_archive_dir"
    MB_WEBDAV_ARCHIVE = "SHE_CTE_MeasureBias_webdav_archive"
    MB_WEBDAV_DIR = "SHE_CTE_MeasureBias_webdav_dir"

    MS_ARCHIVE_DIR = "SHE_CTE_MeasureStatistics_archive_dir"
    MS_WEBDAV_ARCHIVE = "SHE_CTE_MeasureStatistics_webdav_archive"
    MS_WEBDAV_DIR = "SHE_CTE_MeasureStatistics_webdav_dir"


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
                    copyfile(qualified_data_filename, qualified_archive_data_filename)

        else:
            logger.warn("Product " + qualified_filename + " has no 'get_all_filenames' method.")

    except Exception as e:
        logger.warn("Failsafe exception block triggered when trying to save statistics product in archive. " +
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
    if config_filename is None:
        return None

    config_dict = {}

    qualified_config_filename = os.path.join(workdir, config_filename)

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
            if not key in list(map(str, ConfigKeys)):
                err_string = ("Invalid key found in pipeline config file " + qualified_config_filename + ": " +
                              key + ". Allowed keys are: ")
                for allowed_key in ConfigKeys:
                    err_string += "\n--" + allowed_key.value
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
            if not key in list(map(str, ConfigKeys)):
                err_string = ("Invalid key found in pipeline config dict: " +
                              key + ". Allowed keys are: ")
                for allowed_key in ConfigKeys:
                    err_string += "\n--" + allowed_key.value
                raise ValueError(err_string)

            config_file.write(str(key) + " = " + str(config_dict[key]) + "\n")

    return
