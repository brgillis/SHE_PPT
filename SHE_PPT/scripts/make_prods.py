"""
This script generates random (but valid) data sample data products, and puts them in AUX.

This script can be used after a data model version update to re-generate all the sample products.

Sadly due to the requirement of PyQt5 this cannot be used within pipeline code to auto-generate a product on demand.

Usage:
    Run from the top level SHE_PPT directory (e.g. $HOME/Work/Projects/SHE_PPT)
    $ ./build.x86_64-conda_cos6-gcc93-o2g/run python SHE_PPT/scripts/make_prods.py

"""

import sys

import ST_DataModelBindings
import ST_DM_DmUtils.DmUtils as dm_utils

from ST_DM_DPRandom.DPGenerator import RandomDataModel
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

random_dm = RandomDataModel(ST_DataModelBindings)


def get_fits_defs_dict():
    """Goes through all the table formats in SHE_PPT.table_formats and constructs a dict of the fits_def
    and the fits_version"""
    import SHE_PPT.table_formats as tfs

    fits_defs = {}
    for table_name in tfs.__all__:
        table_module = getattr(tfs, table_name)
        try:
            fits_def = table_module.fits_def
            fits_ver = table_module.fits_version
            # NOTE: we use the lowercase version here as some have case mismatches between the fits_def
            # and the DataStorage format
            fits_defs[fits_def.lower()] = fits_ver

            # Edge case for the PSFModelImage where its table def is "she.psfModelImage.shePsfC"
            # Here we trim the .shePsfC off
            if len(fits_def.split(".")) > 2:
                fits_def_short = "%s.%s" % tuple(fits_def.split(".")[:-1])
                fits_defs[fits_def_short.lower()] = fits_ver
                print(fits_def_short)
        except Exception:
            pass

    return fits_defs


FITS_DEFS = get_fits_defs_dict()


def fix_datastorage(datastorage, default_version=0.1):
    """Cleans up the randomly generated DataStorage"""

    # Tries to get the version number from SHE_PPT.table_format, else uses a default
    if hasattr(datastorage, "format"):
        if datastorage.format.lower() in FITS_DEFS:
            datastorage.version = FITS_DEFS[datastorage.format.lower()]
        else:
            datastorage.version = default_version
    datastorage.DataContainer.FileName = "None"
    datastorage.DataContainer.filestatus = "PROPOSED"
    datastorage.DataContainer.checksumMethod = None
    datastorage.DataContainer.checksumValue = None


def create_dpd(dpd_type, output_filename, directory=""):
    print("Creating sample %s with filename %s" % (dpd_type, output_filename))

    dpd = random_dm.get_dp_from_name(dpd_type)

    # fix some aspects of the dpd
    dpd.Header.ProductType = dpd_type

    if hasattr(dpd.Data, "PlaceholderData"):
        dpd.Data.PlaceholderData = ["None"]

    if hasattr(dpd.Data, "DataStorage"):
        try:
            fix_datastorage(dpd.Data.DataStorage)
        except AttributeError:
            # Some products have DataStorage as a list, so we need to modify the 0th element
            fix_datastorage(dpd.Data.DataStorage[0])

    if hasattr(dpd.Data, "KsbCalibrationFileList"):
        fix_datastorage(dpd.Data.KsbCalibrationFileList[0].DataStorage)

    if hasattr(dpd.Data, "RegaussCalibrationFileList"):
        fix_datastorage(dpd.Data.RegaussCalibrationFileList[0].DataStorage)

    if hasattr(dpd.Data, "DataStorageList"):
        fix_datastorage(dpd.Data.DataStorageList[0])

    if hasattr(dpd.Data, "RegaussShearMeasurements"):
        fix_datastorage(dpd.Data.RegaussShearMeasurements.DataStorage)

    if hasattr(dpd.Data, "LensMcShearMeasurements"):
        fix_datastorage(dpd.Data.LensMcShearMeasurements.DataStorage)

    if hasattr(dpd.Data, "MomentsMlShearMeasurements"):
        fix_datastorage(dpd.Data.MomentsMlShearMeasurements.DataStorage)

    if hasattr(dpd.Data, "KsbShearMeasurements"):
        fix_datastorage(dpd.Data.KsbShearMeasurements.DataStorage)

    if hasattr(dpd.Data, "KSB"):
        fix_datastorage(dpd.Data.KSB)

    if hasattr(dpd.Data, "LensMC"):
        fix_datastorage(dpd.Data.LensMC)

    if hasattr(dpd.Data, "MomentsML"):
        fix_datastorage(dpd.Data.MomentsML)

    if hasattr(dpd.Data, "REGAUSS"):
        fix_datastorage(dpd.Data.REGAUSS)

    if hasattr(dpd.Data, "BfdMoments"):
        dpd.Data.BfdMoments = None

    if "LensMcChains" in dpd_type:
        fix_datastorage(dpd.Data.DataStorage)

    dpd.validateBinding()
    dm_utils.save_product_metadata(dpd, output_filename)

    # make sure we can read it back in
    dpd = dm_utils.read_product_metadata(output_filename)


