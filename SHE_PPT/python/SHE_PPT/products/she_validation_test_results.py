""" @file she_validation_test_results.py

    Created 24 Nov 2020

    Functions to create and output a she_validation_test_results data product.

    Origin: OU-SHE - Output from various pipelines.
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


from copy import deepcopy

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.mer.raw.finalcatalog_stub import dpdMerFinalCatalog
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from ST_DataModelBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_no_files


sample_file_name = "SHE_PPT/sample_validation_test_results.xml"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_no_files(binding_class=dpdSheValidationTestResults)


def create_dpd_she_validation_test_results(reference_product=None,
                                           source_pipeline="sheAnalysis",
                                           observation_mode=None,
                                           num_tests=1,
                                           num_exposures=-1,):
    """
        @TODO fill in docstring
    """

    dpd_she_validation_test_results = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_validation_test_results.Header = HeaderProvider.create_generic_header("DpdSheValidationTestResults")

    # Quick alias to Data to save text
    Data = dpd_she_validation_test_results.Data

    # Set up common SourcePipeline and ObservationMode attributes
    Data.SourcePipeline = source_pipeline
    Data.ObservationMode = observation_mode

    # Set the desired number of tests
    if num_tests <= 0:
        del Data.ValidationTestList[0]
    elif num_tests > 1:
        # Make deep copies of the initial test to each entry in the list
        test_zero = Data.ValidationTestList[0]
        Data.ValidationTestList = [test_zero] * num_tests
        for i in range(num_tests):
            if i != 0:
                Data.ValidationTestList[i] = deepcopy(test_zero)

    if reference_product is not None:
        if isinstance(reference_product, dpdMerFinalCatalog):
            # Using a tile as reference, so set attributes that don't apply to None
            Data.ExposureProductId = None
            Data.ObservationId = None
            Data.PointingId = None
            Data.NumberExposures = None

            # And set the Tile ID
            Data.TileId = reference_product.Data.TileIndex

        elif isinstance(reference_product, dpdVisCalibratedFrame):
            # Using an exposure as reference, so delete attributes that don't apply
            Data.TileId = None
            Data.NumberExposures = None

            # And set the values that do apply
            Data.ExposureProductId = reference_product.Header.ProductId
            Data.ObservationId = reference_product.Data.ObservationSequence.ObservationId
            Data.PointingId = reference_product.Data.ObservationSequence.PointingId

        elif isinstance(reference_product, dpdVisStackedFrame):
            # Using an observation as reference, so delete attributes that don't apply
            Data.TileId = None
            Data.PointingId = None
            Data.ExposureProductId = None

            # And set the values that do apply
            Data.ObservationId = reference_product.Data.ObservationId
            Data.NumberExposures = num_exposures

        else:
            raise TypeError("Unrecognized type of reference product: " + str(type(reference_product)))

    else:
        # Set up attributes we do know about
        Data.NumberExposures = num_exposures

    return dpd_she_validation_test_results


# Add a useful alias
create_validation_test_results_product = create_dpd_she_validation_test_results
