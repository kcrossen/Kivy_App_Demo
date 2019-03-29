#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import kivy
kivy.require('1.9.0')

Initialize_Window_Width = 1280
Initialize_Window_Height = 800

from kivy.config import Config
Config.set('graphics', 'width', str(Initialize_Window_Width))
Config.set('graphics', 'height', str(Initialize_Window_Height))

from kivy.utils import platform as Kivy_Platform

from kivy.lang.builder import Builder

from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label

from kivy.uix.image import Image # , AsyncImage

from kivy.clock import Clock

from kivy.graphics import Rectangle, Color

from kivy.properties import ListProperty
from kivy.factory import Factory

import os, sys
import platform

import datetime, calendar

import math

execution_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
os_platform = platform.system()

path_to_time_slider_cursor = ""
path_to_time_slider_cursor_disabled = ""
path_to_cwremote_screen_image = ""

if (os_platform == "Darwin"):
    execution_directory = execution_directory.split("CW_Remote.app")[0]

    def resource_path ( relative_path ):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = execution_directory

        return os.path.join(base_path, relative_path)

    path_to_icon_image = resource_path(os.path.join("data", "cwremote-icon-512.png"))
    path_to_time_slider_cursor = resource_path(os.path.join("data", "time_slider_cursor.png"))
    path_to_time_slider_cursor_disabled = resource_path(os.path.join("data", "time_slider_cursor_disabled.png"))
    path_to_cwremote_screen_image = resource_path(os.path.join("data", "CW_Remote_Screen.png"))

    Config.set('kivy','window_icon', path_to_icon_image)
    Config.write()

elif (os_platform == "Linux"):
    if (Kivy_Platform == "android"):
        pass
elif (os_platform == "Windows"):
    pass
else:
    pass


# Convenience function to bound a value
def bound ( low, high, value ):
    return max(low, min(high, value))


# Local wall time, this works for New York City
class Time_Zone ( datetime.tzinfo ):
    def __init__(self, offset_in_minutes):
        super(Time_Zone, self).__init__()
        self.offset = offset_in_minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.offset)

    def tzname(self, dt):
        return ""

    def dst(self, dt):
        return datetime.timedelta(0)

UTC_Time_Zone = Time_Zone(0)
Eastern_Daylight_Time_Zone = Time_Zone(-4 * 60)
Eastern_Standard_Time_Zone = Time_Zone(-5 * 60)

def NYC_Wall_DateTime_Offset ( Time_Zone_Aware_DateTime ):
    # In the US, since 2007, DST starts at 2am (standard time) on the second
    # Sunday in March, which is the first Sunday on or after Mar 8.
    # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
    datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Standard_Time_Zone)

    # Test whether in primetime
    begin_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
    begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))

    end_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
    end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))

    if ((datetime_nyc_wall >= begin_daylight_savings) and (datetime_nyc_wall <= end_daylight_savings)):
        datetime_nyc_wall_offset = "-0400"
    else: datetime_nyc_wall_offset = "-0500"

    return datetime_nyc_wall_offset

def NYC_Wall_DateTime ( Time_Zone_Aware_DateTime ):
    # In the US, since 2007, DST starts at 2am (standard time) on the second
    # Sunday in March, which is the first Sunday on or after Mar 8.
    # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
    datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Standard_Time_Zone)

    # Test whether in primetime
    begin_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
    begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))

    end_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
    end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))

    if ((datetime_nyc_wall >= begin_daylight_savings) and (datetime_nyc_wall <= end_daylight_savings)):
        datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Daylight_Time_Zone)

    return datetime_nyc_wall

def Return_NYC_Wall_Time_String ( UTC_Datetime=None, NYC_Wall_Datetime=None, Time_Zone_Indicator="" ):
    if (UTC_Datetime is not None):
        datetime_NYC_Wall = NYC_Wall_DateTime(UTC_Datetime)
    elif (NYC_Wall_Datetime is not None):
        datetime_NYC_Wall = NYC_Wall_Datetime
    else:
        datetime_NYC_Wall = None

    isoformatted_datetime_NYC_Wall = datetime_NYC_Wall.isoformat()
    if (Time_Zone_Indicator == "E"):
        return isoformatted_datetime_NYC_Wall[:-6]

    if (datetime_NYC_Wall is not None):
        return (isoformatted_datetime_NYC_Wall + Time_Zone_Indicator)
    else: return "Error"

