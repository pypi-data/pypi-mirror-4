#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for model.py"""

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import os
import sys

import py.test as pytest
import gmpy
import numpy

import wx
app = wx.App()

TESTPATH = "/".join(os.path.realpath(__file__).split("/")[:-1]) + "/"
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + "/../../..")
sys.path.insert(0, TESTPATH + "/../..")

from src.model.model import KeyValueStore, CellAttributes, DictGrid
from src.model.model import DataArray, CodeArray

from src.lib.selection import Selection


class TestKeyValueStore(object):
    """Unit tests for KeyValueStore"""

    def setup_method(self, method):
        """Creates empty KeyValueStore"""

        self.k_v_store = KeyValueStore()

    def test_missing(self):
        """Test if missing value returns None"""

        key = (1, 2, 3)
        assert self.k_v_store[key] is None

        self.k_v_store[key] = 7

        assert self.k_v_store[key] == 7


class TestCellAttributes(object):
    """Unit tests for CellAttributes"""

    def setup_method(self, method):
        """Creates empty CellAttributes"""

        self.cell_attr = CellAttributes()

    def test_undoable_append(self):
        """Test undoable_append"""

        pass

    def test_getitem(self):
        """Test __getitem__"""

        selection_1 = Selection([(2, 2)], [(4, 5)], [55], [55, 66], [(34, 56)])
        selection_2 = Selection([], [], [], [], [(32, 53), (34, 56)])

        self.cell_attr.append((selection_1, 0, {"testattr": 3}))
        self.cell_attr.append((selection_2, 0, {"testattr": 2}))

        assert self.cell_attr[32, 53, 0]["testattr"] == 2
        assert self.cell_attr[2, 2, 0]["testattr"] == 3


class TestParserMixin(object):
    """Unit tests for ParserMixin"""

    def setup_method(self, method):
        """Creates empty DictGrid"""

        self.dict_grid = DictGrid((10, 10, 10))

    def test_parse_to_shape(self):
        """Unit test for parse_to_shape"""

        line = "12\t12\t32"

        self.dict_grid.parse_to_shape(line)

        assert self.dict_grid.shape == (12, 12, 32)

    def test_parse_to_grid(self):
        """Unit test for parse_to_grid"""

        line = "1\t2\t3\t123"

        self.dict_grid.parse_to_grid(line)

        assert self.dict_grid[(1, 2, 3)] == "123"

    def test_parse_to_attribute(self):
        """Unit test for parse_to_attribute"""

        line = "[]\t[]\t[]\t[]\t[(3, 4)]\t0\t'borderwidth_bottom'\t42"

        self.dict_grid.parse_to_attribute(line)

        assert self.dict_grid.cell_attributes[(3, 4, 0)]\
                                ['borderwidth_bottom'] == 42

    def test_parse_to_height(self):
        """Unit test for parse_to_height"""

        line = "1\t0\t45"

        self.dict_grid.parse_to_height(line)

        assert self.dict_grid.row_heights[(1, 0)] == 45

    def test_parse_to_width(self):
        """Unit test for parse_to_width"""

        line = "1\t0\t43"

        self.dict_grid.parse_to_width(line)

        assert self.dict_grid.col_widths[(1, 0)] == 43

    def test_parse_to_macro(self):
        """Unit test for parse_to_macro"""

        line = "Test"

        self.dict_grid.parse_to_macro(line)

        assert self.dict_grid.macros == line


class TestStringGeneratorMixin(object):
    """Unit tests for StringGeneratorMixin"""

    def setup_method(self, method):
        """Creates empty DictGrid"""

        self.dict_grid = DictGrid((100, 100, 100))

    def test_grid_to_strings(self):
        """Unit test for grid_to_strings"""

        self.dict_grid[(3, 2, 1)] = "42"
        grid_string_list = list(self.dict_grid.grid_to_strings())

        expected_res = [ \
        "[shape]\n",
        "100\t100\t100\n",
        "[grid]\n",
        '3\t2\t1\t42\n',
        ]
        assert grid_string_list == expected_res

    def test_attributes_to_strings(self):
        """Unit test for attributes_to_strings"""

        line = "[]\t[]\t[]\t[]\t[(3, 4)]\t0\t'borderwidth_bottom'\t42"
        self.dict_grid.parse_to_attribute(line)

        attr_string_list = list(self.dict_grid.attributes_to_strings())

        expected_res = [ \
        "[attributes]\n",
        "[]\t[]\t[]\t[]\t[(3, 4)]\t0\t'borderwidth_bottom'\t42\n",
        ]

        assert attr_string_list == expected_res

    def test_heights_to_strings(self):
        """Unit test for heights_to_strings"""

        self.dict_grid.row_heights[(2, 0)] = 77

        expected_res = [ \
        "[row_heights]\n",
        "2\t0\t77\n",
        ]

        height_string_list = list(self.dict_grid.heights_to_strings())

        assert height_string_list == expected_res

    def test_widths_to_strings(self):
        """Unit test for widths_to_strings"""

        self.dict_grid.col_widths[(2, 0)] = 77

        expected_res = [ \
        "[col_widths]\n",
        "2\t0\t77\n",
        ]

        width_string_list = list(self.dict_grid.widths_to_strings())

        assert width_string_list == expected_res

    def test_macros_to_strings(self):
        """Unit test for macros_to_strings"""

        self.dict_grid.macros = "Test"

        expected_res = [ \
        "[macros]\n",
        "Test\n",
        ]

        macros_string_list = list(self.dict_grid.macros_to_strings())

        assert macros_string_list == expected_res


