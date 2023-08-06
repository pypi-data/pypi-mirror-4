#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2011 Sebastian Pölsterl
#
# Permission is granted to copy, distribute and/or modify this document
# under the terms of the GNU Free Documentation License, Version 1.3
# or any later version published by the Free Software Foundation;
# with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

import sys
sys.path.insert(0, '../..')
import pgi
pgi.install_as_gi()

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

icons = ["gtk-cut", "gtk-paste", "gtk-copy"]

class IconViewWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self)
    self.set_default_size(200, 200)

    liststore = Gtk.ListStore(Pixbuf, str)
    iconview = Gtk.IconView.new()
    iconview.set_model(liststore)
    iconview.set_pixbuf_column(0)
    iconview.set_text_column(1)

    for icon in icons:
        pixbuf = Gtk.IconTheme.get_default().load_icon(icon, 64, 0)
        liststore.append([pixbuf, "Label"])

    self.add(iconview)

win = IconViewWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
