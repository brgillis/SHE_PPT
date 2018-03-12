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

import EuclidDmBindings.dpd.vis_stub as vis_dpd
import EuclidDmBindings.pro.vis_stub as vis_pro

from EuclidDmBindings.bas.cot_stub import wcs, zeroPoint
from EuclidDmBindings.bas.img_stub import imgSpatialFootprint
from EuclidDmBindings.bas.imp_stub import projectionType
from EuclidDmBindings.bas.imp.eso_stub import dataProduct
from EuclidDmBindings.ins_stub import baseInstrument 
from EuclidDmBindings.pro import le1_stub as le1
from EuclidDmBindings.pro.le1 import vis_stub as le1vis  
from EuclidDmBindings.sys.dss_stub import dataContainer

import HeaderProvider.GenericHeaderProvider as HeaderProvider

def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """
    
    binding_class = vis_dpd.dpdVisStackedFrame

    # Add the data file name methods
    
    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = False
    
    return

def __set_filename(self, filename):
    self.Data.DataContainer.FileName = filename

def __get_filename(self):
    return self.Data.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = []
    
    return all_filenames

def create_dpd_vis_stacked_frame(filename = None):
    """
        @TODO fill in docstring
    """
    
    dpd_vis_stacked_frame = vis_dpd.dpdVisStackedFrame()
    
    dpd_vis_stacked_frame.Header = HeaderProvider.createGenericHeader("VIS")
    
    dpd_vis_stacked_frame.Data = create_vis_stacked_frame(filename)
    
    return dpd_vis_stacked_frame

# Add a useful alias
create_stacked_frame_product = create_dpd_vis_stacked_frame

def create_vis_stacked_frame(filename = None):
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
    
    vis_stacked_frame.DataContainer = dataContainer()
    vis_stacked_frame.DataContainer.FileName = filename
    vis_stacked_frame.DataContainer.filestatus = "PROPOSED"
    
    return vis_stacked_frame

def create_vis_instrument():
    
    instrument = baseInstrument()
    
    instrument.InstrumentName = "VIS Instrument"
    instrument.TelescopeName = "Telescope"
    
    return instrument

def create_vis_wcs():
    
    vis_wcs = wcs()
    
    vis_wcs.CTYPE1 = create_vis_projection_type("RA","SIN")
    vis_wcs.CTYPE2 = create_vis_projection_type("DEC","SIN")
    
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