class TestDictGrid(object):
    """Unit tests for DictGrid"""

    def setup_method(self, method):
        """Creates empty DictGrid"""

        self.dict_grid = DictGrid((100, 100, 100))

    def test_getitem(self):
        """Unit test for __getitem__"""

        with pytest.raises(IndexError):
            self.dict_grid[100, 0, 0]

        self.dict_grid[(2, 4, 5)] = "Test"
        assert self.dict_grid[(2, 4, 5)] == "Test"


class TestDataArray(object):
    """Unit tests for DataArray"""

    def setup_method(self, method):
        """Creates empty DataArray"""

        self.data_array = DataArray((100, 100, 100))

    def test_iter(self):
        """Unit test for __iter__"""

        assert list(iter(self.data_array)) == []

        self.data_array[(1, 2, 3)] = "12"
        self.data_array[(1, 2, 4)] = "13"

        assert sorted(list(iter(self.data_array))) == [(1, 2, 3), (1, 2, 4)]

    def test_keys(self):
        """Unit test for keys"""

        assert self.data_array.keys() == []

        self.data_array[(1, 2, 3)] = "12"
        self.data_array[(1, 2, 4)] = "13"

        assert sorted(self.data_array.keys()) == [(1, 2, 3), (1, 2, 4)]

    def test_pop(self):
        """Unit test for pop"""

        self.data_array[(1, 2, 3)] = "12"
        self.data_array[(1, 2, 4)] = "13"

        assert "12" == self.data_array.pop((1, 2, 3))

        assert sorted(self.data_array.keys()) == [(1, 2, 4)]

    def test_shape(self):
        """Unit test for _get_shape and _set_shape"""

        assert self.data_array.shape == (100, 100, 100)

        self.data_array.shape = (10000, 100, 100)

        assert self.data_array.shape == (10000, 100, 100)

    def test_getstate(self):
        """Unit test for __getstate__ (pickle support)"""

        assert "dict_grid" in self.data_array.__getstate__()

    def test_str(self):
        """Unit test for __str__"""

        self.data_array[(1, 2, 3)] = "12"

        data_array_str = str(self.data_array)
        assert data_array_str == "{(1, 2, 3): '12'}"

    def test_slicing(self):
        """Unit test for __getitem__ and __setitem__"""

        self.data_array[0, 0, 0] = "'Test'"
        ##assert len(self.grid.unredo.undolist) == 1
        self.data_array[0, 0, 0] = "'Tes'"
        ##assert len(self.grid.unredo.undolist) == 2

        assert self.data_array[0, 0, 0] == "'Tes'"

    def test_cell_array_generator(self):
        """Unit test for cell_array_generator"""

        cell_array = self.data_array[:5, 0, 0]

        assert list(cell_array) == [None] * 5

        cell_array = self.data_array[:5, :5, 0]

        assert [list(c) for c in cell_array] == [[None] * 5] * 5

        cell_array = self.data_array[:5, :5, :5]

        assert [[list(e) for e in c] for c in cell_array] == \
                                            [[[None] * 5] * 5] * 5

    def test_adjust_shape(self):
        """Unit test for _adjust_shape"""

        self.data_array._adjust_shape(2, 0)
        res = list(self.data_array.shape)
        assert res == [102, 100, 100]

    def test_set_cell_attributes(self):
        """Unit test for _set_cell_attributes"""

        pass

    def test_adjust_cell_attributes(self):
        """Unit test for _adjust_cell_attributes"""

        pass

    def test_insert(self):
        """Unit test for insert operation"""

        self.data_array[2, 3, 4] = 42
        self.data_array.insert(1, 100, 0)

        assert self.data_array.shape == (200, 100, 100)
        assert self.data_array[2, 3, 4] is None

        assert self.data_array[102, 3, 4] == 42

    def test_delete(self):
        """Tests delete operation"""

        self.data_array[2, 3, 4] = "42"
        self.data_array.delete(1, 1, 0)

        assert self.data_array[2, 3, 4] is None
        assert self.data_array[1, 3, 4] == "42"
        print self.data_array.shape
        assert self.data_array.shape == (99, 100, 100)

    def test_set_row_height(self):
        """Unit test for set_row_height"""

        pass

    def test_set_col_width(self):
        """Unit test for set_col_width"""

        pass


