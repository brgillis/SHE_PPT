""" @file full_mdb.py

    Created 15 Feb 2018

    Functions to get needed information from the MDB.
"""

__updated__ = "2021-08-13"

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

import os
import re

from astropy.io import fits

from EL_PythonUtils.utilities import run_only_once
from ST_DM_MDBTools.Mdb import Mdb
from .constants.fits import EXTNAME_LABEL
from .constants.test_data import MDB_PRODUCT_FILENAME, TEST_DATA_LOCATION
from .file_io import find_file
from .logging import getLogger
from .utility import coerce_to_list

_mdb_not_inited_exception = RuntimeError(
    "mdb module must be initialised with MDB xml object before use.")

full_mdb = {}

_gain_dict = {}
_gain_ave_dict = {}
_read_noise_dict = {}
_read_noise_ave_dict = {}

DEFAULT_MDB_FILE = os.path.join("WEB", TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME)

logger = getLogger(__name__)


def init(mdb_files=None, path=None):
    """Initialises module by loading MDB data from file(s).

    Arguments
    ---------
    mdb_files: string or list of strings
        MDB filename(s)

    Return
    ------
    None

    """

    # Resolve the filename (or list of files) to find their qualified paths
    if isinstance(mdb_files, str):
        qualified_mdb_files = find_file(mdb_files, path)
    elif isinstance(mdb_files, list) or isinstance(object, tuple):
        qualified_mdb_files = []
        for mdb_file in mdb_files:
            qualified_mdb_file = find_file(mdb_file, path)
            qualified_mdb_files.append(qualified_mdb_file)
    elif mdb_files is None:
        qualified_mdb_files = find_file(DEFAULT_MDB_FILE)
        logger.warning("No MDB file specified. Using default file at %s", qualified_mdb_files)
    else:
        raise TypeError("Invalid type for mdb_files object passed to SHE_PPT.mdb.init(): " + str(mdb_files))

    # Get and store the data in a dictionary
    full_dict = Mdb(qualified_mdb_files).get_all()
    full_mdb.clear()
    full_mdb.update(full_dict)

    # Load the gain table
    gain_filenames = get_mdb_value(mdb_keys.vis_gain_coeffs)
    qualified_gain_filenames = _find_mdb_data_file(gain_filenames, qualified_mdb_files)
    _gain_dict.clear()
    for qualified_gain_filename in qualified_gain_filenames:
        _gain_dict.update(_load_quadrant_table(qualified_gain_filename, 'GAIN'))

    # Load the read_noise table
    read_noise_filenames = get_mdb_value(mdb_keys.vis_readout_noise_table)
    qualified_read_noise_filenames = _find_mdb_data_file(read_noise_filenames, qualified_mdb_files)
    _read_noise_dict.clear()
    for qualified_read_noise_filename in qualified_read_noise_filenames:
        _read_noise_dict.update(_load_quadrant_table(qualified_read_noise_filename, 'RON_ELE'))


def _find_mdb_data_file(data_filenames, qualified_mdb_files):
    qualified_mdb_files = coerce_to_list(qualified_mdb_files)

    qualified_data_filenames = []

    for data_filename in data_filenames:

        qualified_data_filename = None

        # Look relative to each MDB file
        for qualified_mdb_filename in qualified_mdb_files:

            mdb_path = os.path.split(qualified_mdb_filename)[0]

            test_mdb_file_paths = [mdb_path, os.path.join(mdb_path, "data"),
                                   os.path.join(mdb_path, ".."), os.path.join(mdb_path, "..", "data"), ]

            found = False

            # Try in the same directory as the MDB file
            for test_path in test_mdb_file_paths:
                test_qualified_data_filename = os.path.join(test_path, data_filename)
                if os.path.isfile(test_qualified_data_filename):
                    qualified_data_filename = test_qualified_data_filename
                    found = True
                    break

            if found:
                break

        if qualified_data_filename is None:
            raise RuntimeError("MDB data file " + data_filename + " cannot be found. " +
                               "Make sure it's in the data subdirectory of where the MDB file is.")

        qualified_data_filenames.append(qualified_data_filename)

    return qualified_data_filenames


