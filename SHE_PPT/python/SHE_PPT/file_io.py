""" @file file_io.py

    Created 29 Aug 2017

    Various functions for input/output
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2019-02-27"

from datetime import datetime
import json
import os
from os.path import join, isfile
from pickle import UnpicklingError
import pickle
import re
from xml.sax._exceptions import SAXParseException

from ElementsServices.DataSync import downloadTestData, localTestFile
from EuclidDmBindings.sys_stub import CreateFromDocument
from FilenameProvider.FilenameProvider import createFilename
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.utility import run_only_once
from astropy.io import fits


logger = getLogger(mv.logger_name)

type_name_maxlen = 45
instance_id_maxlen = 55
processing_function_maxlen = 4


@run_only_once
def warn_deprecated_timestamp():
    logger.warn("The use of the 'timestamp' kwarg in get_allowed_filename is deprecated and will be removed in a future version.")


def get_allowed_filename(type_name, instance_id, extension=".fits", release="00.05", subdir="data",
                         processing_function="SHE", timestamp=None):
    """Gets a filename in the required Euclid format. Now mostly a pass-through to the official version, with
    tweaks to silently shift arguments to upper-case.

    Parameters
    ----------
    type_name : str
        Label for what type of object this is. Maximum 45 characters.
    instance_id : str
        Label for the instance of this object. Maximum 37 characters if timestamp==True, 55 if False
    extension : str
        File extension (eg. ".fits").
    release : str
        Software/data release version, in format "XX.XX" where each X is a digit 0-9.
    subdir : str
        Subdirectory of work directory in which this file will be (default "data")
    processing_function : str
        Label for the processing function which created this file.
    timestamp : bool
        If True, will append a timestamp to the instance_id
    """

    # Silently shift instance_id to upper-case, and add timestamp if desired
    full_instance_id = instance_id.upper()
    if timestamp is not None:
        warn_deprecated_timestamp()

    # Check the extension doesn't start with "." and silently fix if it does
    if extension[0] == ".":
        extension = extension[1:]

    filename = createFilename(processing_function=processing_function,
                              data_product_type=type_name.upper(),
                              instance_id=full_instance_id,
                              extension=extension,
                              release=release)

    if subdir is not None:
        qualified_filename = join(subdir, filename)
    else:
        qualified_filename = filename

    return qualified_filename


def write_listfile(listfile_name, filenames):
    """
        @brief Writes a listfile in json format.

        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files

        @param listfile_name <str> Name of the listfile to be output.

        @param filenames <list<str>> List of filenames (or tuples of filenames) to be put in the listfile.
    """

    with open(listfile_name, 'w') as listfile:
        paths_json = json.dumps(filenames)
        listfile.write(paths_json)

    return


def read_listfile(listfile_name):
    """
        @brief Reads a json listfile and returns a list of filenames.

        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files

        @param listfile_name <str> Name of the listfile to be read.

        @return filenames <list<str>> List of filenames (or tuples of filenames) read in.
    """

    with open(listfile_name, 'r') as f:
        listobject = json.load(f)
        if len(listobject) == 0:
            return listobject
        if isinstance(listobject[0], list):
            return [tuple(el) for el in listobject]
        else:
            return listobject


def replace_in_file(input_filename, output_filename, input_string, output_string):
    """
        @brief Replaces every occurence of $input_string in $input_filename with $output_string
               and prints the results to $output_filename.

        @param input_filename <string>

        @param output_filename <string>

        @param input_string <string>

        @param output_string <string>
    """

    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                fout.write(line.replace(input_string, output_string))


def replace_multiple_in_file(input_filename, output_filename, input_strings, output_strings):
    """she_dpd
        @brief Replaces every occurence of an input_string in input_filename with the corresponding
               output string and prints the results to $output_filename.

        @param input_filename <string>

        @param output_filename <string>

        @param input_strings <iterable of string>

        @param output_strings <iterable of string>
    """

    with open(output_filename, "w") as fout:
        with open(input_filename, "r") as fin:
            for line in fin:
                new_line = line
                for input_string, output_string in zip(input_strings, output_strings):
                    new_line = new_line.replace(input_string, output_string)
                fout.write(new_line)


def write_xml_product(product, xml_file_name, allow_pickled=True):
    try:
        with open(str(xml_file_name), "w") as f:
            f.write(
                product.toDOM().toprettyxml(encoding="utf-8").decode("utf-8"))
    except AttributeError as e:
        if not allow_pickled:
            raise
        if not "object has no attribute 'toDOM'" in str(e):
            raise
        logger.warn(
            "XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, xml_file_name)


def read_xml_product(xml_file_name, allow_pickled=True):
    # @TODO: Should allow_pickled be False by default?
    # Read the xml file as a string
    try:
        with open(str(xml_file_name), "r") as f:
            xml_string = f.read()

        # Create a new product instance using the proper data product dictionary
        product = CreateFromDocument(xml_string)
    except (UnicodeDecodeError, SAXParseException) as _e:
        # Not actually saved as xml
        if allow_pickled:
            # Revert to pickled product
            return read_pickled_product(xml_file_name)
        else:
            raise

    return product


def write_pickled_product(product, pickled_file_name):

    with open(str(pickled_file_name), "wb") as f:
        pickle.dump(product, f)


def read_pickled_product(pickled_file_name):

    with open(str(pickled_file_name), "rb") as f:
        product = pickle.load(f)

    return product


def append_hdu(filename, hdu):

    f = fits.open(filename, mode='append')
    try:
        f.append(hdu)
    finally:
        f.close()


def find_file_in_path(filename, path):
    """
        Searches through a colon-separated path for a file and returns the qualified name of it if found,
        None otherwise.
    """

    colon_separated_path = path.split(":")

    qualified_filename = None

    for test_path in colon_separated_path:

        test_filename = join(test_path, filename)

        if isfile(test_filename):
            qualified_filename = test_filename
            break

    if qualified_filename is None:
        raise RuntimeError(
            "File " + str(filename) + " could not be found in path " + str(path) + ".")

    return qualified_filename


def find_aux_file(filename):
    """
        Searches the auxiliary directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_AUX_PATH'])


