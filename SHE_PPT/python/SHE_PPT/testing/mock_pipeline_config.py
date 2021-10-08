""" @file mock_pipeline_config.py

    Created 8 October 2021.

    Utilities to generate, write, read, and cleanup mock pipeline configs for unit tests.
"""

__updated__ = "2021-10-05"

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

import os
from typing import Any, Dict, Optional, Type

import SHE_PPT
from SHE_PPT.constants.config import ConfigKeys, D_GLOBAL_CONFIG_DEFAULTS, GlobalConfigKeys
from SHE_PPT.file_io import SheFileNamer
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import read_config, write_config

logger = getLogger(__name__)

# Default values for the factory class
DEFAULT_PIPELINE_CONFIG_FILENAME = "shear_bias_pipeline_config.xml"


class MockPipelineConfigFactory:
    # Overridable class attributes
    _config_keys = GlobalConfigKeys
    _config_defaults = D_GLOBAL_CONFIG_DEFAULTS

    # Utilities
    file_namer: SheFileNamer = SheFileNamer(type_name = "PIPELINE-CONFIG",
                                            extension = ".txt",
                                            version = SHE_PPT.__version__)

    # Generated values
    _pipeline_config: Optional[Dict[ConfigKeys, Any]] = None

    def __init__(self,
                 filename: Optional[str] = DEFAULT_PIPELINE_CONFIG_FILENAME,
                 workdir: Optional[str] = None,
                 **kwargs):

        self.file_namer.filename = filename
        self.file_namer.workdir = workdir

        # Update values from kwargs if not None
        for key in kwargs:
            if kwargs[key] is not None:
                setattr(self, f"_{key}", kwargs[key])

    # Getters and setters for input properties

    @property
    def config_keys(self) -> Type[ConfigKeys]:
        return self._config_keys

    @property
    def config_defaults(self) -> Dict[ConfigKeys, Any]:
        return self._config_defaults

    @property
    def filename(self) -> str:
        return self.file_namer.filename

    @filename.setter
    def filename(self, value: str) -> None:
        self.file_namer.filename = value

    @property
    def workdir(self) -> str:
        return self.file_namer.workdir

    @workdir.setter
    def workdir(self, value: str) -> None:
        self.file_namer.workdir = value

    @property
    def qualified_filename(self) -> str:
        return self.file_namer.qualified_filename

    @property
    def pipeline_config(self) -> Dict[ConfigKeys, Any]:
        if self._pipeline_config is None:
            self._pipeline_config = self._make_pipeline_config()
        return self._pipeline_config

    # Private and protected methods

    def _decache(self):
        self._pipeline_config = None

    def _make_pipeline_config(self, ) -> Dict[ConfigKeys, Any]:
        """ Create and return a mock pipeline config dict.
        """

        return read_config(config_filename = None,
                           config_keys = self.config_keys,
                           defaults = self.config_defaults)

    # Public methods

    def write(self, workdir: str) -> None:
        """ Create and output a mock pipeline config file.
        """

        write_config(config_dict = self.pipeline_config,
                     config_filename = self.file_namer.filename,
                     workdir = self.file_namer.workdir,
                     config_keys = GlobalConfigKeys)

    def cleanup(self):
        os.remove(os.path.join(self.file_namer.qualified_filename))
