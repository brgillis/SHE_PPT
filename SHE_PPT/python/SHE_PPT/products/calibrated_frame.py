""" @file calibrated_frame_product.py

    Created 17 Nov 2017

    Functions to create and output a calibrated_frame data product.
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


# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as vis_dpd # FIXME

import EuclidDmBindings.dpd.vis_stub as vis_dpd
import EuclidDmBindings.pro.vis_stub as vis_pro

from EuclidDmBindings.sys.dss_stub import dataContainer
from EuclidDmBindings.bas.imp.eso_stub import dataProduct
from EuclidDmBindings.ins_stub import baseInstrument 
from EuclidDmBindings.pro import le1_stub as le1
from EuclidDmBindings.pro.le1 import vis_stub as le1vis  


import HeaderProvider.GenericHeaderProvider as HeaderProvider

def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """
    
    binding_class = vis_dpd.DpdCalibratedFrame

    # Add the data file name methods
    
    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename
    
    binding_class.set_psf_filename = __set_psf_filename
    binding_class.get_psf_filename = __get_psf_filename
    
    binding_class.set_bkg_filename = __set_bkg_filename
    binding_class.get_bkg_filename = __get_bkg_filename
    
    binding_class.set_wgt_filename = __set_wgt_filename
    binding_class.get_wgt_filename = __get_wgt_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = True
    
    return

def __set_data_filename(self, filename):
    self.Data.DataStorage.DataContainer.FileName = filename

def __get_data_filename(self):
    return self.Data.DataStorage.DataContainer.FileName

def __set_psf_filename(self, filename):
    if not hasattr(self.Data, "PsfModelStorage"):
        self.Data.PsfModelStorage = create_vis_data_storage(filename)
    else:
        self.Data.PsfModelStorage.DataContainer.FileName = filename

def __get_psf_filename(self):
    if hasattr(self.Data, "PsfModelStorage"):
        return self.Data.PsfModelStorage.DataContainer.FileName
    return None

def __set_bkg_filename(self, filename):
    if not hasattr(self.Data, "BackgroundStorage"):
        self.Data.BackgroundStorage = create_vis_data_storage(filename)
    else:
        self.Data.BackgroundStorage.DataContainer.FileName = filename

def __get_bkg_filename(self):
    if hasattr(self.Data, "BackgroundStorage"):
        return self.Data.BackgroundStorage.DataContainer.FileName
    else:
        return None

def __set_wgt_filename(self, filename):
    if not hasattr(self.Data, "WeightStorage"):
        self.Data.WeightStorage = create_vis_data_storage(filename)
    else:
        self.Data.WeightStorage.DataContainer.FileName = filename

def __get_wgt_filename(self):
    if hasattr(self.Data, "WeightStorage"):
        return self.Data.WeightStorage.DataContainer.FileName
    else:
        return None

def __get_all_filenames(self):
    
    all_filenames = [self.get_data_filename(),
                     self.get_psf_filename(),
                     self.get_bkd_filename(),
                     self.get_wgt_filename()]
    
    return all_filenames

def create_dpd_vis_calibrated_frame(filename = None):
    """
        @TODO fill in docstring
    """
    
    dpd_vis_calibrated_frame = vis_dpd.dpdCalibratedFrame()
    
    dpd_vis_calibrated_frame.Header = HeaderProvider.createGenericHeader("VIS")
    dpd_vis_calibrated_frame.Header = "VIS"
    
    dpd_vis_calibrated_frame.Data = create_vis_calibrated_frame(filename)
    
    return dpd_vis_calibrated_frame

# Add a useful alias
create_calibrated_frame_product = create_dpd_vis_calibrated_frame

def create_vis_calibrated_frame(filename = None):
    """
        @TODO fill in docstring
    """
    
    vis_calibrated_frame = vis_pro.calibratedFrameVIS()
    
    # Attributes inherited from imgBaseFrame
    
    vis_calibrated_frame.ImgType = create_img_type()
    vis_calibrated_frame.ImgNumber = 36
    vis_calibrated_frame.AxisNumber = 2
    vis_calibrated_frame.AxisLengths = (4096,4132)
    vis_calibrated_frame.DataSize = -32
    vis_calibrated_frame.DataLength = 4096*4132
    
    # Attributes inherited from baseFrameVis
    
    vis_calibrated_frame.Instrument = create_vis_instrument()
    vis_calibrated_frame.Filter = "VIS"
    vis_calibrated_frame.InstrumentMode = "Science"
    vis_calibrated_frame.ObservationMode = "ScienceWide"
    vis_calibrated_frame.ReconsOrbit = create_vis_recons_orbit()
    vis_calibrated_frame.Readout = create_vis_readout()
    vis_calibrated_frame.ShutterUnit = create_vis_shutter_unit()
    vis_calibrated_frame.CalibUnit = create_vis_calib_unit()
    vis_calibrated_frame.ChargedInduced = create_vis_charged_induced()
    
    # Attributes unique to calibratedFrameVis
    
    vis_calibrated_frame.DataStorage = create_vis_data_storage(filename,"vis.reducedFrameVIS")
    
    return

def create_img_type():
    
    img_type = dataProduct()
    
    img_type.Category = "SCIENCE"
    img_type.FirstType = "OBJECT"
    img_type.SecondType = "SKY"
    img_type.ThirdType = "WIDE"
    img_type.Technique = "IMAGE"
    
    return img_type

def create_vis_instrument():
    
    instrument = baseInstrument()
    
    instrument.InstrumentName = "VIS Instrument"
    instrument.TelescopeName = "Telescope"
    
    return instrument

def create_vis_recons_orbit():
    
    recons_orbit = le1.spacecraftOrbit()
    
    recons_orbit.Position = (999.0,999.0,999.0)
    recons_orbit.Velocity = (999.0,999.0,999.0)
    recons_orbit.SolarAspectAngle = 999.0
    
    return recons_orbit

def create_vis_readout():
    
    readout = le1vis.visReadoutMode()
    
    readout.ReadoutModeMethod = "NominalScience"
    readout.StartTime = "2006-05-05T18:00:00"
    readout.ParallelRegFrequency = 999.0
    readout.SerialRegFrequency = 999.0
    
    return readout

def create_vis_shutter_unit():
    
    shutter_unit = le1vis.shutterUnit()

    shutter_unit.Status = "OPENED"
    
    return shutter_unit

def create_vis_calib_unit():
    
    calib_unit = le1.calibUnit()
    
    calib_unit.Status = False
    
    return calib_unit

def create_vis_charged_induced():
    
    charged_induced = le1vis.chargedInduced()
    
    charged_induced.Status = False
    charged_induced.IntensityLevel = 999.0
    
    return
    
def create_vis_data_storage(filename, format="vis.reducedFrameVIS", version="0.0", filestatus="PROPOSED"):
    
    data_storage = vis_pro.reducedFrameFitsFileVIS()
    
    data_storage.format = format
    data_storage.version = version
    
    data_storage.DataContainer = dss_dict.dataContainer()
    data_storage.DataContainer.FileName = filename
    data_storage.DataContainer.filestatus = filestatus
    
    return data_storage
