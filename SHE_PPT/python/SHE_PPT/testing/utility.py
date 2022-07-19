""" @file testing/utility.py

    Created 29 Oct 2021

    Utility classes and functions for unit testing
"""

from __future__ import annotations

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
import warnings
from argparse import Namespace
from typing import Any, Dict, Optional, Type

import pytest
from astropy.utils.exceptions import AstropyDeprecationWarning
from py.path import local
from pytest import TempdirFactory

from ElementsServices.DataSync import DataSync
from SHE_PPT import mdb
from SHE_PPT.argument_parser import CA_LOGDIR, CA_PIPELINE_CONFIG, CA_WORKDIR
from SHE_PPT.constants.config import ConfigKeys
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         SHE_EXPOSURE_SEGMENTATION_MAPS_LISTFILE_FILENAME,
                                         SHE_PSF_MODEL_IMAGES_LISTFILE_FILENAME, SHE_STACK_SEGMENTATION_MAP_FILENAME,
                                         SYNC_CONF,
                                         TEST_DATA_LOCATION,
                                         TEST_FILES_DATA_STACK, TEST_FILES_MDB,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, VIS_STACKED_FRAME_PRODUCT_FILENAME, )
from SHE_PPT.file_io import symlink_contents
from SHE_PPT.logging import set_log_level_debug
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.testing.mock_pipeline_config import MockPipelineConfigFactory

ENVVAR_WORKSPACE = "WORKSPACE"

MSG_CANT_FIND_FILE = "Cannot find file: %s"


