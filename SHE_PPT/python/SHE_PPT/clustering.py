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
from .coordinates import euclidean_metric, get_distance_matrix, get_subregion, reproject_to_equator


logger = getLogger(__name__)
 
# seed for the k means clustering
RANDOM_SEED=1


def find_blends(xs,ys, sep=10, metric=euclidean_metric):
    """returns a list of groups of blends. Each group is a list of the array indices of the blended objects"""
    
    #get distance matrix for all points to all other points
    dist = get_distance_matrix(xs, ys, metric=metric)

    #construct hierarchical linkage for all the objects
    linkage = H.linkage(dist)

    #now cluster those closer than sep, returning a list of cluster labels (this ranges from 1:n_clusters)
    labels = H.fcluster(linkage,t=sep,criterion="distance")
    
    #count how many objects are in each cluster
    # (returns an int array of length of the number of clusters)
    counts = np.bincount(labels)
    
    blends=[]
    #loop over all the clusters, and for ones with more than one object in them (e.g. blends), get the list of their indices
    for label, count in enumerate(counts):
        if count > 1:
            #gets the list of indices where labels==label
            blend = np.where(labels == label)[0]
            blends.append(blend)
    
    return blends


def all_same(items):
    return all(x == items[0] for x in items)

def update_blended(local_blends, global_blend_ids, local_indices, xs, ys, blend_id):
    """ Records the newly blended objects (local_blends) in the global blended list, and 
        updates the blended objects' positions to the centre of mass of the blend""" 
    
    for local_blend in local_blends:
        global_indices = local_indices[local_blend]

        #see if these objects are already identified as being blended.
        num_in_blend = len(local_blend)
        new = []
        existing = []
        for ind in global_indices:
            if global_blend_ids[ind] == -1:
                new.append(ind)
            else:
                existing.append(ind)
        
        if len(new) == num_in_blend:
            #This is a completely new batch of objects
            
            #increment the blend id by 1 and assign this id to these objects - we have a new blend!
            global_blend_ids[global_indices] = blend_id
            blend_id +=1

        else:
            #at least some of these objects belong to an existing blend

            #check all the identified objects belong to the same blend
            if not all_same(global_blend_ids[existing]):
                #TODO we need to work out how to handle this, beyond just printing a warning... 
                # although if this block of code gets executed something is horribly wrong anyway
                logger.warn("WARNING blended objects seem to belong to different blends... possibly everything is blended together (sep parameter too big?)")
                

            if len(existing) == num_in_blend:
                #we know about all of these objects - nothing more to do
                continue
            else:
                #some of these objects are new... add them to their existing neighbours' blend
                existing_id = global_blend_ids[existing[0]]
                global_blend_ids[new] = existing_id

    return blend_id


def merge_blended(xs, ys, global_blends):
    """For each blend, adjust the positions of the objects so they're all at the centre of mass of the blend"""
    n_blends = np.max(global_blends)
    
    #for each blend...
    for b in range(0,n_blends+1):
        #get the indices of the objects
        inds = np.where(global_blends == b)
        
        #get their x and y coordinates
        x_coords = xs[inds]
        y_coords = ys[inds]

        #find the mean
        xc, yc  = np.mean(x_coords), np.mean(y_coords)
        
        #set them all to the mean
        xs[inds] = xc
        ys[inds] = yc


    return xs, ys
    




