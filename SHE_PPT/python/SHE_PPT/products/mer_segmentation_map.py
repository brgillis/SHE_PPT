""" @file mer_segmentation_map.py

    Created 26 Oct 2017

    Functions to create and output a mosaic data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_mosaic.html

    Origin: OU-MER - Input to Analysis pipeline
"""

__updated__ = "2021-08-16"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import os

from astropy.io import fits

from ST_DataModelBindings.dpd.mer.raw.segmentationmap_stub import dpdMerSegmentationMap
from .. import detector as dtc
from ..constants.fits import SEGMENTATION_TAG
from ..file_io import read_xml_product
from ..product_utility import create_product_from_template, init_just_datastorage
from ..utility import find_extension

sample_file_name = "SHE_PPT/sample_mer_segmentation_map.xml"
product_type_name = "DpdMerSegmentationMap"


# Convenience function to easily load the actual map
def load_mosaic_hdu(filename, workdir = None, hdu = 0, detector_x = None, detector_y = None, **kwargs):
    """Directly loads the mosaic image from the filename of the data product.

    Parameters
    ----------
    filename : str
        Filename of the mosaic data product. If `dir` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `dir` is
        supplied, `filename` should be only the local name of the file.
    workdir : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    hdu : int
        Index of the HDU to load. If `detector` is supplied, this is ignored.
    detector : int
        ID of the detector whose HDU should be loaded. Overrides `hdu` if
        supplied.
    **kwargs
        Keyword arguments to pass to fits.open.

    Returns
    -------
    mosaic_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the mosaic image and its header.

    Raises
    ------
    IOError
        Will raise an IOError if either no such file as `filename` exists or
        if the filename of the mosaic data contained within the product does
        not exist.
    """

    init()

    if workdir is None:
        workdir = ""

    mosaic_product = read_xml_product(
        xml_filename=os.path.join(workdir, filename))

    data_filename = mosaic_product.get_data_filename()

    mosaic_hdulist = fits.open(data_filename, **kwargs)

    if detector_x is not None and detector_y is not None:
        hdu = find_extension(mosaic_hdulist, extname=dtc.get_id_string(
            detector_x, detector_y) + "." + SEGMENTATION_TAG)

    mosaic_hdu = mosaic_hdulist[hdu]

    return mosaic_hdu


# Initialisation function, to add methods to an imported XML class


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdMerSegmentationMap,
                          init_function=create_dpd_mer_mosaic)


def create_dpd_mer_mosaic(filename = None,
                          data_filename = None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename=sample_file_name,
                                        product_type_name="DpdMerSegmentationMap",
                                        filename=filename,
                                        data_filename=data_filename)


# Add a useful alias
create_mosaic_product = create_dpd_mer_mosaic
