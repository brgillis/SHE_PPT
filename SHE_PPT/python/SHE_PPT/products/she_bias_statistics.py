""" @file she_bias_statistics.py

    Created 22 June 2018

    Functions to create and output a shear bias statistics data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
"""

__updated__ = "2021-02-10"

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

from astropy.table import Table

from EL_PythonUtils.utilities import hash_any
import ST_DM_DmUtils.DmUtils as dm_utils
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.intermediategeneral_stub import dpdSheIntermediateGeneral
from ST_DataModelBindings.pro import she_stub as she_pro
import SHE_PPT


from ..file_io import read_xml_product, find_aux_file, get_allowed_filename, find_file
from ..logging import getLogger
from ..product_utility import init_intermediate_general
from ..table_formats.she_bfd_bias_statistics import initialise_bfd_bias_statistics_table, get_bfd_bias_statistics
from ..table_formats.she_bias_statistics import initialise_bias_statistics_table, get_bias_statistics,\
                                                get_bias_measurements


sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'

logger = getLogger(__name__)


def init():
    """
        Adds some extra functionality to the dpdSheBiasStatistics product
    """

    init_intermediate_general()

    binding_class = dpdSheIntermediateGeneral

    # Add useful methods to the class

    # Add general methods

    binding_class.get_method_datastorage = __get_method_datastorage

    binding_class.set_method_bias_statistics_filename = __set_method_bias_statistics_filename
    binding_class.get_method_bias_statistics_filename = __get_method_bias_statistics_filename

    binding_class.set_method_bias_statistics = __set_method_bias_statistics
    binding_class.get_method_bias_statistics = __get_method_bias_statistics

    binding_class.set_method_bias_measurements = __set_method_bias_measurements
    binding_class.get_method_bias_measurements = __get_method_bias_measurements

    # Add methods for specific shear estimation methods

    binding_class.set_BFD_bias_statistics_filename = __set_BFD_bias_statistics_filename
    binding_class.get_BFD_bias_statistics_filename = __get_BFD_bias_statistics_filename

    binding_class.set_BFD_bias_statistics = __set_BFD_bias_statistics
    binding_class.get_BFD_bias_statistics = __get_BFD_bias_statistics

    binding_class.set_BFD_bias_measurements = __set_BFD_bias_measurements
    binding_class.get_BFD_bias_measurements = __get_BFD_bias_measurements

    binding_class.set_KSB_bias_statistics_filename = __set_KSB_bias_statistics_filename
    binding_class.get_KSB_bias_statistics_filename = __get_KSB_bias_statistics_filename

    binding_class.set_KSB_bias_statistics = __set_KSB_bias_statistics
    binding_class.get_KSB_bias_statistics = __get_KSB_bias_statistics

    binding_class.set_KSB_bias_measurements = __set_KSB_bias_measurements
    binding_class.get_KSB_bias_measurements = __get_KSB_bias_measurements

    binding_class.set_LensMC_bias_statistics_filename = __set_LensMC_bias_statistics_filename
    binding_class.get_LensMC_bias_statistics_filename = __get_LensMC_bias_statistics_filename

    binding_class.set_LensMC_bias_statistics = __set_LensMC_bias_statistics
    binding_class.get_LensMC_bias_statistics = __get_LensMC_bias_statistics

    binding_class.set_LensMC_bias_measurements = __set_LensMC_bias_measurements
    binding_class.get_LensMC_bias_measurements = __get_LensMC_bias_measurements

    binding_class.set_MomentsML_bias_statistics_filename = __set_MomentsML_bias_statistics_filename
    binding_class.get_MomentsML_bias_statistics_filename = __get_MomentsML_bias_statistics_filename

    binding_class.set_MomentsML_bias_statistics = __set_MomentsML_bias_statistics
    binding_class.get_MomentsML_bias_statistics = __get_MomentsML_bias_statistics

    binding_class.set_MomentsML_bias_measurements = __set_MomentsML_bias_measurements
    binding_class.get_MomentsML_bias_measurements = __get_MomentsML_bias_measurements

    binding_class.set_REGAUSS_bias_statistics_filename = __set_REGAUSS_bias_statistics_filename
    binding_class.get_REGAUSS_bias_statistics_filename = __get_REGAUSS_bias_statistics_filename

    binding_class.set_REGAUSS_bias_statistics = __set_REGAUSS_bias_statistics
    binding_class.get_REGAUSS_bias_statistics = __get_REGAUSS_bias_statistics

    binding_class.set_REGAUSS_bias_measurements = __set_REGAUSS_bias_measurements
    binding_class.get_REGAUSS_bias_measurements = __get_REGAUSS_bias_measurements