def identify_all_blends(x,y, sep=10, metric = euclidean_metric, batchsize = 2000):
    """Finds all the blended objects in the input list of x and y coordinates of objects.
       returns updated x and y coordinate lists where all the blended objects' coordinates
       have been changed to the centre of mass of the blend, along with an array that 
       identifies the blended objects and the blend they belong to"""

    blend_ids = np.zeros(len(x),np.int64)-1
    xs = np.copy(x)
    ys = np.copy(y)

    #min/max values for x and y
    xmin_global = xs.min()
    xmax_global = xs.max()
    ymin_global = ys.min()
    ymax_global = ys.max()

    # Unfortunately due to memory and compute constrtaints we must identify the blends in batches
    # Each batch slightly overlaps its adjacent batches so that no objects are missed, although this
    # does mean occasionally identifying the same blends twice... however the function update_blended deals with this
    
    #calculate the number of batches in each direction
    nbatches = int(np.ceil(np.sqrt(len(x)/batchsize)))
    
    #width of each batch (without padding)
    wx = (xmax_global-xmin_global)/nbatches
    wy = (ymax_global-ymin_global)/nbatches

    blend_count = 0

    logger.info("Identifying blends in %d x %d batches",nbatches,nbatches)

    #loop over all the batches
    t0 = time.time()
    for i in range(nbatches):

        #calculate xmin and xmax for the batch (with 10% in each direction)
        xmin = xmin_global + i*wx - wx*0.1
        xmax = xmin_global +(i+1)*wx + wx*0.1

        for j in range(nbatches):

            #calculate ymin, ymax for the batch
            ymin = ymin_global + j*wy - wy*0.1
            ymax = ymin_global +(j+1)*wy + wy*0.1
            
            # create arrays for the batch, and an "indices" array that lets us transform
            # the batch's indices into global indices for all the objects
            xp, yp, indices = get_subregion(xs,ys,xmin,xmax, ymin, ymax)

            if len(xp) < 1:
                logger.debug("Batch(%d,%d): Skipping as no objects in batch",(i,j))
                continue
            
            #get the list of blends. Each blend is a list of indices of the objects in that blend
            local_blends = find_blends(xp, yp, sep,metric=metric)
            
            #store the blends in the global array, update their positions to the centre of mass of the blend
            new_blend_count = update_blended(local_blends, blend_ids, indices, xs, ys, blend_count)

            new_blends = new_blend_count-blend_count
            blend_count = new_blend_count

            logger.debug("Batch(%d,%d): Number of objects = %d, Number of new blends = %d",i,j,len(xp),new_blends)
    
    #Now adjust the positions of all blended objects so they are the centre of mass of ther blends
    xs, ys = merge_blended(xs, ys, blend_ids)

    t1 = time.time()
    n_blended = len(np.where(blend_ids >= 0)[0])
    n_objs = len(xs)
    logger.info("Time taken to identify blends = %fs",t1-t0)
    logger.info("Total number of blended objects = %d",n_blended)
    logger.info("Total number of blends = %d",blend_count)
    logger.info("Fraction of objects that are blended = %f",(n_blended/n_objs))
    logger.info("Mean number of objects per blend = %f",(n_blended/blend_count))

    return xs, ys, blend_ids



def partition_into_batches(xs, ys, batchsize=20, nbatches = None, seed=RANDOM_SEED):
    """Given arrays of the objects' x and y coordinates, partition them into many batches approximately
       of size batchsize, or if nbatches != None, partition them into nbatches batches"""
    
    if nbatches is not None:
        k = nbatches
        logger.info("Splitting into k = %d batches (k user specified)",k)
    else:
        k = int(np.ceil(len(xs)/batchsize))
        logger.info("Splitting into k = %d batches",k)
    
    #create an "observations" array for the clusteting
    obs = np.zeros((len(xs),2))
    
    #calculate the standard deviations of x and y
    stdxs = np.std(xs)
    stdys = np.std(ys)
    
    #create "observations" array for the kmeans, normalised to the standard deviations of ra and dec
    #(required for the clustering algorithm)
    obs[:,0] = xs/stdxs
    obs[:,1] = ys/stdys

    #annoyingly the version of scipy Euclid has (1.3.2 as of Nov 2021) uses numpy's internal random state,
    #so to ensure consistent results (whilst not messing with numpy's existing random state) we take a 
    #copy of its state and create a new one according to our seed, then once we're done, put the original
    #state back
    random_state = np.random.get_state()
    np.random.seed(seed)

    #cluster the objects
    t0=time.time()
    clusters, labels = K.kmeans2(obs,k,iter=20,minit="points",check_finite=False)
    t1 = time.time()
    logger.info("Batching took %f s",(t1-t0))

    #put numpy's random state back
    np.random.set_state(random_state)
    
    #Get an array containing the number of objects in each batch
    ns = np.bincount(labels)

    logger.info("Mean number of objects per batch = %f",np.mean(ns))
    logger.info("Min/Max number of objects per batch = (%d, %d)",ns.min(), ns.max())
    logger.info("Standard deviation of number of objects in batch = %f",np.std(ns))
    
    #nultiply the centres of the clusters by the standard deviations of x and y to return them to normal units
    clusters[:,0] *= stdxs
    clusters[:,1] *= stdys

    return clusters, labels, ns