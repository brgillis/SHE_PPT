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

from astropy.io.misc.hdf5 import read_table_hdf5
from astropy.table import Table, Column

import ElementsKernel.Logging as log

from ST_DM_DmUtils.DmUtils import read_product_metadata

from SHE_PPT.flags import flag_psf_quality_good, flag_psf_quality_invalid
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
        psf_model_images.append(PSFModelImageHDF5(qualified_psf_file))

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
        Returns an ObjectModelImage object containing the disk and bulge PSF images for the requested object id

        Inputs:
          - obj_id: the object id for the object whose images we wish to extract

        Returns:
          - bulge: The bulge PSF image
          - disk: The disk PSF image
        """
        pass

    @abstractmethod
    def get_oversampling_factor(self):
        """
        Returns the oversampling factor for the PSF model images
        """
        pass

    def __getitem__(self, obj_id):
        return self.get_model_images(obj_id)


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

    def get_oversampling_factor(self):
        try:
            return self.file.attrs["PSF_OVERSAMPLING_FACTOR"]
        except KeyError as e:
            raise KeyError("PSF oversampling factor is not present in this file") from e


class PSFModelImagesWriter():
    """Class to create PSFModelImage HDF5 files"""
    def __init__(self, object_ids, filename, oversampling_factor):
        """
        Initialises the PSFWriter class:
          - opens the PSFModelImages file
          - creates the table of objects

        Inputs:
          - object_ids: list of object_ids we wish to store in this file.
          - filename: the name of the file to write to
          - oversampling_factor - the oversampling factor for the PSFs
        """

        self.filename = filename

        logger.info("Initialised PSF writer to write PSFModelImages to %s", self.filename)

        self.hdf5_root = h5py.File(self.filename, "w")

        self.hdf5_image_group = self.hdf5_root.create_group("IMAGES")

        self.hdf5_root.attrs["PSF_OVERSAMPLING_FACTOR"] = oversampling_factor

        n_objs = len(object_ids)

        # Initialise the PSF table (with masked columns for FOV as these may not be present for all objects)
        self.psf_table = Table(
            [
                Column(name="OBJECT_ID", data=object_ids),
                Column(name="FOV_X", data=np.full(n_objs, np.nan)),
                Column(name="FOV_Y", data=np.full(n_objs, np.nan)),
                Column(name="SHE_PSF_QUAL_FLAG", data=np.full(n_objs, flag_psf_quality_invalid)),
                Column(name="MODELLED", data=np.full(n_objs, False)),
                Column(name="E1", data=np.full(n_objs, np.nan)),
                Column(name="E2", data=np.full(n_objs, np.nan)),
                Column(name="R", data=np.full(n_objs, np.nan)),
            ]
        )
        self.psf_table.add_index("OBJECT_ID")

        # create the null dataset for objects without PSFs (e.g. objects not in this exposure)
        # This is used as a placeholder dataset for all objects not modelled
        self.null_dataset = self.hdf5_image_group.create_dataset(
            "NULL",
            data=np.zeros((0, 0)),
        )

        self._finalised = False

    def _check_finalised(self):
        if self._finalised:
            raise RuntimeError("This PSFWriter object is finalised!")

    def write_psf(self, obj_id, psf, fov_coords=None, ellipticity=None, r=None, quality_flag=flag_psf_quality_good):
        """
        Writes the supplied psf for a given object to the file.

        Inputs:
          - obj_id: the object id of the object (must be an object in the object_ids passed in during __init__)
          - psf: the PSF image
          - fov_coords: a tuple of the x and y FOV coords
          - ellipticity: a tuple of e1, e2 for the PSF
          - r: the PSF size
          - quality_flag: quality flag for the PSF
        """

        self._check_finalised()

        # NOTE: we use compression to save disk space (around 40%). This requires chunking.
        # A chunk size of 160 is chosen as this is the default size of a un-oversampled PSF,
        # such that we will always have an integer number of chunks in each direction.
        # We want a relatively large chunksize to minimize read/write operations.
        self.hdf5_image_group.create_dataset(
            str(obj_id),
            data=psf,
            chunks=(160, 160),
            compression="gzip"
        )

        try:
            row = self.psf_table.loc[obj_id]
        except KeyError as e:
            raise KeyError(f"Unexpected object id {obj_id}: not in table of objects") from e

        row["SHE_PSF_QUAL_FLAG"] = quality_flag

        row["MODELLED"] = True

        if fov_coords:
            x, y = fov_coords
            row["FOV_X"] = x
            row["FOV_Y"] = y

        if ellipticity:
            e1, e2 = ellipticity
            row["E1"] = e1
            row["E2"] = e2

        if r:
            row["R"] = r

    def close(self):
        """
        Writes necessary bookkeeping data to the hdf5 file and closes it.

        Returns:
         - filename: The filename of the created HDF5 file
        """

        self._check_finalised()

        # For all objects not modelled, link them to the null dataset
        for row in self.psf_table:
            if not row["MODELLED"]:
                obj_id = str(row["OBJECT_ID"])
                self.hdf5_image_group[obj_id] = self.null_dataset

        # Write the table to the file
        self.psf_table.write(self.hdf5_root, "TABLE")

        self.hdf5_root.close()

        self._finalised = True

        logger.info("Written PSFModelImages to %s", self.filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
