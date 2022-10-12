""" @file phz_pf_output_catalog.py

    Created 17 Nov 2017

    Functions to create and output a detections data product.

    Origin: OU-PHZ - PfOutputCatalog (TODO: Confirm) in their data model
"""

__updated__ = "2021-11-18"

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

import PHZ_DMUtils.PHZ_DataModelUtils as phz_dm
from ..product_utility import init_method_files



import pyxb
import numpy as np

import ST_DataModelBindings.bas.imp.stc_stub as stc_dict
import ST_DataModelBindings.bas.cat_stub as cat_dict
import ST_DataModelBindings.bas.cot_stub as cot_dict
import ST_DataModelBindings.ins_stub as ins_dict
import ST_DataModelBindings.bas.dtd_stub as dtd_dict

def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    #init_method_files(binding_class=dpdPhzPfOutputCatalog,
    #                      init_function=create_dpd_photoz_catalog)
    pass

def create_catalog_coverage():
    SpatialCoverage = cot_dict.spatialFootprint()
    SpatialCoverage.Polygon = stc_dict.polygonType()
    SpatialCoverage.Polygon.Vertex.append(stc_dict.vertexType())
    vertex = SpatialCoverage.Polygon.Vertex[0]
    vertex.Position = dtd_dict.double2Type(C1=0, C2=0)


    return SpatialCoverage


def create_dpd_photoz_catalog(photoz_filename=None,
                          gal_sed_filename=None,
                          star_sed_filename=None
                              ):
    """ Creates a product of this type.
    """
    cov = create_catalog_coverage()
    tile_index=0

    pro_phz =  phz_dm.create_PHZ_catalog(photoz_filename,star_sed_filename,
                                          gal_sed_filename,cov,tile_index)
    pro_phz.toDOM()
    return pro_phz
   

# Add useful aliases
create_detections_product = create_dpd_photoz_catalog
create_dpd_phz_pf_output_catalog = create_dpd_photoz_catalog
create_phz_pf_output_catalog_product = create_dpd_photoz_catalog
