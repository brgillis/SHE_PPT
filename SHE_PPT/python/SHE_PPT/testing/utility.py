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
from typing import Optional

import pytest
from py._path.local import LocalPath

from ElementsServices.DataSync import DataSync
from SHE_PPT import mdb
from SHE_PPT.argument_parser import CA_LOGDIR, CA_PIPELINE_CONFIG, CA_WORKDIR
from SHE_PPT.constants.test_data import MDB_PRODUCT_FILENAME, TEST_DATA_LOCATION, VIS_CALIBRATED_FRAME_LISTFILE_FILENAME
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory

MSG_CANT_FIND_FILE = "Cannot find file: %s"


class SheTestCase:
    """ Base class for test cases, which provides various utility methods.
    """

    args: Namespace
    workdir: Optional[str] = None
    logdir: Optional[str] = None
    mdb_filename: Optional[str] = None
    pipeline_config_factory_type = MockPipelineConfigFactory
    mock_pipeline_config_factory: Optional[MockPipelineConfigFactory] = None

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
    def _download_datastack(cls):
        """ Download the test data stack from WebDAV.
        """
        sync = DataSync("testdata/sync.conf", "testdata/test_data_stack.txt")
        sync.download()

        cls._finalize_download(VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, sync)

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

    @pytest.fixture(autouse = True)
    def setup(self):
        """ Default implementation of setup method. Can be overridden or inherited to change funcitonality.
        """
        self._setup()

    # Convenience methods for when setting up with autouse = True

    def _make_mock_args(self):
        """Overridable method to create a mock self.args Namespace. Not necessary to implement if no args are used.
        """
        self.args = Namespace()

    def _setup_workdir_from_tmpdir(self, tmpdir: LocalPath):
        """ Sets up workdir and logdir based on a tmpdir fixture.
        """
        if tmpdir is not None:
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

    def _make_pipeline_config(self):
        """ Write the pipeline config we'll be using and note its filename.
        """
        self.mock_pipeline_config_factory = self.pipeline_config_factory_type(workdir = self.workdir)
        self.mock_pipeline_config_factory.write(self.workdir)
        setattr(self.args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.file_namer.filename)

    def _setup(self, tmpdir: Optional[LocalPath] = None):
        """ Implements common setup when using a tmpdir.
        """
        self._setup_workdir_from_tmpdir(tmpdir)
        self._make_mock_args()
        self._set_workdir_args()
        self._make_pipeline_config()
