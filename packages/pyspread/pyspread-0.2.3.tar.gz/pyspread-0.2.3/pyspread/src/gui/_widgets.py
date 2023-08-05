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
_widgets
========

Provides:
---------
  1. PythonSTC: Syntax highlighting editor
  2. ImageComboBox: Base class for image combo boxes
  3. PenWidthComboBox: ComboBox for pen width selection
  4. PenStyleComboBox: ComboBox for pen style selection
  5. MatplotlibStyleChoice: Base class for matplotlib chart style choices
  6. LineStyleComboBox: ChoiceBox for selection matplotlib line styles
  7. MarkerStyleComboBox: ChoiceBox for selection matplotlib marker styles
  8. FontChoiceCombobox: ComboBox for font selection
  9. BorderEditChoice: ComboBox for border selection
 10. BitmapToggleButton: Button that toggles through a list of bitmaps
 11. EntryLine: The line for entering cell code
 12. StatusBar: Main window statusbar
 13. TableChoiceIntCtrl: IntCtrl for choosing the current grid table

"""

import keyword

import wx
import wx.grid
import wx.combo
import wx.stc as stc
from wx.lib.intctrl import IntCtrl, EVT_INT

import src.lib.i18n as i18n

from _events import post_command_event, EntryLineEventMixin, GridCellEventMixin
from _events import StatusBarEventMixin, GridEventMixin, GridActionEventMixin

from icons import icons

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class PythonSTC(stc.StyledTextCtrl):
    """Editor that highlights Python source code.

    Stolen from the wxPython demo.py
    """

    def __init__(self, *args, **kwargs):
        stc.StyledTextCtrl.__init__(self, *args, **kwargs)

        self._style()

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0, 0)

        self.SetViewWhiteSpace(False)
        self.SetUseAntiAliasing(True)

        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # Import symbol style from config file
        for marker in self.fold_symbol_style:
            self.MarkerDefine(*marker)

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                          "face:%(helv)s,size:%(size)d" % self.faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Import text style specs from config file
        for spec in self.text_styles:
            self.StyleSetSpec(*spec)

        self.SetCaretForeground("BLUE")

        self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 30)

    def _style(self):
        """Set editor style"""

        self.fold_symbols = 2

        """
        Fold symbols
        ------------

        The following styles are pre-defined:
          "arrows"      Arrow pointing right for contracted folders,
                        arrow pointing down for expanded
          "plusminus"   Plus for contracted folders, minus for expanded
          "circletree"  Like a flattened tree control using circular headers
                        and curved joins
          "squaretree"  Like a flattened tree control using square headers

        """

        self.faces = {'times': 'Times',
                      'mono': 'Courier',
                      'helv': wx.SystemSettings.GetFont(
                               wx.SYS_DEFAULT_GUI_FONT).GetFaceName(),
                      'other': 'new century schoolbook',
                      'size': 10,
                      'size2': 8,
                     }

        white = "white"
        black = "black"
        gray1 = "#404040"
        gray2 = "#808080"

        self.fold_symbol_styles = {
          "arrows":
          [
            (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_ARROWDOWN, black, black),
            (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_ARROW, black, black),
            (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, black, black),
            (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, black, black),
            (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, white, black),
          ],
          "plusminus":
          [
            (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, white, black),
            (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS,  white, black),
            (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, white, black),
            (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, white, black),
          ],
          "circletree":
          [
            (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_CIRCLEMINUS,
                                                            white, gray1),
            (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_CIRCLEPLUS, white, gray1),
            (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, white, gray1),
            (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE,
                                                            white, gray1),
            (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_CIRCLEPLUSCONNECTED,
                                                            white, gray1),
            (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED,
                                                            white, gray1),
            (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,
                                                            white, gray1),
          ],
          "squaretree":
          [
            (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, white, gray2),
            (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, white, gray2),
            (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, white, gray2),
            (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, white, gray2),
            (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED,
                                                            white, gray2),
            (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED,
                                                            white, gray2),
            (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,
                                                            white, gray2),
          ]
        }

        self.fold_symbol_style = self.fold_symbol_styles["circletree"]

        """
        Text styles
        -----------

        The lexer defines what each style is used for, we just have to define
        what each style looks like.  The Python style set is adapted from
        Scintilla sample property files.

        """

        self.text_styles = [
          (stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % self.faces),
          (stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,"
                                     "size:%(size2)d" % self.faces),
          (stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % self.faces),
          (stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold"),
          (stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold"),
          # Python styles
          # Default
          (stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" %
                                                                self.faces),
          # Comments
          (stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,"
                                  "size:%(size)d" % self.faces),
          # Number
          (stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % self.faces),
          # String
          (stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" %
                                                                self.faces),
          # Single quoted string
          (stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" %
                                                                self.faces),
          # Keyword
          (stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % self.faces),
          # Triple quotes
          (stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % self.faces),
          # Triple double quotes
          (stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % self.faces),
          # Class name definition
          (stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" %
                                                                self.faces),
          # Function or method name definition
          (stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % self.faces),
          # Operators
          (stc.STC_P_OPERATOR, "bold,size:%(size)d" % self.faces),
          # Identifiers
          (stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" %
                                                                self.faces),
          # Comment-blocks
          (stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % self.faces),
          # End of line where string is not closed
          (stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,"
                                "back:#E0C0E0,eol,size:%(size)d" % self.faces),
        ]

    def OnUpdateUI(self, evt):
        """Syntax highlighting while editing"""

        # check for matching braces
        brace_at_caret = -1
        brace_opposite = -1
        char_before = None
        caret_pos = self.GetCurrentPos()

        if caret_pos > 0:
            char_before = self.GetCharAt(caret_pos - 1)
            style_before = self.GetStyleAt(caret_pos - 1)

        # check before
        if char_before and chr(char_before) in "[]{}()" and \
           style_before == stc.STC_P_OPERATOR:
            brace_at_caret = caret_pos - 1

        # check after
        if brace_at_caret < 0:
            char_after = self.GetCharAt(caret_pos)
            style_after = self.GetStyleAt(caret_pos)

            if char_after and chr(char_after) in "[]{}()" and \
               style_after == stc.STC_P_OPERATOR:
                brace_at_caret = caret_pos

        if brace_at_caret >= 0:
            brace_opposite = self.BraceMatch(brace_at_caret)

        if brace_at_caret != -1 and brace_opposite == -1:
            self.BraceBadLight(brace_at_caret)
        else:
            self.BraceHighlight(brace_at_caret, brace_opposite)

    def OnMarginClick(self, evt):
        """When clicked, old and unfold as needed"""

        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.fold_all()
            else:
                line_clicked = self.LineFromPosition(evt.GetPosition())

                if self.GetFoldLevel(line_clicked) & \
                   stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(line_clicked, True)
                        self.expand(line_clicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(line_clicked):
                            self.SetFoldExpanded(line_clicked, False)
                            self.expand(line_clicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(line_clicked, True)
                            self.expand(line_clicked, True, True, 100)
                    else:
                        self.ToggleFold(line_clicked)

    def fold_all(self):
        """Folds/unfolds all levels in the editor"""

        line_count = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for line_num in range(line_count):
            if self.GetFoldLevel(line_num) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(line_num)
                break

        line_num = 0

        while line_num < line_count:
            level = self.GetFoldLevel(line_num)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(line_num, True)
                    line_num = self.expand(line_num, True)
                    line_num = line_num - 1
                else:
                    last_child = self.GetLastChild(line_num, -1)
                    self.SetFoldExpanded(line_num, False)

                    if last_child > line_num:
                        self.HideLines(line_num + 1, last_child)

            line_num = line_num + 1

    def expand(self, line, do_expand, force=False, vislevels=0, level=-1):
        """Multi-purpose expand method from original STC class"""

        lastchild = self.GetLastChild(line, level)
        line += 1

        while line <= lastchild:
            if force:
                if vislevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            elif do_expand:
                self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    self.SetFoldExpanded(line, vislevels - 1)
                    line = self.expand(line, do_expand, force, vislevels - 1)

                else:
                    expandsub = do_expand and self.GetFoldExpanded(line)
                    line = self.expand(line, expandsub, force, vislevels - 1)
            else:
                line += 1

        return line

# end of class PythonSTC


class ImageComboBox(wx.combo.OwnerDrawnComboBox):
    """Base class for image combo boxes

    The class provides alternating backgrounds. Stolen from demo.py

    """

    def OnDrawBackground(self, dc, rect, item, flags):
        """Called for drawing the background area of each item

        Overridden from OwnerDrawnComboBox

        """

        # If the item is selected, or its item is even,
        # or if we are painting the combo control itself
        # then use the default rendering.

        if (item & 1 == 0 or flags & (wx.combo.ODCB_PAINTING_CONTROL |
                                      wx.combo.ODCB_PAINTING_SELECTED)):
            wx.combo.OwnerDrawnComboBox.OnDrawBackground(self, dc,
                                                         rect, item, flags)
            return

        # Otherwise, draw every other background with
        # different color.

        bg_color = wx.Colour(240, 240, 250)
        dc.SetBrush(wx.Brush(bg_color))
        dc.SetPen(wx.Pen(bg_color))
        dc.DrawRectangleRect(rect)


class PenWidthComboBox(ImageComboBox):
    """Combo box for choosing line width for cell borders"""

    def OnDrawItem(self, dc, rect, item, flags):

        if item == wx.NOT_FOUND:
            return

        r = wx.Rect(*rect)  # make a copy
        r.Deflate(3, 5)

        pen_style = wx.SOLID
        if item == 0:
            pen_style = wx.TRANSPARENT
        pen = wx.Pen(dc.GetTextForeground(), item, pen_style)
        pen.SetCap(wx.CAP_BUTT)

        dc.SetPen(pen)

        # Draw the example line in the combobox
        dc.DrawLine(r.x + 5, r.y + r.height / 2,
                    r.x + r.width - 5, r.y + r.height / 2)

# end of class PenWidthComboBox

# Chart dialog widgets for matplotlib interaction
# -----------------------------------------------


class MatplotlibStyleChoice(wx.Choice):
    """Base class for line and marker choice for matplotlib charts"""

    # Style label and code are stored in styles as a list of tuples
    styles = []

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [style[0] for style in self.styles]
        wx.Choice.__init__(self, *args, **kwargs)

    def get_style_code(self, label):
        """Returns code for given label string

        Inverse of get_code

        Parameters
        ----------
        label: String
        \tLlabel string, field 0 of style tuple

        """

        for style in self.styles:
            if style[0] == label:
                return style[1]

        raise ValueError(_("Label {} is invalid.".format(label)))

    def get_label(self, code):
        """Returns string label for given code string

        Inverse of get_code

        Parameters
        ----------
        code: String
        \tCode string, field 1 of style tuple

        """

        for style in self.styles:
            if style[1] == code:
                return style[0]

        raise ValueError(_("Code {} is invalid.".format(code)))


class LineStyleComboBox(MatplotlibStyleChoice):
    """Combo box for choosing line style for matplotlib charts"""

    styles = [
        ("Solid line style", "-"),
        ("Dashed line style", "--"),
        ("Dash-dot line style", "-."),
        ("Dotted line style", ":"),
    ]


class MarkerStyleComboBox(MatplotlibStyleChoice):
    """Choice box for choosing matplotlib chart markers"""

    styles = [
        ("No marker", ""),
        ("Point marker", "."),
        ("Pixel marker", ","),
        ("Circle marker", "o"),
        ("Triangle_down marker", "v"),
        ("Triangle_up marker", "^"),
        ("Triangle_left marker", "<"),
        ("Triangle_right marker", ">"),
        ("Tri_down marker", "1"),
        ("Tri_up marker", "2"),
        ("Tri_left marker", "3"),
        ("Tri_right marker", "4"),
        ("Square marker", "s"),
        ("Pentagon marker", "p"),
        ("Star marker", "*"),
        ("Hexagon1 marker", "h"),
        ("hexagon2 marker", "H"),
        ("Plus marker", "+"),
        ("X marker", "x"),
        ("Diamond marker", "D"),
        ("Thin_diamond marker", "d"),
        ("Vline marker", "|"),
        ("Hline marker", "_"),
    ]


# End of chart dialog widgets for matplotlib interaction
# ------------------------------------------------------


class FontChoiceCombobox(ImageComboBox):
    """Combo box for choosing fonts"""

    def OnDrawItem(self, dc, rect, item, flags):

        if item == wx.NOT_FOUND:
            return

        __rect = wx.Rect(*rect)  # make a copy
        __rect.Deflate(3, 5)

        font_string = self.GetString(item)
        font = wx.Font(wx.DEFAULT, wx.DEFAULT, wx.NORMAL, wx.NORMAL,
                       False, font_string)
        font.SetPointSize(font.GetPointSize() - 2)
        dc.SetFont(font)
        text_width, text_height = dc.GetTextExtent(font_string)
        text_x = __rect.x
        text_y = __rect.y + int((__rect.height - text_height) / 2.0)

        # Draw the example text in the combobox
        dc.DrawText(font_string, text_x, text_y)

# end of class FontChoiceCombobox


class BorderEditChoice(ImageComboBox):
    """Combo box for selecting the cell borders that shall be changed"""

    def OnDrawItem(self, dc, rect, item, flags):

        if item == wx.NOT_FOUND:
            return

        r = wx.Rect(*rect)  # make a copy
        item_name = self.GetItems()[item]

        bmp = icons[item_name]

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(bmp)

        # Draw the border icon in the combobox
        dc.DrawIcon(icon, r.x, r.y)

    def OnMeasureItem(self, item):
        """Returns the height of the items in the popup"""

        item_name = self.GetItems()[item]
        return icons[item_name].GetHeight()

    def OnMeasureItemWidth(self, item):
        """Returns the height of the items in the popup"""

        item_name = self.GetItems()[item]
        return icons[item_name].GetWidth()

# end of class BorderEditChoice


class BitmapToggleButton(wx.BitmapButton):
    """Toggle button that goes through a list of bitmaps

    Parameters
    ----------
    bitmap_list: List of wx.Bitmap
    \tMust be non-empty

    """

    def __init__(self, parent, bitmap_list):

        assert len(bitmap_list) > 0

        self.bitmap_list = []
        for bmp in bitmap_list:
            mask = wx.Mask(bmp, wx.BLUE)
            bmp.SetMask(mask)
            self.bitmap_list.append(bmp)

        self.state = 0

        super(BitmapToggleButton, self).__init__(parent, -1,
                    self.bitmap_list[0], style=wx.BORDER_NONE)

        # For compatibility with toggle buttons
        setattr(self, "GetToolState", lambda x: self.state)

        self.Bind(wx.EVT_LEFT_UP, self.toggle, self)

    def toggle(self, event):
        """Toggles state to next bitmap"""

        if self.state < len(self.bitmap_list) - 1:
            self.state += 1
        else:
            self.state = 0

        self.SetBitmapLabel(self.bitmap_list[self.state])

        try:
            event.Skip()
        except AttributeError:
            pass

        """For compatibility with toggle buttons"""
        setattr(self, "GetToolState", lambda x: self.state)

# end of class BitmapToggleButton


class EntryLine(wx.TextCtrl, EntryLineEventMixin, GridCellEventMixin):
    """"The line for entering cell code"""

    def __init__(self, parent, id=-1, *args, **kwargs):
        wx.TextCtrl.__init__(self, parent, id, *args, **kwargs)

        self.parent = parent
        self.ignore_changes = False

        parent.Bind(self.EVT_ENTRYLINE_MSG, self.OnContentChange)

        self.SetToolTip(wx.ToolTip("Enter Python expression here."))

        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnContentChange(self, event):
        """Event handler for updating the content"""

        if event.text is None:
            self.SetValue(u"")
        else:
            self.SetValue(event.text)

        event.Skip()

    def OnText(self, event):
        """Text event method evals the cell and updates the grid"""

        if not self.ignore_changes:
            post_command_event(self, self.CodeEntryMsg, code=event.GetString())

        event.Skip()

    def OnChar(self, event):
        """Key event method

         * Forces grid update on <Enter> key
         * Handles insertion of cell access code

        """

        if not self.ignore_changes:

            # Handle special keys
            keycode = event.GetKeyCode()

            if keycode == 13:
                # <Enter> pressed --> Focus on grid
                self.parent.grid.SetFocus()

                # Ignore <Ctrl> + <Enter> and Quote content
                if event.ControlDown():
                    self.SetValue('"' + self.GetValue() + '"')

        event.Skip()