def _load_quadrant_table(qualified_data_filename, colname):
    f = fits.open(qualified_data_filename, mode='readonly')

    quadrant_dict = {}

    for hdu in f:
        # Check if this is the zeroeth hdu, which doesn't have a table in it
        if EXTNAME_LABEL not in hdu.header:
            continue

        quadrant_dict[hdu.header[EXTNAME_LABEL]] = hdu.data[colname][0]

    f.close()

    return quadrant_dict


def get_gain(detector=None, quadrant=None, suppress_warnings=False):
    return _get_quadrant_data(dictionary=_gain_dict,
                              ave_dict=_gain_ave_dict,
                              detector=detector,
                              quadrant=quadrant,
                              suppress_warnings=suppress_warnings)


def get_read_noise(detector=None, quadrant=None, suppress_warnings=False):
    return _get_quadrant_data(dictionary=_read_noise_dict,
                              ave_dict=_read_noise_ave_dict,
                              detector=detector,
                              quadrant=quadrant,
                              suppress_warnings=suppress_warnings)


@run_only_once
def warn_missing_detector():
    logger.warning("No detector value supplied to get_gain or get_read_noise - average value will be used instead.")


@run_only_once
def warn_missing_quadrant():
    logger.warning("No quadrant value supplied to get_gain or get_read_noise - average value will be used instead.")


def _get_quadrant_data(dictionary, ave_dict, detector=None, quadrant=None, suppress_warnings=False):
    # If we have both the detector and quadrant, get the value for that quadrant
    if detector is not None and quadrant is not None:
        return dictionary[detector + "." + quadrant]

    # We're missing some info, so warn and average the possibly-matching data
    if detector is None:
        if not suppress_warnings:
            warn_missing_detector()
        det_regex = r"[1-6]\-[1-6]"
    else:
        det_regex = detector.replace("-", r"\-")

    if quadrant is None:
        if not suppress_warnings:
            warn_missing_quadrant()
        quad_regex = "[E-H]"
    else:
        quad_regex = quadrant

    regex = det_regex + "." + quad_regex

    if regex in ave_dict:
        return ave_dict[regex]

    summation = 0
    count = 0

    for key in dictionary.keys():
        if re.match(regex, key) is None:
            continue
        summation += dictionary[key]
        count += 1

    if count == 0:
        raise RuntimeError("No matching detectors and/or quadrants found for input: detector = " + str(detector) +
                           ", quadrant = " + str(quadrant) + ".")

    # Save and return the average
    average = summation / count
    ave_dict[regex] = average
    return average


def reset():
    """Resets the MDB dictionary.

    Arguments
    ---------
    None

    Return
    ------
    None
    """

    full_mdb.clear()


def get_mdb_value(key):
    """Gets an item's value from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    value: (type dependent on key)

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['Value']


def get_mdb_description(key):
    """Gets an item's description from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    description: str

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['Description']


def get_mdb_source(key):
    """Gets an item's source from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    source: str

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['Source']


def get_mdb_release(key):
    """Gets an item's release version from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    release: str

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['Release']


