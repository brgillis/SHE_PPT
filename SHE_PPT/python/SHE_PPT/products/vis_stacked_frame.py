""" @file vis_stacked_frame.py

    Created 17 Nov 2017

    Functions to create and output a stacked_frame data product.

    Origin: OU-VIS
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

__updated__ = "2020-06-12"

from SHE_PPT.file_io import read_xml_product, find_aux_file
from SHE_PPT.product_utility import get_data_filename_from_product, set_data_filename_of_product
from SHE_PPT.products.vis_calibrated_frame import (create_vis_psf_storage,
                                               create_vis_bkg_storage, create_vis_wgt_storage)
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.vis.raw.visstackedframe_stub import dpdVisStackedFrame

sample_file_name = "SHE_PPT/sample_vis_stacked_frame.xml"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdVisStackedFrame

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.set_psf_filename = __set_psf_filename
    binding_class.get_psf_filename = __get_psf_filename

    binding_class.set_bkg_filename = __set_bkg_filename
    binding_class.get_bkg_filename = __get_bkg_filename

    binding_class.set_wgt_filename = __set_wgt_filename
    binding_class.get_wgt_filename = __get_wgt_filename

    binding_class.get_all_filenames = __get_all_filenames

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def __get_data_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def __set_psf_filename(self, filename):
    if not hasattr(self.Data, "PsfModelStorage") or self.Data.PsfModelStorage is None:
        self.Data.PsfModelStorage = create_vis_psf_storage(filename)
    set_data_filename_of_product(self, filename, "PsfModelStorage")


def __get_psf_filename(self):
    if hasattr(self.Data, "PsfModelStorage") and self.Data.PsfModelStorage is not None:
        return get_data_filename_from_product(self, "PsfModelStorage")
    return None


def __set_bkg_filename(self, filename):
    if not hasattr(self.Data, "BackgroundStorage") or self.Data.BackgroundStorage is None:
        self.Data.BackgroundStorage = create_vis_bkg_storage(filename)
    set_data_filename_of_product(self, filename, "BackgroundStorage")


def __get_bkg_filename(self):
    if hasattr(self.Data, "BackgroundStorage") and self.Data.BackgroundStorage is not None:
        return get_data_filename_from_product(self, "BackgroundStorage")
    return None


def __set_wgt_filename(self, filename):
    if not hasattr(self.Data, "WeightStorage") or self.Data.WeightStorage is None:
        self.Data.WeightStorage = create_vis_wgt_storage(filename)
    set_data_filename_of_product(self, filename, "WeightStorage")


def __get_wgt_filename(self):
    if hasattr(self.Data, "WeightStorage") and self.Data.WeightStorage is not None:
        return get_data_filename_from_product(self, "WeightStorage")
    return None


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename(),
                     self.get_psf_filename(),
                     self.get_bkg_filename(),
                     self.get_wgt_filename(), ]

    return all_filenames


def create_dpd_vis_stacked_frame(data_filename="default_data_filename.fits",
                                 bkg_filename="default_bkg_filename.fits",
                                 wgt_filename="default_wgt_filename.fits"):
    """
        @TODO fill in docstring
    """

    dpd_vis_stacked_frame = read_xml_product(
        find_aux_file(sample_file_name))

    dpd_vis_stacked_frame.Header = HeaderProvider.create_generic_header("VIS")

    dpd_vis_stacked_frame.set_data_filename(data_filename)
    dpd_vis_stacked_frame.set_bkg_filename(bkg_filename)
    dpd_vis_stacked_frame.set_wgt_filename(wgt_filename)

    return dpd_vis_stacked_frame


# Add a useful alias
create_stacked_frame_product = create_dpd_vis_stacked_frame