# end of class EntryLine


class StatusBar(wx.StatusBar, StatusBarEventMixin):
    """Main window statusbar"""

    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)

        self.SetToolTip(wx.ToolTip("Watch the status bar."))

        parent.Bind(self.EVT_STATUSBAR_MSG, self.OnMessage)

    def OnMessage(self, event):
        """Statusbar message event handler"""

        self.SetStatusText(event.text)

# end of class StatusBar


class TableChoiceIntCtrl(IntCtrl, GridEventMixin, GridActionEventMixin):
    """ComboBox for choosing the current grid table"""

    def __init__(self, parent, no_tabs):
        self.parent = parent
        self.no_tabs = no_tabs

        IntCtrl.__init__(self, parent, limited=True, allow_long=True)

        self.SetMin(0)
        self.SetMax(no_tabs - 1)

        tipmsg = _("For switching tables enter the table number or "
                   "use the mouse wheel.")
        self.SetToolTip(wx.ToolTip(tipmsg))

        # State for preventing to post GridActionTableSwitchMsg
        self.switching = False

        self.Bind(EVT_INT, self.OnInt)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.parent.Bind(self.EVT_CMD_RESIZE_GRID, self.OnResizeGrid)

    def change_max(self, no_tabs):
        """Updates to a new number of tables

        Fixes current table if out of bounds.

        Parameters
        ----------
        no_tabs: Integer
        \tNumber of tables for choice

        """

        self.no_tabs = no_tabs

        if self.GetValue() >= no_tabs:
            self.SetValue(no_tabs - 1)

        self.SetMax(no_tabs - 1)

    # Event handlers

    def OnResizeGrid(self, event):
        """Event handler for grid resizing"""

        self.change_max(event.shape[2])

    def OnInt(self, event):
        """IntCtrl event method that updates the current table"""

        self.SetMax(self.no_tabs - 1)
        if event.GetValue() > self.GetMax():
            print event.GetValue(), self.GetMax()
            self.SetValue(self.GetMax())
            return

        if not self.switching:
            self.switching = True
            post_command_event(self, self.GridActionTableSwitchMsg,
                               newtable=event.GetValue())
            wx.Yield()
            self.switching = False

    def OnMouseWheel(self, event):
        """Mouse wheel event handler"""

        self.SetMax(self.no_tabs - 1)

        if event.GetWheelRotation() > 0:
            new_table = self.GetValue() + 1
        else:
            new_table = self.GetValue() - 1

        if self.IsInBounds(new_table):
            self.SetValue(new_table)

    def OnShapeChange(self, event):
        """Grid shape change event handler"""

        self.change_max(event.shape[2])

        event.Skip()

# end of class TableChoiceIntCtrl