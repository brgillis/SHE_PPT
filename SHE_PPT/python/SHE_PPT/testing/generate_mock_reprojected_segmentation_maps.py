""" @file generate_mock_reprojected_segmentation_maps.py

    Created 05 May 2022.

    Utilities to generate mock vis calibrated frames for smoke tests.
"""

__updated__ = "2022-05-05"

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
from SHE_PPT.products.she_exposure_segmentation_map import create_dpd_she_exposure_segmentation_map

logger = getLogger(__name__)

# how larger the mask is than the object
masksize = 5


def __generate_segmentation_mask(radius = 10):
    """Returns a 2*radius by 2*radius array with a circle of 1s within radius, and zero elsewhere"""

    size = int(radius * 2)

    mask = np.zeros((size, size), dtype=np.int64)

    x = np.arange(size) + 0.5 - radius
    y = np.arange(size)[:, np.newaxis] + 0.5 - radius
    mask = np.square(x) + np.square(y) < np.square(radius)

    return mask


def __create_detector_map(object_ids, pixel_coords, detector_shape, objsize = 10):
    """For a given detector, produce a segmentation map"""
    img = np.zeros(detector_shape, dtype=np.int64)

    mask_radius = int(masksize * objsize)

    mask = __generate_segmentation_mask(radius=mask_radius)

    for id, coords in zip(object_ids, pixel_coords):
        xmin = int(coords[0]) - mask_radius
        xmax = int(coords[0]) + mask_radius
        ymin = int(coords[1]) - mask_radius
        ymax = int(coords[1]) + mask_radius

        # zero where the object will go
        img[ymin:ymax, xmin:xmax] *= (1 - mask)
        # set the pixel values to the object_id
        img[ymin:ymax, xmin:xmax] += id * (mask)

    return img


def create_reprojected_segmentation_map(object_ids, pixel_coords, detectors, wcs_list, workdir = ".",
                                        detector_shape = (100, 100), objsize = 10):
    """
    Creates a DpdSheExposureReprojectedSegmentationMap product from a list of input objects, their image positions,
    the detectors they belong to and the detectors' WCSs

    Inputs:
       - object_ids: a list of MER object IDs
       - pixel_coords: a list of the (x,y) tuple of the object's pixel coordinates on its detector
       - detectors: a list of the detector number (0:35) that each object belongs to
       - wcs_list: A list of astropy.wcs.WCS objects, one per detector
       - workdir: The work directory to write the product to (default ".")
       - detector_shape: The size of the detector in pixels
       - objsize: The size of an object in pixels

    Outputs:
       - prod_filename: The filename of the created data product
    """
    n_detectors = len(wcs_list)

    if n_detectors not in (1, 36):
        raise ValueError("Number of detectors seems to be %d. The only valid numbers are 1 or 36" % n_detectors)

    object_ids = np.asarray(object_ids)
    pixel_coords = np.asarray(pixel_coords)
    detectors = np.asarray(detectors)

    hdul = fits.HDUList()
    hdul.append(fits.PrimaryHDU())

    # loop over all detectors in the exposure
    for det in range(n_detectors):

        # get the detector's name
        det_i = det // 6 + 1
        det_j = det % 6 + 1
        det_id = "%s-%s" % (str(det_i), str(det_j))
        logger.info("Creating detector %s" % det_id)

        # create the seg map for the detector from the objects in that detector
        inds = np.where(detectors == det)
        img = __create_detector_map(object_ids[inds], pixel_coords[inds], detector_shape, objsize=objsize)

        # create the HDU and append it to the HDUlist
        header = wcs_list[det].to_header()
        img_hdu = fits.ImageHDU(data=img, header=header, name="CCDID %s.SEG" % det_id)
        hdul.append(img_hdu)

    fits_filename = get_allowed_filename("EXP-RPJ-SEG", "00", version=ppt_version, extension=".fits")
    qualified_fits_filename = os.path.join(workdir, fits_filename)
    logger.info("Writing fits file to %s" % qualified_fits_filename)

    hdul.writeto(qualified_fits_filename, overwrite=True)

    dpd = create_dpd_she_exposure_segmentation_map(data_filename=fits_filename)
    prod_filename = get_allowed_filename("EXP-RPJ-SEG", "00", version=ppt_version, extension=".xml", subdir="")
    qualified_prod_filename = os.path.join(workdir, prod_filename)
    logger.info("Writing xml product to %s" % qualified_prod_filename)
    write_xml_product(dpd, prod_filename, workdir=workdir)

    return prod_filename
