"""
File: telescope_coords.py

Created on: 13 Feb, 2019
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__updated__ = "2020-12-14"

import math
import os

from ElementsKernel.Logging import getLogger
from ST_DM_MDBTools.Mdb import Mdb
import numpy as np


# We'll store telescope details in module-level objects which can be updated from the MDB
class DetectorSpecs(object):

    def calc_specs(self):

        # Details about charge injection inactive pixels
        self.ci_pixels = self.detector_pixels_y - self.detector_activepixels_y
        self.ci_split_point = self.detector_activepixels_y // 2

        # gap between detector pixel areas
        self.det_dx = self.detector_pixels_x * self.pixelsize_um + self.gap_dx
        self.det_dy = self.detector_pixels_y * self.pixelsize_um + self.gap_dy

        # FOV scale
        self.fov_scale_deg_per_um = self.fov_scale_arcsec_per_pixel / 3600 / self.pixelsize_um

        return


class VisDetectorSpecs(DetectorSpecs):

    def __init__(self):

        # gap in um between adjacent detectors in the horizontal direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dx = 1468

        # gap in um between adjacent detectors in the vertical direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dy = 7528

        self.detector_pixels_x = 4096  # number of pixel columns per detector
        self.detector_pixels_y = 4136  # number of pixel rows per detector

        self.detector_activepixels_x = 4096  # number of active pixel columns per detector
        self.detector_activepixels_y = 4132  # number of active pixel rows per detector

        self.pixelsize_um = 12  # edge length of a pixel in micrometres

        # Number of detector columns in x and y dimensions
        self.ndet_x = 6
        self.ndet_y = 6

        # Field of view offsets
        self.fov_x_offset_deg = 0.822
        self.fov_y_offset_deg = 0.

        self.fov_scale_arcsec_per_pixel = 0.1

        self.calc_specs()

        return


class NispDetectorSpecs(DetectorSpecs):

    def __init__(self):

        # gap in um between adjacent detectors in the horizontal direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dx = 5939.5

        # gap in um between adjacent detectors in the vertical direction,
        # including inactive pixels from the detector's edges on both sides
        self.gap_dy = 11879

        self.detector_pixels_x = 2040  # number of pixel columns per detector
        self.detector_pixels_y = 2040  # number of pixel rows per detector

        self.detector_activepixels_x = 2040  # number of active pixel columns per detector
        self.detector_activepixels_y = 2040  # number of active pixel rows per detector

        self.pixelsize_um = 18  # edge length of a pixel in micrometres

        # Number of detector columns in x and y dimensions
        self.ndet_x = 4
        self.ndet_y = 4

        # Field of view offsets - Note that these aren't in the MDB at present, so have to be changed
        # manually.
        self.fov_x_offset_deg = 0.
        self.fov_y_offset_deg = 0.

        self.fov_scale_arcsec_per_pixel = 0.15

        self.calc_specs()

        return


vis_det_specs = VisDetectorSpecs()
nisp_det_specs = NispDetectorSpecs()


def _resolve_mdb_dict(mdb_dict=None,
                      mdb_files=None,
                      path=None):
    """ Resolves the MDB dictionary to use from input arguments

        Arguments
        ---------
        mdb_dict: dict
            MDB dictionary
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
                qualified_mdb_files = os.path.join(path, mdb_files)
        elif isinstance(mdb_files, list) or isinstance(object, tuple):
            qualified_mdb_files = []
            for mdb_file in mdb_files:
                if path is None:
                    qualified_mdb_file = mdb_file
                else:
                    qualified_mdb_file = os.path.join(path, mdb_file)
                qualified_mdb_files.append(qualified_mdb_file)
        elif mdb_files is None:
            raise ValueError("No MDB file specified for load_vis_detector_specs. Either an MDB dictionary or filename " +
                             "must be specified.")
        else:
            raise TypeError("Invalid type for mdb_files object passed to SHE_PPT.mdb.init(): " + str(mdb_files))

        # Get and store the data in a dictionary
        logger.debug("Attempting to load MDB from " + str(qualified_mdb_files))
        mdb_dict = Mdb(qualified_mdb_files).get_all()

    return mdb_dict