class SheTestCase:
    """A base class to be used as a parent for all testing classes throughout the project (except where there's a good
    reason not to). This class performs the following tasks at the beginning of each test run:

    1. Sets the logging level to DEBUG, to ensure that any bugs in debug-level logging are caught during tests.
    2. Sets the WORKSPACE environment variable to be unique to the user, if it's not already set, so that any
       downloaded data will be stored in a unique location for each user; preventing conflicts from arising.
    3. Sets it so that any warning raised from the use of deprecated PF-SHE functions or parameters will be raised as
       an exception.
    4. Prepares a workdir for the tests (assigned to the `self.workdir` attribute) using `pytest`'s `tmpdir` fixture,
       with all test data symlinked to it, as well as a logging directory (assigned to the `self.logdir` attribute).
    5. Creates a mock pipeline configuration dictionary at `self.pipeline_config`.
    6. Creates a mock `Namespace` for read-in arguments at `self.args`, along with dictionary equivalent `d_args`.

    This class provides the following features for subclasses to use:

    1. Overridable method `setup_workdir`, which can be used to handle any downloading of data needed for unit
       tests, along with various convenience functions to download commonly-used test data, which can be used within
       this method:

        - `_download_mdb`
        - `_download_datastack`

       The formats of these methods can be followed if a download of other data is required. It is important that,
       if any data is downloaded, the method `_finalize_download` is called, passing to it the
       download-location-relative filename of any file downloaded and the `DataSync` object used to download it. This
       is used to determine the location to which data was downloaded. (This is already done by the methods listed
       above, and so does not need to be done with them.)

       See the documentation for the `setup_workdir` method for more details and example implementations.

    2. Overridable method `post_setup`, to handle any other setup tasks the user desires for tests,
       outside of downloading test data. See the documentation for this method for example implementations.

    3. Overridable method `teardown`, to handle any teardown tasks the user desires for a test. This should generally
       not be needed, as all data should be written to the workdir, and `pytest`'s `tmpdir` fixture will automatically
       handle deleting old directories created with this fixture, but it is provided in case it proves to be necessary.

    4. Overridable method `_make_mock_args`, which is used to create the mock `Namespace`, `self.args`.

    5. Overridable class attribute `pipeline_config_factory_type`, which is a class that will be used to create a mock
       pipeline configuration dictionary at `self.pipeline_config`. It is possible to generate a custom pipeline
       config by creating a new class that inherits from `MockPipelineConfigFactory`. overriding its
       `_make_pipeline_config` method to set the desired configuration, and then passing the class to this attribute as
       e.g.:

        ```
        class MyMockPipelineConfigFactory(MockPipelineConfigFactory):

            _config_keys = AnalysisConfigKeys

            def _make_pipeline_config(self):
                config = super()._make_pipeline_config()
                config[AnalysisConfigKeys.ES_METHODS] = "KSB REGAUSS"
                return config

        class MyTestCase(SheTestCase):
            pipeline_config_factory_type = MyMockPipelineConfigFactory
            ...
        ```

    Attributes
    ----------

    download_dir : str or None
        The location to which test data was downloaded, if any.
    workdir : str or None
        The path to the workdir created to be used for testing.
    logdir : str or None
        The path to the logging directory created to be used for testing.

    args : Namespace
    d_args : Dict[str, Any]
    pipeline_config : Dict[str, Any] or None
        The pipeline configuration dictionary created for use in testing.

    mdb_filename : str or None
        The filename of the MDB file downloaded, if any.
    data_stack : SHEFrameStack or None
        The SHEFrameStack download for testing, if any.

    pipeline_config_factory_type : Type[MockPipelineConfigFactory]
        The class to be used to create the mock pipeline configuration dictionary.
    mock_pipeline_config_factory : MockPipelineConfigFactory or None
        The instance of the class specified by `pipeline_config_factory_type` that was used to create the mock
        pipeline configuration dictionary.
    """

    download_dir: Optional[str] = None
    workdir: Optional[str] = None
    logdir: Optional[str] = None

    _args: Optional[Namespace] = None
    _d_args: Optional[Dict[str, Any]] = None

    pipeline_config: Optional[Dict[ConfigKeys, Any]] = None

    mdb_filename: Optional[str] = None
    data_stack: Optional[SHEFrameStack] = None

    pipeline_config_factory_type: Type[MockPipelineConfigFactory] = MockPipelineConfigFactory
    mock_pipeline_config_factory: Optional[MockPipelineConfigFactory] = None

    _tmpdir_factory: Optional[TempdirFactory] = None

    # Properties

    @property
    def args(self) -> Namespace:
        """A `Namespace` object which can be passed to tested functions which normally used the `args` `Namespace`
        returned from `parse_args()`. For subclasses, this should be set up by overriding the `_make_mock_args`
        method to generate a Namespace object with the expected attributes for the executable in which the
        function is run.

        Returns
        -------
        args : Namespace
            The generated `Namespace` mock parsed arguments to be used for testing.
        """
        if self._args is None:
            self._args = self._make_mock_args()
        return self._args

    @args.setter
    def args(self, args: Namespace) -> None:
        """Basic setter for the `args` property.

        Parameters
        ----------
        args : Namespace
            The `Namespace` object to be stored in this attribute.
        """
        self._args = args

    @property
    def d_args(self) -> Dict[str, Any]:
        """Similar to the args attribute, except converted to a Dict. This is used for any functions which
        normally take such an object. The Dict form is preferred when command-line arguments are set using
        constant variables, as it provides a cleaner interface to access these them, using d_args[key] instead of
        getattr(args, key).

        Returns
        -------
        d_args : Dict[str, Any]
            The generated dictionary version of the mock parsed arguments to be used for testing.
        """
        if self._d_args is None:
            self._d_args = vars(self.args)
        return self._d_args

    # Class methods

    @classmethod
    def teardown_class(cls) -> None:
        """ Delete the pipeline config if it's been created.
        """
        if cls.mock_pipeline_config_factory:
            cls.mock_pipeline_config_factory.cleanup()

    # Convenience methods to help with downloading data

    def _download_mdb(self) -> None:
        """Download the test Mission Database (MDB) from WebDAV. This stores the filename of the downloaded MDB file
        in the `self.mdb_filename` attribute and initializes the `SHE_PPT.mdb` module with the downloaded MDB.
        """
        sync = DataSync(SYNC_CONF, TEST_FILES_MDB)
        sync.download()
        self.mdb_filename = MDB_PRODUCT_FILENAME

        self._finalize_download(self.mdb_filename, sync)

        mdb.init(os.path.join(self.download_dir, self.mdb_filename))

    def _download_datastack(self,
                            read_in: bool = True, ) -> None:
        """Download the test `SHEFrameStack` data stack files from WebDAV.

        Parameters
        ----------
        read_in : bool, default=True
            If True, the downloaded data will be read in as a `SHEFrameStack` and stored in the
            `self.she_frame_stack` attribute.
        """
        sync = DataSync(SYNC_CONF, TEST_FILES_DATA_STACK)
        sync.download()

        self._finalize_download(VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, sync)

        # Read in the test data if desired
        if read_in:
            self.data_stack = SHEFrameStack.read(exposure_listfile_filename = VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                                 seg_listfile_filename =
                                                 SHE_EXPOSURE_SEGMENTATION_MAPS_LISTFILE_FILENAME,
                                                 stacked_image_product_filename = VIS_STACKED_FRAME_PRODUCT_FILENAME,
                                                 stacked_seg_product_filename = SHE_STACK_SEGMENTATION_MAP_FILENAME,
                                                 psf_listfile_filename = SHE_PSF_MODEL_IMAGES_LISTFILE_FILENAME,
                                                 detections_listfile_filename = MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                                 workdir = self.download_dir,
                                                 clean_detections = False,
                                                 save_products = True,
                                                 memmap = True,
                                                 mode = 'denywrite')

    def _finalize_download(self,
                           filename: str,
                           sync: DataSync,
                           test_data_location: str = TEST_DATA_LOCATION, ) -> None:
        """A method to check that the desired file has been downloaded successfully and set the `self.download_dir`
        attribute based on its location. If you are manually downloading data or setting up your own method to
        download data, this should be called on one of the downloaded files to ensure that the download was
        successful and to set up the `self.download_dir` attribute of this class.

        Parameters
        ----------
        filename : str
            The local filename of one of the files that you expect to have been downloaded (e.g. "test_mdb.xml")
        sync : DataSync
            The `DataSync` object used to download the file.
        test_data_location : str
            The directory set in the test data list file (in the conf directory) where test data is located.
        """

        # Check that the file was downloaded successfully
        qualified_filename = sync.absolutePath(os.path.join(test_data_location, filename))
        assert os.path.isfile(qualified_filename), MSG_CANT_FIND_FILE % qualified_filename

        # Set the download_dir if it's not already set
        if self.download_dir is None:
            self.download_dir = os.path.split(qualified_filename)[0]

    # Overridable setup methods

    def setup_workdir(self) -> None:
        """Overridable method, where the user can specify any unique setup for a given testing class, to be performed
        before the workdir is set up. This is normally used when it's needed to download test data, which will set
        the `self.download_dir` member to the location of the downloaded data.

        If nothing needs to be setup within the workdir, it is possible to use this function to perform all setup tasks
        for tests. Otherwise, the `self.post_setup()` method should be overridden to handle any setup tasks beyond
        downloading data.

        Example implementation:

        ```
        def setup_workdir(self):
            self._download_mdb()
        ```

        ```
        def setup_workdir(self):
            sync = DataSync(SYNC_CONF, MY_TEST_FILE_CONF)
            sync.download()
            self._finalize_download(MY_TEST_FILE_NAME, sync)
        ```
        ```
        """
        pass

    def post_setup(self) -> None:
        """Overridable method, where the user can specify any unique setup for a given testing class, to be performed
        after the workdir is set up. If any test data needs to be downloaded, that should be handled by the
        overriding the `self.setup_workdir()` method, and this method should be used to perform any other setup tasks.

        Example implementation:

        ```
        def post_setup(self):
            self.my_test_data = np.zeros((100, 100))

            self.test_filename = "my_test_file.txt"
            with open(get_qualified_filename(self.test_filename, self.workdir), "w") as f_out:
                f_out.write("Test text")
        ```
        """
        pass

    @pytest.fixture(scope="class")
    def class_setup(self, tmpdir_factory: TempdirFactory) -> SheTestCase:
        """A fixture which performs setup once per initialization of the test class, calling the overridable
        `self.setup_workdir()` and `self.post_setup()` methods.

        As this functions as a fixture, it may be used as an argument for any fixtures with "class" scope which
        depend upon any setup done in these two methods, e.g.:

        ```
        @pytest.fixture(scope = "class")
        def my_fixture(self, class_setup):
            ...
        ```

        Parameters
        ----------
        tmpdir_factory : TempdirFactory
            `pytest`'s `tmpdir_factory` fixture, which is used to generate temporary directories for testing.

        Returns
        -------
        self : SheTestCase
            This object at the end of executing all setup operations.
        """

        # Call initialisation tasks first
        self.__init()

        # Call to overridable `setup_workdir` method
        self.setup_workdir()

        # Internal setup using the state of the class at the end of the `setup_workdir` method.
        self._tmpdir_factory = tmpdir_factory
        self.__setup()

        # Call to overridable `post_setup` method
        self.post_setup()

        return self

    @pytest.fixture(autouse=True)
    def local_setup(self, class_setup: SheTestCase) -> SheTestCase:
        """An automatically-used fixture which imports all changes made to this class in the `class_setup` fixture
        locally. This gets around the fact that normally, after executing class-level fixtures, `pytest` resets the
        state of the class. So if we want to retain changes made in our class-level setup, we have to
        return the results of them as a fixture, then copy over the modifications.

        Parameters
        ----------
        class_setup : SheTestCase
            The `SheTestCase` object at the end of the execution of the `class_setup` fixture, which is used to copy
            over any changes to it to the object used for running this fixture and all tests.

        Returns
        -------
        self : SheTestCase
            This object at the end of executing all setup operations.
        """
        for x in dir(class_setup):
            # Skip any private attributes, which always start with "__"
            if not x.startswith("__"):
                try:
                    setattr(self, x, getattr(class_setup, x))
                except AttributeError:
                    # Silently pass for any attributes we can't set, which can happen if properties are defined without
                    # a setter, for instance. In those cases, the protected attributes storing data will be copied
                    # instead.
                    pass

        return self

    # Protected methods which can be overridden to modify the setup

    def _make_mock_args(self) -> Namespace:
        """Overridable method to create a mock `self.args` `Namespace`. Not necessary to implement if no args are used.

        Returns
        -------
        args : Namespace
            The mock parsed-arguments `Namespace` to be used for testing.
        """
        return Namespace()

    # Private methods

    @staticmethod
    def __init() -> None:
        """Run initialization tasks at the very beginning of tests.
        """

        # Set log level to debug to make sure there aren't any issues with logging strings
        set_log_level_debug()

        # Make sure the "WORKSPACE" envvar is set to be unique to this user, if it's not already set
        if ENVVAR_WORKSPACE not in os.environ or os.environ[ENVVAR_WORKSPACE] == "":
            os.environ[ENVVAR_WORKSPACE] = os.path.join("/tmp", os.environ["USER"])

    def __setup_workdir_from_tmpdir(self, tmpdir: local) -> None:
        """Sets up `self.workdir` and `self.logdir` based on a `tmpdir` fixture.
        """

        # Set the workdir to the tmpdir provided by the factory
        self.workdir = tmpdir.strpath

        # If any data was downloaded, symlink it to the workdir
        if self.download_dir is not None:
            symlink_contents(self.download_dir, self.workdir)

        self.__setup_workdir()

    def __setup_workdir(self) -> None:
        """Sets up `self.logdir` and the other expected subdirs of the workdir if they don't already exist.
        """
        self.logdir = os.path.join(self.workdir, "logs")
        os.makedirs(os.path.join(self.workdir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.workdir, "data"), exist_ok=True)

    def __set_workdir_args(self) -> None:
        """Set the workdir and logdir in the `self.args` `Namespace`. Both must already be set for this object
        when this method is called.
        """
        setattr(self.args, CA_WORKDIR, self.workdir)
        setattr(self.args, CA_LOGDIR, self.logdir)

    def __write_mock_pipeline_config(self) -> None:
        """Write the pipeline config we'll be using and store it in the `self.pipeline_config` attribute. This uses
        the class member `pipeline_config_factory_type` to construct the pipeline_config if it doesn't already exist,
        and thus modifying that variable in subclasses will modify the pipeline_config created here.

        The filename of the written pipeline config is stored in the `self.args` attribute's `pipeline_config`
        attribute.
        """

        # Don't overwrite if a config is already set up to use
        if self.pipeline_config is not None:
            return

        self.mock_pipeline_config_factory = self.pipeline_config_factory_type(workdir=self.workdir)
        self.mock_pipeline_config_factory.write(self.workdir)
        self.pipeline_config = self.mock_pipeline_config_factory.pipeline_config

        setattr(self.args, CA_PIPELINE_CONFIG, self.mock_pipeline_config_factory.filename)

    def __setup(self) -> None:
        """Implements common setup tasks. These include ensuring the workdir is set up, setting the
        workdir-related arguments to `self.args`, and creating a mock pipeline_config.
        """
        self.__setup_workdir_from_tmpdir(self._tmpdir_factory.mktemp("test"))
        self.__set_workdir_args()
        self.__write_mock_pipeline_config()

        # Set to raise an error on any deprecation warnings, to be sure they're caught and fixed in tests
        warnings.simplefilter("error", category=AstropyDeprecationWarning)
