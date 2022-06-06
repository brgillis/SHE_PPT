""" @file shear_utility.py

    Created 9 Feb, 2018

    Miscellaneous utility functions related to shear measurements
"""

__updated__ = "2021-08-13"

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

import math
from dataclasses import dataclass
from typing import Optional, Tuple, Union

import galsim
import numpy as np
from astropy.wcs import WCS as AstropyWCS
from galsim.wcs import BaseWCS as GalsimWCS
from scipy.optimize import minimize

from . import flags as she_flags
from .she_image import SHEImage

MSG_TOO_BIG_SHEAR = "Requested shear exceeds 1"


@dataclass
class ShearEstimate():
    """Dataclass to represent a shear estimate and closely-associated information.

    Attributes
    ----------
    g1 : float
        The first component of the shear value.
    g2 : float
        The second component of the shear value.
    g1_err : float
        The uncertainty in the first component of the shear value.
    g2_err : float
        The uncertainty in the second component of the shear value.
    g1g2_covar : float
        The covariance between the first and second components of the shear value.
    flags : int
        The bit flags associated with this shear estimate, stored as an unsigned integer.
    weight : float
        The weight associated with this shear estimate.
    """

    g1: float = np.NaN
    g2: float = np.NaN
    g1_err: float = np.inf
    g2_err: float = np.inf
    g1g2_covar: float = 0.
    flags: int = 0
    weight: float = 1


def get_g_from_e(e1: float, e2: float) -> Tuple[float, float]:
    """Calculates the g-style shear from e-style, using GalSim's convention of e and g shear, where:

    g = (1-r)/(1+r)
    e = (1+r^2)/(1-r^2)

    where `r` is the axis ratio of an ellipse sheared by this amount.

    Parameters
    ----------
    e1 : float
        The first component of the e-style shear value.
    e2 : float
        The second component of the e-style shear value.

    Returns
    -------
    g1 : float
        The first component of the g-style shear value.
    g2 : float
        The second component of the g-style shear value.

    Raises
    ------
    ValueError
        If the magnitude of the input e-style shear is greater than 1, i.e. sqrt(e1^2 + e2^2) > 1.
    """

    e = math.sqrt(e1 * e1 + e2 * e2)
    beta = math.atan2(e2, e1)

    r2 = (1. - e) / (1. + e)

    r = math.sqrt(r2)

    g = (1. - r) / (1. + r)

    return g * math.cos(beta), g * math.sin(beta)