class TestCodeArray(object):
    """Unit tests for CodeArray"""

    def setup_method(self, method):
        """Creates empty DataArray"""

        self.code_array = CodeArray((100, 10, 3))

    def test_slicing(self):
        """Unit test for __getitem__ and __setitem__"""

        #Test for item getting, slicing, basic evaluation correctness

        shape = self.code_array.shape
        x_list = [0, shape[0]-1]
        y_list = [0, shape[1]-1]
        z_list = [0, shape[2]-1]
        for x, y, z in zip(x_list, y_list, z_list):
            assert self.code_array[x, y, z] == None
            self.code_array[:x, :y, :z]
            self.code_array[:x:2, :y:2, :z:-1]

        get_shape = numpy.array(self.code_array[:, :, :]).shape
        orig_shape = self.code_array.shape
        assert get_shape == orig_shape

        gridsize = 100
        filled_grid = CodeArray((gridsize, 10, 1))
        for i in [-2**99, 2**99, 0]:
            for j in xrange(gridsize):
                filled_grid[j, 0, 0] = str(i)
                filled_grid[j, 1, 0] = str(i) + '+' + str(j)
                filled_grid[j, 2, 0] = str(i) + '*' + str(j)

            for j in xrange(gridsize):
                assert filled_grid[j, 0, 0] == i
                assert filled_grid[j, 1, 0] == i + j
                assert filled_grid[j, 2, 0] == i * j

            for j, funcname in enumerate(['int', 'gmpy.mpz', 'gmpy.mpq']):
                filled_grid[0, 0, 0] = "gmpy = __import__('gmpy')"
                filled_grid[0, 0, 0]
                filled_grid[1, 0, 0] = "math = __import__('math')"
                filled_grid[1, 0, 0]
                filled_grid[j, 3, 0] = funcname + ' (' + str(i) + ')'

                res = eval(funcname + "(" + "i" + ")")
                assert filled_grid[j, 3, 0] == eval(funcname + "(" + "i" + ")")
        #Test X, Y, Z
        for i in xrange(10):
            self.code_array[i, 0, 0] = str(i)
        assert [self.code_array((i, 0, 0)) for i in xrange(10)] == \
                    map(str, xrange(10))

        assert [self.code_array[i, 0, 0] for i in xrange(10)] == range(10)

        # Test cycle detection

        filled_grid[0, 0, 0] = "numpy.arange(0, 10, 0.1)"
        filled_grid[1, 0, 0] = "sum(S[0,0,0])"

        assert filled_grid[1, 0, 0] == sum(numpy.arange(0, 10, 0.1))

        ##filled_grid[0, 0, 0] = "S[5:10, 1, 0]"
        ##assert filled_grid[0, 0, 0].tolist() == range(7, 12)

    def test_make_nested_list(self):
        """Unit test for _make_nested_list"""

        pass

    def test_has_assignment(self):
        """Unit test for _has_assignment"""

        pass

    def test_eval_cell(self):
        """Unit test for _eval_cell"""

        pass

    def test_execute_macros(self):
        """Unit test for execute_macros"""

        pass

    def test_sorted_keys(self):
        """Unit test for _sorted_keys"""

        code_array = self.code_array

        keys = [(1, 0, 0), (2, 0, 0), (0, 1, 0), (0, 99, 0), (0, 0, 0),
                (0, 0, 99), (1, 2, 3)]
        assert list(code_array._sorted_keys(keys, (0, 1, 0))) == \
             [(0, 1, 0), (0, 99, 0), (1, 2, 3), (0, 0, 99), (0, 0, 0),
              (1, 0, 0), (2, 0, 0)]
        sk = list(code_array._sorted_keys(keys, (0, 3, 0), reverse=True))
        assert sk == [(0, 1, 0), (2, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 99),
              (1, 2, 3), (0, 99, 0)]

    def test_string_match(self):
        """Tests creation of _string_match"""

        code_array = self.code_array

        test_strings = ["", "Hello", " Hello", "Hello ", " Hello ", "Hello\n",
            "THelloT", " HelloT", "THello ", "hello", "HELLO", "sd"]

        search_string = "Hello"

        # Normal search
        flags = []
        results = [None, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, None]
        for test_string, result in zip(test_strings, results):
            res = code_array._string_match(test_string, search_string, flags)
            assert res == result

        flags = ["MATCH_CASE"]
        results = [None, 0, 1, 0, 1, 0, 1, 1, 1, None, None, None]
        for test_string, result in zip(test_strings, results):
            res = code_array._string_match(test_string, search_string, flags)
            assert  res == result

        flags = ["WHOLE_WORD"]
        results = [None, 0, 1, 0, 1, 0, None, None, None, 0, 0, None]
        for test_string, result in zip(test_strings, results):
            res = code_array._string_match(test_string, search_string, flags)
            assert  res == result

    def test_findnextmatch(self):
        """Find method test"""

        code_array = self.code_array

        for i in xrange(100):
            code_array[i, 0, 0] = str(i)

        assert code_array[3, 0, 0] == 3
        assert code_array.findnextmatch((0, 0, 0), "3", "DOWN") == (3, 0, 0)
        assert code_array.findnextmatch((0, 0, 0), "99", "DOWN") == (99, 0, 0)