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
import h5py

from SHE_PPT import __version__ as ppt_version
from SHE_PPT.file_io import get_allowed_filename, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products import she_psf_model_image
from SHE_PPT.table_formats.she_psf_model_image import tf
from SHE_PPT.table_utility import init_table, is_in_format

logger = getLogger(__name__)


def __create_table(object_ids, pixel_coords, stampsize, stamp_per_obj):
    """Creates the table holding PSF information"""

    # create the various required columns
    psf_image_x = [c[0] for c in pixel_coords]
    psf_image_y = [c[1] for c in pixel_coords]
    psf_x = [stampsize / 2] * len(pixel_coords)
    psf_y = [stampsize / 2] * len(pixel_coords)

    if stamp_per_obj:
        bulge_index = [2 * i + 2 for i in range(len(pixel_coords))]
        disk_index = [2 * i + 3 for i in range(len(pixel_coords))]
    else:
        bulge_index = [2] * len(pixel_coords)
        disk_index = [3] * len(pixel_coords)

    sed_template = [-1] * len(pixel_coords)

    # convert to the correct dtypes for the table (init_table seemingly fails to do this)
    sed_template = np.asarray(sed_template, dtype=np.int64)
    bulge_index = np.asarray(bulge_index, dtype=np.int32)
    disk_index = np.asarray(disk_index, dtype=np.int32)
    psf_image_x = np.asarray(psf_image_x, dtype=np.int16)
    psf_image_y = np.asarray(psf_image_y, dtype=np.int16)
    psf_x = np.asarray(psf_x, dtype=np.float32)
    psf_y = np.asarray(psf_y, dtype=np.float32)

    # construct the table
    t = init_table(
        tf,
        init_cols={
            tf.ID: object_ids,
            tf.template: sed_template,
            tf.bulge_index: bulge_index,
            tf.disk_index: disk_index,
            tf.image_x: psf_image_x,
            tf.image_y: psf_image_y,
            tf.x: psf_x,
            tf.y: psf_y,
        },
    )

    assert is_in_format(t, tf)

    return t


def __create_mock_psf_image(stampsize=480, radius=5):
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


def __create_hdf5(object_ids, pixel_coords, workdir, stampsize, stamp_per_obj, oversampling):
    """Creates the HDF5 file pointed to by the psf model image data product"""

    # create the table and append it to the HDU list
    table = __create_table(object_ids, pixel_coords, stampsize, stamp_per_obj)

    # create the PSF image
    img = __create_mock_psf_image(stampsize=stampsize)

    # get a valid filename and write to this
    h5_filename = get_allowed_filename("PSF-IMG", "00", version=ppt_version, extension=".h5")

    qualified_filename = os.path.join(workdir, h5_filename)

    with h5py.File(qualified_filename, "w") as f:
        f.attrs["PSF_OVERSAMPLING_FACTOR"] = oversampling

        mock_psf = f.create_dataset(name="MOCK_PSF", data=img)

        img_group = f.create_group("IMAGES")

        for obj_id in object_ids:
            if stamp_per_obj:
                img_group.create_dataset(name=str(obj_id), data=img)
            else:
                img_group[str(obj_id)] = mock_psf

        table.write(f, "TABLE")

    return h5_filename


def create_model_image_product(
    object_ids, pixel_coords, workdir=".", stampsize=480, stamp_per_obj=False, oversampling=3
):
    """Creates a dpdShePsfModelImage product given a list of object ids and pixel coordinates.
    Inputs:
        object_ids: List of object IDs
        pixel_coords: List of tuples of (x,y) pixel coords corresponding to the object_ids
        workdir: The work directory to write the product to (default ".")
        stampsize: Size of the postagestamp in pixels (default 800)
        stamp_per_obj: Use a postage stamp per object (T) or use one stamp for all objects (F) (default False)
    Returns:
        prod_filename: The filename of the output product"""

    data_filename = __create_hdf5(
        object_ids, pixel_coords, workdir, stampsize, stamp_per_obj, oversampling=oversampling
    )

    dpd = she_psf_model_image.create_dpd_she_psf_model_image(data_filename=data_filename)

    prod_filename = get_allowed_filename("PSF-IMG", "00", version=ppt_version, extension=".xml", subdir="")

    logger.info("Writing mock PSF model image product to %s" % os.path.join(workdir, prod_filename))
    write_xml_product(dpd, prod_filename, workdir=workdir)

    return prod_filename
