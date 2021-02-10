""" convert_sim_catalog.py

    Created: 2019/02/26

    Run with a command such as:
    
    E-Run SHE_PPT 0.9 python3 /home/brg/Work/Projects/SHE_PPT/SHE_PPT/scripts/convert_sim_catalog.py EUC_SIM_TUGALCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --star_cat EUC_SIM_TUSTARCAT-52929_20181009T103007.403Z_SC456-VIS-C7a_T2.fits --source_dir /mnt/cephfs/share/SC456/SIM-VIS/vis_science_T2/intermediate/TU/data --max_mag_vis 25.5 --obj_cat obj_cat.xml --dest_dir .

"""

__updated__ = "2019-06-24"

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

from astropy.table import Table, vstack

from SHE_PPT import products
from SHE_PPT.file_io import find_file, get_allowed_filename, write_xml_product
from SHE_PPT.table_formats.mer_final_catalog import initialise_mer_final_catalog
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
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
    obj_gal_cat = initialise_mer_final_catalog(optional_columns=[mfc_tf.SHE_FLAG, mfc_tf.STAR_FLAG, mfc_tf.STAR_PROB],
                                               init_cols={mfc_tf.ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                                                 dtype=mfc_tf.dtypes[mfc_tf.ID]),
                                                          mfc_tf.gal_x_world: sim_gal_cat['ra'][observed_gal_mask].data.astype(
                                                   mfc_tf.dtypes[mfc_tf.gal_x_world]),
        mfc_tf.gal_y_world: sim_gal_cat['dec'][observed_gal_mask].data.astype(
                                                   mfc_tf.dtypes[mfc_tf.gal_y_world]),
        mfc_tf.seg_ID: np.linspace(1, num_gals, num_gals, endpoint=True,
                                                   dtype=mfc_tf.dtypes[mfc_tf.seg_ID]),
        mfc_tf.vis_det: np.ones(num_gals,
                                                   dtype=mfc_tf.dtypes[mfc_tf.vis_det]),
        mfc_tf.SHE_FLAG: np.zeros(num_gals,
                                                   dtype=mfc_tf.dtypes[mfc_tf.SHE_FLAG]),
        mfc_tf.STAR_FLAG: np.zeros(num_gals,
                                                   dtype=mfc_tf.dtypes[mfc_tf.STAR_FLAG]),
        mfc_tf.STAR_PROB: np.zeros(num_gals,
                                                   dtype=mfc_tf.dtypes[mfc_tf.STAR_PROB]),
    })

    # If we're including a star catalogue, create and stack that with the galaxy catalogue
    if sim_star_cat is not None:

        # Get a list of the good galaxies
        observed_star_mask = sim_star_cat['VIS'] <= args.max_mag_vis

        num_stars = len(sim_star_cat['unique_star_id'][observed_star_mask])

        obj_star_cat = initialise_mer_final_catalog(optional_columns=[mfc_tf.SHE_FLAG, mfc_tf.STAR_FLAG, mfc_tf.STAR_PROB],
                                                    init_cols={mfc_tf.ID: np.linspace(1, num_stars, num_stars, endpoint=True,
                                                                                      dtype=mfc_tf.dtypes[mfc_tf.ID]),
                                                               mfc_tf.gal_x_world: sim_star_cat['RA2000.0'][observed_star_mask].data.astype(
                                                        mfc_tf.dtypes[mfc_tf.gal_x_world]),
            mfc_tf.gal_y_world: sim_star_cat['DEC2000.0'][observed_star_mask].data.astype(
                                                        mfc_tf.dtypes[mfc_tf.gal_y_world]),
            mfc_tf.seg_ID: np.linspace(1, num_stars, num_stars, endpoint=True,
                                                        dtype=mfc_tf.dtypes[mfc_tf.seg_ID]),
            mfc_tf.vis_det: np.ones(num_stars,
                                                        dtype=mfc_tf.dtypes[mfc_tf.vis_det]),
            mfc_tf.SHE_FLAG: np.zeros(num_stars,
                                                        dtype=mfc_tf.dtypes[mfc_tf.SHE_FLAG]),
            mfc_tf.STAR_FLAG: np.ones(num_stars,
                                                        dtype=mfc_tf.dtypes[mfc_tf.STAR_FLAG]),
            mfc_tf.STAR_PROB: np.ones(num_stars,
                                                        dtype=mfc_tf.dtypes[mfc_tf.STAR_PROB]),
        })

        obj_cat = vstack([obj_gal_cat, obj_star_cat])
    else:
        obj_cat = obj_gal_cat

    # Create a data product for the output
    obj_cat_filename = get_allowed_filename(type_name="FINAL-CATALOG",
                                            instance_id="TU-CONV",
                                            extension=".fits",
                                            release="00.09",
                                            subdir=None,
                                            processing_function="MER")
    obj_cat_prod = products.mer_final_catalog.create_detections_product(obj_cat_filename)

    write_xml_product(obj_cat_prod, args.obj_cat, workdir=args.dest_dir)

    # Write out the table
    obj_cat.write(obj_cat_filename, overwrite=True)

    return


if __name__ == "__main__":
    main()
