""" @file file_io.py

    Created 29 Aug 2017

    Various functions for input/output
"""

__updated__ = "2021-08-31"

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

import abc
import json
import os
import pickle
import subprocess
from datetime import datetime
from os.path import exists, join
from typing import Any, Callable, Dict, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, Union
from xml.sax import SAXParseException

import numpy as np
from astropy.io import fits
from astropy.io.fits import HDUList
from astropy.io.fits.hdu.base import ExtensionHDU
from astropy.table import Table
from pyxb.exceptions_ import NamespaceError

import SHE_PPT
from EL_PythonUtils.utilities import time_to_timestamp
from ElementsServices.DataSync import DataSync
from ST_DM_FilenameProvider.FilenameProvider import FileNameProvider
from ST_DataModelBindings.sys_stub import CreateFromDocument
from . import __version__
from .constants.classes import ShearEstimationMethods
from .constants.test_data import SYNC_CONF
from .logging import getLogger
from .utility import get_release_from_version, is_any_type_of_none, join_without_none

# CONSTANT strings for default values in filenames
DEFAULT_TYPE_NAME = "UNKNOWN-FILE-TYPE"
DEFAULT_INSTANCE_ID = "0"
DEFAULT_FILE_EXTENSION = ".fits"
DEFAULT_FILE_SUBDIR = "data"
DEFAULT_FILE_PF = "SHE"

# Constant strings for replacement tags
STR_R_FILETYPE = "$FILETYPE"
STR_R_OPERATION = "$OPERATION"

# Constant strings for descriptions of file types
STR_DATA_PRODUCT = "data product"
STR_TABLE = "table"
STR_FITS_FILE = "FITS file"

# Constant strings for access operations
STR_READING = "reading"
STR_WRITING = "writing"
STR_OPENING = "opening"

# Constant strings for messages
BASE_MESSAGE_ACCESSING = f"{STR_R_OPERATION} {STR_R_FILETYPE} from %s in workdir %s"
BASE_MESSAGE_FINISHED_ACCESSING = f"Finished {BASE_MESSAGE_ACCESSING} successfully"

BASE_MESSAGE_READING = BASE_MESSAGE_ACCESSING.replace(STR_R_OPERATION, STR_READING)
BASE_MESSAGE_FINISHED_READING = BASE_MESSAGE_FINISHED_ACCESSING.replace(STR_R_OPERATION, STR_READING)

BASE_MESSAGE_WRITING = BASE_MESSAGE_ACCESSING.replace(STR_R_OPERATION, STR_WRITING)
BASE_MESSAGE_FINISHED_WRITING = BASE_MESSAGE_FINISHED_ACCESSING.replace(STR_R_OPERATION, STR_WRITING)

BASE_MESSAGE_OPENING = BASE_MESSAGE_ACCESSING.replace(STR_R_OPERATION, STR_OPENING)
BASE_MESSAGE_FINISHED_OPENING = BASE_MESSAGE_FINISHED_ACCESSING.replace(STR_R_OPERATION, STR_OPENING)

MSG_READING_DATA_PRODUCT = (BASE_MESSAGE_READING.replace(STR_R_FILETYPE, STR_DATA_PRODUCT)).capitalize()
MSG_FINISHED_READING_DATA_PRODUCT = (BASE_MESSAGE_FINISHED_READING.replace(STR_R_FILETYPE,
                                                                           STR_DATA_PRODUCT)).capitalize()

DATA_SUBDIR = "data/"

# Constants for strings in xml files

STR_KEY = '<Key>'
STR_VALUE = '<Value>'

# Get some constant values from the FileNameProvider

filename_provider = FileNameProvider()

type_name_maxlen = filename_provider.type_name_maxlen
max_timestamp_release_len = 30
instance_id_maxlen = filename_provider.instance_id_maxlen - max_timestamp_release_len
processing_function_maxlen = filename_provider.processing_function_maxlen
filename_forbidden_chars = filename_provider.filename_forbidden_chars

logger = getLogger(__name__)


def _get_optional_log_method(log_info: bool) -> Callable[..., None]:
    """ Get the desired logging method. If log_info==True, will log at info level, otherwise at debug level.
    """
    if log_info:
        log_method = logger.info
    else:
        log_method = logger.debug

    return log_method


# Classes for custom exceptions


class SheFileAccessError(IOError):
    filename: Optional[str] = None
    qualified_filename: str
    workdir: Optional[str] = None
    operation: str = "accessing"

    def __init__(self,
                 qualified_filename: Optional[str] = None,
                 filename: Optional[str] = None,
                 workdir: Optional[str] = None,
                 ):

        if qualified_filename is not None:
            self.qualified_filename = qualified_filename
        elif (filename is not None) and (workdir is not None):
            self.qualified_filename = os.path.join(workdir, filename)
            self.filename = filename
            self.workdir = workdir
        else:
            raise ValueError("Cannot construct SheFileAccessError without either qualified_filename argument or both " +
                             "filename and workdir arguments. Arguments were: "
                             f"qualified_filename = {qualified_filename}, "
                             f"filename = {filename}, "
                             f"workdir = {workdir}, ")

        super().__init__(self.get_message())

    def get_message(self):
        return f"Error {self.operation} file {self.qualified_filename}."


class SheFileReadError(SheFileAccessError):
    operation: str = STR_READING


class SheFileWriteError(SheFileAccessError):
    operation: str = STR_WRITING


