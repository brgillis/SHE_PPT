""" @file generate_mock_object_id_list.py

    Created 05 May 2022.

    Utilities to generate mock mer final catalogues for smoke tests.
"""

__updated__ = "2022-05-05"

# Copyright (C) 2012-2022 Euclid Science Ground Segment
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from SHE_PPT import __version__ as ppt_version
from SHE_PPT.file_io import get_allowed_filename, write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products import she_object_id_list

logger = getLogger(__name__)


def create_object_id_list(id_list, workdir = "."):

    dpd = she_object_id_list.create_dpd_she_object_id_list(id_list=id_list)

    filename = get_allowed_filename("OBJ-IDS", "00", version=ppt_version, extension=".xml", subdir="")

    qualified_filename = os.path.join(workdir, filename)

    logger.info("Writing object_id_list product to %s" % qualified_filename)

    write_xml_product(dpd, filename, workdir=workdir)

    return filename
