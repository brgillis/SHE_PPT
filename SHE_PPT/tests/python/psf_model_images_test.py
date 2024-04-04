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
:file: tests/python/psf_model_images_test.py

:date: 07/11/2022
:author: Gordon Gibb
"""

import pytest
import os

import numpy as np
import json


from SHE_PPT.she_io.psf_model_images import (
    PSFModelImageHDF5,
    PSFModelImage,
    read_psf_model_images,
    ObjectModelImage,
    PSFModelImagesWriter
)

# NOTE the file conftest.py contains the pytest fixtures used by this test

PSF_SHAPE = (480, 480)
OVERSAMPLING_FACTOR = 3
OBJECT_ID_LIST = [0, 1, 2, 3]


def validate_psf_model_image(psf):
    """Tests the API of a PSFModelImages object"""

    object_ids = psf.table["OBJECT_ID"]

    # check that a valid object id returns ndarrays
    object_id = object_ids[0]
    model = psf[object_id]
    assert type(model) is ObjectModelImage, "Output is an unexpected type"
    assert type(model.bulge) is np.ndarray, "Bulge PSF is an unexpected type"
    assert type(model.disk) is np.ndarray, "Disk PSF is an unexpected type"
    assert type(model.quality_flag) is np.int64, f"Quality flag is unexpected type: {type(model.quality_flag)}"

    # check that an invalid object id raises an exception
    while True:
        invalid_obj_id = np.random.randint(0, 2**32 - 1)
        if invalid_obj_id not in object_ids:
            break

    with pytest.raises(KeyError):
        model = psf[invalid_obj_id]


class Testpsf_model_images(object):
    def test_PSFModelImage(self, workdir, input_fits, psf_oversampling_factor):
        """Tests the API of the PSFModelImages objects"""
        _, _, _, _, psf_file_hdf5, _ = input_fits

        qualified_h5_file = os.path.join(workdir, "data", psf_file_hdf5)

        # Validate the PSFModelImages object
        psf_h5 = PSFModelImageHDF5(qualified_h5_file)
        validate_psf_model_image(psf_h5)
        assert psf_h5.get_oversampling_factor() == psf_oversampling_factor

    def test_read_psf_model_images(self, workdir, input_products, num_exposures):
        _, _, psf_listfile, _, _ = input_products

        with open(os.path.join(workdir, psf_listfile)) as fs:
            psf_prods = json.load(fs)
            print(psf_prods)

        psfs = read_psf_model_images(psf_prods, workdir)

        assert (
            len(psf_prods) == num_exposures
        ), "length of psf_listfile (%d) does not match the number of objects (%d)" % (
            len(psf_prods),
            num_exposures,
        )

        for psf in psfs:
            assert issubclass(type(psf), PSFModelImage), "Returned PSF object does not seem to be the correct type"


class TestPSFModelImagesWriter:
    """Tests the PSFModelImagesWriter class"""

    def test_writer(self, workdir):
        """Tests thw writer under basic conditions - write all objects"""

        psf_filename = workdir / "psf.h5"

        with PSFModelImagesWriter(OBJECT_ID_LIST, psf_filename, OVERSAMPLING_FACTOR) as writer:
            psfs = []
            for obj in OBJECT_ID_LIST:
                psf = np.random.random(PSF_SHAPE)
                psfs.append(psf)
                writer.write_psf(obj, psf)

        psf_models = PSFModelImageHDF5(psf_filename)
        for obj, psf in zip(OBJECT_ID_LIST, psfs):
            image = psf_models[obj]
            assert np.array_equal(image.bulge, psf)

        table = psf_models.table
        assert table["MODELLED"].all()

        assert psf_models.file.attrs["PSF_OVERSAMPLING_FACTOR"] == OVERSAMPLING_FACTOR

    def test_writer_missing(self, workdir):
        """Tests that PSFs for objects not written to the file are empty arrays"""

        psf_filename = workdir / "psf.h5"

        with PSFModelImagesWriter(OBJECT_ID_LIST, psf_filename, OVERSAMPLING_FACTOR) as writer:
            psf = np.random.random(PSF_SHAPE)
            writer.write_psf(OBJECT_ID_LIST[0], psf)

        psf_models = PSFModelImageHDF5(psf_filename)

        for obj_id in OBJECT_ID_LIST[1:]:
            image = psf_models[obj_id]
            assert image.bulge.size == 0

        for row in psf_models.table[1:]:
            assert bool(row["MODELLED"]) is False

    def test_writer_invalid_object(self, workdir):
        """Tests that the writer raises an error if an invalid object is written to it"""

        psf_filename = workdir / "psf.h5"

        with PSFModelImagesWriter([], psf_filename, OVERSAMPLING_FACTOR) as writer:
            psf = np.random.random(PSF_SHAPE)
            with pytest.raises(KeyError, match="Unexpected object id"):
                writer.write_psf(0, psf)

    def test_writer_already_finalised(self, workdir):
        """Tests that the writer raises an exception if it has already been finalised"""

        psf_filename = workdir / "psf.h5"

        writer = PSFModelImagesWriter(OBJECT_ID_LIST, psf_filename, OVERSAMPLING_FACTOR)
        writer.close()

        with pytest.raises(RuntimeError, match="This PSFWriter object is finalised!"):
            psf = np.random.random(PSF_SHAPE)
            writer.write_psf(OBJECT_ID_LIST[0], psf)

        with pytest.raises(RuntimeError, match="This PSFWriter object is finalised!"):
            writer.close()
