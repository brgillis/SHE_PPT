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

from py._path.local import LocalPath

from SHE_PPT.argument_parser import CA_LOGDIR, CA_PIPELINE_CONFIG, CA_WORKDIR
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory


class SheTestCase:
    """ Base class for test cases, which provides various utility method.
    """

    args: Namespace
    workdir: Optional[str] = None
    logdir: Optional[str] = None
    pipeline_config_factory_type = MockPipelineConfigFactory
    mock_pipeline_config_factory: Optional[MockPipelineConfigFactory] = None

    @classmethod
    def teardown_class(cls):
        """Delete the pipeline config if it's been created.
        """
        if cls.mock_pipeline_config_factory:
            cls.mock_pipeline_config_factory.cleanup()

    def _make_mock_args(self):
        """Overridable method to create a mock self.args Namespace. Not necessary to implement if no args are used.
        """
        self.args = Namespace()

    def _setup_workdir_from_tmpdir(self, tmpdir: LocalPath):
        """ Sets up workdir and logdir based on a tmpdir fixture.
        """
        self.workdir = tmpdir.strpath
        self.logdir = os.path.join(tmpdir.strpath, "logs")
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

    def _setup_with_tmpdir(self, tmpdir: LocalPath):
        """ Implements common setup when using a tmpdir.
        """
        self._setup_workdir_from_tmpdir(tmpdir)
        self._make_mock_args()
        self._set_workdir_args()
        self._make_pipeline_config()