def correct_for_wcs_shear_and_rotation(shear_estimate: ShearEstimate,
                                       stamp: Optional[SHEImage] = None,
                                       wcs: Optional[Union[AstropyWCS, GalsimWCS]] = None,
                                       x: Optional[float] = None,
                                       y: Optional[float] = None,
                                       ra: Optional[float] = None,
                                       dec: Optional[float] = None) -> None:
    """Corrects (in-place) a shear_estimate object for the shear and rotation information contained within the
    provided WCS (or provided stamp's wcs). Note that this function ignores any flipping, so if e.g. transforming
    from image to sky coordinates, the resulting shear will be in the (-R.A.,Dec.) frame, not (R.A.,Dec.).

    Parameters
    ----------
    shear_estimate : ShearEstimate
        An object containing the shear estimate and errors. This can either be the ShearEstimate class defined in
        this module, or another class that has the g1, g2, g2_err, g1g2_covar, and flags members. This object
        will be modified in-place by this function.
    stamp : Optional[SHEImage]
        A SHEImage, at the center of which is the object in question. Either this or `wcs` must be supplied.
    wcs : Optional[Union[AstropyWCS, GalsimWCS]]
        Either this or `stamp` must be supplied.
    x, y : Optional[float]
        If `wcs` is supplied, the position of the object must be provided, either through `x` and `y` or `ra` and `dec`.
    ra, dec : Optional[float]
        If `wcs` is supplied, the position of the object must be provided, either through `x` and `y` or `ra` and `dec`.
    """

    # Check for valid input
    if (stamp is None) == (wcs is None):
        raise ValueError("Exactly one of `stamp` and `wcs` must be supplied to " +
                         "`correct_for_wcs_shear_and_rotation`.")

    # If no stamp is supplied, create a ministamp to work with
    if stamp is None:
        stamp = _make_ministamp_from_wcs(wcs, x, y, ra, dec)

    # Since we have to solve for the pre-wcs shear, we get the world2pix decomposition and work backwards
    _scale, w2p_shear, w2p_theta, _w2p_flip = stamp.get_world2pix_decomposition()

    # Set up the shear as a matrix
    g_pix_polar = np.array([[shear_estimate.g1], [shear_estimate.g2]])

    # We first have to rotate into the proper frame
    sin_theta = w2p_theta.sin()
    cos_theta = w2p_theta.cos()

    # Get the reverse rotation matrix
    p2w_rotation_matrix = np.array([[cos_theta, sin_theta], [-sin_theta, cos_theta]])

    double_p2w_rotation_matrix = p2w_rotation_matrix @ p2w_rotation_matrix  # 2x2 so it's commutative
    g_world_polar = double_p2w_rotation_matrix @ g_pix_polar

    # TODO: Update errors from the WCS shear

    # Update errors from the WCS rotation
    covar_pix = np.array([[shear_estimate.g1_err ** 2, shear_estimate.g1g2_covar],
                          [shear_estimate.g1g2_covar, shear_estimate.g2_err ** 2]])
    covar_world = double_p2w_rotation_matrix @ covar_pix @ double_p2w_rotation_matrix.transpose()

    # Update error and covar values in the shear_estimate object
    shear_estimate.g1_err = np.sqrt(covar_world[0, 0])
    shear_estimate.g2_err = np.sqrt(covar_world[1, 1])
    shear_estimate.g1g2_covar = covar_world[0, 1]

    # Second, we have to correct for the shear. It's necessary to do this by solving for the pre-WCS shear

    try:

        rot_est_shear = galsim.Shear(g1 = g_world_polar[0, 0], g2 = g_world_polar[1, 0])

    except ValueError as e:

        if MSG_TOO_BIG_SHEAR not in str(e):
            raise

        # Shear is greater than 1, so note this in the flags

        _set_as_failed_shear_estimate(shear_estimate, she_flags.flag_too_large_shear)

        return

    def _get_shear_adding_diff(g):
        """Local function to be minimized in the fitting.
        """
        g1 = g[0]
        g2 = g[1]
        try:
            res_shear = w2p_shear + galsim.Shear(g1 = g1, g2 = g2)
            dist2 = (rot_est_shear.g1 - res_shear.g1) ** 2 + (rot_est_shear.g2 - res_shear.g2) ** 2
        except ValueError as e:
            if MSG_TOO_BIG_SHEAR not in str(e):
                raise
            # Requested a too-high shear value, so return an appropriately high distance
            dist2 = (w2p_shear.g1 + g1 - rot_est_shear.g1) ** 2 + (w2p_shear.g2 + g2 - rot_est_shear.g2) ** 2
        return dist2

    fitting_result = minimize(_get_shear_adding_diff, np.array((0, 0)))

    # If we can't find a solution, return NaN shear
    if not fitting_result.success:

        _set_as_failed_shear_estimate(shear_estimate, she_flags.flag_cannot_correct_distortion)

        return

    shear_estimate.g1 = fitting_result.x[0]
    shear_estimate.g2 = fitting_result.x[1]


