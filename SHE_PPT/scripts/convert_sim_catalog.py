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

import argparse

from os.path import join
from SHE_PPT import products
from SHE_PPT.file_io import find_file, get_allowed_filename, write_xml_product
from SHE_PPT.table_formats.detections import initialise_detections_table
from SHE_PPT.table_formats.detections import tf as detf
from astropy.table import Table, vstack
import numpy as np


def main():
    """
    @brief
        Alternate entry point for non-Elements execution.
    """

    parser = argparse.ArgumentParser()

    # Input arguments
    parser.add_argument('gal_cat', default=None, type=str,
                        help="OU-SIM's True Universe galaxy catalogue.")
    parser.add_argument('--star_cat', default=None, type=str,
                        help="OU-SIM's True Universe star catalogue (default None).")
    parser.add_argument('--source_dir', default='.', type=str,
                        help="Directory in which source catalogues are contained (default '.').")
    parser.add_argument('--max_mag_vis', default=25.5, type=float,
                        help="Maximum VIS magnitude for inclusion in the object catalogue.")

    # Output arguments
    parser.add_argument('--obj_cat', default="obj_cat.xml", type=str,
                        help="Target Final Catalog product to be created (default obj_cat.xml)")
    parser.add_argument('--dest_dir', default='.', type=str,
                        help="Directory in which output catalogue is to be created (default '.').")

    args = parser.parse_args()

    # Read in the galaxy (and optionally star) catalogues
    if args.gal_cat is None:
        raise ValueError("Galaxy catalogue must be provided via the --gal_cat argument.")

    sim_gal_cat = Table.read(find_file(args.gal_cat, path=args.source_dir))

    if args.star_cat is None:
        sim_star_cat = None
    else:
        sim_star_cat = Table.read(find_file(args.star_cat, path=args.source_dir))

    # Get a list of the good galaxies
    observed_gal_mask = sim_gal_cat['VIS'] <= args.max_mag_vis

    num_gals = len(sim_gal_cat['id'][observed_gal_mask])

    # Initialize the output table with the desired columns
    obj_gal_cat = initialise_detections_table(optional_columns=[detf.SHE_FLAG, detf.STAR_FLAG, detf.STAR_PROB],
                                              init_cols={detf.ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                              dtype=detf.dtypes[detf.ID]),
                                                         detf.gal_x_world: sim_gal_cat['ra'][observed_gal_mask].data.astype(
                                                             detf.dtypes[detf.gal_x_world]),
                                                         detf.gal_y_world: sim_gal_cat['dec'][observed_gal_mask].data.astype(
                                                             detf.dtypes[detf.gal_y_world]),
                                                         detf.seg_ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                  dtype=detf.dtypes[detf.seg_ID]),
                                                         detf.vis_det: np.ones(num_gals,
                                                                               dtype=detf.dtypes[detf.vis_det]),
                                                         detf.SHE_FLAG: np.zeros(num_gals,
                                                                                 dtype=detf.dtypes[detf.SHE_FLAG]),
                                                         detf.STAR_FLAG: np.zeros(num_gals,
                                                                                  dtype=detf.dtypes[detf.STAR_FLAG]),
                                                         detf.STAR_PROB: np.zeros(num_gals,
                                                                                  dtype=detf.dtypes[detf.STAR_PROB]),
                                                         })

    # If we're including a star catalogue, create and stack that with the galaxy catalogue
    if sim_star_cat is not None:

        # Get a list of the good galaxies
        observed_star_mask = sim_star_cat['VIS'] <= args.max_mag_vis

        num_stars = len(sim_star_cat['unique_star_id'][observed_star_mask])

        obj_star_cat = initialise_detections_table(optional_columns=[detf.SHE_FLAG, detf.STAR_FLAG, detf.STAR_PROB],
                                                   init_cols={detf.ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                   dtype=detf.dtypes[detf.ID]),
                                                              detf.gal_x_world: sim_star_cat['RA2000.0'][observed_star_mask].data.astype(
                                                                  detf.dtypes[detf.gal_x_world]),
                                                              detf.gal_y_world: sim_star_cat['DEC2000.0'][observed_star_mask].data.astype(
                                                                  detf.dtypes[detf.gal_y_world]),
                                                              detf.seg_ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                       dtype=detf.dtypes[detf.seg_ID]),
                                                              detf.vis_det: np.ones(num_gals,
                                                                                    dtype=detf.dtypes[detf.vis_det]),
                                                              detf.SHE_FLAG: np.zeros(num_gals,
                                                                                      dtype=detf.dtypes[detf.SHE_FLAG]),
                                                              detf.STAR_FLAG: np.ones(num_gals,
                                                                                      dtype=detf.dtypes[detf.STAR_FLAG]),
                                                              detf.STAR_PROB: np.ones(num_gals,
                                                                                      dtype=detf.dtypes[detf.STAR_PROB]),
                                                              })

        obj_cat = vstack([obj_gal_cat, obj_star_cat])
    else:
        obj_cat = obj_gal_cat

    # Create a data product for the output
    obj_cat_filename = get_allowed_filename(type_name="FINAL_CATALOG",
                                            instance_id="FROM_SIM",
                                            extension=".fits",
                                            release="00.09",
                                            subdir=None,
                                            processing_function="MER")
    obj_cat_prod = products.detections.create_detections_product(obj_cat_filename)

    write_xml_product(obj_cat_prod, join(args.obj_cat, args.dest_dir))

    # Write out the table
    obj_cat.write(obj_cat_filename, overwrite=True)

    return


if __name__ == "__main__":
    main()
