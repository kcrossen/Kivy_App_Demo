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
        "The [b]red 'A'[/b] marks the slider that adjusts the duration of the period for which the graphed data will appear. " +
        "It can adjust from 1 hour to 7 days (168 hours). " +
        "The label to the left of the this slider displays the current period duration in days and hours. " +
        "This slider is logarithmic, it is increasingly sensitive toward the right end of the scale. ",

        "The red 'B' marks the slider that adjusts the hours before now that the graphed period ends. " +
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
        self.title = "Kivy App Demo"
        Window.bind(on_key_down=self.on_keyboard_down)

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
        if (self.Visible_Payload_Count == 2):
            self.Duplex_Upper_Payload_Box.clear_widgets()
            self.Duplex_Lower_Payload_Box.clear_widgets()

            upper_payload_label = \
                Label(text=Period_Span_NYC_Wall_Time(self.Period_Duration_Hours, self.Period_End_Hours_Ago))
            self.Duplex_Upper_Payload_Box.add_widget(upper_payload_label)
            lower_payload_label = \
                Label(text=Period_Span_NYC_Wall_Time(self.Period_Duration_Hours, self.Period_End_Hours_Ago))
            self.Duplex_Lower_Payload_Box.add_widget(lower_payload_label)

        elif (self.Visible_Payload_Count == 1):
            self.Simplex_Lower_Payload_Box.clear_widgets()

            lower_payload_label = \
                Label(text=Period_Span_NYC_Wall_Time(self.Period_Duration_Hours, self.Period_End_Hours_Ago))
            self.Simplex_Lower_Payload_Box.add_widget(lower_payload_label)

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