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
_grid
=====

Provides
--------
 1. Grid: The main grid of pyspread
 2. MainWindowEventHandlers: Event handlers for Grid

"""

import wx.grid

from _events import post_command_event, EventMixin

from _grid_table import GridTable
from _grid_renderer import GridRenderer
from _gui_interfaces import GuiInterfaces
from _menubars import ContextMenu
from _chart_dialog import ChartDialog

from src.config import config

import src.lib.i18n as i18n

import src.lib.xrect as xrect
from src.model.model import CodeArray

from src.actions._grid_actions import AllGridActions

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class Grid(wx.grid.Grid, EventMixin):
    """Pyspread's main grid"""

    def __init__(self, main_window, *args, **kwargs):
        self.main_window = main_window

        self._states()

        self.interfaces = GuiInterfaces(self.main_window)

        dimensions = kwargs.pop("dimensions")

        wx.grid.Grid.__init__(self, main_window, *args, **kwargs)

        # Create new grid
        self.code_array = CodeArray(dimensions)
        post_command_event(self, self.GridActionNewMsg, shape=dimensions)

        _grid_table = GridTable(self, self.code_array)
        self.SetTable(_grid_table, True)

        # Grid renderer draws the grid
        self.grid_renderer = GridRenderer(self.code_array)
        self.SetDefaultRenderer(self.grid_renderer)

        # Context menu for quick access of important functions
        self.contextmenu = ContextMenu(parent=self)

        # Handler classes contain event handler methods
        self.handlers = GridEventHandlers(self)
        self.cell_handlers = GridCellEventHandlers(self)

        # Grid actions
        self.actions = AllGridActions(self)

        # Layout and bindings
        self._layout()
        self._bind()

        # Update toolbars
        self.cell_handlers._update_entry_line((0, 0, 0))
        self.cell_handlers._update_attribute_toolbar((0, 0, 0))

        # Focus on grid so that typing can start immediately
        self.SetFocus()

    def _states(self):
        """Sets grid states"""

        # The currently visible table
        self.current_table = 0

    def _layout(self):
        """Initial layout of grid"""

        self.EnableGridLines(False)

        # Standard row and col sizes for zooming
        self.std_row_size = self.GetRowSize(0)
        self.std_col_size = self.GetColSize(0)

        # Standard row and col label sizes for zooming
        self.col_label_size = self.GetColLabelSize()
        self.row_label_size = self.GetRowLabelSize()

        self.SetRowMinimalAcceptableHeight(1)
        self.SetColMinimalAcceptableWidth(1)

        self.SetCellHighlightPenWidth(0)

    def _bind(self):
        """Bind events to handlers"""

        main_window = self.main_window

        handlers = self.handlers
        c_handlers = self.cell_handlers

        # Non wx.Grid events

        self.Bind(wx.EVT_MOUSEWHEEL, handlers.OnMouseWheel)
        self.Bind(wx.EVT_KEY_DOWN, handlers.OnKey)

        # Grid events

        self.GetGridWindow().Bind(wx.EVT_MOTION, handlers.OnMouseMotion)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, handlers.OnMouseClick)
        self.Bind(wx.EVT_SCROLLWIN, handlers.OnScroll)

        # Context menu

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, handlers.OnContextMenu)

        # Cell code events

        main_window.Bind(self.EVT_CMD_CODE_ENTRY, c_handlers.OnCellText)

        main_window.Bind(self.EVT_CMD_INSERT_BMP, c_handlers.OnInsertBitmap)
        main_window.Bind(self.EVT_CMD_LINK_BMP, c_handlers.OnLinkBitmap)
        main_window.Bind(self.EVT_CMD_INSERT_CHART,
                         c_handlers.OnInsertChartDialog)

        # Cell attribute events

        main_window.Bind(self.EVT_CMD_FONT, c_handlers.OnCellFont)
        main_window.Bind(self.EVT_CMD_FONTSIZE, c_handlers.OnCellFontSize)
        main_window.Bind(self.EVT_CMD_FONTBOLD, c_handlers.OnCellFontBold)
        main_window.Bind(self.EVT_CMD_FONTITALICS,
                    c_handlers.OnCellFontItalics)
        main_window.Bind(self.EVT_CMD_FONTUNDERLINE,
                    c_handlers.OnCellFontUnderline)
        main_window.Bind(self.EVT_CMD_FONTSTRIKETHROUGH,
                    c_handlers.OnCellFontStrikethrough)
        main_window.Bind(self.EVT_CMD_FROZEN, c_handlers.OnCellFrozen)
        main_window.Bind(self.EVT_CMD_MERGE, c_handlers.OnMerge)
        main_window.Bind(self.EVT_CMD_JUSTIFICATION,
                    c_handlers.OnCellJustification)
        main_window.Bind(self.EVT_CMD_ALIGNMENT, c_handlers.OnCellAlignment)
        main_window.Bind(self.EVT_CMD_BORDERWIDTH,
                    c_handlers.OnCellBorderWidth)
        main_window.Bind(self.EVT_CMD_BORDERCOLOR,
                    c_handlers.OnCellBorderColor)
        main_window.Bind(self.EVT_CMD_BACKGROUNDCOLOR,
                    c_handlers.OnCellBackgroundColor)
        main_window.Bind(self.EVT_CMD_TEXTCOLOR, c_handlers.OnCellTextColor)
        main_window.Bind(self.EVT_CMD_ROTATIONDIALOG,
                    c_handlers.OnTextRotationDialog)
        main_window.Bind(self.EVT_CMD_TEXTROTATATION,
                    c_handlers.OnCellTextRotation)

        # Cell selection events

        self.Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL, c_handlers.OnCellSelected)

        # Grid view events

        main_window.Bind(self.EVT_CMD_REFRESH_SELECTION,
                    handlers.OnRefreshSelectedCells)
        main_window.Bind(self.EVT_CMD_DISPLAY_GOTO_CELL_DIALOG,
                    handlers.OnDisplayGoToCellDialog)
        main_window.Bind(self.EVT_CMD_GOTO_CELL, handlers.OnGoToCell)
        main_window.Bind(self.EVT_CMD_ZOOM_IN, handlers.OnZoomIn)
        main_window.Bind(self.EVT_CMD_ZOOM_OUT, handlers.OnZoomOut)
        main_window.Bind(self.EVT_CMD_ZOOM_STANDARD, handlers.OnZoomStandard)

        # Find events
        main_window.Bind(self.EVT_CMD_FIND, handlers.OnFind)
        main_window.Bind(self.EVT_CMD_REPLACE, handlers.OnShowFindReplace)
        main_window.Bind(wx.EVT_FIND, handlers.OnReplaceFind)
        main_window.Bind(wx.EVT_FIND_NEXT, handlers.OnReplaceFind)
        main_window.Bind(wx.EVT_FIND_REPLACE, handlers.OnReplace)
        main_window.Bind(wx.EVT_FIND_REPLACE_ALL, handlers.OnReplaceAll)
        main_window.Bind(wx.EVT_FIND_CLOSE, handlers.OnCloseFindReplace)

        # Grid change events

        main_window.Bind(self.EVT_CMD_INSERT_ROWS, handlers.OnInsertRows)
        main_window.Bind(self.EVT_CMD_INSERT_COLS, handlers.OnInsertCols)
        main_window.Bind(self.EVT_CMD_INSERT_TABS, handlers.OnInsertTabs)

        main_window.Bind(self.EVT_CMD_DELETE_ROWS, handlers.OnDeleteRows)
        main_window.Bind(self.EVT_CMD_DELETE_COLS, handlers.OnDeleteCols)
        main_window.Bind(self.EVT_CMD_DELETE_TABS, handlers.OnDeleteTabs)

        main_window.Bind(self.EVT_CMD_SHOW_RESIZE_GRID_DIALOG,
                                                  handlers.OnResizeGridDialog)

        main_window.Bind(wx.grid.EVT_GRID_ROW_SIZE, handlers.OnRowSize)
        main_window.Bind(wx.grid.EVT_GRID_COL_SIZE, handlers.OnColSize)

        # Undo/Redo events

        main_window.Bind(self.EVT_CMD_UNDO, handlers.OnUndo)
        main_window.Bind(self.EVT_CMD_REDO, handlers.OnRedo)

    _get_selection = lambda self: self.actions.get_selection()
    selection = property(_get_selection, doc="Grid selection")

    # Collison helper functions for grid drawing
    # ------------------------------------------

    def get_visiblecell_slice(self):
        """Returns a tuple of 3 slices that contanins the visible cells"""

        topleft_x = self.YToRow(self.GetViewStart()[1] * self.ScrollLineX)
        topleft_y = self.XToCol(self.GetViewStart()[0] * self.ScrollLineY)
        topleft = (topleft_x, topleft_y)
        row, col = topleft_x + 1, topleft_y + 1  # Ensures visibility

        while self.IsVisible(row, topleft[1], wholeCellVisible=False):
            row += 1
        while self.IsVisible(topleft[0], col, wholeCellVisible=False):
            col += 1
        lowerright = (row, col)  # This cell is *not* visible
        return (slice(topleft[0], lowerright[0]),
                slice(topleft[1], lowerright[1]),
                slice(self.current_table, self.current_table + 1))

    def colliding_cells(self, row, col, textbox):
        """Generates distance, row, col tuples of colliding cells

        Parameters
        ----------
        row: Integer
        \tRow of cell that is tested for collision
        col: Integer
        \tColumn of cell that is tested for collision
        """

        def l1_radius_cells(dist):
            """Generator of cell index tuples with distance dist to o"""

            if not dist:
                yield 0, 0

            else:
                for pos in xrange(-dist, dist + 1):
                    yield pos, dist
                    yield pos, -dist
                    yield dist, pos
                    yield -dist, pos

        def get_max_visible_distance(row, col):
            """Returns maximum distance between current and any visible cell"""

            vis_cell_slice = self.get_visiblecell_slice()
            vis_row_min = vis_cell_slice[0].start
            vis_row_max = vis_cell_slice[0].stop
            vis_col_min = vis_cell_slice[1].start
            vis_col_max = vis_cell_slice[1].stop

            return max(vis_row_max - row, vis_col_max - col,
                       row - vis_row_min, col - vis_col_min)

        for dist in xrange(get_max_visible_distance(row, col)):
            all_empty = True

            for radius_cell in l1_radius_cells(dist + 1):
                __row = radius_cell[0] + row
                __col = radius_cell[1] + col

                if self.IsVisible(__row, __col, wholeCellVisible=False):
                    cell_rect = self.CellToRect(__row, __col)
                    cell_rect = xrect.Rect(cell_rect.x, cell_rect.y,
                                           cell_rect.width, cell_rect.height)
                    if textbox.collides_axisaligned_rect(cell_rect):
                        all_empty = False
                        yield dist + 1, __row, __col

            # If there are no collisions in a circle, we break

            if all_empty:
                break

    def get_block_direction(self, rect_row, rect_col, block_row, block_col):
        """Returns a blocking direction string from UP DOWN RIGHT LEFT"""

        diff_row = rect_row - block_row
        diff_col = rect_col - block_col

        assert not diff_row == diff_col == 0

        if abs(diff_row) <= abs(diff_col):
            # Columns are dominant
            if rect_col < block_col:
                return "RIGHT"
            else:
                return "LEFT"
        else:
            # Rows are dominant
            if rect_row < block_row:
                return "DOWN"
            else:
                return "UP"

