# Kivy_App_Demo
Getting started with Kivy can be a very steep learning curve. This will get you started with less pain. The demo examples at the Kivy site (kivy.org) are mostly along the lines of Hello World, which are constructed to test a specific feature or demonstrate the use of that feature. They are unlikely to apply meaningfully to what you are trying to accomplish, and that's why you use Python, right?

Another problem with the Kivy demo examples is that they don't much get into some of the more "advanced" features that nearly every application author will eventually want. For example, how do you install your own icon, how do you package a standard OSX application, and so forth?

Important disclaimer: I am not a Python expert nor a Kivy expert. My recent experience has mostly been with Qt5/C++, but just as Clark Kent must put his pants on one leg at a time, many GUI toolkits have a similar methodology. Anyone feeling that they have a better grasp of either Python or Kivy is welcome to contribute to making this demo app tutorial better. I would like to acknowledge the kind and compassionate assistance of Gabriel Pettier, a Kivy core developer. 

My goal is to make the Kivy learning curve a little less steep.

The graphic data display category of applications has many potential uses. For example, many governmental organizations, NGOs, universities, and corporations publish huge volumes of data on the internet. Weather services publish huge quantities of data such as temperature, humidity, rainfall, etc. as time series data. How would you graph that data?

This application demo kit starts to build a working example of such a graphic data display OSX app. The starting point is: https://github.com/kcrossen/Kivy_App_Demo/blob/master/Kivy_App_Demo_PyInstaller_Kit.zip, and I would recommend the use of a Python IDE such as the free and excellent PyCharm Community Edition (https://www.jetbrains.com/pycharm/download). 

To setup PyCharm for using Kivy, not covered by PyCharm's installation, use PyCharm's "Terminal" tab to:
```
$ pip install kivy
```

In PyCharm, load the file `Kivy_App_Demo.py` to be found where ever you unpacked the Kivy_App_Demo_PyInstaller_Kit, and you are now good to go.

Any Kivy application results from some structure composed of "widgets", each of which accomplishes some small part of your task. This structure, which can be seen as an upside-down tree or alternately as the stump and root system of a felled tree, must always be a widget that you have authored, the App widget. But it is possible for you to "containerize" or encapsulate your own widgets, and use your own widgets as components of your application structure.
