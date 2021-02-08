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

from astropy.table import Table

from EL_CoordsUtils import telescope_coords as tc
from SHE_PPT.file_io import find_file
import numpy as np

mdb_filename = "WEB/SHE_PPT_8_5/sample_mdb-SC8.xml"
qualified_mdb_filename = find_file(mdb_filename)

for (det_specs, instrument) in ((tc.vis_det_specs, "VIS"), (tc.nisp_det_specs, "NISP")):

    # Use the default detector specs for now

    # Set up the points we want to test conversions for
    xp_min = 0
    xp_max = det_specs.detector_pixels_x - 1
    yp_min = 0
    yp_max = det_specs.detector_pixels_y - 1

    det_ix_min = 1
    det_ix_max = det_specs.ndet_x
    det_iy_min = 1
    det_iy_max = det_specs.ndet_x

    # Initialise a table to store results
    coord_table = Table(names=["XP", "YP", "DET_X", "DET_Y", "FOV_X", "FOV_Y"])

    # Calculate for each corner of each detector
    for det_ix in np.linspace(det_ix_min, det_ix_max, (det_ix_max - det_ix_min + 1), endpoint=True, dtype=int):
        for det_iy in np.linspace(det_iy_min, det_iy_max, (det_iy_max - det_iy_min + 1), endpoint=True, dtype=int):
            for xp in (xp_min, xp_max):
                for yp in (yp_min, yp_max):
                    # Calculate the coords
                    fov_x, fov_y = tc.get_fov_coords_from_detector(det_xp=xp,
                                                                   det_yp=yp,
                                                                   det_ix=det_ix,
                                                                   det_iy=det_iy,
                                                                   instrument=instrument)
                    # Store it in the table
                    coord_table.add_row({"XP": xp,
                                         "YP": yp,
                                         "DET_X": det_ix,
                                         "DET_Y": det_iy,
                                         "FOV_X": fov_x,
                                         "FOV_Y": fov_y})

    # Save the table
    coord_table.write(instrument + "_coords.fits", overwrite=True)
