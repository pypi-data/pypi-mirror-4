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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread. If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_chart_dialog
=============

Chart creation dialog with interactive matplotlib chart widget

Provides
--------

* ChartDialog: Chart dialog class

"""

# Architecture
# ------------
#
# Create widgets <Type>Editor for each type
# types are: bool, int, str, color, iterable, marker_style, line_style
# Each widget has a get_code method and a set_code method
#
# A SeriesBoxPanel is defined by:
# [panel_label, (matplotlib_key, widget, label, tooltip), ...]
#
# A <Seriestype>AttributesPanel(SeriesPanelBase) is defined by:
# [seriestype_key, SeriesBoxPanel, ...]
# It is derived from SeriesBasePanel and provides a widgets attribute
#
# SeriesPanelBase provides a method
# __iter__ that yields (key, code) for each widget
#
# SeriesPanel provides a TreeBook of series types
# It is defined by:
# [(seriestype_key, seriestype_label, seriestype_image,
#                                     <Seriestype>AttributesPanel), ...]
#
# AllSeriesPanel provides a flatnotebook with one tab per series
#
# FigureAttributesPanel is equivalent to a <Seriestype>AttributesPanel
#
# FigurePanel provides a matplotlib chart drawing
#
# ChartDialog provides FigureAttributesPanel, Flatnotebook of SeriesPanels,
#                      FigurePanel


import wx
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import wx.lib.colourselect as csel
from wx.lib.intctrl import IntCtrl, EVT_INT
import wx.lib.agw.flatnotebook as fnb

from _widgets import LineStyleComboBox, MarkerStyleComboBox
from _events import post_command_event, ChartDialogEventMixin
import src.lib.i18n as i18n
import src.lib.charts as charts
from src.lib.parsers import color2code, code2color, parse_dict_strings
from icons import icons

#use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


# --------------
# Editor widgets
# --------------


class BoolEditor(wx.CheckBox, ChartDialogEventMixin):
    """Editor widget for bool values"""

    def __init__(self, *args, **kwargs):
        wx.CheckBox.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_CHECKBOX, self.OnChecked)

    def get_code(self):
        """Returns '0' or '1'"""

        return self.GetValue()

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of bool value

        """

        self.SetValue(bool(code))

    # Properties

    code = property(get_code, set_code)

    # Handlers

    def OnChecked(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class IntegerEditor(IntCtrl, ChartDialogEventMixin):
    """Editor widget for integer values"""

    def __init__(self, *args, **kwargs):
        IntCtrl.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(EVT_INT, self.OnInt)

    def get_code(self):
        """Returns string representation of Integer"""

        return unicode(self.GetValue())

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of integer value

        """

        self.SetValue(int(code))

    # Properties

    code = property(get_code, set_code)

    # Handlers

    def OnInt(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class StringEditor(wx.TextCtrl, ChartDialogEventMixin):
    """Editor widget for string values"""

    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_TEXT, self.OnText)

    def get_code(self):
        """Returns code representation of value of widget"""

        return self.GetValue()

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of widget value

        """

        self.SetValue(code)

    # Properties

    code = property(get_code, set_code)

    # Handlers

    def OnText(self, event):
        """Text entry event handler"""

        post_command_event(self, self.DrawChartMsg)


class ColorEditor(csel.ColourSelect, ChartDialogEventMixin):
    """Editor widget for 3-tuples of floats that represent color"""

    def __init__(self, *args, **kwargs):
        csel.ColourSelect.__init__(self, *args, **kwargs)

        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(csel.EVT_COLOURSELECT, self.OnColor)

    def get_code(self):
        """Returns string representation of Integer"""

        return color2code(self.GetValue())

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tString representation of 3 tuple of float

        """

        self.SetColour(code2color(code))

    # Properties

    code = property(get_code, set_code)

    # Handlers

    def OnColor(self, event):
        """Check event handler"""

        post_command_event(self, self.DrawChartMsg)


class StyleEditorMixin(object):
    """Mixin class for stzle editors that are based on MatplotlibStyleChoice"""

    def bindings(self):
        """Binds events to handlers"""

        self.Bind(wx.EVT_CHOICE, self.OnStyle)

    def get_code(self):
        """Returns code representation of value of widget"""

        selection = self.GetSelection()

        if selection == wx.NOT_FOUND:
            selection = 0

        # Return code string
        return self.styles[selection][1]

    def set_code(self, code):
        """Sets widget from code string

        Parameters
        ----------
        code: String
        \tCode representation of widget value

        """

        for i, (_, style_code) in enumerate(self.styles):
            if code == style_code:
                self.SetSelection(i)

    # Properties

    code = property(get_code, set_code)

    # Handlers
    # --------

    def OnStyle(self, event):
        """Marker style event handler"""

        post_command_event(self, self.DrawChartMsg)


class MarkerStyleEditor(MarkerStyleComboBox, ChartDialogEventMixin,
                        StyleEditorMixin):
    """Editor widget for marker style string values"""

    def __init__(self, *args, **kwargs):
        MarkerStyleComboBox.__init__(self, *args, **kwargs)

        self.bindings()


class LineStyleEditor(LineStyleComboBox, ChartDialogEventMixin,
                      StyleEditorMixin):
    """Editor widget for line style string values"""

    def __init__(self, *args, **kwargs):
        LineStyleComboBox.__init__(self, *args, **kwargs)

        self.bindings()


# -------------
# Panel widgets
# -------------

class SeriesBoxPanel(wx.Panel):
    """Box panel that contains labels and widgets

    Parameters
    ----------

    * panel_label: String
    \tLabel that is displayed left of the widget
    * labels: List of strings
    \tWidget labels
    * widgets: List of class instances
    \tWidget instance list must be as long as labels

    """

    def __init__(self, parent, box_label, labels, widget_clss, widget_codes):

        wx.Panel.__init__(self, parent, -1)

        self.staticbox = wx.StaticBox(self, -1, box_label)

        self.labels = labels

        self.widgets = []

        for widget_cls, widget_code in zip(widget_clss, widget_codes):
            widget = widget_cls(self, -1)
            widget.code = widget_code
            self.widgets.append(widget)

        self.__do_layout()

    def __do_layout(self):
        box_sizer = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer = wx.FlexGridSizer(1, 2, 0, 0)

        for label, widget in zip(self.labels, self.widgets):
            grid_sizer.Add(wx.StaticText(self, -1, label), 1,
                           wx.ALL | wx.EXPAND, 2)
            grid_sizer.Add(widget, 1, wx.ALL | wx.EXPAND, 2)

        grid_sizer.AddGrowableCol(1)
        box_sizer.Add(grid_sizer, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(box_sizer)

        self.Layout()


class SeriesAttributesPanelBase(wx.Panel):
    """Base class for <Seriestype>AttributesPanel and FigureAttributesPanel"""

    def __init__(self, parent, series_data, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.data = {}
        self.data.update(self.default_data)

        self.update(series_data)

        self.box_panels = []

        for box_label, keys in self.boxes:

            labels = []
            widget_clss = []
            widget_codes = []

            for key in keys:
                widget_label, widget_cls, widget_default = self.data[key]

                widget_clss.append(widget_cls)
                widget_codes.append(widget_default)
                labels.append(widget_label)

            self.box_panels.append(SeriesBoxPanel(self, box_label, labels,
                                                  widget_clss, widget_codes))

        self.__do_layout()

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        for box_panel in self.box_panels:
            main_sizer.Add(box_panel, 1, wx.ALL | wx.EXPAND, 2)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableRow(0)
        main_sizer.AddGrowableRow(1)
        main_sizer.AddGrowableRow(2)

        self.SetSizer(main_sizer)

        self.Layout()

    def __iter__(self):
        """Yields (key, code) for each widget"""

        for box_panel, (_, keys) in zip(self.box_panels, self.boxes):
            for widget, key in zip(box_panel.widgets, keys):
                yield key, widget

    def update(self, series_data):
        """Updates self.data from series data

        Parameters
        ----------
         * series_data: dict
        \tKey value pairs for self.data, which correspond to chart attributes

        """

        for key in series_data:
            try:
                data_list = list(self.data[key])
                data_list[2] = str(series_data[key])
                self.data[key] = tuple(data_list)
            except KeyError:
                pass


class PlotAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides plot series attributes in multiple boxed panels"""

    # Data for series plot
    # matplotlib_key, label, widget_cls, default_code

    default_data = {
        "name": (_("Series name"), StringEditor, ""),
        "xdata":  (_("X"), StringEditor, ""),
        "ydata":  (_("Y"), StringEditor, ""),
        "linestyle":  (_("Style"), LineStyleEditor, '-'),
        "linewidth":  (_("Width"), IntegerEditor, "1"),
        "color":  (_("Color"), ColorEditor, "(0, 0, 0)"),
        "marker":  (_("Style"), MarkerStyleEditor, ""),
        "markersize":  (_("Size"), IntegerEditor, "5"),
        "markerfacecolor": (_("Face color"), ColorEditor, "(0, 0, 0)"),
        "markeredgecolor": (_("Edge color"), ColorEditor, "(0, 0, 0)"),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("Data"), ["xdata", "ydata"]),
        (_("Line"), ["linestyle", "linewidth", "color"]),
        (_("Marker"), ["marker", "markersize", "markerfacecolor",
                       "markeredgecolor"]),
    ]


class BarAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides bar series attributes in multiple boxed panels"""

    # Data for bar plot
    # matplotlib_key, label, widget_cls, default_code

    default_data = {
        "name": (_("Series name"), StringEditor, ""),
        "left": (_("Left positions"), StringEditor, ""),
        "height": (_("Bar heights"), StringEditor, ""),
        "width": (_("Bar widths"), StringEditor, ""),
        "bottom": (_("Bar bottoms"), StringEditor, ""),
        "color": (_("Bar color"), ColorEditor, "(0, 0, 0)"),
        "edgecolor": (_("Edge color"), ColorEditor, "(0, 0, 0)"),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("Data"), ["left", "height", "width", "bottom"]),
        (_("Bar"), ["color", "edgecolor"]),
    ]


class FigureAttributesPanel(SeriesAttributesPanelBase):
    """Panel that provides figure attributes in multiple boxed panels"""

    # Data for figure
    # matplotlib_key, label, widget_cls, default_code

    default_data = {
        "xlabel": (_("Label"), StringEditor, ""),
        "xlim": (_("Limits"), StringEditor, ""),
        "xscale": (_("Log"), BoolEditor, False),
        "ylabel": (_("Label"), StringEditor, ""),
        "ylim": (_("Limits"), StringEditor, ""),
        "yscale": (_("Log"), BoolEditor, False),
    }

    # Boxes and their widgets' matplotlib_keys
    # label, [matplotlib_key, ...]

    boxes = [
        (_("X-Axis"), ["xlabel", "xlim", "xscale"]),
        (_("Y-Axis"), ["ylabel", "ylim", "yscale"]),
    ]


class SeriesPanel(wx.Panel):
    """Panel that holds attribute information for one series of the chart"""

    plot_types = [
        {"type": "plot", "panel_class": PlotAttributesPanel},
        {"type": "bar", "panel_class": BarAttributesPanel},
    ]

    def __init__(self, grid, series_dict):

        self.grid = grid

        wx.Panel.__init__(self, grid, -1)

        self.chart_type_book = wx.Treebook(self, -1, style=wx.BK_LEFT)
        self.il = wx.ImageList(24, 24)

        # Add plot panels

        for i, plot_type_dict in enumerate(self.plot_types):
            plot_type = plot_type_dict["type"]
            PlotPanelClass = plot_type_dict["panel_class"]

            series_data = {}
            if plot_type == series_dict["type"]:
                series_data.update(series_dict)

            plot_panel = PlotPanelClass(self, series_data, -1)

            self.chart_type_book.AddPage(plot_panel, plot_type, imageId=i)
            self.il.Add(icons[plot_type_dict["type"]])

        self.plot_type = series_dict["type"]

        self._properties()
        self.__do_layout()

    def _properties(self):
        self.chart_type_book.SetImageList(self.il)

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)
        main_sizer.Add(self.chart_type_book, 1, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(main_sizer)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)

        self.Layout()

    def __iter__(self):
        """Yields all keys of current pot panel"""

        panel = self.get_plot_panel()

        # First yield the panel type because it is not contained in any widget
        chart_type_number = self.chart_type_book.GetSelection()
        chart_type = self.plot_types[chart_type_number]["type"]
        yield "type", chart_type

        for key, code in panel:
            yield key, code

    def get_plot_panel(self):
        """Returns current plot_panel"""

        plot_type_no = self.chart_type_book.GetSelection()
        return self.chart_type_book.GetPage(plot_type_no)

    def set_plot_panel(self, plot_type_no):
        """Sets current plot_panel to plot_type_no"""

        self.chart_type_book.SetSelection(plot_type_no)

    plot_panel = property(get_plot_panel, set_plot_panel)

    def get_plot_type(self):
        """Returns current plot type"""

        return self.plot_types[self.plot_panel]["type"]

    def set_plot_type(self, plot_type):
        """Sets plot type"""

        ptypes = [pt["type"] for pt in self.plot_types]
        self.plot_panel = ptypes.index(plot_type)

    plot_type = property(get_plot_type, set_plot_type)


class AllSeriesPanel(wx.Panel, ChartDialogEventMixin):
    """Panel that holds series panels for all series of the chart"""

    def __init__(self, grid):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | \
                        wx.THICK_FRAME

        self.grid = grid

        self.updating = False  # Set to true if you want to delete all tabs

        wx.Panel.__init__(self, grid, style=style)

        agwstyle = fnb.FNB_NODRAG | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_BOTTOM
        self.series_notebook = fnb.FlatNotebook(self, -1, agwStyle=agwstyle)

        self.__bindings()
        self.__do_layout()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnSeriesChanged)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnSeriesDeleted)

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        main_sizer.Add(self.series_notebook,
                       1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableRow(0)

        self.SetSizer(main_sizer)

        self.Layout()

    def __iter__(self):
        """Yields series panels of the chart's series"""

        no_pages = self.series_notebook.GetPageCount()
        for page_number in xrange(no_pages - 1):
            yield self.series_notebook.GetPage(page_number)

    def update(self, series_list):
        """Updates widget content from series_list

        Parameters
        ----------
        series_list: List of dict
        \tList of dicts with data from all series

        """

        if not series_list:
            self.series_notebook.AddPage(wx.Panel(self, -1), _("+"))
            return

        self.updating = True

        # Delete all tabs in the notebook
        self.series_notebook.DeleteAllPages()

        # Add as many tabs as there are series in code

        for page, attrdict in enumerate(series_list):
            series_panel = SeriesPanel(self.grid, attrdict)
            name = "Series"

            self.series_notebook.InsertPage(page, series_panel, name)

        self.series_notebook.AddPage(wx.Panel(self, -1), _("+"))

        self.updating = False

    # Handlers
    # --------

    def OnSeriesChanged(self, event):
        """FlatNotebook change event handler"""

        selection = event.GetSelection()

        if not self.updating and \
           selection == self.series_notebook.GetPageCount() - 1:
            # Add new series
            new_panel = SeriesPanel(self, {"type": "plot"})
            self.series_notebook.InsertPage(selection, new_panel, _("Series"))

        event.Skip()

    def OnSeriesDeleted(self, event):
        """FlatNotebook closing event handler"""

        # Redraw Chart
        post_command_event(self, self.DrawChartMsg)

        event.Skip()


