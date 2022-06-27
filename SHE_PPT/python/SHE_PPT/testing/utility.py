""" @file testing/utility.py

    Created 29 Oct 2021

    Utility classes and functions for unit testing
"""

__updated__ = "2022-06-27"

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

import os
from argparse import Namespace
from typing import Any, Dict, Optional

import pytest
from py._path.local import LocalPath

from ElementsServices.DataSync import DataSync
from SHE_PPT import mdb
from SHE_PPT.argument_parser import CA_LOGDIR, CA_PIPELINE_CONFIG, CA_WORKDIR
from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME, SYNC_CONF,
                                         TEST_DATA_LOCATION,
                                         TEST_FILES_DATA_STACK, TEST_FILES_MDB,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.file_io import symlink_contents
from SHE_PPT.logging import set_log_level_debug
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory

ENVVAR_WORKSPACE = "WORKSPACE"

MSG_CANT_FIND_FILE = "Cannot find file: %s"


class SheTestCase:
    """ Base class for test cases, which provides various utility methods.
    """

    _args: Optional[Namespace] = None
    _d_args: Optional[Dict[str, Any]] = None

    download_dir: Optional[str] = None
    workdir: Optional[str] = None
    logdir: Optional[str] = None

    mdb_filename: Optional[str] = None

    data_stack: Optional[SHEFrameStack] = None

    pipeline_config: Optional[Dict[ConfigKeys, Any]] = None

    pipeline_config_factory_type = MockPipelineConfigFactory
    mock_pipeline_config_factory: Optional[MockPipelineConfigFactory] = None

    tmpdir_factory = None

    # Properties

    @property
    def args(self) -> Namespace:
        """ A Namespace object which can be passed to tested functions which normally used the args Namespace
            returned from parse_args(). For subclasses, this should be set up by overriding the _make_mock_args
            method to generate a Namespace object with the expected attributes for the executable in which the
            function is run.
        """
        if self._args is None:
            self._args = self._make_mock_args()
        return self._args

    @args.setter
    def args(self, args: Namespace) -> None:
        self._args = args

    @property
    def d_args(self) -> Dict[str, Any]:
        """ Similar to the args attribute, except converted to a Dict. This is used for any functions which
            normally take such an object. The Dict form is preferred when command-line arguments are set using
            constant variables, as it provides a cleaner interface to access these them, using d_args[key] instead of
            getattr(args, key).
        """
        if self._d_args is None:
            self._d_args = vars(self.args)
        return self._d_args

    # Class methods

    @classmethod
    def teardown_class(cls):
        """ Delete the pipeline config if it's been created.
        """
        if cls.mock_pipeline_config_factory:
            cls.mock_pipeline_config_factory.cleanup()

    # Overridable methods to setup/teardown for tests

    def setup_workdir(self) -> None:
        """Overridable method, where the user can specify any unique setup for a given testing class, to be performed
           before the workdir is setup. This is normally used when it's needed to download test data, which will set
           the self.workdir member to the location of the workdir.
        """
        return None

    def post_setup(self) -> None:
        """Overridable method, where the user can specify any unique setup for a given testing class, to be performed
           after the workdir is setup.
        """
        return None

    def teardown(self) -> None:
        """Overridable method, where the user can specify any commands to be run at the end of any tests.
        """
        return None

    # Protected methods

    def _make_mock_args(self) -> Namespace:
        """Overridable method to create a mock self.args Namespace. Not necessary to implement if no args are used.
        """
        return Namespace()

    # Protected convenience methods for downloading data

    def _download_mdb(self):
        """ Download the test MDB from WebDAV.
        """
        sync = DataSync(SYNC_CONF, TEST_FILES_MDB)
        sync.download()
        self.mdb_filename = MDB_PRODUCT_FILENAME

        self._finalize_download(self.mdb_filename, sync)

        mdb.init(os.path.join(self.download_dir, self.mdb_filename))

    def _download_datastack(self,
                            read_in: bool = True, ):
        """ Download the test data stack from WebDAV.
        """
        sync = DataSync(SYNC_CONF, TEST_FILES_DATA_STACK)
        sync.download()

        self._finalize_download(VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, sync)

        # Read in the test data if desired
        if read_in:
            self.data_stack = SHEFrameStack.read(exposure_listfile_filename = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                                 detections_listfile_filename = MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                                 workdir = self.download_dir,
                                                 clean_detections = False,
                                                 memmap = True,
                                                 mode = 'denywrite')

    def _finalize_download(self,
                           filename: str,
                           sync_mdb: DataSync):
        """ Check that the desired file has been downloaded successfully and set the workdir based on its location.
        """

        # Check that the file was downloaded successfully
        qualified_filename = sync_mdb.absolutePath(os.path.join(TEST_DATA_LOCATION, filename))
        assert os.path.isfile(qualified_filename), MSG_CANT_FIND_FILE % qualified_filename

        # Set the download_dir if it's not already set
        if self.download_dir is None:
            self.download_dir = os.path.split(qualified_filename)[0]

    # Fixtures used in setup. These can be used as arguments for new fixtures to control when they're created.

    @pytest.fixture(scope = 'class')
    def class_setup(self, tmpdir_factory):
        """ This performs setup once per initialization of the test class, calling the overridable setup_workdir and
            post_setup methods.
        """

        # Call initialisation tasks first
        self.__init()

        # Call to overridable `setup_workdir` method
        self.setup_workdir()

        # Internal setup using the state of the class at the end of the `setup_workdir` method.
        self.tmpdir_factory = tmpdir_factory
        self.__setup()

        # Call to overridable `post_setup` method
        self.post_setup()

        return self

    @pytest.fixture(autouse = True)
    def local_setup(self, class_setup):
        """ Import all changes made to this class in the class_setup locally. This gets around the fact that normally,
            after executing class-level fixtures, PyTest resets the state of the class. So if we want to retain changes
            made in our class-level setup, we have to return the results of them as a fixture, then copy over the
            modifications.
        """
        for x in dir(class_setup):
            # Skip any private attributes, which always start with "__"
            if len(x) < 2 or x[0:2] != "__":
                try:
                    setattr(self, x, getattr(class_setup, x))
                except AttributeError:
                    # Silently pass for any attributes we can't set, which can happen if properties are defined without
                    # a setter, for instance. In those cases, the protected attributes storing data will be copied
                    # instead.
                    pass

        return self

    # Private methods

    def __init(self):
        """Run initialization tasks at the very beginning of tests.
        """

        # Set log level to debug to make sure there aren't any issues with logging strings
        set_log_level_debug()

        # Make sure the "WORKSPACE" envvar is set to be unique to this user, if it's not already set
        if ENVVAR_WORKSPACE not in os.environ or os.environ[ENVVAR_WORKSPACE] == "":
            os.environ[ENVVAR_WORKSPACE] = os.path.join("/tmp", os.environ["USER"])

    def __setup_workdir_from_tmpdir(self, tmpdir: LocalPath):
        """ Sets up workdir and logdir based on a tmpdir fixture.
        """

        # Set the workdir to the tmpdir provided by the factory
        self.workdir = tmpdir.strpath

        # If any data was downloaded, symlink it to the workdir
        if self.download_dir is not None:
            symlink_contents(self.download_dir, self.workdir)

        self.__setup_workdir()

    def __setup_workdir(self):
        """ Sets up self.logdir and the expected subdirs of the workdir if they don't already exist.
        """
        self.logdir = os.path.join(self.workdir, "logs")
        os.makedirs(os.path.join(self.workdir, "logs"), exist_ok = True)
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok = True)

    def __set_workdir_args(self) -> None:
        """ Set the workdir and logdir in the self.args attribute. Both must already be set for this object when this
            method is called.
        """
        setattr(self.args, CA_WORKDIR, self.workdir)
        setattr(self.args, CA_LOGDIR, self.logdir)

    def __write_mock_pipeline_config(self):
        """ Write the pipeline config we'll be using and note its filename. This uses the class member
            pipeline_config_factory_type to construct the pipeline_config if it doesn't already exist, and thus
            modifying that variable in subclasses will modify the pipeline_config created here.
        """

        # Don't overwrite if a config is already set up to use
        if self.pipeline_config is not None:
            return

        self.mock_pipeline_config_factory = self.pipeline_config_factory_type(workdir = self.workdir)
        self.mock_pipeline_config_factory.write(self.workdir)
        self.pipeline_config = self.mock_pipeline_config_factory.pipeline_config

        setattr(self.args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.file_namer.filename)

    def __setup(self):
        """ Implements common setup tasks. These include ensuring the workdir is set up, setting the workdir-related
            arguments to self.args, and creating a mock pipeline_config.
        """
        self.__setup_workdir_from_tmpdir(self.tmpdir_factory.mktemp("test"))
        self.__set_workdir_args()
        self.__write_mock_pipeline_config()

    @pytest.fixture(scope = "session", autouse = True)
    def _teardown(self, request):
        """Method set up to be run at session-level, to define the `teardown` method to be run at end of all tests.
        """

        request.addfinalizer(self.teardown)