class SheFileNamer(FileNameProvider):
    """ Class to handle generating Euclid-compliant filenames piecewise from components.
    """

    # Attributes used to generate the filename - can be set at init or otherwise before calling get()

    # For type name
    _type_name_head: Optional[str] = None
    _type_name_body: Optional[str] = None
    _type_name_tail: Optional[str] = None

    _type_name: Optional[str] = None

    default_type_name: str = "FILE"

    # For instance ID
    _instance_id_head: Optional[str] = None
    _instance_id_body: Optional[str] = None
    _instance_id_tail: Optional[str] = None

    _instance_id: Optional[str] = None

    default_instance_id: str = "0"

    # Options for getting the filename
    _extension: str = DEFAULT_FILE_EXTENSION
    _release: Optional[str] = None
    _version: Optional[str] = None
    _subdir: Optional[str] = DEFAULT_FILE_SUBDIR
    _processing_function: str = DEFAULT_FILE_PF
    _timestamp: bool = True

    # Other options
    _workdir: Optional[str] = None

    # Output values
    _filename: Optional[str] = None
    _qualified_filename: Optional[str] = None

    def __init__(self,
                 type_name: Optional[str] = None,
                 instance_id: Optional[str] = None,
                 extension: Optional[str] = None,
                 release: Optional[str] = None,
                 version: Optional[str] = None,
                 subdir: Optional[str] = None,
                 processing_function: Optional[str] = None,
                 timestamp: Optional[bool] = None,
                 workdir: Optional[str] = None):

        super().__init__()

        # Override defaults with any options provided at init

        if type_name is not None:
            self._type_name_body = type_name

        if instance_id is not None:
            self._instance_id_body = instance_id

        if extension is not None:
            self._extension = extension

        if release is not None:
            self._release = release

        if version is not None:
            self._version = version

        if subdir is not None:
            self._subdir = subdir

        if processing_function is not None:
            self._processing_function = processing_function

        if timestamp is not None:
            self._timestamp = timestamp

        if workdir is not None:
            self._workdir = workdir

    # Attribute accessors and setters

    @property
    def type_name_head(self) -> str:
        return self._type_name_head

    @type_name_head.setter
    def type_name_head(self, type_name_head: Optional[str]) -> None:
        self._type_name_head = type_name_head
        self.type_name = None

    @property
    def type_name_body(self) -> str:
        if self._type_name_body is None:
            self._determine_type_name_body()
        return self._type_name_body

    @type_name_body.setter
    def type_name_body(self, type_name_body: Optional[str]) -> None:
        self._type_name_body = type_name_body
        self.type_name = None

    @property
    def type_name_tail(self) -> str:
        return self._type_name_tail

    @type_name_tail.setter
    def type_name_tail(self, type_name_tail: Optional[str]) -> None:
        self._type_name_tail = type_name_tail
        self.type_name = None

    @property
    def instance_id_head(self) -> str:
        return self._instance_id_head

    @instance_id_head.setter
    def instance_id_head(self, instance_id_head: Optional[str]) -> None:
        self._instance_id_head = instance_id_head
        self.instance_id = None

    @property
    def instance_id_body(self) -> str:
        if self._instance_id_body is None:
            self._determine_instance_id_body()
        return self._instance_id_body

    @instance_id_body.setter
    def instance_id_body(self, instance_id_body: Optional[str]) -> None:
        self._instance_id_body = instance_id_body
        self.instance_id = None

    @property
    def instance_id_tail(self) -> str:
        return self._instance_id_tail

    @instance_id_tail.setter
    def instance_id_tail(self, instance_id_tail: Optional[str]) -> None:
        self._instance_id_tail = instance_id_tail
        self.instance_id = None

    @property
    def extension(self) -> str:
        return self._extension

    @extension.setter
    def extension(self, extension: Optional[str]) -> None:
        self._extension = extension
        self.filename = None

    @property
    def release(self) -> str:
        return self._release

    @release.setter
    def release(self, release: Optional[str]) -> None:
        self._release = release
        self.filename = None

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, version: Optional[str]) -> None:
        self._version = version
        self.filename = None

    @property
    def subdir(self) -> str:
        return self._subdir

    @subdir.setter
    def subdir(self, subdir: Optional[str]) -> None:
        self._subdir = subdir
        self.filename = None

    @property
    def processing_function(self) -> str:
        return self._processing_function

    @processing_function.setter
    def processing_function(self, processing_function: Optional[str]) -> None:
        self._processing_function = processing_function
        self.filename = None

    @property
    def timestamp(self) -> bool:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: bool) -> None:
        self._timestamp = timestamp
        self.filename = None

    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: Optional[str]) -> None:
        self._workdir = workdir
        self.qualified_filename = None

    @property
    def type_name(self) -> str:
        if self._type_name is None:
            self.__determine_type_name()
        return self._type_name

    @type_name.setter
    def type_name(self, type_name: Optional[str]) -> None:
        self._type_name = type_name
        self.filename = None

    @property
    def instance_id(self) -> str:
        if self._instance_id is None:
            self.__determine_instance_id()
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id: Optional[str]) -> None:
        self._instance_id = instance_id
        self.filename = None

    @property
    def filename(self) -> str:
        if self._filename is None:
            self._filename = self.get()
        return self._filename

    @filename.setter
    def filename(self, filename: Optional[str]) -> None:
        self._filename = filename
        self.qualified_filename = None

    @property
    def qualified_filename(self) -> str:
        if self._qualified_filename is None:
            self._qualified_filename = get_qualified_filename(self.filename, self.workdir)
        return self._qualified_filename

    @qualified_filename.setter
    def qualified_filename(self, qualified_filename: Optional[str]) -> None:
        self._qualified_filename = qualified_filename

    # Private methods

    def __determine_type_name(self):
        # Piece together the type ID from the components, leaving out Nones
        self._type_name = join_without_none(l_s = [self.type_name_head,
                                                   self.type_name_body,
                                                   self.type_name_tail],
                                            default = self.default_type_name)

    def __determine_instance_id(self):
        # Piece together the instance ID from the components, leaving out Nones
        self._instance_id = join_without_none(l_s = [self.instance_id_head,
                                                     self.instance_id_body,
                                                     self.instance_id_tail],
                                              default = self.default_instance_id)

    # Protected methods

    def _determine_type_name_body(self):
        raise TypeError("_determine_type_name_body must be overriden if type_name "
                        "is not passed to init of SheFileNamer.")

    def _determine_instance_id_body(self):
        raise TypeError("_determine_instance_id_body must be overriden if instance_id "
                        "is not passed to init of SheFileNamer.")

    # Public methods

    def get(self):
        """ Get a filename based on internal attributes.
        """
        # Check we have just one of release and version
        if (self.release is None) == (self.version is None):
            raise ValueError("Exactly one of release or version must be supplied to get_allowed_filename.")

        # If given version, convert it to release format
        if self.version is not None:
            release = get_release_from_version(self.version)
        else:
            release = self.release

        # Check the extension doesn't start with "." and silently fix if it does
        if self.extension[0] == ".":
            extension = self.extension[1:]
        else:
            extension = self.extension

        filename = self.get_allowed_filename(processing_function = self.processing_function,
                                             type_name = self.type_name.upper(),
                                             instance_id = self.instance_id.upper(),
                                             extension = extension,
                                             release = release,
                                             timestamp = self.timestamp)

        if self.subdir is not None:
            qualified_filename = join(self.subdir, filename)
        else:
            qualified_filename = filename

        return qualified_filename


