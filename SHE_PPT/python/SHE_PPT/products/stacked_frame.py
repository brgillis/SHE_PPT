""" @file stacked_frame_product.py

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from EuclidDmBindings.bas.cot_stub import wcs, zeroPoint
from EuclidDmBindings.bas.img_stub import imgSpatialFootprint
from EuclidDmBindings.bas.imp.eso_stub import dataProduct
from EuclidDmBindings.bas.imp_stub import projectionType
import EuclidDmBindings.dpd.vis_stub as vis_dpd
from EuclidDmBindings.ins_stub import baseInstrument
from EuclidDmBindings.pro import le1_stub as le1
from EuclidDmBindings.pro.le1 import vis_stub as le1vis
import EuclidDmBindings.pro.vis_stub as vis_pro
from EuclidDmBindings.sys.dss_stub import dataContainer
import HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT.products.calibrated_frame import create_vis_data_storage


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = vis_dpd.dpdVisStackedFrame

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
        self.Data.PsfModelStorage = create_vis_data_storage(filename)
    elif self.Data.PsfModelStorage is None:
        self.Data.PsfModelStorage = create_vis_data_storage(filename)
    else:
        self.Data.PsfModelStorage.DataContainer.FileName = filename

def __get_psf_filename(self):
    if hasattr(self.Data, "PsfModelStorage"):
        if self.Data.PsfModelStorage is not None:
            return self.Data.PsfModelStorage.DataContainer.FileName
    return None

def __set_bkg_filename(self, filename):
    if not hasattr(self.Data, "BackgroundStorage"):
        self.Data.BackgroundStorage = create_vis_data_storage(filename)
    elif self.Data.BackgroundStorage is None:
        self.Data.BackgroundStorage = create_vis_data_storage(filename)
    else:
        self.Data.BackgroundStorage.DataContainer.FileName = filename

def __get_bkg_filename(self):
    if hasattr(self.Data, "BackgroundStorage"):
        if self.Data.BackgroundStorage is not None:
            return self.Data.BackgroundStorage.DataContainer.FileName
    return None

def __set_wgt_filename(self, filename):
    if not hasattr(self.Data, "WeightStorage"):
        self.Data.WeightStorage = create_vis_data_storage(filename)
    elif self.Data.WeightStorage is None:
        self.Data.WeightStorage = create_vis_data_storage(filename)
    else:
        self.Data.WeightStorage.DataContainer.FileName = filename

def __get_wgt_filename(self):
    if hasattr(self.Data, "WeightStorage"):
        if self.Data.WeightStorage is not None:
            return self.Data.WeightStorage.DataContainer.FileName
    return None

def create_dpd_vis_stacked_frame(filename = "default_filename"):
    """
        @TODO fill in docstring
    """

    dpd_vis_stacked_frame = vis_dpd.dpdVisStackedFrame()

    dpd_vis_stacked_frame.Header = HeaderProvider.createGenericHeader("VIS")

    dpd_vis_stacked_frame.Data = create_vis_stacked_frame(filename)

    return dpd_vis_stacked_frame

# Add a useful alias
create_stacked_frame_product = create_dpd_vis_stacked_frame

def create_vis_stacked_frame(filename = "default_filename"):
    """
        @TODO fill in docstring
    """

    vis_stacked_frame = vis_pro.visStackedFrame()

    # Attributes inherited from baseFrameVis

    vis_stacked_frame.Instrument = create_vis_instrument()
    vis_stacked_frame.Filter = "VIS"
    vis_stacked_frame.WCS = create_vis_wcs()
    vis_stacked_frame.ZeroPoint = create_vis_zeropoint()
    vis_stacked_frame.ImgSpatialFootprint = None

    # Attributes unique to visStackedFrame

    vis_stacked_frame.format = "UNDEFINED"
    vis_stacked_frame.version = "0.0"

    vis_stacked_frame.DataStorage = create_vis_data_storage(filename)

    return vis_stacked_frame

def create_vis_instrument():

    instrument = baseInstrument()

    instrument.InstrumentName = "VIS Instrument"
    instrument.TelescopeName = "Telescope"

    return instrument

def create_vis_wcs():

    vis_wcs = wcs()

    vis_wcs.CTYPE1 = create_vis_projection_type("RA", "SIN")
    vis_wcs.CTYPE2 = create_vis_projection_type("DEC", "SIN")

    vis_wcs.CRVAL1 = 3.0
    vis_wcs.CRVAL2 = 4.0
    vis_wcs.CRPIX1 = 3.0
    vis_wcs.CRPIX2 = 3.0

    vis_wcs.CD1_1 = 3.0
    vis_wcs.CD1_2 = 3.0
    vis_wcs.CD2_1 = 3.0
    vis_wcs.CD2_2 = 3.0

    return vis_wcs

def create_vis_projection_type(CoordinateType, ProjectionType):

    projection_type = projectionType()

    projection_type.CoordinateType = CoordinateType
    projection_type.ProjectionType = ProjectionType

    return projection_type

def create_vis_zeropoint():

    zeropoint = zeroPoint()

    zeropoint.Value = 23.9
    zeropoint.Error = 0.029

    return zeropoint

def create_vis_data_storage(filename, format = "vis.reducedFrameVIS", version = "0.0", filestatus = "PROPOSED"):

    data_storage = vis_pro.reducedFrameFitsFileVIS()

    data_storage.format = format
    data_storage.version = version

    data_storage.DataContainer = dataContainer()
    data_storage.DataContainer.FileName = filename
    data_storage.DataContainer.filestatus = filestatus

    return data_storage