def find_conf_file(filename):
    """
        Searches the conf directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_CONF_PATH'])


def find_web_file(filename):
    """
        Searches on WebDAV for a file. If found, downloads it and returns the qualified name of it.
        If it isn't found, returns None.
    """

    filelist = os.path.join(os.getcwd(), os.path.splitext(os.path.split(filename)[-1])[0] + "_list.txt")

    logger.debug("Writing filelist to " + filelist)

    try:
        with open(filelist, 'w') as fo:
            fo.write(filename + "\n")

        downloadTestData("testdata/sync.conf", filelist)
        qualified_filename = localTestFile(mv.test_datadir, filename)
    except:
        raise
    finally:
        if os.path.exists(filelist):
            logger.debug("Cleaning up " + filelist)
            os.remove(filelist)

    return qualified_filename


def find_file(filename, path=None):
    """
        Locates a file based on the presence/absence of an AUX/ or CONF/ prefix, searching in the aux or conf
        directories respectively for it, or else the work directory if supplied.
    """

    if filename[0:4] == "WEB/":
        return find_web_file(filename[4:])
    elif filename[0:4] == "AUX/":
        return find_aux_file(filename[4:])
    elif filename[0:5] == "CONF/":
        return find_conf_file(filename[5:])
    elif filename[0:5] == "HOME/":
        path = os.path.join(os.getenv('HOME'),os.path.dirname(filename[5:]))
        return find_file_in_path(os.path.basename(filename), path)
    elif filename[0] == "/":
        if not os.path.exists(filename):
            raise RuntimeError("File " + filename + " cannot be found.")
        else:
            return filename
    elif path is not None:
        return find_file_in_path(filename, path)
    else:
        raise ValueError(
            "path must be supplied if filename doesn't start with AUX/ or CONF/")


def first_in_path(path):
    """
        Gets the first directory listed in the path.
    """

    return path.split(":")[0]


def first_writable_in_path(path):
    """
        Gets the first directory listed in the path which we have write access for.
    """

    colon_separated_path = path.split(":")

    first_writable_dir = None

    for test_path in colon_separated_path:

        if os.access(test_path, os.W_OK):
            first_writable_dir = test_path
            break

    return first_writable_dir


def get_data_filename(filename, workdir="."):
    """ Given the unqualified name of a file and the work directory, determine if it's an XML data
        product or not, and get the filename of its DataContainer if so; otherwise, just return
        the input filename. In either case, the unqualified filename is returned.

        This script is intended to help smooth the transition from using raw data files as
        input/output to data products.
    """

    # First, see if we can open this as an XML data product
    try:
        qualified_filename = find_file(filename, workdir)

        prod = read_xml_product(qualified_filename, allow_pickled=True)

        # If we get here, it is indeed an XML data product. Has it been monkey-patched
        # to have a get_filename method?

        if hasattr(prod, "get_filename"):
            return prod.get_filename()
        # or a get_data_filename method?
        elif hasattr(prod, "get_data_filename"):
            return prod.get_data_filename()

        # Check if the filename exists in the default location
        try:
            return prod.Data.DataStorage.DataContainer.FileName
        except AttributeError as _e:
            raise AttributeError("Data product does not have filename stored in the expected " +
                                 "location (self.Data.DataStorage.DataContainer.FileName. " +
                                 "In order to use get_data_filename with this product, the " +
                                 "product's class must be monkey-patched to have a get_filename " +
                                 "or get_data_filename method.")

    except (UnicodeDecodeError, SAXParseException, UnpicklingError) as _e:
        # Not an XML file - so presumably it's a raw data file; return the
        # input filename
        return filename


def update_xml_with_value(filename):
    r""" Updates xml files with value

    Checks for <Key><\Key> not followed by <Value><\Value>
    r"""

    lines = open(filename).readlines()
    key_lines = [ii for ii, line in enumerate(lines) if '<Key>' in line]
    bad_lines = [idx for idx in key_lines if '<Value>' not in lines[idx + 1]]
    if bad_lines:
        print("%s has incorrect parameter settings, missing <Value> in lines: %s"
              % (filename, ','.join(map(str, bad_lines))))
        # Do update
        for ii, idx in enumerate(bad_lines):
            # Check next 3 lines for String/Int etc Value

            info = [line for line in lines[idx + 1 + ii:min(idx + 4 + ii, len(lines) - 1)] if 'Value>' in line]
            new_line = None
            n_defaults = 0
            if info:
                data_value = info[0].split('Value>')[1].split('<')[0]
                if len(data_value) > 0:
                    new_line = lines[idx + ii].split('<Key>')[0] + '<Value>%s</Value>\n' % data_value

            if not new_line:
                # Add random string...
                new_line = lines[idx + ii].split('<Key>')[0] + '<Value>dkhf</Value>\n'
                n_defaults += 1
            lines = lines[:idx + ii + 1] + [new_line] + lines[idx + ii + 1:]
            open(filename, 'w').writelines(lines)
            print('Updated %s lines in %s: n_defaults=%s' %
                  (len(bad_lines), filename, n_defaults))
    else:
        print('No updates required')
