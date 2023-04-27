""" @file generate_mock_mer_catalogues.py

    Created 16 Mar 2022.

    Utilities to generate mock mer final catalogues for smoke tests.
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

import numpy as np

from SHE_PPT import __version__ as ppt_version
from SHE_PPT.file_io import get_allowed_filename, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products import mer_final_catalog
from SHE_PPT.table_formats.mer_final_catalog import initialise_mer_final_catalog, tf
from SHE_PPT.table_utility import is_in_format

logger = getLogger(__name__)


def create_catalogue(obj_coords=[], workdir=".", group_ids=None, tile_id=1, obs_ids = []):
    """
       Creates a mock dpdMerFinalCatalog for a list of object coordinates

       Arguments:
         - obj_coords: a list of world coordinates (astropy.coordinates.SkyCoord)
         - workdir: the workdir to write the files to
         - group_ids: the group_ids of the objects. If None, this column is not created
           in the table
         - tile_id: The ID of the MER tile
         - obs_ids: List of observations covering this tile

       Outputs:
         - product_filename: The filename of the created dpdMerFinalCatalog product
         - object_ids: a list of the MER object ids of each object
    """

    logger.info("Creating MER final catalogue table with %d object(s)" % len(obj_coords))

    n_objs = len(obj_coords)

    # create the table columns

    # NOTE: we wish to make sure the object_ids do not overlap with their indices (e.g. 0...n-1),
    # so the ID list starts at n to prevent this.
    object_ids = [n_objs + i for i in range(n_objs)]
    ras = [c.ra.deg for c in obj_coords]
    decs = [c.dec.deg for c in obj_coords]
    vis_det = np.ones(n_objs, dtype=np.int16)
    flux_vis_aper = np.ones(n_objs, dtype=np.float32) * 1E-10
    seg_area = np.ones(n_objs, dtype=np.int32)

    # create the table
    table = initialise_mer_final_catalog(init_cols={
        tf.ID: object_ids,
        tf.gal_x_world: ras,
        tf.gal_y_world: decs,
        tf.seg_ID: object_ids,
        tf.vis_det: vis_det,
        tf.FLUX_VIS_APER: flux_vis_aper,
        tf.SEGMENTATION_AREA: seg_area})

    if group_ids is not None:
        table.add_column(group_ids, name=tf.GROUP_ID)

    assert is_in_format(table, tf)

    # get a filename for the table
    table_filename = get_allowed_filename("MER-CAT", "00", version=ppt_version)
    qualified_table_filename = os.path.join(workdir, table_filename)

    # write the table to file
    logger.info("Writing table to %s" % table_filename)
    table.write(qualified_table_filename)

    # create the data product
    product = mer_final_catalog.create_dpd_mer_final_catalog(filename=table_filename)
    product.Data.TileIndex = tile_id
    product.Data.ObservationIdList = obs_ids

    # get a name for it
    product_filename = get_allowed_filename("PROD-MER-CAT", "00", version=ppt_version, subdir="",
                                            extension=".xml")
    qualified_product_filename = os.path.join(workdir, product_filename)

    # write the product to file
    logger.info("Writing dpdMerFinalCatalog product to %s" % product_filename)
    write_xml_product(product, qualified_product_filename)

    return product_filename, object_ids
