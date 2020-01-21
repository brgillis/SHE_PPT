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

__updated__ = "2020-01-21"

from datetime import datetime
import json
import os
from os.path import join, isfile
from pickle import UnpicklingError
import pickle
from xml.sax._exceptions import SAXParseException

from ElementsServices.DataSync import downloadTestData, localTestFile
from EuclidDmBindings.sys_stub import CreateFromDocument
from FilenameProvider.FilenameProvider import createFilename
from SHE_PPT import magic_values as mv
import SHE_PPT
from SHE_PPT.logging import getLogger
from SHE_PPT.utility import run_only_once, get_release_from_version, time_to_timestamp
from astropy.io import fits
import numpy as np
import py


logger = getLogger(mv.logger_name)

type_name_maxlen = 45
instance_id_maxlen = 55
processing_function_maxlen = 4

filename_include_data_subdir = False
data_subdir = "data/"
len_data_subdir = len(data_subdir)


@run_only_once
def warn_deprecated_timestamp():
    logger.warning(
        "The use of the 'timestamp' kwarg in get_allowed_filename is deprecated and will be removed in a future version.")


def get_allowed_filename(type_name, instance_id, extension=".fits", release=None, version=None, subdir="data",
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
        Software/data release version, in format "XX.XX" where each X is a digit 0-9. Either this or version must be
        supplied.
    version : str
        Software/data release version, in format "X.X(.Y)" where each X is an integer 0-99. Either this or release must
        be supplied.
    subdir : str
        Subdirectory of work directory in which this file will be (default "data")
    processing_function : str
        Label for the processing function which created this file.
    timestamp : bool
        If True, will append a timestamp to the instance_id
    """

    # Check we have just one of release and version
    if (release is None) == (version is None):
        raise ValueError("Exactly one of release or version must be supplied to get_allowed_filename.")

    # If given version, convert it to release format
    if version is not None:
        release = get_release_from_version(version)

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
            tupled_list = [tuple(el) for el in listobject]
            if np.all([len(t) == 1 for t in tupled_list]):
                return [t[0] for t in tupled_list]
            else:
                return tupled_list
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


def write_xml_product(product, xml_filename, workdir=".", allow_pickled=True):

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    # Check if the product has a ProductId, and set it if necessary
    try:
        if product.Header.ProductId == "None":
            # Set the product ID to a timestamp
            t = datetime.now()
            product.Header.ProductId = time_to_timestamp(t)
    except AttributeError as e:
        pass

    # Check if the product has a catalog file object, and set the name and write a dummy one if necessary
    try:
        cat_filename = product.Data.CatalogStorage.CatalogFileStorage.StorageSpace[0].DataContainer.FileName
        if cat_filename == "None":
            # Create a name for the catalog file
            cat_filename = get_allowed_filename(type_name="CAT", instance_id="0", extension=".csv",
                                                version=SHE_PPT.__version__, subdir=None)
            product.Data.CatalogStorage.CatalogFileStorage.StorageSpace[0].DataContainer.FileName = cat_filename

        # Check if the catalogue exists, and create it if necessary

        datadir = os.path.join(workdir, "data/")
        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        qualified_cat_filename = os.path.join(workdir, "data/" + cat_filename)
        if not os.path.isfile(qualified_cat_filename):
            open(qualified_cat_filename, 'a').close()

    except AttributeError as e:
        pass

    if xml_filename[0] == "/":
        qualified_xml_filename = xml_filename
    else:
        qualified_xml_filename = os.path.join(workdir, xml_filename)

    try:
        with open(str(qualified_xml_filename), "w") as f:
            f.write(product.toDOM().toprettyxml(encoding="utf-8").decode("utf-8"))
    except AttributeError as e:
        if not allow_pickled:
            raise
        if not "object has no attribute 'toDOM'" in str(e):
            raise
        logger.warning(
            "XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, qualified_xml_filename)


def read_xml_product(xml_filename, workdir=".", allow_pickled=True):

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    qualified_xml_filename = find_file(xml_filename, workdir)

    try:
        with open(str(qualified_xml_filename), "r") as f:
            xml_string = f.read()

        # Create a new product instance using the proper data product dictionary
        product = CreateFromDocument(xml_string)
    except (UnicodeDecodeError, SAXParseException) as _e:
        # Not actually saved as xml
        if allow_pickled:
            # Revert to pickled product
            return read_pickled_product(qualified_xml_filename)
        else:
            raise

    return product


def write_pickled_product(product, pickled_filename, workdir="."):

    # Silently coerce input into a string
    pickled_filename = str(pickled_filename)

    if pickled_filename[0] == "/":
        qualified_pickled_filename = pickled_filename
    else:
        qualified_pickled_filename = os.path.join(workdir, pickled_filename)

    with open(str(qualified_pickled_filename), "wb") as f:
        pickle.dump(product, f)


def read_pickled_product(pickled_filename, workdir="."):

    # Silently coerce input into a string
    pickled_filename = str(pickled_filename)

    qualified_pickled_filename = find_file(pickled_filename, workdir)

    with open(str(qualified_pickled_filename), "rb") as f:
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

    # Silently coerce input into a string
    filename = str(filename)

    if filename[0:4] == "WEB/":
        return find_web_file(filename[4:])
    elif filename[0:4] == "AUX/":
        return find_aux_file(filename[4:])
    elif filename[0:5] == "CONF/":
        return find_conf_file(filename[5:])
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


def get_data_filename_from_product(p, attr_name=None):
    """ Helper function to get a data filename from a product, adjusting for whether to include the data subdir as desired.
    """

    if attr_name is None or attr_name == 0:
        data_filename = p.Data.DataContainer.FileName
    elif attr_name == -1:
        data_filename = p.Data.FileName
    else:
        data_filename = getattr(p.Data, attr_name).DataContainer.FileName

    if data_filename is None:
        return None

    # Silently force the filename returned to start with "data/" regardless of
    # whether the returned value does, unless it's absolute
    if len(data_filename) > 0 and (data_filename[0:len_data_subdir] == data_subdir or data_filename[0] == "/"):
        return data_filename
    else:
        return data_subdir + data_filename


def set_data_filename_of_product(p, data_filename, attr_name=None):
    """ Helper function to set a data filename of a product, adjusting for whether to include the data subdir as desired.
    """

    if data_filename is not None and len(data_filename) > 0 and data_filename[0] != "/":
        if filename_include_data_subdir:

                # Silently force the filename returned to start with "data/" regardless of
                # whether the returned value does
            if data_filename[0:len_data_subdir] != data_subdir:
                data_filename = data_subdir + data_filename

        else:

            # Silently force the filename returned to NOT start with "data/"
            # regardless of whether the returned value does
            if data_filename[0:len_data_subdir] == data_subdir:
                data_filename = data_filename.replace(data_subdir, "", 1)

    if attr_name is None or attr_name == 0:
        p.Data.DataContainer.FileName = data_filename
    elif attr_name == -1:
        p.Data.FileName = data_filename
    else:
        getattr(p.Data, attr_name).DataContainer.FileName = data_filename

    return
