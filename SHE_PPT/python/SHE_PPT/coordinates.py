"""
File: python/SHE_PPT/coordinates.py

Created on: 03/11/21

Contains code for operations on lists of coordinates
"""

__updated__ = "2021-11-03"

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

import numpy as np

#degree to/from radian conversion factors
DTOR = np.pi/180
RTOD = 180/np.pi

def _hav(x):
    return np.sin(x/2.)**2

def haversine_metric(lon1, lat1, lon2, lat2):
    """Returns the great circle distance between two points on a sphere"""
    
    d=2*np.arcsin(np.sqrt(_hav(lat2-lat1)+np.cos(lat1)*np.cos(lat2)*_hav(lon2-lon1)))

    return d

def haversine_metric_deg(lon1, lat1, lon2, lat2):
    """Returns the great circle distance between two points, with the input and outputs in degrees"""
    return haversine_metric(lon1*DTOR, lat1*DTOR, lon2*DTOR, lat2*DTOR)

def euclidean_metric(x1, y1, x2, y2):
    """Returns the Euclidean distance bwtween two points in two dimensions"""
    
    d= np.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    return d

def get_distance_matrix(x,y,metric=euclidean_metric):
    """Given a set of N points (given by their x and y coordinates), returns a flattened distance matrix of
       size N(N-1)/2 between every point. This is similar to scipy.spatial.distance.pdist, but allows for a
       custom metric to be used efficiently"""
    
    # pair all the points up into large vectors so we can measure their distances between each other all at once
    n = len(x)

    newn = n*(n-1)//2

    x1 = np.zeros(newn)
    x2 = np.zeros(newn)
    y1 = np.zeros(newn)
    y2 = np.zeros(newn)

    # the pairing algorithm in a more readable form for clarity, but it's too slow
    # ind = 0
    # for i in range(n):
    #     for j in range(i+1,n):
    #         x1[ind] = x[i]
    #         x2[ind] = x[j]
    #         y1[ind] = y[i]
    #         y2[ind] = y[j]
    #         ind +=1
    
    # the algorithm in a quicker form
    ind = 0
    for i in range(n):
        dind = n-i
        # print(ind, ind+dind)
        x1[ind:ind+dind-1] = x[i]
        y1[ind:ind+dind-1] = y[i]
        x2[ind:ind+dind-1] = x[i+1:n]
        y2[ind:ind+dind-1] = y[i+1:n]
        ind += dind-1

    #now calculate the distances between all the points
    dist = metric(x1, y1, x2, y2)

    return dist


def get_subregion(x,y,xmin,xmax,ymin,ymax):
    """Given arrays of x and y coordinates, creates new arrays containing only the objects in the specified ranges,
       Also returns the indices of the original arrays for each point in the new arrays"""
    xp = []
    yp = []
    indices = []

    for i in range(len(x)):
        if x[i] > xmin and x[i] < xmax and y[i] > ymin and y[i] < ymax:
            xp.append(x[i])
            yp.append(y[i])
            indices.append(i)

    xp = np.asarray(xp)
    yp = np.asarray(yp)
    indices = np.asarray(indices)

    return xp, yp, indices 



def reproject_to_equator(ras, decs):
    """Takes a list of sky coordinates (in degrees) and converts them to a new spherical coordinate system 
       where their centre of mass lies on the equator at (0,0) degrees"""
    
    #first determine the centre of mass in ra and dec:
    ra_c = np.mean(ras)
    dec_c = np.mean(decs)

    #rotate in ra so that the mean of the points is at 0 degrees
    ras = ras - ra_c

    #Now ensure these are in the range (-180,180]
    ras = (ras + 180)%360 -180

    #Now we want to rotate in declination so that the points are at the equator... e.g. by dec_c degrees.
    # To do this, convert coords to Cartesian, then rotate in the x-z plane by dec_c degrees clockwise
    #    
    #    z^     *
    #     |    /
    #     |   /
    #     |  /
    #     | / dec_c
    #     |/_____________> x
    #
    #
    
    #convert to Cartesian
    x = np.cos(ras*DTOR)*np.cos(decs*DTOR)
    y = np.sin(ras*DTOR)*np.cos(decs*DTOR)
    z = np.sin(decs*DTOR)
    
    #rotate in x-z plane clockwise by dec_c
    xp = x*np.cos(dec_c*DTOR) + z*np.sin(dec_c*DTOR)
    zp = -x*np.sin(dec_c*DTOR) + z*np.cos(dec_c*DTOR)
    yp = y

    #Now convert back to spherical (and degrees)
    decs = np.arcsin(zp) * RTOD
    ras = np.arctan2(yp,xp) * RTOD


    return ras, decs