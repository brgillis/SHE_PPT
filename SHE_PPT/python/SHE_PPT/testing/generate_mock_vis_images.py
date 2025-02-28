""" @file generate_mock_vis_images.py

    Created 14 Mar 2022.

    Utilities to generate mock vis calibrated frames for smoke tests.
"""

__updated__ = "2022-05-04"

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
import pathlib

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

from SHE_PPT import __version__ as ppt_version
from SHE_PPT.file_io import get_allowed_filename, write_xml_product, find_file
from SHE_PPT.logging import getLogger
from SHE_PPT.products import vis_calibrated_frame, vis_calibrated_quad_frame

logger = getLogger(__name__)

# how much larger the radius of the stamp is than the radius of the object
stampscale = 5

DEFAULT_OBJ_SIZE = 2

# templates of the FITS Headers
PRIMARY_HEADER_PATH = find_file(pathlib.Path("AUX") / "SHE_PPT" / "vis_quad_primary_header_20240305.txt")
IMAGE_HEADER_PATH = find_file(pathlib.Path("AUX") / "SHE_PPT" / "vis_quad_image_header_20240305.txt")


def __generate_gausian_blob(objsize=DEFAULT_OBJ_SIZE):
    """generates a (objsize*stampscale*2 x objsize*stampscale*2) pixel image of a sersic profile (n=1) with width of
    objsize pixels"""

    # size of the stamp
    size = int(objsize * stampscale * 2)

    blob = np.zeros((size, size))

    x = np.arange(size) - size / 2.0
    for j in range(size):
        y = x[j]
        r = np.sqrt(x * x + y * y)
        blob[j, :] = np.exp(-(r / objsize))

    return blob


def __generate_detector_images(
    detector_shape=(4136, 4096),
    nobjs=10,
    background=10.0,
    snr=10,
    objsize=DEFAULT_OBJ_SIZE,
    obj_rng=None,
    noise_rng=None,
):
    """Generates the SCI, RMG, FLG, WGT and BKG pixel maps for a detector

    Arguments:
      - detector_shape: the shape of the detector (ny, nx)
      - nobjs: the number of simulated objects to place in the image
      - background: The background level (background noise is sqrt(background))
      - snr: signal to noise ratio for the created objects
      - objsize: the width (in pixels) of the gaussian representing an object
      - obj_rng: numpy.RandomState object for the object random number generator
      - noise_rng: numpy.RandomState object for the noise random number generator

    Outputs:
      - sci: sci image
      - rms: rms image
      - flg: flg image
      - wgt: wgt image
      - bkg: bkg image
      - x_px: list of x pixel coordinates of the nobjs objects
      - y_px: list of y pixel coordinates of the nobjs objects
    """

    if obj_rng is None:
        obj_rng = np.random.RandomState()

    if noise_rng is None:
        noise_rng = np.random.RandomState()

    stampsize = int(objsize * stampscale * 2)

    if stampsize >= min(detector_shape):
        raise ValueError("Detector size must be at least %d pixels" % stampsize)

    # generate sci image with poisson noise
    sci = noise_rng.poisson(background, detector_shape).astype(np.float32)

    # populate it with nobjs "galaxies"
    x_px = []
    y_px = []
    for i in range(nobjs):
        blob = __generate_gausian_blob(objsize)

        # select (randomly) the x and y coordinates of the blob's bottom corner
        x = obj_rng.randint(0, detector_shape[1] - stampsize)
        y = obj_rng.randint(0, detector_shape[0] - stampsize)

        # store the blob's centre coordinates
        x_px.append(x + stampsize / 2)
        y_px.append(y + stampsize / 2)

        # add the blob to the image
        sci[y:y + stampsize, x:x + stampsize] += snr * np.sqrt(background) * blob

    # generate rms image (standard deviation of the image in this case)
    rms_val = np.std(sci)
    rms = np.ones(detector_shape, dtype=np.float32) * rms_val

    # generate FLG image (flag = 0)
    flg = np.zeros(detector_shape, dtype=np.int32)

    # generate wgt image (wgt = 1.0)
    wgt = np.ones(detector_shape, dtype=np.float32)

    # generate bkg image (bkg = noise)
    bkg = np.ones(detector_shape, dtype=np.float32) * background

    return sci, rms, flg, wgt, bkg, x_px, y_px