def load_vis_detector_specs(mdb_dict=None,
                            mdb_files=None,
                            path=None):
    """ Loads and updates specifications for the VIS detectors from an MDB file

        Arguments
        ---------
        mdb_dict: dict
            MDB dictionary
        mdb_files: string or list of strings
            MDB filename(s)
        path: string
            Location of mdb files. If None, will assume filenames are fully-qualified

        Return
        ------
        None

    """

    mdb_dict = _resolve_mdb_dict(mdb_dict, mdb_files, path)

    # Update values from the MDB now

    vis_det_specs.gap_dx = 1000 * mdb_dict["SpaceSegment.Instrument.VIS.VISCCDGapShortDimensionNominalImage"]['Value']
    vis_det_specs.gap_dy = 1000 * mdb_dict["SpaceSegment.Instrument.VIS.VISCCDGapLongDimensionNominalImage"]['Value']

    # Get the number of total and active pixels per detector
    # Note that in the x dimension, active = total
    vis_det_specs.detector_pixels_x = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelShortDimensionFormat"]['Value']
    vis_det_specs.detector_pixels_y = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorPixelLongDimensionFormat"]['Value']
    vis_det_specs.detector_activepixels_x = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelShortDimensionFormat"]['Value']
    vis_det_specs.detector_activepixels_y = mdb_dict["SpaceSegment.Instrument.VIS.VISDetectorActivePixelLongDimensionFormat"]['Value']

    # Number of detector columns in x and y dimensions
    ndet = int(mdb_dict["SpaceSegment.Instrument.VIS.VISCCDNumber"]['Value'])
    vis_det_specs.ndet_x = int(math.sqrt(ndet))
    vis_det_specs.ndet_y = vis_det_specs.ndet_x

    assert vis_det_specs.ndet_x * vis_det_specs.ndet_y == ndet

    # FOV offset
    vis_det_specs.fov_x_offset_deg = mdb_dict["SpaceSegment.PLM.TelescopeVISFoVCentreXscNominal"]['Value']
    vis_det_specs.fov_y_offset_deg = mdb_dict["SpaceSegment.PLM.TelescopeVISFoVCentreYscNominal"]['Value']

    # edge length of a pixel in micrometres
    vis_det_specs.pixelsize_um = mdb_dict["SpaceSegment.Instrument.VIS.VISAveragePixelSizemicron"]['Value']

    vis_det_specs.calc_specs()

    return


def load_nisp_detector_specs(mdb_dict=None,
                             mdb_files=None,
                             path=None):
    """ Loads and updates specifications for the NISP detectors from an MDB file

        Arguments
        ---------
        mdb_dict: dict
            MDB dictionary
        mdb_files: string or list of strings
            MDB filename(s)
        path: string
            Location of mdb files. If None, will assume filenames are fully-qualified

        Return
        ------
        None

    """

    mdb_dict = _resolve_mdb_dict(mdb_dict, mdb_files, path)

    # Update values from the MDB now

    nisp_det_specs.gap_dx = 1000 * \
        mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorGapShortDimensionNominalObject"]['Value']
    nisp_det_specs.gap_dy = 1000 * \
        mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorGapLongDimensionNominalObject"]['Value']

    # Get the number of total and active pixels per detector
    # Note that in the x dimension, active = total
    nisp_det_specs.detector_pixels_x = mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorPixelShortDimensionFormat"]['Value']
    nisp_det_specs.detector_pixels_y = mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorPixelLongDimensionFormat"]['Value']

    # Note - no entry for NISP active pixels in MDB at present
    nisp_det_specs.detector_activepixels_x = mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorPixelShortDimensionFormat"]['Value']
    nisp_det_specs.detector_activepixels_y = mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorPixelLongDimensionFormat"]['Value']

    # Number of detector columns in x and y dimensions
    ndet = int(mdb_dict["SpaceSegment.Instrument.NISP.NISPDetectorNumber"]['Value'])
    nisp_det_specs.ndet_x = int(math.sqrt(ndet))
    nisp_det_specs.ndet_y = nisp_det_specs.ndet_x

    assert nisp_det_specs.ndet_x * nisp_det_specs.ndet_y == ndet

    # NISP FOV offset not in the MDB at present
    # nisp_det_specs.fov_x_offset_deg = mdb_dict["SpaceSegment.PLM.TelescopeNISPFOVCentreXscNominal"]['Value']
    # nisp_det_specs.fov_y_offset_deg = mdb_dict["SpaceSegment.PLM.TelescopeNISPFOVCentreYscNominal"]['Value']

    # edge length of a pixel in micrometres
    nisp_det_specs.pixelsize_um = mdb_dict["SpaceSegment.Instrument.NISP.NISPAveragePixelSize"]['Value']

    nisp_det_specs.calc_specs()

    return


