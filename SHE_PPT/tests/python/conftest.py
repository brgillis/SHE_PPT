#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
:file: tests/python/conftest.py

:date: 21/02/2023
:author: Gordon Gibb
"""

import pytest

import os

from SHE_PPT.testing import (
    generate_mock_mer_catalogues,
    generate_mock_vis_images,
    generate_mock_psf_model_image,
    generate_mock_reprojected_segmentation_maps,
    generate_mock_object_id_list,
)
from SHE_PPT.file_io import write_listfile, read_listfile

from SHE_PPT import SHE_PPT_RELEASE_STRING as lensmc_version
from SHE_PPT.she_io.hdf5 import convert_to_hdf5

from ST_DM_FilenameProvider.FilenameProvider import FileNameProvider

from ST_DM_DmUtils.DmUtils import read_product_metadata

NUM_DETECTORS = 1
NUM_DETECTORS_CCD = 36
NUM_DETECTORS_QUADRANT = 144
NUM_OBJECTS_PER_DETECTOR = 2
OBJSIZE = 2.5
NUM_EXP = 4


@pytest.fixture
def workdir(tmpdir):
    workdir = tmpdir

    # make the datadir
    datadir = os.path.join(workdir, "data")
    os.mkdir(datadir)

    return workdir


@pytest.fixture
def num_detectors():
    return NUM_DETECTORS


@pytest.fixture
def num_detectors_ccd():
    return NUM_DETECTORS_CCD


@pytest.fixture
def num_detectors_quadrant():
    return NUM_DETECTORS_QUADRANT


@pytest.fixture
def num_objects_per_detector():
    return NUM_OBJECTS_PER_DETECTOR


@pytest.fixture
def num_objects():
    return NUM_OBJECTS_PER_DETECTOR * NUM_DETECTORS


@pytest.fixture
def objsize():
    return OBJSIZE


@pytest.fixture
def input_products(num_detectors, workdir, num_objects_per_detector, objsize):
    """Creates the data products/listfiles needed as an input to the various executables"""
    exposure_product, sky_coords, pixel_coords, detectors, wcs_list = generate_mock_vis_images.create_exposure(
        n_detectors=num_detectors, workdir=workdir, n_objs_per_det=num_objects_per_detector, objsize=objsize, seed=2
    )
    catalogue_product, object_ids = generate_mock_mer_catalogues.create_catalogue(
        obj_coords=sky_coords, workdir=workdir
    )
    id_list_product = generate_mock_object_id_list.create_object_id_list(object_ids, workdir=workdir)
    psf_product = generate_mock_psf_model_image.create_model_image_product(object_ids, pixel_coords, workdir=workdir)
    seg_map_product = generate_mock_reprojected_segmentation_maps.create_reprojected_segmentation_map(
        object_ids, pixel_coords, detectors, wcs_list, objsize=objsize, workdir=workdir
    )

    # create the contents of the listfiles for the vis and mer products
    exposure_list = [exposure_product for i in range(NUM_EXP)]
    catalogue_list = [catalogue_product]
    psf_list = [psf_product for i in range(NUM_EXP)]
    seg_map_list = [seg_map_product for i in range(NUM_EXP)]

    # write them to disk
    data_images = os.path.join(workdir, "data_images.json")
    write_listfile(data_images, exposure_list)

    mer_final_catalog_tables = os.path.join(workdir, "mer_final_catalog_tables.json")
    write_listfile(mer_final_catalog_tables, catalogue_list)

    psf_model_images = os.path.join(workdir, "psf_model_images.json")
    write_listfile(psf_model_images, psf_list)

    seg_maps = os.path.join(workdir, "segmaps.json")
    write_listfile(seg_maps, seg_map_list)

    return "data_images.json", "mer_final_catalog_tables.json", "psf_model_images.json", "segmaps.json", id_list_product


@pytest.fixture
def input_fits(workdir, input_products):
    """Returns the input FITS files (from input_products). Only one file from each is returned (e.g. one exposure)"""

    vis_listfile, mer_listfile, psf_listfile, seg_listfile, _ = input_products

    vis_prod = read_listfile(vis_listfile, workdir=workdir)[0]
    mer_prod = read_listfile(mer_listfile, workdir=workdir)[0]
    psf_prod = read_listfile(psf_listfile, workdir=workdir)[0]
    seg_prod = read_listfile(seg_listfile, workdir=workdir)[0]

    vis_dpd = read_product_metadata(os.path.join(workdir, vis_prod))
    mer_dpd = read_product_metadata(os.path.join(workdir, mer_prod))
    psf_dpd = read_product_metadata(os.path.join(workdir, psf_prod))
    seg_dpd = read_product_metadata(os.path.join(workdir, seg_prod))

    det = vis_dpd.Data.DataStorage.DataContainer.FileName
    wgt = vis_dpd.Data.WeightStorage.DataContainer.FileName
    bkg = vis_dpd.Data.BackgroundStorage.DataContainer.FileName
    mer = mer_dpd.Data.DataStorage.DataContainer.FileName
    psf = psf_dpd.Data.DataStorage.DataContainer.FileName
    seg = seg_dpd.Data.DataStorage.DataContainer.FileName

    return det, wgt, bkg, mer, psf, seg


@pytest.fixture
def input_hdf5(workdir, input_fits):
    """Returns a HDF5 file corresponding to the data in input_fits"""

    det, wgt, bkg, _, _, seg = input_fits

    det_file = os.path.join(workdir, "data", det)
    wgt_file = os.path.join(workdir, "data", wgt)
    bkg_file = os.path.join(workdir, "data", bkg)
    seg_file = os.path.join(workdir, "data", seg)

    output_filename = FileNameProvider().get_allowed_filename(
        type_name="EXP",
        instance_id="HDF5",
        extension=".h5",
        release=lensmc_version,
        processing_function="SHE",
    )

    qualified_output_filename = os.path.join(workdir, "data", output_filename)

    convert_to_hdf5(det_file, bkg_file, wgt_file, seg_file, qualified_output_filename, chunk=(100, 100))

    return output_filename


@pytest.fixture
def hdf5_listfile(workdir, input_hdf5):
    """Returns the listfile containing the HDF5 files"""

    listfile_filename = FileNameProvider().get_allowed_filename(
        type_name="HDF5",
        instance_id="LISTFILE",
        extension=".json",
        release=lensmc_version,
        processing_function="SHE",
    )

    write_listfile(os.path.join(workdir, listfile_filename), [input_hdf5] * NUM_EXP)

    return listfile_filename


@pytest.fixture
def input_products_ccd(num_detectors_ccd, workdir, num_objects_per_detector, objsize):
    """Creates the data products/listfiles needed as an input to the various executables"""
    exposure_product, sky_coords, pixel_coords, detectors, wcs_list = generate_mock_vis_images.create_exposure(
        n_detectors=num_detectors_ccd, workdir=workdir, n_objs_per_det=num_objects_per_detector, objsize=objsize, seed=2
    )
    catalogue_product, object_ids = generate_mock_mer_catalogues.create_catalogue(
        obj_coords=sky_coords, workdir=workdir
    )
    id_list_product = generate_mock_object_id_list.create_object_id_list(object_ids, workdir=workdir)
    psf_product = generate_mock_psf_model_image.create_model_image_product(object_ids, pixel_coords, workdir=workdir)
    seg_map_product = generate_mock_reprojected_segmentation_maps.create_reprojected_segmentation_map(
        object_ids, pixel_coords, detectors, wcs_list, objsize=objsize, workdir=workdir
    )

    # create the contents of the listfiles for the vis and mer products
    exposure_list = [exposure_product for i in range(NUM_EXP)]
    catalogue_list = [catalogue_product]
    psf_list = [psf_product for i in range(NUM_EXP)]
    seg_map_list = [seg_map_product for i in range(NUM_EXP)]

    # write them to disk
    data_images = os.path.join(workdir, "data_images.json")
    write_listfile(data_images, exposure_list)

    mer_final_catalog_tables = os.path.join(workdir, "mer_final_catalog_tables.json")
    write_listfile(mer_final_catalog_tables, catalogue_list)

    psf_model_images = os.path.join(workdir, "psf_model_images.json")
    write_listfile(psf_model_images, psf_list)

    seg_maps = os.path.join(workdir, "segmaps.json")
    write_listfile(seg_maps, seg_map_list)

    return "data_images.json", "mer_final_catalog_tables.json", "psf_model_images.json", "segmaps.json", id_list_product


@pytest.fixture
def input_fits_ccd(workdir, input_products_ccd):
    """Returns the input FITS files (from input_products). Only one file from each is returned (e.g. one exposure)"""

    vis_listfile, mer_listfile, psf_listfile, seg_listfile, _ = input_products_ccd

    vis_prod = read_listfile(vis_listfile, workdir=workdir)[0]
    mer_prod = read_listfile(mer_listfile, workdir=workdir)[0]
    psf_prod = read_listfile(psf_listfile, workdir=workdir)[0]
    seg_prod = read_listfile(seg_listfile, workdir=workdir)[0]

    vis_dpd = read_product_metadata(os.path.join(workdir, vis_prod))
    mer_dpd = read_product_metadata(os.path.join(workdir, mer_prod))
    psf_dpd = read_product_metadata(os.path.join(workdir, psf_prod))
    seg_dpd = read_product_metadata(os.path.join(workdir, seg_prod))

    det = vis_dpd.Data.DataStorage.DataContainer.FileName
    wgt = vis_dpd.Data.WeightStorage.DataContainer.FileName
    bkg = vis_dpd.Data.BackgroundStorage.DataContainer.FileName
    mer = mer_dpd.Data.DataStorage.DataContainer.FileName
    psf = psf_dpd.Data.DataStorage.DataContainer.FileName
    seg = seg_dpd.Data.DataStorage.DataContainer.FileName

    return det, wgt, bkg, mer, psf, seg


@pytest.fixture
def input_hdf5_ccd(workdir, input_fits_ccd):
    """Returns a HDF5 file corresponding to the data in input_fits"""

    det, wgt, bkg, _, _, seg = input_fits_ccd

    det_file = os.path.join(workdir, "data", det)
    wgt_file = os.path.join(workdir, "data", wgt)
    bkg_file = os.path.join(workdir, "data", bkg)
    seg_file = os.path.join(workdir, "data", seg)

    output_filename = FileNameProvider().get_allowed_filename(
        type_name="EXP",
        instance_id="HDF5",
        extension=".h5",
        release=lensmc_version,
        processing_function="SHE",
    )

    qualified_output_filename = os.path.join(workdir, "data", output_filename)

    convert_to_hdf5(det_file, bkg_file, wgt_file, seg_file, qualified_output_filename, chunk=(100, 100))

    return output_filename


@pytest.fixture
def hdf5_listfile_ccd(workdir, input_hdf5_ccd):
    """Returns the listfile containing the HDF5 files"""

    listfile_filename = FileNameProvider().get_allowed_filename(
        type_name="HDF5",
        instance_id="LISTFILE",
        extension=".json",
        release=lensmc_version,
        processing_function="SHE",
    )

    write_listfile(os.path.join(workdir, listfile_filename), [input_hdf5_ccd] * NUM_EXP)

    return listfile_filename


@pytest.fixture
def input_products_quadrant(num_detectors_quadrant, workdir, num_objects_per_detector, objsize):
    """Creates the data products/listfiles needed as an input to the various executables"""
    exposure_product, sky_coords, pixel_coords, detectors, wcs_list = generate_mock_vis_images.create_exposure(
        n_detectors=num_detectors_quadrant,
        workdir=workdir,
        n_objs_per_det=num_objects_per_detector,
        objsize=objsize,
        seed=2,
    )
    catalogue_product, object_ids = generate_mock_mer_catalogues.create_catalogue(
        obj_coords=sky_coords, workdir=workdir
    )
    id_list_product = generate_mock_object_id_list.create_object_id_list(object_ids, workdir=workdir)
    psf_product = generate_mock_psf_model_image.create_model_image_product(object_ids, pixel_coords, workdir=workdir)
    seg_map_product = generate_mock_reprojected_segmentation_maps.create_reprojected_segmentation_map(
        object_ids, pixel_coords, detectors, wcs_list, objsize=objsize, workdir=workdir
    )

    # create the contents of the listfiles for the vis and mer products
    exposure_list = [exposure_product for i in range(NUM_EXP)]
    catalogue_list = [catalogue_product]
    psf_list = [psf_product for i in range(NUM_EXP)]
    seg_map_list = [seg_map_product for i in range(NUM_EXP)]

    # write them to disk
    data_images = os.path.join(workdir, "data_images.json")
    write_listfile(data_images, exposure_list)

    mer_final_catalog_tables = os.path.join(workdir, "mer_final_catalog_tables.json")
    write_listfile(mer_final_catalog_tables, catalogue_list)

    psf_model_images = os.path.join(workdir, "psf_model_images.json")
    write_listfile(psf_model_images, psf_list)

    seg_maps = os.path.join(workdir, "segmaps.json")
    write_listfile(seg_maps, seg_map_list)

    return "data_images.json", "mer_final_catalog_tables.json", "psf_model_images.json", "segmaps.json", id_list_product


@pytest.fixture
def input_fits_quadrant(workdir, input_products_quadrant):
    """Returns the input FITS files (from input_products). Only one file from each is returned (e.g. one exposure)"""

    vis_listfile, mer_listfile, psf_listfile, seg_listfile, _ = input_products_quadrant

    vis_prod = read_listfile(vis_listfile, workdir=workdir)[0]
    mer_prod = read_listfile(mer_listfile, workdir=workdir)[0]
    psf_prod = read_listfile(psf_listfile, workdir=workdir)[0]
    seg_prod = read_listfile(seg_listfile, workdir=workdir)[0]

    vis_dpd = read_product_metadata(os.path.join(workdir, vis_prod))
    mer_dpd = read_product_metadata(os.path.join(workdir, mer_prod))
    psf_dpd = read_product_metadata(os.path.join(workdir, psf_prod))
    seg_dpd = read_product_metadata(os.path.join(workdir, seg_prod))

    det = vis_dpd.Data.DataStorage.DataContainer.FileName
    wgt = vis_dpd.Data.WeightStorage.DataContainer.FileName
    bkg = vis_dpd.Data.BackgroundStorage.DataContainer.FileName
    mer = mer_dpd.Data.DataStorage.DataContainer.FileName
    psf = psf_dpd.Data.DataStorage.DataContainer.FileName
    seg = seg_dpd.Data.DataStorage.DataContainer.FileName

    return det, wgt, bkg, mer, psf, seg


@pytest.fixture
def input_hdf5_quadrant(workdir, input_fits_quadrant):
    """Returns a HDF5 file corresponding to the data in input_fits"""

    det, wgt, bkg, _, _, seg = input_fits_quadrant

    det_file = os.path.join(workdir, "data", det)
    wgt_file = os.path.join(workdir, "data", wgt)
    bkg_file = os.path.join(workdir, "data", bkg)
    seg_file = os.path.join(workdir, "data", seg)

    output_filename = FileNameProvider().get_allowed_filename(
        type_name="EXP",
        instance_id="HDF5",
        extension=".h5",
        release=lensmc_version,
        processing_function="SHE",
    )

    qualified_output_filename = os.path.join(workdir, "data", output_filename)

    convert_to_hdf5(det_file, bkg_file, wgt_file, seg_file, qualified_output_filename, chunk=(100, 100))

    return output_filename


@pytest.fixture
def hdf5_listfile_quadrant(workdir, input_hdf5_quadrant):
    """Returns the listfile containing the HDF5 files"""

    listfile_filename = FileNameProvider().get_allowed_filename(
        type_name="HDF5",
        instance_id="LISTFILE",
        extension=".json",
        release=lensmc_version,
        processing_function="SHE",
    )

    write_listfile(os.path.join(workdir, listfile_filename), [input_hdf5_quadrant] * NUM_EXP)

    return listfile_filename