def __create_header(header, wcs, **kwargs):
    """Returns a newly created FITS header
    Args:
      header - an astropy.io.fits.Header object
      wcs - an astropy.wcs.WCS object, this overwrites the existing wcs in the header if provided
      **kwargs - additional keywords to put into the header
    """

    # if wcs is provided, overwrite the current header wcs
    if wcs is not None:
        header.update(wcs.to_header())

    # add in additional keywords to the header from the args
    for key, val in kwargs.items():
        header[key] = val

    return header


def _create_primary_header(header=None, wcs=None, **kwargs):
    if header is None:
        header_blob = fits.Header.fromtextfile(PRIMARY_HEADER_PATH)

    h = __create_header(header_blob, wcs, **kwargs)

    return h


def _create_image_header(header=None, wcs=None, **kwargs):
    if header is None:
        header_blob = fits.Header.fromtextfile(IMAGE_HEADER_PATH)

    h = __create_header(header_blob, wcs, **kwargs)

    return h


def create_exposure(
    n_detectors=1,
    detector_shape=(100, 100),
    workdir=".",
    seed=1,
    noise_seed=1,
    n_objs_per_det=10,
    objsize=DEFAULT_OBJ_SIZE,
    pointing_id=1,
    obs_id=1,
    use_quadrant=True,
    header_primary=None,
    header_image=None,
    kwargs_header_primary=None,
    kwargs_header_image=None,
):
    """
    Creates a mock dpdVisCalibratedFrame data product for use in smoke tests

    Arguments:
       - n_detectors: The number of detectors to create (default 1)
       - detector_shape: The shape of the detector in pixels (ny, nx) (default (100,100))
       - objs_per_detector: Number of objects per detector (default 10)
       - workdir: workdir for the files (default ".")
       - seed: seed for the random number generator for objects
       - noise_seed: seed for the random number generator for applying noise to images
       - n_objs_per_det: Number of objects generated per detector
       - objsize: size of the objects in pixels
       - pointing_id: the pointing id to be used for the output product
       - obs_id: the observation id to be used for the output product

    Returns:
       - prod_filename (The name of the created data product)
       - sky_coords (a list of world coodinates for the objects in the image - to be used when creating
         mock mer catalogues for this exposure (astropy.coordinates.SkyCoord))
       - img_coords (a list of image coordinates (x,y) of each object)
       - detectors (a list stating which detector (0:ndetectors-1) the object is in)
       - wcs_list (a list of all the WCSs used for each detector)
    """
    # pixelsize = 0.1"
    PIXELSIZE = 1.0 / 3600 / 10.0

    if use_quadrant:
        n_detector_max = 144
    else:
        n_detector_max = 36

    if n_detectors < 1 or n_detectors > n_detector_max:
        raise ValueError(
            "Number of detectors seems to be %d. The only valid numbers are between 1 and %d inclusive."
            % (n_detectors, n_detector_max),
        )

    obj_rng = np.random.RandomState(seed=seed)
    noise_rng = np.random.RandomState(seed=noise_seed)

    if kwargs_header_primary is None:
        kwargs_header_primary = {}

    if kwargs_header_image is None:
        kwargs_header_image = {}

    # create hdulists for the 3 fits files (DET, WGT, BKG)
    det_hdr = _create_primary_header(header=header_primary, **kwargs_header_primary)
    det_primary = fits.PrimaryHDU(data=None, header=det_hdr)
    det_hdul = fits.HDUList([det_primary])

    wgt_hdr = _create_primary_header(header=header_primary, **kwargs_header_primary)
    wgt_primary = fits.PrimaryHDU(data=None, header=wgt_hdr)
    wgt_hdul = fits.HDUList([wgt_primary])

    bkg_hdr = _create_primary_header(header=header_primary, **kwargs_header_primary)
    bkg_primary = fits.PrimaryHDU(data=None, header=bkg_hdr)
    bkg_hdul = fits.HDUList([bkg_primary])

    sky_coords = []
    img_coords = []
    detectors = []
    wcs_list = []

    detector_names = []

    # loop over all detectors in the exposure
    for det in range(n_detectors):
        # get the detector's
        if use_quadrant:
            det_i = (det // 4) // 6 + 1
            det_j = (det // 4) % 6 + 1
            det_k = det % 4
            det_sk = {0: "E", 1: "F", 2: "G", 3: "H"}[det_k]
            det_id = "%d-%d" % (det_i, det_j)
            quad_id = "%s" % (det_sk)
            _detector_name = det_id + "." + quad_id
            x_c = (1.1 * detector_shape[1]) * (2 * (det_i - 1) + (det_k % 2)) * PIXELSIZE
            y_c = (1.1 * detector_shape[0]) * (2 * (det_j - 1) + (det_k // 2)) * PIXELSIZE
        else:
            det_i = det // 6 + 1
            det_j = det % 6 + 1
            det_id = "%d-%d" % (det_i, det_j)
            _detector_name = det_id
            x_c = (1.1 * detector_shape[1]) * (det_i - 1) * PIXELSIZE
            y_c = (1.1 * detector_shape[0]) * (det_j - 1) * PIXELSIZE

        detector_names.append(_detector_name)
        logger.info("Creating detector %s" % _detector_name)

        # create image data
        sci, rms, flg, wgt, bkg, x_px, y_px = __generate_detector_images(
            detector_shape=detector_shape, obj_rng=obj_rng, noise_rng=noise_rng, nobjs=n_objs_per_det, objsize=objsize
        )

        # create WCS (Use Airy projection - arbitrary decision, we just want something in valid sky coordinates!)
        wcs = WCS(naxis=2)
        wcs.wcs.crpix = [detector_shape[1] // 2, detector_shape[0] // 2]
        wcs.wcs.crval = [x_c, y_c]
        wcs.wcs.cd = np.identity(2) * PIXELSIZE
        wcs.wcs.cd[0, 0] *= -1
        wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        wcs.array_shape = detector_shape

        # obtain the world coordinates of the objects in the image, and append them to the object_positions list
        world_coords = wcs.pixel_to_world(x_px, y_px)
        for coord in world_coords:
            sky_coords.append(coord)

        # also store the pixel coordinates of each object and the detector it belongs to
        for coord in zip(x_px, y_px):
            img_coords.append(coord)
            detectors.append(det)

        wcs_list.append(wcs)

        # now make the hdus for these images

        # common header tor HDUs in the DET file (sci, flg, rms)
        if use_quadrant:
            det_hdr = _create_image_header(
                wcs=wcs,
                NAXIS1=detector_shape[0],
                NAXIS2=detector_shape[1],
                CCDID=det_id,
                QUADID=quad_id,
                **kwargs_header_image,
            )
        else:
            det_hdr = _create_image_header(
                wcs=wcs,
                NAXIS1=detector_shape[0],
                NAXIS2=detector_shape[1],
                CCDID=det_id,
                **kwargs_header_image,
            )

        # create hdus for the DET file and append them to the HDUlist
        sci_hdu = fits.ImageHDU(data=sci, header=det_hdr, name="%s.SCI" % _detector_name)
        rms_hdu = fits.ImageHDU(data=rms, header=det_hdr, name="%s.RMS" % _detector_name)
        flg_hdu = fits.ImageHDU(data=flg, header=det_hdr, name="%s.FLG" % _detector_name)
        det_hdul.append(sci_hdu)
        det_hdul.append(rms_hdu)
        det_hdul.append(flg_hdu)

        # BKG HDU
        bkg_hdr = _create_image_header(**kwargs_header_image)
        bkg_hdu = fits.ImageHDU(data=bkg, header=bkg_hdr, name="%s" % _detector_name)
        bkg_hdul.append(bkg_hdu)

        # WGT HDU
        wgt_hdr = _create_image_header(**kwargs_header_image)
        wgt_hdu = fits.ImageHDU(data=wgt, header=wgt_hdr, name="%s" % _detector_name)
        wgt_hdul.append(wgt_hdu)

    logger.info("Created %d detector(s) with a total of %d object(s)" % (n_detectors, len(sky_coords)))

    # determine the data directory, creating it if it doesn't already exist
    datadir = os.path.join(workdir, "data")
    if not os.path.exists(datadir):
        logger.info("Creating non-existing data directory %s" % datadir)
        os.mkdir(datadir)

    # get qualified filename for the fits files
    identifier = f"{obs_id}-{pointing_id}"
    det_fname = get_allowed_filename("VIS-DET", identifier, version=ppt_version, extension=".fits")
    wgt_fname = get_allowed_filename("VIS-WGT", identifier, version=ppt_version, extension=".fits")
    bkg_fname = get_allowed_filename("VIS-BKG", identifier, version=ppt_version, extension=".fits")

    # write the fits files
    logger.info("Writing DET file to %s" % os.path.join(workdir, det_fname))
    det_hdul.writeto(os.path.join(workdir, det_fname), overwrite=True)
    logger.info("Writing WGT file to %s" % os.path.join(workdir, wgt_fname))
    wgt_hdul.writeto(os.path.join(workdir, wgt_fname), overwrite=True)
    logger.info("Writing BKG file to %s" % os.path.join(workdir, bkg_fname))
    bkg_hdul.writeto(os.path.join(workdir, bkg_fname), overwrite=True)

    # create the data product
    if use_quadrant:
        exposure_prod = vis_calibrated_quad_frame.create_dpd_vis_calibrated_quad_frame(
            data_filename=det_fname, bkg_filename=bkg_fname, wgt_filename=wgt_fname
        )
        # set up the correct number of Quadrants in the product, and make sure they have the correct names
        quad_template = exposure_prod.Data.QuadrantList.Qadrant[0]
        exposure_prod.Data.QuadrantList.Qadrant = [quad_template] * n_detectors
        for i, name in enumerate(detector_names):
            exposure_prod.Data.QuadrantList.Qadrant[i].QuadrantId = name
    else:
        exposure_prod = vis_calibrated_frame.create_dpd_vis_calibrated_frame(
            data_filename=det_fname, bkg_filename=bkg_fname, wgt_filename=wgt_fname
        )
        # set up the correct number of Detectors in the product, and make sure they have the correct names
        det_template = exposure_prod.Data.DetectorList.Detector[0]
        exposure_prod.Data.DetectorList.Detector = [det_template] * n_detectors
        for i, name in enumerate(detector_names):
            exposure_prod.Data.DetectorList.Detector[i].DetectorId = name

    exposure_prod.Data.ObservationSequence.PointingId = pointing_id
    exposure_prod.Data.ObservationSequence.ObservationId = obs_id

    # Write it to file
    prod_filename = get_allowed_filename("VIS-CAL-FRAME", "00", version=ppt_version, extension=".xml", subdir="")
    qualified_prod_filename = os.path.join(workdir, prod_filename)
    logger.info("Writing dpdVisCalibratedFrame product to %s" % qualified_prod_filename)
    write_xml_product(exposure_prod, qualified_prod_filename)

    return prod_filename, sky_coords, img_coords, detectors, wcs_list