# End of class Grid


class GridCellEventHandlers(object):
    """Contains grid cell event handlers incl. attribute events"""

    def __init__(self, grid):
        self.grid = grid

    # Cell code entry events

    def OnCellText(self, event):
        """Text entry event handler"""

        key = self.grid.actions.cursor

        self.grid.actions.set_code(key, event.code)

        event.Skip()

    def OnInsertBitmap(self, event):
        """Insert bitmap event handler"""

        # Get file name
        wildcard = "*"
        message = _("Select bitmap for current cell")
        style = wx.OPEN | wx.CHANGE_DIR
        filepath, __ = self.grid.interfaces.get_filepath_findex_from_user(
                                                    wildcard, message, style)

        bmp = wx.Bitmap(filepath)
        if bmp.Size == (-1, -1):
            # Bitmap could not be read
            return

        key = self.grid.actions.cursor
        code = self.grid.main_window.actions.bmp2code(key, bmp)

        self.grid.actions.set_code(key, code)

    def OnLinkBitmap(self, event):
        """Link bitmap event handler"""

        # Get file name
        wildcard = "*"
        message = _("Select bitmap for current cell")
        style = wx.OPEN | wx.CHANGE_DIR
        filepath, __ = self.grid.interfaces.get_filepath_findex_from_user(
                                                    wildcard, message, style)

        bmp = wx.Bitmap(filepath)
        if bmp.Size == (-1, -1):
            # Bitmap could not be read
            return

        code = "wx.Bitmap('{}')".format(filepath)

        key = self.grid.actions.cursor
        self.grid.actions.set_code(key, code)

    def OnInsertChartDialog(self, event):
        """Chart dialog event handler"""

        cell_code = self.grid.code_array(self.grid.actions.cursor)

        if cell_code is None:
            cell_code = u""

        chart_dialog = ChartDialog(self.grid, cell_code)

        if chart_dialog.ShowModal() == wx.ID_OK:
            code = chart_dialog.get_code()
            key = self.grid.actions.cursor
            self.grid.actions.set_code(key, code)

    # Cell attribute events

    def OnCellFont(self, event):
        """Cell font event handler"""

        self.grid.actions.set_attr("textfont", event.font)

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFontSize(self, event):
        """Cell font size event handler"""

        self.grid.actions.set_attr("pointsize", event.size)

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFontBold(self, event):
        """Cell font bold event handler"""

        try:
            if event.weight == "wxNORMAL":
                weight = wx.NORMAL
            elif event.weight == "wxBOLD":
                weight = wx.BOLD
            else:
                raise ValueError(_("Weight {} unknown").format(event.weight))

            self.grid.actions.set_attr("fontweight", weight)

        except AttributeError:
            self.grid.actions.toggle_attr("fontweight")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFontItalics(self, event):
        """Cell font italics event handler"""

        try:
            if event.style == "wxNORMAL":
                style = wx.NORMAL
            elif event.style == "wxITALIC":
                style = wx.ITALIC
            else:
                raise ValueError(_("Style {} unknown").format(event.style))

            self.grid.actions.set_attr("fontstyle", style)

        except AttributeError:
            self.grid.actions.toggle_attr("fontstyle")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFontUnderline(self, event):
        """Cell font underline event handler"""

        self.grid.actions.toggle_attr("underline")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFontStrikethrough(self, event):
        """Cell font strike through event handler"""

        self.grid.actions.toggle_attr("strikethrough")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellFrozen(self, event):
        """Cell frozen event handler"""

        self.grid.actions.change_frozen_attr()

        self.grid.ForceRefresh()

        event.Skip()

    def OnMerge(self, event):
        """Merge cells event handler"""

        self.grid.actions.merge_selected_cells(self.grid.selection)

        self.grid.ForceRefresh()

    def OnCellJustification(self, event):
        """Horizontal cell justification event handler"""

        self.grid.actions.toggle_attr("justification")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellAlignment(self, event):
        """Vertical cell alignment event handler"""

        self.grid.actions.toggle_attr("vertical_align")

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellBorderWidth(self, event):
        """Cell border width event handler"""

        self.grid.actions.set_border_attr("borderwidth", event.width,
                                                         event.borders)

        event.Skip()

    def OnCellBorderColor(self, event):
        """Cell border color event handler"""

        self.grid.actions.set_border_attr("bordercolor", event.color,
                                                         event.borders)

        event.Skip()

    def OnCellBackgroundColor(self, event):
        """Cell background color event handler"""

        self.grid.actions.set_attr("bgcolor", event.color)

        self.grid.ForceRefresh()

        event.Skip()

    def OnCellTextColor(self, event):
        """Cell text color event handler"""

        self.grid.actions.set_attr("textcolor", event.color)

        self.grid.ForceRefresh()

        event.Skip()

    def OnTextRotationDialog(self, event):
        """Text rotation dialog event handler"""

        cond_func = lambda i: 0 <= i <= 359
        get_int = self.grid.interfaces.get_int_from_user
        angle = get_int(_("Enter text angle in degrees."), cond_func)

        if angle is not None:
            post_command_event(self.grid.main_window,
                               self.grid.TextRotationMsg, angle=angle)

    def OnCellTextRotation(self, event):
        """Cell text rotation event handler"""

        self.grid.actions.set_attr("angle", event.angle)

        self.grid.ForceRefresh()

        event.Skip()

    def _update_entry_line(self, key):
        """Updates the entry line"""

        cell_code = self.grid.code_array(key)

        # Do not display anything if there is no cell code, i. e. it is None
        # Also do not display anything if there is too much code because
        # wx.TextCtrl can only handle up to max_textctrl_length characters

        if cell_code is None or \
           len(cell_code) < int(config["max_textctrl_length"]):

            post_command_event(self.grid, self.grid.EntryLineMsg,
                               text=cell_code)

    def _update_attribute_toolbar(self, key):
        """Updates the attribute toolbar"""

        post_command_event(self.grid, self.grid.ToolbarUpdateMsg, key=key,
                           attr=self.grid.code_array.cell_attributes[key])

    # Cell selection event handlers

    def set_cursor(self, row, col, tab):
        """Sets grid cursor to key"""

        self.grid.SetGridCursor(row, col)
        self._last_selected_cell = row, col, tab
        return

    def OnCellSelected(self, event):
        """Cell selection event handler"""

        key = row, col, tab = event.Row, event.Col, self.grid.current_table

        # Is the cell merged then go to merging cell
        merge_area = self.grid.code_array.cell_attributes[key]["merge_area"]

        if merge_area is not None:
            top, left, bottom, right = merge_area
            if self._last_selected_cell == (top, left, tab):
                if row == top + 1:
                    self.set_cursor(bottom + 1, left, tab)
                    return
                elif col == left + 1:
                    self.set_cursor(top, right + 1, tab)
                    return
            elif (row, col) != (top, left):
                self.set_cursor(top, left, tab)
                return

        # Redraw cursor
        self.grid.ForceRefresh()

        # Update entry line
        self._update_entry_line(key)

        # Update attribute toolbar
        self._update_attribute_toolbar(key)

        self._last_selected_cell = key

        event.Skip()


