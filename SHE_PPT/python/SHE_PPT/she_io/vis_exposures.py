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
:file: python/SHE_PPT/io/vis_exposures.py

:date: 15/02/23
:author: Gordon Gibb

"""

import os
import json
import gc

from abc import ABC, abstractmethod

from dataclasses import dataclass

import numpy as np

from astropy.io import fits
from astropy.wcs import WCS

import fitsio
import h5py

import ElementsKernel.Logging as log

from ST_DM_DmUtils.DmUtils import read_product_metadata

from .profiling import io_stats

logger = log.getLogger(__name__)


def read_vis_data(vis_listfile, seg_listfile=None, workdir=".", method="astropy", hdf5_listfile=None):
    """
    Reads listfiles of DpdVisCalibratedFrame (and optionally dpdSheExposureReprojectedSegmentationMap),
    returning a list of VisExposure objects

    Inputs:
     - vis_listfile: a listfile of the vis products
     - seg_listfile: a listfile of the reprojected segmentation map products
     - workdir: the workdir
     - method: the IO method to use... options are astropy, fitsio, hdf5
     - hdf5_listfile: the listfile of hdf5 files to use (only if method == "hdf5")

    returns:
     - vis_exposures: a list of VisExposure objects
    """

    datadir = os.path.join(workdir, "data")

    # Make sure we have a valid method:
    if method not in ("astropy", "fitsio", "hdf5"):
        raise ValueError("VIS IO method %s not know. Choose from %s" % (method, "astropy, fitsio, hdf5"))

    # Regardless of the method, we always need the VIS products
    logger.info("Opening VIS listfile %s", os.path.join(workdir, vis_listfile))

    with open(os.path.join(workdir, vis_listfile), "r") as f:
        vis_prods = json.load(f)
    vis_dpds = [read_product_metadata(os.path.join(workdir, p)) for p in vis_prods]

    n_exps = len(vis_dpds)

    if n_exps == 0:
        raise ValueError("VIS listfile is empty")

    # HDF5 is different to the other two methods as it does not need the FITS files,
    # so deal with this first and return
    if method == "hdf5":
        with open(os.path.join(workdir, hdf5_listfile), "r") as f:
            hdf5_files = json.load(f)

        if len(hdf5_files) != n_exps:
            raise ValueError(
                "HDF5 listfile (len %d) has different length from vis listfile (len %d)" % (len(vis_dpds), n_exps)
            )

        qualified_hdf5_files = [os.path.join(datadir, f) for f in hdf5_files]

        vis_exposures = [VisExposureHDF5(h5, dpd=dpd) for h5, dpd in zip(qualified_hdf5_files, vis_dpds)]

        logger.info("Created %d %s exposures", n_exps, vis_exposures[-1].__class__.__name__)

        return vis_exposures

    # get the FITS files we need to access
    dets = [os.path.join(datadir, p.Data.DataStorage.DataContainer.FileName) for p in vis_dpds]
    wgts = [os.path.join(datadir, p.Data.WeightStorage.DataContainer.FileName) for p in vis_dpds]
    bkgs = [os.path.join(datadir, p.Data.BackgroundStorage.DataContainer.FileName) for p in vis_dpds]

    # get the segmentation FITS file (if provided)
    if seg_listfile:
        with open(os.path.join(workdir, seg_listfile), "r") as f:
            seg_prods = json.load(f)
        seg_dpds = [read_product_metadata(os.path.join(workdir, p)) for p in seg_prods]

        if len(seg_dpds) != len(vis_dpds):
            raise ValueError(
                "Segmentation listfile (len %d) has different length from vis listfile (len %d)"
                % (len(seg_dpds), n_exps)
            )

        segs = [os.path.join(datadir, p.Data.DataStorage.DataContainer.FileName) for p in seg_dpds]
    else:
        segs = [None for _ in range(n_exps)]

    vis_exposures = []
    for det, wgt, bkg, seg, dpd in zip(dets, wgts, bkgs, segs, vis_dpds):
        if method == "astropy":
            exp = VisExposureAstropyFITS(det, bkg, wgt, seg, dpd=dpd)
        else:
            exp = VisExposureFitsIO(det, bkg, wgt, seg, dpd=dpd)

        vis_exposures.append(exp)

    logger.info("Created %d %s exposures", n_exps, vis_exposures[-1].__class__.__name__)

    return vis_exposures


@dataclass
class Detector:
    """Contains the header and wcs for a detector, plus handles to the detector data"""

    header: fits.header
    wcs: WCS
    sci: np.ndarray
    rms: np.ndarray
    flg: np.ndarray
    wgt: np.ndarray
    bkg: np.ndarray
    seg: np.ndarray
    dpd: "DpdVisCalibratedFrame"  # noqa: F821

    def __eq__(self, other):
        if self.header != other.header:
            return False

        if self.wcs.to_header_string() != other.wcs.to_header_string():
            return False

        if not np.array_equal(self.sci[:, :], other.sci[:, :]):
            return False

        if not np.array_equal(self.flg[:, :], other.flg[:, :]):
            return False

        if not np.array_equal(self.rms[:, :], other.rms[:, :]):
            return False

        if not np.array_equal(self.wgt[:, :], other.wgt[:, :]):
            return False

        if not np.array_equal(self.bkg[:, :], other.bkg[:, :]):
            return False

        if not np.array_equal(self.seg[:, :], other.seg[:, :]):
            return False

        return True


class VisExposure(ABC):
    """
    Abstract class allowing access to a VIS exposure's data. The class exposes the following methods:

    - get_wcs_list - returns the list of WCS objects for the detectors associated with this exposure
    - get_header_list - returns the list of headers for the detectors associated with this exposure
    - get_detector - returns a Detector object for the requested detector. Can be indexed by the detector
                     number (0-36) or its id (e.g. "5-5")
    - delete_detector - dereferences a detector object to e.g. free up memory/resources

    The class can also be indexed to get a detector object - e.g exposure["5-5"] or exposure[22]
    Similarly, the detector object can be dereferenced by del(exposure["5-5"]) or del(exposure[22])

    This class is supposed to be agnostic to the method of accessing the data (e.g. astropy.io.fits,
    fitsio, others...) so a subclass must be created that implements data access via the chosen method.
    """

    def __init__(self):
        self._wcs_list = None
        self._header_list = None
        self._detectors = {}
        self.n_detectors = None
        self.dpd = None

    def get_wcs_list(self):
        if not self._wcs_list:
            self._get_wcs_and_header_list()
        return self._wcs_list

    def get_header_list(self):
        if not self._header_list:
            self._get_wcs_and_header_list()
        return self._header_list

    def get_detector(self, det_name):
        if not self._header_list:
            self._get_wcs_and_header_list()
        if det_name not in self._detectors:
            self._create_detector(det_name)

        return self._detectors[det_name]

    def __getitem__(self, item):
        return self.get_detector(item)

    def __len__(self):
        return len(self.get_header_list())

    def delete_detector(self, det_name):
        if det_name in self._detectors:
            det_num, det_id = self._parse_detector_name(det_name)
            logger.info("Deleting detector %d with ID %s", det_num, det_id)
            del self._detectors[det_num]
            del self._detectors[det_id]
        # It can't hurt to garbage collect regardless of whether we have deleted the detector or not
        gc.collect()

    def __delitem__(self, item):
        self.delete_detector(item)

    def _parse_detector_name(self, det_name):
        # detector name can be either its index (0-35) or its id (e.g. "5-3")
        if type(det_name) is int:
            det_num = det_name
            i, j = (det_num // 6) + 1, (det_num % 6) + 1
            det_id = "%d-%d" % (i, j)
        elif type(det_name) is str:
            det_id = det_name
            si, sj = det_name.split("-")
            i, j = int(si) - 1, int(sj) - 1
            det_num = 6 * i + j
        else:
            raise IndexError("Invalid detector name %s" % det_name)

        if det_num >= self.n_detectors:
            raise IndexError("Invalid detector name %s" % det_name)

        return det_num, det_id

    def get_dpd(self):
        return self.dpd

    @abstractmethod
    def _get_wcs_and_header_list(self):
        # OVERRIDE ME
        pass

    @abstractmethod
    def _create_detector(self):
        # OVERRIDE ME
        pass


class VisExposureAstropyFITS(VisExposure):
    """Implementation of the VisExposure class using astropy.io.fits"""

    @io_stats
    def __init__(
        self, det_file, bkg_file=None, wgt_file=None, seg_file=None, load_rms=True, load_flg=True, memmap=True, dpd=None
    ):

        super().__init__()

        self._det_hdul = None
        self._bkg_hdul = None
        self._wgt_hdul = None
        self._seg_hdul = None

        self.sci_hdus = []
        self.rms_hdus = []
        self.flg_hdus = []
        self.bkg_hdus = []
        self.wgt_hdus = []
        self.seg_hdus = []

        self.dpd = dpd

        # open the files

        self._det_hdul = fits.open(det_file, memmap=memmap)

        if bkg_file:
            self._bkg_hdul = fits.open(bkg_file, memmap=memmap)

        if wgt_file:
            self._wgt_hdul = fits.open(wgt_file, memmap=memmap)

        if seg_file:
            self._seg_hdul = fits.open(seg_file, memmap=memmap)

        # parse the HDUs into lists

        self.n_detectors = len(self._det_hdul) // 3

        # files made by SHE_GST lack the empty PrimaryHDU, so have an offset of zero.
        # "proper" files have an empty PrimaryHDU, so have an offset of 1
        offset = len(self._det_hdul) % 3
        if offset == 2:
            raise ValueError("File has an unexpected number of HDUs")

        self.sci_hdus = [hdu for hdu in self._det_hdul[offset::3]]

        if load_rms:
            self.rms_hdus = [hdu for hdu in self._det_hdul[(offset + 1)::3]]

        if load_flg:
            self.flg_hdus = [hdu for hdu in self._det_hdul[(offset + 2)::3]]

        if self._bkg_hdul:
            offset = len(self._bkg_hdul) - self.n_detectors
            self.bkg_hdus = [hdu for hdu in self._bkg_hdul[offset:]]

        if self._wgt_hdul:
            offset = len(self._wgt_hdul) - self.n_detectors
            self.wgt_hdus = [hdu for hdu in self._wgt_hdul[offset:]]

        if self._seg_hdul:
            offset = len(self._seg_hdul) - self.n_detectors
            self.seg_hdus = [hdu for hdu in self._seg_hdul[offset:]]

    @io_stats
    def _get_wcs_and_header_list(self):
        self._header_list = [_correct_header(hdu.header) for hdu in self.sci_hdus]
        self._wcs_list = [WCS(hdr) for hdr in self._header_list]

    @io_stats
    def _create_detector(self, det_name):

        # Make a new class that inherits from np.ndarray.
        # Cutout2D converts all input data to np.ndarray (dtype=float64) unless it is already
        # an instance of this ndarray. This means we cast the HDUs to different dtypes.
        # This class disguises the hdu as an ndarray, allowing it to be used directly by Cutout2D.
        class CCDData(np.ndarray):
            def __new__(cls, hdu):

                shape = tuple(hdu.shape)
                dtype = hdu.dtype

                obj = super().__new__(cls, shape, dtype=dtype, buffer=None, offset=0, strides=None, order=None)
                obj.hdu = hdu

                return obj

            # When indexing this object, we want to index the hdu
            def __getitem__(self, inds):
                return self.hdu[inds]

        det_num, det_id = self._parse_detector_name(det_name)

        # get the data references for the detector object (where available)
        wcs = self._wcs_list[det_num]
        header = self._header_list[det_num]
        sci = CCDData(self.sci_hdus[det_num].data)
        flg = CCDData(self.flg_hdus[det_num].data) if self.flg_hdus else None
        rms = CCDData(self.rms_hdus[det_num].data) if self.rms_hdus else None
        wgt = CCDData(self.wgt_hdus[det_num].data) if self.wgt_hdus else None
        bkg = CCDData(self.bkg_hdus[det_num].data) if self.bkg_hdus else None
        seg = CCDData(self.seg_hdus[det_num].data) if self.seg_hdus else None

        # create the detector object and add it to this class's detector's dictionary
        det = Detector(header=header, wcs=wcs, sci=sci, rms=rms, flg=flg, wgt=wgt, bkg=bkg, seg=seg, dpd=self.dpd)

        self._detectors[det_id] = det
        self._detectors[det_num] = det


class VisExposureFitsIO(VisExposure):
    """Implementation of the VisExposure class using fitsio"""

    @io_stats
    def __init__(self, det_file, bkg_file=None, wgt_file=None, seg_file=None, load_rms=True, load_flg=True, dpd=None):

        super().__init__()

        self._det_hdul = None
        self._bkg_hdul = None
        self._wgt_hdul = None
        self._seg_hdul = None

        self.sci_hdus = []
        self.rms_hdus = []
        self.flg_hdus = []
        self.bkg_hdus = []
        self.wgt_hdus = []
        self.seg_hdus = []

        self.dpd = dpd

        # open the files

        self._det_hdul = fitsio.FITS(
            det_file,
        )

        if bkg_file:
            self._bkg_hdul = fitsio.FITS(
                bkg_file,
            )

        if wgt_file:
            self._wgt_hdul = fitsio.FITS(
                wgt_file,
            )

        if seg_file:
            self._seg_hdul = fitsio.FITS(
                seg_file,
            )

        # parse the HDUs into lists

        self.n_detectors = len(self._det_hdul) // 3

        # files made by SHE_GST lack the empty PrimaryHDU, so have an offset of zero.
        # "proper" files have an empty PrimaryHDU, so have an offset of 1
        offset = len(self._det_hdul) % 3
        if offset == 2:
            raise ValueError("File has an unexpected number of HDUs")

        self.sci_hdus = [hdu for hdu in self._det_hdul[offset::3]]

        if load_rms:
            self.rms_hdus = [hdu for hdu in self._det_hdul[(offset + 1)::3]]

        if load_flg:
            self.flg_hdus = [hdu for hdu in self._det_hdul[(offset + 2)::3]]

        if self._bkg_hdul:
            offset = len(self._bkg_hdul) - self.n_detectors
            self.bkg_hdus = [hdu for hdu in self._bkg_hdul[offset:]]

        if self._wgt_hdul:
            offset = len(self._wgt_hdul) - self.n_detectors
            self.wgt_hdus = [hdu for hdu in self._wgt_hdul[offset:]]

        if self._seg_hdul:
            offset = len(self._seg_hdul) - self.n_detectors
            self.seg_hdus = [hdu for hdu in self._seg_hdul[offset:]]

    @io_stats
    def _get_wcs_and_header_list(self):
        self._header_list = [_fitsio_to_astropy_header(hdu.read_header()) for hdu in self.sci_hdus]
        self._wcs_list = [WCS(hdr) for hdr in self._header_list]

    @io_stats
    def _create_detector(self, det_name):

        # Make a new class that inherits from np.ndarray.
        # Cutout2D converts all input data to np.ndarray unless it is already an instance
        # of this class. Numpy doesn't convert the fitsio.ImageHDU properly, breaking Cutout2D.
        # This class disguises the hdu as an ndarray, allowing it to be used directly.
        class CCDData(np.ndarray):
            def __new__(cls, hdu):

                shape = tuple(hdu.get_dims())
                dtype = hdu._get_image_numpy_dtype()

                obj = super().__new__(cls, shape, dtype=dtype, buffer=None, offset=0, strides=None, order=None)
                obj.hdu = hdu

                return obj

            # When indexing this object, we want to index the hdu
            def __getitem__(self, inds):
                return self.hdu[inds]

        det_num, det_id = self._parse_detector_name(det_name)

        # get the data references for the detector object (where available)
        wcs = self._wcs_list[det_num]
        header = self._header_list[det_num]
        sci = CCDData(self.sci_hdus[det_num])
        flg = CCDData(self.flg_hdus[det_num]) if self.flg_hdus else None
        rms = CCDData(self.rms_hdus[det_num]) if self.rms_hdus else None
        wgt = CCDData(self.wgt_hdus[det_num]) if self.wgt_hdus else None
        bkg = CCDData(self.bkg_hdus[det_num]) if self.bkg_hdus else None
        seg = CCDData(self.seg_hdus[det_num]) if self.seg_hdus else None

        # create the detector object and add it to this class's detector's dictionary
        det = Detector(header=header, wcs=wcs, sci=sci, rms=rms, flg=flg, wgt=wgt, bkg=bkg, seg=seg, dpd=self.dpd)

        self._detectors[det_id] = det
        self._detectors[det_num] = det


class VisExposureHDF5(VisExposure):
    """Implementation of the VisExposure class using HDF5"""

    @io_stats
    def __init__(self, exposure_file, chunk_cache_mb=8, dpd=None):
        super().__init__()

        # Open the file, with a chunk cache of chunk_cache_mb
        # NOTE This is the cache per dataset, so if we were to open all datasets per exposure
        # this would be: 6 dataset per CCD x 36 CCDs x 8MB cache = 1728 MB
        self.file = h5py.File(exposure_file, "r", rdcc_nbytes=(1024 * 1024 * chunk_cache_mb))

        det_list_json = self.file.attrs["det_list"]
        self.det_list = json.loads(det_list_json)

        self.n_detectors = len(self.det_list)

        self.dpd = dpd

    @io_stats
    def _get_wcs_and_header_list(self):
        headers_json = self.file.attrs["header_list"]
        headers_str_list = json.loads(headers_json)

        self._header_list = [_correct_header(fits.Header.fromstring(hdr_str)) for hdr_str in headers_str_list]
        self._wcs_list = [WCS(header) for header in self._header_list]

    @io_stats
    def _create_detector(self, det_name):
        det_num, det_id = self._parse_detector_name(det_name)

        try:
            detector_group = self.file[det_id]
        except Exception as e:
            raise e

        # Make a new class that inherits from np.ndarray for the dataset
        # Cutout2D converts all input data to np.ndarray unless it is already an instance
        # of this class. This means it reads the whole dataset in and converts it. This
        # class wraps it into an np.ndarray, preventing this conversion.
        class CCDData(np.ndarray):
            def __new__(cls, dataset):

                shape = dataset.shape
                dtype = dataset.dtype

                obj = super().__new__(cls, shape, dtype=dtype, buffer=None, offset=0, strides=None, order=None)
                obj.dataset = dataset

                return obj

            # When indexing this object, we want to index the dataset
            def __getitem__(self, inds):
                return self.dataset[inds]

        wcs = self._wcs_list[det_num]
        header = self._header_list[det_num]
        sci = CCDData(detector_group["sci"])
        flg = CCDData(detector_group["flg"])
        rms = CCDData(detector_group["rms"])
        bkg = CCDData(detector_group["bkg"])
        wgt = CCDData(detector_group["wgt"])
        seg = CCDData(detector_group["seg"])

        # create the detector object and add it to this class's detector's dictionary
        det = Detector(header=header, wcs=wcs, sci=sci, rms=rms, flg=flg, wgt=wgt, bkg=bkg, seg=seg, dpd=self.dpd)

        self._detectors[det_id] = det
        self._detectors[det_num] = det


def _correct_header(hdr):
    """Corrects strings in headers that may be shorter than 8 chars"""
    cards = []
    for c in hdr.cards:
        if type(c.value) is str:
            if len(c.value) < 8:
                c.value = "%-8s" % c.value
        card = fits.Card(keyword=c.keyword, value=c.value, comment=c.comment)
        cards.append(card)
    new_hdr = fits.Header(cards)
    return new_hdr


def _fitsio_to_astropy_header(hdr):
    """Converts a fitsio header to an astropy.fits.Header"""
    cards = []
    for record in hdr.records():
        keyword = record["name"]
        value = record["value"]
        comment = record["comment"]

        card = fits.Card(keyword, value, comment)
        card.verify()
        cards.append(card)
    return fits.Header(cards)
