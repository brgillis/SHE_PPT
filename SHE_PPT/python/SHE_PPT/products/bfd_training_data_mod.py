""" @file bfd_training_data_product.py

    Created 24 Nov 2017

    Functions to create and output a bfd_training_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
"""

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

__updated__ = "2019-08-15"


# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import os
import pickle

from sphinx.websupport import storage

import ST_DataModelBindings.bas.cat_stub as cat_dict
import ST_DataModelBindings.bas.cot_stub as cot_dict
import ST_DataModelBindings.bas.dtd_stub as dtd_dict
import ST_DataModelBindings.bas.imp.stc_stub as stc_dict
from ST_DataModelBindings.dpd.she.shearbfdtraining_stub import dpdShearBFDTraining
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdSheBFDTrainingDataProduct # @FIXME
    binding_class = DpdSheBFDTrainingDataProduct

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_filename(self, filename):
    # @TODO: Update
    set_data_filename_of_product(self, filename, "ShearBFDTrainingFile")


def __get_filename(self):
    # @TODO: Update
    return get_data_filename_from_product(self, "ShearBFDTrainingFile")


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


class DpdSheBFDTrainingDataProduct(dpdShearBFDTraining):  # @FIXME

    def __init__(self):
        testXmlFile = find_aux_file('SHE_PPT/test_bfdtraining.xml')
        if not os.path.exists(testXmlFile):
            self.Header = None
            self.Data = None
            #self.QualityFlags = None
            #self.Parameters = None
        else:
            prod = read_xml_product(testXmlFile, allow_pickled=False)
            self.Header = prod.Header
            self.Data = prod.Data
            #self.QualityFlags = prod.QualityFlags
            #self.Parameters = prod.Parameters

    def validateBinding(self):
        return False


class SheBFDTrainingDataProduct:  # @FIXME

    def __init__(self):
        testXmlFile = find_aux_file('SHE_PPT/test_bfdtraining.xml')
        if not os.path.exists(testXmlFile):
            self.format = None
            self.version = None
            self.ShearBFDTrainingFile = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_bfd_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_bfd_training_data = she_dpd.DpdSheBFDTrainingDataProduct() #
    # FIXME
    dpd_she_bfd_training_data = DpdSheBFDTrainingDataProduct()
    pass
    # Check to see if xml test file exists..
    testXmlFile = find_aux_file('SHE_PPT/test_bfdtraining.xml')
    if os.path.exists(testXmlFile):
        print("Reading %s" % testXmlFile)
        she_bfd_training_data = read_xml_product(testXmlFile, allow_pickled=False)
        print("PID: ", she_bfd_training_data.Header.ProductId)
        print("CATID: ", she_bfd_training_data.Data.IdCatalog)
        print("FN: ", she_bfd_training_data.Data.ShearBFDTrainingFile.DataContainer.FileName)

    else:

        # dpd_she_bfd_training_data.Header =
        # HeaderProvider.createGenericHeader("SHE") # FIXME
        dpd_she_bfd_training_data.Header = "SHE"

        # @FIXME: Needs serious updating.
        dpd_she_bfd_training_data.Data = create_she_bfd_training_data(filename)

    #dpd_she_bfd_training_data.QualityFlags = create_she_bfd_training_qf()

    #dpd_she_bfd_training_data.Parameters = create_she_bfd_training_param()

    return dpd_she_bfd_training_data


# Add a useful alias
create_bfd_training_data_product = create_dpd_she_bfd_training_data


def create_she_bfd_training_data(filename=None):
    """
        @TODO fill in docstring
    """
    pass

    # @TODO: Check arrangement of things --> tenporary test_bfdtraining.xml.
    # @TODO: How to use sequences?
    # she_bfd_training_data = she_dpd.SheBFDTrainingDataProduct() # @FIXME
    she_bfd_training_data = SheBFDTrainingDataProduct()

    she_bfd_training_data.format = "UNDEFINED"
    she_bfd_training_data.version = "0.0"

    she_bfd_training_data.DataContainer = DataContainer()
    she_bfd_training_data.DataContainer.FileName = filename
    she_bfd_training_data.DataContainer.filestatus = "PROPOSED"

    # @TODO:  Need to add in the catalog

    she_bfd_training_data.IdCatalog = "1"
    she_bfd_training_data.CatalogCoverage = create_catalog_coverage()
    she_bfd_training_data.CatalogStorage = create_catalog_storage()
    she_bfd_training_data.CatalogDescription = create_catalog_description()
    return she_bfd_training_data


def create_catalog_coverage():
    """
    bas.cat, bas.cot,bas.imp.stc
    Use CatalogCoverage includes spatial footprint bas.cot.SpatialFootprint and 
    SpectralFootprint (optional)

    """

    cover = cat_dict.catalogCoverage()
    cover.SpatialCoverage = cot_dict.spatialFootprint()
    cover.SpatialCoverage.Polygon = stc_dict.polygonType()
    # Define multiple vertices - check code for vertexType() -- gitlab
    #cover.SpatialCoverage.Polygon.Vertex = stc_dict.vertexType()
    #cover.SpatialCoverage.Polygon.Vertex.Position = dtd_dict.double2Type()
    #cover.SpatialCoverage.Polygon.Vertex.Position.C1 = "0."
    #cover.SpatialCoverage.Polygon.Vertex.Position.C2 = "0."

    return cover


def create_catalog_storage():
    """
    Uses bas.cat 
    Sets up catalogue storage binding.

    """
    storage = cat_dict.catalogStorage()
    storage.CatalogFileStorage = cat_dict.catalogFileStorage()
    #storage.CatalogFileStorage.Id = "CFSId"
    #storage.CatalogFileStorage.FileFormat = "ASCII"
    #storage.CatalogFileStorage.FileNumber = "1"
    #storage.CatalogFileStorage.StorageSpace = cat_dict.catalogPartitionStorage()
    #storage.CatalogFileStorage.StorageSpace.Id = "CFS_SSId"
    #storage.CatalogFileStorage.StorageSpace.DataContainer = DataContainer()
    #storage.CatalogFileStorage.StorageSpace.DataContainer.FileName = "tmp.ascii"
    #storage.CatalogFileStorage.StorageSpace.DataContainer.filestatus = "PROPOSED"

    return storage


def create_catalog_description():
    """

    Sets up catalog description initialiser
    """

    descrip = cat_dict.catalogDescription()
    descrip.CatalogDataProduct = "Prod"
    descrip.PathToCatalogDefinition = "Path"
    descrip.CatalogFormatBase = "nir.masterFlat"
    descrip.CatalogFormatHDU = "1"
    descrip.CatalogFitsColumnsDefinition = "djjd"
    return descrip
