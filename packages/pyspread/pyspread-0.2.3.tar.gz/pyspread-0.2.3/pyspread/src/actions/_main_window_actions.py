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
_main_window_actions.py
=======================

Module for main window level actions.
All non-trivial functionality that results from main window actions
and belongs to the application as whole (in contrast to the grid only)
goes here.

Provides:
---------
  1. ExchangeActions: Actions for foreign format import and export
  2. PrintActions: Actions for printing
  3. ClipboardActions: Actions which affect the clipboard
  4. MacroActions: Actions which affect macros
  5. HelpActions: Actions for getting help
  6. AllMainWindowActions: All main window actions as a bundle

"""

import base64
import bz2
import os

import wx
import wx.html

import lib.i18n as i18n
from src.sysvars import get_help_path

from src.config import config
from src.lib.__csv import CsvInterface, TxtGenerator
from src.gui._printout import PrintCanvas, Printout

from src.gui._events import post_command_event, EventMixin

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class Actions(EventMixin):
    """Actions base class"""

    def __init__(self, grid):
        self.main_window = grid.main_window
        self.grid = grid
        self.code_array = grid.code_array


class ExchangeActions(Actions):
    """Actions for foreign format import and export"""

    def _import_csv(self, path):
        """CSV import workflow"""

        # If path is not set, do nothing
        if not path:
            return

        # Get csv info

        try:
            dialect, has_header, digest_types = \
                self.main_window.interfaces.get_csv_import_info(path)

        except IOError:
            statustext = _("Error opening file {}.").format(path)
            post_command_event(self.main_window, self.StatusBarMsg,
                               text=statustext)
            return

        return CsvInterface(self.main_window,
                            path, dialect, digest_types, has_header)

    def _import_txt(self, path):
        """Whitespace-delimited txt import workflow. This should be fast."""

        return TxtGenerator(self.main_window, path)

    def import_file(self, filepath, filterindex):
        """Imports external file

        Parameters
        ----------

        filepath: String
        \tPath of import file
        filterindex: Integer
        \tIndex for type of file, 0: csv, 1: tab-delimited text file

        """

        # Mark content as changed
        post_command_event(self.main_window, self.ContentChangedMsg,
                           changed=True)

        if filterindex == 0:
            # CSV import option choice
            return self._import_csv(filepath)
        elif filterindex == 1:
            # TXT import option choice
            return self._import_txt(filepath)
        else:
            msg = _("Unknown import choice {}.").format(filterindex)
            short_msg = _('Error reading CSV file')

            self.main_window.interfaces.display_warning(msg, short_msg)

    def _export_csv(self, filepath, data):
        """CSV import workflow"""

        # Get csv info

        csv_info = self.main_window.interfaces.get_csv_export_info(data)

        if csv_info is None:
            return

        try:
            dialect, digest_types, has_header = csv_info
        except TypeError:
            return

        # Export CSV file

        csv_interface = CsvInterface(filepath, dialect, digest_types,
                                     has_header)

        try:
            csv_interface.write(data)

        except IOError, err:
            msg = _("The file {} could not be fully written\n \n"
                    "Error message:\n{}").format(filepath, err)
            short_msg = _('Error writing CSV file')
            self.main_window.interfaces.display_warning(msg, short_msg)

    def export_file(self, filepath, filterindex, data):
        """Exports external file. Only CSV supported yet."""

        self._export_csv(filepath, data)


class PrintActions(Actions):
    """Actions for printing"""

    def print_preview(self, print_area, print_data):
        """Launch print preview"""

        # Create the print canvas
        canvas = PrintCanvas(self.main_window, self.grid, print_area)

        printout = Printout(canvas)
        printout2 = Printout(canvas)

        preview = wx.PrintPreview(printout, printout2, print_data)

        if not preview.Ok():
            print "Printout preview failed.\n"
            return

        pfrm = wx.PreviewFrame(preview, self.main_window, _("Print preview"))

        pfrm.Initialize()
        pfrm.SetPosition(self.main_window.GetPosition())
        pfrm.SetSize(self.main_window.GetSize())
        pfrm.Show(True)

    def printout(self, print_area, print_data):
        """Print out print area

        See:
        http://aspn.activestate.com/ASPN/Mail/Message/wxpython-users/3471083

        """

        pdd = wx.PrintDialogData(print_data)
        printer = wx.Printer(pdd)

        # Create the print canvas
        canvas = PrintCanvas(self.main_window, self.grid, print_area)

        printout = Printout(canvas)

        if printer.Print(self.main_window, printout, True):
            self.print_data = \
                wx.PrintData(printer.GetPrintDialogData().GetPrintData())

        printout.Destroy()
        canvas.Destroy()


class ClipboardActions(Actions):
    """Actions which affect the clipboard"""

    def cut(self, selection):
        """Cuts selected cells and returns data in a tab separated string

        Parameters
        ----------

        selection: Selection object
        \tSelection of cells in current table that shall be copied

        """

        # Call copy with delete flag

        return self.copy(selection, delete=True)

    def _get_code(self, key):
        """Returns code for given key (one cell)

        Parameters
        ----------

        key: 3-Tuple of Integer
        \t Cell key

        """

        data = self.grid.code_array(key)
        self.grid.code_array.result_cache.clear()

        return data

    def copy(self, selection, getter=None, delete=False):
        """Returns code from selection in a tab separated string

        Cells that are not in selection are included as empty.

        Parameters
        ----------

        selection: Selection object
        \tSelection of cells in current table that shall be copied
        getter: Function, defaults to _get_code
        \tGetter function for copy content
        delete: Bool
        \tDeletes all cells inside selection

        """

        if getter is None:
            getter = self._get_code

        tab = self.grid.current_table

        selection_bbox = selection.get_bbox()

        if not selection_bbox:
            # There is no selection
            bb_top, bb_left = self.grid.actions.cursor[:2]
            bb_bottom, bb_right = bb_top, bb_left
        else:
            replace_none = self.main_window.grid.actions._replace_bbox_none
            (bb_top, bb_left), (bb_bottom, bb_right) = \
                            replace_none(selection.get_bbox())

        data = []

        for __row in xrange(bb_top, bb_bottom + 1):
            data.append([])

            for __col in xrange(bb_left, bb_right + 1):
                # Only copy content if cell is in selection or
                # if there is no selection

                if (__row, __col) in selection or not selection_bbox:
                    content = getter((__row, __col, tab))

                    # Delete cell if delete flag is set

                    if delete:
                        try:
                            self.grid.code_array.pop((__row, __col, tab))

                        except KeyError:
                            pass

                    # Store data

                    if content is None:
                        data[-1].append(u"")

                    else:
                        data[-1].append(content)

                else:
                    data[-1].append(u"")

        return "\n".join("\t".join(line) for line in data)

    def _get_result_string(self, key):
        """Returns unicode string of result for given key (one cell)

        Parameters
        ----------

        key: 3-Tuple of Integer
        \t Cell key

        """

        row, col, tab = key

        return unicode(self.grid.code_array[row, col, tab])

    def copy_result(self, selection):
        """Returns result

        If selection consists of one cell only and result is a bitmap then
        the bitmap is returned.
        Otherwise the method returns string representations of the result
        for the given selection in a tab separated string.

        """

        bbox = selection.get_bbox()

        if not bbox:
            # There is no selection
            bb_top, bb_left = self.grid.actions.cursor[:2]
            bb_bottom, bb_right = bb_top, bb_left
        else:
            # Thereis a selection
            (bb_top, bb_left), (bb_bottom, bb_right) = bbox

        if bb_top == bb_bottom and bb_left == bb_right:
            # We have  a single selection

            tab = self.grid.current_table
            result = self.grid.code_array[bb_top, bb_left, tab]

            if type(result) is wx._gdi.Bitmap:
                # the result is a bitmap
                return result

        # So we have result strings to be returned
        getter = self._get_result_string

        return self.copy(selection, getter=getter)

    def bmp2code(self, key, bmp):
        """Pastes bitmap into single cell"""

        assert type(bmp) is wx._gdi.Bitmap

        row, col, tab = key
        width = self.grid.GetColSize(col) / self.grid.grid_renderer.zoom
        height = self.grid.GetRowSize(row) / \
                    self.grid.grid_renderer.zoom

        code_str = ""
        code_template = \
            "wx.BitmapFromImage(wx.ImageFromData(" + \
            "{width}, {height}, bz2.decompress(base64.b64decode('{data}'))))"

        # Fix length limitation of wx.TextCtrl
        # Therefore scale down image until text length < max_textctrl_length

        while not code_str or \
              len(code_str) > int(config["max_textctrl_length"]):

            img = bmp.ConvertToImage()

            img.Rescale(width, height, quality=wx.IMAGE_QUALITY_HIGH)

            data = base64.b64encode(bz2.compress(img.GetData(), 9))

            code_str = code_template.format(width=img.GetWidth(),
                                            height=img.GetHeight(), data=data)

            width *= 0.9
            height *= 0.9

        return code_str

    def paste(self, key, data):
        """Pastes data into grid

        Parameters
        ----------

        key: 2-Tuple of Integer
        \tTop left cell
        data: String or wx.Bitmap
        \tTab separated string of paste data
        \tor paste data image
        """

        if type(data) is wx._gdi.Bitmap:
            code_str = self.bmp2code(key, data)
            data_gen = [[code_str]]
        else:
            data_gen = (line.split("\t") for line in data.split("\n"))

        self.grid.actions.paste(key[:2], data_gen)

        self.main_window.grid.ForceRefresh()


class MacroActions(Actions):
    """Actions which affect macros"""

    def replace_macros(self, macros):
        """Replaces macros"""

        self.grid.code_array.macros = macros

    def execute_macros(self):
        """Executes macros and marks grid as changed"""

        # Mark content as changed
        post_command_event(self.main_window, self.ContentChangedMsg,
                           changed=True)

        self.grid.code_array.execute_macros()

    def open_macros(self, filepath):
        """Loads macros from file and marks grid as changed

        Parameters
        ----------
        filepath: String
        \tPath to macro file

        """

        try:
            macro_infile = open(filepath, "r")

        except IOError:
            statustext = _("Error opening file {}.").format(filepath)
            post_command_event(self.main_window, self.StatusBarMsg,
                               text=statustext)

            return False

        # Mark content as changed
        post_command_event(self.main_window, self.ContentChangedMsg,
                           changed=True)

        macrocode = macro_infile.read()
        macro_infile.close()

        self.grid.code_array.macros += "\n" + macrocode.strip("\n")

        self.main_window.grid.actions.enter_safe_mode()
        post_command_event(self.main_window, self.SafeModeEntryMsg)

    def save_macros(self, filepath, macros):
        """Saves macros to file

        Parameters
        ----------
        filepath: String
        \tPath to macro file
        macros: String
        \tMacro code

        """

        macro_outfile = open(filepath, "w")
        macro_outfile.write(macros)
        macro_outfile.close()


class HelpActions(Actions):
    """Actions for getting help"""

    def launch_help(self, helpname, filename):
        """Generic help launcher

        Launches HTMLWindow that shows content of filename
        or the Internet page with the filename url

        Parameters
        ----------

        filename: String
        \thtml file or url

        """

        # Set up window

        position = config["help_window_position"]
        size = config["help_window_size"]

        help_window = wx.Frame(self.main_window, -1, helpname, position, size)
        help_htmlwindow = wx.html.HtmlWindow(help_window, -1, (0, 0), size)

        help_window.Bind(wx.EVT_MOVE, self.OnHelpMove)
        help_window.Bind(wx.EVT_SIZE, self.OnHelpSize)

        # Get help data
        current_path = os.getcwd()
        os.chdir(get_help_path())

        try:
            help_file = open(filename, "r")
            help_html = help_file.read()
            help_file.close()
            help_htmlwindow.SetPage(help_html)

        except IOError:

            help_htmlwindow.LoadPage(filename)

        # Show tutorial window

        help_window.Show()

        os.chdir(current_path)

    def OnHelpMove(self, event):
        """Help window move event handler stores position in config"""

        position = event.GetPosition()
        config["help_window_position"] = repr((position.x, position.y))

        event.Skip()

    def OnHelpSize(self, event):
        """Help window size event handler stores size in config"""

        size = event.GetSize()
        config["help_window_size"] = repr((size.width, size.height))

        event.Skip()


class AllMainWindowActions(ExchangeActions, PrintActions,
                           ClipboardActions, MacroActions, HelpActions):
    """All main window actions as a bundle"""

    pass