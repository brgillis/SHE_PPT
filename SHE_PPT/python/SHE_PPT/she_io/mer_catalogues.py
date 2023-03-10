#
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
#

"""
:file: python/SHE_PPT/she_io/mer_catalogues.py

:date: 15/02/23
:author: Gordon Gibb

"""

import os
import json

import numpy as np
from astropy.table import Table, vstack

from ST_DM_DmUtils.DmUtils import read_product_metadata

import ElementsKernel.Logging as log

logger = log.getLogger(__name__)

def read_mer_final_catalogue(cat_file, workdir = ".", object_list_prod = None):
    """
    Reads a MER catalogue (product or listfile of products) and returns the (stacked) mer_final_catalog table

    Inputs:
     - cat_file: listfile of DpdMerFinalCatalog products, or a DpdMerFinalCatalog product
     - workdir: working directory
     - object_list_prod: (optional) DpdSheObjectIdList product (if supplied, the output catalog contains _only_ the object_ids in this product)

    Outputs:
     - mer_cat: The MER final catalog (astropy table)
     - products: a list of the mer products
    """
    
    #we assume it is a json so try to parse that first
    try:
        mer_cat, prods = _read_mer_listfile(cat_file, workdir)
        
    except json.decoder.JSONDecodeError:
        # File is a data product? Try that
        mer_cat, prod = _read_mer_final_cat_product(cat_file, workdir)
        prods = [prod]

    if object_list_prod:
        logger.info("Reading object_id_list product %s", os.path.join(workdir,object_list_prod))
        obj_dpd = read_product_metadata(os.path.join(workdir,object_list_prod))

        obj_list = obj_dpd.Data.ObjectIdList

        if len(obj_list) == 0:
            raise ValueError("Input Object_id_list contains no objects")

        mer_cat = prune_mer_catalogue(mer_cat, obj_list)
        
        

    logger.info("Obtained detection table with %d objects from %d input MER final catalogue(s)", len(mer_cat), len(prods))
    
    return mer_cat, prods



def prune_mer_catalogue(mer_cat, obj_list):
    n_orig = len(mer_cat)
    n_objs = len(obj_list)
        
    _, inds, _ = np.intersect1d(mer_cat["OBJECT_ID"], obj_list, return_indices=True)

    pruned_mer_cat = mer_cat[inds]
    n_new = len(pruned_mer_cat)

    if n_new < n_orig:
        logger.info("Pruned %s objects from catalog that were not in the object list", n_orig-n_new)
    if n_new < n_objs:
        logger.warning("%d objects in the object list were not present in the catalog", n_objs-n_new)

    if len(pruned_mer_cat) == 0:
        raise ValueError("Pruned MER Final Catalog contains no objects")

    return pruned_mer_cat

    
    


def _read_mer_listfile(filename,workdir):
    qualified_filename = os.path.join(workdir,filename)

    with open(qualified_filename, "r") as f:
        mer_prods = json.load(f)
    logger.info("Parsed MER catalog listfile %s", qualified_filename)

    

    if len(mer_prods) == 0:
        raise ValueError("Empty listfile of mer final catalogs provided")
    
    tables, dpds = zip(*[_read_mer_final_cat_product(prod, workdir) for prod in mer_prods])

    return vstack(tables), dpds
    

def _read_mer_final_cat_product(filename, workdir):
    qualified_filename = os.path.join(workdir,filename)

    datadir = os.path.join(workdir,"data")

    logger.info("Reading MER final catalog product %s", qualified_filename)

    dpd = read_product_metadata(qualified_filename)

    cat_fits = dpd.Data.DataStorage.DataContainer.FileName

    t = Table.read(os.path.join(datadir,cat_fits))

    return t, dpd


    

