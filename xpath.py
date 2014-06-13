#!/usr/bin/env python

"""XPath Navigator in PyGTK"""

# Copyright (C) 2006-2012 Andreas Madsack <madsacas@ims.uni-stuttgart.de>
#
# xpath.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# xpath.py is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# Licence: http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


# changes:
# - 1.2   (2012-12-09)
#         updates for github
# - 1.1   (2008-12-08)
#         transfer to lxml
# - 1.0.2 (2006-03-20)
#         string speed improvements by Daniel Contag
# - 1.0.1 (2006-02-04)
#         minor fixes
# - 1.0   (2006-02-04)
#         first release
#

__version__ = "1.2"

# Todos:
#  - use config-file:
#    - save filename
#    - save xpath
#    - add history (dropdown)
#  - ...

import pygtk
pygtk.require('2.0')
import gtk

from lxml import etree

class XPathViewer:
    """XPathViewer using PyGTK"""
    def file_chooser(self, widget, entry):
        """file chooser dialog"""
        dialog = gtk.FileChooserDialog("Open..", None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filterx = gtk.FileFilter()
        filterx.set_name("XML-Files")
        filterx.add_pattern("*.xml")
        dialog.add_filter(filterx)

        filterx = gtk.FileFilter()
        filterx.set_name("All files")
        filterx.add_pattern("*")
        dialog.add_filter(filterx)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            entry.set_text(dialog.get_filename())

            dialog.destroy()

    def set_status_bar(self, message):
        """sets statusbar with message"""
        self.status_bar.pop(self.context_id)
        self.status_bar.push(self.context_id, message)

    def populate_tree(self, treewidget, elements):
        """put xml-elemets in treewidget"""
        self.treestore.clear()

        def make_trees(elements, piter):
            """traverse over dom-tree and generate treedata """
            pitern = None
            for elem in elements:
                try:
                    attrs = ''
                    x = elem.tag
                    tmplist = []
                    if elem.attrib:
                        for i in elem.attrib.keys():
                            tmplist.append('@')
                            tmplist.append(i)
                            tmplist.append('="')
                            tmplist.append(elem.get(i))
                            tmplist.append('" ')

                    attrs = ''.join(tmplist)

                   tmplist = []

                   if len(attrs):
                        tmplist.append(elem.tag)
                        tmplist.append(' (')
                        tmplist.append(attrs[:-1])
                        tmplist.append(')')
                        x = ''.join(tmplist)

                    pitern = self.treestore.append(piter, [x])

                    # text auch anhaengen
                    x = elem.text
                    if x:
                        x.strip()
                        for i in (' ', '\n', '\t'):
                            x = x.replace(i,'')
                        if x:
                            self.treestore.append(pitern,
                                                  [elem.text.encode('UTF-8')])

                    make_trees(elem.getchildren(), pitern)

                except AttributeError:
                    pitern = piter
                    self.treestore.append(pitern,
                                          [elem.encode('UTF-8')])

        make_trees(elements, None)

    def runxpath(self, widget, treewidget, ent_fc, ent_xp):
        """run xpath and check for exceptions"""
        try:
            doc = etree.parse(open(ent_fc.get_text()))
        except IOError:
            self.set_status_bar("File does not exist?")
            return

        try:
            self.populate_tree(treewidget, doc.xpath(ent_xp.get_text()))
        except:
            self.set_status_bar("Error in evaluating XPath.")
            return
        # no error, so clean status_bar
        self.set_status_bar('')

    def treeview_menu(self, widget, event):
        """show contextmenu"""
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.popup(None, None, None, event.button, event.time)
            return True
        return False

    def __init__(self):
        """generate gui for application"""
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(600, 500)
        self.window.set_title("simple XPath Navigator")
        self.window.connect("delete_event", lambda w, e: gtk.main_quit())

        box1 = gtk.VBox(False, 0)

        # filename-input
        label = gtk.Label("Filename: ")

        ent_fc = gtk.Entry()
        ent_fc.set_text("choose-xml-file")
        ent_fc.select_region(0, len(ent_fc.get_text()))

        button = gtk.Button("choose File")
        button.connect("clicked", self.file_chooser, ent_fc)

        box = gtk.HBox(False, 0)
        box.pack_start(label, False, False, 0)
        box.pack_start(ent_fc, True, True, 0)
        box.pack_start(button, False, False, 0)

        box1.pack_start(box, False, False, 0)

        label.show()
        ent_fc.show()
        box.show()

        button.show()

        # treeview
        self.treestore = gtk.TreeStore(str)
        self.treeview = gtk.TreeView(self.treestore)

        # xpath-input
        label = gtk.Label("XPath: ")

        ent_xp = gtk.Entry()
        ent_xp.set_text("/*")
        ent_xp.select_region(0, len(ent_xp.get_text()))

        ent_xp.connect("activate", self.runxpath, self.treeview, ent_fc, ent_xp)

        button = gtk.Button("Go")
        button.connect("clicked", self.runxpath, self.treeview, ent_fc, ent_xp)

        box = gtk.HBox(False, 0)
        box.pack_start(label, False, False, 0)
        box.pack_start(ent_xp, True, True, 0)
        box.pack_start(button, False, False, 0)

        box1.pack_start(box, False, False, 0)

        label.show()
        ent_xp.show()
        box.show()

        button.show()

        # rest of treeview
        self.tvcolumn = gtk.TreeViewColumn('DOM Tree')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(1, 0)
        scrolled.add(self.treeview)
        scrolled.show()

        # context-menu
        menu = gtk.Menu()

        menu_item = gtk.MenuItem("Expand all")
        menu.append(menu_item)
        menu_item.connect("activate", lambda w: self.treeview.expand_all())
        menu_item.show()

        menu_item = gtk.MenuItem("Collapse all")
        menu.append(menu_item)
        menu_item.connect("activate", lambda w: self.treeview.collapse_all())
        menu_item.show()

        menu_item = gtk.SeparatorMenuItem()
        menu.append(menu_item)
        menu_item.show()

        menu_item = gtk.MenuItem("Quit")
        menu.append(menu_item)
        menu_item.connect("activate", lambda w: gtk.main_quit())
        menu_item.show()

        self.treeview.connect_object("event", self.treeview_menu, menu)

        self.treeview.show()
        box1.pack_start(scrolled, True, True, 0)

        #
        self.window.add(box1)

        self.status_bar = gtk.Statusbar()
        box1.pack_start(self.status_bar, False, False, 0)
        self.status_bar.show()
        self.context_id = self.status_bar.get_context_id("Statusbar")

        box1.show()

        # Showing the window last so everything pops up at once.
        self.window.show()

    def main(self):
        """start gtk-mainloop"""
        gtk.main()

if __name__ == "__main__":
    # Check for new pygtk: this is new class in PyGtk 2.4
    if gtk.pygtk_version < (2, 3, 90):
        print "PyGtk 2.3.90 or later required for this program"
    else:
        XPathViewer = XPathViewer()
        XPathViewer.main()
