#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Martin Manns
# Distributed under the terms of the GNU General Public License

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
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
Selection
=========

Grid selection representation

"""

from copy import copy

from itertools import izip


class Selection(object):
    """Represents grid selection

    Parameters
    ----------

    block_top_left: List of 2-tuples
    \tTop left edges of all selection rectangles
    block_bottom_right: List of 2-tuples
    \tBottom right edges of all selection rectangles
    rows: List
    \tList of selected rows
    cols: List
    \tList of selected columns
    cells: List of 2-tuples
    \tList of (row, column) tuples of individually selected cells

    """

    def __init__(self, block_top_left, block_bottom_right, rows, cols, cells):
        self.block_tl = block_top_left
        self.block_br = block_bottom_right
        self.rows = rows
        self.cols = cols
        self.cells = cells

    def __nonzero__(self):
        """Returns True iif any attribute is non-empty"""

        return any((self.block_tl,
                    self.block_br,
                    self.rows,
                    self.cols,
                    self.cells))

    def __repr__(self):
        """String output for printing selection"""

        return "Selection" + repr(
                   (self.block_tl,
                    self.block_br,
                    self.rows,
                    self.cols,
                    self.cells))

    def __eq__(self, other):
        assert type(other) is type(self)

        attrs = ("block_tl", "block_br", "rows", "cols", "cells")

        return all(getattr(self, at) == getattr(other, at) for at in attrs)

    def __contains__(self, cell):
        """Returns True iif cell is in selection

        Parameters
        ----------

        cell: 2-Tuple
        \tIndex of cell that is checked if it is inside selection.

        """

        assert len(cell) == 2

        cell_row, cell_col = cell

        # Block selections
        for top_left, bottom_right in izip(self.block_tl, self.block_br):
            top, left = top_left
            bottom, right = bottom_right

            if top <= cell_row <= bottom and left <= cell_col <= right:
                return True

        # Row and column selections

        if cell_row in self.rows or cell_col in self.cols:
            return True

        # Cell selections
        if cell in self.cells:
            return True

        return False

    def __add__(self, value):
        """Shifts selection down and / or right

        Parameters
        ----------

        value: 2-tuple
        \tRows and cols to be shifted up

        """

        delta_row, delta_col = value

        selection = copy(self)

        selection.block_tl = [(t + delta_row, l + delta_col)
                                    for t, l in selection.block_tl]

        selection.block_br = [(t + delta_row, l + delta_col)
                                    for t, l in selection.block_br]

        selection.rows = [row + delta_row for row in selection.rows]

        selection.cols = [col + delta_col for col in selection.cols]

        selection.cells = [(r + delta_row, c + delta_col)
                                    for r, c in selection.cells]

        return selection

    def insert(self, point, number, axis):
        """Inserts number of rows/cols/tabs into selection at point on axis
        Parameters
        ----------

        point: Integer
        \tAt this point the rows/cols are inserted or deleted
        number: Integer
        \tNumber of rows/cols to be inserted, negative number deletes
        axis: Integer in 0, 1
        \tDefines whether rows or cols are affected

        """

        assert axis in [0, 1]

        def build_tuple_list(source_list, point, number, axis):
            """"""

            target_list = []

            for tl in source_list:
                tl_list = list(tl)
                if tl[axis] > point:
                    tl_list[axis] += number
                target_list.append(tuple(tl_list))

            return target_list

        self.block_tl = build_tuple_list(self.block_tl, point, number, axis)

        self.block_br = build_tuple_list(self.block_br, point, number, axis)

        if axis == 0:
            self.rows = [row + number if row > point else row
                            for row in self.rows]
        elif axis == 1:
            self.cols = [col + number if col > point else col
                            for col in self.cols]

        self.cells = build_tuple_list(self.cells, point, number, axis)

    def get_bbox(self):
        """Returns ((top, left), (bottom, right)) of bounding box

        A bounding box is the smallest rectangle that contains all selections.
        Non-specified boundaries are None.

        """

        bb_top, bb_left, bb_bottom, bb_right = [None] * 4

        # Block selections

        for top_left, bottom_right in zip(self.block_tl, self.block_br):
            top, left = top_left
            bottom, right = bottom_right

            if bb_top is None or bb_top > top:
                bb_top = top
            if bb_left is None or bb_left > left:
                bb_left = left
            if bb_bottom is None or bb_bottom < bottom:
                bb_bottom = bottom
            if bb_right is None or bb_right > right:
                bb_right = right

        # Row and column selections

        for row in self.rows:
            if bb_top is None or bb_top > row:
                bb_top = row
            if bb_bottom is None or bb_bottom < row:
                bb_bottom = row

        for col in self.cols:
            if bb_left is None or bb_left > col:
                bb_left = col
            if bb_right is None or bb_right < col:
                bb_right = col

        # Cell selections

        for cell in self.cells:
            cell_row, cell_col = cell

            if bb_top is None or bb_top > cell_row:
                bb_top = cell_row
            if bb_left is None or bb_left > cell_col:
                bb_left = cell_col
            if bb_bottom is None or bb_bottom < cell_row:
                bb_bottom = cell_row
            if bb_right is None or bb_right < cell_col:
                bb_right = cell_col

        if all(val is None for val in [bb_top, bb_left, bb_bottom, bb_right]):
            return None

        return ((bb_top, bb_left), (bb_bottom, bb_right))

    def get_grid_bbox(self, shape):
        """Returns ((top, left), (bottom, right)) of bounding box

        A bounding box is the smallest rectangle that contains all selections.
        Non-specified boundaries are filled i from size.

        Parameters
        ----------

        shape: 3-Tuple of Integer
        \tGrid shape

        """

        (bb_top, bb_left), (bb_bottom, bb_right) = self.get_bbox()

        if bb_top is None:
            bb_top = 0
        if bb_left is None:
            bb_left = 0
        if bb_bottom is None:
            bb_bottom = shape[0]
        if bb_right is None:
            bb_right = shape[1]

        return ((bb_top, bb_left), (bb_bottom, bb_right))