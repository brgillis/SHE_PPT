""" @file file_io_test.py

    Created 25 Aug 2017

    Unit tests relating to I/O functions.
"""

__updated__ = "2021-08-20"

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

import filecmp
import json
import os
import shutil
import stat
import subprocess
from time import sleep
from typing import Type

import numpy as np
import pytest
from astropy.io.fits import HDUList, PrimaryHDU, table_to_hdu
from astropy.table import Table

import SHE_PPT
from ElementsServices.DataSync.DataSynchronizer import DownloadFailed
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.constants.misc import DATA_SUBDIR
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME, SYNC_CONF,
                                         TEST_DATADIR, TEST_DATA_LOCATION, )
from SHE_PPT.file_io import (DEFAULT_FILE_EXTENSION, DEFAULT_FILE_SUBDIR, DEFAULT_INSTANCE_ID, DEFAULT_TYPE_NAME,
                             FileLoader, FitsLoader, MultiFileLoader, MultiFitsLoader, MultiProductLoader,
                             MultiTableLoader, ProductLoader, SheFileAccessError, SheFileNamer, SheFileReadError,
                             SheFileWriteError, TableLoader, append_hdu, copy_listfile_between_dirs,
                             copy_product_between_dirs, find_aux_file, find_conf_file, find_file, find_file_in_path,
                             find_web_file, first_in_path, first_writable_in_path, get_all_files, get_allowed_filename,
                             get_data_filename, get_qualified_filename, instance_id_maxlen, processing_function_maxlen,
                             read_d_l_method_table_filenames, read_d_l_method_tables, read_d_method_table_filenames,
                             read_d_method_tables, read_fits, read_listfile, read_product_and_table, read_table,
                             read_table_from_product, read_xml_product, remove_files, replace_in_file,
                             replace_multiple_in_file, safe_copy, symlink_contents, tar_files, try_remove_file,
                             type_name_maxlen, update_xml_with_value, write_fits, write_listfile,
                             write_product_and_table, write_table, write_xml_product, )
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.products.she_validated_measurements import create_dpd_she_validated_measurements
from SHE_PPT.table_formats.mer_final_catalog import MerFinalCatalogFormat
from SHE_PPT.testing.mock_measurements_cat import EST_SEED, MockShearEstimateTableGenerator
from SHE_PPT.testing.mock_mer_final_cat import MockMFCGalaxyTableGenerator
from SHE_PPT.testing.utility import ENVVAR_WORKSPACE, SheTestCase
from ST_DataModelBindings.dpd.she.raw.validatedmeasurements_stub import dpdSheValidatedMeasurements
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from ST_DataModelBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame

TEST_AUX_FILE = 'SHE_PPT/sample_vis_stacked_frame.xml'
FILENAME_NO_FILE = "nonexistent_file"
PATH_NO_DIRECTORY = "/no/directory/"
IS_ROOT = os.geteuid() == 0


