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
import shutil
import subprocess
from datetime import datetime
from os.path import exists, join
from typing import Any, Callable, Dict, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, Union

import numpy as np
from astropy.io import fits
from astropy.io.fits import HDUList
from astropy.io.fits.hdu.base import ExtensionHDU
from astropy.table import Table
from astropy.utils import deprecated, deprecated_renamed_argument
from pyxb.exceptions_ import NamespaceError

from EL_PythonUtils.utilities import time_to_timestamp
from ElementsServices.DataSync import DataSync
from ElementsServices.DataSync.DataSynchronizer import DownloadFailed
from ST_DM_FilenameProvider.FilenameProvider import FileNameProvider
from ST_DataModelBindings.sys_stub import CreateFromDocument
from . import __version__
from .constants.classes import ShearEstimationMethods
from .constants.test_data import SYNC_CONF, TEST_DATADIR
from .logging import getLogger
from .utility import get_release_from_version, is_any_type_of_none, join_without_none

# Constant strings for default values in filenames
DEFAULT_WORKDIR = "."
DEFAULT_TYPE_NAME = "UNKNOWN-FILE-TYPE"
DEFAULT_INSTANCE_ID = "0"
DEFAULT_FILE_EXTENSION = ".fits"
DEFAULT_FILE_SUBDIR = "data"
DEFAULT_FILE_PF = "SHE"

# Constant strings for operations
STR_READING = "reading"
STR_WRITING = "writing"

# Constant strings for messages

MSG_FINISHED_READING_LISTFILE = "Finished reading listfile from %s"
MSG_READING_LISTFILE = "Reading listfile from %s"
MSG_FINISHED_WRITING_LISTFILE = "Finished writing listfile to %s"
MSG_WRITING_LISTFILE = "Writing listfile to %s"

MSG_READING_DATA_PRODUCT = f"Reading data product from %s in workdir %s"
MSG_WRITING_DATA_PRODUCT = f"Writing data product to %s in workdir %s"
MSG_FINISHED_READING_DATA_PRODUCT = f"Finished reading data product from %s in workdir %s successfully"
MSG_FINISHED_WRITING_DATA_PRODUCT = f"Finished writing data product to %s in workdir %s successfully"

MSG_READING_TABLE = f"Reading table from %s in workdir %s"
MSG_WRITING_TABLE = f"Writing table to %s in workdir %s"
MSG_FINISHED_READING_TABLE = f"Finished reading table from %s in workdir %s successfully"
MSG_FINISHED_WRITING_TABLE = f"Finished writing table to %s in workdir %s successfully"

MSG_READING_FITS_FILE = f"Reading FITS file from %s in workdir %s"
MSG_WRITING_FITS_FILE = f"Writing FITS file to %s in workdir %s"
MSG_FINISHED_READING_FITS_FILE = f"Finished reading FITS file from %s in workdir %s successfully"
MSG_FINISHED_WRITING_FITS_FILE = f"Finished writing FITS file to %s in workdir %s successfully"

MSG_SRC_NOT_EXIST = "In safe_copy, source file %s does not exist"
MSG_DEST_EXIST = "In safe_copy, destination file %s already exists"

# Constant string for the data subdirectory, where datafiles are expected to be stored during pipeline execution
DATA_SUBDIR = "data/"

# Constant string to represent that a file does not exist
FILENAME_NONE = "None"

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


# Private functions for this module

def _get_optional_log_method(log_info: bool) -> Callable[..., None]:
    """Get the desired logging method. If log_info==True, will log at info level, otherwise at debug level. Returns a
    method of the SHE_PPT.file_io logger.

    Parameters
    ----------
    log_info : bool
        Whether logging should be at info level (True), or else debug level (False).

    Returns
    -------
    log_method : Callable
        The appropriate method of the SHE_PPT.file_io logger, either logger.info or logger.debug.
    """
    if log_info:
        return logger.info
    return logger.debug


# Classes for custom exceptions raised by functions in this module

class SheFileAccessError(IOError):
    """A custom exception type for exceptions raised by functions in the SHE_PPT.file io module related to accessing
    a file - either reading from it or writing to it.

    Attributes
    ----------
    filename : Optional[str]
        The workdir-relative filename of the file for which the exception was raised. In some cases, this might not
        be available, in which case this attribute will be `None`. This occurs if the exception was constructed
        with only `qualified_filename` provided.
    qualified_filename : str
        The fully-qualified filename of the file for which the exception was raised.
    workdir : Optional[str]
        The workdir in which resides the file for which the exception was raised. As with `filename`, this will be
        set to `None` if this exception is constructed with only `qualified_filename` provided.
    operation : {"accessing", "reading", "writing"}
        The type of operation being performed when the exception occurred.
    message
    """
    filename: Optional[str] = None
    qualified_filename: str
    workdir: Optional[str] = None
    operation: str = "accessing"
    _message: Optional[str] = None

    def __init__(self,
                 qualified_filename: Optional[str] = None,
                 filename: Optional[str] = None,
                 workdir: Optional[str] = None,
                 message: Optional[str] = None,
                 ):
        """Initialise an instance of a SheFileAccessError object.

        This must be initialised with either:
        1. (Preferably) both the `filename` and `workdir` kwargs specified.
        OR
        2. (If necessary) the `qualified_filename` kwarg specified.
        If the `filename` and `workdir` kwargs are provided, these will be used to determine the `qualified_filename`
        attribute. If the `qualified_filename` kwarg was also provided and it conflicts with this, an exception will
        be raised.

        Parameters
        ----------
        qualified_filename : Optional[str], default=None
            The fully-qualified filename of the file for which this exception occurred.
        filename : Optional[str], default=None
            The workdir-relative filename of the file for which this exception occurred.
        workdir : Optional[str], default=None
            The workdir containing the file for which this exception occurred.
        message : Optional[str], default=None
            If desired, a detailed description of the exception which occurred. If not provided, this exception's
            message will take a default format, noting simply that there was an issue accessing the given file.
        """

        # Set the filename, workdir, and qualified_filename attributes, checking that enough information is provided
        # and it doesn't conflict

        if (filename is not None) and (workdir is not None):

            self.filename = filename
            self.workdir = workdir

            # Check that the provided value for qualified_filename doesn't conflict with what we construct here
            constructed_qualified_filename = get_qualified_filename(filename = filename, workdir = workdir)
            if qualified_filename is not None and qualified_filename != constructed_qualified_filename:
                raise ValueError("In construction of `SheFileAccessError`, `qualified_filename`, `filename`, "
                                 "and `workdir` were all supplied, and give conflicting qualified filenames: "
                                 f"`qualified_filename` = '{qualified_filename}', "
                                 f"`filename` = '{filename}', "
                                 f"`workdir` = '{workdir}', "
                                 f"`constructed_qualified_filename` = '{constructed_qualified_filename}'")

            self.qualified_filename = constructed_qualified_filename

        elif qualified_filename is not None:

            self.qualified_filename = qualified_filename

        else:
            raise ValueError("Cannot construct `SheFileAccessError` without either `qualified_filename` argument or "
                             "both `filename` and `workdir` arguments. Arguments were: "
                             f"`qualified_filename` = '{qualified_filename}', "
                             f"`filename` = '{filename}', "
                             f"`workdir` = '{workdir}'")

        # Set the message if explicitly provided; otherwise it will be default generated
        if message is not None:
            self._message = message

        super().__init__(self.message)

    @property
    def message(self) -> str:
        """A message detailing the nature of the exception. This may be provided at class initialisation,
        or else generated automatically with a default format.

        Returns
        -------
        self._message : str
            The message detailing the nature of the exception
        """
        if self._message is None:
            self._message = f"Error {self.operation} file {self.qualified_filename}."
        return self._message


class SheFileReadError(SheFileAccessError):
    """A specialisation of the SheFileAccessError class, specifically for exceptions which arise from attempting to
    read a file.
    """
    operation: str = STR_READING


class SheFileWriteError(SheFileAccessError):
    """A specialisation of the SheFileAccessError class, specifically for exceptions which arise from attempting to
    write a file.
    """
    operation: str = STR_WRITING


