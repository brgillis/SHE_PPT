""" @file full_mdb.py

    Created 15 Feb 2018

    Functions to get needed information from the MDB.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from MdbUtils.Mdb import Mdb as _Mdb

from SHE_PPT.file_io import find_file

_not_inited_exception = RuntimeError(
    "mdb module must be initialised with MDB xml object before use.")

full_mdb = {}


def init(mdb_files, path=None):
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

    # Get and store the data in a dictionary
    full_dict = _Mdb(qualified_mdb_files).get_all()
    full_mdb.clear()
    full_mdb.update(full_dict)

    return


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
        raise _not_inited_exception

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
        raise _not_inited_exception

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
        raise _not_inited_exception

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
        raise _not_inited_exception

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
        raise _not_inited_exception

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
        raise _not_inited_exception

    return full_mdb[key]['unit']


# MDB keys stored as attributes of the mdb_keys object

class MDBKeys(object):

    def __init__(self):

        # Environmental constants

        self.velocity_of_light_constant_vacuum = "Environment.Constant.VelocityOfLightConstantVacuum"
        self.astronomical_unit_2_meter = "Environment.Constant.AstronomicalUnit2Meter"
        self.day_2_second = "Environment.Constant.Day2Second"
        self.degree_2_radian = "Environment.Constant.Degree2Radian"

        # SpaceSegment.PLM

        self.telescope_vis_fov_centre_xsc_nominal = "TelescopeVISFoVCentreXscNominal"
        self.telescope_vis_fov_centre_ysc_nominal = "TelescopeVISFoVCentreYscNominal"
        self.telescope_vis_fov_xsc = "TelescopeVISFOVXsc"
        self.telescope_vis_fov_ysc = "TelescopeVISFOVYsc"
        self.telescope_vis_local_focal_length_centre = "TelescopeVISLocalFocalLengthCentre"
        self.telescope_vis_paraxial_focal_ratio = "TelescopeVISParaxialFocalRatio"
        self.telescope_vis_platescale = "TelescopeVISPlatescale"
        self.telescope_vis_psf_ellipticity = "TelescopeVISPSFEllipticity"
        self.telescope_vis_psf_ellipticity_stability = "TelescopeVISPSFEllipticityStability"
        self.telescope_vis_psf_fwhm = "TelescopeVISPSFFWHM"
        self.telescope_vis_psf_lambda_parameter_alpha = "TelescopeVISPSFLambdaParameterAlpha"
        self.telescope_vis_psf_r2 = "TelescopeVISPSFR2"
        self.telescope_vis_psf_r2_stability = "TelescopeVISPSFR2Stability"

        #   SpaceSegment.SVM

        self.dither_step_angular_error = "DitherStepAngularError"
        self.dither_step_angular_minimum = "DitherStepAngularMinimum"
        self.max_field_2_field_overlap = "MaxField2FieldOverlap"
        self.min_field_2_field_overlap = "MinField2FieldOverlap"
        self.nominal_science_observation_sequence_duration = "MinField2FieldOverlap"

        # SpaceSegment.Instrument.VIS

        self.shutter_closing_duration = "ShutterClosingDuration"
        self.shutter_opening_duration = "ShutterOpeningDuration"
        self.vis_adc_dynamics = "VISADCDynamics"
        self.cu_uniformity_map_normalised = "CUUniformityMapNormalised"
        self.vis_average_pixel_sizemicron = "VISAveragePixelSizemicron"
        self.vis_ccd_charge_injection = "VISCCDChargeInjection"
        self.vis_ccd_column = "VISCCDColumn"
        self.vis_ccd_defects_column_eol = "VISCCDDefectsColumnEOL"
        self.vis_ccd_defects_total_spots_eol = "VISCCDDefectsTotalSpotsEOL"
        self.vis_ccd_defects_traps_eol = "VISCCDDefectsTrapsEOL"
        self.vis_ccd_defects_white_spots_bol = "VISCCDDefectsWhiteSpotsBOL"
        self.vis_ccd_defects_white_spots_eol = "VISCCDDefectsWhiteSpotsEOL"
        self.vis_ccd_gap_long_dimension_nominal_image = "VISCCDGapLongDimensionNominalImage"
        self.vis_ccd_gap_short_dimension_nominal_image = "VISCCDGapShortDimensionNominalImage"
        self.vis_ccd_number = "VISCCDNumber"
        self.vis_ccd_quadrant_list = "VISCCDQuadrantList"
        self.vis_ccd_row = "VISCCDRow"
        self.vis_dark_current = "VISDarkCurrent"
        self.vis_data_compression = "VISDataCompression"
        self.vis_detector_active_pixel_long_dimension_format = "VISDetectorActivePixelLongDimensionFormat"
        self.vis_detector_active_pixel_short_dimension_format = "VISDetectorActivePixelShortDimensionFormat"
        self.vis_detector_overscanx = "VISDetectorOverscanx"
        self.vis_detector_pixel_long_dimension_format = "VISDetectorPixelLongDimensionFormat"
        self.vis_detector_prescanx = "VISDetectorPrescanx"
        self.vis_exposure_time = "VISExposureTime"
        self.vis_exposure_time_knowledge_error = "VISExposureTimeKnowledgeError"
        self.vis_focal_plane_assembly_long_dimension_max_image = "VISFocalPlaneAssemblyLongDimensionMaxImage"
        self.vis_focal_plane_assembly_short_dimension_max_image = "VISFocalPlaneAssemblyShortDimensionMaxImage"
        self.vis_gain = "VISGain"
        self.vis_readout_noise = "VISReadoutNoise"
        self.vis_distortion_maps = "VISDistortionMaps"
        self.cti_parallel_acs_mode = "CTIParallelAcsMode"
        self.cti_parallel_clocking_mode = "CTIParallelClockingMode"
        self.cti_parallel_express = "CTIParallelExpress"
        self.cti_parallel_niterations = "CTIParallelNIterations"
        self.cti_parallel_nlevels = "CTIParallelNLevels"
        self.cti_parallel_nspecies = "CTIParallelNSpecies"
        self.cti_parallel_read_out_offset = "CTIParallelReadOutOffset"
        self.cti_parallel_trap_density = "CTIParallelTrapDensity"
        self.cti_parallel_trap_life_time = "CTIParallelTrapLifeTime"
        self.cti_parallel_well_depth = "CTIParallelWellDepth"
        self.cti_parallel_well_fill_power = "CTIParallelWellFillPower"
        self.cti_parallel_well_notch_depth = "CTIParallelWellNotchDepth"
        self.cti_serial_acs_mode = "CTISerialAcsMode"
        self.cti_serial_clocking_mode = "CTISerialClockingMode"
        self.cti_serial_express = "CTISerialExpress"
        self.cti_serial_niterations = "CTISerialNIterations"
        self.cti_serial_nlevels = "CTISerialNLevels"
        self.cti_serial_nspecies = "CTISerialNSpecies"
        self.cti_serial_read_out_offset = "CTISerialReadOutOffset"
        self.cti_serial_trap_density = "CTISerialTrapDensity"
        self.cti_serial_trap_life_time = "CTISerialTrapLifeTime"
        self.cti_serial_well_depth = "CTISerialWellDepth"
        self.cti_serial_well_fill_power = "CTISerialWellFillPower"
        self.cti_serial_well_notch_depth = "CTISerialWellNotchDepth"
        self.fwhm_int_0 = "FWHMInt0"
        self.fwhm_xa_int_1x = "FWHMxaInt1x"
        self.fwhm_xa_lambda_1x = "FWHMxalambda1x"
        self.fwhm_xb_int_1x = "FWHMxbInt1x"
        self.fwhm_xb_lambda_1x = "FWHMxblambda1x"
        self.fwhm_ya_int_1y = "FWHMyaInt1y"
        self.fwhm_ya_lambda_1y = "FWHMyalambda1y"
        self.fwhm_yb_int_1y = "FWHMybInt1y"
        self.fwhm_yb_lambda_1y = "FWHMyblambda1y"
        self.ghost_model = "GhostModel"
        self.ghost_model_position_matrix_a = "GhostModelPositionMatrixA"
        self.ghost_model_position_matrix_b = "GhostModelPositionMatrixB"
        self.ghost_model_shift_x = "GhostModelShiftX"
        self.ghost_model_shift_y = "GhostModelShiftY"
        self.ghost_model_star_brightness = "GhostModelStarBrightness"
        self.mean_detector_quantum_efficiency_cbenominal_eol = "MeanDetectorQuantumEfficiencyCBENominalEOL"
        self.nl_p1 = "NL_P1"
        self.nl_p2 = "NL_P2"
        self.nl_p3 = "NL_P3"
        self.nlfwc = "NLFWC"
        self.ccd_full_well_capacity_eol = "CCDFullWellCapacityEOL"
        self.distortion_model = "DistortionModel"
        self.vis_optics_aocspixel_detector_psf = "VISOpticsAOCSPixelDetectorPSF"
        self.prnu = "PRNU"


mdb_keys = MDBKeys()