def __get_method_datastorage(self, method):
    # Find the index label in the StringData list
    i = None
    for s in self.Data.StringData:
        if method + ":" in s:
            i = int(s.split(":")[1])
            break
    if i is None:
        return None
    return self.Data.DataStorage[i]


def __set_method_bias_statistics_filename(self, method, filename):

    bias_statistics = self.get_method_datastorage(method)

    if bias_statistics is None and filename is not None:
        len_datastorage = len(self.Data.DataStorage)
        self.Data.StringData.append(method + ":" + str(len_datastorage))
        self.Data.DataStorage.append(create_method_she_bias_statistics(filename))
    elif bias_statistics is not None and filename is not None:
        bias_statistics.DataContainer.FileName = filename
    elif bias_statistics is None and filename is None:
        # Already set to None, so nothing to do
        pass
    elif bias_statistics is not None and filename is None:
        # Delete the string value and data storage
        for i_s, s in enumerate(self.Data.StringData):
            if method + ":" in s:
                i = int(s.split(":")[1])
                break
        del self.Data.StringData[i_s]
        del self.Data.DataStorage[i]


def __get_method_bias_statistics_filename(self, method):

    bias_statistics = self.get_method_datastorage(method)

    if bias_statistics is None:
        return None

    filename = bias_statistics.DataContainer.FileName

    if filename in ("None","data/None"):
        return None

    return filename


def __set_method_bias_statistics(self, method, stats, workdir="."):

    # If a previous file exists, delete it
    old_filename = __get_method_bias_statistics_filename(self, method)
    if old_filename is not None:
        qualified_old_filename = os.path.join(workdir, old_filename)
        if os.path.exists(qualified_old_filename):
            try:
                os.remove(qualified_old_filename)
            except Exception:
                logger.warning("Deprecated file %s cannot be deleted", qualified_old_filename)

    # Handle if the new statistics object is None
    if stats is None:
        self.set_method_bias_statistics_filename(method, None)

    # Create a new file to store the statistics

    subfolder_number = os.getpid() % 256
    subfolder_name = "data/s" + str(subfolder_number)

    qualified_subfolder_name = os.path.join(workdir, subfolder_name)

    # Make sure the subdirectory for the file exists
    if not os.path.exists(qualified_subfolder_name):
        os.makedirs(qualified_subfolder_name)

    instance_id = hash_any(stats, format='base64')
    instance_id_fn = instance_id[0:17].replace('.', '-').replace('+', '-')
    new_filename = get_allowed_filename(type_name=method.upper() + "", instance_id=instance_id_fn,
                                        extension=".fits", version=SHE_PPT.__version__, subdir=subfolder_name)

    # Create the file using the statistics
    if method == "BFD":
        bias_statistics_table = initialise_bfd_bias_statistics_table(method=method,
                                                                     bfd_bias_statistics=stats)
    else:
        bias_statistics_table = initialise_bias_statistics_table(method=method,
                                                                 g1_bias_statistics=stats[0],
                                                                 g2_bias_statistics=stats[1])

    qualified_new_filename = os.path.join(workdir, new_filename)

    bias_statistics_table.write(qualified_new_filename)

    # Set the filename for the object
    self.set_method_bias_statistics_filename(method, new_filename)



def __get_method_bias_statistics(self, method, workdir="."):

    filename = self.get_method_bias_statistics_filename(method)

    if filename is None:
        if method == "BFD":
            return None
        return None, None

    qualified_filename = find_file(filename, path=workdir)

    bias_statistics_table = Table.read(qualified_filename)

    if method == "BFD":
        bias_statistics = get_bfd_bias_statistics(bias_statistics_table, compress=True)
    else:
        bias_statistics = get_bias_statistics(bias_statistics_table, compress=True)

    return bias_statistics