def Period_Span_NYC_Wall_Time ( Period_Hours, Period_End_Hours_Ago ):
    datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
    period_end_utc = datetime_now_utc - datetime.timedelta(hours=Period_End_Hours_Ago)
    period_begin_utc = period_end_utc - datetime.timedelta(hours=Period_Hours)

    period_begin_NYC_Wall = NYC_Wall_DateTime(period_begin_utc)
    period_end_NYC_Wall = NYC_Wall_DateTime(period_end_utc)

    period_begin_nyc_wall_string = \
        Return_NYC_Wall_Time_String(NYC_Wall_Datetime=period_begin_NYC_Wall, Time_Zone_Indicator="E")[:-10].replace("T", " ")
    period_end_nyc_wall_string = \
        Return_NYC_Wall_Time_String(NYC_Wall_Datetime=period_end_NYC_Wall, Time_Zone_Indicator="E")[:-10].replace("T", " ")

    return (calendar.day_abbr[period_begin_NYC_Wall.weekday()] + " " + period_begin_nyc_wall_string + "NYC to " +
            calendar.day_abbr[period_end_NYC_Wall.weekday()] + " " + period_end_nyc_wall_string + "NYC")

def Parse_ISO_DateTime_String ( ISO_DateTime_String ):
    if (ISO_DateTime_String.endswith('Z')):
        ISO_DateTime_String = ISO_DateTime_String[:-1] + "+00:00"
    # "2019-01-03T00:00:05.522864Z"
    # "2017-04-27T04:02:59.008000+00:00"
    #  00000000001111111111222222222233
    #  01234567890123456789012345678901
    iso_microseconds = 0
    iso_timezone_string = ''
    if (len(ISO_DateTime_String) == 19):
        # No microseconds and no time zone specification
        # Interpret this as NYC wall time
        iso_microseconds = 0
        iso_timezone_string = ''
    elif ((len(ISO_DateTime_String) == 26) and (ISO_DateTime_String[19] == '.')):
        # Microseconds but no time zone specification
        # Interpret this as NYC wall time
        iso_microseconds = int(ISO_DateTime_String[20:26])
        iso_timezone_string = ''
    elif ((ISO_DateTime_String[19] == '+') or (ISO_DateTime_String[19] == '-')):
        # No microseconds but having time zone specification
        iso_microseconds = 0
        iso_timezone_string = ISO_DateTime_String[19:]
    elif ((ISO_DateTime_String[19] == '.') and
          ((ISO_DateTime_String[26] == '+') or (ISO_DateTime_String[26] == '-'))):
        # Both microseconds plus time zone specification
        iso_microseconds = int(ISO_DateTime_String[20:26])
        iso_timezone_string = ISO_DateTime_String[26:]
    # "2016-07-09T03:27:27-0400"
    #  00000000001111111111222222
    #  01234567890123456789012345
    # "2016-07-09T03:27:27-04:00"
    # Compute UTC offset, supporting all forms: "+0400", "-0400", "+04:00", and "-04:00"
    if (len(iso_timezone_string) == 0):
        # In the US, since 2007, DST starts at 2am (standard time) on the second
        # Sunday in March, which is the first Sunday on or after Mar 8.
        # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
        begin_daylight_savings = \
            datetime.datetime(year=int(ISO_DateTime_String[0:4]), month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
        begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))

        end_daylight_savings = \
            datetime.datetime(year=int(ISO_DateTime_String[0:4]), month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
        end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))

        datetime_EST = \
           datetime.datetime(int(ISO_DateTime_String[0:4]), # year
                             int(ISO_DateTime_String[5:7]), # month
                             int(ISO_DateTime_String[8:10]), # day
                             int(ISO_DateTime_String[11:13]), # hour
                             int(ISO_DateTime_String[14:16]), # minute
                             int(ISO_DateTime_String[17:19]), # second
                             iso_microseconds, # microseconds
                             Eastern_Standard_Time_Zone)

        if ((datetime_EST >= begin_daylight_savings) and (datetime_EST <= end_daylight_savings)):
            minutes_offset = -4 * 60  # Eastern_Daylight_Time_Zone
        else: minutes_offset = -5 * 60 # Eastern_Standard_Time_Zone

    elif (iso_timezone_string[3] == ':'):
        minutes_offset = (60 * int(iso_timezone_string[1:3])) + int(iso_timezone_string[4:6])
    else:
        minutes_offset = (60 * int(iso_timezone_string[1:3])) + int(iso_timezone_string[3:5])
    if ((len(iso_timezone_string) > 0) and
        (iso_timezone_string[0] == '-')): minutes_offset = -minutes_offset

    # Return ISO_DateTime_String as UTC datetime
    return datetime.datetime(int(ISO_DateTime_String[0:4]), # year
                             int(ISO_DateTime_String[5:7]), # month
                             int(ISO_DateTime_String[8:10]), # day
                             int(ISO_DateTime_String[11:13]), # hour
                             int(ISO_DateTime_String[14:16]), # minute
                             int(ISO_DateTime_String[17:19]), # second
                             iso_microseconds, # microseconds
                             Time_Zone(minutes_offset)).astimezone(UTC_Time_Zone)


from Graph_Index_0 import Graph_Index_0
from Graph_Index_1 import Graph_Index_1

import matplotlib

matplotlib.use('AGG')

from matplotlib_backend_kivyagg import FigureCanvasKivyAgg as FigureCanvas
import matplotlib.pyplot as plotter
from matplotlib.dates import MinuteLocator, HourLocator, DayLocator, DateFormatter


