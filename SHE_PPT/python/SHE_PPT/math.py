""" @file math.py

    Created 12 February, 2018

    Miscellaneous mathematical functions
"""

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import numpy as np

def linregress_with_errors( x, y, y_err ):
    """
    @brief
        Perform a linear regression with errors on the y values
    @details
        This uses a direct translation of GSL's gsl_fit_wlinear function, using
        inverse-variance weighting
        
    @param x <np.ndarray>
    @param y <np.ndarray>
    @param y_err <np.ndarray>
    
    @return slope <float>,
            intercept <float>,
            slope_err <float>,
            intercept_err <float>,
            slope_intercept_covar <float>
    """

    y_weights = y_err ** -2
    total_weight = y_weights.sum()

    x_weighted_mean = np.average( x, weights = y_weights )
    y_weighted_mean = np.average( y, weights = y_weights )

    dx = x - x_weighted_mean
    dy = y - y_weighted_mean

    dx2_weighted_mean = np.average( dx ** 2, weights = y_weights )
    dxdy_weighted_mean = np.average( dx * dy, weights = y_weights )

    slope = dxdy_weighted_mean / dx2_weighted_mean
    intercept = y_weighted_mean - x_weighted_mean * slope

    slope_err = np.sqrt( 1. / ( total_weight * dx2_weighted_mean ) )
    intercept_err = np.sqrt( ( 1.0 + x_weighted_mean ** 2 / dx2_weighted_mean ) / total_weight )
    slope_intercept_covar = -x_weighted_mean / ( total_weight * dx2_weighted_mean )

    return slope, intercept, slope_err, intercept_err, slope_intercept_covar

def decompose_transformation_matrix( m ):
    """Decomposes a translation-free 2x2 transformation matrix into a scale matrix and rotation matrix.
    
    Parameters
    ----------
    m : 2x2 np.matrix
    
    Returns
    -------
    s : 2x2 np.matrix
        Scale matrix
    r : 2x2 np.matrix
        Rotation matrix
    """

    s0 = np.sqrt( m[0, 0] ** 2 + m[1, 0] ** 2 )
    s1 = np.sqrt( m[0, 1] ** 2 + m[1, 1] ** 2 )

    s = np.matrix( [[s0, 0],
                    [0, s1]] )

    r = np.matrix( [[m[0, 0] / s0, m[0, 1] / s1],
                    [m[1, 0] / s0, m[1, 1] / s1]] )

    return s, r

