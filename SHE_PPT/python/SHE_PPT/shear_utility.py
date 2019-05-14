""" @file shear_utility.py

    Created 9 Feb, 2018

    Miscellaneous utility functions related to shear measurements
"""
from Program_Files.GalSim.devel.lsst.treering_flat import wcs

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

__updated__ = "2019-05-14"

import math

from SHE_PPT.she_image import SHEImage
import astropy.wcs.WCS
import galsim.wcs.BaseWCS
import numpy as np


class ShearEstimate(object):

    def __init__(self,
                 g1,
                 g2,
                 g1_err=np.inf,
                 g2_err=np.inf,
                 g1g2_covar=0,
                 flags=0):
        self.g1 = g1
        self.g2 = g2
        self.g1_err = g1_err
        self.g2_err = g2_err
        self.g1g2_covar = g1g2_covar
        self.flags = flags


def get_g_from_e(e1, e2):
    """
    @brief
        Calculates the g-style shear from e-style

    @param e1
    @param e2

    @return g1, g2
    """

    e = math.sqrt(e1 * e1 + e2 * e2)
    beta = math.atan2(e2, e1)

    r2 = (1. - e) / (1. + e)

    r = math.sqrt(r2)

    g = (1. - r) / (1. + r)

    return g * math.cos(beta), g * math.sin(beta)


def correct_for_wcs_shear_and_rotation(shear_estimate,
                                       stamp=None,
                                       wcs=None,
                                       x=None,
                                       y=None,
                                       ra=None,
                                       dec=None,):
    """Corrects (in-place) a shear_estimate object for the shear and rotation information contained within the
    provided WCS (or provided stamp's wcs). Note that this function ignores any flipping, so if e.g. transforming
    from image to sky coordinates, the resulting shear will be in the (-R.A.,Dec.) frame, not (R.A.,Dec.).

    Parameters
    ----------
    shear_estimate : ShearEstimate
        An object containing the shear estimate and errors. This can either be the ShearEstimate class defined in
        this module, or another class that has the g1, g2, g1_err, g2_err, g1g2_covar, and flags members.
    stamp : SHEImage
        A SHEImage, at the center of which is the object in question. Either this or "wcs" must be supplied
    wcs : an astropy or galsim WCS
        Either this or "stamp" must be supplied
    x, y : float
        If wcs is supplied, the position of the object must be provided, either through x and y or ra and dec
    ra, dec : float
        If wcs is supplied, the position of the object must be provided, either through x and y or ra and dec

    Returns
    -------
    None

    Side-effects
    ------------
    shear_estimate is corrected to be in the (-R.A.,Dec.) frame.

    """

    # Check for valid input
    if (stamp is None) == (wcs is None):
        raise ValueError("Exactly one of \"stamp\" and \"wcs\" must be supplied to " +
                         "correct_for_wcs_shear_and_rotation.")

    # If no stamp is supplied, create a ministamp to work with
    if stamp is None:

        stamp = SHEImage(data=np.zeros((1, 1)))

        # Add the WCS to the stamp
        if isinstance(wcs, astropy.wcs.WCS):
            stamp.wcs = wcs
        elif isinstance(wcs, galsim.wcs.BaseWCS):
            stamp.galsim_wcs = wcs
        else:
            raise TypeError("wcs is of invalid type: " + str(type(wcs)))

        # Set the offset of the stamp from the provided position
        if ra is not None and dec is not None:
            x, y = stamp.world2pix(ra, dec)
        if x is None or y is None:
            raise ValueError("x and y or ra and dec must be supplied to correct_for_wcs_shear_and_rotation.")

        stamp.offset = np.array((x, y))

    # Since we have to solve for the pre-wcs shear, we get the world2pix decomposition and work backwards
    _scale, w2p_shear, w2p_theta, _w2p_flip = stamp.get_world2pix_decomposition()

    # Set up the shear as a matrix
    g_pix_polar = np.matrix([[shear_estimate.g1], [shear_estimate.g2]])

    # We first have to rotate into the proper frame
    sintheta = w2p_theta.sin()
    costheta = w2p_theta.cos()

    # Get the reverse rotation matrix
    p2w_rotation_matrix = np.matrix([[costheta, sintheta], [-sintheta, costheta]])

    double_p2w_rotation_matrix = p2w_rotation_matrix @ p2w_rotation_matrix  # 2x2 so it's commutative
    g_world_polar = double_p2w_rotation_matrix @ g_pix_polar

    # TODO: Update errors from the WCS shear

    # Update errors from the WCS rotation
    covar_pix = np.matrix([[shear_estimate.g1_err**2, shear_estimate.g1g2_covar],
                           [shear_estimate.g1g2_covar, shear_estimate.g2_err**2]])
    covar_world = double_p2w_rotation_matrix @ covar_pix @ double_p2w_rotation_matrix.transpose()

    # Update error and covar values in the shear_estimate object
    shear_estimate.g1_err = np.sqrt(covar_world[0, 0])
    shear_estimate.g2_err = np.sqrt(covar_world[1, 1])
    shear_estimate.g1g2_covar = covar_world[0, 1]

    # Second, we have to correct for the shear. It's necessary to do this by solving for the pre-WCS shear

    try:

        rot_est_shear = galsim.Shear(g1=g_world_polar[0, 0], g2=g_world_polar[1, 0])

    except ValueError as e:

        if not "Requested shear exceeds 1" in str(e):
            raise

        # Shear is greater than 1, so note this in the flags
        shear_estimate.g1 = np.NaN
        shear_estimate.g2 = np.NaN
        shear_estimate.gerr = np.inf
        shear_estimate.g1_err = np.inf
        shear_estimate.g2_err = np.inf
        shear_estimate.g1g2_covar = np.inf

        shear_estimate.flags |= flags.flag_too_large_shear

        return

    def get_shear_adding_diff(g):
        g1 = g[0]
        g2 = g[1]
        try:
            res_shear = w2p_shear + galsim.Shear(g1=g1, g2=g2)
            dist2 = (rot_est_shear.g1 - res_shear.g1)**2 + (rot_est_shear.g2 - res_shear.g2)**2
        except ValueError as e:
            if not "Requested shear exceeds 1" in str(e):
                raise
            # Requested a too-high shear value, so return an appropriately high distance
            dist2 = (w2p_shear.g1 + g1 - rot_est_shear.g1)**2 + (w2p_shear.g2 + g2 - rot_est_shear.g2)**2
        return dist2

    fitting_result = minimize(get_shear_adding_diff, np.array((0, 0)))

    # If we can't find a solution, return NaN shear
    if not fitting_result.success:
        shear_estimate.g1 = np.NaN
        shear_estimate.g2 = np.NaN
        shear_estimate.gerr = np.inf
        shear_estimate.g1_err = np.inf
        shear_estimate.g2_err = np.inf
        shear_estimate.g1g2_covar = np.inf

        shear_estimate.flags |= flags.flag_cannot_correct_distortion

        return
    else:
        shear_estimate.g1 = fitting_result.x[0]
        shear_estimate.g2 = fitting_result.x[1]

    return