def get_qualified_filename(filename: str, workdir: str = ".") -> str:
    """ Gets a fully-qualified filename, checking if the first argument is already fully-qualified first.
    """
    if filename[0] == "/":
        qualified_xml_filename = filename
    else:
        qualified_xml_filename = os.path.join(workdir, filename)
    return qualified_xml_filename


def get_allowed_filename(type_name: str = DEFAULT_TYPE_NAME,
                         instance_id: str = DEFAULT_INSTANCE_ID,
                         extension: str = ".fits",
                         release: Optional[str] = None,
                         version: Optional[str] = None,
                         subdir: Optional[str] = "data",
                         processing_function: str = "SHE",
                         timestamp: bool = True) -> str:
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

    return SheFileNamer(type_name = type_name,
                        instance_id = instance_id,
                        extension = extension,
                        release = release,
                        version = version,
                        subdir = subdir,
                        processing_function = processing_function,
                        timestamp = timestamp).get()


def write_listfile(listfile_name: str,
                   filenames: Sequence[str],
                   log_info: bool = False) -> None:
    """
        @brief Writes a listfile in json format.

        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files

        @param listfile_name <str> Name of the listfile to be output.

        @param filenames <list<str>> List of filenames (or tuples of filenames) to be put in the listfile.

        @param log_info <bool> If True, will log at info level, otherwise will log at debug level.
    """

    log_method = _get_optional_log_method(log_info)
    log_method("Writing listfile to %s", listfile_name)

    try:
        with open(listfile_name, 'w') as listfile:
            paths_json = json.dumps(filenames)
            listfile.write(paths_json)
    except Exception as e:
        raise SheFileWriteError(listfile_name) from e

    logger.debug("Finished writing listfile to %s", listfile_name)


def read_listfile(listfile_name: str,
                  log_info: bool = False) -> List[Union[str, Tuple[str]]]:
    """
        @brief Reads a json listfile and returns a list of filenames.

        @details This is copied from https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files

        @param listfile_name <str> Name of the listfile to be read.

        @param log_info <bool> If True, will log at info level, otherwise will log at debug level.

        @return filenames <list<str>> List of filenames (or tuples of filenames) read in.
    """

    log_method = _get_optional_log_method(log_info)
    log_method("Reading listfile from %s", listfile_name)

    try:
        with open(listfile_name, 'r') as f:
            list_object = json.load(f)
            if len(list_object) == 0:
                return list_object
            if isinstance(list_object[0], list):
                tupled_list = [tuple(el) for el in list_object]
                if np.all([len(t) == 1 for t in tupled_list]):
                    tupled_list = [t[0] for t in tupled_list]
                return tupled_list
    except Exception as e:
        raise SheFileReadError(listfile_name) from e

    log_method("Reading listfile from %s", listfile_name)

    return list_object


def replace_in_file(input_filename: str, output_filename: str, input_string: str, output_string: str) -> None:
    """
        @brief Replaces every occurence of $input_string in $input_filename with $output_string
               and prints the results to $output_filename.

        @param input_filename <string>

        @param output_filename <string>

        @param input_string <string>

        @param output_string <string>
    """

    with open(output_filename, "w") as f_out:
        with open(input_filename, "r") as f_in:
            for line in f_in:
                f_out.write(line.replace(input_string, output_string))


def replace_multiple_in_file(input_filename: str,
                             output_filename: str,
                             input_strings: Sequence[str],
                             output_strings: Sequence[str]) -> None:
    """she_dpd
        @brief Replaces every occurence of an input_string in input_filename with the corresponding
               output string and prints the results to $output_filename.

        @param input_filename <string>

        @param output_filename <string>

        @param input_strings <iterable of string>

        @param output_strings <iterable of string>
    """

    with open(output_filename, "w") as f_out:
        with open(input_filename, "r") as f_in:
            for line in f_in:
                new_line = line
                for input_string, output_string in zip(input_strings, output_strings):
                    new_line = new_line.replace(input_string, output_string)
                f_out.write(new_line)


