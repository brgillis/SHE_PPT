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
:file: tests/python/vis_exposures_test.py

:date: 08/11/22
:author: Gordon Gibb
"""

import pytest
import os
import json

from SHE_PPT.she_io.vis_exposures import (
    VisExposureAstropyFITS,
    VisExposureFitsIO,
    VisExposureHDF5,
    Detector,
    read_vis_data,
)

# NOTE the file conftest.py contains the pytest fixtures used by this test


def verify_exposure(exp):
    """Verifies the API of the VisExposure class"""
    n_detectors = len(exp)

    hdr_list = exp.get_header_list()
    assert len(hdr_list) == n_detectors, "Length of detector list does not match number of exposures"

    wcs_list = exp.get_wcs_list()
    assert len(wcs_list) == n_detectors, "Length of WCS list does not match number of exposures"

    # make sure we can retrieve all the detectors
    for i in range(n_detectors):
        det = exp[i]

        assert type(det) is Detector, "Detector object is an unexpected type"

    # make sure a IndexError is thrown if we try to extract an invalid detector ID
    with pytest.raises(IndexError):
        det = exp[n_detectors]

    # make sure we can iterate through detectors:
    for i, det in enumerate(exp):
        pass

    assert i + 1 == len(exp), "iterated through exposure, but got an unexpected number of iterations: %d vs %d" % (
        i + 1,
        len(exp),
    )


def verify_all_exposure_types(workdir, fits_files, hdf5_file, n_detectors, quadrants):
    """Verifies that VisExposureAstropyFits, VisExposureFitsIO and VisExposureHDF5 all give the same outputs"""
    # Get the filenames of the FITS/HDF5 input files

    det, wgt, bkg, _, _, seg = fits_files

    hdf5_file = os.path.join(workdir, hdf5_file)

    det_file = os.path.join(workdir, "data", det)
    wgt_file = os.path.join(workdir, "data", wgt)
    bkg_file = os.path.join(workdir, "data", bkg)
    seg_file = os.path.join(workdir, "data", seg)

    # make the VisExposure objects (one per IO method)

    exp_astropy = VisExposureAstropyFITS(det_file, bkg_file, wgt_file, seg_file)
    verify_exposure(exp_astropy)

    exp_fitsio = VisExposureFitsIO(det_file, bkg_file, wgt_file, seg_file)
    verify_exposure(exp_fitsio)

    exp_hdf5 = VisExposureHDF5(hdf5_file)
    verify_exposure(exp_hdf5)

    assert quadrants is exp_astropy.quadrant_based
    assert quadrants is exp_fitsio.quadrant_based
    assert quadrants is exp_hdf5.quadrant_based

    assert len(exp_astropy) == n_detectors
    assert (
        len(exp_hdf5) == len(exp_astropy) == len(exp_fitsio)
    ), "astropy, fitsio and HDF5 VisExposure objects have different number of detectors"

    # make sure the detectors for all 3 objects are the same
    for i in range(n_detectors):
        det_astropy = exp_astropy[i]
        det_fitsio = exp_fitsio[i]
        det_hdf5 = exp_hdf5[i]

        # Check the names are correct
        assert det_astropy.number == i
        hdr = det_astropy.header
        det_name = hdr["CCDID"]
        if "QUADID" in hdr:
            det_name += f".{hdr['QUADID']}"
        assert det_astropy.name == det_name

        assert det_astropy == det_fitsio
        assert det_astropy == det_hdf5

    # Check for uniqueness of detector names and IDs
    # NOTE: we only need to check one of the exposure objects as above we asserted that they are all equal
    names = [det.name for det in exp_astropy]
    numbers = [det.number for det in exp_astropy]
    assert len(names) == len(set(names))
    assert len(numbers) == len(set(numbers))


def verify_read_vis_data(workdir, input_products, hdf5_listfile):
    vis_listfile, _, _, seg_listfile, _ = input_products

    # Read listfiles
    with open(os.path.join(workdir, vis_listfile)) as fs:
        vis_prods = json.load(fs)
    with open(os.path.join(workdir, seg_listfile)) as fs:
        seg_prods = json.load(fs)
    with open(os.path.join(workdir, hdf5_listfile)) as fs:
        hdf5_files = json.load(fs)

    # check astropy
    exps = read_vis_data(vis_prods=vis_prods, seg_prods=seg_prods, workdir=workdir, method="astropy")
    for exp in exps:
        assert type(exp) is VisExposureAstropyFITS

    # check fitsio
    exps = read_vis_data(vis_prods=vis_prods, seg_prods=seg_prods, workdir=workdir, method="fitsio")
    for exp in exps:
        assert type(exp) is VisExposureFitsIO

    # check hdf5
    exps = read_vis_data(
        vis_prods=vis_prods, seg_prods=seg_prods, workdir=workdir, method="hdf5", hdf5_files=hdf5_files
    )
    for exp in exps:
        assert type(exp) is VisExposureHDF5

    # check invalid method
    with pytest.raises(ValueError):
        exps = read_vis_data(vis_prods=vis_prods, seg_prods=seg_prods, workdir=workdir, method="invalid method")


class Testvis_exposures(object):
    def testExposures(self, workdir, input_fits, input_hdf5, num_detectors):
        """Tests the Exposure classes"""
        verify_all_exposure_types(workdir, input_fits, input_hdf5, num_detectors, quadrants=False)

    def test_read_vis_data(self, workdir, input_products, hdf5_listfile):
        """Tests read_vis_exposures"""
        verify_read_vis_data(workdir, input_products, hdf5_listfile)


class Testvis_exposures_CCD(object):
    def testExposures(self, workdir, input_fits_ccd, input_hdf5_ccd, num_detectors_ccd):
        """Tests the Exposure classes"""
        verify_all_exposure_types(workdir, input_fits_ccd, input_hdf5_ccd, num_detectors_ccd, quadrants=False)

    def test_read_vis_data(self, workdir, input_products_ccd, hdf5_listfile_ccd):
        """Tests read_vis_exposures"""
        verify_read_vis_data(workdir, input_products_ccd, hdf5_listfile_ccd)


class Testvis_exposures_quadrant(object):
    def testExposures(self, workdir, input_fits_quadrant, input_hdf5_quadrant, num_detectors_quadrant):
        """Tests the Exposure classes"""
        verify_all_exposure_types(
            workdir, input_fits_quadrant, input_hdf5_quadrant, num_detectors_quadrant, quadrants=True
        )

    def test_read_vis_data(self, workdir, input_products_quadrant, hdf5_listfile_quadrant):
        """Tests read_vis_exposures"""
        verify_read_vis_data(workdir, input_products_quadrant, hdf5_listfile_quadrant)
