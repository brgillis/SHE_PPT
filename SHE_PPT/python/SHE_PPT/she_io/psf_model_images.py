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
:file: python/SHE_PPT/she_io/psf_model_images.py

:date: 15/02/23
:author: Gordon Gibb

"""

import os

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import h5py

from astropy.io import fits
from astropy.table import Table
from astropy.io.misc.hdf5 import read_table_hdf5

import ElementsKernel.Logging as log

from ST_DM_DmUtils.DmUtils import read_product_metadata

from .profiling import io_stats

logger = log.getLogger(__name__)


def read_psf_model_images(psf_prods, workdir="."):
    """
    Reads a list of PSFModelImages data product filenames, returning a list of PSFModelImage objects
    Inputs:
     - psf_prods: list of PSF model image data product filenames
     - workdir: name of the working directory

    Returns:
     - psf_model_images: list of PSFModelImage objects
    """

    datadir = os.path.join(workdir, "data")

    n_exps = len(psf_prods)

    psf_dpds = [read_product_metadata(os.path.join(workdir, p)) for p in psf_prods]

    psf_files = [p.Data.DataStorage.DataContainer.FileName for p in psf_dpds]

    psf_model_images = []
    # Read get the appropriate PSFModelImages object depending on the file extension of the files to be read
    for psf_file in psf_files:
        qualified_psf_file = os.path.join(datadir, psf_file)
        _, ext = os.path.splitext(psf_file)

        if ext in (".h5", ".hdf5"):
            psf_model_images.append(PSFModelImageHDF5(qualified_psf_file))
        elif ext in (".fits"):
            psf_model_images.append(PSFModelImageFITS(qualified_psf_file))
        else:
            raise ValueError("Unknown file extension for psf_model_images file %s" % qualified_psf_file)

    logger.info("Created %d %s objects", n_exps, psf_model_images[-1].__class__.__name__)

    return psf_model_images


@dataclass
class ObjectModelImage:
    """Contains the bulge and disk model images for an object, along with the quality flag"""

    bulge: np.ndarray
    disk: np.ndarray
    quality_flag: np.int32
    # Table row included in case any information from the table is required in future
    table_row: "astropy.table.row.Row"  # noqa: F821


class PSFModelImage(ABC):
    def __init__(self, filename):
        """
        Sets up the class

        Inputs:
          - filename: The qualified filename of the ShePSFModelImage file
        """
        pass

    @abstractmethod
    def get_model_images(self, obj_id):
        """
        Returns the disk and bulge PSF images from the file for the requested object id

        Inputs:
          - obj_id: the object id for the object whose images we wish to extract

        Returns:
          - bulge: The bulge PSF image
          - disk: The disk PSF image
        """
        pass

    def __getitem__(self, obj_id):
        return self.get_model_images(obj_id)


class PSFModelImageFITS(PSFModelImage):
    """Class for interfacing with a psf_model_image fits file"""

    @io_stats
    def __init__(self, filename):

        self.filename = filename

        # No point in memory mapping as we wish to access the whole HDU at once.
        # We do not lazy load HDUs so that the whole file is traversed and the locations/offsets of
        # each HDU is known. This means when we call self.get_model_images (below) it knows where in
        # the FITS file to read from, so doesn't spend time seeking through the file. This means
        # all the time in get_model_images is spent reading the image, not seeking through the FITS
        # to find the data.

        self.hdul = fits.open(filename, memmap=False, lazy_load_hdus=False)

        self.table = Table.read(self.hdul[1])

        # index table by object_id
        self.table.add_index("OBJECT_ID")

    @io_stats
    def get_model_images(self, obj_id):

        try:
            row = self.table.loc[obj_id]
        except KeyError as e:
            raise KeyError("Object %s not present in PSFModelImages file %s" % (obj_id, self.filename)) from e

        bulge_idx = row["SHE_PSF_BULGE_INDEX"]
        disk_idx = row["SHE_PSF_DISK_INDEX"]
        quality_flag = row["SHE_PSF_QUAL_FLAG"]

        bulge = self.hdul[bulge_idx].data
        if disk_idx == bulge_idx:
            disk = bulge
        else:
            disk = self.hdul[disk_idx].data

        return ObjectModelImage(bulge=bulge, disk=disk, quality_flag=quality_flag, table_row=row)


class PSFModelImageHDF5(PSFModelImage):
    """Class for interfacing with a psf_model_image HDF5 file"""

    @io_stats
    def __init__(self, filename):

        self.file = h5py.File(filename, "r")

        # NOTE: We can do Table.read(self.file["TABLE"]) directly but this uses hundreds
        # of read ops... I presume astropy tries everything before defaulting to HDF5.
        # The solution is to explicitly call the hdf5 reader - which uses only handful
        # of read ops :)
        self.table = read_table_hdf5(self.file["TABLE"])

        # index table by object_id
        self.table.add_index("OBJECT_ID")

        # store reference to the IMAGES group
        self.images = self.file["IMAGES"]

        # Get the list of objects in the file
        self.objects = list(self.images.keys())

    @io_stats
    def get_model_images(self, obj_id):

        # a HDF5 dataset's name is a string
        if str(obj_id) not in self.objects:
            raise KeyError("Object %s not present in PSFModelImages file %s" % (obj_id, self.file.filename))

        image = self.images[str(obj_id)][:, :]

        row = self.table.loc[int(obj_id)]

        quality_flag = row["SHE_PSF_QUAL_FLAG"]

        return ObjectModelImage(bulge=image, disk=image, quality_flag=quality_flag, table_row=row)