def Get_Metric_Statistics_Datapoints(Metric_Index, Perion_End_UTC, Period_Hours):

    if (Metric_Index == 0): return Graph_Index_0
    else: return Graph_Index_1

def Metric_Statistics_Datapoints_Time_and_Values(Metric_Statistics_Datapoints, Y_Factor):
    data_point_list = []
    for data_point in Metric_Statistics_Datapoints:
        data_datetime = Parse_ISO_DateTime_String(data_point["Timestamp"])
        nyc_wall_time_offset = NYC_Wall_DateTime_Offset(data_datetime)
        data_datetime = data_datetime + datetime.timedelta(hours=int(nyc_wall_time_offset) / 100)
        data_maximum = data_point["Maximum"] * Y_Factor
        data_average = data_point["Average"] * Y_Factor
        data_point_list.append((data_datetime, data_maximum, data_average))
    data_point_list.sort()

    data_time_list = [time for time, max, avg in data_point_list]
    data_max_list = [max for time, max, avg in data_point_list]
    data_avg_list = [avg for time, max, avg in data_point_list]
    return (data_time_list, data_max_list, data_avg_list)


every_day = tuple([day for day in range(31)])

every_hour = tuple([hour for hour in range(24)])
every_two_hours = tuple([(2 * hour) for hour in range(24 // 2)])
every_three_hours = tuple([(3 * hour) for hour in range(24 // 3)])
every_four_hours = tuple([(4 * hour) for hour in range(24 // 4)])
every_six_hours = tuple([(6 * hour) for hour in range(24 // 6)])
every_twelve_hours = tuple([(12 * hour) for hour in range(24 // 12)])

every_five_minutes_labeled = tuple([(5 * minute) for minute in range(60 // 5) if (minute > 0)])
every_ten_minutes_labeled = tuple([(10 * minute) for minute in range(60 // 10) if (minute > 0)])
every_fifteen_minutes_labeled = tuple([(15 * minute) for minute in range(60 // 15) if (minute > 0)])
every_thirty_minutes_labeled = tuple([(30 * minute) for minute in range(60 // 30) if (minute > 0)])
every_thirty_minutes = tuple([(30 * minute) for minute in range(60 // 30)])


def Prepare_Get_Metric_Statistics_Figure(Mertric_Statistics_List,
                                         Period_Value, Graph_Width, Graph_Height,
                                         Close_Existing_Plot_Figure):
    if (Close_Existing_Plot_Figure is not None): plotter.close(Close_Existing_Plot_Figure)

    line_width = 0.75

    plot_figure = plotter.figure(figsize=((Graph_Width / 100), (Graph_Height / 100)), dpi=100)

    axes = plot_figure.gca()
    axis_2 = axes.twinx()

    # Store tuples of (text, text_color) for the two axes
    # There could be none, one, or two
    left_y_axis_labels = []
    right_y_axis_labels = []

    minimum_time = None
    maximum_time = None

    for metric_stats in reversed(Mertric_Statistics_List):
        metric_stats_descriptor = metric_stats.get("MetricDescriptor", {})
        metric_stats_datapoints = metric_stats.get("Datapoints", [])
        datapoints_time, datapoints_max, datapoints_avg = \
            Metric_Statistics_Datapoints_Time_and_Values(metric_stats_datapoints,
                                                         metric_stats_descriptor.get("YFactor", 1))
        if ((minimum_time is None) and (maximum_time is None)):
            minimum_time = datapoints_time[0]
            maximum_time = datapoints_time[-1]
        else:
            minimum_time = min(minimum_time, datapoints_time[0])
            maximum_time = max(maximum_time, datapoints_time[-1])

        line_color = metric_stats_descriptor.get("Color", [0, 0, 0])

        this_y_axis_label = (metric_stats_descriptor.get("MetricLabel", " "),
                             tuple(metric_stats_descriptor.get("LabelColor", line_color)))
        y_axis = metric_stats_descriptor.get("YAxis", "left")
        if (y_axis == "left"):
            left_y_axis_labels.append(this_y_axis_label)
            this_axis = axes
        else:
            right_y_axis_labels.append(this_y_axis_label)
            this_axis = axis_2

        this_axis.plot(datapoints_time, datapoints_max, linewidth=line_width, color=tuple(line_color))
        this_axis.tick_params('y', colors="black")

    # Now draw left y axis labels and ...
    if (len(left_y_axis_labels) > 0):
        # Darker y-axis label text for legibility
        label_text, label_color = left_y_axis_labels[0]
        axes.set_ylabel(label_text, fontsize="large", color=label_color)

        if (len(left_y_axis_labels) > 1):
            label_text, label_color = left_y_axis_labels[1]
            plotter.gcf().text(0.02, 0.55, label_text,
                               rotation="vertical", verticalalignment="center",
                               fontsize="large", color=label_color)
    # ... right y axis labels
    if (len(right_y_axis_labels) > 0):
        # Darker y-axis label text for legibility
        label_text, label_color = right_y_axis_labels[0]
        axis_2.set_ylabel(label_text, fontsize="large", color=label_color)

        if (len(right_y_axis_labels) > 1):
            label_text, label_color = right_y_axis_labels[1]
            plotter.gcf().text(0.98, 0.55, label_text,
                               rotation="vertical", verticalalignment="center",
                               fontsize="large", color=label_color)

    # Attempt optimum x axis (date/time) tic labeling, complicated, heuristic
    major_minor_formatter = "hour"

    # Adaptive time axis tics and tic labels
    if ((Period_Value >= 1) and (Period_Value < 3)):
        axes.xaxis.set_major_locator(HourLocator(every_hour))
        axes.xaxis.set_minor_locator(MinuteLocator(every_five_minutes_labeled))
        major_minor_formatter = "hour/minute"
    elif ((Period_Value >= 3) and (Period_Value < 6)):
        axes.xaxis.set_major_locator(HourLocator(every_hour))
        axes.xaxis.set_minor_locator(MinuteLocator(every_ten_minutes_labeled))
        major_minor_formatter = "hour/minute"
    elif ((Period_Value >= 6) and (Period_Value < 8)):
        axes.xaxis.set_major_locator(HourLocator(every_hour))
        axes.xaxis.set_minor_locator(MinuteLocator(every_fifteen_minutes_labeled))
        major_minor_formatter = "hour/minute"
    elif ((Period_Value >= 8) and (Period_Value < 16)):
        axes.xaxis.set_major_locator(HourLocator(every_hour))
        axes.xaxis.set_minor_locator(MinuteLocator(every_thirty_minutes_labeled))
        major_minor_formatter = "hour/minute"
    elif ((Period_Value >= 16) and (Period_Value < 24)):
        axes.xaxis.set_major_locator(HourLocator(every_hour))
        axes.xaxis.set_minor_locator(MinuteLocator(every_thirty_minutes))

    elif ((Period_Value >= 24) and (Period_Value < (24 + 12))):
        axes.xaxis.set_major_locator(HourLocator(every_two_hours))
        axes.xaxis.set_minor_locator(HourLocator(every_hour))

    elif ((Period_Value >= (24 + 12)) and (Period_Value < (48 + 12))):
        axes.xaxis.set_major_locator(HourLocator(every_three_hours))
        axes.xaxis.set_minor_locator(HourLocator(every_hour))

    elif ((Period_Value >= (48 + 12)) and (Period_Value < (72 + 12))):
        axes.xaxis.set_major_locator(HourLocator(every_four_hours))
        axes.xaxis.set_minor_locator(HourLocator(every_hour))

    elif ((Period_Value >= (72 + 12)) and (Period_Value < (96 + 12))):
        axes.xaxis.set_major_locator(HourLocator(every_six_hours))
        axes.xaxis.set_minor_locator(HourLocator(every_three_hours))

    elif ((Period_Value >= (96 + 12)) and (Period_Value < (120 + 12))):
        axes.xaxis.set_major_locator(HourLocator(every_twelve_hours))
        axes.xaxis.set_minor_locator(HourLocator(every_six_hours))

    elif ((Period_Value >= (120 + 12)) and (Period_Value < (144 + 12))):
        axes.xaxis.set_major_locator(DayLocator(every_day))
        axes.xaxis.set_minor_locator(HourLocator(every_four_hours))
        major_minor_formatter = "day"

    elif ((Period_Value >= (144 + 12)) and (Period_Value < (168 + 12))):
        axes.xaxis.set_major_locator(DayLocator(every_day))
        axes.xaxis.set_minor_locator(HourLocator(every_six_hours))
        major_minor_formatter = "day"

    if (major_minor_formatter == "hour/minute"):
        axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))
        axes.xaxis.set_minor_formatter(DateFormatter("%M"))
    elif (major_minor_formatter == "hour"):
        axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))
    elif (major_minor_formatter == "day"):
        axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))

    plotter.setp(axes.get_xticklabels(), rotation=0, ha="center")

    # cpu_time is sorted, so this can work
    axes.set_xlim(minimum_time, maximum_time)
    axes.grid(True)

    # Trim off real estate wasting margins
    plotter.subplots_adjust(left=0.06, bottom=0.13, right=0.94, top=0.98, wspace=0, hspace=0)

    canvas = FigureCanvas(plot_figure)
    canvas.draw()

    return (canvas, plot_figure)


# Since this is a "static" widget, it's more convenient to create as kv
Builder.load_string(
"""
<VerticalTabBarBoxLayout>:
    orientation: 'vertical'

    canvas:
        Color:
            rgba: 0.75, 0.95, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    size_hint: (0.02, 1)

    Widget:
        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_previous()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.texture_size[0] / 2.0)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Previous"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_simplex()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.parent.height * 0.3)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Simplex"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_help()
            center: self.parent.center
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Help"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_duplex()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.parent.height * 0.7)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Duplex"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_next()
            center_x: self.parent.center_x
            center_y: self.parent.top - self.parent.height + (self.texture_size[0] / 2.0)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Next"
""")


class VerticalTabBarBoxLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(VerticalTabBarBoxLayout, self).__init__(**kwargs)
        self.register_event_type('on_press_previous')
        self.register_event_type('on_press_next')

        self.register_event_type('on_press_simplex')
        self.register_event_type('on_press_duplex')

        self.register_event_type('on_press_help')

    def trigger_on_press_previous(self, *args):
        self.dispatch('on_press_previous')

    def on_press_previous(self, *args):
        pass

    def trigger_on_press_next(self, *args):
        self.dispatch('on_press_next')

    def on_press_next(self, *args):
        pass

    def trigger_on_press_simplex(self, *args):
        self.dispatch('on_press_simplex')

    def on_press_simplex(self, *args):
        pass

    def trigger_on_press_duplex(self, *args):
        self.dispatch('on_press_duplex')

    def on_press_duplex(self, *args):
        pass

    def trigger_on_press_help(self, *args):
        self.dispatch('on_press_help')

    def on_press_help(self, *args):
        pass


# This slider extension allows the code to avoid the very expensive refreshes of ...
# ... the widget images until the user has stopped sliding the slider. Refresh then.
class SliderExtended(Slider):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(SliderExtended, self).__init__(**kwargs)

    def on_release(self):
        pass

    # Because there appears to be no event for touch_up, ...
    # ... override on_touch_up and create a custom event
    def on_touch_up(self, touch):
        super(SliderExtended, self).on_touch_up(touch)
        if (touch.grab_current == self):
            self.dispatch('on_release')
            return True


# Since this is a relatively complicated "dynamic" widget, ...
# ... it's more convenient to render as Python code.
class TimeSpanControlBar(BoxLayout):
    Period_Duration_Steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 18
                             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                             100, 104, 108, 112, 116, 120,  # 6
                             124, 128, 132, 136, 140, 144,  # 6
                             148, 152, 156, 160, 164, 168]  # 6

    Period_Hours_Ago_Steps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 19
                              26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                              50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                              74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                              100, 104, 108, 112, 116, 120,  # 6
                              124, 128, 132, 136, 140, 144,  # 6
                              148, 152, 156, 160, 164, 168]  # 6

    def __init__(self, **kwargs):
        self.register_event_type('on_release')

        self._period_duration_hours = 24
        self._period_end_hours_ago = 0

        slider_minimum_value = -1000

        period_duration_slider_maximum_value = -1
        self.period_duration_slider_value_span = period_duration_slider_maximum_value - slider_minimum_value

        period_end_slider_maximum_value = 0
        self.period_end_slider_value_span = period_end_slider_maximum_value - slider_minimum_value

        super(TimeSpanControlBar, self).__init__(**kwargs)

        self.period_duration_label = Label(text="proxy", size_hint=(0.075, 1))

        self.period_duration_slider = \
            SliderExtended(cursor_image=path_to_time_slider_cursor,
                           cursor_disabled_image=path_to_time_slider_cursor_disabled,
                           cursor_height=28,
                           border_horizontal=[0, 0, 0, 0], padding=12,
                           min=slider_minimum_value, max=period_duration_slider_maximum_value,
                           value=period_duration_slider_maximum_value, step=1, size_hint=(0.4, 1))
        self.period_duration_slider.bind(value=self._on_period_duration_value_change)
        self.period_duration_slider.bind(on_release=self._trigger_on_release)

        refresh_button = Button(text="Refresh", size_hint=(0.05, 1))
        refresh_button.font_size = 14
        refresh_button.bind(on_press=self._trigger_on_release)

        self.period_end_slider = \
            SliderExtended(cursor_image=path_to_time_slider_cursor,
                           cursor_disabled_image=path_to_time_slider_cursor_disabled,
                           cursor_height=28,
                           border_horizontal=[0, 0, 0, 0], padding=12,
                           min=slider_minimum_value, max=period_end_slider_maximum_value,
                           value=period_end_slider_maximum_value, step=1, size_hint=(0.4, 1))
        self.period_end_slider.bind(value=self._on_period_end_value_change)
        self.period_end_slider.bind(on_release=self._trigger_on_release)

        self.period_end_label = Label(text="proxy", size_hint=(0.075, 1))

        self.add_widget(self.period_duration_label)
        self.add_widget(self.period_duration_slider)

        self.add_widget(refresh_button)

        self.add_widget(self.period_end_slider)
        self.add_widget(self.period_end_label)

        self.set_period_duration_value(self._period_duration_hours)
        self.set_period_end_value(self._period_end_hours_ago)

    # Public functions (used to synchronize multiple TimeSpanControlBars) ...
    def set_period_duration_value(self, period_duration_value, *args):
        self._period_duration_hours = period_duration_value
        self.period_duration_label.text = (self._period_value_display(self._period_duration_hours))
        self.period_duration_slider.value = -(self.period_duration_slider_value_span *
                                              (self.Period_Duration_Steps.index(self._period_duration_hours) /
                                               len(self.Period_Duration_Steps)))

    def set_period_end_value(self, period_end_value, *args):
        self._period_end_hours_ago = period_end_value
        self.period_end_slider.value = -(self.period_end_slider_value_span *
                                         (self.Period_Hours_Ago_Steps.index(self._period_end_hours_ago) /
                                          len(self.Period_Hours_Ago_Steps)))
        self.period_end_label.text = (self._period_value_display(self._period_end_hours_ago) + " ago")

    # ... Public functions  (used to synchronize multiple TimeSpanControlBars)

    # Private functions ...
    def _period_value_display(self, Period_Value):
        period_value_string = ""
        if ((Period_Value // 24) > 0): period_value_string += str(Period_Value // 24) + "D"
        if (((Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Period_Value % 24) + "H"
        return period_value_string

    def _on_period_duration_value_change(self, instance, period_duration_slider_value, *args):
        # print (period_duration_slider_value)
        period_value_index = \
            int(round(len(self.Period_Duration_Steps) *
                      (abs(period_duration_slider_value) / self.period_duration_slider_value_span)))
        self._period_duration_hours = \
            self.Period_Duration_Steps[bound(0, (len(self.Period_Duration_Steps) - 1), period_value_index)]
        self.period_duration_label.text = (self._period_value_display(self._period_duration_hours))
        # print (period_duration_slider_value, period_value_index, self._period_duration_hours, self.period_duration_label.text)
        return True

    def _on_period_end_value_change(self, instance, period_end_slider_value, *args):
        period_end_value_index = \
            int(round(len(self.Period_Hours_Ago_Steps) *
                      (abs(period_end_slider_value) / self.period_end_slider_value_span)))
        self._period_end_hours_ago = \
            self.Period_Hours_Ago_Steps[bound(0, (len(self.Period_Hours_Ago_Steps) - 1), period_end_value_index)]
        self.period_end_label.text = (self._period_value_display(self._period_end_hours_ago) + " ago")
        return True

    # ... Private functions

    # Proxy for public event
    def on_release(self, *args):
        pass

    # Private function
    def _trigger_on_release(self, *args):
        self.dispatch('on_release', self._period_duration_hours, self._period_end_hours_ago)
        return True


Builder.load_string("""
<LabelExtended>:
  background_color: 1, 1, 1, 1
  canvas.before:
    Color:
      rgba: self.background_color
    Rectangle:
      pos: self.pos
      size: self.size
""")

class LabelExtended(Label):
    background_color = ListProperty([1, 1, 1, 1])

Factory.register('KivyExtended', module='LabelExtended')


class GridLayoutExtended ( GridLayout ):
    def __init__(self, **kwargs):
        # Gotta be able to do its business
        super(GridLayoutExtended, self).__init__(**kwargs)

        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


def Build_Help_GridLayout ( on_help_escape_callback ):
    kivy_app_help = \
        GridLayoutExtended(cols=1, padding=[2, 2, 0, 2], spacing=0,
                           size_hint=(None, None), width=Initialize_Window_Width)

    cwremote_screen_image = \
        Image(source=path_to_cwremote_screen_image,
              size=((Initialize_Window_Width - 4), 815), size_hint=(None, None))
    kivy_app_help.add_widget(cwremote_screen_image)

    help_escape_button = Button(text="Return to graphs", bold=True,
                                background_color=[1, 0, 0, 1],
                                size=((Initialize_Window_Width - 4), 28), size_hint=(None, None))
    help_escape_button.bind(on_press=on_help_escape_callback)
    kivy_app_help.add_widget(help_escape_button)

    CW_Remote_Help_Text_Paragraphs = [
        "The red '[b][color=ff0000]A[/color][/b]' marks the slider that adjusts the duration of the period for which the graphed data will appear. " +
        "It can adjust from 1 hour to 7 days (168 hours). " +
        "The label to the left of the this slider displays the current period duration in days and hours. " +
        "This slider is logarithmic, it is increasingly sensitive toward the right end of the scale. ",

        "The red '[b][color=ff0000]B[/color][/b]' marks the slider that adjusts the hours before now that the graphed period ends. " +
        "It can adjust from 0 hours to 7 days (168 hours). " +
        "The label to the right of the this slider displays the days and hours before now that the graphed period ends. " +
        "This slider is logarithmic, it is increasingly sensitive toward the right end of the scale. "
    ]

    # Add help text paragraphs to grid.
    for help_text_paragraph in CW_Remote_Help_Text_Paragraphs:
        help_txt_para = LabelExtended(text=help_text_paragraph, markup=True, text_size=(1272, None),
                                      color=[0, 0, 0, 1], padding_x=2,
                                      width=(Initialize_Window_Width - 4), size_hint=(None, None))
        help_txt_para.height = math.ceil(len(help_text_paragraph) * (1.33 / 255)) * 25
        kivy_app_help.add_widget(help_txt_para)

        kivy_app_help.bind(minimum_height=kivy_app_help.setter('height'))

    return kivy_app_help


class Build_Kivy_App_UI ( App ):
    def __init__(self, **kwargs):
        super(Build_Kivy_App_UI, self).__init__(**kwargs)
        Window.bind(on_key_down=self.on_keyboard_down)

    def build(self):
        self.title = "Kivy App Demo Step3"
        Window.bind(on_key_down=self.on_keyboard_down)

        Vertical_Graph_Height_Factor = 0.96

        # Automatically size widget images to fit screen real estate
        horizontal_size, vertical_size = Window.size
        self.Horizontal_Graph_Width = int(round(horizontal_size * 0.98))
        self.Vertical_Graph_Height = vertical_size * Vertical_Graph_Height_Factor

        self.fw_plot_figure_0 = None
        self.fw_plot_figure_1 = None

        self.Period_Duration_Hours = 24
        self.Period_End_Hours_Ago = 0

        self.Visible_Payload_Count = 2

        self.Kivy_App_UI = ScreenManager(transition=NoTransition())

        # Duplex
        self.Kivy_App_Duplex_Screen = Screen(name="duplex")
        self.Kivy_App_Duplex = BoxLayout(orientation='horizontal')

        self.Duplex_Tab_Bar = VerticalTabBarBoxLayout()

        self.Duplex_Tab_Bar.bind(on_press_previous=self.on_previous)
        self.Duplex_Tab_Bar.bind(on_press_next=self.on_next)

        self.Duplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
        self.Duplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

        self.Duplex_Tab_Bar.bind(on_press_help=self.on_help)

        self.Duplex_Kivy_App_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

        self.Duplex_TimeSpanControlBar = TimeSpanControlBar()
        self.Duplex_TimeSpanControlBar.bind(on_release=self.update_with_parameters)
        self.Duplex_TimeSpanControlBar.size_hint = (1, 0.04)

        # Simplex
        self.Kivy_App_Simplex_Screen = Screen(name="simplex")
        self.Kivy_App_Simplex = BoxLayout(orientation='horizontal')

        self.Simplex_Tab_Bar = VerticalTabBarBoxLayout()

        self.Simplex_Tab_Bar.bind(on_press_previous=self.on_previous)
        self.Simplex_Tab_Bar.bind(on_press_next=self.on_next)

        self.Simplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
        self.Simplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

        self.Simplex_Tab_Bar.bind(on_press_help=self.on_help)

        self.Simplex_Kivy_App_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

        self.Simplex_TimeSpanControlBar = TimeSpanControlBar()
        self.Simplex_TimeSpanControlBar.bind(on_release=self.update_with_parameters)
        self.Simplex_TimeSpanControlBar.size_hint = (1, 0.04)

        # Duplex screen
        self.Duplex_Upper_Payload_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))
        self.Duplex_Lower_Payload_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))

        self.Duplex_Kivy_App_Panel.add_widget(self.Duplex_Upper_Payload_Box)
        self.Duplex_Kivy_App_Panel.add_widget(self.Duplex_TimeSpanControlBar)
        self.Duplex_Kivy_App_Panel.add_widget(self.Duplex_Lower_Payload_Box)

        self.Kivy_App_Duplex.add_widget(self.Duplex_Tab_Bar)
        self.Kivy_App_Duplex.add_widget(self.Duplex_Kivy_App_Panel)

        self.Kivy_App_Duplex_Screen.add_widget(self.Kivy_App_Duplex)
        self.Kivy_App_UI.add_widget(self.Kivy_App_Duplex_Screen)

        # Simplex screen
        self.Simplex_Lower_Payload_Box = BoxLayout(orientation='vertical', size_hint=(1, (2 * 0.48)))

        self.Simplex_Kivy_App_Panel.add_widget(self.Simplex_TimeSpanControlBar)
        self.Simplex_Kivy_App_Panel.add_widget(self.Simplex_Lower_Payload_Box)

        self.Kivy_App_Simplex.add_widget(self.Simplex_Tab_Bar)
        self.Kivy_App_Simplex.add_widget(self.Simplex_Kivy_App_Panel)

        self.Kivy_App_Simplex_Screen.add_widget(self.Kivy_App_Simplex)
        self.Kivy_App_UI.add_widget(self.Kivy_App_Simplex_Screen)

        # Help screen
        self.Kivy_App_Help_Screen = Screen(name="help")

        self.Kivy_App_Help = Build_Help_GridLayout(self.on_help_escape)

        self.Kivy_App_Help_ScrollView = \
            ScrollView(size_hint=(None, None), size=(Initialize_Window_Width, Initialize_Window_Height),
                       bar_width=5, bar_color=[1, 0, 0, 0.5], bar_inactive_color=[1, 0, 0, 0.2],
                       do_scroll_x=False)
        self.Kivy_App_Help_ScrollView.add_widget(self.Kivy_App_Help)

        self.Kivy_App_Help_Screen.add_widget(self.Kivy_App_Help_ScrollView)
        self.Kivy_App_UI.add_widget(self.Kivy_App_Help_Screen)

        return self.Kivy_App_UI
        

    def on_simplex ( self, *args ):
        if (self.Visible_Payload_Count == 2): self.toggle_duplex_versus_simplex()
        return True

    def on_duplex ( self, *args ):
        if (self.Visible_Payload_Count == 1): self.toggle_duplex_versus_simplex()
        return True

    def toggle_duplex_versus_simplex ( self ):
        if (self.Kivy_App_UI.current == "duplex"):
            self.synchronize_control_bar_values(self.Simplex_TimeSpanControlBar)
            self.Visible_Payload_Count = 1
            self.Kivy_App_UI.current = "simplex"
        elif (self.Kivy_App_UI.current == "simplex"):
            self.synchronize_control_bar_values(self.Duplex_TimeSpanControlBar)
            self.Visible_Payload_Count = 2
            self.Kivy_App_UI.current = "duplex"

        self.update()

    def synchronize_control_bar_values ( self, target_control_bar ):
        for destination_child in target_control_bar.children:
            target_control_bar.set_period_duration_value(self.Period_Duration_Hours)
            target_control_bar.set_period_end_value(self.Period_End_Hours_Ago)

    def update_with_parameters ( self, instance, period_value, period_end_value, *args ):
        # print ("update_params:", period_value, period_end_value)
        self.Period_Duration_Hours = period_value
        self.Period_End_Hours_Ago = period_end_value
        self.update()

    def update ( self, *args ):
        datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
        period_end_utc = datetime_now_utc - datetime.timedelta(hours=self.Period_End_Hours_Ago)

        graph_width = self.Horizontal_Graph_Width

        if (self.Visible_Payload_Count == 2):
            self.Duplex_Upper_Payload_Box.clear_widgets()
            self.Duplex_Lower_Payload_Box.clear_widgets()

            graph_height = int(round(self.Vertical_Graph_Height / 2.0))

            metric_statistics_list = \
                Get_Metric_Statistics_Datapoints(0, period_end_utc, self.Period_Duration_Hours)

            metric_figure_widget, plot_figure = \
                Prepare_Get_Metric_Statistics_Figure(metric_statistics_list,
                                                     self.Period_Duration_Hours, graph_width, graph_height,
                                                     self.fw_plot_figure_0)

            self.fw_plot_figure_0 = plot_figure
            self.Duplex_Upper_Payload_Box.add_widget(metric_figure_widget)

            metric_statistics_list = \
                Get_Metric_Statistics_Datapoints(1, period_end_utc, self.Period_Duration_Hours)

            metric_figure_widget, plot_figure = \
                Prepare_Get_Metric_Statistics_Figure(metric_statistics_list,
                                                     self.Period_Duration_Hours, graph_width, graph_height,
                                                     self.fw_plot_figure_1)

            self.fw_plot_figure_1 = plot_figure
            self.Duplex_Lower_Payload_Box.add_widget(metric_figure_widget)

        elif (self.Visible_Payload_Count == 1):
            graph_height = int(round(self.Vertical_Graph_Height))

            self.Simplex_Lower_Payload_Box.clear_widgets()

            metric_statistics_list = \
                Get_Metric_Statistics_Datapoints(0, period_end_utc, self.Period_Duration_Hours)

            metric_figure_widget, plot_figure = \
                Prepare_Get_Metric_Statistics_Figure(metric_statistics_list,
                                                     self.Period_Duration_Hours, graph_width, graph_height,
                                                     self.fw_plot_figure_0)

            self.fw_plot_figure_0 = plot_figure
            self.Simplex_Lower_Payload_Box.add_widget(metric_figure_widget)

        self.Kivy_App_UI.canvas.ask_update()

    def on_previous ( self, *args ):
        return True
    def on_next ( self, *args ):
        return True

    def on_help ( self, *args ):
        self.Kivy_App_UI.current = "help"
        return True

    def on_help_escape ( self, *args ):
        if (self.Kivy_App_UI.current == "help"):
            if (self.Visible_Payload_Count == 2):
                self.Kivy_App_UI.current = "duplex"
            elif (self.Visible_Payload_Count == 1):
                self.Kivy_App_UI.current = "simplex"

    def on_keyboard_down ( self, instance, keyboard, keycode, text, modifiers ):
        # print ("keycode:", keycode, ", text:", text, ", modifiers:", modifiers)
        if (keycode == 44):
            if (not (self.Kivy_App_UI.current == "help")):
                self.toggle_duplex_versus_simplex()
        elif (keycode == 41):
            self.on_help_escape()
        elif ((keycode == 81) or (keycode == 79)):
            if (not (self.Kivy_App_UI.current == "help")):
                self.on_next()
        elif ((keycode == 82) or (keycode == 80)):
            if (not (self.Kivy_App_UI.current == "help")):
                self.on_previous()
        return True

    def on_start ( self, **kwargs ):
        Clock.schedule_once(self.update, 0.5)
        return True

if __name__ == '__main__':
    Build_Kivy_App_UI().run()