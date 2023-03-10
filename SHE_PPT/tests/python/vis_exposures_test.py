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

    # make sure a Value error is thrown if we try to extract an invalid detector ID
    with pytest.raises(ValueError):
        det = exp[n_detectors]


class Testvis_exposures(object):
    def testExposures(self, workdir, input_fits, input_hdf5):
        """Tests the Exposure classes"""

        # Get the filenames of the FITS/HDF5 input files

        det, wgt, bkg, _, _, seg = input_fits

        hdf5_file = os.path.join(workdir, "data", input_hdf5)

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

        assert (
            len(exp_hdf5) == len(exp_astropy) == len(exp_fitsio)
        ), "astropy, fitsio and HDF5 VisExposure objects have different number of detectors"

        # make sure the detectors for all 3 objects are the same

        n_detectors = len(exp_astropy)

        for i in range(n_detectors):
            det_astropy = exp_astropy[i]
            det_fitsio = exp_fitsio[i]
            det_hdf5 = exp_hdf5[i]

            assert det_astropy == det_fitsio
            assert det_astropy == det_hdf5

    def test_read_vis_data(self, workdir, input_products, hdf5_listfile):
        vis, _, _, seg, _ = input_products

        # check astropy
        exps = read_vis_data(vis_listfile=vis, seg_listfile=seg, workdir=workdir, method="astropy")
        for exp in exps:
            assert type(exp) is VisExposureAstropyFITS

        # check fitsio
        exps = read_vis_data(vis_listfile=vis, seg_listfile=seg, workdir=workdir, method="fitsio")
        for exp in exps:
            assert type(exp) is VisExposureFitsIO

        # check hdf5
        exps = read_vis_data(
            vis_listfile=vis, seg_listfile=seg, workdir=workdir, method="hdf5", hdf5_listfile=hdf5_listfile
        )
        for exp in exps:
            assert type(exp) is VisExposureHDF5

        # check invalid method
        with pytest.raises(ValueError):
            exps = read_vis_data(vis_listfile=vis, seg_listfile=seg, workdir=workdir, method="invalid method")
