""" @file mock_data_generation_test.py

    Created 30 June 2022

    Tests of mock data creation functions.
"""

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

__updated__ = "2022-06-30"

import os

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.units import degree
from astropy.wcs import WCS
from astropy.io import fits

from SHE_PPT.file_io import read_xml_product
from SHE_PPT.products import (
    mer_final_catalog,
    she_exposure_segmentation_map,
    she_object_id_list,
    she_psf_model_image,
    vis_calibrated_frame,
)
from SHE_PPT.testing.generate_mock_mer_catalogues import create_catalogue
from SHE_PPT.testing.generate_mock_object_id_list import create_object_id_list
from SHE_PPT.testing.generate_mock_psf_model_image import create_model_image_product
from SHE_PPT.testing.generate_mock_reprojected_segmentation_maps import create_reprojected_segmentation_map, masksize
from SHE_PPT.testing.generate_mock_vis_images import create_exposure
from SHE_PPT.testing.utility import SheTestCase

RANDOM_SEED = 1

rng = np.random.RandomState(RANDOM_SEED)


class TestMockData(SheTestCase):
    def test_vis_images(self, num_detectors, num_objects_per_detector, num_objects):
        detector_shape = (200, 200)
        workdir = self.workdir

        # Create the frame product
        prod_filename, sky_coords, img_coords, detectors, wcs_list = create_exposure(
            n_detectors=num_detectors,
            detector_shape=detector_shape,
            workdir=workdir,
            n_objs_per_det=num_objects_per_detector,
        )
        # check the product is readable, and that its FITS files exist
        # NOTE: We don't check the validity of the FITS files
        dpd = read_xml_product(prod_filename, workdir=workdir)

        assert type(dpd) is vis_calibrated_frame.dpdVisCalibratedFrame

        det = dpd.get_data_filename()
        assert os.path.exists(os.path.join(workdir, det))

        wgt = dpd.get_wgt_filename()
        assert os.path.exists(os.path.join(workdir, wgt))

        bkg = dpd.get_bkg_filename()
        assert os.path.exists(os.path.join(workdir, bkg))

        # check the sky_coords are valid
        assert len(sky_coords) == num_objects
        for c in sky_coords:
            assert type(c) is SkyCoord

        # check that the img_coords are valid
        assert len(img_coords) == num_objects
        for c in img_coords:
            assert type(c) is tuple
            assert len(c) == 2

        # check the detectors list
        assert len(detectors) == num_objects
        assert (np.unique(detectors) == np.asarray([i for i in range(num_detectors)])).all()

        # check the wcs list
        assert len(wcs_list) == num_detectors
        for w in wcs_list:
            assert type(w) is WCS

    def test_mer_catalogues(self, num_objects):

        workdir = self.workdir

        # generate random coordinates
        obj_coords = [SkyCoord(ra=np.random.random(), dec=np.random.random(), unit=degree) for i in range(num_objects)]

        # create product
        prod_filename, object_ids = create_catalogue(obj_coords, workdir)

        # verify output product
        dpd = read_xml_product(prod_filename, workdir=workdir)
        assert type(dpd) is mer_final_catalog.dpdMerFinalCatalog

        # Make sure the FITS file was created
        table = dpd.get_data_filename()
        assert os.path.exists(os.path.join(workdir, table))

        # verify object_ids
        assert len(object_ids) == num_objects
        assert len(np.unique(object_ids)) == num_objects

    def test_object_ids(self):

        workdir = self.workdir
        object_list = [i for i in range(10)]

        # create the product

        prod_filename = create_object_id_list(object_list, workdir=workdir)

        # make sure the product is correct
        dpd = read_xml_product(prod_filename, workdir=workdir)
        assert type(dpd) is she_object_id_list.dpdSheObjectIdList

        # make sure we can get the object_list from the product
        obj_l = dpd.Data.ObjectIdList
        assert obj_l == object_list

    def test_psf_model_image(self, num_objects):

        workdir = self.workdir

        object_ids = [i for i in range(num_objects)]
        pixel_coords = [tuple(np.random.random(2)) for i in range(num_objects)]

        # create the product
        prod_filename = create_model_image_product(object_ids, pixel_coords, workdir=workdir)

        # check the product is valid
        dpd = read_xml_product(prod_filename, workdir=workdir)
        assert type(dpd) is she_psf_model_image.dpdShePsfModelImage

        # make sure the fits exists
        model_fits = dpd.get_data_filename()
        assert os.path.exists(os.path.join(workdir, model_fits))

    def test_mer_segmentation_map_ccd(self, num_detectors, num_objects_per_detector, num_objects):

        workdir = self.workdir
        detector_shape = (100, 100)
        objsize = 2.5

        ny, nx = detector_shape

        # allowed min/max coordinates of the object positions
        xmin = ymin = objsize * masksize
        xmax = nx - objsize * masksize
        ymax = ny - objsize * masksize

        # set up the inputs
        object_ids = [i + 1 for i in range(num_objects)]

        pixel_coords = [(rng.uniform(xmin, xmax), rng.uniform(ymin, ymax)) for i in range(num_objects)]

        detectors = [i // num_objects_per_detector for i in range(num_objects)]

        wcs_list = [WCS() for i in range(num_detectors)]

        # create the product
        prod_filename = create_reprojected_segmentation_map(
            object_ids,
            pixel_coords,
            detectors,
            wcs_list,
            workdir=workdir,
            detector_shape=detector_shape,
            objsize=objsize,
            use_quadrant=False,
        )

        # check the product is valid
        dpd = read_xml_product(prod_filename, workdir=workdir)
        assert type(dpd) is she_exposure_segmentation_map.dpdSheExposureReprojectedSegmentationMap

        # make sure its FITS file exists
        map_fits = dpd.get_data_filename()
        qualified_fits_filename = os.path.join(workdir, map_fits)
        assert os.path.exists(qualified_fits_filename)

        # Nominal test of validity of segmap - make sure pixel values are correct at the centre of the objects
        with fits.open(qualified_fits_filename) as hdul:
            for det in range(num_detectors):
                data = hdul[det + 1].data

                for i, (x, y) in enumerate(pixel_coords):
                    if detectors[i] != det:
                        # object not on this detector
                        continue

                    assert (
                        data[int(y), int(x)] == object_ids[i]
                    ), "Segmentation map has the wrong value at the object's location"

    def test_mer_segmentation_map_quadrant(self, num_detectors, num_objects_per_detector, num_objects):

        workdir = self.workdir
        detector_shape = (100, 100)
        objsize = 2.5

        ny, nx = detector_shape

        # allowed min/max coordinates of the object positions
        xmin = ymin = objsize * masksize
        xmax = nx - objsize * masksize
        ymax = ny - objsize * masksize

        # set up the inputs
        object_ids = [i + 1 for i in range(num_objects)]

        pixel_coords = [(rng.uniform(xmin, xmax), rng.uniform(ymin, ymax)) for i in range(num_objects)]

        detectors = [i // num_objects_per_detector for i in range(num_objects)]

        wcs_list = [WCS() for i in range(num_detectors)]

        # create the product
        prod_filename = create_reprojected_segmentation_map(
            object_ids,
            pixel_coords,
            detectors,
            wcs_list,
            workdir=workdir,
            detector_shape=detector_shape,
            objsize=objsize,
            use_quadrant=True,
        )

        # check the product is valid
        dpd = read_xml_product(prod_filename, workdir=workdir)
        assert type(dpd) is she_exposure_segmentation_map.dpdSheExposureReprojectedSegmentationMap

        # make sure its FITS file exists
        map_fits = dpd.get_data_filename()
        qualified_fits_filename = os.path.join(workdir, map_fits)
        assert os.path.exists(qualified_fits_filename)

        # Nominal test of validity of segmap - make sure pixel values are correct at the centre of the objects
        with fits.open(qualified_fits_filename) as hdul:
            for det in range(num_detectors):
                data = hdul[det + 1].data

                for i, (x, y) in enumerate(pixel_coords):
                    if detectors[i] != det:
                        # object not on this detector
                        continue

                    assert (
                        data[int(y), int(x)] == object_ids[i]
                    ), "Segmentation map has the wrong value at the object's location"
