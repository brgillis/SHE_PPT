""" @file she_validation_test_results.py

    Created 24 Nov 2020

    Functions to create and output a she_validation_test_results data product.

    Origin: OU-SHE - Output from various pipelines.
"""

__updated__ = "2021-08-16"

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


from copy import deepcopy

from ST_DataModelBindings.dpd.mer.raw.finalcatalog_stub import dpdMerFinalCatalog
from ST_DataModelBindings.dpd.she.raw.starcatalog_stub import dpdSheStarCatalog
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from ST_DataModelBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame
from ..product_utility import create_product_from_template, init_no_files

sample_file_name = "SHE_PPT/sample_validation_test_results.xml"
product_type_name = "DpdSheValidationTestResults"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_no_files(binding_class = dpdSheValidationTestResults,
                  init_function = create_dpd_she_validation_test_results)


def create_dpd_she_validation_test_results(reference_product = None,
                                           source_pipeline = "sheAnalysis",
                                           observation_mode = None,
                                           num_tests = 1,
                                           num_exposures = -1, ):
    """
        @TODO fill in docstring
    """

    dpd_she_validation_test_results = create_product_from_template(template_filename = sample_file_name,
                                                                   product_type_name = product_type_name, )

    # Quick alias to data_attr to save text
    data_attr = dpd_she_validation_test_results.Data

    # Set up common SourcePipeline and ObservationMode attributes
    data_attr.SourcePipeline = source_pipeline
    data_attr.ObservationMode = observation_mode

    # Set the desired number of tests
    if num_tests <= 0:
        del data_attr.ValidationTestList[0]
    elif num_tests > 1:
        # Make deep copies of the initial test to each entry in the list
        test_zero = data_attr.ValidationTestList[0]
        data_attr.ValidationTestList = [test_zero] * num_tests
        for i in range(num_tests):
            if i != 0:
                data_attr.ValidationTestList[i] = deepcopy(test_zero)

    if reference_product is not None:
        if isinstance(reference_product, dpdMerFinalCatalog):

            _init_for_tile(data_attr, tile_id = reference_product.Data.TileIndex)

        elif isinstance(reference_product, dpdVisCalibratedFrame):

            _init_for_exposure(data_attr,
                               exp_product_id = reference_product.Header.ProductId.value(),
                               obs_id = reference_product.Data.ObservationSequence.ObservationId,
                               pointing_id = reference_product.Data.ObservationSequence.PointingId)

        elif isinstance(reference_product, dpdSheStarCatalog):

            _init_for_exposure(data_attr,
                               exp_product_id = reference_product.Data.ExposureProductIdList[0],
                               obs_id = reference_product.Data.ObservationId,
                               pointing_id = reference_product.Data.PointingIdList[0])

        elif isinstance(reference_product, dpdVisStackedFrame):

            obs_id = reference_product.Data.ObservationId

            _init_for_observation(data_attr,
                                  obs_id = reference_product.Data.ObservationId,
                                  num_exposures = num_exposures)

        else:
            raise TypeError("Unrecognized type of reference product: " + str(type(reference_product)))

    else:
        # Set up attributes we do know about
        data_attr.NumberExposures = num_exposures

    return dpd_she_validation_test_results


def _init_for_observation(data_attr, obs_id, num_exposures):
    """Init the Data attr using an observation product as reference.
    """

    # Using an observation as reference, so delete attributes that don't apply
    data_attr.TileId = None
    data_attr.PointingId = None
    data_attr.ExposureProductId = None

    # And set the values that do apply
    data_attr.ObservationId = obs_id
    data_attr.NumberExposures = num_exposures


def _init_for_exposure(data_attr, exp_product_id, obs_id, pointing_id):
    """Init the Data attr using an exposure product as reference.
    """

    # Using an exposure as reference, so delete attributes that don't apply
    data_attr.TileId = None
    data_attr.NumberExposures = None

    # And set the values that do apply
    data_attr.ExposureProductId = exp_product_id
    data_attr.ObservationId = obs_id
    data_attr.PointingId = pointing_id


def _init_for_tile(data_attr, tile_id):
    """Init the Data attr using a tile product as reference.
    """

    # Using a tile as reference, so set attributes that don't apply to None
    data_attr.ExposureProductId = None
    data_attr.ObservationId = None
    data_attr.PointingId = None
    data_attr.NumberExposures = None

    # And set the Tile ID
    data_attr.TileId = tile_id


# Add a useful alias
create_validation_test_results_product = create_dpd_she_validation_test_results
