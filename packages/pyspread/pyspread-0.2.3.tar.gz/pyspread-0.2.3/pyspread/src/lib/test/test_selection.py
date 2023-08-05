#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _layer0.py"""

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

import wx
app = wx.App()

TESTPATH = "/".join(os.path.realpath(__file__).split("/")[:-1]) + "/"
sys.path.insert(0, TESTPATH)
sys.path.insert(0, TESTPATH + "/../../..")
sys.path.insert(0, TESTPATH + "/../..")

from src.lib.selection import Selection
import src.actions._grid_actions as grid_actions


class TestSelection(object):
    """Unit tests for Selection"""

    def setup_method(self, method):
        """Creates selection"""

        self.selection = Selection([], [], [], [], [(32, 53), (34, 56)])
        self.SelectionCls = grid_actions.Selection

    def test_nonzero(self):
        """Unit test for __nonzero__"""

        pass

    def test_repr(self):
        """Unit test for __repr__"""

        assert str(self.selection) == \
               "Selection([], [], [], [], [(32, 53), (34, 56)])"

    def test_eq(self):
        """Unit test for __eq__"""

        pass

    def test_contains(self):
        """Unit test for __contains__

        Used in: ele in selection"""

        assert (32, 53) in self.selection
        assert not (23, 34534534) in self.selection

        # Test block selection

        selection = self.SelectionCls([(4, 5)], [(100, 200)], [], [], [])
        cells_in_selection = ((i, j) for i in xrange(4, 100, 5)
                                     for j in xrange(5, 200, 5))

        for cell in cells_in_selection:
            assert cell in selection

        cells_not_in_selection = \
            [(0, 0), (0, 1), (1, 0), (1, 1), (4, 4), (3, 5),
             (100, 201), (101, 200), (101, 201), (10**10, 10**10),
             [0, 0]]

        for cell in cells_not_in_selection:
            assert cell not in selection

        # Test row selection

        # Test column selection

        # Test cell selection

    def test_insert(self):
        """Unit test for insert"""

        pass

    def test_get_bbox(self):
        """Unit test for get_bbox"""

        assert self.selection.get_bbox() == ((32, 53), (34, 56))

        sel_tl, sel_br = [(4, 5)], [(100, 200)]

        selection = self.SelectionCls(sel_tl, sel_br, [], [], [])
        bbox_tl, bbox_br = selection.get_bbox()
        assert bbox_tl == sel_tl[0]
        assert bbox_br == sel_br[0]
