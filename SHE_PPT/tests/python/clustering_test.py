""" @file clustering_test.py

    Created 26 Jan 2022

    Tests of functions in the 'coordinates' module.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2022-01-27"

import math

import numpy as np

from SHE_PPT.clustering import identify_all_groups, partition_into_batches
from SHE_PPT.testing.utility import SheTestCase


class Test_coordinates(SheTestCase):

    def test_identify_all_groups(self):
        """Tests identify_all_groups by generating clouds of points and making sure the correct number of groups
           are identified in them"""

        # baseline number of points in each direction
        nx = ny = 128

        x = []
        y = []

        # generate regular grid of points with separation 1, this is our base set of points for the tests
        for i in range(nx):
            x += [i for j in range(ny)]
            y += [j for j in range(ny)]

        # identify groups in this with separation of 0.9 - should find 0 groups as all points have a separation of >= 1
        xx, yy, groups = identify_all_groups(x, y, sep = 0.9)

        # make sure there are 0 groups
        n_groups = groups.max() + 1
        assert (n_groups == 0)

        # now add two points in the middle of squares of points, creating two groups of 5 objects
        x2, y2 = x + [1.5, 10.5], y + [1.5, 10.5]

        xx, yy, groups = identify_all_groups(x2, y2, sep = 0.9)

        # make sure there are now two groups
        n_groups = groups.max() + 1
        assert (n_groups == 2)

        counts = np.bincount(groups + 1)
        # make sure number of un-grouped objects is correct
        assert (counts[0] == nx * ny - 2 * 4)
        # make sure the count in each group is correct
        assert (counts[1] == 5)
        assert (counts[2] == 5)

        # now add a chain of nx-1 points in the x-direction to connect a whole line of points into a single group
        x_chain = x + [i + 0.5 for i in range(nx - 1)]
        y_chain = y + [20 for i in range(nx + 1)]

        xx, yy, groups = identify_all_groups(x_chain, y_chain, sep = 0.9)

        # ensure we have one group
        n_groups = groups.max() + 1
        assert (n_groups == 1)

        counts = np.bincount(groups + 1)
        # make sure number of un-grouped objects is correct
        assert (counts[0] == nx * ny - nx)
        # make sure the count in each group is correct
        assert (counts[1] == nx * 2 - 1)

        # extreme test case: have separation large enough that all objects are collected into one group
        xx, yy, groups = identify_all_groups(x, y, sep = 1.1)

        # ensure we have one group
        n_groups = groups.max() + 1
        assert (n_groups == 1)

    def test_partition_into_batches(self):

        # create a unit square of n random points
        n = 10000
        x = np.random.random(n)
        y = np.random.random(n)

        # partition into 20 batches
        nbatches = 20
        clusters, batch_ids, n_per_batch = partition_into_batches(x, y, nbatches = nbatches)
        # make sure we have 20 batches
        assert (len(n_per_batch) == nbatches)
        # make sure all the objects have been batched
        assert (n_per_batch.sum() == n)
        # make sure all objects are assigned to a batch
        assert (len(batch_ids) == n)
        assert (batch_ids.min() == 0)
        assert (batch_ids.max() == nbatches - 1)

        # partition into batches with batchsize 20
        batchsize = 20
        clusters, batch_ids, n_per_batch = partition_into_batches(x, y, batchsize = batchsize)

        # make sure we have the expected number of batches
        n_expected = math.ceil(n / batchsize)
        assert (len(n_per_batch) == n_expected)
        # make sure all the objects have been batched
        assert (n_per_batch.sum() == n)
        # make sure all objects are assigned to a batch
        assert (len(batch_ids) == n)
        assert (batch_ids.min() == 0)
        assert (batch_ids.max() == n_expected - 1)