prods = {
    "DpdSheStarCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_star_catalog.xml",
    # Deprecated
    # "DpdShePsfCalibrationParameters": "SHE_PPT/auxdir/SHE_PPT/sample_psf_calibration_parameters.xml",
    "DpdShePsfLevel1CalibrationParameters": "SHE_PPT/auxdir/SHE_PPT/sample_psf_level1_calibration_parameters.xml",
    "DpdShePsfLevel2CalibrationParameters": "SHE_PPT/auxdir/SHE_PPT/sample_psf_level2_calibration_parameters.xml",
    "DpdSheCommonCalibration": "SHE_PPT/auxdir/SHE_PPT/sample_common_calibration.xml",
    "DpdSheLensMcCalibration": "SHE_PPT/auxdir/SHE_PPT/sample_lensmc_calibration.xml",
    "DpdSheValidatedMeasurements": "SHE_PPT/auxdir/SHE_PPT/sample_validated_shear_measurements.xml",
    "DpdVisCalibratedFrame": "SHE_PPT/auxdir/SHE_PPT/sample_vis_calibrated_frame.xml",
    "DpdVisStackedFrame": "SHE_PPT/auxdir/SHE_PPT/sample_vis_stacked_frame.xml",
    "DpdSheKsbCalibration": "SHE_PPT/auxdir/SHE_PPT/sample_ksb_calibration.xml",
    "DpdSheIntermediateCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_intermediate_catalog.xml",
    "DpdSheAnalysisConfig": "SHE_PPT/auxdir/SHE_PPT/sample_analysis_config.xml",
    "DpdSheReconciliationConfig": "SHE_PPT/auxdir/SHE_PPT/sample_reconciliation_config.xml",
    "DpdSheIntermediateEuclidizedHstImages": "SHE_PPT/auxdir/SHE_PPT/sample_intermediate_euclidized_hst_images.xml",
    "DpdShePsfFieldParameters": "SHE_PPT/auxdir/SHE_PPT/sample_psf_field_parameters.xml",
    "DpdShePlaceholderCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_placeholder_catalog.xml",
    "DpdSheLensMcTraining": "SHE_PPT/auxdir/SHE_PPT/sample_lensmc_training.xml",
    "DpdSheGalaxyPopulationPriors": "SHE_PPT/auxdir/SHE_PPT/sample_galaxy_population_priors.xml",
    "DpdShePsfModelImage": "SHE_PPT/auxdir/SHE_PPT/sample_psf_model_image.xml",
    "DpdSheIntermediateObservationCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_intermediate_observation_catalog.xml",
    "DpdShePlaceholderGeneral": "SHE_PPT/auxdir/SHE_PPT/sample_placeholder_general.xml",
    "DpdSheRegaussTraining": "SHE_PPT/auxdir/SHE_PPT/sample_regauss_training.xml",
    "DpdSheCalibrationConfig": "SHE_PPT/auxdir/SHE_PPT/sample_calibration_config.xml",
    "DpdSheObjectIdList": "SHE_PPT/auxdir/SHE_PPT/sample_object_id_list.xml",
    "DpdSheMomentsMlTrainingConfig": "SHE_PPT/auxdir/SHE_PPT/sample_momentsml_training_config.xml",
    "DpdSheExpectedShearValidationStatistics": "SHE_PPT/auxdir/SHE_PPT/sample_expected_shear_validation_statistics.xml",
    "DpdMerFinalCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_mer_final_catalog.xml",
    "DpdSheValidationTestResults": "SHE_PPT/auxdir/SHE_PPT/sample_validation_test_results.xml",
    "DpdSheMomentsMlTraining": "SHE_PPT/auxdir/SHE_PPT/sample_momentsml_training.xml",
    "DpdSheMomentsMlCalibration": "SHE_PPT/auxdir/SHE_PPT/sample_momentsml_calibration.xml",
    "DpdSheReconciledLensMcChains": "SHE_PPT/auxdir/SHE_PPT/sample_reconciled_lensmc_chains.xml",
    "DpdSheStackReprojectedSegmentationMap": "SHE_PPT/auxdir/SHE_PPT/sample_stack_reprojected_segmentation_map.xml",
    "DpdShePlaceholderObservationCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_placeholder_observation_catalog.xml",
    "DpdSheRegaussCalibration": "SHE_PPT/auxdir/SHE_PPT/sample_regauss_calibration.xml",
    "DpdSheMeasurements": "SHE_PPT/auxdir/SHE_PPT/sample_shear_measurements.xml",
    "DpdSheFinalEuclidizedHstImages": "SHE_PPT/auxdir/SHE_PPT/sample_final_euclidized_hst_images.xml",
    "DpdSheIntermediateTileCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_intermediate_tile_catalog.xml",
    "DpdMerSegmentationMap": "SHE_PPT/auxdir/SHE_PPT/sample_mer_segmentation_map.xml",
    "DpdShePlaceholderTileCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_placeholder_tile_catalog.xml",
    "DpdSheExposureReprojectedSegmentationMap": "SHE_PPT/auxdir/SHE_PPT/sample_exposure_reprojected_segmentation_map.xml",  # noqa: E501
    "DpdSheIntermediateGeneral": "SHE_PPT/auxdir/SHE_PPT/sample_intermediate_general.xml",
    "DpdSheReconciledMeasurements": "SHE_PPT/auxdir/SHE_PPT/sample_reconciled_shear_measurements.xml",
    "DpdShePsfAnalysisConfig": "SHE_PPT/auxdir/SHE_PPT/sample_psf_analysis_config.xml",
    "DpdShePsfCalibrationConfig": "SHE_PPT/auxdir/SHE_PPT/sample_psf_calibration_config.xml",
    "DpdSheLensMcChains": "SHE_PPT/auxdir/SHE_PPT/sample_lensmc_chains.xml",
    "DpdSheKsbTraining": "SHE_PPT/auxdir/SHE_PPT/sample_ksb_training.xml",
    "DpdPhzPfOutputCatalog": "SHE_PPT/auxdir/SHE_PPT/sample_phz_pf_output_catalog.xml",
    "DpdSheBiasParams": "SHE_PPT/auxdir/SHE_PPT/sample_she_bias_parameters.xml",
}

if __name__ == "__main__":
    for dpd_type, output_name in prods.items():
        create_dpd(dpd_type, output_name)