def write_xml_product(product: Any,
                      xml_filename: str,
                      workdir: str = ".",
                      log_info: bool = False,
                      allow_pickled: bool = False) -> None:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_WRITING, STR_DATA_PRODUCT, xml_filename, workdir)

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    try:
        _write_xml_product(product, xml_filename, workdir, allow_pickled)
    except Exception as e:
        raise SheFileWriteError(filename = xml_filename, workdir = workdir) from e

    logger.debug(BASE_MESSAGE_FINISHED_WRITING, STR_DATA_PRODUCT, xml_filename, workdir)


def _write_xml_product(product: Any, xml_filename: str, workdir: str, allow_pickled: bool) -> None:
    # Check if the product has a ProductId, and set it if necessary
    try:
        if product.Header.ProductId == "None":
            # Set the product ID to a timestamp
            t = datetime.now()
            product.Header.ProductId = time_to_timestamp(t)
    except AttributeError:
        pass

    # Check if the product has a catalog file object, and set the name and write a dummy one if necessary
    try:
        cat_filename = product.Data.CatalogStorage.CatalogFileStorage.StorageSpace[0].DataContainer.FileName
        if cat_filename == "None":
            # Create a name for the catalog file
            cat_filename = get_allowed_filename(type_name = "CAT", instance_id = "0", extension = ".csv",
                                                version = __version__, subdir = None)
            product.Data.CatalogStorage.CatalogFileStorage.StorageSpace[0].DataContainer.FileName = cat_filename

        # Check if the catalogue exists, and create it if necessary

        datadir = os.path.join(workdir, DATA_SUBDIR)
        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        qualified_cat_filename = os.path.join(workdir, DATA_SUBDIR + cat_filename)
        if not os.path.isfile(qualified_cat_filename):
            open(qualified_cat_filename, 'a').close()

    except AttributeError:
        pass

    qualified_xml_filename = get_qualified_filename(xml_filename, workdir)

    try:
        with open(str(qualified_xml_filename), "w") as f:
            f.write(product.toDOM().toprettyxml(encoding = "utf-8").decode("utf-8"))
    except AttributeError as e:
        if not allow_pickled:
            raise
        if "object has no attribute 'toDOM'" not in str(e):
            raise
        logger.warning(
            "XML writing is not available; falling back to pickled writing instead.")
        write_pickled_product(product, qualified_xml_filename)