class SheFileNamer(FileNameProvider):
    """ Class to handle generating Euclid-compliant filenames piecewise from components.

    Attributes
    ----------
    type_name
    default_type_name : str
        The default value to be used for the `type_name` attribute if no other information is supplied
    instance_id
    default_instance_id : str
        The default value to be used for the `instance_id` attribute if no other information is supplied
    extension
    release
    version
    subdir
    processing_function
    timestamp
    workdir
    filename
    qualified_filename
    """

    # Attributes used to generate the filename - can be set (at init or otherwise) before calling get()

    # For type name
    _type_name_head: Optional[str] = None
    _type_name_body: Optional[str] = None
    _type_name_tail: Optional[str] = None

    _type_name: Optional[str] = None

    default_type_name: str = DEFAULT_TYPE_NAME

    # For instance ID
    _instance_id_head: Optional[str] = None
    _instance_id_body: Optional[str] = None
    _instance_id_tail: Optional[str] = None

    _instance_id: Optional[str] = None

    default_instance_id: str = DEFAULT_INSTANCE_ID

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
        """Initializes an instance of a SheFileNamer object.

        Parameters
        ----------
        type_name : Optional[str], default=None
            The desired type name for the generated filename. If not provided, will be determined from the
            `_type_name_head`, `_type_name_body`, and `_type_name_tail` class attributes, unless all of these are
            `None`, in which case a ValueError will be raised.
        instance_id : Optional[str], default=None
            The desired instance ID for the generated filename. If not provided, will be determined from the
            `_instance_id_head`, `_instance_id_body`, and `_instance_id_tail` class attributes, unless all of these are
            `None`, in which case a ValueError will be raised.
        extension : Optional[str], default=None
            The desired extension of the generated filename (e.g. '.fits'). If not provided, will be determined from the
            `_extension` class attribute.
        release : Optional[str], default=None
            The code release that this file corresponds to, in the format 'XX.YY' where XX and YY are integers
            between 00 and 99, inclusive (e.g. '01.00'). Either this or `version` must be provided.
        version : Optional[str], default=None
            The code version that this file corresponds to, in the format 'X.Y' or `X.Y.Z`, where X, Y, and Z are
            non-negative integers (e.g. `1.0` or '1.0.0'). Either this or `release` must be provided.
        subdir : Optional[str], default=None
            The desired subdirectory for the generated filename (e.g. "data/"). If not provided, will be determined
            from the `_subdir` class attribute. If it is desired that the file not be in a subdirectory, this must be
            set to an empty string (''), and NOT `None` - the latter will result in it being determined from the
            `_subdir` class attribute, as if the kwarg were not supplied.
        processing_function : Optional[str], default=None
            The name of the processing function in which this file was created (e.g. 'SHE'). If not provided,
            will be determined from the `_processing_function` class attribute.
        timestamp : Optional[bool], default=None
            Whether or not to include a timestamp as part of the filename's instance ID. If not provided,
            will be determined from the `_timestamp` class attribute.
        workdir : Optional[str], default=None
            The workdir in which this file will reside. This is used to generate the `qualified_filename` attribute
            if provided.
        """

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
        """The first string to be combined to form the type name in the generated filename.

        Returns
        -------
        self._type_name_head : str
        """
        return self._type_name_head

    @type_name_head.setter
    def type_name_head(self, type_name_head: Optional[str]) -> None:
        """Setter for `type_name_head`. When called, de-caches the value of `self.type_name`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        type_name_head : Optional[str]
        """
        self._type_name_head = type_name_head
        self.type_name = None

    @property
    def type_name_body(self) -> str:
        """The middle string to be combined to form the type name in the generated filename.

        Returns
        -------
        self._type_name_body : str
        """
        if self._type_name_body is None:
            self._determine_type_name_body()
        return self._type_name_body

    @type_name_body.setter
    def type_name_body(self, type_name_body: Optional[str]) -> None:
        """Setter for `type_name_body`. When called, de-caches the value of `self.type_name`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        type_name_body : Optional[str]
        """
        self._type_name_body = type_name_body
        self.type_name = None

    @property
    def type_name_tail(self) -> str:
        """The final string to be combined to form the type name in the generated filename.

        Returns
        -------
        self._type_name_tail : str
        """
        return self._type_name_tail

    @type_name_tail.setter
    def type_name_tail(self, type_name_tail: Optional[str]) -> None:
        """Setter for `type_name_tail`. When called, de-caches the value of `self.type_name`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        type_name_tail : Optional[str]
        """
        self._type_name_tail = type_name_tail
        self.type_name = None

    @property
    def instance_id_head(self) -> str:
        """The first string to be combined to form the instance ID in the generated filename.

        Returns
        -------
        self._instance_id_head : str
        """
        return self._instance_id_head

    @instance_id_head.setter
    def instance_id_head(self, instance_id_head: Optional[str]) -> None:
        """Setter for `instance_id_head`. When called, de-caches the value of `self.instance_id`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        instance_id_head : Optional[str]
        """
        self._instance_id_head = instance_id_head
        self.instance_id = None

    @property
    def instance_id_body(self) -> str:
        """The middle string to be combined to form the instance ID in the generated filename.

        Returns
        -------
        self._instance_id_body : str
        """
        if self._instance_id_body is None:
            self._determine_instance_id_body()
        return self._instance_id_body

    @instance_id_body.setter
    def instance_id_body(self, instance_id_body: Optional[str]) -> None:
        """Setter for `instance_id_body`. When called, de-caches the value of `self.instance_id`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        instance_id_body : Optional[str]
        """
        self._instance_id_body = instance_id_body
        self.instance_id = None

    @property
    def instance_id_tail(self) -> str:
        """The final string to be combined to form the instance ID in the generated filename.

        Returns
        -------
        self._instance_id_tail : str
        """
        return self._instance_id_tail

    @instance_id_tail.setter
    def instance_id_tail(self, instance_id_tail: Optional[str]) -> None:
        """Setter for `instance_id_tail`. When called, de-caches the value of `self.instance_id`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        instance_id_tail : Optional[str]
        """
        self._instance_id_tail = instance_id_tail
        self.instance_id = None

    @property
    def extension(self) -> str:
        """The desired extension of the filename to be generated (e.g. '.fits').

        Returns
        -------
        self._extension : str
        """
        return self._extension

    @extension.setter
    def extension(self, extension: Optional[str]) -> None:
        """Setter for `extension`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        extension : Optional[str]
        """
        self._extension = extension
        self.filename = None

    @property
    def release(self) -> str:
        """The code release that this file corresponds to, in the format 'XX.YY' where XX and YY are integers
        between 00 and 99, inclusive (e.g. '01.00'). Either this or `version` must be non-`None` for a filename to be
        generated.

        Returns
        -------
        self._release : str
        """
        return self._release

    @release.setter
    def release(self, release: Optional[str]) -> None:
        """Setter for `release`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        release : Optional[str]
        """
        self._release = release
        self.filename = None

    @property
    def version(self) -> str:
        """The code version that this file corresponds to, in the format 'X.Y' or `X.Y.Z`, where X, Y,
        and Z are non-negative integers (e.g. `1.0` or '1.0.0'). Either this or `release` must be non-`None` for a
        filename to be generated.

        Returns
        -------
        self._version : str
        """
        return self._version

    @version.setter
    def version(self, version: Optional[str]) -> None:
        """Setter for `version`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        version : Optional[str]
        """
        self._version = version
        self.filename = None

    @property
    def subdir(self) -> str:
        """The desired subdirectory for the generated filename (e.g. "data/"). If it is desired that the file not be
        in a subdirectory, this must be set to an empty string (''), and NOT `None`.

        Returns
        -------
        self._subdir : str
        """
        return self._subdir

    @subdir.setter
    def subdir(self, subdir: Optional[str]) -> None:
        """Setter for `subdir`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        subdir : Optional[str]
        """
        self._subdir = subdir
        self.filename = None

    @property
    def processing_function(self) -> str:
        """The name of the processing function in which this file was created (e.g. 'SHE').

        Returns
        -------
        self._processing_function : str
        """
        return self._processing_function

    @processing_function.setter
    def processing_function(self, processing_function: Optional[str]) -> None:
        """Setter for `processing_function`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        processing_function : Optional[str]
        """
        self._processing_function = processing_function
        self.filename = None

    @property
    def timestamp(self) -> bool:
        """Whether or not to include a timestamp as part of the filename's instance ID.

        Returns
        -------
        self._timestamp : bool
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: bool) -> None:
        """Setter for `timestamp`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        timestamp : Optional[str]
        """
        self._timestamp = timestamp
        self.filename = None

    @property
    def workdir(self) -> Optional[str]:
        """The workdir in which this file will reside. This is used to generate the `qualified_filename` attribute if
        provided. If this is `None` and the `qualified_filename` attribute is accessed, an exception will be raised.

        Returns
        -------
        self._workdir : Optional[str]
        """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: Optional[str]) -> None:
        """Setter for `workdir`. When called, de-caches the value of `self.qualified_filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        workdir : Optional[str]
        """
        self._workdir = workdir
        self.qualified_filename = None

    @property
    def type_name(self) -> str:
        """The desired type name for the generated filename.

        Returns
        -------
        self._type_name : str
        """
        if self._type_name is None:
            self.__determine_type_name()
        return self._type_name

    @type_name.setter
    def type_name(self, type_name: Optional[str]) -> None:
        """Setter for `type_name`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        type_name : Optional[str]
        """
        self._type_name = type_name
        self.filename = None

    @property
    def instance_id(self) -> str:
        """The desired instance ID for the generated filename.

        Returns
        -------
        self._instance_id : str
        """
        if self._instance_id is None:
            self.__determine_instance_id()
        return self._instance_id

    @instance_id.setter
    def instance_id(self, instance_id: Optional[str]) -> None:
        """Setter for `instance_id`. When called, de-caches the value of `self.filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        instance_id : Optional[str]
        """
        self._instance_id = instance_id
        self.filename = None

    @property
    def filename(self) -> str:
        """The generated workdir-relative filename.

        Returns
        -------
        self._filename : str
        """
        if self._filename is None:
            self._filename = self.get()
        return self._filename

    @filename.setter
    def filename(self, filename: Optional[str]) -> None:
        """Setter for `filename`. When called, de-caches the value of `self.qualified_filename`, so that the next time
        that is accessed, it's properly updated.

        Parameters
        ----------
        filename : Optional[str]
        """
        self._filename = filename
        self.qualified_filename = None

    @property
    def qualified_filename(self) -> str:
        """The fully-qualified generated filename.

        Returns
        -------
        self._qualified_filename : str
        """
        if self._qualified_filename is None:
            self._qualified_filename = get_qualified_filename(self.filename, self.workdir)
        return self._qualified_filename

    @qualified_filename.setter
    def qualified_filename(self, qualified_filename: Optional[str]) -> None:
        """Setter for `qualified_filename`.

        Parameters
        ----------
        qualified_filename : Optional[str]
        """
        self._qualified_filename = qualified_filename

    # Private methods

    def __determine_type_name(self) -> None:
        """Piece together the type name from the components, leaving out any which are `None`.
        """
        self._type_name = join_without_none(l_s = [self.type_name_head,
                                                   self.type_name_body,
                                                   self.type_name_tail],
                                            default = self.default_type_name)

    def __determine_instance_id(self) -> None:
        """Piece together the instance ID from the components, leaving out any which are `None`.
        """
        self._instance_id = join_without_none(l_s = [self.instance_id_head,
                                                     self.instance_id_body,
                                                     self.instance_id_tail],
                                              default = self.default_instance_id)

    # Protected methods

    def _determine_type_name_body(self) -> None:
        """A child class of this may override this method with an implementation which sets the `self._type_name_body`
        attribute, and this will be called if `self._type_name_body` is found to be `None` when `self.type_name_body` is
        accessed to generate it.

        It is not necessary that this be implemented by child classes. They may instead either directly set
        `self._type_name_body` as a class attribute, or else any initialization must specify the `type_name` kwarg.

        Example implementation:
        ```
        self._type_name_body = "TYPE_NAME"
        ```
        """
        raise NotImplementedError(
            "`_determine_type_name_body` must be overridden if `type_name` is not passed to `__init__` of "
            "`SheFileNamer` and `_type_name_body` is not directly set as a class attribute.")

    def _determine_instance_id_body(self) -> None:
        """A child class of this may override this method with an implementation which sets the `self._instance_id_body`
        attribute, and this will be called if `self._instance_id_body` is found to be `None` when
        `self.instance_id_body` is accessed to generate it.

        It is not necessary that this be implemented by child classes. They may instead either directly set
        `self._instance_id_body` as a class attribute, or else any initialization must specify the `instance_id` kwarg.

        Example implementation:
        ```
        self._instance_id_body = "INSTANCE_ID"
        ```
        """
        raise NotImplementedError(
            "`_determine_instance_id_body` must be overridden if `instance_id` is not passed to `__init__` "
            "of `SheFileNamer` and `_instance_id_body` is not directly set as a class attribute.")

    # Public methods

    def get(self):
        """Generate a filename based on this object's attributes. This method re-generates a filename each time it is
        called, which differs from the `filename` property, which generates a filename once and caches it. If
        `timestamp==True`, this will result in this usually returning different filenames each time it is called,
        even if none of this object's attributes are changed, due simply to the timestamp changing.

        Returns
        -------
        filename : str
        """
        # Check we have just one of release and version
        if (self.release is None) == (self.version is None):
            raise ValueError("Exactly one of the `release` and `version` attributes of a `SheFileNamer` object must "
                             "be non-`None`.")

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

        # Call the parent class's method to get an allowed filename, relative to the sub-directory
        local_filename: str = self.get_allowed_filename(processing_function = self.processing_function,
                                                        type_name = self.type_name.upper(),
                                                        instance_id = self.instance_id.upper(),
                                                        extension = extension,
                                                        release = release,
                                                        timestamp = self.timestamp)

        # Add the sub-directory to get the full filename - check if it's None, just in case a child class overrides
        # the class attribute to be None
        if self.subdir is not None:
            filename = join(self.subdir, local_filename)
        else:
            filename = local_filename

        return filename


def get_qualified_filename(filename: str,
                           workdir: str = DEFAULT_WORKDIR) -> str:
    """Gets a fully-qualified filename, checking if the first argument is already fully-qualified first. If it is,
    it's return directly. Otherwise the workdir is joined to it.

    Parameters
    ----------
    filename : str
    workdir : str

    Returns
    -------
    qualified_filename : str
    """

    # Check if filename is an empty string, and raise an exception if so - this indicates something must be going wrong
    if filename == "":
        raise ValueError("Filename provided to `get_qualified_filename` cannot be an empty string.")

    # Check if the filename is fully-qualified already by checking if it starts with a "/"
    if filename[0] == "/":
        return filename

    return os.path.join(workdir, filename)


def get_allowed_filename(type_name: str = DEFAULT_TYPE_NAME,
                         instance_id: str = DEFAULT_INSTANCE_ID,
                         extension: str = DEFAULT_FILE_EXTENSION,
                         release: Optional[str] = None,
                         version: Optional[str] = None,
                         subdir: Optional[str] = DEFAULT_FILE_SUBDIR,
                         processing_function: str = DEFAULT_FILE_PF,
                         timestamp: bool = True) -> str:
    """Gets a filename in the required Euclid format. This function is provided for backwards-compatibility; for any new
    use it is recommend to use the `SheFileNamer` class directly, with syntax as shown here.

    See the documentation of the `SheFileNamer` class's `__init__` method for documentation of this function's
    parameters.

    Returns
    -------
    filename : str
        The generated workdir-relative filename.
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
                   filenames: Sequence[Union[str, Tuple[str, ...]]],
                   log_info: bool = False,
                   workdir: str = DEFAULT_WORKDIR) -> None:
    """Writes a listfile in json format. The implementation here is copied from
    https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files with some modification.

    Parameters
    ----------
    listfile_name : str
        The fully-qualified or workdir-relative name of the listfile to which the list of filenames should be written.
    filenames : Sequence[Union[str, Tuple[str, ...]]]
        List of workdir-relative filenames to be output
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    workdir : str, default="."
        The workdir in which the file should be created. If `listfile_name` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    """

    qualified_listfile_name = get_qualified_filename(filename = listfile_name, workdir = workdir)

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_WRITING_LISTFILE, listfile_name)

    try:
        with open(qualified_listfile_name, 'w') as listfile:
            paths_json = json.dumps(filenames)
            listfile.write(paths_json)
    except Exception as e:
        raise SheFileWriteError(filename = listfile_name, workdir = workdir) from e

    logger.debug(MSG_FINISHED_WRITING_LISTFILE, qualified_listfile_name)


