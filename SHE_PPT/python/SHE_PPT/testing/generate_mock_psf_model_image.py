""" @file generate_mock_psf_model_image.py

    Created 02 May 2022.

    Utilities to generate mock vis calibrated frames for smoke tests.
"""

__updated__ = "2022-05-02"

# Copyright (C) 2012-2022 Euclid Science Ground Segment
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

import numpy as np
import uuid
import pathlib

from ST_DM_FilenameProvider.FilenameProvider import FileNameProvider

from SHE_PPT import SHE_PPT_RELEASE_STRING

from SHE_PPT.file_io import write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products import she_psf_model_image
from SHE_PPT.she_io.psf_model_images import PSFModelImagesWriter

logger = getLogger(__name__)


def _create_mock_psf_image(stampsize=480, radius=5):
    """Creates a mock PSF image (gausian)"""

    img = np.zeros((stampsize, stampsize), dtype=np.float32)

    # centre coord of the image
    c = stampsize / 2

    # create the gaussian
    x_r = (np.arange(stampsize) - c) / radius
    y_r = (np.arange(stampsize)[:, np.newaxis] - c) / radius
    img = np.exp(-np.square(x_r) - np.square(y_r))

    # normalise
    img = img / img.sum()

    return img


def create_model_image_product(
    object_ids, pixel_coords, workdir=".", stampsize=480, stamp_per_obj=False, oversampling=3
):
    """Creates a dpdShePsfModelImage product given a list of object ids and pixel coordinates.
    Inputs:
        object_ids: List of object IDs
        pixel_coords: List of tuples of (x,y) pixel coords corresponding to the object_ids
        workdir: The work directory to write the product to (default ".")
        stampsize: Size of the postagestamp in pixels
        stamp_per_obj: Use a postage stamp per object (T) or use one stamp for all objects (F) (default False)
    Returns:
        prod_filename: The filename of the output product"""

    workdir = pathlib.Path(workdir)
    datadir = workdir / "data"

    h5_filename = FileNameProvider().get_allowed_filename(
            type_name='PSF-MODEL-IMAGES',
            instance_id=uuid.uuid4().hex[:8],
            extension='.h5',
            release=SHE_PPT_RELEASE_STRING,
            processing_function='SHE',
    )

    with PSFModelImagesWriter(object_ids, datadir / h5_filename, oversampling_factor=oversampling) as writer:
        psf_image = _create_mock_psf_image(stampsize=stampsize)
        for obj in object_ids:
            writer.write_psf(obj, psf_image)

    dpd = she_psf_model_image.create_dpd_she_psf_model_image(data_filename=h5_filename)

    prod_filename = FileNameProvider().get_allowed_filename(
            type_name='PSF-MODEL-IMAGES',
            instance_id=uuid.uuid4().hex[:8],
            extension='.xml',
            release=SHE_PPT_RELEASE_STRING,
            processing_function='SHE',
    )

    logger.info("Writing mock PSF model image product to %s" % os.path.join(workdir, prod_filename))
    write_xml_product(dpd, prod_filename, workdir=workdir)

    return prod_filename
