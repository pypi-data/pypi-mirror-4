#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py: Simple and powerful GUI framework for agile development - Main Package"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"
__version__ = "0.9a"

# some parts where inspired or borrowed from different sources & projects
# please see the respective files or commit messages for proper recognition

import wx

##import wxversion
##wxversion.select("2.9")

# useful shortcuts:

from .controls import Label, Button, TextBox, CheckBox, ListBox, ComboBox, \
                      HtmlBox, Image, Gauge, Slider, ListView, ListColumn, \
                      TreeView, Notebook, TabPanel, Panel, RadioButton, Line, \
                      GridView, GridColumn
from .windows import Window, HtmlWindow
from .menu import MenuBar, Menu, MenuItem, MenuItemCheckable, MenuItemSeparator
from .statusbar import StatusBar

from .component import get
from .dialog import alert, prompt, confirm, select_font, select_color, \
                    open_file, save_file, choose_directory, \
                    single_choice, multiple_choice, find

#from . import tools

import os

# disable ubuntu unified menu
os.environ['UBUNTU_MENUPROXY'] = '0'

# create an app, note that the app could be already created (i.e. by an IDE):

app = wx.GetApp()
if app is None:
    app = wx.App(False)
    main_loop = app.MainLoop
else:
    # app and main loop is already created and executed by a third party tool
    main_loop = lambda: None