class FigurePanel(wx.Panel):
    """Panel that draws a matplotlib figure_canvas"""

    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.__do_layout()

    def __do_layout(self):
        self.main_sizer = wx.FlexGridSizer(1, 1, 0, 0)

        self.main_sizer.AddGrowableCol(0)
        self.main_sizer.AddGrowableCol(1)

        self.SetSizer(self.main_sizer)

        self.Layout()

    def _get_figure_canvas(self, figure):
        """Returns figure canvas"""

        return FigureCanvasWxAgg(self, -1, figure)

    def update(self, figure):
        """Updates figure on data change

        Parameters
        ----------
        * figure: matplotlib.figure.Figure
        \tMatplotlib figure object that is displayed in self

        """

        if hasattr(self, "figure_canvas"):
            self.figure_canvas.Destroy()

        self.figure_canvas = self._get_figure_canvas(figure)

        self.figure_canvas.SetSize(self.GetSize())

        self.main_sizer.Add(self.figure_canvas, 1,
                            wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.Layout()
        self.figure_canvas.draw()


class ChartDialog(wx.Dialog, ChartDialogEventMixin):
    """Chart dialog for generating chart generation strings"""

    def __init__(self, grid, code):
        style = wx.RESIZE_BORDER | wx.CLOSE_BOX
        wx.Dialog.__init__(self, grid, -1, style=style)

        self.grid = grid
        self.key = self.grid.actions.cursor
        code = self.grid.code_array(self.key)

        self.figure_attributes_panel = FigureAttributesPanel(self, {}, -1)
        self.all_series_panel = AllSeriesPanel(self)
        self.figure_panel = FigurePanel(self)

        # Figure cache speeds up screen updates if figure code is unchanged
        self.figure_code_old = None
        self.figure_cache = None

        self.cancel_button = wx.Button(self, wx.ID_CANCEL)
        self.ok_button = wx.Button(self, wx.ID_OK)

        self.set_code(code)

        self.__set_properties()
        self.__do_layout()
        self.__bindings()

    def __bindings(self):
        """Binds events to handlers"""

        self.Bind(self.EVT_CMD_DRAW_CHART, self.OnUpdateFigurePanel)

    def __set_properties(self):
        self.SetTitle(_("Insert chart"))
        self.SetSize((1000, 400))

        self.figure_attributes_staticbox = wx.StaticBox(self, -1, _(u"Axes"))
        self.series_staticbox = wx.StaticBox(self, -1, _(u"Series"))

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(2, 3, 2, 2)
        figure_attributes_box_sizer = wx.StaticBoxSizer(
                        self.figure_attributes_staticbox, wx.HORIZONTAL)
        series_box_sizer = wx.StaticBoxSizer(
                        self.series_staticbox, wx.VERTICAL)
        button_sizer = wx.FlexGridSizer(1, 3, 0, 3)

        main_sizer.Add(figure_attributes_box_sizer, 1, wx.EXPAND, 0)
        main_sizer.Add(series_box_sizer, 1, wx.EXPAND, 0)
        main_sizer.Add(self.figure_panel, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)
        main_sizer.Add(button_sizer, wx.ALL | wx.EXPAND, 3)

        main_sizer.AddGrowableRow(0)
        main_sizer.SetItemMinSize(1, (300, 300))
        main_sizer.AddGrowableCol(2)

        figure_attributes_box_sizer.Add(self.figure_attributes_panel,
                                        1, wx.EXPAND, 0)
        series_box_sizer.Add(self.all_series_panel, 1, wx.EXPAND, 0)

        button_sizer.Add(self.ok_button, 0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        button_sizer.Add(self.cancel_button, 0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        button_sizer.AddGrowableCol(2)

        self.SetSizer(main_sizer)
        self.Layout()

    def get_figure(self, code):
        """Returns figure from executing code in grid

        Returns an empty matplotlib figure if code does not eval to a
        matplotlib figure instance.

        Parameters
        ----------
        code: Unicode
        \tUnicode string which contains Python code that should yield a figure

        """

        # Caching for fast response if there are no changes
        if code == self.figure_code_old and self.figure_cache:
            return self.figure_cache

        self.figure_code_old = code

        # key is the current cursor cell of the grid
        key = self.grid.actions.cursor
        cell_result = self.grid.code_array._eval_cell(key, code)

        # If cell_result is matplotlib figure
        if isinstance(cell_result, matplotlib.pyplot.Figure):
            # Return it
            self.figure_cache = cell_result
            return cell_result

        else:
            # Otherwise return empty figure
            self.figure_cache = charts.ChartFigure()

        return self.figure_cache

    # Tuple keys have to be put in parentheses
    tuple_keys = ["xdata", "ydata", "left", "height", "width", "bottom",
                  "xlim", "ylim"]

    # String keys need to be put in "
    string_keys = ["type", "linestyle", "marker"]

    def set_code(self, code):
        """Update widgets from code"""

        # Get attributes from code

        attributes = []
        strip = lambda s: s.strip('u').strip("'").strip('"')
        for attr_dict in parse_dict_strings(unicode(code).strip()[19:-1]):
            attrs = list(strip(s) for s in parse_dict_strings(attr_dict[1:-1]))
            attributes.append(dict(zip(attrs[::2], attrs[1::2])))

        if not attributes:
            return

        # Set widgets from attributes
        # ---------------------------

        # Figure attributes
        figure_attributes = attributes[0]

        for key, widget in self.figure_attributes_panel:
            try:
                obj = figure_attributes[key]

            except KeyError:
                obj = ""

            widget.code = charts.object2code(key, obj)

        # Series attributes
        self.all_series_panel.update(attributes[1:])

    def get_code(self):
        """Returns code that generates figure from widgets"""

        def dict2str(attr_dict):
            """Returns string with dict content with values as code

            Code means that string identifiers are removed

            """

            result = u"{"

            for key in attr_dict:
                code = attr_dict[key]

                if key in self.string_keys:
                    code = repr(code)

                elif code and key in self.tuple_keys and \
                     not (code[0] in ["[", "("] and code[-1] in ["]", ")"]):
                    code = "(" + code + ")"

                elif key in ["xscale", "yscale"]:
                    if code:
                        code = '"log"'
                    else:
                        code = '"linear"'

                if not code:
                    code = 'u""'

                result += repr(key) + ": " + code + ", "

            result = result[:-2] + u"}"

            return result

        # cls_name inludes full class name incl. charts
        cls_name = "charts." + charts.ChartFigure.__name__

        attr_dicts = []

        # Figure attributes
        attr_dict = {}
        # figure_attributes is a dict key2code
        for key, widget in self.figure_attributes_panel:
            if key == "type":
                attr_dict[key] = widget
            else:
                attr_dict[key] = widget.code

        attr_dicts.append(attr_dict)

        # Series_attributes is a list of dicts key2code
        for series_panel in self.all_series_panel:
            attr_dict = {}
            for key, widget in series_panel:
                if key == "type":
                    attr_dict[key] = widget
                else:
                    attr_dict[key] = widget.code

            attr_dicts.append(attr_dict)

        code = cls_name + "("

        for attr_dict in attr_dicts:
            code += dict2str(attr_dict) + ", "

        code = code[:-2] + ")"

        return code

    # Properties
    # ----------

    code = property(get_code, set_code)

    # Handlers
    # --------

    def OnUpdateFigurePanel(self, event):
        """Redraw event handler for the figure panel"""

        self.figure_panel.update(self.get_figure(self.code))