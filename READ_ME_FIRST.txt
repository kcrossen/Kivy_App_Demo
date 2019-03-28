See directions at https://github.com/kcrossen/CloudWatch_Remote_Monitor/blob/master/PyInstaller_Build/README.md

$ pyinstaller -F -w --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant --exclude-module twisted --add-data 'data/*.*:data' --osx-bundle-identifier com.techview.kivyappdemo  -i appIcon.icns  Kivy_App_Demo.py