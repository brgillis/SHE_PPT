""" @file she_psf_model_image_product.py

    Created 17 Nov 2017

    Functions to create and output a she_psf_model_image data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines
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

__updated__ = "2020-06-25"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdShePsfModelImage # @FIXME
    binding_class = DpdShePsfModelImage

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename)


def __get_data_filename(self):
    return get_data_filename_from_product(self)


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename()]

    return all_filenames


class DpdShePsfModelImage:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class ShePsfModelImage:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_psf_model_image(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_psf_model_image = she_dpd.DpdShePsfModelImage() # FIXME
    dpd_she_psf_model_image = DpdShePsfModelImage()

    # dpd_she_psf_model_image.Header = HeaderProvider.create_generic_header("SHE") #
    # FIXME
    dpd_she_psf_model_image.Header = "SHE"

    dpd_she_psf_model_image.Data = create_she_psf_model_image(filename)

    return dpd_she_psf_model_image


# Add a useful alias
create_psf_model_image_product = create_dpd_she_psf_model_image


def create_she_psf_model_image(filename=None):
    """
        @TODO fill in docstring
    """

    # she_psf_model_image = she_dpd.ShePsfModelImage() # @FIXME
    she_psf_model_image = ShePsfModelImage()

    she_psf_model_image.format = "UNDEFINED"
    she_psf_model_image.version = "0.0"

    she_psf_model_image.DataContainer = DataContainer()
    she_psf_model_image.DataContainer.FileName = filename
    she_psf_model_image.DataContainer.filestatus = "PROPOSED"

    return she_psf_model_image