def get_focal_plane_coords_from_detector(det_xp,
                                         det_yp,
                                         det_ix,
                                         det_iy,
                                         instrument="VIS",
                                         detector_orientation=0):
    """ Convert VIS detector pixel co-ordinates to focal_plane co-ordinates.

        Parameters
        ----------
        det_xp : float
            x pixel co-ordinate in the detector frame. Not enforced to actually be on the detector
        det_yp : float
            y pixel co-ordinate in the detector frame. Not enforced to actually be on the detector
        det_ix : int
            x index of the detector's position
        det_iy : int
            y index of the detector's position
        instrument : str
            Which instrument to calculate for - either "VIS" or "NISP"
        detector_orientation : float
            Orientation of the detector relative to the field-of-view in radians. Default=0

        Return
        ------
        foc_x, foc_y : float, float
            VIS focal plane co-ordinates in um



    """

    if instrument == "VIS":
        det_specs = vis_det_specs
    elif instrument == "NISP":
        det_specs = nisp_det_specs
    else:
        raise ValueError("Invalid instrument value: " + str(instrument) + ". Allowed values are \"VIS\" and \"NISP\"")

    # Check for valid det_ix and det_iy
    det_range_x = np.add(1, range(det_specs.ndet_x))
    det_range_y = np.add(1, range(det_specs.ndet_y))
    if det_ix not in det_range_x or det_iy not in det_range_y:
        raise ValueError("det_ix and det_iy must be in " + str(det_range_x) + " and " + str(det_range_y) + ".")

    offset_x = -0.5 * (det_specs.ndet_x * det_specs.det_dx - det_specs.gap_dx) + (det_ix - 1) * det_specs.det_dx
    offset_y = -0.5 * (det_specs.ndet_y * det_specs.det_dy - det_specs.gap_dy) + (det_iy - 1) * det_specs.det_dy

    # Get pixel distances relative to centre of the detector
    xpc = det_xp - det_specs.detector_pixels_x / 2
    ypc = det_yp - det_specs.detector_pixels_y / 2

    # Get cos and sin of orientation angle
    cos_o = math.cos(detector_orientation)
    sin_o = math.sin(detector_orientation)

    # Get positions on the focal plane
    # @TODO: IF VIS revert, x,y? and careful about sign.
    # How do we test this?????
    # Are there some numbers???
    foc_x = offset_x + det_specs.pixelsize_um * (det_specs.detector_pixels_x / 2 + cos_o * xpc - sin_o * ypc)
    foc_y = offset_y + det_specs.pixelsize_um * (det_specs.detector_pixels_y / 2 + sin_o * xpc + cos_o * ypc)

    return foc_x, foc_y


