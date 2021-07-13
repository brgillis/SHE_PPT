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

__updated__ = "2021-07-13"

from datetime import datetime
import json
import os
from os.path import join, exists
from pickle import UnpicklingError
import pickle
import subprocess
from xml.sax._exceptions import SAXParseException

from EL_PythonUtils.utilities import time_to_timestamp
from astropy.io import fits
from pyxb.exceptions_ import NamespaceError

from ElementsServices.DataSync import DataSync
from ST_DM_FilenameProvider.FilenameProvider import FileNameProvider
from ST_DataModelBindings.sys_stub import CreateFromDocument
import numpy as np

from . import __version__ as SHE_PPT_version
from . import magic_values as mv
from .constants.test_data import SYNC_CONF
from .logging import getLogger
from .utility import get_release_from_version


logger = getLogger(mv.logger_name)

type_name_maxlen = 45
instance_id_maxlen = 55
processing_function_maxlen = 4


def get_allowed_filename(type_name, instance_id, extension=".fits", release=None, version=None, subdir="data",
                         processing_function="SHE", timestamp=True):
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

    # Silently shift instance_id to upper-case
    instance_id = instance_id.upper()

    # Check the extension doesn't start with "." and silently fix if it does
    if extension[0] == ".":
        extension = extension[1:]

    filename = FileNameProvider().get_allowed_filename(processing_function=processing_function,
                                                       type_name=type_name.upper(),
                                                       instance_id=instance_id,
                                                       extension=extension,
                                                       release=release,
                                                       timestamp=timestamp)

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
                tupled_list = [t[0] for t in tupled_list]
            return tupled_list
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