def get_mdb_expression(key):
    """Gets an item's expression from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    expression: str

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['Expression']


def get_mdb_unit(key):
    """Gets an item's unit from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    unit: str

    """

    if len(full_mdb) == 0:
        raise _mdb_not_inited_exception

    return full_mdb[key]['unit']


# MDB keys stored as attributes of the mdb_keys object


class MDBKeys():

    def __init__(self):
        # Environmental constants

        self.velocity_of_light_constant_vacuum = "Environment.Constant.VelocityOfLightConstantVacuum"
        self.astronomical_unit_2_meter = "Environment.Constant.AstronomicalUnit2Meter"
        self.day_2_second = "Environment.Constant.Day2Second"
        self.degree_2_radian = "Environment.Constant.Degree2Radian"

        # SpaceSegment.PLM

        self.telescope_vis_fov_centre_xsc_nominal = "SpaceSegment.PLM.TelescopeVISFoVCentreXscNominal"
        self.telescope_vis_fov_centre_ysc_nominal = "SpaceSegment.PLM.TelescopeVISFoVCentreYscNominal"
        self.telescope_vis_fov_xsc = "SpaceSegment.PLM.TelescopeVISFOVXsc"
        self.telescope_vis_fov_ysc = "SpaceSegment.PLM.TelescopeVISFOVYsc"
        self.telescope_vis_local_focal_length_centre = "SpaceSegment.PLM.TelescopeVISLocalFocalLengthCentre"
        self.telescope_vis_paraxial_focal_ratio = "SpaceSegment.PLM.TelescopeVISParaxialFocalRatio"
        self.telescope_vis_platescale = "SpaceSegment.PLM.TelescopeVISPlatescale"
        self.telescope_vis_psf_ellipticity = "SpaceSegment.PLM.TelescopeVISPSFEllipticity"
        self.telescope_vis_psf_ellipticity_stability = "SpaceSegment.PLM.TelescopeVISPSFEllipticityStability"
        self.telescope_vis_psf_fwhm = "SpaceSegment.PLM.TelescopeVISPSFFWHM"
        self.telescope_vis_psf_lambda_parameter_alpha = "SpaceSegment.PLM.TelescopeVISPSFLambdaParameterAlpha"
        self.telescope_vis_psf_r2 = "SpaceSegment.PLM.TelescopeVISPSFR2"
        self.telescope_vis_psf_r2_stability = "SpaceSegment.PLM.TelescopeVISPSFR2Stability"

        #   SpaceSegment.SVM

        self.dither_step_angular_error = "SpaceSegment.SVM.DitherStepAngularError"
        self.dither_step_angular_minimum = "SpaceSegment.SVM.DitherStepAngularMinimum"
        self.max_field_2_field_overlap = "SpaceSegment.SVM.MaxField2FieldOverlap"
        self.min_field_2_field_overlap = "SpaceSegment.SVM.MinField2FieldOverlap"
        self.nominal_science_observation_sequence_duration = "SpaceSegment.SVM.MinField2FieldOverlap"

        # SpaceSegment.Instrument.VIS

        self.shutter_closing_duration = "SpaceSegment.Instrument.VIS.ShutterClosingDuration"
        self.shutter_opening_duration = "SpaceSegment.Instrument.VIS.ShutterOpeningDuration"
        self.vis_adc_dynamics = "SpaceSegment.Instrument.VIS.VISADCDynamics"
        self.cu_uniformity_map_normalised = "SpaceSegment.Instrument.VIS.CUUniformityMapNormalised"
        self.vis_average_pixel_sizemicron = "SpaceSegment.Instrument.VIS.VISAveragePixelSizemicron"
        self.vis_ccd_charge_injection = "SpaceSegment.Instrument.VIS.VISCCDChargeInjection"
        self.vis_ccd_column = "SpaceSegment.Instrument.VIS.VISCCDColumn"
        self.vis_ccd_defects_column_eol = "SpaceSegment.Instrument.VIS.VISCCDDefectsColumnEOL"
        self.vis_ccd_defects_total_spots_eol = "SpaceSegment.Instrument.VIS.VISCCDDefectsTotalSpotsEOL"
        self.vis_ccd_defects_traps_eol = "SpaceSegment.Instrument.VIS.VISCCDDefectsTrapsEOL"
        self.vis_ccd_defects_white_spots_bol = "SpaceSegment.Instrument.VIS.VISCCDDefectsWhiteSpotsBOL"
        self.vis_ccd_defects_white_spots_eol = "SpaceSegment.Instrument.VIS.VISCCDDefectsWhiteSpotsEOL"
        self.vis_ccd_gap_long_dimension_nominal_image = "SpaceSegment.Instrument.VIS.VISCCDGapLongDimensionNominalImage"
        self.vis_ccd_gap_short_dimension_nominal_image = \
            "SpaceSegment.Instrument.VIS.VISCCDGapShortDimensionNominalImage"
        self.vis_ccd_number = "SpaceSegment.Instrument.VIS.VISCCDNumber"
        self.vis_ccd_quadrant_list = "SpaceSegment.Instrument.VIS.VISCCDQuadrantList"
        self.vis_ccd_row = "SpaceSegment.Instrument.VIS.VISCCDRow"
        self.vis_dark_current = "SpaceSegment.Instrument.VIS.VISDarkCurrent"
        self.vis_data_compression = "SpaceSegment.Instrument.VIS.VISDataCompression"
        self.vis_detector_active_pixel_long_dimension_format = \
            "SpaceSegment.Instrument.VIS.VISDetectorActivePixelLongDimensionFormat"
        self.vis_detector_active_pixel_short_dimension_format = \
            "SpaceSegment.Instrument.VIS.VISDetectorActivePixelShortDimensionFormat"
        self.vis_detector_overscanx = "SpaceSegment.Instrument.VIS.VISDetectorOverscanx"
        self.vis_detector_pixel_long_dimension_format = \
            "SpaceSegment.Instrument.VIS.VISDetectorPixelLongDimensionFormat"
        self.vis_detector_prescanx = "SpaceSegment.Instrument.VIS.VISDetectorPrescanx"
        self.vis_exposure_time = "SpaceSegment.Instrument.VIS.VISExposureTime"
        self.vis_exposure_time_knowledge_error = "SpaceSegment.Instrument.VIS.VISExposureTimeKnowledgeError"
        self.vis_focal_plane_assembly_long_dimension_max_image = \
            "SpaceSegment.Instrument.VIS.VISFocalPlaneAssemblyLongDimensionMaxImage"
        self.vis_focal_plane_assembly_short_dimension_max_image = \
            "SpaceSegment.Instrument.VIS.VISFocalPlaneAssemblyShortDimensionMaxImage"
        self.vis_gain_coeffs = "SpaceSegment.Instrument.VIS.GainCoeffs"
        self.vis_readout_noise_table = "SpaceSegment.Instrument.VIS.ReadoutNoiseTable"
        self.vis_distortion_maps = "SpaceSegment.Instrument.VIS.VISDistortionMaps"
        self.cti_parallel_acs_mode = "SpaceSegment.Instrument.VIS.CTIParallelAcsMode"
        self.cti_parallel_clocking_mode = "SpaceSegment.Instrument.VIS.CTIParallelClockingMode"
        self.cti_parallel_express = "SpaceSegment.Instrument.VIS.CTIParallelExpress"
        self.cti_parallel_niterations = "SpaceSegment.Instrument.VIS.CTIParallelNIterations"
        self.cti_parallel_nlevels = "SpaceSegment.Instrument.VIS.CTIParallelNLevels"
        self.cti_parallel_nspecies = "SpaceSegment.Instrument.VIS.CTIParallelNSpecies"
        self.cti_parallel_read_out_offset = "SpaceSegment.Instrument.VIS.CTIParallelReadOutOffset"
        self.cti_parallel_trap_density = "SpaceSegment.Instrument.VIS.CTIParallelTrapDensity"
        self.cti_parallel_trap_life_time = "SpaceSegment.Instrument.VIS.CTIParallelTrapLifeTime"
        self.cti_parallel_well_depth = "SpaceSegment.Instrument.VIS.CTIParallelWellDepth"
        self.cti_parallel_well_fill_power = "SpaceSegment.Instrument.VIS.CTIParallelWellFillPower"
        self.cti_parallel_well_notch_depth = "SpaceSegment.Instrument.VIS.CTIParallelWellNotchDepth"
        self.cti_serial_acs_mode = "SpaceSegment.Instrument.VIS.CTISerialAcsMode"
        self.cti_serial_clocking_mode = "SpaceSegment.Instrument.VIS.CTISerialClockingMode"
        self.cti_serial_express = "SpaceSegment.Instrument.VIS.CTISerialExpress"
        self.cti_serial_niterations = "SpaceSegment.Instrument.VIS.CTISerialNIterations"
        self.cti_serial_nlevels = "SpaceSegment.Instrument.VIS.CTISerialNLevels"
        self.cti_serial_nspecies = "SpaceSegment.Instrument.VIS.CTISerialNSpecies"
        self.cti_serial_read_out_offset = "SpaceSegment.Instrument.VIS.CTISerialReadOutOffset"
        self.cti_serial_trap_density = "SpaceSegment.Instrument.VIS.CTISerialTrapDensity"
        self.cti_serial_trap_life_time = "SpaceSegment.Instrument.VIS.CTISerialTrapLifeTime"
        self.cti_serial_well_depth = "SpaceSegment.Instrument.VIS.CTISerialWellDepth"
        self.cti_serial_well_fill_power = "SpaceSegment.Instrument.VIS.CTISerialWellFillPower"
        self.cti_serial_well_notch_depth = "SpaceSegment.Instrument.VIS.CTISerialWellNotchDepth"
        self.fwhm_int_0 = "SpaceSegment.Instrument.VIS.FWHMInt0"
        self.fwhm_xa_int_1x = "SpaceSegment.Instrument.VIS.FWHMxaInt1x"
        self.fwhm_xa_lambda_1x = "SpaceSegment.Instrument.VIS.FWHMxalambda1x"
        self.fwhm_xb_int_1x = "SpaceSegment.Instrument.VIS.FWHMxbInt1x"
        self.fwhm_xb_lambda_1x = "SpaceSegment.Instrument.VIS.FWHMxblambda1x"
        self.fwhm_ya_int_1y = "SpaceSegment.Instrument.VIS.FWHMyaInt1y"
        self.fwhm_ya_lambda_1y = "SpaceSegment.Instrument.VIS.FWHMyalambda1y"
        self.fwhm_yb_int_1y = "SpaceSegment.Instrument.VIS.FWHMybInt1y"
        self.fwhm_yb_lambda_1y = "SpaceSegment.Instrument.VIS.FWHMyblambda1y"
        self.ghost_model = "SpaceSegment.Instrument.VIS.GhostModel"
        self.ghost_model_position_matrix_a = "SpaceSegment.Instrument.VIS.GhostModelPositionMatrixA"
        self.ghost_model_position_matrix_b = "SpaceSegment.Instrument.VIS.GhostModelPositionMatrixB"
        self.ghost_model_shift_x = "SpaceSegment.Instrument.VIS.GhostModelShiftX"
        self.ghost_model_shift_y = "SpaceSegment.Instrument.VIS.GhostModelShiftY"
        self.ghost_model_star_brightness = "SpaceSegment.Instrument.VIS.GhostModelStarBrightness"
        self.mean_detector_quantum_efficiency_cbenominal_bol = \
            "SpaceSegment.Instrument.VIS.MeanDetectorQuantumEfficiencyNominalBOL"
        self.mean_detector_quantum_efficiency_cbenominal_eol = \
            "SpaceSegment.Instrument.VIS.MeanDetectorQuantumEfficiencyNominalEOL"
        self.ccd_full_well_capacity_eol = "SpaceSegment.Instrument.VIS.CCDFullWellCapacityEOL"
        self.distortion_model = "SpaceSegment.Instrument.VIS.DistortionModel"
        self.vis_optics_aocspixel_detector_psf = "SpaceSegment.Instrument.VIS.VISOpticsAOCSPixelDetectorPSF"
        self.prnu = "SpaceSegment.Instrument.VIS.PRNU"


mdb_keys = MDBKeys()
