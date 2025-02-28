""" @file test_data.py

    Created 12 Aug 2021

    Constants used for miscellaneous purposes
"""

__updated__ = "2021-08-18"

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

from typing import Any, Dict, Tuple, Type, Union

# Task name for generic config keys
from .classes import AllowedEnum
from ..argument_parser import CA_DISABLE_FAILSAFE, CA_PROFILE

PIPELINE_HEAD = "SHE_Pipeline_"


class ConfigKeys(AllowedEnum):
    """ Derived class for ConfigKeys, for type-checking purposes.
    """
    pass


class GlobalConfigKeys(ConfigKeys):
    """ Derived class for ConfigKeys, which contains common keys for all pipelines
    """

    # Pipeline-wide options

    PIP_PROFILE = PIPELINE_HEAD + "profile"
    PIP_DISABLE_FAILSAFE = PIPELINE_HEAD + "disable_failsafe"

    # Placeholder options

    PIP_PLACEHOLDER_0 = PIPELINE_HEAD + "placeholder_0"
    PIP_PLACEHOLDER_1 = PIPELINE_HEAD + "placeholder_1"
    PIP_PLACEHOLDER_2 = PIPELINE_HEAD + "placeholder_2"
    PIP_PLACEHOLDER_3 = PIPELINE_HEAD + "placeholder_3"
    PIP_PLACEHOLDER_4 = PIPELINE_HEAD + "placeholder_4"
    PIP_PLACEHOLDER_5 = PIPELINE_HEAD + "placeholder_5"
    PIP_PLACEHOLDER_6 = PIPELINE_HEAD + "placeholder_6"
    PIP_PLACEHOLDER_7 = PIPELINE_HEAD + "placeholder_7"
    PIP_PLACEHOLDER_8 = PIPELINE_HEAD + "placeholder_8"
    PIP_PLACEHOLDER_9 = PIPELINE_HEAD + "placeholder_9"


# Task names for Analysis pipeline
REMAP_HEAD = "SHE_MER_RemapMosaic_"
OBJECT_ID_SPLIT_HEAD = "SHE_CTE_ObjectIdSplit_"
SUBOBJECT_ID_SPLIT_HEAD = "SHE_CTE_SubObjectIdSplit_"
PSF_HEAD = "SHE_PSFToolkit_"
ESTIMATE_SHEAR_HEAD = "SHE_CTE_EstimateShear_"
LENSMC_HEAD = "SHE_LensMC_"
SHEAR_ESTIMATES_MERGE_HEAD = "SHE_CTE_ShearEstimatesMerge_"
TU_MATCH_HEAD = "SHE_Validation_MatchToTU_"

# Task names for the Validation and Analysis pipelines
VALIDATION_HEAD = "SHE_Validation_"
CTI_GAL_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidateCTIGal_"
CTI_PSF_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidateCTIPSF_"
SHEAR_BIAS_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidateShearBias_"
PSF_RES_SP_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidatePSFResStarPos_"
PSF_RES_INT_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidatePSFResInt_"


class AnalysisConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE analysis pipelines.
    """

    # Options for SHE_MER_RemapMosaic

    REMAP_NUM_THREADS_EXP = REMAP_HEAD + "num_threads_exposures"
    REMAP_NUM_SWARP_THREADS_EXP = REMAP_HEAD + "num_swarp_threads_exposures"
    REMAP_NUM_THREADS_STACK = REMAP_HEAD + "num_threads_stack"
    REMAP_NUM_SWARP_THREADS_STACK = REMAP_HEAD + "num_swarp_threads_stack"
    REMAP_STAGGER = REMAP_HEAD + "stagger_per_thread"

    # Options for SHE_PSFToolkit_ModelPSFs

    PSF_WV_SAMPLES = PSF_HEAD + "wv_samples"
    PSF_ROTATION = PSF_HEAD + "psf_rotation"
    PSF_FITTING_MODE = PSF_HEAD + "fitting_mode"
    PSF_WAVEFRONT_SIZE = PSF_HEAD + "wavefront_size"
    PSF_OVERSAMPLING_FACTOR = PSF_HEAD + "oversampling_factor"
    PSF_WAVEFRONT_SAMPLING_METHOD = PSF_HEAD + "wavefront_sampling_method"
    PSF_FFT_ALGORITHM = PSF_HEAD + "fft_algorithm"
    PSF_FFT_PROCESSES = PSF_HEAD + "fft_processes"
    PSF_FFT_MEM_MANAGEMENT = PSF_HEAD + "fft_mem_management"
    PSF_OUTPUT_PIXEL_SIZE = PSF_HEAD + "output_pixel_size"
    PSF_OUTPUT_PSF_SIZE = PSF_HEAD + "output_psf_size"
    PSF_DEFAULT_PSF_MODEL = PSF_HEAD + "default_psf_model"
    PSF_PIXEL_SHIFT_X = PSF_HEAD + "pixel_shift_x"
    PSF_PIXEL_SHIFT_Y = PSF_HEAD + "pixel_shift_y"
    PSF_ZERNIKE_MODE_SKIP = PSF_HEAD + "zernike_mode_skip"
    PSF_ZERNIKE_MODE_COUNT = PSF_HEAD + "zernike_mode_count"
    PSF_INTERPOLATE_ZERNIKE = PSF_HEAD + "interpolate_zernike"
    PSF_EXTRAPOLATE_DISTORTION_FOV = PSF_HEAD + "extrapolate_distortion_fov"
    PSF_PUPIL_TELESCOPE_GEOMETRY = PSF_HEAD + "pupil_telescope_geometry"
    PSF_PUPIL_AMPLITUDE_ANTIALIAS = PSF_HEAD + "pupil_amplitude_antialias"
    PSF_PUPIL_AMPLITUDE_SHIFT = PSF_HEAD + "pupil_amplitude_shift"
    PSF_NIEMI_EFFECT_SWITCH = PSF_HEAD + "niemi_effect_switch"
    PSF_AOCS_EFFECT_SWITCH = PSF_HEAD + "aocs_effect_switch"
    PSF_PIXELRESPONSE_EFFECT_SWITCH = PSF_HEAD + "pixelresponse_effect_switch"
    PSF_AOCS_TIME_SERIES_FILE = PSF_HEAD + "aocs_time_series_file"
    PSF_BANDPASS_START = PSF_HEAD + "bandpass_start"
    PSF_BANDPASS_END = PSF_HEAD + "bandpass_end"
    PSF_BANDPASS_FULL_STEP = PSF_HEAD + "bandpass_full_step"
    PSF_RESAMPLING_RESPONSE_CONSERVE_FLUX = PSF_HEAD + "resampling_response_conserve_flux"
    PSF_BINNED_RESPONSE_INTERPOLATION_METHOD = PSF_HEAD + "binned_response_interpolation_method"
    PSF_WAVELENGTH_RANGE_START = PSF_HEAD + "wavelength_range_start"
    PSF_WAVELENGTH_RANGE_END = PSF_HEAD + "wavelength_range_end"
    PSF_CACHE_INTERPOLATED_PSF_CUBE = PSF_HEAD + "cache_interpolated_psf_cube"
    PSF_EXPOSURE_TIME = PSF_HEAD + "exposure_time"
    PSF_TELESCOPE_MODEL_PATH = PSF_HEAD + "telescope_model_path"
    PSF_TELESCOPE_MODEL_NOMINAL_FILE = PSF_HEAD + "telescope_model_nominal_file"
    PSF_PICKLES_DATA_PATH = PSF_HEAD + "pickles_data_path"
    PSF_COUNTS_PATH = PSF_HEAD + "counts_path"
    PSF_TELESCOPE_MODEL = PSF_HEAD + "telescope_model"
    PSF_RAYFILE_PATH = PSF_HEAD + "rayfile_path"
    PSF_VERBOSE = PSF_HEAD + "verbose"
    PSF_USERWARNINGS = PSF_HEAD + "userWarnings"
    PSF_TIME_MONO = PSF_HEAD + "time_mono"
    PSF_TIME_EXPAND = PSF_HEAD + "time_expand"
    PSF_WAVEFRONT_PAD_AMOUNT = PSF_HEAD + "wavefront_pad_amount"
    PSF_WAVEFRONT_CORRECTION = PSF_HEAD + "wavefront_correction"
    PSF_MIN_FLUX_VIS_APER = PSF_HEAD + "min_flux_vis_aper"
    PSF_MAX_FLUX_VIS_APER = PSF_HEAD + "max_flux_vis_aper"
    PSF_MIN_POINT_LIKE_PROB = PSF_HEAD + "min_point_like_prob"
    PSF_OUTPUT_FIXED_PSF = PSF_HEAD + "output_fixed_psf"
    PSF_FIT_THREADS = PSF_HEAD + "fit_threads"
    PSF_MODEL_THREADS = PSF_HEAD + "model_threads"
    PSF_PASS_IN_MEMORY = PSF_HEAD + "pass_in_memory"
    PSF_DEFAULT_FIELD_PARAMS = PSF_HEAD + "use_default_field_params"
    PSF_NUM_STARS = PSF_HEAD + "no_stars_to_fit"
    PSF_USE_EXPOSURES = PSF_HEAD + "use_exposures"
    PSF_USE_DETECTORS = PSF_HEAD + "use_detectors"
    PSF_NUM_PARAMETERS_TO_FIT = PSF_HEAD + "num_parameters_to_fit"
    PSF_MAX_FIT_ITERATIONS = PSF_HEAD + "max_fit_iterations"
    PSF_DET_TO_FIT = PSF_HEAD + "det_to_fit"
    PSF_FIT_CHECKPOINT_ITER = PSF_HEAD + "checkpoint_iter"
    PSF_MODEL_MASK_SIZE = PSF_HEAD + "model_mask_size"
    PSF_NUM_PROCESS = PSF_HEAD + "number_process"
    PSF_FRAC_INTERP = PSF_HEAD + "frac_stars_to_test_interp"

    # Options for SHE_CTE_ObjectIdSplit

    OID_BATCH_SIZE = OBJECT_ID_SPLIT_HEAD + "batch_size"
    OID_MAX_BATCHES = OBJECT_ID_SPLIT_HEAD + "max_batches"
    OID_IDS = OBJECT_ID_SPLIT_HEAD + "ids"
    OID_GROUPING_RADIUS = OBJECT_ID_SPLIT_HEAD + "grouping_radius"

    # Options for SHE_CTE_SubObjectIdSplit

    SOID_BATCH_SIZE = SUBOBJECT_ID_SPLIT_HEAD + "batch_size"
    SOID_MAX_BATCHES = SUBOBJECT_ID_SPLIT_HEAD + "max_batches"
    SOID_IDS = SUBOBJECT_ID_SPLIT_HEAD + "ids"

    # Options for SHE_CTE_EstimateShear

    ES_METHODS = ESTIMATE_SHEAR_HEAD + "methods"
    ES_CHAINS_METHOD = ESTIMATE_SHEAR_HEAD + "chains_method"
    ES_MEMMAP_IMAGES = ESTIMATE_SHEAR_HEAD + "memmap_images"

    # Options for SHE_LensMC

    LENSMC_STAMP_SIZE = LENSMC_HEAD + "stamp_size"
    LENSMC_X_BUFFER = LENSMC_HEAD + "x_buffer"
    LENSMC_Y_BUFFER = LENSMC_HEAD + "y_buffer"
    LENSMC_NO_MASK_DILATION = LENSMC_HEAD + "no_mask_dilation"
    LENSMC_HL_TO_EXP = LENSMC_HEAD + "hl_to_exp"
    LENSMC_N_BULGE = LENSMC_HEAD + "n_bulge"
    LENSMC_N_DISC = LENSMC_HEAD + "n_disc"
    LENSMC_E_MAX = LENSMC_HEAD + "e_max"
    LENSMC_RE_MAX = LENSMC_HEAD + "re_max"
    LENSMC_DELTA_MAX = LENSMC_HEAD + "delta_max"
    LENSMC_E_FLAG = LENSMC_HEAD + "e_flag"
    LENSMC_RE_FLAG = LENSMC_HEAD + "re_flag"
    LENSMC_DELTA_FLAG = LENSMC_HEAD + "delta_flag"
    LENSMC_DISC_ONLY = LENSMC_HEAD + "disc_only"
    LENSMC_PSF_OVERSAMPLING = LENSMC_HEAD + "psf_oversampling"
    LENSMC_SEED = LENSMC_HEAD + "seed"
    LENSMC_SHAPE_NOISE = LENSMC_HEAD + "shape_noise"
    LENSMC_RE_SG = LENSMC_HEAD + "re_sg"
    LENSMC_RETURN_CHAINS = LENSMC_HEAD + "return_chains"
    LENSMC_FAST_MODE = LENSMC_HEAD + "fast_mode"
    LENSMC_INCLUDE_VIS_UNDETECTED = LENSMC_HEAD + "include_vis_undetected"
    LENSMC_MONITOR = LENSMC_HEAD + "monitor"

    # Options for SHE_CTE_ShearEstimatesMerge

    SEM_NUM_THREADS = SHEAR_ESTIMATES_MERGE_HEAD + "number_threads"

    # Options for multiple validation tasks - these global values will be overridden by values specific to a task if
    # those are set

    VAL_LOCAL_FAIL_SIGMA = f"{VALIDATION_HEAD}local_fail_sigma"
    VAL_GLOBAL_FAIL_SIGMA = f"{VALIDATION_HEAD}global_fail_sigma"
    VAL_FAIL_SIGMA_SCALING = f"{VALIDATION_HEAD}fail_sigma_scaling"

    VAL_SNR_BIN_LIMITS = f"{VALIDATION_HEAD}snr_bin_limits"
    VAL_BG_BIN_LIMITS = f"{VALIDATION_HEAD}bg_bin_limits"
    VAL_COLOUR_BIN_LIMITS = f"{VALIDATION_HEAD}colour_bin_limits"
    VAL_SIZE_BIN_LIMITS = f"{VALIDATION_HEAD}size_bin_limits"
    VAL_EPOCH_BIN_LIMITS = f"{VALIDATION_HEAD}epoch_bin_limits"

    # Options for SHE_Validation_MatchToTU

    TUM_ADD_BIN_COLUMNS = TU_MATCH_HEAD + "add_bin_columns"

    # Options for SHE_Validation_ValidateCTIGal

    CG_LOCAL_FAIL_SIGMA = f"{CTI_GAL_VALIDATION_HEAD}local_fail_sigma"
    CG_GLOBAL_FAIL_SIGMA = f"{CTI_GAL_VALIDATION_HEAD}global_fail_sigma"
    CG_FAIL_SIGMA_SCALING = f"{CTI_GAL_VALIDATION_HEAD}fail_sigma_scaling"

    CG_SNR_BIN_LIMITS = f"{CTI_GAL_VALIDATION_HEAD}snr_bin_limits"
    CG_BG_BIN_LIMITS = f"{CTI_GAL_VALIDATION_HEAD}bg_bin_limits"
    CG_COLOUR_BIN_LIMITS = f"{CTI_GAL_VALIDATION_HEAD}colour_bin_limits"
    CG_SIZE_BIN_LIMITS = f"{CTI_GAL_VALIDATION_HEAD}size_bin_limits"
    CG_EPOCH_BIN_LIMITS = f"{CTI_GAL_VALIDATION_HEAD}epoch_bin_limits"

    # Options for SHE_Validation_ValidateCTIPSF

    CP_LOCAL_FAIL_SIGMA = f"{CTI_PSF_VALIDATION_HEAD}local_fail_sigma"
    CP_GLOBAL_FAIL_SIGMA = f"{CTI_PSF_VALIDATION_HEAD}global_fail_sigma"
    CP_FAIL_SIGMA_SCALING = f"{CTI_PSF_VALIDATION_HEAD}fail_sigma_scaling"

    CP_SNR_BIN_LIMITS = f"{CTI_PSF_VALIDATION_HEAD}snr_bin_limits"
    CP_BG_BIN_LIMITS = f"{CTI_PSF_VALIDATION_HEAD}bg_bin_limits"
    CP_COLOUR_BIN_LIMITS = f"{CTI_PSF_VALIDATION_HEAD}colour_bin_limits"
    CP_SIZE_BIN_LIMITS = f"{CTI_PSF_VALIDATION_HEAD}size_bin_limits"
    CP_EPOCH_BIN_LIMITS = f"{CTI_PSF_VALIDATION_HEAD}epoch_bin_limits"

    # Options for SHE_Validation_ValidatePSFResStarPos

    PRSP_P_FAIL = f"{PSF_RES_SP_VALIDATION_HEAD}p_fail"

    PRSP_SNR_BIN_LIMITS = f"{PSF_RES_SP_VALIDATION_HEAD}snr_bin_limits"

    # Options for SHE_Validation_ValidatePSFResInterp

    PRINT_LOCAL_FAIL_SIGMA = f"{PSF_RES_INT_VALIDATION_HEAD}local_fail_sigma"
    PRINT_GLOBAL_FAIL_SIGMA = f"{PSF_RES_INT_VALIDATION_HEAD}global_fail_sigma"
    PRINT_FAIL_SIGMA_SCALING = f"{PSF_RES_INT_VALIDATION_HEAD}fail_sigma_scaling"

    PRINT_SNR_BIN_LIMITS = f"{PSF_RES_INT_VALIDATION_HEAD}snr_bin_limits"
    PRINT_SED_BIN_LIMITS = f"{PSF_RES_INT_VALIDATION_HEAD}sed_bin_limits"
    PRINT_COORD_BIN_LIMITS = f"{PSF_RES_INT_VALIDATION_HEAD}coord_bin_limits"
    PRINT_EPOCH_BIN_LIMITS = f"{PSF_RES_INT_VALIDATION_HEAD}epoch_bin_limits"
    PRINT_ASPECT_BIN_LIMITS = f"{PSF_RES_INT_VALIDATION_HEAD}aspect_bin_limits"


class ValidationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE Validation pipeline.
    """

    # The first set of values here are shared with the Analysis pipeline, so we take the value directly from that
    # pipeline's ConfigKeys to reduce code duplication

    # Options for multiple validation tasks - these global values will be overridden by values specific to a task if
    # those are set

    VAL_LOCAL_FAIL_SIGMA = AnalysisConfigKeys.VAL_LOCAL_FAIL_SIGMA.value
    VAL_GLOBAL_FAIL_SIGMA = AnalysisConfigKeys.VAL_GLOBAL_FAIL_SIGMA.value
    VAL_FAIL_SIGMA_SCALING = AnalysisConfigKeys.VAL_FAIL_SIGMA_SCALING.value

    VAL_SNR_BIN_LIMITS = AnalysisConfigKeys.VAL_SNR_BIN_LIMITS.value
    VAL_BG_BIN_LIMITS = AnalysisConfigKeys.VAL_BG_BIN_LIMITS.value
    VAL_COLOUR_BIN_LIMITS = AnalysisConfigKeys.VAL_COLOUR_BIN_LIMITS.value
    VAL_SIZE_BIN_LIMITS = AnalysisConfigKeys.VAL_SIZE_BIN_LIMITS.value
    VAL_EPOCH_BIN_LIMITS = AnalysisConfigKeys.VAL_EPOCH_BIN_LIMITS.value

    # Options for SHE_Validation_MatchToTU

    TUM_ADD_BIN_COLUMNS = AnalysisConfigKeys.TUM_ADD_BIN_COLUMNS.value

    # Options for SHE_Validation_ValidateCTIGal

    CG_LOCAL_FAIL_SIGMA = AnalysisConfigKeys.CG_LOCAL_FAIL_SIGMA.value
    CG_GLOBAL_FAIL_SIGMA = AnalysisConfigKeys.CG_GLOBAL_FAIL_SIGMA.value
    CG_FAIL_SIGMA_SCALING = AnalysisConfigKeys.CG_FAIL_SIGMA_SCALING.value

    CG_SNR_BIN_LIMITS = AnalysisConfigKeys.CG_SNR_BIN_LIMITS.value
    CG_BG_BIN_LIMITS = AnalysisConfigKeys.CG_BG_BIN_LIMITS.value
    CG_COLOUR_BIN_LIMITS = AnalysisConfigKeys.CG_COLOUR_BIN_LIMITS.value
    CG_SIZE_BIN_LIMITS = AnalysisConfigKeys.CG_SIZE_BIN_LIMITS.value
    CG_EPOCH_BIN_LIMITS = AnalysisConfigKeys.CG_EPOCH_BIN_LIMITS.value

    # Options for SHE_Validation_ValidateCTIPSF

    CP_LOCAL_FAIL_SIGMA = AnalysisConfigKeys.CP_LOCAL_FAIL_SIGMA.value
    CP_GLOBAL_FAIL_SIGMA = AnalysisConfigKeys.CP_GLOBAL_FAIL_SIGMA.value
    CP_FAIL_SIGMA_SCALING = AnalysisConfigKeys.CP_FAIL_SIGMA_SCALING.value

    CP_SNR_BIN_LIMITS = AnalysisConfigKeys.CP_SNR_BIN_LIMITS.value
    CP_BG_BIN_LIMITS = AnalysisConfigKeys.CP_BG_BIN_LIMITS.value
    CP_COLOUR_BIN_LIMITS = AnalysisConfigKeys.CP_COLOUR_BIN_LIMITS.value
    CP_SIZE_BIN_LIMITS = AnalysisConfigKeys.CP_SIZE_BIN_LIMITS.value
    CP_EPOCH_BIN_LIMITS = AnalysisConfigKeys.CP_EPOCH_BIN_LIMITS.value

    # Options for SHE_Validation_ValidatePSFResStarPos

    PRSP_P_FAIL = AnalysisConfigKeys.PRSP_P_FAIL.value

    PRSP_SNR_BIN_LIMITS = AnalysisConfigKeys.PRSP_SNR_BIN_LIMITS.value

    # Options for SHE_Validation_ValidatePSFResInterp

    PRINT_LOCAL_FAIL_SIGMA = AnalysisConfigKeys.PRINT_LOCAL_FAIL_SIGMA.value
    PRINT_GLOBAL_FAIL_SIGMA = AnalysisConfigKeys.PRINT_GLOBAL_FAIL_SIGMA.value
    PRINT_FAIL_SIGMA_SCALING = AnalysisConfigKeys.PRINT_FAIL_SIGMA_SCALING.value

    PRINT_SNR_BIN_LIMITS = AnalysisConfigKeys.PRINT_SNR_BIN_LIMITS.value
    PRINT_SED_BIN_LIMITS = AnalysisConfigKeys.PRINT_SED_BIN_LIMITS.value
    PRINT_COORD_BIN_LIMITS = AnalysisConfigKeys.PRINT_COORD_BIN_LIMITS.value
    PRINT_EPOCH_BIN_LIMITS = AnalysisConfigKeys.PRINT_EPOCH_BIN_LIMITS.value
    PRINT_ASPECT_BIN_LIMITS = AnalysisConfigKeys.PRINT_ASPECT_BIN_LIMITS.value

    # And below here are options that are only used in the validation pipeline

    # Options for SHE_Validation_ValidateShearBias

    SBV_MAX_G_IN = f"{SHEAR_BIAS_VALIDATION_HEAD}max_g_in"
    SBV_BOOTSTRAP_ERRORS = f"{SHEAR_BIAS_VALIDATION_HEAD}bootstrap_errors"
    SBV_REQUIRE_FITCLASS_ZERO = f"{SHEAR_BIAS_VALIDATION_HEAD}require_fitclass_zero"

    SBV_SNR_BIN_LIMITS = f"{SHEAR_BIAS_VALIDATION_HEAD}snr_bin_limits"
    SBV_BG_BIN_LIMITS = f"{SHEAR_BIAS_VALIDATION_HEAD}bg_bin_limits"
    SBV_COLOUR_BIN_LIMITS = f"{SHEAR_BIAS_VALIDATION_HEAD}colour_bin_limits"
    SBV_SIZE_BIN_LIMITS = f"{SHEAR_BIAS_VALIDATION_HEAD}size_bin_limits"
    SBV_EPOCH_BIN_LIMITS = f"{SHEAR_BIAS_VALIDATION_HEAD}epoch_bin_limits"


