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
    PSFModelImageFITS,
    PSFModelImageHDF5,
    PSFModelImage,
    read_psf_model_images,
    ObjectModelImage,
)

# NOTE the file conftest.py contains the pytest fixtures used by this test


def validate_psf_model_image(psf):
    """Tests the API of a PSFModelImages object"""

    object_ids = psf.table["OBJECT_ID"]

    # check that a valid object id returns ndarrays
    object_id = object_ids[0]
    model = psf[object_id]
    assert type(model) is ObjectModelImage, "Output is an unexpected type"
    assert type(model.bulge) is np.ndarray, "Bulge PSF is an unexpected type"
    assert type(model.disk) is np.ndarray, "Disk PSF is an unexpected type"
    assert type(model.quality_flag) is np.int32, "Quality flag is unexpected type"

    # check that an invalid object id raises an exception
    while True:
        invalid_obj_id = np.random.randint(0, 2**32 - 1)
        if invalid_obj_id not in object_ids:
            break

    with pytest.raises(KeyError):
        model = psf[invalid_obj_id]


class Testpsf_model_images(object):
    def test_PSFModelImage(self, workdir, input_fits):
        """Tests the API of the PSFModelImages objects (FITS and HDF5 versions)"""
        _, _, _, _, psf_file_fits, psf_file_hdf5, _ = input_fits

        qualified_fits_file = os.path.join(workdir, "data", psf_file_fits)
        qualified_h5_file = os.path.join(workdir, "data", psf_file_hdf5)

        # Validate the PSFModelImages objects
        psf_fits = PSFModelImageFITS(qualified_fits_file)
        validate_psf_model_image(psf_fits)
        with pytest.raises(NotImplementedError):
            psf_fits.get_oversampling_factor()

        psf_h5 = PSFModelImageHDF5(qualified_h5_file)
        validate_psf_model_image(psf_h5)
        psf_h5.get_oversampling_factor()

    def test_read_psf_model_images(self, workdir, input_products, num_exposures):
        _, _, psf_listfile_fits, psf_listfile_hdf5, _, _ = input_products

        for psf_listfile in (psf_listfile_fits, psf_listfile_hdf5):

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
