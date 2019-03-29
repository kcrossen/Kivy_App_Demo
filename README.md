# Kivy by example, step-by-step from kit download to OSX application
### Table of Contents ###
[Kivy_App_Demo](#kivy-app-demo)

[Kivy_App_Demo_Step2](#kivy-app-demo-step2)

Getting started with Kivy can be a very steep learning curve. The demo examples at the Kivy site (kivy.org) are mostly along the lines of Hello World, which are constructed to test a specific feature or demonstrate the use of that feature. They are unlikely to apply meaningfully to what you are trying to accomplish, and that's why you use Python, right?

Another problem with the Kivy demo examples is that they don't much get into some of the more "advanced" features that nearly every application author will eventually want. For example, how do you install your own icon, how do you package a standard OSX application, and so forth?

Important disclaimer: I am not a Python expert nor a Kivy expert. My recent experience has mostly been with Qt5/C++, but just as Clark Kent must put his pants on one leg at a time, GUI toolkits have a generally similar methodology. Anyone feeling that they have a better grasp of either Python or Kivy is welcome to contribute toward making this demo app recipe better. I would like to acknowledge the kind assistance of Gabriel Pettier, a Kivy core developer. 

My goal is to make the Kivy learning curve a little less steep, to get you started with less pain. 

The graphic data display category of applications has many potential uses. For example, many governmental organizations, NGOs, universities, and corporations publish huge volumes of data on the internet. Weather services publish huge quantities of data such as temperature, humidity, rainfall, etc. as time series data. How would you graph that data?

This application demo kit starts to build a working example of such a graphic data display OSX app. The starting point is: https://github.com/kcrossen/Kivy_App_Demo/blob/master/Kivy_App_Demo_PyInstaller_Kit.zip, and I would recommend the use of a Python IDE such as the free and excellent PyCharm Community Edition (https://www.jetbrains.com/pycharm/download). 

To setup PyCharm for using Kivy, not covered by PyCharm's installation, use PyCharm's "Terminal" tab to:
```
$ pip install kivy
```

[to table of contents](#table-of-contents)

## Kivy App Demo
In PyCharm, load the file `Kivy_App_Demo.py` to be found where ever you unpacked the Kivy_App_Demo_PyInstaller_Kit, and you are now good to go.

Any Kivy application results from a structure composed of "widgets", each of which accomplishes some small part of your task. This structure, which can be seen as an upside-down tree or alternately as the stump and root system of a felled tree, must always be a widget that you have authored, the App widget. But it is possible for you to "containerize" or encapsulate your own widgets, and use your own widgets as components of your application structure.

There are two general approaches to authoring your own widgets, the kv language and Python subclassing. The kv approach would probably be considered more "in style", and for "static" widgets with a complicated layout it is far easier to visualize that layout in kv. On the other hand, for widgets with simple layout and complicated "code behind the form", direct Python subclassing may lead to smaller code volume that is easier to understand at a glance.

In any case, a modestly involved example of each approach is included in `Kivy_App_Demo.py` so that you can decide for yourself which works best for you.

Here is an example of the kv approach:
```
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
```
This is a "static" widget with extremely simple "code behind the form" (everthing from `class VerticalTabBarBoxLayout(BoxLayout):` onward). If authoring your widget's functionality is this simple, the kv approach is probably the right approach for your widget.

And for a completely different type of widget, here is an example of the Python subclassing approach:
```
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
```
This creates a control bar containing two logarithmic sliders. The Python code required for functionality is relatively complicated while the layout is exceedingly simple. In this case, it is harder to see a significant advantage to the kv approach, because the "code behind the form" would have to be similar.

[to table of contents](#table-of-contents)

## Kivy App Demo Step2
In PyCharm, load the file `Kivy_App_Demo_Step2.py` also to be found where ever you unpacked the Kivy_App_Demo_PyInstaller_Kit, and you are now good to go for this step.

In this revision you can add a help screen. Kivy's built-in widgets are not well suited to a words-and-pictures help presentation, so you will have to subclass yet again:
```
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
```
These create Labels and GridLayouts with background colors. Labels can be quite powerful in that they support a variant of markup, allowing character-by-character control of text attributes, bolding for example. More information can be found here: https://kivy.org/doc/stable/api-kivy.core.text.markup.html.

Use of this Label markup capability is shown here:
```
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
```
This also demonstrates a third approach to encapsulating complicated UI construction, the function approach. Here it is being used to reduce "clutter" in the App build code. Since the help widget has only one reference to anything outside itself, this "escape-from-me" callback is passed in from the App parent.

The three approaches to encapsulation (kv, subclassing, and functions) are not religions. Use whichever creates your desired functionality most easily and naturally for you.
