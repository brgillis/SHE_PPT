""" @file testing/utility.py

    Created 29 Oct 2021

    Utility classes and functions for unit testing
"""

__updated__ = "2021-08-16"

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
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME, TEST_DATA_LOCATION,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, )
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory

MSG_CANT_FIND_FILE = "Cannot find file: %s"


class SheTestCase:
    """ Base class for test cases, which provides various utility methods.
    """

    _args: Optional[Namespace] = None

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
        if self._args is None:
            self._args = self._make_mock_args()
        return self._args

    # Class methods, for when setup/teardown_class can be used

    @classmethod
    def teardown_class(cls):
        """ Delete the pipeline config if it's been created.
        """
        if cls.mock_pipeline_config_factory:
            cls.mock_pipeline_config_factory.cleanup()

    @classmethod
    def _download_mdb(cls):
        """ Download the test MDB from WebDAV.
        """
        sync = DataSync("testdata/sync.conf", "testdata/test_mdb.txt")
        sync.download()
        cls.mdb_filename = MDB_PRODUCT_FILENAME

        cls._finalize_download(cls.mdb_filename, sync)

        mdb.init(os.path.join(cls.workdir, cls.mdb_filename))

    @classmethod
    def _download_datastack(cls,
                            read_in: bool = True, ):
        """ Download the test data stack from WebDAV.
        """
        sync = DataSync("testdata/sync.conf", "testdata/test_data_stack.txt")
        sync.download()

        cls._finalize_download(VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, sync)

        # Read in the test data if desired
        if read_in:
            cls.data_stack = SHEFrameStack.read(exposure_listfile_filename = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                                detections_listfile_filename = MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                                workdir = cls.workdir,
                                                clean_detections = False,
                                                memmap = True,
                                                mode = 'denywrite')

    @classmethod
    def _finalize_download(cls,
                           filename: str,
                           sync_mdb: DataSync):
        """ Check that the desired file has been downloaded successfully and set the workdir based on its location.
        """

        # Check that the file was downloaded successfully
        qualified_filename = sync_mdb.absolutePath(os.path.join(TEST_DATA_LOCATION, filename))
        assert os.path.isfile(qualified_filename), MSG_CANT_FIND_FILE % qualified_filename

        # Set the workdir if it's not already set
        if cls.workdir is None:
            cls.workdir = os.path.split(qualified_filename)[0]

    def setup(self) -> None:
        """Overridable method, where the user can specify any unique setup for a given testing class."""
        return None

    @pytest.fixture(scope = 'class')
    def class_setup(self, tmpdir_factory):
        self.setup()
        self._finalize_class_setup(tmpdir_factory)
        return self

    def _finalize_class_setup(self, tmpdir_factory):
        self.tmpdir_factory = tmpdir_factory
        self._setup()

    @pytest.fixture(autouse = True)
    def local_setup(self, class_setup):
        """ Import all changes made to this class in the class_setup locally.
        """
        self._import_setup(class_setup)

        return self

    def _import_setup(self, setup):
        """ Copies all changes to a pickled fixture of this test case into this instnace.
        """
        for x in dir(setup):
            if len(x) < 2 or x[0:2] != "__":
                try:
                    setattr(self, x, getattr(setup, x))
                except AttributeError:
                    pass

    # Convenience methods for when setting up with autouse = True

    def _make_mock_args(self) -> Namespace:
        """Overridable method to create a mock self.args Namespace. Not necessary to implement if no args are used.
        """
        return Namespace()

    def _setup_workdir_from_tmpdir(self, tmpdir: LocalPath):
        """ Sets up workdir and logdir based on a tmpdir fixture.
        """
        if tmpdir is not None and self.workdir is None:
            self.workdir = tmpdir.strpath
        elif not hasattr(self, "workdir"):
            raise ValueError("self.workdir must be set if tmpdir is not provided to _setup_workdir_from_tmpdir.")
        self._setup_workdir()

    def _setup_workdir(self):
        """ Sets up self.logdir and otherwise prepares the workdir.
        """
        self.logdir = os.path.join(self.workdir, "logs")
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok = True)

    def _set_workdir_args(self) -> None:
        """ Set the workdir and logdir in the self.args attribute. Both must already be set for this object.
        """
        setattr(self.args, CA_WORKDIR, self.workdir)
        setattr(self.args, CA_LOGDIR, self.logdir)

    def _write_mock_pipeline_config(self):
        """ Write the pipeline config we'll be using and note its filename.
        """

        # Don't overwrite if a config is already set up to use
        if self.pipeline_config is not None:
            return

        self.mock_pipeline_config_factory = self.pipeline_config_factory_type(workdir = self.workdir)
        self.mock_pipeline_config_factory.write(self.workdir)
        self.pipeline_config = self.mock_pipeline_config_factory.pipeline_config

        setattr(self.args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.file_namer.filename)

    def _setup(self):
        """ Implements common setup when using a tmpdir.
        """
        if self.workdir is None:
            self._setup_workdir_from_tmpdir(self.tmpdir_factory.mktemp("test"))
        self._set_workdir_args()
        self._write_mock_pipeline_config()