def read_xml_product(xml_filename: str,
                     workdir: str = ".",
                     log_info: bool = False,
                     allow_pickled: bool = False,
                     product_type: Optional[Type] = None) -> Any:
    """ Reads in an XML data product. If product_type is set to a type of a data product, will check that the product
        read in is of that type.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_DATA_PRODUCT, xml_filename, workdir)

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    try:

        product = _read_xml_product(xml_filename, workdir, allow_pickled)

    except NamespaceError:
        # If we hit a namespace error, it likely means the SHE_PPT.products module hasn't been imported.
        # Try importing it and reading again
        from . import products

        try:
            product = _read_xml_product(xml_filename, workdir, allow_pickled)
        except Exception as e:
            raise SheFileReadError(filename = xml_filename, workdir = workdir) from e

    except Exception as e:
        raise SheFileReadError(filename = xml_filename, workdir = workdir) from e

    # Check the type of the read-in product if product_type is not None
    if (product_type is not None) and not isinstance(product, product_type):
        raise TypeError(f"Product read in from file {xml_filename} in directory {workdir} is of type "
                        f"{type(product)}, but type {product_type} was expected.")

    logger.debug(MSG_FINISHED_READING_DATA_PRODUCT, xml_filename, workdir)

    return product


def _read_xml_product(xml_filename: str, workdir: str, allow_pickled: bool) -> Any:
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
            product = read_pickled_product(qualified_xml_filename)
        else:
            raise

    return product


def write_pickled_product(product,
                          pickled_filename: str,
                          workdir: str = ".",
                          log_info: bool = False) -> None:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_WRITING, STR_DATA_PRODUCT, pickled_filename, workdir)

    # Silently coerce input into a string
    pickled_filename = str(pickled_filename)

    qualified_pickled_filename = get_qualified_filename(pickled_filename, workdir)

    try:
        with open(str(qualified_pickled_filename), "wb") as f:
            pickle.dump(product, f)
    except Exception as e:
        raise SheFileWriteError(filename = pickled_filename, workdir = workdir) from e

    logger.debug(BASE_MESSAGE_FINISHED_WRITING, STR_DATA_PRODUCT, pickled_filename, workdir)


def read_pickled_product(pickled_filename,
                         workdir = ".",
                         log_info: bool = False) -> Any:
    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_DATA_PRODUCT, pickled_filename, workdir)

    # Silently coerce input into a string
    pickled_filename = str(pickled_filename)

    qualified_pickled_filename = find_file(pickled_filename, workdir)

    try:
        with open(str(qualified_pickled_filename), "rb") as f:
            product = pickle.load(f)
    except Exception as e:
        raise SheFileReadError(filename = pickled_filename, workdir = workdir) from e

    logger.debug(MSG_FINISHED_READING_DATA_PRODUCT, pickled_filename, workdir)

    return product


def write_table(t: Table,
                filename: str,
                workdir: str = ".",
                log_info: bool = False,
                *args, **kwargs) -> None:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_WRITING, STR_TABLE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        t.write(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileWriteError(filename = filename, workdir = workdir) from e

    logger.debug(BASE_MESSAGE_FINISHED_WRITING, STR_TABLE, filename, workdir)


def read_table(filename: str,
               workdir: str = ".",
               log_info: bool = False,
               *args, **kwargs) -> Table:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_READING, STR_TABLE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        t: Table = Table.read(qualified_filename, format = "fits", *args, **kwargs)
    except Exception as e:
        raise SheFileReadError(filename = filename, workdir = workdir) from e

    logger.debug(BASE_MESSAGE_FINISHED_READING, STR_TABLE, filename, workdir)
    return t


def write_product_and_table(product: Any,
                            product_filename: str,
                            table: Table,
                            *args: Any,
                            table_filename: Optional[str] = None,
                            workdir: str = ".",
                            log_info: bool = False,
                            **kwargs: Any):
    """ Convenience function to write a product and table at the same time, setting up a filename for the table if
        one is not provided, and setting the product to point to the table's filename with its set_data_filename
        method.
    """

    # Generate a filename for the table if one hasn't been provided
    if table_filename is None:
        table_file_namer = SheFileNamer(type_name = DEFAULT_TYPE_NAME,
                                        instance_id = DEFAULT_INSTANCE_ID,
                                        workdir = workdir,
                                        version = SHE_PPT.__version__)
        table_filename = table_file_namer.filename

    # Write the table
    write_table(table, *args, filename = table_filename, workdir = workdir, log_info = log_info, **kwargs)

    # Set the table filename within the product
    product.set_data_filename(table_filename)

    # Write the product
    write_xml_product(product, xml_filename = product_filename, workdir = workdir, log_info = log_info)


def read_product_and_table(product_filename: str,
                           workdir: str = ".",
                           log_info: bool = False,
                           product_type: Optional[Type] = None,
                           *args, **kwargs) -> Tuple[Any, Table]:
    """ Convenience function to read in a data product and the data table it points to, and return both as a tuple.
    """

    p = read_xml_product(product_filename, workdir = workdir, log_info = log_info, product_type = product_type)
    table_filename: str = p.get_data_filename()

    t = read_table(table_filename, workdir = workdir, log_info = log_info, *args, **kwargs)

    return p, t


def read_table_from_product(product_filename: str,
                            workdir: str = ".",
                            log_info: bool = False,
                            product_type: Optional[Type] = None,
                            *args, **kwargs) -> Table:
    """ Convenience function to read a data table given the filename of the xml data product which points to it.
    """

    _, t = read_product_and_table(product_filename = product_filename,
                                  workdir = workdir,
                                  log_info = log_info,
                                  product_type = product_type,
                                  *args, *kwargs)

    return t


def write_fits(hdu_list: HDUList,
               filename: str,
               workdir: str = ".",
               log_info: bool = False,
               *args, **kwargs) -> None:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_WRITING, STR_FITS_FILE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        hdu_list.writeto(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileWriteError(filename = filename, workdir = workdir) from e
    logger.debug(BASE_MESSAGE_FINISHED_WRITING, STR_FITS_FILE, filename, workdir)


def read_fits(filename: str,
              workdir: str = ".",
              log_info: bool = False,
              *args, **kwargs) -> HDUList:
    log_method = _get_optional_log_method(log_info)
    log_method(BASE_MESSAGE_OPENING, STR_FITS_FILE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        f: HDUList = fits.open(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileReadError(filename = filename, workdir = workdir) from e
    logger.debug(BASE_MESSAGE_FINISHED_OPENING, STR_FITS_FILE, filename, workdir)

    return f


def read_d_l_method_table_filenames(l_product_filenames: List[str],
                                    workdir: str,
                                    log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, List[str]],
                                                                     List[Any]]:
    """ Read in a dict of lists of table filenames for each shear estimation method from a list of measurements product
        filenames.
    """

    # Init lists of filenames for each method
    d_method_l_table_filenames: Dict[ShearEstimationMethods, List[str]] = {}
    for method in ShearEstimationMethods:
        d_method_l_table_filenames[method] = []

    # Read in the table filenames from each product, for each method
    l_products: List[Any] = []
    for product_filename in l_product_filenames:

        qualified_product_filename: str = get_qualified_filename(product_filename,
                                                                 workdir = workdir)

        product = read_xml_product(qualified_product_filename,
                                   log_info = log_info)
        l_products.append(product)

        # Get the list of table filenames for each method and store it if it exists
        for method in ShearEstimationMethods:
            method_matched_catalog_filename = product.get_method_filename(method)
            if not is_any_type_of_none(method_matched_catalog_filename):
                d_method_l_table_filenames[method].append(method_matched_catalog_filename)

    return d_method_l_table_filenames, l_products


def read_d_l_method_tables(l_product_filenames: List[str],
                           workdir: str,
                           log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, List[Table]],
                                                            List[Any]]:
    """ Read in a dict of lists of tables for each shear estimation method from a list of measurements product
        filenames.
    """

    # Use the read_d_l_method_table_filenames function for reading, to share common code
    (d_l_method_table_filenames,
     l_products) = read_d_l_method_table_filenames(l_product_filenames = l_product_filenames,
                                                   workdir = workdir,
                                                   log_info = log_info)

    # Load each table into a new dict
    d_l_method_tables: Dict[ShearEstimationMethods, List[Table]] = {}

    for method in ShearEstimationMethods:
        d_l_method_tables[method] = []
        for filename in d_l_method_table_filenames[method]:
            d_l_method_tables[method].append(read_table(filename = filename,
                                                        workdir = workdir,
                                                        log_info = log_info))

    return d_l_method_tables, l_products


def read_d_method_table_filenames(product_filename: str,
                                  workdir: str,
                                  log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, str],
                                                                   Any]:
    """ Read in a dict of table filenames for each shear estimation method from a measurements product
        filename.
    """

    # Use the read_d_l_method_table_filenames function for reading, to share common code
    (d_l_method_table_filenames,
     l_products) = read_d_l_method_table_filenames(l_product_filenames = [product_filename],
                                                   workdir = workdir,
                                                   log_info = log_info)

    # Turn each list into a scalar, in a new dict
    d_method_table_filenames: Dict[ShearEstimationMethods, str] = {}

    for method in ShearEstimationMethods:
        d_method_table_filenames[method] = d_l_method_table_filenames[method][0]

    product = l_products[0]

    return d_method_table_filenames, product


def read_d_method_tables(product_filename: str,
                         workdir: str,
                         log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, Table],
                                                          Any]:
    """ Read in a dict of tables for each shear estimation method from a measurements product
        filename.
    """

    # Use the read_d_l_method_table_filenames function for reading, to share common code
    (d_l_method_table_filenames,
     l_products) = read_d_l_method_table_filenames(l_product_filenames = [product_filename],
                                                   workdir = workdir,
                                                   log_info = log_info)

    # Turn each list into a scalar, in a new dict
    d_method_tables: Dict[ShearEstimationMethods, Optional[Table]] = {}

    for method in ShearEstimationMethods:
        l_method_table_filenames: Sequence[str] = d_l_method_table_filenames[method]
        if len(l_method_table_filenames) == 0:
            d_method_tables[method] = None
        else:
            d_method_tables[method] = read_table(d_l_method_table_filenames[method][0], workdir)

    product = l_products[0]

    return d_method_tables, product


def append_hdu(filename: str,
               hdu: ExtensionHDU,
               log_info: bool = False) -> None:
    log_method = _get_optional_log_method(log_info)
    log_method("Appending HDU to file %s", filename)

    try:
        f = fits.open(filename, mode = 'append')
    except Exception as e:
        raise SheFileReadError(filename) from e

    try:
        f.append(hdu)
    except Exception as e:
        raise SheFileWriteError(filename) from e
    finally:
        f.close()

    logger.debug("Finished appending HDU to file %s", filename)


def try_remove_file(filename: str,
                    workdir: str = ".",
                    warn: bool = False):
    """ Attempts to remove a file, but passes if any exception is raised (optionally raising a warning).
    """
    try:
        qualified_filename = get_qualified_filename(filename, workdir = workdir)
        os.remove(os.path.join(qualified_filename))
    except IOError:
        if warn:
            logger.warning("Unable to delete file %s in workdir %s", filename, workdir)


def find_file_in_path(filename: str, path: str) -> str:
    """
        Searches through a colon-separated path for a file and returns the qualified name of it if found,
        None otherwise.
    """

    logger.debug("Searching for file %s in path %s", filename, path)

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

    logger.debug("Found file %s at %s", filename, qualified_filename)

    return qualified_filename


def find_aux_file(filename) -> str:
    """
        Searches the auxiliary directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_AUX_PATH'])


