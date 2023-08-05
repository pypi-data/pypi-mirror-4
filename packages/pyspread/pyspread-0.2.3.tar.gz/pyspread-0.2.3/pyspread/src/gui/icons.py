#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
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
icons
=====

Provides:
---------
  1) _ArtProvider: Provides stock and custom icons
  2) Icons: Provides pyspread's icons

"""

import wx

from src.sysvars import get_program_path


class _ArtProvider(wx.ArtProvider):
    """Provides extra icons in addition to the standard ones

    Used only by Icons class

    """

    def __init__(self, theme, icon_size):

        wx.ArtProvider.__init__(self)

        _size_str = "x".join(map(str, icon_size))

        _theme_path = get_program_path() + "share/icons/"
        _icon_path = _theme_path + theme + "/" + _size_str + "/"
        _action_path = _icon_path + "actions/"
        _toggle_path = _icon_path + "toggles/"

        self.extra_icons = {
            "PyspreadLogo": _theme_path + "pyspread.png",
            "EditCopyRes": _action_path + "edit-copy-results.png",
            "FormatTextBold": _action_path + "format-text-bold.png",
            "FormatTextItalic": _action_path + "format-text-italic.png",
            "FormatTextUnderline": _action_path +
                                            "format-text-underline.png",
            "FormatTextStrikethrough": _action_path +
                                            "format-text-strikethrough.png",
            "JustifyRight": _action_path + "format-justify-right.png",
            "JustifyCenter": _action_path + "format-justify-center.png",
            "JustifyLeft": _action_path + "format-justify-left.png",
            "AlignTop": _action_path + "format-text-aligntop.png",
            "AlignCenter": _action_path + "format-text-aligncenter.png",
            "AlignBottom": _action_path + "format-text-alignbottom.png",
            "Freeze": _action_path + "frozen_small.png",
            "Merge": _action_path + "format-merge-table-cells.png",
            "AllBorders": _toggle_path + "border_all.xpm",
            "LeftBorders": _toggle_path + "border_left.xpm",
            "RightBorders": _toggle_path + "border_right.xpm",
            "TopBorders": _toggle_path + "border_top.xpm",
            "BottomBorders": _toggle_path + "border_bottom.xpm",
            "InsideBorders": _toggle_path + "border_inside.xpm",
            "OutsideBorders": _toggle_path + "border_outside.xpm",
            "TopBottomBorders": _toggle_path + "border_top_n_bottom.xpm",
            "MATCH_CASE": _toggle_path + "aA.png",
            "REG_EXP": _toggle_path + "regex.png",
            "WHOLE_WORD": _toggle_path + "wholeword.png",
            "InsertBitmap": _action_path + "insert_bmp.png",
            "LinkBitmap": _action_path + "link_bmp.png",
            "InsertChart": _action_path + "chart_line.png",
            "plot": _action_path + "chart_line.png",  # matplotlib plot chart
            "bar": _action_path + "chart_column.png",  # matplotlib bar chart
            }

    def CreateBitmap(self, artid, client, size):
        """Adds custom images to Artprovider"""

        if artid in self.extra_icons:
            return wx.Bitmap(self.extra_icons[artid], wx.BITMAP_TYPE_ANY)

        else:
            return wx.ArtProvider.GetBitmap(artid, client, size)


class Icons(object):
    """Provides icons for pyspread

    Parameters
    ----------
    icon_set: Integer, defaults to wx.ART_OTHER
    \tIcon set as defined by wxArtProvider
    icon_theme: String, defaults to "Tango"
    \tIcon theme
    icon_size: 2-Tuple of Integer, defaults to (24, 24)
    \tI=Size of icon bitmaps

    """

    theme = "Tango"

    icon_size = (24, 24)
    icon_set = wx.ART_OTHER

    icons = {
        "FileNew": wx.ART_NEW,
        "FileOpen": wx.ART_FILE_OPEN,
        "FileSave": wx.ART_FILE_SAVE,
        "FilePrint": wx.ART_PRINT,
        "EditCut": wx.ART_CUT,
        "EditCopy": wx.ART_COPY,
        "EditPaste": wx.ART_PASTE,
        "Undo": wx.ART_UNDO,
        "Redo": wx.ART_REDO,
        "Find": wx.ART_FIND,
        "FindReplace": wx.ART_FIND_AND_REPLACE,
        "GoUp": wx.ART_GO_UP,
        "GoDown": wx.ART_GO_DOWN,
        "Add": wx.ART_ADD_BOOKMARK,
        "Remove": wx.ART_DEL_BOOKMARK,
        }

    def __init__(self, icon_set=wx.ART_OTHER, icon_theme="Tango",
                 icon_size=(24, 24)):

        self.icon_set = icon_set
        self.icon_theme = icon_theme
        self.icon_size = icon_size

        wx.ArtProvider.Push(_ArtProvider(icon_theme, icon_size))

    def __getitem__(self, icon_name):
        """Returns by bitmap

        Parameters
        ----------
        icon_name: String
        \tString identifier of the icon.

        """

        if icon_name in self.icons:
            icon_name = self.icons[icon_name]

        return wx.ArtProvider.GetBitmap(icon_name, self.icon_set,
                                       self.icon_size)

icons = Icons()