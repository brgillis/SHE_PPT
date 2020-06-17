""" @file shear_estimates_product.py

    Created 9 Oct 2017

    Functions to create and output a shear estimates data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
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

__updated__ = "2020-06-10"

from SHE_PPT.file_io import (read_xml_product, find_aux_file, get_data_filename_from_product,
                             set_data_filename_of_product)
from ST_DM_HeaderProvider import GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.validatedmeasurements_stub import dpdSheValidatedMeasurements
from ST_DataModelBindings.pro import she_stub as she_pro
from ST_DataModelBindings.sys.dss_stub import dataContainer

sample_file_name = "SHE_PPT/sample_validated_shear_measurements.xml"


def init():
    """
        Adds some extra functionality to the dpdSheValidatedMeasurements product
    """

    binding_class = dpdSheValidatedMeasurements

    # Add the data file name methods

    binding_class.set_BFD_filename = __set_BFD_filename
    binding_class.get_BFD_filename = __get_BFD_filename

    binding_class.set_KSB_filename = __set_KSB_filename
    binding_class.get_KSB_filename = __get_KSB_filename

    binding_class.set_LensMC_filename = __set_LensMC_filename
    binding_class.get_LensMC_filename = __get_LensMC_filename

    binding_class.set_MomentsML_filename = __set_MomentsML_filename
    binding_class.get_MomentsML_filename = __get_MomentsML_filename

    binding_class.set_REGAUSS_filename = __set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = __get_REGAUSS_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_method_filename = __get_method_filename
    binding_class.set_method_filename = __set_method_filename

    binding_class.get_spatial_footprint = __get_spatial_footprint
    binding_class.set_spatial_footprint = __set_spatial_footprint

    binding_class.has_files = True


def __set_BFD_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "BfdMoments"):
            self.Data.BfdMoments = None
    else:
        if not hasattr(self.Data, "BfdMoments") or self.Data.BfdMoments is None:
            self.Data.BfdMoments = create_bfd_moments(filename)
        set_data_filename_of_product(self, filename, "BfdMoments.DataStorage")
    return


def __get_BFD_filename(self):
    if not hasattr(self.Data, "BfdMoments") or self.Data.BfdMoments is None:
        return None
    else:
        return get_data_filename_from_product(self, "BfdMoments.DataStorage")


def __set_KSB_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "KsbShearMeasurements"):
            self.Data.KsbShearMeasurements = None
    else:
        if not hasattr(self.Data, "KsbShearMeasurements") or self.Data.KsbShearMeasurements is None:
            self.Data.KsbShearMeasurements = create_ksb_estimates(filename)
        set_data_filename_of_product(self, filename, "KsbShearMeasurements.DataStorage")
    return


def __get_KSB_filename(self):
    if not hasattr(self.Data, "KsbShearMeasurements") or self.Data.KsbShearMeasurements is None:
        return None
    else:
        return get_data_filename_from_product(self, "KsbShearMeasurements.DataStorage")


def __set_LensMC_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "LensMcShearMeasurements"):
            self.Data.LensMcShearMeasurements = None
    else:
        if not hasattr(self.Data, "LensMcShearMeasurements") or self.Data.LensMcShearMeasurements is None:
            self.Data.LensMcShearMeasurements = create_lensmc_estimates(filename)
        set_data_filename_of_product(self, filename, "LensMcShearMeasurements.DataStorage")
    return


def __get_LensMC_filename(self):
    if not hasattr(self.Data, "LensMcShearMeasurements") or self.Data.LensMcShearMeasurements is None:
        return None
    else:
        return get_data_filename_from_product(self, "LensMcShearMeasurements.DataStorage")


def __set_MomentsML_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "MomentsMlShearMeasurements"):
            self.Data.MomentsMlShearMeasurements = None
    else:
        if not hasattr(self.Data, "MomentsMlShearMeasurements") or self.Data.MomentsMlShearMeasurements is None:
            self.Data.MomentsMlShearMeasurements = create_momentsml_estimates(filename)
        set_data_filename_of_product(self, filename, "MomentsMlShearMeasurements.DataStorage")
    return


def __get_MomentsML_filename(self):
    if not hasattr(self.Data, "MomentsMlShearMeasurements") or self.Data.MomentsMlShearMeasurements is None:
        return None
    else:
        return get_data_filename_from_product(self, "MomentsMlShearMeasurements.DataStorage")


def __set_REGAUSS_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "RegaussShearMeasurements"):
            self.Data.RegaussShearMeasurements = None
    else:
        if not hasattr(self.Data, "RegaussShearMeasurements") or self.Data.RegaussShearMeasurements is None:
            self.Data.RegaussShearMeasurements = create_regauss_estimates(filename)
        set_data_filename_of_product(self, filename, "RegaussShearMeasurements.DataStorage")
    return


def __get_REGAUSS_filename(self):
    if not hasattr(self.Data, "RegaussShearMeasurements") or self.Data.RegaussShearMeasurements is None:
        return None
    else:
        return get_data_filename_from_product(self, "RegaussShearMeasurements.DataStorage")


def __get_all_filenames(self):

    all_filenames = [self.get_BFD_filename(),
                     self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MomentsML_filename(),
                     self.get_REGAUSS_filename(), ]

    return all_filenames


def __get_method_filename(self, method):

    if method == "KSB":
        return self.get_KSB_filename()
    elif method == "LensMC":
        return self.get_LensMC_filename()
    elif method == "MomentsML":
        return self.get_MomentsML_filename()
    elif method == "REGAUSS":
        return self.get_REGAUSS_filename()
    elif method == "BFD":
        return self.get_BFD_filename()
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def __set_method_filename(self, method, filename):

    if method == "KSB":
        return self.set_KSB_filename(filename)
    elif method == "LensMC":
        return self.set_LensMC_filename(filename)
    elif method == "MomentsML":
        return self.set_MomentsML_filename(filename)
    elif method == "REGAUSS":
        return self.set_REGAUSS_filename(filename)
    elif method == "BFD":
        return self.set_BFD_filename(filename)
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def __set_spatial_footprint(self, p):
    """ Set the spatial footprint. p can be either the spatial footprint, or
        another product which has a spatial footprint defined.
    """

    # Figure out how the spatial footprint was passed to us
    if isinstance(p, str):
        # If we got a filepath, read it in and apply this function to the read-in product
        return __set_spatial_footprint(self, read_xml_product(p))
    elif isinstance(p, polygonType):
        poly = p
    elif hasattr(p, "Polygon"):
        poly = p.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "ImgSpatialFootprint"):
        poly = p.Data.ImgSpatialFootprint.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "CatalogCoverage"):
        poly = p.Data.CatalogCoverage.SpatialCoverage.Polygon
    else:
        raise TypeError("For set_spatial_footprint, must be provided a spatial footprint, a product which has it, " +
                        "or the path to such a product. Received: " + str(type(p)))

    self.Data.CatalogCoverage.SpatialCoverage.Polygon = poly

    return


def __get_spatial_footprint(self):
    """ Get the spatial footprint as a polygonType object.
    """

    return self.Data.CatalogCoverage.SpatialCoverage.Polygon


def create_dpd_validated_shear_estimates(BFD_filename="",
                                         KSB_filename="",
                                         LensMC_filename="",
                                         MomentsML_filename="",
                                         REGAUSS_filename="",
                                         spatial_footprint=None):
    """
        @TODO fill in docstring
    """

    dpd_validated_shear_estimates = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_validated_shear_estimates.Header = HeaderProvider.create_generic_header("SHE")

    __set_BFD_filename(dpd_validated_shear_estimates, BFD_filename)
    __set_KSB_filename(dpd_validated_shear_estimates, KSB_filename)
    __set_LensMC_filename(dpd_validated_shear_estimates, LensMC_filename)
    __set_MomentsML_filename(dpd_validated_shear_estimates, MomentsML_filename)
    __set_REGAUSS_filename(dpd_validated_shear_estimates, REGAUSS_filename)
    if spatial_footprint is not None:
        __set_spatial_footprint(dpd_validated_shear_estimates, spatial_footprint)

    return dpd_validated_shear_estimates


# Add a useful alias
create_validated_shear_estimates_product = create_dpd_validated_shear_estimates


def create_bfd_moments(filename):
    """
        @TODO fill in docstring
    """

    BFD_shear_estimates = she_pro.sheBfdMoments()

    BFD_shear_estimates.format = "she.bfdMoments"
    BFD_shear_estimates.version = "0.1"

    BFD_shear_estimates.DataStorage = she_pro.sheBfdMomentsFile()
    BFD_shear_estimates.Valid = "UNKNOWN"

    BFD_shear_estimates.DataStorage.DataContainer = dataContainer()
    BFD_shear_estimates.DataStorage.DataContainer.FileName = filename
    BFD_shear_estimates.DataStorage.DataContainer.filestatus = "PROPOSED"

    return BFD_shear_estimates


def create_ksb_estimates(filename):
    """
        @TODO fill in docstring
    """

    KSB_shear_estimates = she_pro.sheKsbShearMeasurements()

    KSB_shear_estimates.format = "she.ksbShearMeasurements"
    KSB_shear_estimates.version = "0.1"

    KSB_shear_estimates.DataContainer = dataContainer()
    KSB_shear_estimates.DataContainer.FileName = filename
    KSB_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return KSB_shear_estimates


def create_lensmc_estimates(filename):
    """
        @TODO fill in docstring
    """

    LensMC_shear_estimates = she_pro.sheLensMcShearMeasurements()

    LensMC_shear_estimates.format = "she.lensMcShearMeasurements"
    LensMC_shear_estimates.version = "0.1"

    LensMC_shear_estimates.DataContainer = dataContainer()
    LensMC_shear_estimates.DataContainer.FileName = filename
    LensMC_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return LensMC_shear_estimates


def create_momentsml_estimates(filename):
    """
        @TODO fill in docstring
    """

    MomentsML_shear_estimates = she_pro.sheMomentsMlShearMeasurements()

    MomentsML_shear_estimates.format = "she.momentsMlShearMeasurements"
    MomentsML_shear_estimates.version = "0.1"

    MomentsML_shear_estimates.DataContainer = dataContainer()
    MomentsML_shear_estimates.DataContainer.FileName = filename
    MomentsML_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return MomentsML_shear_estimates


def create_regauss_estimates(filename):
    """
        @TODO fill in docstring
    """

    REGAUSS_shear_estimates = she_pro.sheRegaussShearMeasurements()

    REGAUSS_shear_estimates.format = "she.regaussShearMeasurements"
    REGAUSS_shear_estimates.version = "0.1"

    REGAUSS_shear_estimates.DataContainer = dataContainer()
    REGAUSS_shear_estimates.DataContainer.FileName = filename
    REGAUSS_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return REGAUSS_shear_estimates
