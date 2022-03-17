""" @file generate_mock_mer_catalogues.py

    Created 16 Mar 2022.

    Utilities to generate mock mer final catalogues for smoke tests.
"""

__updated__ = "2022-03-17"

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

from SHE_PPT.table_formats.mer_final_catalog import tf, initialise_mer_final_catalog
from SHE_PPT.products import mer_final_catalog
from SHE_PPT.file_io import get_allowed_filename, write_xml_product
from SHE_PPT import __version__ as ppt_version

from SHE_PPT.logging import getLogger

logger = getLogger(__name__)

def create_catalogue(obj_coords=[], workdir="."):
    """
       Creates a mock dpdMerFinalCatalog for a list of object coordinates

       Arguments:
         - obj_coords: a list of world coordinate pairs of the form (dec, ra)
         - workdir: the workdir to write the files to

       Outputs:
         - product_filename: The filename of the created dpdMerFinalCatalog product
    """

    logger.info("Creating MER final catalogue table with %d object(s)"%len(obj_coords))
    
    #initialise the mer_final_catalog table
    table = initialise_mer_final_catalog()
    
    #loop over all objects and add them to the table
    for i, coords in enumerate(obj_coords):
        obj_id = i+1
        
        #TODO: Improve how this done as adding rows to a table is ASTRONOMICALLY slow.
        # maybe initialise the table with these columns instead?
        table.add_row(vals={
                            tf.ID: obj_id,
                            tf.gal_x_world: coords[1],
                            tf.gal_y_world: coords[0],
                            tf.seg_ID: obj_id,
                            tf.vis_det: 1,
                            tf.FLUX_VIS_APER: 1E-10, #WHERE DOES THIS COME FROM?
                            tf.SEGMENTATION_AREA: 1 #WHERE DOES THIS COME FROM?
                            })
    
    #get a filename for the table
    table_filename = get_allowed_filename("MER-CAT", "00", version=ppt_version)
    qualified_table_filename = os.path.join(workdir, table_filename)
     
    #write the table to file
    logger.info("Writing table to %s"%table_filename)
    table.write(qualified_table_filename)
    
    #create the data product
    product=mer_final_catalog.create_dpd_mer_final_catalog(filename=table_filename)

    #get a name for it
    product_filename = get_allowed_filename("PROD-MER-CAT", "00", version=ppt_version, subdir="", extension=".xml")
    qualified_product_filename = os.path.join(workdir,product_filename)
    
    #write the product to file
    logger.info("Writing dpdMerFinalCatalog product to %s"%product_filename)
    write_xml_product(product, qualified_product_filename)

    return product_filename

    