def __set_method_bias_measurements(self, method, measurements, workdir="."):

    filename = None
    qualified_filename = None

    subfolder_number = os.getpid() % 256
    subfolder_name = "data/s" + str(subfolder_number)

    qualified_subfolder_name = os.path.join(workdir, subfolder_name)

    # Make sure the subdirectory for the file exists
    if not os.path.exists(qualified_subfolder_name):
        os.makedirs(qualified_subfolder_name)

    instance_id = hash_any(measurements, format='base64')
    instance_id_fn = instance_id[0:17].replace('.', '-').replace('+', '-')
    filename = get_allowed_filename(type_name=method.upper() + "", instance_id=instance_id_fn,
                                    extension=".fits", version=SHE_PPT.__version__, subdir=subfolder_name)
    qualified_filename = os.path.join(workdir, filename)

    # Create the file using the measurements
    if method == "BFD":
        bias_statistics_table = initialise_bfd_bias_statistics_table(method=method,
                                                                     g1_bias_measurements=measurements[0],
                                                                     g2_bias_measurements=measurements[1])
    else:
        bias_statistics_table = initialise_bias_statistics_table(method=method,
                                                                 g1_bias_measurements=measurements[0],
                                                                 g2_bias_measurements=measurements[1])

    # If a previous file exists, we'll use it

    old_filename = self.get_method_bias_statistics_filename(method)
    if old_filename is not None:
        qualified_old_filename = os.path.join(workdir, old_filename)
        if os.path.exists(qualified_old_filename):

            filename = old_filename
            qualified_filename = qualified_old_filename

            # Copy over the data we set up in the table header to this file
            old_bias_statistics_table = Table.read(qualified_filename)
            old_bias_statistics_table.meta = bias_statistics_table.meta
            bias_statistics_table = old_bias_statistics_table

            try:
                os.remove(qualified_old_filename)
            except Exception:
                logger.warning("Deprecated file %s cannot be deleted", qualified_old_filename)

    # Set the filename for the object
    self.set_method_bias_statistics_filename(method, filename)

    # Write the table
    bias_statistics_table.write(qualified_filename)


def __get_method_bias_measurements(self, method, workdir="."):

    filename = __get_method_bias_statistics_filename(self, method)

    if filename is None:
        return None

    qualified_filename = find_file(filename, path=workdir)

    bias_statistics_table = Table.read(qualified_filename)

    bias_measurements = get_bias_measurements(bias_statistics_table)

    return bias_measurements


def __set_BFD_bias_statistics_filename(self, filename):
    __set_method_bias_statistics_filename(self, method="BFD", filename=filename)


def __get_BFD_bias_statistics_filename(self):
    return __get_method_bias_statistics_filename(self, method="BFD")


def __set_BFD_bias_statistics(self, stats, workdir="."):
    return __set_method_bias_statistics(self, method="BFD", stats=stats, workdir=workdir)


def __get_BFD_bias_statistics(self, workdir="."):
    return __get_method_bias_statistics(self, method="BFD", workdir=workdir)


def __set_BFD_bias_measurements(self, measurements, workdir="."):
    return __set_method_bias_measurements(self, method="BFD", measurements=measurements, workdir=workdir)


def __get_BFD_bias_measurements(self, workdir="."):
    return __get_method_bias_measurements(self, method="BFD", workdir=workdir)


def __set_KSB_bias_statistics_filename(self, filename):
    __set_method_bias_statistics_filename(self, method="KSB", filename=filename)


def __get_KSB_bias_statistics_filename(self):
    return __get_method_bias_statistics_filename(self, method="KSB")


def __set_KSB_bias_statistics(self, stats, workdir="."):
    return __set_method_bias_statistics(self, method="KSB", stats=stats, workdir=workdir)


def __get_KSB_bias_statistics(self, workdir="."):
    return __get_method_bias_statistics(self, method="KSB", workdir=workdir)


def __set_KSB_bias_measurements(self, measurements, workdir="."):
    return __set_method_bias_measurements(self, method="KSB", measurements=measurements, workdir=workdir)


def __get_KSB_bias_measurements(self, workdir="."):
    return __get_method_bias_measurements(self, method="KSB", workdir=workdir)


def __set_LensMC_bias_statistics_filename(self, filename):
    __set_method_bias_statistics_filename(self, method="LensMC", filename=filename)


def __get_LensMC_bias_statistics_filename(self):
    return __get_method_bias_statistics_filename(self, method="LensMC")


def __set_LensMC_bias_statistics(self, stats, workdir="."):
    return __set_method_bias_statistics(self, method="LensMC", stats=stats, workdir=workdir)


def __get_LensMC_bias_statistics(self, workdir="."):
    return __get_method_bias_statistics(self, method="LensMC", workdir=workdir)


def __set_LensMC_bias_measurements(self, measurements, workdir="."):
    return __set_method_bias_measurements(self, method="LensMC", measurements=measurements, workdir=workdir)


def __get_LensMC_bias_measurements(self, workdir="."):
    return __get_method_bias_measurements(self, method="LensMC", workdir=workdir)


def __set_MomentsML_bias_statistics_filename(self, filename):
    __set_method_bias_statistics_filename(self, method="MomentsML", filename=filename)


