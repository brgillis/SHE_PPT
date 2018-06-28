""" @file calibrated_frame_product.py

    Created 17 Nov 2017

    Functions to create and output a calibrated_frame data product.

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

from EuclidDmBindings.dpd.vis.raw.calibratedframe_stub import dpdVisCalibratedFrame
import EuclidDmBindings.pro.vis_stub as vis_pro
from EuclidDmBindings.sys.dss_stub import dataContainer
import HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT.file_io import read_xml_product, find_aux_file


sample_file_name = "SHE_PPT/sample_calibrated_frame.xml"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdVisCalibratedFrame

    # Add the data file name methods

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.set_psf_filename = __set_psf_filename
    binding_class.get_psf_filename = __get_psf_filename

    binding_class.set_bkg_filename = __set_bkg_filename
    binding_class.get_bkg_filename = __get_bkg_filename

    binding_class.set_wgt_filename = __set_wgt_filename
    binding_class.get_wgt_filename = __get_wgt_filename

    return


def __set_data_filename(self, filename):
    self.Data.DataStorage.DataContainer.FileName = filename


def __get_data_filename(self):
    return self.Data.DataStorage.DataContainer.FileName


def __set_psf_filename(self, filename):
    if not hasattr(self.Data, "PsfModelStorage"):
        self.Data.PsfModelStorage = create_vis_psf_storage(filename)
    elif self.Data.PsfModelStorage is None:
        self.Data.PsfModelStorage = create_vis_psf_storage(filename)
    else:
        self.Data.PsfModelStorage.DataContainer.FileName = filename


def __get_psf_filename(self):
    if hasattr(self.Data, "PsfModelStorage"):
        if self.Data.PsfModelStorage is not None:
            return self.Data.PsfModelStorage.DataContainer.FileName
    return None


def __set_bkg_filename(self, filename):
    if not hasattr(self.Data, "BackgroundStorage"):
        self.Data.BackgroundStorage = create_vis_bkg_storage(filename)
    elif self.Data.BackgroundStorage is None:
        self.Data.BackgroundStorage = create_vis_bkg_storage(filename)
    else:
        self.Data.BackgroundStorage.DataContainer.FileName = filename


def __get_bkg_filename(self):
    if hasattr(self.Data, "BackgroundStorage"):
        if self.Data.BackgroundStorage is not None:
            return self.Data.BackgroundStorage.DataContainer.FileName
    return None


def __set_wgt_filename(self, filename):
    if not hasattr(self.Data, "WeightStorage"):
        self.Data.WeightStorage = create_vis_wgt_storage(filename)
    elif self.Data.WeightStorage is None:
        self.Data.WeightStorage = create_vis_wgt_storage(filename)
    else:
        self.Data.WeightStorage.DataContainer.FileName = filename


def __get_wgt_filename(self):
    if hasattr(self.Data, "WeightStorage"):
        if self.Data.WeightStorage is not None:
            return self.Data.WeightStorage.DataContainer.FileName
    return None


def create_dpd_vis_calibrated_frame(data_filename='default_filename.fits',
                                    bkg_filename=None,
                                    wgt_filename=None):
    """
        @TODO fill in docstring
    """

    dpd_vis_calibrated_frame = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_vis_calibrated_frame.Header = HeaderProvider.createGenericHeader("SHE")

    dpd_vis_calibrated_frame.set_data_filename(dpd_vis_calibrated_frame, data_filename)
    if bkg_filename is not None:
        dpd_vis_calibrated_frame.set_bkg_filename(dpd_vis_calibrated_frame, bkg_filename)
    if wgt_filename is not None:
        dpd_vis_calibrated_frame.set_wgt_filename(dpd_vis_calibrated_frame, wgt_filename)

    return dpd_vis_calibrated_frame


def init_storage(type, filename, format, version, filestatus):

    data_storage = type()

    data_storage.format = format
    data_storage.version = version

    data_storage.DataContainer = dataContainer()
    data_storage.DataContainer.FileName = filename
    data_storage.DataContainer.filestatus = filestatus

    return data_storage


def create_vis_data_storage(filename, format="vis.calibratedFrame", version="0.1", filestatus="PROPOSED"):

    data_storage = init_storage(
        vis_pro.visCalibratedStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_psf_storage(filename, format="vis.psfModel", version="0.1", filestatus="PROPOSED"):

    data_storage = init_storage(
        vis_pro.visPsfModelStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_bkg_storage(filename, format="vis.backgroundMap", version="0.1", filestatus="PROPOSED"):

    data_storage = init_storage(
        vis_pro.visBackgroundStorageFitsFile, filename, format, version, filestatus)

    return data_storage


def create_vis_wgt_storage(filename, format="vis.weightMap", version="0.1", filestatus="PROPOSED"):

    data_storage = init_storage(
        vis_pro.visWeightStorageFitsFile, filename, format, version, filestatus)

    return data_storage