def read_listfile(listfile_name: str,
                  log_info: bool = False,
                  workdir: str = "") -> List[Union[str, Tuple[str, ...]]]:
    """Reads a json listfile and returns a list of filenames. The implementation here is copied from
    https://euclid.roe.ac.uk/projects/codeen-users/wiki/Pipeline_Interfaces#List-Files with some modification.

    Parameters
    ----------
    listfile_name: str
        The fully-qualified or workdir-relative name of the listfile from which the list of filenames should be read.
    log_info: bool
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    workdir: str
        The workdir in which the file exists. If `listfile_name` is provided fully-qualified, it is not necessary for
        this to be provided (and it will be ignored if it is).

    Returns
    -------
    l_filenames : List[Union[str, Tuple[str, ...]]]
        A list of workdir-relative filenames, or a list of tuples of filenames, depending on how the listfile which
        is read in is formatted.
    """

    qualified_listfile_name = get_qualified_filename(filename = listfile_name, workdir = workdir)

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_LISTFILE, qualified_listfile_name)

    try:
        with open(qualified_listfile_name, 'r') as f:
            l_filenames = json.load(f)
            if len(l_filenames) == 0:
                return l_filenames
            if isinstance(l_filenames[0], list):
                tupled_list = [tuple(el) for el in l_filenames]
                if np.all([len(t) == 1 for t in tupled_list]):
                    tupled_list = [t[0] for t in tupled_list]
                return tupled_list
    except Exception as e:
        raise SheFileReadError(filename = listfile_name, workdir = workdir) from e

    log_method(MSG_FINISHED_READING_LISTFILE, qualified_listfile_name)

    return l_filenames


def replace_in_file(input_filename: str,
                    output_filename: str,
                    input_string: str,
                    output_string: str) -> None:
    """Creates a copy of the file at `input_filename` in which all occurrences of `input_string` are replaced with
    `output_string`, and saves it to `output_filename`.

    Parameters
    ----------
    input_filename : str
        The fully-qualified path to the input file.
    output_filename : str
        The fully-qualified path to the desired location of the output file to be created. This must differ from
        `input_filename`.
    input_string : str
        The string for which all occurrences in the input file should be replaced with `output_string`.
    output_string : str
        The string to replace all occurrences of `input_string` in the input file with.
    """

    if input_filename == output_filename:
        raise ValueError("In `replace_in_file`, `input_filename` and `output_filename` must differ. Input arguments "
                         f"were: {input_filename=}, {output_filename=}, {input_string=}, {output_string=}.)")

    with open(output_filename, "w") as f_out:
        with open(input_filename, "r") as f_in:
            for line in f_in:
                f_out.write(line.replace(input_string, output_string))


def replace_multiple_in_file(input_filename: str,
                             output_filename: str,
                             input_strings: Sequence[str],
                             output_strings: Sequence[str]) -> None:
    """Creates a copy of the file at `input_filename` in which all occurrences of each string in the sequence
    `input_strings` are replaced with the corresponding string in the sequence `output_strings`, and saves it to
    `output_filename`.

    For example, if `input_strings=["one", "two"]` and `output_strings=["1", "2"]`, all occurrences of "one" will
    be replaced with "1", and all occurrences of "two" will be replaced with "2".

    Parameters
    ----------
    input_filename : str
        The fully-qualified path to the input file.
    output_filename : str
        The fully-qualified path to the desired location of the output file to be created. This must differ from
        `input_filename`.
    input_strings : Sequence[str]
        The string for which all occurrences in the input file should be replaced with `output_string`.
    output_strings : Sequence[str]
        The string to replace all occurrences of `input_string` in the input file with.
    """

    if input_filename == output_filename:
        raise ValueError(
            "In `replace_multiple_in_file`, `input_filename` and `output_filename` must differ. Input arguments "
            f"were: {input_filename=}, {output_filename=}, {input_strings=}, {output_strings=}.)")

    if len(input_strings) != len(output_strings):
        raise ValueError(
            "In `replace_multiple_in_file`, `input_strings` and `output_strings` were provided with different "
            f"lengths. Input arguments were: {input_filename=}, {output_filename=}, {input_strings=}, "
            f"{output_strings=}.)")

    with open(output_filename, "w") as f_out:
        with open(input_filename, "r") as f_in:
            for line in f_in:
                new_line = line
                for input_string, output_string in zip(input_strings, output_strings):
                    new_line = new_line.replace(input_string, output_string)
                f_out.write(new_line)