class TestIO(SheTestCase):
    """ A class to handle tests of functions and classes in the SHE_PPT/file_io.py module.
    """

    listfile_name: str = "test_listfile.junk"
    src_subdir = "src"
    dest_subdir = "dest"

    def post_setup(self):
        """ Perform some setup tasks for functions tested here, setting up data which is used for multiple tests.
        """

        # Create source and destination subdirs of the workdir to test copying functions
        self.src_dir = os.path.join(self.workdir, self.src_subdir)
        os.makedirs(os.path.join(self.src_dir, DATA_SUBDIR), exist_ok=True)

        self.dest_dir = os.path.join(self.workdir, self.dest_subdir)
        os.makedirs(os.path.join(self.dest_dir, DATA_SUBDIR), exist_ok=True)

        # Create a table, data product, and listfile we wish to test copying
        mfc_table_gen = MockMFCGalaxyTableGenerator(workdir=self.src_dir,
                                                    num_test_points=2)

        # write_mock_listfile writes all the files we need, so just call it
        mfc_table_gen.write_mock_listfile()

        # Get the filenames of the created objects
        self.table_filename = mfc_table_gen.table_filename
        self.product_filename = mfc_table_gen.product_filename
        self.listfile_filename = mfc_table_gen.listfile_filename

        # Use one of the sample data products in the auxdir for testing
        self.test_xml_product = read_xml_product(find_aux_file(TEST_AUX_FILE))

        # Make a sample table for testing
        self.test_table = Table(data=[[0.0, 1.0], [0.1, 1.1]])

        table_hdu = table_to_hdu(self.test_table)

        self.test_hdulist = HDUList([PrimaryHDU(), table_hdu])

    def test_get_qualified_filename(self):
        """Unit test of get_qualified_filename.
        """

        test_local_filename = "filename.txt"
        test_qualified_filename = "/path/filename.txt"

        # Check it combines properly
        assert get_qualified_filename(test_local_filename, self.workdir) == os.path.join(self.workdir,
                                                                                         test_local_filename, )

        # Check a fully-qualified filename is used without incorporating workdir
        assert get_qualified_filename(test_qualified_filename, self.workdir) == test_qualified_filename

        # Check an error is raised when expected
        with pytest.raises(ValueError):
            _ = get_qualified_filename("")

    def test_she_file_access_error(self):
        """Unit test of the SheAccessError exception class and child classes of it.
        """

        test_filename = "filename.txt"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)
        test_message = "This is a test message."

        test_access_error = SheFileAccessError(filename=test_filename,
                                               workdir=self.workdir)
        test_write_error = SheFileWriteError(qualified_filename=test_qualified_filename)
        test_read_error = SheFileReadError(filename=test_filename,
                                           workdir=self.workdir,
                                           qualified_filename=test_qualified_filename,
                                           message=test_message)

        # Check that all attrs are as expected

        assert test_access_error.filename == test_filename
        assert test_access_error.workdir == self.workdir
        assert test_access_error.qualified_filename == test_qualified_filename
        assert test_access_error.operation == SheFileAccessError.operation

        assert test_write_error.qualified_filename == test_qualified_filename
        assert test_write_error.operation == SheFileWriteError.operation

        assert test_read_error.filename == test_filename
        assert test_read_error.workdir == self.workdir
        assert test_read_error.qualified_filename == test_qualified_filename
        assert test_read_error.operation == SheFileReadError.operation
        assert test_read_error.message == test_message

        # Check that they can all be raised and caught as expected parent classes
        for test_error in (test_access_error, test_write_error, test_read_error):
            with pytest.raises(IOError):
                raise test_error
            with pytest.raises(SheFileAccessError):
                raise test_error

        # Check it raises a ValueError if not properly initialised
        with pytest.raises(ValueError):
            _ = SheFileAccessError()
        with pytest.raises(ValueError):
            _ = SheFileAccessError(filename=test_filename,
                                   workdir=self.workdir,
                                   qualified_filename="/not/the/right.filename")

    def test_get_allowed_filename(self):
        """Test the function and classes to get a filename.
        """

        instance_id = "instance"

        filename = get_allowed_filename("test", instance_id, extension=".junk", release="06.66", subdir="subdir")

        expect_filename_head = "subdir/EUC_SHE_TEST_INSTANCE_"
        expect_filename_tail = "Z_06.66.junk"

        # Check the beginning and end are correct
        assert filename[0:len(expect_filename_head)] == expect_filename_head
        assert filename[-len(expect_filename_tail):] == expect_filename_tail

        # Check that if we wait a tenth of a second, it will change
        sleep(0.1)
        new_filename = get_allowed_filename("test", instance_id, extension=".junk", release="06.66",
                                            subdir="subdir")
        assert new_filename != filename

        # Test that it raises when we expect it to

        # Test for forbidden character
        with pytest.raises(ValueError):
            get_allowed_filename("test*", instance_id, extension=".junk", release="06.66", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id + "/", extension=".junk", release="06.66", subdir="subdir")

        # Test for bad release
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.666", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.6a", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.", subdir="subdir")

        # Test for too long
        with pytest.raises(ValueError):
            get_allowed_filename("t" * (type_name_maxlen + 1), instance_id,
                                 extension=".junk", release="06.66", subdir="subdir")
        with pytest.raises(ValueError):
            get_allowed_filename("test", "i" * (instance_id_maxlen + 3),
                                 extension=".junk", release="06.66", subdir="subdir", timestamp=True)
        with pytest.raises(ValueError):
            get_allowed_filename("test", instance_id, extension=".junk", release="06.66", subdir="subdir",
                                 processing_function="p" * (processing_function_maxlen + 1))

    def test_file_namer(self):
        """Test the functionality of the SheFileNamer class, except that which was already tested through the test of
        get_allowed_filename above.
        """
        file_namer = SheFileNamer(version="1.2", workdir=self.workdir, subdir="", extension="junk")

        # Set up type name and instance ID, testing setters and getters while we do so

        str_tnh = "TNH"
        file_namer.type_name_head = str_tnh
        assert file_namer.type_name_head == str_tnh

        str_tnb = "TNB"
        file_namer.type_name_body = str_tnb
        assert file_namer.type_name_body == str_tnb

        str_tnt = "TNT"
        file_namer.type_name_tail = str_tnt
        assert file_namer.type_name_tail == str_tnt

        file_namer.instance_id_head = None
        assert file_namer.instance_id_head is None

        str_iib = "IIB"
        file_namer.instance_id_body = str_iib
        assert file_namer.instance_id_body == str_iib

        str_iit = "IIT"
        file_namer.instance_id_tail = str_iit
        assert file_namer.instance_id_tail == str_iit

        # Check that the constructed filename is as expected
        filename = file_namer.filename
        qualified_filename = file_namer.qualified_filename

        # Check type name
        ex_type_name = f"{str_tnh}-{str_tnb}-{str_tnt}"
        assert file_namer.type_name == ex_type_name
        assert f"_{ex_type_name}_" in filename

        # Check instance ID
        ex_instance_id = f"{str_iib}-{str_iit}"
        assert f"_{ex_instance_id}_" in filename

        # Check version was properly converted to release
        ex_filename_tail = "Z_01.02.junk"
        assert filename[-len(ex_filename_tail):] == ex_filename_tail

        # Check qualified filename is as expected
        assert get_qualified_filename(filename, self.workdir) == qualified_filename

        # Check that the filename updates when a setter is called
        sleep(0.1)
        file_namer.type_name_head = file_namer.type_name_head

        new_filename = file_namer.filename
        new_qualified_filename = file_namer.qualified_filename

        assert new_filename != filename
        assert new_qualified_filename != qualified_filename

        # Check that all other getters and setters function as expected
        file_namer.type_name = "1"
        assert file_namer.type_name == "1"

        file_namer.instance_id = "2"
        assert file_namer.instance_id == "2"

        file_namer.extension = ".ext"
        assert file_namer.extension == ".ext"

        file_namer.release = "40.03"
        assert file_namer.release == "40.03"

        file_namer.version = "5.1.0"
        assert file_namer.version == "5.1.0"
        file_namer.version = None

        file_namer.subdir = "foo/"
        assert file_namer.subdir == "foo/"

        file_namer.processing_function = "EXT"
        assert file_namer.processing_function == "EXT"

        file_namer.timestamp = False
        assert file_namer.timestamp is False

        file_namer.workdir = "/home/user"
        assert file_namer.workdir == "/home/user"

        file_namer.filename = "foo.bar"
        assert file_namer.filename == "foo.bar"

        file_namer.qualified_filename = "/etc/conf/this.file"
        assert file_namer.qualified_filename == "/etc/conf/this.file"

        # Check that setting subdir to None is the same as setting it to an empty string
        file_namer.subdir = None
        f1 = file_namer.get()
        file_namer.subdir = ""
        f2 = file_namer.get()
        assert f1 == f2

        # Test we get expected exceptions when we don't have a type name or instance ID
        with pytest.raises(NotImplementedError):
            file_namer.type_name_body = None
            _ = file_namer.type_name
        file_namer.type_name_body = "type_name"
        with pytest.raises(NotImplementedError):
            file_namer.instance_id_body = None
            _ = file_namer.instance_id
        file_namer.instance_id_body = "instance_id"

        # Check we get a ValueError if both release and version are None
        with pytest.raises(ValueError):
            file_namer.release = None
            file_namer.version = None
            _ = file_namer.get()
        file_namer.version = "1.0"

    def test_rw_xml_product(self):
        """Tests of the read_xml_product and write_xml_product functions.
        """

        ex_type = dpdVisStackedFrame
        non_ex_type = dpdVisCalibratedFrame

        test_filename = "product.xml"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample product and read it back in
        write_xml_product(self.test_xml_product, test_qualified_filename)

        p2 = read_xml_product(test_qualified_filename, product_type=ex_type)
        p2.validateBinding()

        assert type(self.test_xml_product) is type(p2)

        # Test that if we specify the wrong type, a TypeError is raised
        with pytest.raises(TypeError):
            _ = read_xml_product(test_qualified_filename, product_type=non_ex_type)

        # Test that we get expected read/write errors if the path doesn't exist
        with pytest.raises(SheFileWriteError):
            write_xml_product(self.test_xml_product,
                              test_filename,
                              workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY, ),
                              log_info=True)
        with pytest.raises(SheFileReadError):
            _ = read_xml_product(test_filename,
                                 workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                                 log_info=True)

        try_remove_file(test_qualified_filename)

    @staticmethod
    def _run_file_loader_test(file_loader: FileLoader, ex_type: Type):
        """Run common tests that a FileLoader works as expected.
        """

        file_loader.load()
        assert isinstance(file_loader.obj, ex_type)

        file_loader.close()
        assert file_loader.obj is None

        file_loader.open()
        assert isinstance(file_loader.obj, ex_type)

        file_loader.close()

    @staticmethod
    def _run_multi_file_loader_test(multi_file_loader: MultiFileLoader, ex_type: Type):
        """Run common tests that a MultiFileLoader works as expected.
        """
        multi_file_loader.load_all()
        assert isinstance(multi_file_loader.l_file_loaders[0].obj, ex_type)

        multi_file_loader.close_all()
        assert multi_file_loader.l_file_loaders[0].obj is None

        l_objects = multi_file_loader.get_all()
        assert isinstance(l_objects[0], ex_type)

        multi_file_loader.open_all()
        assert isinstance(multi_file_loader.l_file_loaders[0].obj, ex_type)
        multi_file_loader.close_all()

    def test_product_loader(self):
        """Test that the ProductLoader class works as expected.
        """

        test_filename = "product_loader_product.xml"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample product and read it back in with the ProductLoader
        write_xml_product(self.test_xml_product, test_qualified_filename)

        product_loader = ProductLoader(filename=test_filename,
                                       workdir=self.workdir)

        # Test that the ProductLoader is set up as expected
        assert product_loader.filename == test_filename
        assert product_loader.workdir == self.workdir
        assert product_loader.qualified_filename == test_qualified_filename
        assert product_loader.object is None
        assert product_loader.obj is None

        # Test making a MultiProductLoader with this
        multi_product_loader = MultiProductLoader(workdir=self.workdir,
                                                  l_file_loaders=[product_loader],
                                                  file_loader_type=ProductLoader)

        # Run common tests on this and the Multi version
        ex_type = dpdVisStackedFrame
        self._run_file_loader_test(product_loader, ex_type)
        self._run_multi_file_loader_test(multi_product_loader, ex_type)

        try_remove_file(test_qualified_filename)

        # Test we get expected exceptions with making the MultiProductLoader

        # ValueError if providing both a list of filenames and a list of file loaders
        with pytest.raises(ValueError):
            _ = MultiProductLoader(workdir=self.workdir,
                                   l_filenames=[test_filename],
                                   l_file_loaders=[product_loader],
                                   file_loader_type=ProductLoader)

        # TypeError if type mismatch
        with pytest.raises(TypeError):
            _ = MultiProductLoader(workdir=self.workdir,
                                   l_file_loaders=[product_loader],
                                   file_loader_type=FitsLoader)

        # ValueError if l_filenames but not file_loader_type
        with pytest.raises(ValueError):
            _ = MultiFileLoader(workdir=self.workdir,
                                l_filenames=[test_filename], )

        # Check init with only workdir works though
        _ = MultiProductLoader(workdir=self.workdir)

    def test_rw_listfile(self):
        """Tests of reading and writing listfiles.
        """

        l_simple = ["file1.ext", "file2.ext", "file3.ext"]
        l_tupled = [("file1a.ext", "file1b.ext"), ("file2a.ext", "file2b.ext"), ("file3a.ext", "file3b.ext")]
        l_single_tupled = [("file1.ext",), ("file2.ext",), ("file3.ext",)]

        write_listfile(self.listfile_name, l_simple, workdir=self.workdir)
        assert read_listfile(self.listfile_name, workdir=self.workdir) == l_simple
        os.remove(os.path.join(self.workdir, self.listfile_name))

        # Test that tupled listfile is properly read in
        write_listfile(self.listfile_name, l_tupled, workdir=self.workdir)
        assert read_listfile(self.listfile_name, workdir=self.workdir) == l_tupled
        os.remove(os.path.join(self.workdir, self.listfile_name))

        # Test that the singly-tupled listfile is properly flattened when read back in
        write_listfile(self.listfile_name, l_single_tupled, workdir=self.workdir)
        assert read_listfile(self.listfile_name, workdir=self.workdir) == l_simple
        os.remove(os.path.join(self.workdir, self.listfile_name))

        with pytest.raises(SheFileWriteError):
            write_listfile(self.listfile_name,
                           l_simple,
                           workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY, ),
                           log_info=True)
        with pytest.raises(SheFileReadError):
            _ = read_listfile(self.listfile_name,
                              workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                              log_info=True)

        try_remove_file(self.listfile_name, workdir=self.workdir)

    def test_listfile_write_kwargs(self, tmp_path):
        """check that write_listfile can take json.dump arguments"""

        l_simple = ["file1.ext", "file2.ext", "file3.ext"]

        # we try the indent=2 argument
        reference_string = json.dumps(l_simple, indent=2)
        write_listfile(self.listfile_name, l_simple, workdir=tmp_path, indent=2)
        with open(tmp_path / self.listfile_name) as f:
            string = f.read()
        assert reference_string == string

    def test_listfile_read_kwargs(self, tmp_path):
        """check that read_listfile can take json.load arguments"""

        # We use the parse_float CLA, checking that we can convert all floats to numpy.float32
        array = [1.0, 2.0, 3.0]
        with open(tmp_path / self.listfile_name, "w") as f:
            json.dump(array, f)
        output_array = read_listfile(self.listfile_name, workdir=tmp_path, parse_float=np.float32)
        for element in output_array:
            assert type(element) is np.float32

    def test_rw_table(self):
        """Tests of the read_table and write_table functions.
        """

        test_filename = "table.fits"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample table and read it back in
        write_table(self.test_table, test_qualified_filename)

        t2 = read_table(test_qualified_filename)
        assert np.all(self.test_table == t2)

        # Test that we get expected read/write errors
        with pytest.raises(SheFileWriteError):
            write_table(self.test_table,
                        test_filename,
                        workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY, ),
                        log_info=True)
        with pytest.raises(SheFileReadError):
            _ = read_table(test_filename,
                           workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                           log_info=True)

        try_remove_file(test_qualified_filename)

    def test_table_loader(self):
        """Test that the TableLoader class works as expected.
        """

        test_filename = "table_loader_table.fits"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample table and read it back in
        write_table(self.test_table, test_qualified_filename)

        table_loader = TableLoader(filename=test_filename,
                                   workdir=self.workdir)

        # Test making a MultiProductLoader with this
        multi_table_loader = MultiTableLoader(workdir=self.workdir,
                                              l_filenames=[test_filename],
                                              file_loader_type=TableLoader)

        # Run common tests on this and the Multi version
        ex_type = Table
        self._run_file_loader_test(table_loader, ex_type)
        self._run_multi_file_loader_test(multi_table_loader, ex_type)

        try_remove_file(test_qualified_filename)

    def test_rw_fits(self):
        """Tests of the read_fits and write_fits functions.
        """

        test_filename = "fits.fits"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample fits and read it back in
        write_fits(self.test_hdulist, test_qualified_filename)

        f2 = read_fits(test_qualified_filename)
        assert np.all(self.test_hdulist[1].data == f2[1].data)

        # Test that we get expected read/write errors
        with pytest.raises(SheFileWriteError):
            write_fits(self.test_hdulist,
                       test_filename,
                       workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY, ),
                       log_info=True)
        with pytest.raises(SheFileReadError):
            _ = read_fits(test_filename,
                          workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                          log_info=True)

        try_remove_file(test_qualified_filename)

    def test_fits_loader(self):
        """Test that the FitsLoader class works as expected.
        """

        test_filename = "fits_loader_fits.fits"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)

        # Test that we can write out the sample fits and read it back in
        write_fits(self.test_hdulist, test_qualified_filename)

        fits_loader = FitsLoader(filename=test_filename,
                                 workdir=self.workdir)

        # Test making a MultiProductLoader with this
        multi_fits_loader = MultiFitsLoader(workdir=self.workdir,
                                            l_filenames=[test_filename])

        # Run common tests on this and the Multi version
        ex_type = HDUList
        self._run_file_loader_test(fits_loader, ex_type)
        self._run_multi_file_loader_test(multi_fits_loader, ex_type)

        # Test that we get expected read/write errors
        with pytest.raises(SheFileWriteError):
            write_fits(self.test_xml_product,
                       test_filename,
                       workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY, ),
                       log_info=True)
        with pytest.raises(SheFileReadError):
            _ = read_fits(test_filename,
                          workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                          log_info=True)

        try_remove_file(test_qualified_filename)

    @pytest.mark.xfail(IS_ROOT, reason="root has unrestricted capabilities to write files")
    def test_append_hdu(self):
        """Tests of the append_hdu function.
        """

        # Start by writing a file to disk
        test_filename = "append_hdu.fits"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)
        write_fits(self.test_hdulist, test_qualified_filename)

        # Create a new file and try appending it
        t = Table([[10, 20]])
        t_hdu = table_to_hdu(t)

        append_hdu(test_qualified_filename, t_hdu)

        # Check that the new HDU was in fact appended

        f2 = read_fits(test_qualified_filename)
        assert np.all(t_hdu.data == f2[2].data)

        # Test that we get expected read/write errors
        with pytest.raises(SheFileReadError):
            append_hdu(test_filename,
                       hdu=t_hdu,
                       workdir=os.path.join(self.workdir, PATH_NO_DIRECTORY),
                       log_info=True)
        try:
            with pytest.raises(SheFileWriteError):
                os.chmod(test_qualified_filename, stat.S_IREAD)
                append_hdu(test_qualified_filename,
                           hdu=t_hdu,
                           log_info=True)
        finally:
            os.chmod(test_qualified_filename, stat.S_IREAD | stat.S_IWRITE)

        try_remove_file(test_qualified_filename)

    def test_replace_in_file(self):
        """Unit test of replace_in_file and replace_multiple_in_file functions.
        """

        # Define variables for input and output strings
        str_key1 = "key1"
        str_key2 = "key2"
        str_key3 = "key3"

        str_val1 = "val1"
        str_val2 = "val2"

        str_val1a = "val1a"
        str_key3a = "key3a"

        l_input_lines = [f"{str_key1}: {str_val1}\n",
                         f"{str_key2}: {str_val1} {str_val1}\n",
                         f"{str_key3}: {str_val2}\n"]

        # Create a file to test some replacement commands
        filename_in = "test.txt"
        qualified_filename_in = get_qualified_filename(filename_in, workdir=self.workdir)
        with open(qualified_filename_in, "w") as fo:
            for line in l_input_lines:
                fo.write(line)

        filename_out = "test_out.txt"
        qualified_filename_out = get_qualified_filename(filename_out, workdir=self.workdir)

        # Try replacing a single value
        replace_in_file(input_filename=qualified_filename_in,
                        output_filename=qualified_filename_out,
                        input_string=str_val1,
                        output_string=str_val1a)
        with open(qualified_filename_out, "r") as fi:
            for input_line, output_line in zip(l_input_lines, fi):
                assert input_line.replace(str_val1, str_val1a) == output_line

        # Try replacing multiple values
        replace_multiple_in_file(input_filename=qualified_filename_in,
                                 output_filename=qualified_filename_out,
                                 input_strings=[str_val1, str_key3],
                                 output_strings=[str_val1a, str_key3a])
        with open(qualified_filename_out, "r") as fi:
            for input_line, output_line in zip(l_input_lines, fi):
                assert input_line.replace(str_val1, str_val1a).replace(str_key3, str_key3a) == output_line

        # Test expected exceptions

        with pytest.raises(ValueError):
            # Same file as input and output
            replace_in_file(input_filename=qualified_filename_in,
                            output_filename=qualified_filename_in,
                            input_string=str_val1,
                            output_string=str_val1a)

        with pytest.raises(ValueError):
            # Same file as input and output
            replace_multiple_in_file(input_filename=qualified_filename_in,
                                     output_filename=qualified_filename_in,
                                     input_strings=[str_val1, str_key3],
                                     output_strings=[str_val1a, str_key3a])

        with pytest.raises(ValueError):
            # Different list lengths
            replace_multiple_in_file(input_filename=qualified_filename_in,
                                     output_filename=qualified_filename_out,
                                     input_strings=[str_val1, str_key3],
                                     output_strings=[str_val1a])

    def test_find_file_in_path(self):
        """Unit tests of `find_file_in_path`.
        """

        # Try searching for a file we know exists
        test_qualified_filename = find_file_in_path(self.table_filename, self.src_dir)
        assert os.path.isfile(test_qualified_filename)

        # Now test with a more complicated path
        test_path = ":".join([self.workdir, self.src_dir, self.dest_dir])
        test_qualified_filename = find_file_in_path(self.table_filename, test_path)
        assert os.path.isfile(test_qualified_filename)

        # Test it raises an exception when expected
        with pytest.raises(RuntimeError):
            _ = find_file_in_path(FILENAME_NO_FILE, test_path)

    def test_find_conf_file(self):
        """Unit tests of `find_conf_file`.
        """

        # Try searching for a file we know exists
        test_qualified_filename = find_conf_file(SYNC_CONF)
        assert os.path.isfile(test_qualified_filename)

        # Test it raises an exception when expected
        with pytest.raises(RuntimeError):
            _ = find_conf_file(FILENAME_NO_FILE)

    def test_find_aux_file(self):
        """Unit tests of `find_aux_file`.
        """

        # Try searching for a file we know exists
        test_qualified_filename = find_aux_file(TEST_AUX_FILE)
        assert os.path.isfile(test_qualified_filename)

        # Test it raises an exception when expected
        with pytest.raises(RuntimeError):
            _ = find_aux_file(FILENAME_NO_FILE)

    def test_find_web_file(self):
        """Unit tests of `find_web_file`.
        """

        # Try searching for a file we know exists
        test_qualified_filename = find_web_file(os.path.join(TEST_DATA_LOCATION,
                                                             MER_FINAL_CATALOG_LISTFILE_FILENAME))
        assert os.path.isfile(test_qualified_filename)

        # Also try searching for an MDB file, which follows a different code branch
        test_qualified_filename = find_web_file(os.path.join(TEST_DATA_LOCATION,
                                                             MDB_PRODUCT_FILENAME))
        assert os.path.isfile(test_qualified_filename)

        # Test it raises an exception when expected

        # Delete any potentially cached version of the null file, both before and after the test
        qualified_null_filename = os.path.join(os.environ[ENVVAR_WORKSPACE], TEST_DATADIR[1:], FILENAME_NO_FILE)
        try_remove_file(qualified_null_filename)

        with pytest.raises(DownloadFailed):
            _ = find_web_file(FILENAME_NO_FILE)

        try_remove_file(qualified_null_filename)

    def test_find_file(self):
        """Unit test of `find_file`.
        """

        # Check that we can find files of each type using the standard prefix

        # auxdir - AUX/
        test_qualified_filename = find_file("CONF/" + SYNC_CONF)
        assert os.path.isfile(test_qualified_filename)

        # conf - CONF/
        test_qualified_filename = find_file("AUX/" + TEST_AUX_FILE)
        assert os.path.isfile(test_qualified_filename)

        # WebDAV - WEB/
        test_qualified_filename = find_file(os.path.join("WEB", TEST_DATA_LOCATION,
                                                         MER_FINAL_CATALOG_LISTFILE_FILENAME))
        assert os.path.isfile(test_qualified_filename)

        # $HOME - HOME/
        test_qualified_filename = find_file("HOME/.bashrc")
        assert os.path.isfile(test_qualified_filename)

        # Already fully-qualified
        test_qualified_filename = find_file(test_qualified_filename)
        assert os.path.isfile(test_qualified_filename)

        # Find in path
        test_qualified_filename = find_file(SYNC_CONF, path=os.environ['ELEMENTS_CONF_PATH'])
        assert os.path.isfile(test_qualified_filename)

        # Test expected errors

        # Can't find fully-qualified file
        with pytest.raises(RuntimeError):
            _ = find_file("/" + FILENAME_NO_FILE)

        # Path not supplied
        with pytest.raises(ValueError):
            _ = find_file(SYNC_CONF)

    def test_get_all_files(self):
        """Unit test of the `get_all_files` function.
        """

        test_dir = os.path.join(self.workdir, 'test_dir')
        os.mkdir(test_dir)

        subdir_name1 = 'sub_a'
        os.mkdir(os.path.join(test_dir, subdir_name1))

        subdir_name2 = 'sub_b'
        os.mkdir(os.path.join(test_dir, subdir_name2))

        file_name1 = 'file1.txt'
        file_name2 = 'file2.txt'
        open(os.path.join(test_dir, file_name1), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, file_name2), 'w').writelines(['2\n'])

        file_name3 = 'file3.txt'
        file_name4 = 'file4.txt'
        open(os.path.join(test_dir, subdir_name1, file_name3), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, subdir_name2, file_name4), 'w').writelines(['2\n'])

        subdir_name3 = 'sub_b1'
        os.mkdir(os.path.join(test_dir, subdir_name2, subdir_name3))

        file_name5 = 'file5.txt'
        open(os.path.join(test_dir, subdir_name2, subdir_name3, file_name5), 'w').writelines(['1\n'])

        file_list = get_all_files(test_dir)
        assert len(file_list) == 5

        for ii, fName in enumerate(sorted(file_list)):
            assert os.path.basename(fName) == 'file%s.txt' % (ii + 1)
        shutil.rmtree(test_dir)

    def test_update_xml_with_value(self):
        """ Test creating a simple xml file and updating with <Value>
        """

        qualified_test_filename = find_aux_file('SHE_PPT/sample_vis_stacked_frame.xml')

        product = read_xml_product(qualified_test_filename)
        lines = open(qualified_test_filename).readlines()
        num_lines = len(lines)
        lines = [line for ii, line in enumerate(lines) if not ('<Value>' in line and '<Key>' in lines[ii - 1])]
        if len(lines) < num_lines:
            qualified_temp_test_filename = os.path.join(self.workdir, 'temp_test.xml')
            open(qualified_temp_test_filename, 'w').writelines(lines)

            update_xml_with_value(qualified_temp_test_filename)
            product = read_xml_product(qualified_temp_test_filename)
        product.validateBinding()

    @pytest.mark.xfail(IS_ROOT, reason="root has unrestricted capabilities to write files")
    def test_tar_files(self):
        """ Runs test of tarring files.
        """

        # Set up the files

        l_filenames = ["a.txt", "b.txt"]
        l_texts = ["foo/n", "bar/n"]

        l_qualified_filenames = [get_qualified_filename(filename, self.workdir) for filename in l_filenames]

        for filename, text in zip(l_filenames, l_texts):
            with open(os.path.join(self.workdir, filename), "w") as fo:
                fo.write(text)

        tarball_filename = "tarball.tar"
        qualified_tarball_filename = get_qualified_filename(tarball_filename, self.workdir)

        # Check everything is set up as expected
        assert os.path.isfile(l_qualified_filenames[0])
        assert os.path.isfile(l_qualified_filenames[1])

        tar_files(tarball_filename=tarball_filename,
                  l_filenames=l_filenames,
                  workdir=self.workdir,
                  delete_files=True)

        # Check things have been tarred up
        assert not os.path.isfile(l_qualified_filenames[0])
        assert not os.path.isfile(l_qualified_filenames[1])
        assert os.path.isfile(qualified_tarball_filename)

        # Check that we can un-tar and retrieve the data
        subprocess.call(f"cd {self.workdir} && tar xf {tarball_filename}", shell=True)

        assert os.path.isfile(l_qualified_filenames[0])
        assert os.path.isfile(l_qualified_filenames[1])

        for filename, text in zip(l_filenames, l_texts):
            with open(os.path.join(self.workdir, filename), "r") as fi:
                read_text = fi.read()
                assert read_text == text

        # Check that we get expected errors

        for filename, text in zip(l_filenames, l_texts):
            with open(os.path.join(self.workdir, filename), "w") as fo:
                fo.write(text)

        # Try writing to an un-writable file
        try:
            os.chmod(qualified_tarball_filename, stat.S_IREAD)
            with pytest.raises(SheFileWriteError):
                tar_files(tarball_filename=qualified_tarball_filename,
                          l_filenames=l_filenames,
                          workdir=self.workdir,
                          delete_files=False)
        finally:
            os.chmod(qualified_tarball_filename, stat.S_IREAD | stat.S_IWRITE)

        # Try writing files that don't exist
        with pytest.raises(SheFileWriteError):
            tar_files(tarball_filename=qualified_tarball_filename,
                      l_filenames=[FILENAME_NO_FILE],
                      workdir=self.workdir,
                      delete_files=False)

    def test_rw_product_and_table(self):
        """ Test reading and writing a product and table together with utility functions.
        """

        # Create sample product and table
        p = create_dpd_mer_final_catalog()
        t = MerFinalCatalogFormat.init_table(size=2)

        # Write them out together

        product_filename = SheFileNamer(type_name="TESTPROD",
                                        instance_id="0",
                                        workdir=self.workdir,
                                        subdir="",
                                        version=SHE_PPT.__version__).filename

        # Try first without specifying a table filename
        write_product_and_table(product=p,
                                product_filename=product_filename,
                                table=t,
                                workdir=self.workdir)

        table_filename = p.get_data_filename()

        # Check that the default filename generated is as expected
        assert DEFAULT_TYPE_NAME in table_filename
        assert DEFAULT_INSTANCE_ID in table_filename
        assert DEFAULT_FILE_SUBDIR in table_filename
        assert DEFAULT_FILE_EXTENSION in table_filename

        # Check that the files have been written out
        assert os.path.exists(os.path.join(self.workdir, product_filename))
        assert os.path.exists(os.path.join(self.workdir, table_filename))

        # Read the product and table back in
        p2, t2 = read_product_and_table(product_filename, workdir=self.workdir)

        # Check that they're the same as was written out
        assert p2.Header.ProductId.value() == p.Header.ProductId.value()
        assert p2.get_data_filename() == p.get_data_filename()
        assert np.all(t2 == t)

        # Now try while specifying the table filename
        input_table_filename = get_allowed_filename(type_name="TABLE", instance_id="1",
                                                    version=SHE_PPT.__version__)
        write_product_and_table(product=p,
                                product_filename=product_filename,
                                table=t,
                                table_filename=input_table_filename,
                                workdir=self.workdir)

        # Check that the files have been written out
        output_table_filename = p.get_data_filename()
        assert output_table_filename == input_table_filename
        assert os.path.exists(os.path.join(self.workdir, output_table_filename))

        # Read the product and table back in
        p3, t3 = read_product_and_table(product_filename, workdir=self.workdir)

        # Check that they're the same as was written out
        assert p3.Header.ProductId.value() == p.Header.ProductId.value()
        assert p3.get_data_filename() == p.get_data_filename()
        assert np.all(t3 == t)

        # And try reading just the table from the product
        t4 = read_table_from_product(product_filename, workdir=self.workdir)
        assert np.all(t4 == t)

    def test_safe_copy(self):
        """ Unit test of SHE_PPT.file_io.safe_copy
        """

        qualified_src_filename = os.path.join(self.src_dir, self.table_filename)
        qualified_dest_filename = os.path.join(self.dest_dir, self.table_filename)

        # Try a basic copy first, when the target doesn't yet exist
        safe_copy(qualified_src_filename, qualified_dest_filename)

        # Check that both input and output match
        src_table = read_table(self.table_filename, workdir=self.src_dir)
        dest_table = read_table(self.table_filename, workdir=self.dest_dir)

        assert np.all(src_table == dest_table)

        # Check that it succeeds without issue if the destination file exists, as it now does, unless we require the
        # destination is free
        safe_copy(qualified_src_filename, qualified_dest_filename,
                  require_dest_free=False)
        with pytest.raises(SheFileWriteError):
            safe_copy(qualified_src_filename, qualified_dest_filename,
                      require_dest_free=True)

        # Cleanup the created file for future checks
        os.remove(qualified_dest_filename)

        # Check that if the source file doesn't exist, it only raises an exception if we require that it does
        qualified_nonexistent_src_filename = os.path.join(self.src_dir, "no_file_here")

        safe_copy(qualified_nonexistent_src_filename, qualified_dest_filename,
                  require_src_exist=False)
        with pytest.raises(SheFileReadError):
            safe_copy(qualified_nonexistent_src_filename, qualified_dest_filename,
                      require_src_exist=True)

        # Check that if we copy to a directory that doesn't yet exist, that directory is created
        dest_subdir = os.path.join(self.dest_dir, "subdir")
        qualified_dest_subdir_filename = os.path.join(dest_subdir, self.table_filename)

        safe_copy(qualified_src_filename, qualified_dest_subdir_filename)

        # Cleanup created data
        shutil.rmtree(dest_subdir)

    def test_copy_product(self):
        """ Unit test for SHE_PPT.file_io.copy_product_between_dirs
        """

        qualified_src_product_filename = os.path.join(self.src_dir, self.product_filename)
        qualified_dest_product_filename = os.path.join(self.dest_dir, self.product_filename)
        qualified_dest_table_filename = os.path.join(self.dest_dir, self.table_filename)

        # Try running the function and make sure it succeeds
        copy_product_between_dirs(product_filename=self.product_filename,
                                  src_dir=self.src_dir,
                                  dest_dir=self.dest_dir)

        # Check that expected files exist and match input
        assert os.path.exists(qualified_dest_product_filename)
        assert os.path.exists(qualified_dest_table_filename)

        # Check that the copied product matches the source product
        src_product = read_xml_product(qualified_src_product_filename)
        dest_product = read_xml_product(qualified_dest_product_filename)

        assert src_product.Header.ProductId.value() == dest_product.Header.ProductId.value()
        assert src_product.get_all_filenames() == dest_product.get_all_filenames()

        # Test that the function doesn't raise any error if the destination file already exists, as it now does
        copy_product_between_dirs(product_filename=self.product_filename,
                                  src_dir=self.src_dir,
                                  dest_dir=self.dest_dir)

        # Cleanup the created files
        os.remove(qualified_dest_product_filename)
        os.remove(qualified_dest_table_filename)

    def test_copy_listfile(self):
        """ Unit test for SHE_PPT.file_io.copy_listfile_between_dirs
        """

        qualified_src_listfile_filename = os.path.join(self.src_dir, self.listfile_filename)
        qualified_dest_listfile_filename = os.path.join(self.dest_dir, self.listfile_filename)
        qualified_dest_product_filename = os.path.join(self.dest_dir, self.product_filename)
        qualified_dest_table_filename = os.path.join(self.dest_dir, self.table_filename)

        # Try running the function and make sure it succeeds
        copy_listfile_between_dirs(listfile_filename=self.listfile_filename,
                                   src_dir=self.src_dir,
                                   dest_dir=self.dest_dir)

        # Check that expected files exist and match input
        assert os.path.exists(qualified_dest_listfile_filename)
        assert os.path.exists(qualified_dest_product_filename)
        assert os.path.exists(qualified_dest_table_filename)

        # Check that the copied listfile matches the source product
        l_src_products = read_listfile(qualified_src_listfile_filename)
        l_dest_products = read_listfile(qualified_dest_listfile_filename)

        assert np.all(l_src_products == l_dest_products)

        # Test that the function doesn't raise any error if the destination file already exists, as it now does
        copy_listfile_between_dirs(listfile_filename=self.listfile_filename,
                                   src_dir=self.src_dir,
                                   dest_dir=self.dest_dir)

        # Cleanup the created files
        os.remove(qualified_dest_listfile_filename)
        os.remove(qualified_dest_product_filename)
        os.remove(qualified_dest_table_filename)

    def test_symlink_contents(self):
        """ Unit test for SHE_PPT.file_io.symlink_contents function.
        """

        # Clean out the destination directory
        shutil.rmtree(self.dest_dir)

        # Symlink the contents of the source directory to the destination directory
        symlink_contents(src_dir=self.src_dir,
                         dest_dir=self.dest_dir)

        # Check that the destination directory now contains the same files as the source directory

        for filename in os.listdir(self.src_dir):

            src_filename = os.path.join(self.src_dir, filename)
            dest_filename = os.path.join(self.dest_dir, filename)

            assert os.path.exists(dest_filename)

            if os.path.isfile(src_filename):

                # It's a file, so compare in the source and destination directory
                assert filecmp.cmp(src_filename, dest_filename), f"{src_filename} != {dest_filename}"

                # Check that the destination file is a symlink
                assert os.path.islink(dest_filename)

            else:

                assert os.path.isdir(dest_filename)

                # It's a directory, so compare the contents of the source and destination directory
                for subfilename in os.listdir(src_filename):

                    src_subfilename = os.path.join(src_filename, subfilename)
                    dest_subfilename = os.path.join(dest_filename, subfilename)

                    assert os.path.exists(dest_subfilename)

                    if os.path.isfile(src_subfilename):

                        assert filecmp.cmp(src_subfilename, dest_subfilename), \
                            f"{src_subfilename} != {dest_subfilename}"
                        assert os.path.islink(dest_subfilename)

                    else:

                        assert os.path.isdir(dest_subfilename)

                        # Stop here if it's a directory; no need to test even deeper

    def test_try_remove_file(self):
        """Unit test of the `try_remove_file` function.
        """

        # Start by writing a file to disk which we'll try to remove
        test_filename = "try_remove_file.txt"
        test_qualified_filename = get_qualified_filename(test_filename,
                                                         workdir=self.workdir)
        write_listfile(test_qualified_filename, [])

        # Try removing the file, and check that it doesn't exist after
        try_remove_file(test_qualified_filename)
        assert not os.path.exists(test_qualified_filename)

        # Now try removing a file that doesn't exist, and make sure an exception isn't raised
        try_remove_file(FILENAME_NO_FILE,
                        workdir=self.workdir,
                        warn=True)

    @pytest.mark.xfail(IS_ROOT, reason="root has unrestricted capabilities to write files")
    def test_first_in_path(self):
        """Unit test of `first_(writable_)in_path`.
        """

        # Make a path to test
        test_path = ":".join([self.src_dir, self.workdir, self.dest_dir])

        # Test we get the expected directory
        test_dir = first_in_path(test_path)
        assert test_dir == self.src_dir

        # Test we get the first writable, by making the workdir temporarily read-only
        try:
            os.chmod(self.src_dir, stat.S_IREAD)
            test_dir = first_writable_in_path(test_path)
            assert test_dir == self.workdir
        finally:
            os.chmod(self.src_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

        # Test we get the expected error when no path is writable
        try:
            os.chmod(self.src_dir, stat.S_IREAD)
            os.chmod(self.dest_dir, stat.S_IREAD)
            os.chmod(self.workdir, stat.S_IREAD)
            with pytest.raises(IOError):
                _ = first_writable_in_path(test_path)
        finally:
            os.chmod(self.workdir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            os.chmod(self.src_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            os.chmod(self.dest_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    def test_get_data_filename(self):
        """Unit test of `get_data_filename`.
        """

        # Check that we get the expected table filename for the MER Final Catalog product created for testing here
        test_filename = get_data_filename(self.product_filename, workdir=self.src_dir)
        assert test_filename == self.table_filename

        # Check that if we input the data filename directly, we get it back
        test_filename = get_data_filename(self.table_filename, workdir=self.src_dir)
        assert test_filename == self.table_filename

    @pytest.mark.xfail(IS_ROOT, reason="root has unrestricted capabilities to write files")
    def test_remove_files(self):
        """Unit test of `remove_files`.
        """

        # Create a few files, one non-writable, plus a nonexistent file
        test_filename_1 = "rm_f_1.txt"
        test_qualified_filename_1 = get_qualified_filename(test_filename_1, self.workdir)
        write_listfile(test_qualified_filename_1, [])

        test_filename_2 = "rm_f_2.txt"
        test_qualified_filename_2 = get_qualified_filename(test_filename_2, self.dest_dir)
        write_listfile(test_qualified_filename_2, [])

        qualified_noexist_filename = get_qualified_filename(FILENAME_NO_FILE, self.workdir)

        # Try removing them, and make sure no errors are raised
        try:
            os.chmod(self.dest_dir, stat.S_IREAD)
            remove_files([test_qualified_filename_1, test_qualified_filename_2, qualified_noexist_filename])
        finally:
            os.chmod(self.dest_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

        # Check that file 1 doesn't exist and file 2 does
        assert not os.path.exists(test_qualified_filename_1)
        assert os.path.exists(test_qualified_filename_2)

        # Cleanup
        try_remove_file(test_qualified_filename_2)


class TestMeasurementsProductIO(SheTestCase):
    """ A class to handle tests of functions and classes in the SHE_PPT/file_io.py module related to reading in
    measurements products.
    """

    # Define some constant class attributes
    LMC_TABLE_FILENAME = "data/lmc_table.fits"
    KSB_TABLE_FILENAME = "data/ksb_table.fits"
    SHM_PRODUCT_FILENAME = "shm_product.xml"

    def post_setup(self):
        """ Perform some setup tasks for functions tested here, setting up data which is used for multiple tests.
        """

        lensmc_table_gen = MockShearEstimateTableGenerator(workdir=self.workdir,
                                                           num_test_points=4,
                                                           method=ShearEstimationMethods.LENSMC,
                                                           table_filename=self.LMC_TABLE_FILENAME,
                                                           seed=EST_SEED)
        lensmc_table_gen.write_mock_table()

        ksb_table_gen = MockShearEstimateTableGenerator(workdir=self.workdir,
                                                        num_test_points=4,
                                                        method=ShearEstimationMethods.KSB,
                                                        table_filename=self.KSB_TABLE_FILENAME,
                                                        seed=EST_SEED + 1)
        ksb_table_gen.write_mock_table()

        self.shm_product = create_dpd_she_validated_measurements(KSB_filename=self.KSB_TABLE_FILENAME,
                                                                 LensMC_filename=self.LMC_TABLE_FILENAME)
        write_xml_product(self.shm_product, self.SHM_PRODUCT_FILENAME, workdir=self.workdir)

        # Since astropy or numpy converts NaN values to masked when reading in a table, we read-in the tables here
        # from what we just wrote, rather than comparing to what's in-memory (which will have some NaNs, as opposed
        # to the masked values when read in)
        self.lmc_table = read_table(self.LMC_TABLE_FILENAME, workdir=self.workdir)
        self.ksb_table = read_table(self.KSB_TABLE_FILENAME, workdir=self.workdir)

        # Get the expected product ID for when the product is read in
        self.ex_product_id = self.shm_product.Header.ProductId.value()

    def test_read_d_l_method_table_filenames(self):
        """Unit test of `read_d_l_method_table_filenames` function.
        """

        # Try reading in the product created at init
        (d_l_method_table_filenames,
         l_products) = read_d_l_method_table_filenames(l_product_filenames=[self.SHM_PRODUCT_FILENAME],
                                                       workdir=self.workdir,
                                                       log_info=True)

        # Check that the filenames are as expected
        assert d_l_method_table_filenames[ShearEstimationMethods.LENSMC][0] == self.LMC_TABLE_FILENAME
        assert d_l_method_table_filenames[ShearEstimationMethods.KSB][0] == self.KSB_TABLE_FILENAME

        # Check that the product is as expected
        test_product = l_products[0]
        assert isinstance(test_product, dpdSheValidatedMeasurements)
        assert test_product.Header.ProductId.value() == self.ex_product_id

    def test_read_d_method_table_filenames(self):
        """Unit test of `read_d_method_table_filenames` function.
        """

        # Try reading in the product created at init
        (d_method_table_filenames,
         test_product) = read_d_method_table_filenames(product_filename=self.SHM_PRODUCT_FILENAME,
                                                       workdir=self.workdir,
                                                       log_info=True)

        # Check that the filenames are as expected
        assert d_method_table_filenames[ShearEstimationMethods.LENSMC] == self.LMC_TABLE_FILENAME
        assert d_method_table_filenames[ShearEstimationMethods.KSB] == self.KSB_TABLE_FILENAME

        # Check that the product is as expected
        assert isinstance(test_product, dpdSheValidatedMeasurements)
        assert test_product.Header.ProductId.value() == self.ex_product_id

    def test_read_d_l_method_tables(self):
        """Unit test of `read_d_l_method_tables` function.
        """

        # Try reading in the product created at init
        (d_l_method_tables,
         l_products) = read_d_l_method_tables(l_product_filenames=[self.SHM_PRODUCT_FILENAME],
                                              workdir=self.workdir,
                                              log_info=True)

        # Check that the tables are as expected
        test_lmc_table = d_l_method_tables[ShearEstimationMethods.LENSMC][0]
        for colname in self.lmc_table.colnames:
            assert np.all(test_lmc_table[colname] == self.lmc_table[colname])
        test_ksb_table = d_l_method_tables[ShearEstimationMethods.KSB][0]
        for colname in self.ksb_table.colnames:
            assert np.all(test_ksb_table[colname] == self.ksb_table[colname])

        # Check that the product is as expected
        test_product = l_products[0]
        assert isinstance(test_product, dpdSheValidatedMeasurements)
        assert test_product.Header.ProductId.value() == self.ex_product_id

    def test_read_d_method_tables(self):
        """Unit test of `read_d_method_tables` function.
        """

        # Try reading in the product created at init
        (d_method_tables,
         test_product) = read_d_method_tables(product_filename=self.SHM_PRODUCT_FILENAME,
                                              workdir=self.workdir,
                                              log_info=True)

        # Check that the tables are as expected
        test_lmc_table = d_method_tables[ShearEstimationMethods.LENSMC]
        for colname in self.lmc_table.colnames:
            assert np.all(test_lmc_table[colname] == self.lmc_table[colname])
        test_ksb_table = d_method_tables[ShearEstimationMethods.KSB]
        for colname in self.ksb_table.colnames:
            assert np.all(test_ksb_table[colname] == self.ksb_table[colname])

        # Check that the product is as expected
        assert isinstance(test_product, dpdSheValidatedMeasurements)
        assert test_product.Header.ProductId.value() == self.ex_product_id