def __get_MomentsML_bias_statistics_filename(self):
    return __get_method_bias_statistics_filename(self, method="MomentsML")


def __set_MomentsML_bias_statistics(self, stats, workdir="."):
    return __set_method_bias_statistics(self, method="MomentsML", stats=stats, workdir=workdir)


def __get_MomentsML_bias_statistics(self, workdir="."):
    return __get_method_bias_statistics(self, method="MomentsML", workdir=workdir)


def __set_MomentsML_bias_measurements(self, measurements, workdir="."):
    return __set_method_bias_measurements(self, method="MomentsML", measurements=measurements, workdir=workdir)


def __get_MomentsML_bias_measurements(self, workdir="."):
    return __get_method_bias_measurements(self, method="MomentsML", workdir=workdir)


def __set_REGAUSS_bias_statistics_filename(self, filename):
    __set_method_bias_statistics_filename(self, method="REGAUSS", filename=filename)


def __get_REGAUSS_bias_statistics_filename(self):
    return __get_method_bias_statistics_filename(self, method="REGAUSS")


def __set_REGAUSS_bias_statistics(self, stats, workdir="."):
    return __set_method_bias_statistics(self, method="REGAUSS", stats=stats, workdir=workdir)


def __get_REGAUSS_bias_statistics(self, workdir="."):
    return __get_method_bias_statistics(self, method="REGAUSS", workdir=workdir)


def __set_REGAUSS_bias_measurements(self, measurements, workdir="."):
    return __set_method_bias_measurements(self, method="REGAUSS", measurements=measurements, workdir=workdir)


def __get_REGAUSS_bias_measurements(self, workdir="."):
    return __get_method_bias_measurements(self, method="REGAUSS", workdir=workdir)


def create_dpd_she_bias_statistics(BFD_bias_statistics_filename=None,
                                   KSB_bias_statistics_filename=None,
                                   LensMC_bias_statistics_filename=None,
                                   MomentsML_bias_statistics_filename=None,
                                   REGAUSS_bias_statistics_filename=None,):
    """
        @TODO fill in docstring
    """

    dpd_shear_bias_stats = read_xml_product(find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_shear_bias_stats.Header = HeaderProvider.create_generic_header("SHE")

    dpd_shear_bias_stats.set_BFD_bias_statistics_filename(BFD_bias_statistics_filename)
    dpd_shear_bias_stats.set_KSB_bias_statistics_filename(KSB_bias_statistics_filename)
    dpd_shear_bias_stats.set_LensMC_bias_statistics_filename(LensMC_bias_statistics_filename)
    dpd_shear_bias_stats.set_MomentsML_bias_statistics_filename(MomentsML_bias_statistics_filename)
    dpd_shear_bias_stats.set_REGAUSS_bias_statistics_filename(REGAUSS_bias_statistics_filename)

    return dpd_shear_bias_stats


def create_dpd_she_bias_statistics_from_stats(BFD_bias_statistics=None,
                                              KSB_bias_statistics=None,
                                              LensMC_bias_statistics=None,
                                              MomentsML_bias_statistics=None,
                                              REGAUSS_bias_statistics=None,
                                              workdir="."):
    """
        @TODO fill in docstring
    """

    dpd_shear_bias_stats = read_xml_product(find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among other things)
    dpd_shear_bias_stats.Header = HeaderProvider.create_generic_header("SHE")

    # Set the statistics for each method
    dpd_shear_bias_stats.set_BFD_bias_statistics(BFD_bias_statistics, workdir=workdir)
    dpd_shear_bias_stats.set_KSB_bias_statistics(KSB_bias_statistics, workdir=workdir)
    dpd_shear_bias_stats.set_LensMC_bias_statistics(LensMC_bias_statistics, workdir=workdir)
    dpd_shear_bias_stats.set_MomentsML_bias_statistics(MomentsML_bias_statistics, workdir=workdir)
    dpd_shear_bias_stats.set_REGAUSS_bias_statistics(REGAUSS_bias_statistics, workdir=workdir)

    return dpd_shear_bias_stats


# Add useful aliases
create_she_bias_statistics_product = create_dpd_she_bias_statistics
create_she_bias_statistics_product_from_stats = create_dpd_she_bias_statistics_from_stats

# Creation functions


def create_method_she_bias_statistics(filename):

    method_she_bias_statistics = dm_utils.create_fits_storage(she_pro.sheGenericFile,
                                                              filename,
                                                              "she.biasStatistics",
                                                              "8.0")
    method_she_bias_statistics.Valid = "VALID"

    return method_she_bias_statistics
