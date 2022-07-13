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
from astropy.io import fits

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
    t = init_table(tf, init_cols={
        tf.ID         : object_ids,
        tf.template   : sed_template,
        tf.bulge_index: bulge_index,
        tf.disk_index : disk_index,
        tf.image_x    : psf_image_x,
        tf.image_y    : psf_image_y,
        tf.x          : psf_x,
        tf.y          : psf_y
        })

    assert is_in_format(t, tf)

    return t


def __create_mock_psf_image(stampsize=800, radius=5):
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


def __create_fits(object_ids, pixel_coords, workdir, stampsize, stamp_per_obj):
    """Creates the FITS file pointed to by the psf model image data product"""

    hdul = fits.HDUList()

    # create the table and append it to the HDU list
    table = __create_table(object_ids, pixel_coords, stampsize, stamp_per_obj)
    table_hdu = fits.BinTableHDU(table, name="PSFC")
    hdul.append(table_hdu)

    # create the PSF image
    img = __create_mock_psf_image(stampsize=stampsize)

    # create the appropriate HDUlists for the bulge and disk PSF images
    if stamp_per_obj:
        for obj_id in object_ids:
            bpsf_hdu = fits.ImageHDU(img, name="%d.BPSF" % obj_id,
                                     header=fits.Header({"GS_SCALE": 5.55555555555555E-06}))
            dpsf_hdu = fits.ImageHDU(img, name="%d.DPSF" % obj_id,
                                     header=fits.Header({"GS_SCALE": 5.55555555555555E-06}))

            hdul.append(bpsf_hdu)
            hdul.append(dpsf_hdu)

    else:
        bpsf_hdu = fits.ImageHDU(img, name="ALL.BPSF", header=fits.Header({"GS_SCALE": 5.55555555555555E-06}))
        dpsf_hdu = fits.ImageHDU(img, name="ALL.DPSF", header=fits.Header({"GS_SCALE": 5.55555555555555E-06}))

        hdul.append(bpsf_hdu)
        hdul.append(dpsf_hdu)

    # get a valid filename and write to this
    fits_filename = get_allowed_filename("PSF-IMG", "00", version=ppt_version, extension=".fits")

    qualified_fits_filename = os.path.join(workdir, fits_filename)

    logger.info("Writing mock PSF model image FITS to %s" % qualified_fits_filename)
    hdul.writeto(qualified_fits_filename, overwrite=True)

    return fits_filename


def create_model_image_product(object_ids, pixel_coords, workdir=".", stampsize=800, stamp_per_obj=False):
    """Creates a dpdShePsfModelImage product given a list of object ids and pixel coordinates.
       Inputs:
           object_ids: List of object IDs
           pixel_coords: List of tuples of (x,y) pixel coords corresponding to the object_ids
           workdir: The work directory to write the product to (default ".")
           stampsize: Size of the postagestamp in pixels (default 800)
           stamp_per_obj: Use a postage stamp per object (T) or use one stamp for all objects (F) (default False)
       Returns:
           prod_filename: The filename of the output product"""

    # create the fits file (table and PSF stamps)
    fits_filename = __create_fits(object_ids, pixel_coords, workdir, stampsize, stamp_per_obj)

    # create the data product
    dpd = she_psf_model_image.create_dpd_she_psf_model_image(data_filename=fits_filename)

    prod_filename = get_allowed_filename("PSF-IMG", "00", version=ppt_version, extension=".xml", subdir="")

    logger.info("Writing mock PSF model image product to %s" % os.path.join(workdir, prod_filename))
    write_xml_product(dpd, prod_filename, workdir=workdir)

    return prod_filename
