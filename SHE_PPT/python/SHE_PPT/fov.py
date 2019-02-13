"""
File: fov.py

Created on: 13 Feb, 2019
"""

__updated__ = "2019-02-13"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from ElementsKernel.Logging import getLogger
from MdbUtils.Mdb import Mdb

# We'll store telescope details in a module-level object which can be updated from the MDB

class VisDetectorSpecs(object):
    
    def __init__(self):
            
        # gap in um between adjacent detectors in the horizontal direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dy = 1468
        
        # gap in um between adjacent detectors in the vertical direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dy = 7528

        self.detector_pixels_x = 4096  # number of pixel columns per detector
        self.detector_pixels_y = 4136  # number of pixel rows per detector

        self.detector_activepixels_x = 4096  # number of active pixel columns per detector
        self.detector_activepixels_y = 4132  # number of active pixel rows per detector

        self.pixelsize_um = 12  # edge length of a pixel in micrometres
        
        self.calc_specs()
        
        return
    
    def calc_specs(self):
        
        # Details about charge injection inactive pixels
        self.ci_pixels = self.detector_pixels_y - self.detector_activepixels_y
        self.ci_split_point = self.detector_activepixels_y // 2

        # gap between detector pixel areas
        self.det_dx = self.detector_pixels_x * self.pixelsize_um + self.gap_dx
        self.det_dy = self.detector_pixels_y * self.pixelsize_um + self.gap_dy
        
vis_det_specs = VisDetectorSpecs()
        
def load_vis_detector_specs(mdb_dict=None, mdb_files=None, path=None):
    """Loads and updates specifications for the VIS detectors from an MDB file

    Arguments
    ---------
    mdb_files: string or list of strings
        MDB filename(s)
    path: string
        Location of mdb files. If None, will assume filenames are fully-qualified

    Return
    ------
    None

    """

    logger = getLogger(__name__ + "[" + str(os.getpid()) + "]")
    
    if mdb_dict is not None:
        # Check it's in the correct format
        if not isinstance(mdb_dict, dict):
            raise TypeError("mdb_dict must be a dictionary")
        # Check for a required value
        if not "SpaceSegment.Instrument.VIS.VISCCDGapLongDimensionNominalImage" in mdb_dict:
            raise ValueError("mdb_dict doesn't have required values")
    else:
        # Resolve the filename (or list of files) to find their qualified paths, and load the mdb_dict
        if isinstance(mdb_files, str):
            if path is None:
                qualified_mdb_files = mdb_files
            else:
                qualified_mdb_files = os.path.join(path,mdb_files)
        elif isinstance(mdb_files, list) or isinstance(object, tuple):
            qualified_mdb_files = []
            for mdb_file in mdb_files:
                if path is None:
                    qualified_mdb_file = mdb_file
                else:
                    qualified_mdb_file = os.path.join(path,mdb_file)
                qualified_mdb_files.append(qualified_mdb_file)
        elif mdb_files is None:
            raise ValueError("No MDB file specified for load_vis_detector_specs. Either an MDB dictionary or filename " +
                             "must be specified.")
        else:
            raise TypeError("Invalid type for mdb_files object passed to SHE_PPT.mdb.init(): " + str(mdb_files))
    
        # Get and store the data in a dictionary
        logger.debug("Attempting to load MDB from " + str(qualified_mdb_files))
        mdb_dict = Mdb(qualified_mdb_files).get_all()
        
    # Update values from the MDB now
    
    vis_det_specs.gap_dx = 1000*mdb_dict["SpaceSegment.Instrument.VIS.VISCCDGapShortDimensionNominalImage"]['Value']
    vis_det_specs.gap_dy = 1000*mdb_dict["SpaceSegment.Instrument.VIS.VISCCDGapLongDimensionNominalImage"]['Value']

    # Get the number of total and active pixels per detector
    # Note that in the x dimension, active = total
    vis_det_specs.detector_pixels_x = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelShortDimensionFormat"]['Value']
    vis_det_specs.detector_pixels_y = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorPixelLongDimensionFormat"]['Value']
    vis_det_specs.detector_activepixels_x = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelShortDimensionFormat"]['Value']
    vis_det_specs.detector_activepixels_y = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelLongDimensionFormat"]['Value']

    # edge length of a pixel in micrometres
    vis_det_specs.pixelsize_um = mdb_dict["SpaceSegment.Instrument.VIS.VISAveragePixelSizemicron"]['Value']  

    vis_det_specs.calc_specs()

    return