def uncorrect_for_wcs_shear_and_rotation(shear_estimate: ShearEstimate,
                                         stamp: Optional[SHEImage] = None,
                                         wcs: Optional[Union[AstropyWCS, GalsimWCS]] = None,
                                         x: Optional[float] = None,
                                         y: Optional[float] = None,
                                         ra: Optional[float] = None,
                                         dec: Optional[float] = None) -> None:
    """Uncorrects (in-place) a shear_estimate object for the shear and rotation information contained within the
    provided WCS (or provided stamp's wcs). Note that this function ignores any flipping.

    Parameters
    ----------
    shear_estimate : ShearEstimate
        An object containing the shear estimate and errors. This can either be the ShearEstimate class defined in
        this module, or another class that has the g1, g2, g2_err, g1g2_covar, and flags members. This object
        will be modified in-place by this function.
    stamp : Optional[SHEImage]
        A SHEImage, at the center of which is the object in question. Either this or `wcs` must be supplied.
    wcs : Optional[Union[AstropyWCS, GalsimWCS]]
        Either this or `stamp` must be supplied.
    x, y : Optional[float]
        If `wcs` is supplied, the position of the object must be provided, either through `x` and `y` or `ra` and `dec`.
    ra, dec : Optional[float]
        If `wcs` is supplied, the position of the object must be provided, either through `x` and `y` or `ra` and `dec`.
    """

    # Check for valid input
    if (stamp is None) == (wcs is None):
        raise ValueError("Exactly one of `stamp` and `wcs` must be supplied to " +
                         "`correct_for_wcs_shear_and_rotation`.")

    # If no stamp is supplied, create a ministamp to work with
    if stamp is None:
        stamp = _make_ministamp_from_wcs(wcs, x, y, ra, dec)

    # In this direction, we can straightforwardly apply the world2pix transformation
    _scale, w2p_shear, w2p_theta, _w2p_flip = stamp.get_world2pix_decomposition()

    # Apply the shear first

    try:

        world_shear = galsim.Shear(g1 = shear_estimate.g1, g2 = shear_estimate.g2)

    except ValueError as e:

        if MSG_TOO_BIG_SHEAR not in str(e):
            raise

        _set_as_failed_shear_estimate(shear_estimate, she_flags.flag_too_large_shear)

        return

    res_shear = w2p_shear + world_shear

    # Set up the shear as a matrix
    g_world_polar = np.array([[res_shear.g1], [res_shear.g2]])

    # We secondly rotate into the proper frame
    sintheta = w2p_theta.sin()
    costheta = w2p_theta.cos()

    # Get the rotation matrix
    w2p_rotation_matrix = np.array([[costheta, -sintheta], [sintheta, costheta]])

    double_w2p_rotation_matrix = w2p_rotation_matrix @ w2p_rotation_matrix  # 2x2 so it's commutative
    g_pix_polar = double_w2p_rotation_matrix @ g_world_polar

    shear_estimate.g1 = g_pix_polar[0, 0]
    shear_estimate.g2 = g_pix_polar[1, 0]

    # TODO: Update errors from the WCS shear

    # Update errors from the WCS rotation
    covar_pix = np.array([[shear_estimate.g1_err ** 2, shear_estimate.g1g2_covar],
                          [shear_estimate.g1g2_covar, shear_estimate.g2_err ** 2]])
    covar_world = double_w2p_rotation_matrix @ covar_pix @ double_w2p_rotation_matrix.transpose()

    # Update error and covar values in the shear_estimate object
    shear_estimate.g1_err = np.sqrt(covar_world[0, 0])
    shear_estimate.g2_err = np.sqrt(covar_world[1, 1])
    shear_estimate.g1g2_covar = covar_world[0, 1]


def _make_ministamp_from_wcs(wcs: Union[AstropyWCS, GalsimWCS],
                             x: Optional[float],
                             y: Optional[float],
                             ra: Optional[float],
                             dec: Optional[float]) -> SHEImage:
    """Private function to generate a trivial stamp from a WCS object and a position.
    """

    # Initialize a trivial stamp
    stamp = SHEImage(data = np.zeros((1, 1)))

    # Add the WCS to the stamp
    if isinstance(wcs, AstropyWCS):
        stamp.wcs = wcs
    elif isinstance(wcs, GalsimWCS):
        stamp.galsim_wcs = wcs
    else:
        raise TypeError("wcs is of invalid type: " + str(type(wcs)))

    # Set the offset of the stamp from the provided position
    if ra is not None and dec is not None:
        x, y = stamp.world2pix(ra, dec)
    if x is None or y is None:
        raise ValueError("`x` and `y` or `ra` and `dec` must be supplied to `correct_for_wcs_shear_and_rotation`.")

    stamp.offset = np.array((x, y))

    return stamp


def _set_as_failed_shear_estimate(shear_estimate, err_flag):
    """Local function to modify a ShearEstimate object in-place to flag it as a failure, with a given failure flag.
    """
    shear_estimate.g1 = np.NaN
    shear_estimate.g2 = np.NaN
    shear_estimate.g1_err = np.inf
    shear_estimate.g2_err = np.inf
    shear_estimate.g1g2_covar = np.inf
    shear_estimate.flags |= err_flag


