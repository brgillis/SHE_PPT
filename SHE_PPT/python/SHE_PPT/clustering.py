"""
File: python/SHE_PPT/clustering.py

Created on: 03/11/21

Contains code for clustering points together
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

import time

import numpy as np
import scipy.cluster.hierarchy as H
import scipy.cluster.vq as K

from SHE_PPT.logging import getLogger
from .coordinates import euclidean_metric, get_distance_matrix, get_subregion

logger = getLogger(__name__)

# seed for the k means clustering
RANDOM_SEED = 1


def _find_groups(xs, ys, sep=1., metric=euclidean_metric):
    """returns a list of groups of potential blends. Each group is a list of the array indices of the identified objects

    Parameters:
        xs (np.ndarray)  : The x coordinates of the objects
        ys (np.ndarray)  : The y coordinates of the objects
        sep (float)      : The maximum separation between objects to count them as belonging to the same group
        metric(function) : The distance metric to use d=f(x1,y1,x2,y2)

    Returns:
        groups (list)    : a list of the identified groups. Each group is a list (np.ndarray) of the array indices
                           of the objects belonging to that group)
    """

    # get distance matrix for all points to all other points
    dist = get_distance_matrix(xs, ys, metric=metric)

    # construct hierarchical linkage for all the objects
    linkage = H.linkage(dist)

    # now cluster those closer than sep, returning a list of cluster labels (this ranges from 1:n_clusters)
    labels = H.fcluster(linkage, t=sep, criterion="distance")

    # count how many objects are in each cluster
    # (returns an int array of length of the number of clusters)
    counts = np.bincount(labels)

    groups = []
    # loop over all the clusters, and for ones with more than one object in them (e.g. groups), get the list of their
    # indices
    for label, count in enumerate(counts):
        if count > 1:
            # gets the list of indices where labels==label
            group = np.where(labels == label)[0]
            groups.append(group)

    return groups


def _all_same(items):
    """Returns True if all the items in the list are identical, False otherwise"""
    return len(set(items)) == 1


def _update_grouped(local_groups, global_group_ids, local_indices, xs, ys, group_id):
    """ Records the newly grouped objects (local_groups) in the global grouped list


        Parameters:
            local_groups (list) : The list of the newly identified groups (np.ndarray of the array indices of the
            objects in the group)
            global_group_ids (np.ndarray) : An int array containing the group_id of each object (-1 means ungrouped)
            local_indices (np.ndarray): An int array of the indices from the original object list for this local list
            of objects
            xs (np.ndarray): x coordinates of the objects
            ys (np.ndarray): y coordinates of the objects
            group_id (int) : The current maximum id of any group in the global group list (e.g. a counter of how many
            distinct groups we have)

        Returns:
            group_id (int) : Same as group_id above, just incremented by however many new groups were detected  """

    for local_group in local_groups:
        global_indices = local_indices[local_group]

        # see if these objects are already identified as being grouped.
        num_in_group = len(local_group)
        new = []
        existing = []
        for ind in global_indices:
            if global_group_ids[ind] == -1:
                new.append(ind)
            else:
                existing.append(ind)

        if len(new) == num_in_group:
            # This is a completely new batch of objects

            # increment the group id by 1 and assign this id to these objects - we have a new group!
            global_group_ids[global_indices] = group_id
            group_id += 1

        else:
            # at least some of these objects belong to an existing group

            # check all the identified objects belong to the same group
            if not _all_same(global_group_ids[existing]):
                # TODO we need to work out how to handle this, beyond just printing a warning...
                # although if this block of code gets executed something is horribly wrong anyway
                logger.warn(
                    "WARNING grouped objects seem to belong to different groups... possibly everything is grouped "
                    "together (sep parameter too big?)")

            if len(existing) == num_in_group:
                # we know about all of these objects - nothing more to do
                continue
            else:
                # some of these objects are new... add them to their existing neighbours' group
                existing_id = global_group_ids[existing[0]]
                global_group_ids[new] = existing_id

    return group_id


def _merge_grouped(xs, ys, global_groups):
    """For each group, adjust the positions of the objects so they're all at the centre of mass of the group

        Parameters:
            xs (np.ndarray) : list of the x coordinates of the objects
            ys (np.ndarray) : list of the y coordinates of the objects
            global_groups (np.ndarray) : int array with the group_id for each object

        Returns:
            xs (np.ndarray): The x coordinates of the objects (updated to the COM of the group)
            ys (np.ndarray): The x coordinates of the objects (updated to the COM of the group)
        """
    n_groups = np.max(global_groups)

    # for each group...
    for b in range(0, n_groups + 1):
        # get the indices of the objects
        inds = np.where(global_groups == b)

        # get their x and y coordinates
        x_coords = xs[inds]
        y_coords = ys[inds]

        # find the mean
        xc, yc = np.mean(x_coords), np.mean(y_coords)

        # set them all to the mean
        xs[inds] = xc
        ys[inds] = yc

    return xs, ys


def identify_all_groups(x, y, sep=1., metric=euclidean_metric, batchsize=2000):
    """Finds all the grouped objects in the input list of x and y coordinates of objects.
       returns updated x and y coordinate lists where all the grouped objects' coordinates
       have been changed to the centre of mass of the group, along with an array that
       identifies the grouped objects and the group they belong to.

       A group is defined of a set of >1 objects. Ungroupped objects have a group_id of -1,
       whilst the indices for groups begins at 0

        Parameters:
            x (np.ndarray) : The list of x coordinates of the objects
            y (np.ndarray) : The list of y coordinates of the objects
            sep (float) : The maximum separation between any two objects to group them together
            metric (function) : The distance metric to use d = f(x1,x2,y1,y2)
            batchsize (int) : The number of objects to process at once when determining groups

        Returns:
            xs (np.ndarray) : updated x coordinates of the objects
            ys (np.ndarray) : updated y coordinates of the objects
            group_ids (np.ndarray) : int array of the group_id for each object """

    group_ids = np.zeros(len(x), np.int64) - 1
    xs = np.copy(x)
    ys = np.copy(y)

    # min/max values for x and y
    xmin_global = xs.min()
    xmax_global = xs.max()
    ymin_global = ys.min()
    ymax_global = ys.max()

    # Unfortunately due to memory and compute constrtaints we must identify the groups in batches
    # Each batch slightly overlaps its adjacent batches so that no objects are missed, although this
    # does mean occasionally identifying the same groups twice... however the function update_grouped deals with this

    # calculate the number of batches in each direction
    nbatches = int(np.ceil(np.sqrt(len(x) / batchsize)))

    # width of each batch (without padding)
    wx = (xmax_global - xmin_global) / nbatches
    wy = (ymax_global - ymin_global) / nbatches

    group_count = 0

    logger.info("Grouping objects who have a separation of less than %f" % sep)

    logger.info("Identifying groups in %d x %d batches", nbatches, nbatches)

    # loop over all the batches
    t0 = time.time()
    for i in range(nbatches):

        # calculate xmin and xmax for the batch (with 10% in each direction)
        xmin = xmin_global + i * wx - wx * 0.1
        xmax = xmin_global + (i + 1) * wx + wx * 0.1

        for j in range(nbatches):

            # calculate ymin, ymax for the batch
            ymin = ymin_global + j * wy - wy * 0.1
            ymax = ymin_global + (j + 1) * wy + wy * 0.1

            # create arrays for the batch, and an "indices" array that lets us transform
            # the batch's indices into global indices for all the objects
            xp, yp, indices = get_subregion(xs, ys, xmin, xmax, ymin, ymax)

            if len(xp) < 1:
                logger.debug("Batch(%d,%d): Skipping as no objects in batch", i, j)
                continue

            # get the list of groups. Each group is a list of indices of the objects in that group
            local_groups = _find_groups(xp, yp, sep, metric=metric)

            # store the groups in the global array, update their positions to the centre of mass of the group
            new_group_count = _update_grouped(local_groups, group_ids, indices, xs, ys, group_count)

            new_groups = new_group_count - group_count
            group_count = new_group_count

            logger.debug("Batch(%d,%d): Number of objects = %d, Number of new groups = %d", i, j, len(xp), new_groups)

    # Now adjust the positions of all grouped objects so they are the centre of mass of ther groups
    xs, ys = _merge_grouped(xs, ys, group_ids)

    t1 = time.time()
    n_grouped = len(np.where(group_ids >= 0)[0])
    n_objs = len(xs)
    logger.info("Time taken to identify groups = %fs", t1 - t0)
    logger.info("Total number of grouped objects = %d", n_grouped)
    logger.info("Total number of groups = %d", group_count)
    logger.info("Fraction of objects that are grouped = %f", (n_grouped / n_objs))
    if group_count > 0:
        logger.info("Mean number of objects per group = %f", (n_grouped / group_count))

    return xs, ys, group_ids


def partition_into_batches(xs, ys, batchsize=20, nbatches=None, seed=RANDOM_SEED):
    """Given arrays of the objects' x and y coordinates, spatially partition them into many batches
       approximately of size batchsize, or if nbatches != None, partition them into nbatches batches

        Parameters:
            xs (np.ndarray) : x coordinates of the objects
            ys (np.ndarray) : y coordinates of the objects
            batchsize (int) : The mean number of objects in each batch
            nbatches (int) : The number of batches to produce (if this is set, overrides batchsize)
            seed (int) : The seed for the random number generator used in the batching

        Returns:
            clusters (np.ndarray) : (nbatches,2) array of the centres of each cluster
            labels (np.ndarray)  : an int array of the batch number each object belongs to
            ns (np.ndarray) : the number of objects in each batch
           """

    if nbatches is not None:
        k = nbatches
        logger.info("Splitting into k = %d batches (k user specified)", k)
    else:
        k = int(np.ceil(len(xs) / batchsize))
        logger.info("Splitting into k = %d batches", k)

    # create an "observations" array for the clusteting
    obs = np.zeros((len(xs), 2))

    # calculate the standard deviations of x and y
    stdxs = np.std(xs)
    stdys = np.std(ys)

    # create "observations" array for the kmeans, normalised to the standard deviations of ra and dec
    # (required for the clustering algorithm)
    obs[:, 0] = xs / stdxs
    obs[:, 1] = ys / stdys

    # cluster the objects
    t0 = time.time()
    clusters, labels = K.kmeans2(obs, k, iter=20, minit="points", check_finite=False, seed=seed)
    t1 = time.time()
    logger.info("Batching took %f s", (t1 - t0))

    # Get an array containing the number of objects in each batch
    ns = np.bincount(labels)

    logger.info("Mean number of objects per batch = %f", np.mean(ns))
    logger.info("Min/Max number of objects per batch = (%d, %d)", ns.min(), ns.max())
    logger.info("Standard deviation of number of objects in batch = %f", np.std(ns))

    # nultiply the centres of the clusters by the standard deviations of x and y to return them to normal units
    clusters[:, 0] *= stdxs
    clusters[:, 1] *= stdys

    return clusters, labels, ns