def get_fov_coords_from_focal_plane(foc_x,
                                    foc_y,
                                    instrument="VIS",):
    """ Convert detector pixel co-ordinates to field-of-view co-ordinates.

        Parameters
        ----------
        foc_x : float
            Focal plane x co-ordinate in um
        foc_y : float
            Focal plane y co-ordinate in um
        instrument : str
            Which instrument to calculate for - either "VIS" or "NISP"

        Return
        ------
        fov_x, fov_y : float, float
            Field-of-view co-ordinates in degrees


        @fixme:
        ISSUE 56: ??
        I've started reading it and it lacks a function, which would be called
"get_detector_coords_from_focal_plane()" using your naming convention, and
I've started writing it, but I miss some details on the VIS reference frames
you're using. There is the detector frame in pixels, the focal plane frame in
micrometres (which I assume is centered on the center of the focal plane), and
the field of view frame, in degrees, which origin is offset from the focal
plane center by -0.822 degrees along the X axis.

         My concern is that usually the VIS FOV frame has its Y axis along the X FPA
axis, and the FOV X axis is along -Y FPA, and I don't see this transformation
in your "get_fov_coords_from_focal_plane()" function.

        I don't think that's correct, unfortunately. The rotation is between the focal plane and the FoV, while the orientation parameter rotates between the focal plane and the detectors. It might appear to solve our problem, but would get us into trouble later when the focal plane to FoV conversion is made more accurate
    """

    # Convert from position on the focal plane to the field-of-view

    if instrument == "VIS":
        det_specs = vis_det_specs

        # ? rotate before or after offset..
        # Try rotate before, i.e.

        # @NOTE: MDB has fov_x and fov_y the incorrect way around.
        fov_y = det_specs.fov_x_offset_deg + det_specs.fov_scale_deg_per_um * foc_y
        fov_x = det_specs.fov_y_offset_deg - det_specs.fov_scale_deg_per_um * foc_x

    elif instrument == "NISP":
        det_specs = nisp_det_specs

        fov_x = det_specs.fov_x_offset_deg + det_specs.fov_scale_deg_per_um * foc_x
        fov_y = det_specs.fov_y_offset_deg + det_specs.fov_scale_deg_per_um * foc_y

    else:
        raise ValueError("Invalid instrument value: " + str(instrument) + ". Allowed values are \"VIS\" and \"NISP\"")

    return fov_x, fov_y


def get_fov_coords_from_detector(det_xp,
                                 det_yp,
                                 det_ix,
                                 det_iy,
                                 instrument="VIS",
                                 detector_orientation=0):
    """ Convert detector pixel co-ordinates to field-of-view co-ordinates.

        Parameters
        ----------
        det_xp : float
            x pixel co-ordinate in the detector frame. Not enforced to actually be on the detector
        det_yp : float
            y pixel co-ordinate in the detector frame. Not enforced to actually be on the detector
        det_ix : int
            x index of the detector's position. Must be between 1 and 6
        det_iy : int
            y index of the detector's position. Must be between 1 and 6
        instrument : str
            Which instrument to calculate for - either "VIS" or "NISP"
        detector_orientation : float
            Orientation of the detector relative to the field-of-view in radians. Default=0



        Return
        ------
        fov_x, fov_y : float, float
            Field-of-view co-ordinates in degrees
    """

    foc_x, foc_y = get_focal_plane_coords_from_detector(det_xp=det_xp,
                                                        det_yp=det_yp,
                                                        det_ix=det_ix,
                                                        det_iy=det_iy,
                                                        instrument=instrument,
                                                        detector_orientation=detector_orientation)

    fov_x, fov_y = get_fov_coords_from_focal_plane(foc_x=foc_x,
                                                   foc_y=foc_y,
                                                   instrument=instrument,)

    return fov_x, fov_y


# Quadrant layout - note that due to column/row-major flip and the visual layout starting from bottom-left, this is transposed
# and flipped vertically compared to how the layout actually looks


quadrant_layout_123 = [["E", "H"],
                       ["F", "G"]]
quadrant_layout_456 = [["G", "F"],
                       ["H", "E"]]

quad_x_size = 2119
quad_y_size = 2066


def get_quadrant(x_pix: float,
                 y_pix: float,
                 det_iy: int):
    """ Get the letter signifying the quadrant of a detector where a pixel coordinate is. Returns "X" if the position
        is outside of the detector bounds.

        This uses the charts at http://euclid.esac.esa.int/dm/dpdd/latest/le1dpd/dpcards/le1_visrawframe.html for its
        logic.
    """

    if det_iy <= 3:
        quadrant_layout = quadrant_layout_123
    else:
        quadrant_layout = quadrant_layout_456

    quad_ix = int(x_pix / quad_x_size)
    quad_iy = int(y_pix / quad_y_size)

    if quad_ix in (0, 1) and quad_iy in (0, 1):
        quadrant = quadrant_layout[quad_ix, quad_iy]
    else:
        quadrant = "X"

    return quadrant
