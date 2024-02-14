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
import h5py
import json

from astropy.io import fits
from astropy.table import Table


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
        _, _, _, _, psf_file, _ = input_fits

        psf_fits = os.path.join(workdir, "data", psf_file)

        # Convert the FITS PSFModelImages file to hdf5
        psf_h5 = os.path.splitext(psf_fits)[0] + ".h5"

        hdul = fits.open(psf_fits)
        t = Table.read(hdul[1])

        # create HDF5 version of this file
        with h5py.File(psf_h5, "w") as f:
            g = f.create_group("IMAGES")
            for row in t:
                obj_id = row["OBJECT_ID"]
                hdu = row["SHE_PSF_BULGE_INDEX"]
                data = hdul[hdu].data
                g.create_dataset(str(obj_id), data=data)
            t.write(f, "TABLE")

        hdul.close()

        # Validate the PSFModelImages objects
        validate_psf_model_image(PSFModelImageFITS(psf_fits))
        validate_psf_model_image(PSFModelImageHDF5(psf_h5))

    def test_read_psf_model_images(self, workdir, input_products, num_exposures):
        _, _, psf_listfile, _, _ = input_products

        with open(os.path.join(workdir, psf_listfile)) as fs:
            psf_prods = json.load(fs)
            print(psf_prods)

        psfs = read_psf_model_images(psf_prods, workdir)

        assert psfs is not None, "Returned PSF object list is None"

        assert (
            len(psf_prods) == num_exposures
        ), "length of psf_listfile (%d) does not match the number of objects (%d)" % (
            len(psf_prods),
            num_exposures,
        )

        for psf in psfs:
            assert issubclass(type(psf), PSFModelImage), "Returned PSF object does not seem to be the correct type"

    def test_read_psf_model_images_quadrant(self, workdir, input_products_quadrant, num_exposures):
        _, _, psf_listfile, _, _ = input_products_quadrant

        with open(os.path.join(workdir, psf_listfile)) as fs:
            psf_prods = json.load(fs)
            print(psf_prods)

        psfs = read_psf_model_images(psf_prods, workdir)

        assert psfs is not None, "Returned PSF object list is None"

        assert (
            len(psf_prods) == num_exposures
        ), "length of psf_listfile (%d) does not match the number of objects (%d)" % (
            len(psf_prods),
            num_exposures,
        )

        for psf in psfs:
            assert issubclass(type(psf), PSFModelImage), "Returned PSF object does not seem to be the correct type"