def find_conf_file(filename) -> str:
    """
        Searches the conf directory path for a file and returns a qualified name of it if found,
        None otherwise.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_CONF_PATH'])


def _is_no_file(name: Optional[str]):
    return name is None or name == "None" or name == f"{DATA_SUBDIR}None" or name == "" or name == DATA_SUBDIR


def _find_web_file_xml(filename: str, qualified_filename: str) -> str:
    webpath: str = os.path.split(filename)[0]

    try:
        p = read_xml_product(qualified_filename, workdir = "")
        for subfilename in p.get_all_filenames():
            # Skip if there's no file to download
            if _is_no_file(subfilename):
                continue
            find_web_file(os.path.join(webpath, subfilename))
    except SheFileReadError as e:
        if "elementBinding" not in str(e.__cause__):
            raise
        # MDB files end in XML but can't be read this way, and will raise this exception, so silently pass

    return webpath


def _find_web_file_json(filename: str, qualified_filename: str) -> None:
    webpath: str = os.path.split(filename)[0]

    l_filenames = read_listfile(qualified_filename)
    for element in l_filenames:
        if isinstance(element, str):
            # Skip if there's no file to download
            if _is_no_file(element):
                continue
            find_web_file(os.path.join(webpath, element))
        else:
            for sub_element in element:
                # Skip if there's no file to download
                if _is_no_file(sub_element):
                    continue
                find_web_file(os.path.join(webpath, sub_element))


def find_web_file(filename: str) -> str:
    """
        Searches on WebDAV for a file. If found, downloads it and returns the qualified name of it. If
        it's an xml data product, will also download all associated files.

        If it isn't found, returns None.
    """

    listfile_name: str = os.path.join(os.getcwd(),
                                      os.path.splitext(os.path.split(filename)[-1])[0] + f"{os.getpid()}_list.txt")

    logger.debug("Writing filelist to %s", listfile_name)

    try:
        try:
            with open(listfile_name, 'w') as fo:
                fo.write(filename + "\n")
        except Exception as e:
            raise SheFileWriteError(listfile_name) from e

        sync = DataSync(SYNC_CONF, listfile_name)
        sync.download()

        qualified_filename: str = sync.absolutePath(filename)
    finally:
        if os.path.exists(listfile_name):
            logger.debug("Cleaning up %s", listfile_name)
            os.remove(listfile_name)

    # If it's an xml data product, we'll also need to download all files it points to
    if filename[-4:] == ".xml":

        _find_web_file_xml(filename, qualified_filename)

    # If it's json listfile, we'll also need to download all files it points to
    elif filename[-5:] == ".json":

        _find_web_file_json(filename, qualified_filename)

    return qualified_filename


def find_file(filename: str, path: Optional[str] = None) -> str:
    """
        Locates a file based on the presence/absence of an AUX/ or CONF/ prefix, searching in the aux or conf
        directories respectively for it, or else the work directory if supplied.
    """

    logger.debug("Finding file %s, with path %s", filename, path)

    # Silently coerce input into a string
    filename = str(filename)
    qualified_filename: Optional[str]

    if filename[0:4] == "WEB/":
        qualified_filename = find_web_file(filename[4:])
    elif filename[0:4] == "AUX/":
        qualified_filename = find_aux_file(filename[4:])
    elif filename[0:5] == "CONF/":
        qualified_filename = find_conf_file(filename[5:])
    elif filename[0:5] == "HOME/":
        path = os.path.join(os.getenv('HOME'), os.path.dirname(filename[5:]))
        qualified_filename = find_file_in_path(os.path.basename(filename), path)
    elif filename[0] == "/":
        if not os.path.exists(filename):
            raise RuntimeError("File " + filename + " cannot be found.")
        qualified_filename = filename
    elif path is not None:
        qualified_filename = find_file_in_path(filename, path)
    else:
        raise ValueError("path must be supplied if filename doesn't start with AUX/ or CONF/")
    return qualified_filename


def first_in_path(path: str) -> str:
    """ Gets the first directory listed in the path.
    """

    return path.split(":")[0]


def first_writable_in_path(path: str) -> Optional[str]:
    """ Gets the first directory listed in the path which we have write access for.
    """

    colon_separated_path = path.split(":")

    first_writable_dir = None

    for test_path in colon_separated_path:

        if os.access(test_path, os.W_OK):
            first_writable_dir = test_path
            break

    return first_writable_dir


def get_data_filename(filename: str, workdir: str = ".") -> Optional[str]:
    """ Given the unqualified name of a file and the work directory, determine if it's an XML data
        product or not, and get the filename of its DataContainer if so; otherwise, just return
        the input filename. In either case, the unqualified filename is returned.

        This script is intended to help smooth the transition from using raw data files as
        input/output to data products.
    """

    # First, see if we can open this as an XML data product
    try:
        qualified_filename = find_file(filename, workdir)

        prod = read_xml_product(qualified_filename, allow_pickled = True)

        # If we get here, it is indeed an XML data product. Has it been monkey-patched
        # to have a get_filename method?

        if hasattr(prod, "get_filename"):
            data_filename = prod.get_filename()
        # or a get_data_filename method?
        elif hasattr(prod, "get_data_filename"):
            data_filename = prod.get_data_filename()
        else:
            # Check if the filename exists in the default location
            try:
                data_filename = DATA_SUBDIR + prod.Data.DataStorage.DataContainer.FileName
            except AttributeError:
                raise AttributeError("Data product does not have filename stored in the expected " +
                                     "location (self.Data.DataStorage.DataContainer.FileName. " +
                                     "In order to use get_data_filename with this product, the " +
                                     "product's class must be monkey-patched to have a get_filename " +
                                     "or get_data_filename method.")

    except SheFileReadError:
        # Not an XML file - so presumably it's a raw data file; return the
        # input filename
        data_filename = filename

    return data_filename


def update_xml_with_value(filename: str) -> None:
    r""" Updates xml files with value

    Checks for <Key><\Key> not followed by <Value><\Value>
    r"""

    try:
        lines = open(filename).readlines()
    except Exception as e:
        raise SheFileReadError(filename) from e

    key_lines = [ii for ii, line in enumerate(lines) if STR_KEY in line]
    bad_lines = [idx for idx in key_lines if STR_VALUE not in lines[idx + 1]]
    if not bad_lines:
        logger.debug('No updates required')
        return
    logger.warning("%s has incorrect parameter settings, missing <Value> in lines: %s",
                   filename,
                   ','.join(map(str, bad_lines)))
    # Do update
    n_defaults = 0
    for ii, idx in enumerate(bad_lines):
        # Check next 3 lines for String/Int etc Value

        info = [line for line in lines[idx + 1 + ii:min(idx + 4 + ii, len(lines) - 1)] if 'Value>' in line]
        new_line = None
        if info:
            data_value = info[0].split('Value>')[1].split('<')[0]
            if len(data_value) > 0:
                new_line = lines[idx + ii].split(STR_KEY)[0] + '<Value>%s</Value>\n' % data_value

        if not new_line:
            # Add random string...
            new_line = lines[idx + ii].split(STR_KEY)[0] + '<Value>dkhf</Value>\n'
            n_defaults += 1
        lines = lines[:idx + ii + 1] + [new_line] + lines[idx + ii + 1:]

        try:
            open(filename, 'w').writelines(lines)
        except Exception as e:
            raise SheFileWriteError(filename) from e

    logger.info('Updated %s lines in %s: n_defaults=%s',
                len(bad_lines),
                filename,
                n_defaults)


def filename_exists(filename: Optional[str]) -> bool:
    """Quick function to check the filename isn't one of many strings indicating the file doesn't exist.
    """
    return filename not in (None, "None", f"{DATA_SUBDIR}None", "", DATA_SUBDIR)


def remove_files(l_qualified_filenames: Sequence[str]) -> None:
    """ Loop through and try to remove all files in a list. No exception is raised if the files can't be removed,
        but a warning is logged.
    """
    for qualified_filename in l_qualified_filenames:
        try:
            os.remove(qualified_filename)
        except Exception:
            # Don't need to fail the whole process, but log the issue
            logger.warning(f"Cannot delete file: {qualified_filename}")


def tar_files(tarball_filename: str,
              l_filenames: Sequence[str],
              workdir: str = ".",
              delete_files: bool = False):
    qualified_tarball_filename: str = get_qualified_filename(tarball_filename, workdir)

    filename_string = " ".join(l_filenames)

    # Tar the files and fully log the process
    logger.info(f"Creating tarball {qualified_tarball_filename}.")

    tar_cmd = f"cd {workdir} && tar -cf {qualified_tarball_filename} {filename_string}"
    tar_results = subprocess.run(tar_cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    logger.info(f"tar stdout: {tar_results.stdout}")
    logger.debug("tar stderr: %s", tar_results.stderr)

    # Check that the tar process succeeded
    if not os.path.isfile(qualified_tarball_filename):
        base_error = FileNotFoundError(f"{qualified_tarball_filename} not found. "
                                       f"stderr from tar process "
                                       f"was: \n"
                                       f"{tar_results.stderr}")
        raise SheFileWriteError(filename = tarball_filename, workdir = workdir) from base_error
    if tar_results.returncode:
        base_error = ValueError(f"Tarring of {qualified_tarball_filename} failed. stderr from tar process was: \n"
                                f"{tar_results.stderr}")
        raise SheFileWriteError(filename = tarball_filename, workdir = workdir) from base_error

    # Delete the files if desired
    if delete_files:
        for filename in l_filenames:
            qualified_filename = get_qualified_filename(filename, workdir)
            try:
                os.remove(qualified_filename)
            except Exception:
                # Don't need to fail the whole process, but log the issue
                logger.warning(f"Cannot delete file: {qualified_filename}")


T = TypeVar('T')


class FileLoader(abc.ABC, Generic[T]):
    """ Abstract base class for loading in a data from the work directory.
    """

    # Attributes set at init
    _filename: str
    _workdir: str

    # Attributes set on-demand
    _qualified_filename: Optional[str] = None

    # Attributes set when loaded
    _obj: Optional[T] = None

    def __init__(self,
                 filename: str,
                 workdir: str):

        self.filename = filename
        self.workdir = workdir

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._qualified_filename = None
        self._filename = filename

    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: str):
        self._qualified_filename = None
        self._workdir = workdir

    @property
    def qualified_filename(self) -> str:
        if not self._qualified_filename:
            self._qualified_filename = get_qualified_filename(self.filename, self.workdir)
        return self._qualified_filename

    @property
    def object(self) -> Optional[T]:
        return self._obj

    @property
    def obj(self) -> Optional[T]:
        return self._obj

    def load(self, *args, **kwargs) -> None:
        """ Method to load in the object.
        """
        self._obj = self.get(*args, **kwargs)

    def open(self, *args, **kwargs) -> None:
        """ Alias to self.load.
        """
        self.load(*args, **kwargs)

    def close(self) -> None:
        """ Deletes the object to allow memory to be freed.
        """
        self._obj = None

    @abc.abstractmethod
    def get(self, *args, **kwargs) -> T:
        """ Method to get the object.  Should take a format such as:

            return load_object(filename=self.filename, workdir=self.workdir, *args, **kwargs)
        """


class ProductLoader(FileLoader):
    """ FileLoader specialized to load in .xml data products.
    """

    def get(self, *args, **kwargs) -> Any:
        return read_xml_product(xml_filename = self.filename, workdir = self.workdir, *args, **kwargs)


class TableLoader(FileLoader[Table]):
    """ FileLoader specialized to load in astropy data tables.
    """

    def get(self, *args, **kwargs) -> Table:
        return read_table(filename = self.filename, workdir = self.workdir, *args, **kwargs)


class FitsLoader(FileLoader[Table]):
    """ FileLoader specialized to load in astropy data tables.
    """

    def get(self, *args, **kwargs) -> HDUList:
        return read_fits(self.filename, self.workdir, *args, **kwargs)


class MultiFileLoader(Generic[T]):
    """ A class to handle loading in multiple files of the same type.
    """

    # Attributes set at init
    workdir: str
    l_filenames: Sequence[str]
    l_file_loaders: Sequence[FileLoader[T]]
    file_loader_type: Optional[Type[T]] = None

    def __init__(self,
                 workdir: str,
                 l_file_loaders: Optional[Sequence[FileLoader[T]]] = None,
                 l_filenames: Optional[Sequence[str]] = None,
                 file_loader_type: Optional[Type[T]] = None) -> None:

        self.workdir = workdir

        if file_loader_type:
            self.file_loader_type = file_loader_type

        if l_file_loaders:
            if l_filenames:
                raise ValueError("MultiFileLoader can be inited with only one of l_file_loaders and l_filenames.")
            self.l_file_loaders = l_file_loaders
            self.l_filenames = [file_loader.filename for file_loader in self.l_file_loaders]

        elif l_filenames:
            self.l_filenames = l_filenames
            self.l_file_loaders = [self.file_loader_type(filename = filename, workdir = self.workdir) for
                                   filename in self.l_filenames]

        else:
            self.l_file_loaders = []
            self.l_filenames = []

    def load_all(self, *args, **kwargs):
        """ Load all files.
        """
        for file_loader in self.l_file_loaders:
            file_loader.load(*args, **kwargs)

    def open_all(self, *args, **kwargs):
        """ Alias to load_all.
        """
        self.load_all(*args, **kwargs)

    def close_all(self):
        """ Close all files.
        """
        for file_loader in self.l_file_loaders:
            file_loader.close()

    def get_all(self, *args, **kwargs) -> List[T]:
        """ Get a list of all files (load and return, but don't keep a reference).
        """
        return [file_loader.get(*args, **kwargs) for file_loader in self.l_file_loaders]


class MultiProductLoader(MultiFileLoader):
    """ A class to handle loading in multiple xml data products.
    """

    file_loader_type: Type = ProductLoader


class MultiTableLoader(MultiFileLoader):
    """ A class to handle loading in multiple xml data products.
    """

    file_loader_type: Type = TableLoader
