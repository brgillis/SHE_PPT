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
:file: tests/python/mer_catalogues_test.py

:date: 22/02/2023
:author: Gordon Gibb
"""

import pytest

import json
import os

import numpy as np

from SHE_PPT.she_io.mer_catalogues import read_mer_final_catalogue, prune_mer_catalogue


class TestMerCatalogues(object):
    def test_read_mer_final_catalog_listfile(self, workdir, input_products, num_objects):
        """Tests read_mer_final_catalogue when reading a listfile of MER catalogue products"""

        _, mer_listfile, _, _, _, object_id_prod = input_products

        # test with no object_id_list product
        mer_cat, prods = read_mer_final_catalogue(mer_listfile, workdir)
        assert len(mer_cat) == num_objects, "Read in MER catalogue is the wrong size"

        # test with object_id_list product provided
        mer_cat_obj_prod, prods = read_mer_final_catalogue(mer_listfile, workdir, object_id_prod)
        assert len(mer_cat_obj_prod) == num_objects, "Read in MER catalogue is the wrong size"

        # both output catalogues should be the same
        assert (mer_cat == mer_cat_obj_prod).all()

    def test_read_mer_final_catalog_product(self, workdir, input_products, num_objects):
        """Tests read_mer_final_catalogue when reading a MER catalogue product directly"""

        _, mer_listfile, _, _, _, object_id_prod = input_products

        with open(os.path.join(workdir, mer_listfile)) as f:
            (mer_prod,) = json.load(f)

        # test with no object_id_list product
        mer_cat, prods = read_mer_final_catalogue(mer_prod, workdir)
        assert len(mer_cat) == num_objects, "Read in MER catalogue is the wrong size"

        # test with object_id_list product provided
        mer_cat_obj_prod, prods = read_mer_final_catalogue(mer_prod, workdir, object_id_prod)
        assert len(mer_cat_obj_prod) == num_objects, "Read in MER catalogue is the wrong size"

        # both output catalogues should be the same
        assert (mer_cat == mer_cat_obj_prod).all()

    def test_prune_mer_catalog(self, workdir, input_products):
        """Tests pruning a MER catalogue with an object list"""
        _, mer_listfile, _, _, _, _ = input_products

        mer_cat, prods = read_mer_final_catalogue(mer_listfile, workdir)

        all_objs = list(mer_cat["OBJECT_ID"])

        # pass in the same object list, assert the output catalogue is the same
        pruned_cat = prune_mer_catalogue(mer_cat, all_objs)
        assert (pruned_cat == mer_cat).all(), "Pruned and original catalogues should match"

        # use only one object from the table
        pruned_cat = prune_mer_catalogue(mer_cat, [all_objs[0]])
        assert len(pruned_cat) == 1, "Pruned catalogue should only have one row in it"
        assert pruned_cat["OBJECT_ID"] == [
            all_objs[0]
        ], "Object remaining in pruned catalogue does not match the expected one"

        # make sure an exception is thrown if we pass in a list of objects, none of which are in the catalogue to prune
        unique_objs = []
        i = 0
        max_i = 5
        while i < max_i:
            obj = np.random.randint(2**32)
            if obj not in all_objs:
                unique_objs.append(obj)
                i += 1

        with pytest.raises(ValueError):
            pruned_cat, dpds = prune_mer_catalogue(mer_cat, unique_objs)