@deprecated_renamed_argument("allow_pickled",
                             new_name = None,
                             since = "9.1")
def write_xml_product(product: Any,
                      xml_filename: str,
                      workdir: str = DEFAULT_WORKDIR,
                      log_info: bool = False,
                      allow_pickled: bool = False) -> None:
    """Outputs an instance of a Data Model product to a .xml file on disk. The implementation of this is copied from
    https://euclid.roe.ac.uk/projects/codeen-users/wiki/DataModelTutorial2017 with some modification.

    Parameters
    ----------
    product : Any type of Euclid data product defined in the Data Model bindings
        The data product to be output.
    xml_filename : str
        The desired fully-qualified or workdir-relative filename of the output file.
    workdir : str, default="."
        The workdir in which the file should be created. If `xml_filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    allow_pickled : bool, default=False
        (Deprecated and to be removed soon; do not use)
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_WRITING_DATA_PRODUCT, xml_filename, workdir)

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    try:
        _write_xml_product(product, xml_filename, workdir)
    except Exception as e:
        raise SheFileWriteError(filename = xml_filename, workdir = workdir) from e

    logger.debug(MSG_FINISHED_WRITING_DATA_PRODUCT, xml_filename, workdir)


def _write_xml_product(product: Any, xml_filename: str, workdir: str) -> None:
    """Private implementation of the core operations of `write_xml_product`; see that function's documentation for
    information on functionality and parameters.
    """

    # Make sure the product's header has a likely-unique value, and not the default value of "None"
    try:
        if product.Header.ProductId.value() == "None":
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
            cat_filename = get_allowed_filename(type_name = "CAT", instance_id = DEFAULT_INSTANCE_ID,
                                                extension = ".csv",
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

    with open(str(qualified_xml_filename), "w") as f:
        f.write(product.toDOM().toprettyxml(encoding = "utf-8").decode("utf-8"))


@deprecated_renamed_argument("allow_pickled",
                             new_name = None,
                             since = "9.1")
def read_xml_product(xml_filename: str,
                     workdir: str = ".",
                     log_info: bool = False,
                     allow_pickled: bool = False,
                     product_type: Optional[Type] = None) -> Any:
    """Reads in an XML data product defined in the Euclid Data Model Bindings. Before calling this, it is necessary
    that the Data Model Binding class for the expected type of product be imported. It is recommended that this class
    is passed to the kwarg `product_type`, which will check that the product read-in is of this type.

    The implementation of this is copied from
    https://euclid.roe.ac.uk/projects/codeen-users/wiki/DataModelTutorial2017 with some modification.

    Parameters
    ----------
    xml_filename : str
        The fully-qualified or workdir-relative filename of the input file.
    workdir : str, default="."
        The workdir in which the file exists. If `xml_filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    allow_pickled : bool, default=False
        (Deprecated and to be removed soon; do not use)
    product_type : Optional[Type], default=None
        If not None, this function will check that the product which has been read in is of this type, and raise a
        `TypeError` if not.

    Returns
    -------
    product : product_type, or else Any if product_type is None
        An instance of the data product which was stored on disk.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_DATA_PRODUCT, xml_filename, workdir)

    # Silently coerce input into a string
    xml_filename = str(xml_filename)

    try:

        product = _read_xml_product(xml_filename, workdir)

    except NamespaceError:
        # If we hit a namespace error, it likely means the SHE_PPT.products module hasn't been imported.
        # Try importing it and reading again
        from . import products

        try:
            product = _read_xml_product(xml_filename, workdir)
        except Exception as e:
            raise SheFileReadError(filename = xml_filename, workdir = workdir) from e

    except Exception as e:
        raise SheFileReadError(filename = xml_filename, workdir = workdir) from e

    # Check the type of the read-in product if `product_type` is not None
    if (product_type is not None) and not isinstance(product, product_type):
        raise TypeError(f"Product read in from file {xml_filename} in directory {workdir} is of type "
                        f"{type(product)}, but type {product_type} was expected.")

    logger.debug(MSG_FINISHED_READING_DATA_PRODUCT, xml_filename, workdir)

    return product


def _read_xml_product(xml_filename: str, workdir: str) -> Any:
    """Private implementation of the core functionality of `read_xml_product`. See that function's documentation for
    details on functionality and parameters.
    """

    qualified_xml_filename = find_file(xml_filename, workdir)

    with open(str(qualified_xml_filename), "r") as f:
        xml_string = f.read()

    # Create a new product instance using the proper data product dictionary
    product = CreateFromDocument(xml_string)

    return product


@deprecated(since = "9.1",
            alternative = "write_xml_product")
def write_pickled_product(product,
                          pickled_filename: str,
                          workdir: str = ".",
                          log_info: bool = False) -> None:
    """This function is now deprecated and should not generally be used.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_WRITING_DATA_PRODUCT, pickled_filename, workdir)

    # Silently coerce input into a string
    pickled_filename = str(pickled_filename)

    qualified_pickled_filename = get_qualified_filename(pickled_filename, workdir)

    try:
        with open(str(qualified_pickled_filename), "wb") as f:
            pickle.dump(product, f)
    except Exception as e:
        raise SheFileWriteError(filename = pickled_filename, workdir = workdir) from e

    logger.debug(MSG_FINISHED_WRITING_DATA_PRODUCT, pickled_filename, workdir)


@deprecated(since = "9.1",
            alternative = "read_xml_product")
def read_pickled_product(pickled_filename,
                         workdir = DEFAULT_WORKDIR,
                         log_info: bool = False) -> Any:
    """This function is now deprecated and should not generally be used.
    """

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
                *args,
                workdir: str = DEFAULT_WORKDIR,
                log_info: bool = False,
                **kwargs) -> None:
    """Outputs an astropy table to a file on disk. In addition to the standard functionality provided by the table
    object's `write` method, this function handles logging, determination of qualified filename, and raising an
    exception of the common SheFileWriteError type on error.

    Parameters
    ----------
    t : astropy.table.Table
        The table to be output.
    filename : str
        The desired fully-qualified or workdir-relative filename of the output file.
    workdir : str, default="."
        The workdir in which the file should be created. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call of the table's `write` method. See that method's
        documentation for details on allowed arguments.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_WRITING_TABLE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        t.write(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileWriteError(filename = filename, workdir = workdir) from e

    logger.debug(MSG_FINISHED_WRITING_TABLE, filename, workdir)


def read_table(filename: str,
               *args,
               workdir: str = DEFAULT_WORKDIR,
               log_info: bool = False,
               **kwargs) -> Table:
    """Reads in an astropy Table stored on disk. Reads in an astropy Table file on disk. In addition to the standard
    functionality provided by the `Table.read` method, this function handles logging, determination of qualified
    filename, and raising an exception of the common SheFileReadError type on error.

    Parameters
    ----------
    filename : str
        The fully-qualified or workdir-relative filename of the input file.
    workdir : str, default="."
        The workdir in which the file exists. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call to the `astropy.table.Table.read` method. See
        that method's documentation for details on allowed arguments.

    Returns
    -------
    t : Table
        An instance of the table which was stored on disk.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_TABLE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        t: Table = Table.read(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileReadError(filename = filename, workdir = workdir) from e

    logger.debug(MSG_FINISHED_READING_TABLE, filename, workdir)

    return t


def write_product_and_table(product: Any,
                            product_filename: str,
                            table: Table,
                            *args: Any,
                            table_filename: Optional[str] = None,
                            workdir: str = DEFAULT_WORKDIR,
                            log_info: bool = False,
                            **kwargs: Any):
    """Convenience function to write a product and table at the same time, setting up a filename for the table if
    one is not provided, and setting the product to point to the table's filename with its `set_data_filename`
    method. Note that this function is not compatible with all types of data products; it requires that the product's
    binding class is set up with a `set_data_filename` which sets the workdir-relative filename of the  desired data
    table.

    Parameters
    ----------
    product : Any type of Euclid data product defined in the Data Model bindings
        The data product to be output.
    product_filename : str
        The desired fully-qualified or workdir-relative filename of the output file for the data product.
    table : astropy.table.Table
        The table to be output.
    table_filename : str
        The desired fully-qualified or workdir-relative filename of the output file for the table.
    workdir : str, default="."
        The workdir in which the files should be created. If both `product_filename` and `table_filename` are provided
        fully-qualified, it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call of the table's `write` method. See that method's
        documentation for details on allowed arguments.
    """

    # Generate a filename for the table if one hasn't been provided
    if table_filename is None:
        table_filename = get_allowed_filename(version = __version__)

    # Write the table
    write_table(table, *args, filename = table_filename, workdir = workdir, log_info = log_info, **kwargs)

    # Set the table filename within the product
    product.set_data_filename(table_filename)

    # Write the product
    write_xml_product(product, xml_filename = product_filename, workdir = workdir, log_info = log_info)


def read_product_and_table(product_filename: str,
                           *args,
                           workdir: str = DEFAULT_WORKDIR,
                           log_info: bool = False,
                           product_type: Optional[Type] = None,
                           **kwargs) -> Tuple[Any, Table]:
    """ Convenience function to read in a data product and the data table it points to, and return both as a tuple.
    Note that this function is not compatible with all types of data products; it requires that the product's binding
    class is set up with a `get_data_filename` which provides the workdir-relative filename of the desired data table.

    Parameters
    ----------
    product_filename : str
        The fully-qualified or workdir-relative filename of the input file for the data product.
    workdir : str, default="."
        The workdir in which the file exists. If `xml_filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    product_type : Optional[Type], default=None
        If not None, this function will check that the product which has been read in is of this type, and raise a
        `TypeError` if not.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call to the `astropy.table.Table.read` method. See
        that method's documentation for details on allowed arguments.

    Returns
    -------
    p : product_type, or else Any if product_type is None
        An instance of the data product which was stored on disk.
    t : Table
        An instance of the table which was stored on disk and pointed to by the data product.
    """

    p = read_xml_product(product_filename, workdir = workdir, log_info = log_info, product_type = product_type)
    table_filename: str = p.get_data_filename()

    t = read_table(table_filename, *args, workdir = workdir, log_info = log_info, **kwargs)

    return p, t


def read_table_from_product(product_filename: str,
                            *args,
                            workdir: str = DEFAULT_WORKDIR,
                            log_info: bool = False,
                            product_type: Optional[Type] = None,
                            **kwargs) -> Table:
    """Convenience function to read in a data table given the filename of the xml data product which points to it.
    Note that this function is not compatible with all types of data products; it requires that the product's binding
    class is set up with a `get_data_filename` which provides the workdir-relative filename of the desired data table.

    Parameters
    ----------
    product_filename : str
        The fully-qualified or workdir-relative filename of the input file for the data product.
    workdir : str, default="."
        The workdir in which the file exists. If `xml_filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    product_type : Optional[Type], default=None
        If not None, this function will check that the product which has been read in is of this type, and raise a
        `TypeError` if not.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call to the `astropy.table.Table.read` method. See
        that method's documentation for details on allowed arguments.

    Returns
    -------
    t : Table
        An instance of the table which was stored on disk and pointed to by the data product.
    """

    _, t = read_product_and_table(product_filename = product_filename,
                                  workdir = workdir,
                                  log_info = log_info,
                                  product_type = product_type,
                                  *args, *kwargs)

    return t


def write_fits(hdu_list: HDUList,
               filename: str,
               *args,
               workdir: str = DEFAULT_WORKDIR,
               log_info: bool = False,
               **kwargs) -> None:
    """Outputs a FITS HDUList to a file on disk. In addition to the standard functionality provided by the table
    object's `writeto` method, this function handles logging, determination of qualified filename, and raising an
    exception of the common SheFileWriteError type on error.

    Parameters
    ----------
    hdu_list : astropy.io.fits.hdu.hdulist.HDUList
        The FITS HDUList to be output
    filename : str
        The desired fully-qualified or workdir-relative filename of the output file.
    workdir : str, default="."
        The workdir in which the file should be created. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call of the HDUList's `writeto` method. See that
        method's documentation for details on allowed arguments.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_WRITING_FITS_FILE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        hdu_list.writeto(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileWriteError(filename = filename, workdir = workdir) from e
    logger.debug(MSG_FINISHED_WRITING_FITS_FILE, filename, workdir)


def read_fits(filename: str,
              *args,
              workdir: str = DEFAULT_WORKDIR,
              log_info: bool = False,
              **kwargs) -> HDUList:
    """Reads in a FITS file on disk. In addition to the standard functionality provided by the `fits.open` method,
    this function handles logging, determination of qualified filename, and raising an
    exception of the common SheFileReadError type on error.

    Parameters
    ----------
    filename : str
        The fully-qualified or workdir-relative filename of the input file.
    workdir : str, default="."
        The workdir in which the file exists. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call to the `astropy.io.fits.open` method. See
        that method's documentation for details on allowed arguments.

    Returns
    -------
    f : HDUList
        An open handle to the FITS file which is stored on disk.
    """

    log_method = _get_optional_log_method(log_info)
    log_method(MSG_READING_FITS_FILE, filename, workdir)

    qualified_filename = get_qualified_filename(filename, workdir)

    try:
        f: HDUList = fits.open(qualified_filename, *args, **kwargs)
    except Exception as e:
        raise SheFileReadError(filename = filename, workdir = workdir) from e
    logger.debug(MSG_FINISHED_READING_FITS_FILE, filename, workdir)

    return f


def read_d_l_method_table_filenames(l_product_filenames: Sequence[str],
                                    workdir: str,
                                    log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, List[str]],
                                                                     List[Any]]:
    """Read in a dict of lists of table filenames for each shear estimation method from a list of measurements product
    filenames. This function is intended for use with lists of data products which each (optionally) contain a
    data table for each shear estimation method.

    Parameters
    ----------
    l_product_filenames : Sequence[str]:
        A sequence of workdir-relative filenames, each corresponding to the location on disk of a '.xml' data product
        which contains shear estimation data.
    workdir: str
        The workdir in which the data exists.
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.

    Returns
    -------
    d_l_method_table_filenames : Dict[ShearEstimationMethods, List[str]]
        A dictionary indexed by shear estimation method to lists of workdir-relative filenames of the data tables for
        each method.
    l_products: List[Any]
        A list of the data products which have been read in.
    """

    # Init lists of filenames for each method
    d_l_method_table_filenames: Dict[ShearEstimationMethods, List[str]] = {}
    for method in ShearEstimationMethods:
        d_l_method_table_filenames[method] = []

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
                d_l_method_table_filenames[method].append(method_matched_catalog_filename)

    return d_l_method_table_filenames, l_products


def read_d_l_method_tables(l_product_filenames: Sequence[str],
                           workdir: str,
                           log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, List[Table]],
                                                            List[Any]]:
    """Read in a dict of lists of tables for each shear estimation method from a list of measurements product
    filenames. This function is intended for use with lists of data products which each (optionally) contain a
    data table for each shear estimation method.

    Parameters
    ----------
    l_product_filenames : Sequence[str]:
        A sequence of workdir-relative filenames, each corresponding to the location on disk of a '.xml' data product
        which contains shear estimation data.
    workdir: str
        The workdir in which the data exists.
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.

    Returns
    -------
    d_l_method_tables : Dict[ShearEstimationMethods, List[Table]]
        A dictionary indexed by shear estimation method to lists of data tables for each method.
    l_products: List[Any]
        A list of the data products which have been read in.
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
    """Read in a dict of table filenames for each shear estimation method from a measurements product filename. This
    function is intended for use with lists of data products which each (optionally) contain a data table for each
    shear estimation method.

    Parameters
    ----------
    product_filename : str:
        Workdir-relative filename corresponding to the location on disk of a '.xml' data product which contains shear
        estimation data.
    workdir: str
        The workdir in which the data exists.
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.

    Returns
    -------
    d_method_table_filenames : Dict[ShearEstimationMethods, str]
        A dictionary indexed by shear estimation method to filenames of data tables for each method.
    product: Any
        The data product which has been read in.
    """

    # Use the read_d_l_method_table_filenames function for reading, to share common code
    (d_l_method_table_filenames,
     l_products) = read_d_l_method_table_filenames(l_product_filenames = [product_filename],
                                                   workdir = workdir,
                                                   log_info = log_info)

    # Turn each list into a scalar, in a new dict
    d_method_table_filenames: Dict[ShearEstimationMethods, str] = {}

    for method in ShearEstimationMethods:
        l_method_table_filenames = d_l_method_table_filenames[method]
        if len(l_method_table_filenames) == 0:
            d_method_table_filenames[method] = FILENAME_NONE
        else:
            d_method_table_filenames[method] = d_l_method_table_filenames[method][0]

    product = l_products[0]

    return d_method_table_filenames, product


def read_d_method_tables(product_filename: str,
                         workdir: str,
                         log_info: bool = False) -> Tuple[Dict[ShearEstimationMethods, Optional[Table]],
                                                          Any]:
    """Read in a dict of tables for each shear estimation method from a measurements product filename. This
    function is intended for use with lists of data products which each (optionally) contain a data table for each
    shear estimation method.

    Parameters
    ----------
    product_filename : str:
        Workdir-relative filename corresponding to the location on disk of a '.xml' data product which contains shear
        estimation data.
    workdir: str
        The workdir in which the data exists.
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.

    Returns
    -------
    d_method_tables : Dict[ShearEstimationMethods, Optional[Table]]
        A dictionary indexed by shear estimation method to a data table for each method. Will be indexed to `None` if no
        table is present in the data table for a given method
    product: Any
        The data product which has been read in.
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
            d_method_tables[method] = read_table(d_l_method_table_filenames[method][0], workdir = workdir)

    product = l_products[0]

    return d_method_tables, product


def append_hdu(filename: str,
               hdu: ExtensionHDU,
               *args,
               workdir: str = DEFAULT_WORKDIR,
               log_info: bool = False,
               **kwargs) -> None:
    """Appends an HDU to a FITS file on disk. In addition to the standard functionality provided by the HDUList
    object's `append` method, this function handles logging, determination of qualified filename, and raising an
    exception of the common SheFileWriteError type on error.

    Parameters
    ----------
    filename : str
        The fully-qualified or workdir-relative filename of the '.fits' file to append the HDU to.
    hdu : astropy.io.fits.hdu.base.ExtensionHDU
        The HDU to be appended to the '.fits' file.
    workdir : str, default="."
        The workdir in which the file should be created. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    log_info : bool, default=False
        If True, all logging will be at the INFO level, otherwise some will be at the DEBUG level.
    *args, **kwargs : Any
        Any additional args and kwargs will be forwarded to the call of the `fits.open` method. See that
        method's documentation for details on allowed arguments.
    """

    log_method = _get_optional_log_method(log_info)
    log_method("Appending HDU to file %s in workdir %s", filename, workdir)

    qualified_filename = get_qualified_filename(filename = filename,
                                                workdir = workdir)

    try:
        f = fits.open(qualified_filename, 'append', *args, **kwargs)
    except Exception as e:
        # If we can open in read-only, raise a SheFileWriteError, otherwise raise a SheFileReadError
        try:
            f2 = fits.open(qualified_filename, 'readonly', *args, **kwargs)
            f2.close()
            raise SheFileWriteError(filename = filename, workdir = workdir) from e
        except Exception as e2:
            # Re-raise if this was caught from the try block above
            if isinstance(e2, SheFileWriteError):
                raise
            raise SheFileReadError(filename = filename, workdir = workdir) from e

    f.append(hdu)
    f.close()

    logger.debug("Finished appending HDU to file %s in workdir %s", filename, workdir)


def try_remove_file(filename: str,
                    workdir: str = DEFAULT_WORKDIR,
                    warn: bool = False):
    """Attempts to remove a file, but passes if any exception is raised (optionally raising a warning).

    Parameters
    ----------
    filename : str
        The fully-qualified or workdir-relative filename of the file to be removed.
    workdir : str, default="."
        The workdir in which the file exists. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    warn : bool
        If True, will log a warning if anything goes wrong while trying to remove the file.
    """
    try:
        qualified_filename = get_qualified_filename(filename, workdir = workdir)
        os.remove(os.path.join(qualified_filename))
    except IOError:
        if warn:
            logger.warning("Unable to delete file %s in workdir %s", filename, workdir)


def safe_copy(qualified_src_filename: str,
              qualified_dest_filename: str,
              require_src_exist: bool = False,
              require_dest_free: bool = False) -> None:
    """Copy a file, without raising an exception if the source doesn't exist or destination does,
    and making necessary directories.

    Parameters
    ----------
    qualified_src_filename : str
        The fully-qualified path of the file to be copied.
    qualified_dest_filename : str
        The fully-qualified path of where the file at qualified_src_filename should be copied to.
    require_src_exist : bool, default=False
        If True, will raise an exception if the source file does not exist.
    require_dest_free : bool, default=False
        If True, will raise an exception if the destination file already exists.
    """

    # Check if the file already exists, and optionally skip if it does
    if os.path.exists(qualified_dest_filename):

        # Raise an exception if we require that the destination is free
        if require_dest_free:
            raise SheFileWriteError(qualified_filename = qualified_dest_filename,
                                    message = MSG_DEST_EXIST % qualified_dest_filename)

        # We don't require that it's free, so just note in debug log and return
        logger.debug(MSG_DEST_EXIST, qualified_dest_filename)

        return

    # Check if the source file exists, and optionally skip if it doesn't
    if not os.path.exists(qualified_src_filename):

        # Raise an exception if we require that the file exists
        if require_src_exist:
            raise SheFileReadError(qualified_filename = qualified_src_filename,
                                   message = MSG_SRC_NOT_EXIST % qualified_src_filename)

        # We don't require that it exists, so just note in debug log and return
        logger.debug(MSG_SRC_NOT_EXIST, qualified_src_filename)

        return

    # Make the containing directory for the file
    os.makedirs(os.path.split(qualified_dest_filename)[0], exist_ok = True)

    # Now that we know it's safe, copy the file
    shutil.copy(qualified_src_filename, qualified_dest_filename)


def copy_product_between_dirs(product_filename: str,
                              src_dir: str,
                              dest_dir: str,
                              require_all_src_datafiles_exist: bool = False,
                              require_all_dest_datafiles_free: bool = False) -> str:
    """Copies a data product and all files it points to from one directory to another

    Parameters
    ----------
    product_filename : str
        The fully-qualified path of the file to be copied.
    src_dir : str
        The path to the source directory, where the product already resides.
    dest_dir : str
        The path to the target directory, where the product should be copied to.
    require_all_src_datafiles_exist : bool, default=False
        If True, will raise an exception if any datafile pointed to by the product does not exist.
    require_all_dest_datafiles_free : bool, default=False
        If True, will raise an exception if any datafile pointed to by the product already exists in the target
        location.

    Returns
    -------
    qualified_copied_product_filename : str
        The fully-qualified path of the new location of the product that was copied.
    """

    # Ensure a data subdirectory exists in the tmpdir
    os.makedirs(os.path.join(dest_dir, DATA_SUBDIR), exist_ok = True)

    # Copy the product itself
    qualified_product_filename = os.path.join(src_dir, product_filename)
    qualified_copied_product_filename = os.path.join(dest_dir, product_filename)

    safe_copy(qualified_src_filename = qualified_product_filename,
              qualified_dest_filename = qualified_copied_product_filename,
              require_src_exist = True)

    # Read in the product and get all filenames
    p = read_xml_product(product_filename, workdir = src_dir)
    l_filenames = p.get_all_filenames()

    for filename in l_filenames:

        if is_any_type_of_none(filename):
            continue

        # Copy each file pointed to by this product
        qualified_filename = os.path.join(src_dir, filename)
        qualified_copied_filename = os.path.join(dest_dir, filename)

        safe_copy(qualified_src_filename = qualified_filename,
                  qualified_dest_filename = qualified_copied_filename,
                  require_src_exist = require_all_src_datafiles_exist,
                  require_dest_free = require_all_dest_datafiles_free)

    return qualified_copied_product_filename


def copy_listfile_between_dirs(listfile_filename: str,
                               src_dir: str,
                               dest_dir: str,
                               require_all_datafiles_exist: bool = False,
                               require_all_dest_datafiles_free: bool = False) -> str:
    """Copies a listfile, all products it points to, and all datafiles those products point to, from one directory
    to another.

    Parameters
    ----------
    listfile_filename : str
        The fully-qualified path of the listfile to be copied.
    src_dir : str
        The path to the source directory, where the listfile already resides.
    dest_dir : str
        The path to the target directory, where the listfile should be copied to.
    require_all_datafiles_exist : bool, default=False
        If True, will raise an exception if any datafile pointed to by any product in the listfile does not
        exist.
    require_all_dest_datafiles_free : bool, default=False
        If True, will raise an exception if any datafile pointed to by the product already exists in the target
        location.

    Returns
    -------
    qualified_copied_listfile_filename : str
        The fully-qualified path of the new location of the listfile that was copied.
    """

    # Copy the listfile itself
    qualified_listfile_filename = os.path.join(src_dir, listfile_filename)
    qualified_copied_listfile_filename = os.path.join(dest_dir, listfile_filename)

    safe_copy(qualified_src_filename = qualified_listfile_filename,
              qualified_dest_filename = qualified_copied_listfile_filename,
              require_src_exist = True)

    # Read in the list of products
    l_product_filenames = read_listfile(qualified_listfile_filename)

    for product_filename in l_product_filenames:
        copy_product_between_dirs(product_filename = product_filename,
                                  src_dir = src_dir,
                                  dest_dir = dest_dir,
                                  require_all_src_datafiles_exist = require_all_datafiles_exist,
                                  require_all_dest_datafiles_free = require_all_dest_datafiles_free)

    return qualified_copied_listfile_filename


def find_file_in_path(filename: str, path: str) -> str:
    """Searches through a colon-separated path for a file and returns the qualified name of it if found,
    or raises a RuntimeError otherwise. The first instance of the file in the provided path is always returned in
    case of multiple instances.

    Parameters
    ----------
    filename : str
        The path-relative filename to be searched for.
    path : str
        A colon-separated list of directories to search for the file in.

    Returns
    -------
    qualified_filename : str
        The fully-qualified location of the filename which has been found.
    """

    logger.debug("Searching for file %s in path %s", filename, path)

    colon_separated_path = path.split(":")

    for test_path in colon_separated_path:

        qualified_filename = join(test_path, filename)

        if exists(qualified_filename):
            break

    else:
        raise RuntimeError(
            "File " + str(filename) + " could not be found in path " + str(path) + ".")

    logger.debug("Found file %s at %s", filename, qualified_filename)

    return qualified_filename


def find_aux_file(filename) -> str:
    """Searches the auxiliary directory path for a file and returns a qualified name of it if found,
    or raises a RuntimeError otherwise. The first instance of the file in the provided path is always returned in
    case of multiple instances.

    Parameters
    ----------
    filename : str
        The path-relative filename to be searched for.

    Returns
    -------
    qualified_filename : str
        The fully-qualified location of the filename which has been found.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_AUX_PATH'])


def find_conf_file(filename) -> str:
    """Searches the conf directory path for a file and returns a qualified name of it if found,
    or raises a RuntimeError otherwise. The first instance of the file in the provided path is always returned in
    case of multiple instances.

    Parameters
    ----------
    filename : str
        The path-relative filename to be searched for.

    Returns
    -------
    qualified_filename : str
        The fully-qualified location of the filename which has been found.
    """

    return find_file_in_path(filename, os.environ['ELEMENTS_CONF_PATH'])


S_NON_FILENAMES = {None, FILENAME_NONE, f"{DATA_SUBDIR}{FILENAME_NONE}", "", DATA_SUBDIR}


def filename_not_exists(filename: Optional[str]):
    """Check if a filename is one of several possible values indicating that no such file exists.

    Parameters
    ----------
    filename : Optional[str]
        The filename to check

    Returns
    -------
    bool
        True if the filename is a value indicating the file does not exist; False otherwise
    """
    return filename in S_NON_FILENAMES


def filename_exists(filename: Optional[str]) -> bool:
    """Check if a filename is not one of several possible values indicating that no such file exists.

    Parameters
    ----------
    filename : Optional[str]
        The filename to check

    Returns
    -------
    bool
        False if the filename is a value indicating the file does not exist; True otherwise
    """
    return not filename_not_exists(filename)


def find_web_file(filename: str) -> str:
    """Searches on WebDAV for a file. If found, downloads it and returns the qualified name of it. If
    it's an xml data product or listfile, will also download all associated files. If it isn't found,
    raises a `ElementsServices.DataSync.DataSynchronizer.DownloadFailed` exception.

    IMPORTANT: This function should be used with care. In production, there won't be internet access, so this will
    fail for that reason. And for testing, it is preferred to use the common DataSync class to download test data.

    Parameters
    ----------
    filename : str
        The name of the file to retrieve from WebDAV, relative to the PF-SHE directory on it.

    Returns
    -------
    qualified_filename : str
        The fully-qualified path to where the file exists after download.
    """

    file_list_name: str = os.path.join(os.getcwd(),
                                       os.path.splitext(os.path.split(filename)[-1])[0] + f"{os.getpid()}_list.txt")

    try:
        # We need a listfile to pass to the DataSync, so create one listing only this one filename
        with open(file_list_name, "w") as fo:
            fo.write(filename + "\n")

        sync = DataSync(SYNC_CONF, file_list_name)
        sync.download()

        qualified_filename: str = sync.absolutePath(filename)
    except DownloadFailed:
        # Cleanup any attempt to create the file if the download failed
        try_remove_file(os.path.join(TEST_DATADIR, filename))
        raise
    finally:
        # Cleanup the created listfile on either success or failure
        if os.path.exists(file_list_name):
            logger.debug("Cleaning up %s", file_list_name)
            try_remove_file(file_list_name)

    # If it's an xml data product, we'll also need to download all files it points to
    if filename[-4:] == ".xml":

        _find_web_file_xml(filename, qualified_filename)

    # If it's json listfile, we'll also need to download all files it points to
    elif filename[-5:] == ".json":

        _find_web_file_json(filename, qualified_filename)

    return qualified_filename


def _find_web_file_xml(filename: str, qualified_filename: str) -> str:
    """Private implementation of part of find_web_file, handling downloading data files pointed to by a downloaded
    data product.
    """

    webpath: str = os.path.split(filename)[0]

    try:
        p = read_xml_product(qualified_filename, workdir = "")
        for subfilename in p.get_all_filenames():
            # Skip if there's no file to download
            if not filename_exists(subfilename):
                continue
            find_web_file(os.path.join(webpath, subfilename))
    except SheFileReadError as e:
        # MDB files end in XML but can't be read this way, and will raise this exception, so silently pass in that case
        if "elementBinding" not in str(e.__cause__):
            raise

    return webpath


def _find_web_file_json(filename: str, qualified_filename: str) -> None:
    """Private implementation of part of find_web_file, handling downloading data products pointed to by a downloaded
    listfile.
    """

    webpath: str = os.path.split(filename)[0]

    l_filenames = read_listfile(qualified_filename)
    for element in l_filenames:
        if isinstance(element, str):
            # Skip if there's no file to download
            if not filename_exists(element):
                continue
            find_web_file(os.path.join(webpath, element))
        else:
            for sub_element in element:
                # Skip if there's no file to download
                if not filename_exists(sub_element):
                    continue
                find_web_file(os.path.join(webpath, sub_element))


def find_file(filename: str, path: Optional[str] = None) -> str:
    """Locates a file based on the presence/absence of an 'AUX/', 'CONF/', 'WEB/', or 'HOME/' prefix, searching in the
    aux, conf, WebDAV, or home directories respectively for it, or else the provided path if one is supplied.

    Parameters
    ----------
    filename : str
        The name of the file to search for.
    path : Optional[str]
        The path to search for the file in, if the filename does not start with either the 'AUX/', 'CONF/',
        'WEB/', or 'HOME/' prefixes.

    Returns
    -------
    qualified_filename : str
        The fully-qualified path to the located file.
    """

    logger.debug("Finding file %s, with path %s", filename, path)

    # Silently coerce input into a string
    filename = str(filename)
    qualified_filename: Optional[str]

    # Delegate to the appropriate method based on the prefix of the filename
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
        # The file appears to already be fully-qualified, so check if it exists
        if not os.path.exists(filename):
            raise RuntimeError("File " + filename + " cannot be found.")
        qualified_filename = filename
    elif path is not None:
        qualified_filename = find_file_in_path(filename, path)
    else:
        raise ValueError("path must be supplied if filename doesn't start with 'AUX/', 'CONF/', 'WEB/', or 'HOME/'.")

    return qualified_filename


def first_in_path(path: str) -> str:
    """ Gets the first directory listed in the provided path string.

    Parameters
    ----------
    path : str
        Colon-separated list of directories.

    Returns
    -------
    str
        The first directory in the provided path.
    """

    return path.split(":")[0]


def first_writable_in_path(path: str) -> str:
    """ Gets the first directory listed in the provided path string which we have write access for. Raises an
    IOError if no directory in the path is writable

    Parameters
    ----------
    path : str
        Colon-separated list of directories.

    Returns
    -------
    str
        The first directory in the provided path which we have write access for.
    """

    colon_separated_path = path.split(":")

    for test_path in colon_separated_path:

        if os.access(test_path, os.W_OK):
            first_writable_dir = test_path
            break
    else:
        raise IOError(f"In call to `first_writable_in_path`, no directory in path {path} is writable.")

    return first_writable_dir


def get_data_filename(filename: str, workdir: str = DEFAULT_WORKDIR) -> Optional[str]:
    """Given the unqualified name of a file and the work directory, determine if it's an XML data
    product or not, and get the filename of its DataContainer if so; otherwise, just return
    the input filename. In either case, the unqualified filename is returned.

    This script is intended to help smooth the transition from using raw data files as
    input/output to data products.

    Parameters
    ----------
    filename : str
        The fully-qualified or workdir-relative filename of the file to get the data filename for.
    workdir : str, default="."
        The workdir in which the file exists. If `filename` is provided fully-qualified, or if it starts with a
        prefix indicating it should be found in the auxdir or elsewhere, it is not necessary for this to be provided
        (and it will be ignored if it is).

    Returns
    -------
    data_filename : Optional[str]
        The workdir-relative name of the data file. Note that this may be one of several values which indicates that
        no such file exists, such as the string "None". This can be checked for through use of the
        `filename_not_exists` function.
    """

    # First, see if we can open this as an XML data product
    try:
        qualified_filename = find_file(filename, workdir)

        prod = read_xml_product(qualified_filename)

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
                                     "location (`self.Data.DataStorage.DataContainer.FileName`. " +
                                     "In order to use `get_data_filename` with this product, the " +
                                     "product's class must be monkey-patched to have a `get_filename` " +
                                     "or `get_data_filename` method.")

    except SheFileReadError:
        # Not an XML file - so presumably it's a raw data file; return the
        # input filename
        data_filename = filename

    return data_filename


def update_xml_with_value(filename: str) -> None:
    r"""Updates xml files with value. Checks for <Key><\Key> not followed by <Value><\Value>.

    This function is provided for manual use in fixing .xml files, and should not
    be used in production code.
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
            new_line = lines[idx + ii].split(STR_KEY)[0] + '<Value>NULL</Value>\n'
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


def remove_files(l_qualified_filenames: Sequence[str]) -> None:
    """Loop through and try to remove all files in a list. No exception is raised if the files can't be removed,
    but a warning is logged.

    Parameters
    ----------
    l_qualified_filenames : Sequence[str]
        A sequence of fully-qualified filenames of files to be removed.
    """

    for qualified_filename in l_qualified_filenames:
        try:
            os.remove(qualified_filename)
        except IOError:
            # Don't need to fail the whole process, but log the issue
            logger.warning("Cannot delete file: %s", qualified_filename)


def tar_files(tarball_filename: str,
              l_filenames: Sequence[str],
              workdir: str = DEFAULT_WORKDIR,
              delete_files: bool = False):
    """Create a tarball containing all files in the provided list of filenames.

    Parameters
    ----------
    tarball_filename : str
        The desired fully-qualified or workdir-relative filename of the tarball to be created.
    l_filenames : Sequence[str]
        A sequence of workdir-relative filenames to be put into the tarball.
    workdir : str, default="."
        The workdir in which the file exists. If `filename` is provided fully-qualified,
        it is not necessary for this to be provided (and it will be ignored if it is).
    delete_files : bool, default=False
        If True, all files in `l_filenames` will be deleted after being put into the tarball
    """

    qualified_tarball_filename: str = get_qualified_filename(tarball_filename, workdir)

    filename_string = " ".join(l_filenames)

    # Tar the files and fully log the process
    logger.info("Creating tarball %s", qualified_tarball_filename)

    tar_cmd = f"cd {workdir} && tar -cf {qualified_tarball_filename} {filename_string}"
    tar_results = subprocess.run(tar_cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    logger.info("tar stdout: %s", tar_results.stdout)
    logger.debug("tar stderr: %s", tar_results.stderr)

    # Check that the tar process succeeded
    if not os.path.isfile(qualified_tarball_filename):
        base_error = FileNotFoundError(f"{qualified_tarball_filename} not found. "
                                       f"stderr from tar process was: \n"
                                       f"{tar_results.stderr}")
        raise SheFileWriteError(filename = tarball_filename, workdir = workdir) from base_error
    if tar_results.returncode:
        base_error = ValueError(f"Tarring of {qualified_tarball_filename} failed. stderr from tar process was: \n"
                                f"{tar_results.stderr}")
        raise SheFileWriteError(filename = tarball_filename, workdir = workdir) from base_error

    # Delete the files if desired
    if delete_files:
        l_qualified_filenames = [get_qualified_filename(filename, workdir) for filename in l_filenames]
        remove_files(l_qualified_filenames)


T = TypeVar('T')


class FileLoader(abc.ABC, Generic[T]):
    """ Abstract base class for loading in a data from the work directory. Instances of this class serve as a "hook"
    to allow data to be loaded on-demand at some point in the future, using a consistent interface which doesn't
    depend on the file type.

    Attributes
    ----------
    filename : str
        The workdir-relative filename of the file from which data is to be loaded.
    qualified_filename : str
        The fully-qualified filename of the file from which data is to be loaded.
    workdir : str
        The workdir in which resides the file from which data is to be loaded.
    object, obj : Optional[T]
        If loaded, the data which has been loaded in; otherwise `None`.
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
        """Initializes an instance of a `FileLoader` object.

        Parameters
        ----------
        filename : str
            The workdir-relative filename of the file from which data is to be loaded.
        workdir : str
            The workdir in which resides the file from which data is to be loaded.
        """

        self.filename = filename
        self.workdir = workdir

    @property
    def filename(self) -> str:
        """The workdir-relative filename of the file from which data is to be loaded.
        """
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._qualified_filename = None
        self._filename = filename

    @property
    def workdir(self) -> str:
        """The workdir in which resides the file from which data is to be loaded.
        """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: str):
        self._qualified_filename = None
        self._workdir = workdir

    @property
    def qualified_filename(self) -> str:
        """The fully-qualified filename of the file from which data is to be loaded.
        """
        if not self._qualified_filename:
            self._qualified_filename = get_qualified_filename(self.filename, self.workdir)
        return self._qualified_filename

    @property
    def object(self) -> Optional[T]:
        """If loaded, the data which has been loaded in; otherwise `None`.
        """
        return self._obj

    @property
    def obj(self) -> Optional[T]:
        """Alias to `object`
        """
        return self._obj

    def load(self, *args, **kwargs) -> None:
        """Load in the object, making it accessible via the `object` property.

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the appropriate method to load in the object.
        """
        self._obj = self.get(*args, **kwargs)

    def open(self, *args, **kwargs) -> None:
        """ Alias to `load`.
        """
        self.load(*args, **kwargs)

    def close(self) -> None:
        """ Deletes the reference to the object to allow memory to be freed. Can be overridden/inherit to explicitly
        close file handles for certain file types.
        """
        self._obj = None

    @abc.abstractmethod
    def get(self, *args, **kwargs) -> T:
        """Abstract method to get and return the object.  Should take a format such as:
        ```
        return load_object(filename=self.filename, workdir=self.workdir, *args, **kwargs)
        ```

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the appropriate method to load in the object.

        Returns
        -------
        T
            The loaded-in object.
        """


class ProductLoader(FileLoader):
    """`FileLoader` specialized to load in `.xml` data products.
    """

    def get(self, *args, **kwargs) -> Any:
        """Method to get and return the data product.

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the method to load in the data product.

        Returns
        -------
        Any
            The loaded-in data product.
        """
        return read_xml_product(xml_filename = self.filename, workdir = self.workdir, *args, **kwargs)


class TableLoader(FileLoader[Table]):
    """`FileLoader` specialized to load in `astropy` data tables.
    """

    def get(self, *args, **kwargs) -> Table:
        """Method to get and return the table.

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the method to load in the table.

        Returns
        -------
        Table
            The loaded-in table.
        """
        return read_table(self.filename, *args, workdir = self.workdir, *args, **kwargs)


class FitsLoader(FileLoader[HDUList]):
    """`FileLoader` specialized to load in `FITS` files via `astropy`.
    """

    def get(self, *args, **kwargs) -> HDUList:
        """Method to open and return the `FITS` file's `HDUList`.

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the method to open the `FITS` file.

        Returns
        -------
        HDUList
            The HDUList for the opened `FITS` file.
        """
        return read_fits(filename = self.filename, *args, workdir = self.workdir, *args, **kwargs)

    def close(self):
        """Inherit parent `close` method to also close the file handle.
        """

        if self.object:
            self.object.flush()
            self.object.close()
        super().close()


class MultiFileLoader(Generic[T]):
    """A class to handle loading in multiple files - similar to `FileLoader` (and in fact wrapping
    it), but for lists of files rather than single files.

    Attributes
    ----------
    workdir : str
        The workdir in which resides the files from which data is to be loaded.
    l_filenames : str
        The workdir-relative filenames of the files from which data is to be loaded.
    l_file_loaders : Sequence[FileLoader[T]]
        The `FileLoader` objects used to load in the data from each file.
    file_loader_type : Optional[Type[FileLoader[T]]]
        The type of `FileLoader` used to load all files if specified or determined at init, or else `None`
    """

    # Attributes set at init
    workdir: str
    l_filenames: Sequence[str]
    l_file_loaders: Sequence[FileLoader[T]]
    file_loader_type: Optional[Type[FileLoader[T]]] = None

    def __init__(self,
                 workdir: str,
                 l_file_loaders: Optional[Sequence[FileLoader[T]]] = None,
                 l_filenames: Optional[Sequence[str]] = None,
                 file_loader_type: Optional[Type[FileLoader[T]]] = None) -> None:
        """Initializes an instance of a `MultiFileLoader` object.

        Parameters
        ----------
        workdir : str
            The workdir in which resides the file from which data is to be loaded.
        l_file_loaders : Optional[Sequence[FileLoader[T]]], default=None
            A sequence of `FileLoader` objects to be used for loading data when requested. Cannot be provided
            alongside `l_filenames`.
        l_filenames : Optional[Sequence[str]], default=None
            A sequence of filenames for which `FileLoader` objects should be created. Cannot be provided alongside
            `l_file_loaders`, and must have `file_loader_type` provided if used.
        file_loader_type : Optional[Type[FileLoader[T]]], default=None
            The type of `FileLoader` to be used. Must be provided if `l_filenames` is provided.
        """

        self.workdir = workdir

        if file_loader_type:
            self.file_loader_type = file_loader_type

        if l_file_loaders:

            if l_filenames:
                raise ValueError("MultiFileLoader can be inited with only one of `l_file_loaders` and `l_filenames`.")
            self.l_file_loaders = l_file_loaders
            self.l_filenames = [file_loader.filename for file_loader in self.l_file_loaders]

            file_loader_type_in_list = type(self.l_file_loaders[0])
            if file_loader_type and file_loader_type != file_loader_type_in_list:
                raise TypeError(f"Type of `FileLoader` in `l_file_loaders` does not match `file_loader_type`: "
                                f"{file_loader_type=}, {file_loader_type_in_list=}")
            self.file_loader_type = file_loader_type_in_list

        elif l_filenames:
            if not file_loader_type:
                raise ValueError("`file_loader_type` must be specified when initializing a `MultiFileLoader` object "
                                 f"with a list of filenames: {l_filenames=}, {file_loader_type=}")
            self.l_filenames = l_filenames
            self.l_file_loaders = [self.file_loader_type(filename = filename, workdir = self.workdir) for
                                   filename in self.l_filenames]

        else:
            self.l_file_loaders = []
            self.l_filenames = []

    def load_all(self, *args, **kwargs):
        """Load all files.

        Parameters
        ----------
        *args, **kwargs : Any
            Any arguments passed to this will be forwarded to the appropriate method to load in the objects.
        """
        for file_loader in self.l_file_loaders:
            file_loader.load(*args, **kwargs)

    def open_all(self, *args, **kwargs):
        """Alias to load_all.
        """
        self.load_all(*args, **kwargs)

    def close_all(self):
        """Deletes the references to the objects to allow memory to be freed and file handles to be closed.
        """
        for file_loader in self.l_file_loaders:
            file_loader.close()

    def get_all(self, *args, **kwargs) -> List[T]:
        """Get a list of all files (load and return, but don't keep a reference within this object).

        Returns
        -------
        List[T]
            A list of loaded-in objects.
        """
        return [file_loader.get(*args, **kwargs) for file_loader in self.l_file_loaders]


class MultiProductLoader(MultiFileLoader):
    """A class to handle loading in multiple xml data products.
    """

    file_loader_type: Type[FileLoader] = ProductLoader


class MultiTableLoader(MultiFileLoader):
    """A class to handle loading in multiple xml data products.
    """

    file_loader_type: Type[FileLoader] = TableLoader


class MultiFitsLoader(MultiFileLoader):
    """A class to handle loading in multiple `FITS` files.
    """

    file_loader_type: Type[FileLoader] = FitsLoader