def write_xml_product(product, xml_filename, workdir=".", allow_pickled=False):

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
                                                version=SHE_PPT_version, subdir=None)
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
        if "object has no attribute 'toDOM'" not in str(e):
            raise
        logger.warning(
            "XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, qualified_xml_filename)


def read_xml_product(xml_filename, workdir=".", allow_pickled=False):

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    qualified_xml_filename = find_file(xml_filename, workdir)

    try:
        with open(str(qualified_xml_filename), "r") as f:
            xml_string = f.read()

        # Create a new product instance using the proper data product dictionary
        product = CreateFromDocument(xml_string)
    except (UnicodeDecodeError, SAXParseException):
        # Not actually saved as xml
        if allow_pickled:
            # Revert to pickled product
            return read_pickled_product(qualified_xml_filename)
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

        if exists(test_filename):
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


def _is_no_file(name):
    return name is None or name == "None" or name == "data/None" or name == "" or name == "data/"


def _find_web_file_xml(filename, qualified_filename):
    try:
        webpath = os.path.split(filename)[0]
        p = read_xml_product(qualified_filename, workdir="")
        for subfilename in p.get_all_filenames():
            # Skip if there's no file to download
            if _is_no_file(subfilename):
                continue
            find_web_file(os.path.join(webpath, subfilename))
    except NamespaceError as e:
        if "elementBinding" not in str(e):
            raise
        # MDB files end in XML but can't be read this way, and will raise this exception, so silently pass
    return webpath


def _find_web_file_json(filename, qualified_filename):
    webpath = os.path.split(filename)[0]
    l = read_listfile(qualified_filename)
    for element in l:
        if isinstance(element, str):
            # Skip if there's no file to download
            if _is_no_file(element):
                continue
            find_web_file(os.path.join(webpath, element))
        else:
            for subelement in element:
                # Skip if there's no file to download
                if _is_no_file(subelement):
                    continue
                find_web_file(os.path.join(webpath, subelement))


def find_web_file(filename):
    """
        Searches on WebDAV for a file. If found, downloads it and returns the qualified name of it. If
        it's an xml data product, will also download all associated files.

        If it isn't found, returns None.
    """

    filelist = os.path.join(os.getcwd(), os.path.splitext(os.path.split(filename)[-1])[0] + f"{os.getpid()}_list.txt")

    logger.debug("Writing filelist to %s", filelist)

    try:
        with open(filelist, 'w') as fo:
            fo.write(filename + "\n")

        sync = DataSync(SYNC_CONF, filelist)
        sync.download()

        qualified_filename = sync.absolutePath(filename)
    finally:
        if os.path.exists(filelist):
            logger.debug("Cleaning up %s", filelist)
            os.remove(filelist)

    # If it's an xml data product, we'll also need to download all files it points to
    if filename[-4:] == ".xml":

        _webpath = _find_web_file_xml(filename, qualified_filename)

    # If it's json listfile, we'll also need to download all files it points to
    elif filename[-5:] == ".json":

        _find_web_file_json(filename, qualified_filename)

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
    if filename[0:4] == "AUX/":
        return find_aux_file(filename[4:])
    if filename[0:5] == "CONF/":
        return find_conf_file(filename[5:])
    if filename[0:5] == "HOME/":
        path = os.path.join(os.getenv('HOME'), os.path.dirname(filename[5:]))
        return find_file_in_path(os.path.basename(filename), path)
    if filename[0] == "/":
        if not os.path.exists(filename):
            raise RuntimeError("File " + filename + " cannot be found.")
        return filename
    if path is not None:
        return find_file_in_path(filename, path)
    raise ValueError("path must be supplied if filename doesn't start with AUX/ or CONF/")


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
        if hasattr(prod, "get_data_filename"):
            return prod.get_data_filename()

        # Check if the filename exists in the default location
        try:
            return prod.Data.DataStorage.DataContainer.FileName
        except AttributeError:
            raise AttributeError("Data product does not have filename stored in the expected " +
                                 "location (self.Data.DataStorage.DataContainer.FileName. " +
                                 "In order to use get_data_filename with this product, the " +
                                 "product's class must be monkey-patched to have a get_filename " +
                                 "or get_data_filename method.")

    except (UnicodeDecodeError, SAXParseException, UnpicklingError):
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
        logger.warning("%s has incorrect parameter settings, missing <Value> in lines: %s",
                       filename,
                       ','.join(map(str, bad_lines)))
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
            logger.info('Updated %s lines in %s: n_defaults=%s',
                        len(bad_lines),
                        filename,
                        n_defaults)
    else:
        logger.debug('No updates required')


def filename_exists(filename):
    """Quick function to check the filename isn't one of many strings indicating the file doesn't exist.
    """
    return filename not in (None, "None", "data/None", "", "data/")


def remove_files(l_qualified_filenames):
    """ Loop through and try to remove all files in a list. No exception is raised if the files can't be removed,
        but a warning is logged.
    """
    for qualified_filename in l_qualified_filenames:
        try:
            os.remove(qualified_filename)
        except Exception:
            # Don't need to fail the whole process, but log the issue
            logger.warning(f"Cannot delete file: {qualified_filename}")


def tar_files(qualified_tarball_filename, l_qualified_filenames, delete_files=False):

    qualified_filename_string = " ".join(l_qualified_filenames)

    # Tar the files and fully log the process
    logger.info(f"Creating tarball {qualified_tarball_filename}.")

    tar_cmd = f"tar -cf {qualified_tarball_filename} {qualified_filename_string}"
    tar_results = subprocess.run(tar_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    logger.info(f"tar stdout: {tar_results.stdout}")
    logger.debug("tar stderr: %s", tar_results.stderr)

    # Check that the tar process succeeded
    if not os.path.isfile(qualified_tarball_filename):
        raise FileNotFoundError(f"{qualified_tarball_filename} not found. stderr from tar process was: \n"
                                f"{tar_results.stderr}")
    if tar_results.returncode:
        raise ValueError(f"Tarring of {qualified_tarball_filename} failed. stderr from tar process was: \n"
                         f"{tar_results.stderr}")

    # Delete the files if desired
    if delete_files:
        remove_files(l_qualified_filenames)
