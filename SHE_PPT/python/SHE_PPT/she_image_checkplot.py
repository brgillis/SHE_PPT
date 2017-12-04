#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
File: python/SHE_PPT/she_image_checkplot.py

Created on: 10/19/17
Author: Malte Tewes
"""


from future_builtins import *

import os

from . import sky_image_plot as sip

from . import logging
logger = logging.getLogger(__name__)




def draw_to_axes(img, ax, z1=None, z2=None, **kwargs):
    """Visualizes a SHEImage using Matplotlib on some existing Matplotlib axes
    
    This function implements a simple default style for plotting a SHEImage on some existing axes, and can therefore
    be used to make figures with subplots etc.
    
    If instead you want to create a Figure, use the Checkplot class below.
    (It will call the same code in the present function to draw)
    
    Parameters
    ----------
    img : SHEImage
        The SHEImage to draw
    ax : Matplotlib Axes
        Axes on which to plot the image.
    z1 : float or string
        The lower bound for the z-scaling. Default (None) uses the minimum value. Set it to "auto" to use an automatic
        algorithm to set its value based upon an analysis of the image.
    z2 :
        idem for the upper bound.
    """
       
    # Make a SkyImage object with the data
    skyimage = sip.SkyImage(img.data, z1, z2)
    sip.draw_sky_image(ax, skyimage)    
    sip.draw_mask(ax, img.boolmask)
    
    
    
class Checkplot(sip.SimpleFigure):
    """Visualizes a SHEImage using Matplotlib in a simple standalone figure
    
    """
    def __init__(self, img, **kwargs):
        
        self.sheimage = img
        sip.SimpleFigure.__init__(self, img.data, **kwargs)
        
    
    def draw(self, **kwargs):
        """
        
        """
        draw_to_axes(self.sheimage, self.ax, self.z1, self.z2, **kwargs)