def check_data_quality(gal_stamp: SHEImage,
                       psf_stamp: SHEImage,
                       stacked: bool = False) -> int:
    """Checks the galaxy and PSF stamps for any data quality issues, and returns an
    appropriate set of flags.

    Parameters
    ----------
    gal_stamp : SHEImage
        The galaxy stamp to check.
    psf_stamp : SHEImage
        The PSF stamp to check.
    stacked : bool
        Whether the stamps are from stacked images or not.

    Returns
    -------
    flags : int
        A set of bitwise flags indicating any data quality issues.
    """

    # Start with a 0 flag that we'll |= (bitwise or-set) to if/when we find issues
    flags = 0

    # Check for issues with the PSF
    flags |= get_psf_quality_flags(psf_stamp)

    # Now check for issues with the galaxy image

    flags |= _get_galaxy_quality_flags(gal_stamp, stacked)

    return flags


def get_psf_quality_flags(psf_stamp: SHEImage) -> int:
    """Check a PSF stamp for data quality issues and return a set of flags for it.

    Parameters
    ----------
    psf_stamp : SHEImage
        The PSF stamp to check.

    Returns
    -------
    flags : int
        A set of bitwise flags indicating any data quality issues.
    """

    flags = 0

    if psf_stamp is None or psf_stamp.data is None:
        flags |= she_flags.flag_no_psf

    good_psf_data = psf_stamp.data.ravel()
    if (good_psf_data.sum() == 0) or ((good_psf_data < -0.01 * good_psf_data.max()).any()):
        flags |= she_flags.flag_corrupt_psf

    return flags


def _get_galaxy_quality_flags(gal_stamp: SHEImage,
                              stacked: bool) -> int:
    """Check a galaxy stamp for data quality issues and return a set of flags for it.

    Parameters
    ----------
    gal_stamp : SHEImage
        The galaxy stamp to check.
    stacked : bool
        Whether the stamps are from stacked images or not.

    Returns
    -------
    flags : int
        A set of bitwise flags indicating any data quality issues.
    """

    flags = 0

    # Check if the mask exists
    if gal_stamp.mask is None:

        flags |= she_flags.flag_no_mask

        # Check if we have at least some other data; in which case make mask shaped like it
        have_some_data = False

        for a, missing_flag in ((gal_stamp.data, she_flags.flag_no_science_image),
                                (gal_stamp.background_map, she_flags.flag_no_background_map),
                                (gal_stamp.noisemap, she_flags.flag_no_noisemap),
                                (gal_stamp.segmentation_map, she_flags.flag_no_segmentation_map),):

            if a is None:
                flags |= missing_flag
            else:
                ravelled_mask = np.zeros_like(a.ravel(), dtype = bool)
                ravelled_antimask = ~ravelled_mask
                have_some_data = True

        if not have_some_data:
            # We don't have any data, so we can't do any further checks; return the flag so far
            return flags

    else:
        # Check for any possible corruption issues in the mask
        if (gal_stamp.mask < 0).any():
            flags |= she_flags.flag_corrupt_mask

        ravelled_mask = gal_stamp.boolmask.ravel()
        ravelled_antimask = ~ravelled_mask

    # Check how much of the data is unmasked, and if we have enough
    unmasked_count = ravelled_antimask.sum()
    total_count = len(ravelled_antimask)
    frac_unmasked = float(unmasked_count) / total_count
    if frac_unmasked < 0.25:
        flags |= she_flags.flag_insufficient_data

    # Check for missing or corrupt data
    if stacked:
        data = gal_stamp.data + gal_stamp.background_map
    else:
        data = gal_stamp.data

    for a, missing_flag, corrupt_flag in ((data, she_flags.flag_no_science_image,
                                           she_flags.flag_corrupt_science_image),
                                          (gal_stamp.background_map, she_flags.flag_no_background_map,
                                           she_flags.flag_corrupt_background_map),
                                          (gal_stamp.noisemap, she_flags.flag_no_noisemap,
                                           she_flags.flag_corrupt_noisemap),
                                          (gal_stamp.segmentation_map, she_flags.flag_no_segmentation_map,
                                           she_flags.flag_corrupt_segmentation_map),):

        # Check for missing data
        if a is None:
            flags |= missing_flag
            continue

        # Check for corrupt data by checking that all data are valid

        if corrupt_flag == she_flags.flag_corrupt_segmentation_map:
            min_value = -1
        else:
            min_value = 0

        good_data = a.ravel()[ravelled_antimask]
        if (np.isnan(good_data).any() or np.isinf(good_data).any() or
                ((good_data.sum() == 0) or (good_data < min_value).any())):
            flags |= corrupt_flag

    return flags