# Task names for Reconciliation pipeline
RECONCILE_MEASUREMENTS_HEAD = "SHE_CTE_ReconcileMeasurements_"


class ReconciliationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE reconciliation pipeline.
    """

    # Options for SHE_CTE_CleanupBiasMeasurement

    REC_METHOD = RECONCILE_MEASUREMENTS_HEAD + "method"
    CHAINS_REC_METHOD = RECONCILE_MEASUREMENTS_HEAD + "chains_method"


# Task names for Calibration pipeline
CLEANUP_BIAS_MEASUREMENTS_HEAD = "SHE_CTE_CleanupBiasMeasurement_"
MEASURE_BIAS_HEAD = "SHE_CTE_MeasureBias_"
MEASURE_STATISTICS_HEAD = "SHE_CTE_MeasureStatistics_"


class CalibrationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE calibration pipelines.
    """

    # Options for SHE_CTE_CleanupBiasMeasurement

    CBM_CLEANUP = CLEANUP_BIAS_MEASUREMENTS_HEAD + "cleanup"

    # Options for SHE_CTE_EstimateShear - copy these from the other enum

    ES_METHODS = AnalysisConfigKeys.ES_METHODS.value
    ES_CHAINS_METHOD = AnalysisConfigKeys.ES_CHAINS_METHOD.value

    # Options for SHE_CTE_MeasureBias

    MB_ARCHIVE_DIR = MEASURE_BIAS_HEAD + "archive_dir"
    MB_NUM_THREADS = MEASURE_BIAS_HEAD + "number_threads"
    MB_WEBDAV_ARCHIVE = MEASURE_BIAS_HEAD + "webdav_archive"
    MB_WEBDAV_DIR = MEASURE_BIAS_HEAD + "webdav_dir"

    # Options for SHE_CTE_MeasureStatistics

    MS_ARCHIVE_DIR = MEASURE_STATISTICS_HEAD + "archive_dir"
    MS_WEBDAV_ARCHIVE = MEASURE_STATISTICS_HEAD + "webdav_archive"
    MS_WEBDAV_DIR = MEASURE_STATISTICS_HEAD + "webdav_dir"


