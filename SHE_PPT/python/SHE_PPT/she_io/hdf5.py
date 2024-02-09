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
:file: python/SHE_PPT/she_io/hdf5.py

:date: 13/10/22
:author: Gordon Gibb

"""


import os
from astropy.io import fits
from astropy.wcs import WCS

import h5py
import json

import ElementsKernel.Logging as log

from .profiling import io_stats

logger = log.getLogger(__name__)


def convert_to_hdf5(det_file, bkg_file, wgt_file, seg_file, output_filename, chunk=None):
    """
    Converts a set of FITS files corresponding to a VIS exposure to a HDF5 file

    Inputs:
      - det_file: The DET VIS FITS filename
      - bkg_file: The BKG VIS FITS filename
      - wgt_file: The WGT VIS FITS filename
      - seg_file: The reprojected segmentation map FITS filename
      - output_filename: The name of the created hdf5 file
      - chunk: [optional] whether to chunk the file or not. If chunking is requested, this should be a tuple
        of integers denoting the chunk size

    """

    if os.path.exists(output_filename):
        logger.warning("Output file %s exists. This will be overwritten!", output_filename)

    if chunk is None:
        logger.info("No chunking will be applied to the output file")
    else:
        logger.info("Using chunks of size %s in the output file", chunk)

    # open the FITS files
    # Do not memory map. We read a detector in one at a time and convert it. Memory mapping only slows this down
    logger.info("Opening %s", det_file)
    det_hdul = fits.open(det_file, memmap=False)
    logger.info("Opening %s", bkg_file)
    bkg_hdul = fits.open(bkg_file, memmap=False)
    logger.info("Opening %s", seg_file)
    seg_hdul = fits.open(seg_file, memmap=False)
    logger.info("Opening %s", wgt_file)
    wgt_hdul = fits.open(wgt_file, memmap=False)

    # get the number of detectors
    n_hdu = len(det_hdul)
    n_det = n_hdu // 3

    # get the hdu lists for each detector
    offset = n_hdu % 3
    sci_list = [hdu for hdu in det_hdul[offset::3]]
    rms_list = [hdu for hdu in det_hdul[(offset + 1)::3]]
    flg_list = [hdu for hdu in det_hdul[(offset + 2)::3]]

    offset = len(bkg_hdul) - n_det
    bkg_list = [hdu for hdu in bkg_hdul[offset:]]

    offset = len(wgt_hdul) - n_det
    wgt_list = [hdu for hdu in wgt_hdul[offset:]]

    offset = len(seg_hdul) - n_det
    seg_list = [hdu for hdu in seg_hdul[offset:]]

    assert len(sci_list) == len(rms_list) == len(flg_list) == n_det

    detector_names = []
    if n_det == 36:
        for k in range(n_det):
            i = k // 6 + 1
            j = k % 6 + 1
            name = "%d-%d" % (i, j)
            detector_names.append(name)
    elif n_det == 144:
        for k in range(n_det):
            i = (k // 4) // 6 + 1
            j = (k // 4) % 6 + 1
            q = k % 4
            sq = {0: "E", 1: "F", 2: "G", 3: "H"}[q]
            name = "%d-%d.%s" % (i, j, sq)
            detector_names.append(name)
    else:
        raise ValueError("Invalid number of detector %s" % n_det)

    wcs_list = [WCS(sci.header) for sci in sci_list]

    # create the HDF5 file
    logger.info("Opening the output file %s", output_filename)
    h = h5py.File(output_filename, "w")

    h.attrs["header"] = det_hdul[0].header.tostring()

    # save structured information (lists, headers, WCSs) as json strings in the attributes
    h.attrs["det_list"] = json.dumps(detector_names)

    wcs_str_list = [w.to_header_string() for w in wcs_list]
    h.attrs["wcs_list"] = json.dumps(wcs_str_list)

    header_list = [hdu.header.tostring() for hdu in sci_list]
    h.attrs["header_list"] = json.dumps(header_list)

    logger.info("Set the detector, header and wcs list attributes")

    logger.info(detector_names)
    # make the datasets
    for name, sci, rms, flg, wgt, bkg, seg, wcs in zip(
        detector_names, sci_list, rms_list, flg_list, wgt_list, bkg_list, seg_list, wcs_list
    ):

        @io_stats
        def create_dataset_from_hdu(group, name, hdu, chunk):
            ds = group.create_dataset(name, data=hdu.data, chunks=chunk)
            ds.attrs["header"] = hdu.header.tostring()

            logger.info("Created dataset %s", ds.name)

            # ensure the HDU's data is cleaned up by the garbage collector
            del hdu.data

            return ds

        logger.info("Creating group %s", name)
        g = h.create_group(name)
        g.attrs["wcs"] = wcs.to_header_string()

        create_dataset_from_hdu(g, "sci", sci, chunk)
        create_dataset_from_hdu(g, "rms", rms, chunk)
        create_dataset_from_hdu(g, "flg", flg, chunk)
        create_dataset_from_hdu(g, "wgt", wgt, chunk)
        create_dataset_from_hdu(g, "bkg", bkg, chunk)
        create_dataset_from_hdu(g, "seg", seg, chunk)

    logger.info("Closing the output file %s", output_filename)
    h.close()
