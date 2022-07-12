""" @file vis_calibrated_frame.py

    Created 17 Nov 2017

    Functions to create and output a calibrated_frame data product.

    Origin: OU-VIS
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

import ST_DataModelBindings.pro.vis_stub as vis_pro
from ST_DataModelBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
from ST_DataModelBindings.sys.dss_stub import dataContainer
from ..product_utility import (create_product_from_template, get_data_filename_from_product, get_filename_datastorage,
                               set_data_filename_of_product, set_filename_datastorage, )

sample_file_name = "SHE_PPT/sample_vis_calibrated_frame.xml"
product_type_name = "DpdVisCalibratedFrame"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdVisCalibratedFrame

    # Add the data file name methods

    binding_class.set_filename = set_filename_datastorage
    binding_class.get_filename = get_filename_datastorage

    binding_class.set_data_filename = set_filename_datastorage
    binding_class.get_data_filename = get_filename_datastorage

    binding_class.set_psf_filename = _set_psf_filename
    binding_class.get_psf_filename = _get_psf_filename

    binding_class.set_bkg_filename = _set_bkg_filename
    binding_class.get_bkg_filename = _get_bkg_filename

    binding_class.set_wgt_filename = _set_wgt_filename
    binding_class.get_wgt_filename = _get_wgt_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.has_files = True

    binding_class.init_function = create_dpd_vis_calibrated_frame


def _set_psf_filename(self, filename):
    if not hasattr(self.Data, "PsfModelStorage") or self.Data.PsfModelStorage is None:
        self.Data.PsfModelStorage = create_vis_psf_storage(filename)

    set_data_filename_of_product(self, filename, "PsfModelStorage")


def _get_psf_filename(self):
    if hasattr(self.Data, "PsfModelStorage") and self.Data.PsfModelStorage is not None:
        return get_data_filename_from_product(self, "PsfModelStorage")
    return None


def _set_bkg_filename(self, filename):
    if not hasattr(self.Data, "BackgroundStorage") or self.Data.BackgroundStorage is None:
        self.Data.BackgroundStorage = create_vis_bkg_storage(filename)

    set_data_filename_of_product(self, filename, "BackgroundStorage")


def _get_bkg_filename(self):
    if hasattr(self.Data, "BackgroundStorage") and self.Data.BackgroundStorage is not None:
        return get_data_filename_from_product(self, "BackgroundStorage")
    return None


def _set_wgt_filename(self, filename):
    if not hasattr(self.Data, "WeightStorage") or self.Data.WeightStorage is None:
        self.Data.WeightStorage = create_vis_wgt_storage(filename)

    set_data_filename_of_product(self, filename, "WeightStorage")


def _get_wgt_filename(self):
    if hasattr(self.Data, "WeightStorage") and self.Data.WeightStorage is not None:
        return get_data_filename_from_product(self, "WeightStorage")
    return None


def _get_all_filenames(self):

    all_filenames = [self.get_data_filename(),
                     self.get_psf_filename(),
                     self.get_bkg_filename(),
                     self.get_wgt_filename(), ]

    return all_filenames


def create_dpd_vis_calibrated_frame(data_filename = "None",
                                    psf_filename = "None",
                                    bkg_filename = "None",
                                    wgt_filename = "None"):
    """
        @TODO fill in docstring
    """

    dpd_vis_calibrated_frame = create_product_from_template(template_filename=sample_file_name,
                                                            product_type_name=product_type_name,
                                                            data_filename=data_filename)
    dpd_vis_calibrated_frame.set_psf_filename(psf_filename)
    dpd_vis_calibrated_frame.set_bkg_filename(bkg_filename)
    dpd_vis_calibrated_frame.set_wgt_filename(wgt_filename)

    return dpd_vis_calibrated_frame


def init_storage(type, filename, format, version, filestatus):

    data_storage = type()

    data_storage.format = format
    data_storage.version = version

    data_storage.DataContainer = dataContainer()
    data_storage.DataContainer.FileName = filename
    data_storage.DataContainer.filestatus = filestatus

    return data_storage


def create_vis_data_storage(filename, format = "vis.calibratedFrame", version = "0.1", filestatus = "PROPOSED"):

    data_storage = init_storage(
        vis_pro.visCalibratedStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_psf_storage(filename, format = "vis.psfModel", version = "0.1", filestatus = "PROPOSED"):

    data_storage = init_storage(
        vis_pro.visPsfModelStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_bkg_storage(filename, format = "vis.backgroundMap", version = "0.1", filestatus = "PROPOSED"):

    data_storage = init_storage(
        vis_pro.visBackgroundStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_wgt_storage(filename, format = "vis.weightMap", version = "0.1", filestatus = "PROPOSED"):

    data_storage = init_storage(
        vis_pro.visWeightStorageFitsFile, filename, format, version, filestatus)

    return data_storage