# Set up dicts for pipeline config defaults and types
D_GLOBAL_CONFIG_DEFAULTS: Dict[ConfigKeys, Any] = {
    GlobalConfigKeys.PIP_PROFILE: False,
    GlobalConfigKeys.PIP_DISABLE_FAILSAFE: False,
    }

D_GLOBAL_CONFIG_TYPES: Dict[ConfigKeys, Union[Type, Tuple[Type, Type]]] = {
    GlobalConfigKeys.PIP_PROFILE: bool,
    GlobalConfigKeys.PIP_DISABLE_FAILSAFE: bool,
    }

D_GLOBAL_CONFIG_CLINE_ARGS: Dict[ConfigKeys, str] = {
    GlobalConfigKeys.PIP_PROFILE: CA_PROFILE,
    GlobalConfigKeys.PIP_DISABLE_FAILSAFE: CA_DISABLE_FAILSAFE,
    }


class ScalingExperimentsConfigKeys(ConfigKeys):
    HDF5 = "HDF5"
    CHUNKED = "chunked"
    MAXBATCHES = "maxbatches"
    BATCHSIZE = "batchsize"
    MEMMAP = "memmap"
    SPATIAL_BATCHING = "spatial_batching"
    DRY_RUN = "dry_run"
    MEAN_COMPUTE_TIME = "mean_compute_time"
    COMPRESSION = "compression"
