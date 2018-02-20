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
import EuclidDmBindings.sys.dss_stub as dss_dict

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
    self.Data.PsfModelStorage.DataContainer.FileName = filename

def __get_psf_filename(self):
    return self.Data.PsfModelStorage.DataContainer.FileName

def __set_bkg_filename(self, filename):
    self.Data.BackgroundStorage.DataContainer.FileName = filename

def __get_bkg_filename(self):
    return self.Data.BackgroundStorage.DataContainer.FileName

def __set_wgt_filename(self, filename):
    self.Data.WeightStorage.DataContainer.FileName = filename

def __get_wgt_filename(self):
    return self.Data.WeightStorage.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = [self.get_data_filename(),
                     self.get_psf_filename(),
                     self.get_bkd_filename(),
                     self.get_wgt_filename()]
    
    return all_filenames

def create_dpd_vis_calibrated_frame(filename = None,
                                    psf_filename = None,
                                    bkg_filename = None,
                                    wgt_filename = None):
    """
        @TODO fill in docstring
    """
    
    dpd_vis_calibrated_frame = vis_dpd.DpdCalibratedFrame()
    
    dpd_vis_calibrated_frame.Header = HeaderProvider.createGenericHeader("VIS")
    dpd_vis_calibrated_frame.Header = "VIS"
    
    dpd_vis_calibrated_frame.Data = create_vis_calibrated_frame(filename,
                                                                psf_filename,
                                                                bkg_filename,
                                                                wgt_filename)
    
    return dpd_vis_calibrated_frame

# Add a useful alias
create_calibrated_frame_product = create_dpd_vis_calibrated_frame

def create_vis_calibrated_frame(filename = None,
                                psf_filename = None,
                                bkg_filename = None,
                                wgt_filename = None):
    """
        @TODO fill in docstring
    """
    
    vis_calibrated_frame = vis_pro.calibratedFrameVIS()
    
    vis_calibrated_frame.DataStorage = create_vis_data_storage(filename,"vis.reducedFrameVIS")
    vis_calibrated_frame.PsfModelStorage = create_vis_data_storage(psf_filename,"vis.reducedFrameVIS")
    vis_calibrated_frame.BackgroundStorage = create_vis_data_storage(bkg_filename,"vis.reducedFrameVIS")
    vis_calibrated_frame.WeightStorage = create_vis_data_storage(wgt_filename,"vis.reducedFrameVIS")
    
    vis_calibrated_frame.Masks = create_vis_masks()
    vis_calibrated_frame.DetectorList = create_vis_detector_list()
    vis_calibrated_frame.ObservationSequence = create_vis_observation_sequence()
    
    return
    
def create_vis_data_storage(filename, format="UNDEFINED", version="0.0", filestatus="PROPOSED"):
    
    data_storage = vis_pro.reducedFrameFitsFileVIS()
    
    data_storage.format = format
    data_storage.version = version
    
    data_storage.DataContainer = dss_dict.dataContainer()
    data_storage.DataContainer.FileName = filename
    data_storage.DataContainer.filestatus = filestatus
    
    return data_storage

def create_vis_masks():
    
    masks = vis_pro.bitMaskList()
    
    return masks

def create_vis_detector_list():
    
    detector_list = vis_pro.reducedDetectorFrameListVIS()
    
    return detector_list

def create_vis_observation_sequence():
    
    observation_sequence = vis_pro.observationSequenceVIS()
    
    return observation_sequence
