"""
File: python/SHE_PPT/she_image_stack.py

Created on: 09/01/17
"""

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

__updated__ = "2021-02-10"

import weakref

from . import logging
from .she_image import SHEImage


logger = logging.getLogger(__name__)


class SHEImageStack():
    """Structure containing a list of SHEImage objects and optionally a stack of them

    Attributes
    ----------
    exposures : list<SHEImage>
        List of SHEImage objects representing the different exposures
    stacked_image : SHEImage
        Stacked image of all exposures

    """

    def __init__(self, exposures, stacked_image=None, x_world=None, y_world=None, parent_frame_stack=None):
        """
        Parameters
        ----------
        exposures : list
            a list of SHEImageData objects representing the different exposures. Any or all may be None
        stacked_image : SHEImage or None
            The stacked image of the exposures (optional)
        x_world : float
            Right Ascension of the centre of this stack, in degrees
        y_world : float
            Declination of the centre of this stack, in degrees
        parent_frame_stack : SHE_PPT.she_frame_stack.SHEFrameStack
            Reference to parent SHEFrameStack object if it exists; None otherwise
        """

        # References to parent objects
        self.parent_frame_stack = parent_frame_stack

        self.exposures = exposures
        self.stacked_image = stacked_image

        self.x_world = x_world
        self.y_world = y_world


    @property
    def parent_frame_stack(self):
        return self._parent_frame_stack()

    @parent_frame_stack.setter
    def parent_frame_stack(self, parent_frame_stack):

        if parent_frame_stack is None:
            self._parent_frame_stack = lambda: None
        else:
            # Use a weak reference so we don't keep the parent alive indefinitely
            self._parent_frame_stack = weakref.ref(parent_frame_stack)

    @parent_frame_stack.deleter
    def parent_frame_stack(self):
        self._parent_frame_stack = lambda: None

    def __eq__(self, rhs):
        """Equality test for SHEImageStack class.
        """

        def neq(lhs, rhs):
            try:
                return bool(lhs != rhs)
            except ValueError:
                return (lhs != rhs).any()

        if neq(self.exposures, rhs.exposures):
            return False
        if neq(self.stacked_image, rhs.stacked_image):
            return False
        if neq(self.x_world, rhs.x_world):
            return False
        if neq(self.y_world, rhs.y_world):
            return False

        return True

    def is_not_empty(self):
        """ Checks if at least one exposure isn't None """

        return not self.is_empty()

    def is_empty(self):
        """ Checks if all exposures are None """

        empty = True
        for exposure in self.exposures:
            if exposure is not None:
                empty = False
                break

        return empty

    @classmethod
    def read(cls, filename_list, stacked_image_filename=None, workdir=".", **kwargs):
        """Reads a SHEImageStack from disk

        This function successively calls SHEImage.read_from_fits() on contents of filename_list.


        Parameters
        ----------
        filename_list : list
            A list of filenames to the FITS files containing SHEImage objects.
        stacked_image_filename : list
            A filename for the FITS file containing the stacked image SHEImage object

        Any kwargs are passed to the reading of the SHEImage
        """

        exposures = []
        for filenames in filename_list:
            exposures.append(SHEImage.read_from_fits(filepath=filenames[0],
                                                     workdir=workdir,
                                                     **kwargs))

        if stacked_image_filename is None:
            stacked_image = None
        else:
            stacked_image = SHEImage.read_from_fits(
                stacked_image_filename, workdir=workdir, **kwargs)

        return SHEImageStack(exposures, stacked_image)