class GridEventHandlers(object):
    """Contains grid event handlers"""

    def __init__(self, grid):
        self.grid = grid
        self.interfaces = grid.interfaces
        self.main_window = grid.main_window

    def OnMouseMotion(self, event):
        """Mouse motion event handler"""

        grid = self.grid

        pos_x, pos_y = grid.CalcUnscrolledPosition(event.GetPosition())

        row = grid.YToRow(pos_y)
        col = grid.XToCol(pos_x)
        tab = grid.current_table

        key = row, col, tab

        merge_area = self.grid.code_array.cell_attributes[key]["merge_area"]
        if merge_area is not None:
            top, left, bottom, right = merge_area
            row, col = top, left

        grid.actions.on_mouse_over((row, col, tab))

        event.Skip()

    def OnMouseClick(self, event):
        """Grid left mouse click event handler"""

        cursor = self.grid.actions.cursor
        click_key = event.GetRow(), event.GetCol(), self.grid.current_table

        if event.ControlDown() and not event.ShiftDown() and event.AltDown():
            # Add click position as relative reference
            self.grid.actions.append_reference_code(cursor, click_key,
                                                    ref_type="relative")
            # Yield to let grid update happen first
            wx.Yield()
            self.grid.ForceRefresh()

            # Enter entry line to continue editing

            self.grid.main_window.entry_line.SetFocus()
            self.grid.main_window.entry_line.SetInsertionPointEnd()

        elif event.ControlDown() and event.ShiftDown() and not event.AltDown():
            # Add click position as absolute reference
            self.grid.actions.append_reference_code(cursor, click_key,
                                                    ref_type="absolute")
            # Yield to let grid update happen first
            wx.Yield()
            self.grid.ForceRefresh()

            # Enter entry line to continue editing

            self.grid.main_window.entry_line.SetFocus()
            self.grid.main_window.entry_line.SetInsertionPointEnd()

        else:
            event.Skip()

    def OnKey(self, event):
        """Handles non-standard shortcut events"""

        keycode = event.GetKeyCode()

        if event.ControlDown():
            if keycode == 388:
                # Ctrl + + pressed
                post_command_event(self.grid, self.grid.ZoomInMsg)

            elif keycode == 390:
                # Ctrl + - pressed
                post_command_event(self.grid, self.grid.ZoomOutMsg)

            elif keycode == 13:
            # <Ctrl> + <Enter>
                grid = self.grid
                grid.DisableCellEditControl()

                row = self.grid.GetGridCursorRow()
                col = self.grid.GetGridCursorCol()
                tab = grid.current_table
                key = row, col, tab

                val = grid.code_array(key)
                grid.actions.set_code(key, '"' + val + '"')

                grid.MoveCursorDown(False)

        else:
            # No Ctrl pressed

            if keycode == 127:
                # Del pressed

                # Delete cell at cursor
                cursor = self.grid.actions.cursor
                self.grid.actions.delete_cell(cursor)

                # Delete selection
                self.grid.actions.delete_selection()

                # Update grid
                self.grid.ForceRefresh()

                # Do not enter cell
                return

            elif keycode == 27:
                # Esc pressed
                self.grid.actions.need_abort = True

        event.Skip()

    def OnScroll(self, event):
        """Event handler for grid scroll event"""

        event.Skip()

    # Grid view events

    def OnDisplayGoToCellDialog(self, event):
        """Shift a given cell into view"""

        self.interfaces.display_gotocell()

        event.Skip()

    def OnGoToCell(self, event):
        """Shift a given cell into view"""

        row, col, tab = event.key

        self.grid.actions.cursor = row, col, tab
        self.grid.MakeCellVisible(row, col)

        event.Skip()

    def OnRefreshSelectedCells(self, event):
        """Event handler for refreshing the selected cells via menu"""

        self.grid.actions.refresh_selected_frozen_cells()
        self.grid.ForceRefresh()

        event.Skip()

    def OnZoomIn(self, event):
        """Event handler for increasing grid zoom"""

        self.grid.actions.zoom_in()

        event.Skip()

    def OnZoomOut(self, event):
        """Event handler for decreasing grid zoom"""

        self.grid.actions.zoom_out()

        event.Skip()

    def OnZoomStandard(self, event):
        """Event handler for resetting grid zoom"""

        self.grid.actions.zoom(zoom=1.0)

        event.Skip()

    def OnContextMenu(self, event):
        """Context menu event handler"""

        self.grid.PopupMenu(self.grid.contextmenu)

        event.Skip()

    def OnMouseWheel(self, event):
        """Event handler for mouse wheel actions

        Invokes zoom when mouse when Ctrl is also pressed

        """

        if event.ControlDown():
            if event.WheelRotation > 0:
                post_command_event(self.grid, self.grid.ZoomInMsg)
            else:
                post_command_event(self.grid, self.grid.ZoomOutMsg)
        else:
            event.Skip()

    # Find events

    def OnFind(self, event):
        """Find functionality, called from toolbar, returns find position"""

        # Search starts in next cell after the current one
        gridpos = list(self.grid.actions.cursor)
        text, flags = event.text, event.flags
        findpos = self.grid.actions.find(gridpos, text, flags)

        if findpos is None:
            # If nothing is found mention it in the statusbar and return

            statustext = _("'{}' not found.").format(text)

        else:
            # Otherwise select cell with next occurrence if successful
            self.grid.actions.cursor = findpos

            # Update statusbar
            statustext = _(u"Found '{}' in cell {}.").format(text, findpos)

        post_command_event(self.grid.main_window, self.grid.StatusBarMsg,
                           text=statustext)

        event.Skip()

        return findpos

    def OnShowFindReplace(self, event):
        """Calls the find-replace dialog"""

        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self.grid, data, "Find & Replace",
                                   wx.FR_REPLACEDIALOG)
        dlg.data = data  # save a reference to data
        dlg.Show(True)

    def _wxflag2flag(self, wxflag):
        """Converts wxPython integer flag to pyspread flag list"""

        wx_flags = {
            0: ["UP", ],
            1: ["DOWN"],
            2: ["UP", "WHOLE_WORD"],
            3: ["DOWN", "WHOLE_WORD"],
            4: ["UP", "MATCH_CASE"],
            5: ["DOWN", "MATCH_CASE"],
            6: ["UP", "WHOLE_WORD", "MATCH_CASE"],
            7: ["DOWN", "WHOLE_WORD", "MATCH_CASE"],
        }

        return wx_flags[wxflag]

    def OnReplaceFind(self, event):
        """Called when a find operation is started from F&R dialog"""

        event.text = event.GetFindString()
        event.flags = self._wxflag2flag(event.GetFlags())

        self.OnFind(event)

    def OnReplace(self, event):
        """Called when a replace operation is started, returns find position"""

        event.text = find_string = event.GetFindString()
        event.flags = self._wxflag2flag(event.GetFlags())
        replace_string = event.GetReplaceString()

        findpos = self.OnFind(event)

        if findpos is not None:
            self.grid.actions.replace(findpos, find_string, replace_string)

        event.Skip()

        return findpos

    def OnReplaceAll(self, event):
        """Called when a replace all operation is started"""

        while self.OnReplace(event) is not None:
            pass

        event.Skip()

    def OnCloseFindReplace(self, event):
        """Called when the find&replace dialog is closed"""

        event.GetDialog().Destroy()

        event.Skip()

    # Grid change events

    def _get_no_rowscols(self, bbox):
        """Returns tuple of number of rows and cols from bbox"""

        if bbox is None:
            return 1, 1
        else:
            (bb_top, bb_left), (bb_bottom, bb_right) = bbox
            if bb_top is None:
                bb_top = 0
            if bb_left is None:
                bb_left = 0
            if bb_bottom is None:
                bb_bottom = self.grid.code_array.shape[0] - 1
            if bb_right is None:
                bb_right = self.grid.code_array.shape[1] - 1

            return bb_bottom - bb_top + 1, bb_right - bb_left + 1

    def OnInsertRows(self, event):
        """Insert the maximum of 1 and the number of selected rows"""

        no_rows, _ = self._get_no_rowscols(self.grid.selection.get_bbox())

        cursor = self.grid.actions.cursor

        self.grid.actions.insert_rows(cursor[0], no_rows)

        self.grid.GetTable().ResetView()

        event.Skip()

    def OnInsertCols(self, event):
        """Inserts the maximum of 1 and the number of selected columns"""

        _, no_cols = self._get_no_rowscols(self.grid.selection.get_bbox())

        cursor = self.grid.actions.cursor

        self.grid.actions.insert_cols(cursor[1], no_cols)

        self.grid.GetTable().ResetView()

        event.Skip()

    def OnInsertTabs(self, event):
        """Insert one table into grid"""

        self.grid.actions.insert_tabs(self.grid.current_table, 1)

        event.Skip()

    def OnDeleteRows(self, event):
        """Deletes rows from all tables of the grid"""

        no_rows, _ = self._get_no_rowscols(self.grid.selection.get_bbox())

        cursor = self.grid.actions.cursor

        self.grid.actions.delete_rows(cursor[0], no_rows)

        self.grid.GetTable().ResetView()

        event.Skip()

    def OnDeleteCols(self, event):
        """Deletes columns from all tables of the grid"""

        _, no_cols = self._get_no_rowscols(self.grid.selection.get_bbox())

        cursor = self.grid.actions.cursor

        self.grid.actions.delete_cols(cursor[1], no_cols)

        self.grid.GetTable().ResetView()

        event.Skip()

    def OnDeleteTabs(self, event):
        """Deletes tables"""

        self.grid.actions.delete_tabs(self.grid.current_table, 1)

        event.Skip()

    def OnResizeGridDialog(self, event):
        """Resizes current grid by appending/deleting rows, cols and tables"""

        # Get grid dimensions

        new_shape = self.interfaces.get_dimensions_from_user(no_dim=3)

        if new_shape is None:
            return

        self.grid.actions.change_grid_shape(new_shape)

        self.grid.GetTable().ResetView()

        statustext = _("Grid dimensions changed to {}.").format(new_shape)
        post_command_event(self.grid.main_window, self.grid.StatusBarMsg,
                           text=statustext)

        event.Skip()

    # Grid attribute events

    def OnRowSize(self, event):
        """Row size event handler"""

        row = event.GetRowOrCol()
        tab = self.grid.current_table

        rowsize = self.grid.GetRowSize(row) / self.grid.grid_renderer.zoom

        self.grid.code_array.set_row_height(row, tab, rowsize)

        event.Skip()

    def OnColSize(self, event):
        """Column size event handler"""

        col = event.GetRowOrCol()
        tab = self.grid.current_table

        colsize = self.grid.GetColSize(col) / self.grid.grid_renderer.zoom

        self.grid.code_array.set_col_width(col, tab, colsize)

        event.Skip()

    # Undo and redo events

    def OnUndo(self, event):
        """Calls the grid undo method"""

        self.grid.actions.undo()
        self.grid.GetTable().ResetView()
        self.grid.Refresh()

    def OnRedo(self, event):
        """Calls the grid redo method"""

        self.grid.actions.redo()
        self.grid.GetTable().ResetView()
        self.grid.Refresh()

# End of class GridEventHandlers