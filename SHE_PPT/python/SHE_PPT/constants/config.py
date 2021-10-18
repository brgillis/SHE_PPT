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
SHEAR_ESTIMATES_MERGE_HEAD = "SHE_CTE_ShearEstimatesMerge_"
TU_MATCH_HEAD = "SHE_Validation_MatchToTU"


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
    # Options for SHE_CTE_ObjectIdSplit

    OID_BATCH_SIZE = OBJECT_ID_SPLIT_HEAD + "batch_size"
    OID_MAX_BATCHES = OBJECT_ID_SPLIT_HEAD + "max_batches"
    OID_IDS = OBJECT_ID_SPLIT_HEAD + "ids"

    # Options for SHE_CTE_SubObjectIdSplit

    SOID_BATCH_SIZE = SUBOBJECT_ID_SPLIT_HEAD + "batch_size"
    SOID_MAX_BATCHES = SUBOBJECT_ID_SPLIT_HEAD + "max_batches"
    SOID_IDS = SUBOBJECT_ID_SPLIT_HEAD + "ids"

    # Options for SHE_CTE_EstimateShear

    ES_METHODS = ESTIMATE_SHEAR_HEAD + "methods"
    ES_CHAINS_METHOD = ESTIMATE_SHEAR_HEAD + "chains_method"
    ES_FAST_MODE = ESTIMATE_SHEAR_HEAD + "fast_mode"
    ES_MEMMAP_IMAGES = ESTIMATE_SHEAR_HEAD + "memmap_images"

    # Options for SHE_CTE_ShearEstimatesMerge

    SEM_NUM_THREADS = SHEAR_ESTIMATES_MERGE_HEAD + "number_threads"

    # Options for SHE_Validation_MatchToTU

    TUM_ADD_BIN_COLUMNS = TU_MATCH_HEAD + "add_bin_columns"


# Task names for the Validation pipeline
VALIDATION_HEAD = "SHE_Validation_"
CTI_GAL_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidateCTIGal_"
SHEAR_BIAS_VALIDATION_HEAD = f"{VALIDATION_HEAD}ValidateShearBias_"


class ValidationConfigKeys(ConfigKeys):
    """ An Enum of all allowed keys for the SHE analysis validation pipeline.
    """

    # Options for multiple tasks - these global values will be overridden by values specific to a task if those are set

    VAL_LOCAL_FAIL_SIGMA = f"{VALIDATION_HEAD}local_fail_sigma"
    VAL_GLOBAL_FAIL_SIGMA = f"{VALIDATION_HEAD}global_fail_sigma"
    VAL_FAIL_SIGMA_SCALING = f"{VALIDATION_HEAD}fail_sigma_scaling"

    VAL_SNR_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "snr_bin_limits"
    VAL_BG_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "bg_bin_limits"
    VAL_COLOUR_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "colour_bin_limits"
    VAL_SIZE_BIN_LIMITS = CTI_GAL_VALIDATION_HEAD + "size_bin_limits"

    # Options for SHE_Validation_ValidateShearBias

    SBV_MAX_G_IN = f"{SHEAR_BIAS_VALIDATION_HEAD}max_g_in"
    SBV_BOOTSTRAP_ERRORS = f"{SHEAR_BIAS_VALIDATION_HEAD}bootstrap_errors"
    SBV_REQUIRE_FITCLASS_ZERO = f"{SHEAR_BIAS_VALIDATION_HEAD}require_fitclass_zero"

    # Options for SHE_Validation_MatchToTU

    TUM_ADD_BIN_COLUMNS = TU_MATCH_HEAD + "add_bin_columns"


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
    }

D_GLOBAL_CONFIG_TYPES: Dict[ConfigKeys, Union[Type, Tuple[Type, Type]]] = {
    GlobalConfigKeys.PIP_PROFILE: bool,
    }

D_GLOBAL_CONFIG_CLINE_ARGS: Dict[ConfigKeys, str] = {
    GlobalConfigKeys.PIP_PROFILE: "profile",
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
