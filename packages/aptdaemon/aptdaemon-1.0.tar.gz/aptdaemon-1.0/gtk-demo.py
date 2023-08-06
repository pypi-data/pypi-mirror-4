#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Provides a graphical demo application for aptdaemon
"""
# Copyright (C) 2008-2009 Sebastian Heinlein <sevel@glatzor.de>
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

__author__ = "Sebastian Heinlein <devel@glatzor.de>"

from optparse import OptionParser
import logging

import gobject
import gtk

import aptdaemon.client
from aptdaemon.enums import *
from aptdaemon.gtkwidgets import AptErrorDialog, \
                                 AptConfirmDialog, \
                                 AptProgressDialog
import aptdaemon.errors


class AptDaemonDemo(object):

    """Provides a graphical test application."""

    def _run_transaction(self, transaction):
        dia = AptProgressDialog(transaction, parent=self.win)
        dia.run(close_on_finished=True, show_error=True,
                reply_handler=lambda: True,
                error_handler=self._on_error)

    def _simulate_trans(self, trans):
        trans.simulate(reply_handler=lambda: self._confirm_deps(trans),
                       error_handler=self._on_error)

    def _confirm_deps(self, trans):
        if [pkgs for pkgs in trans.dependencies if pkgs]:
            dia = AptConfirmDialog(trans, parent=self.win)
            res = dia.run()
            dia.hide()
            if res != gtk.RESPONSE_OK:
                return
        self._run_transaction(trans)

    def _on_error(self, error):
        try:
            raise error
        except aptdaemon.errors.NotAuthorizedError:
            # Silently ignore auth failures
            return
        except aptdaemon.errors.TransactionFailed as error:
            pass
        except Exception as error:
            error = aptdaemon.errors.TransactionFailed(ERROR_UNKNOWN,
                                                       str(error))
        dia = AptErrorDialog(error)
        dia.run()
        dia.hide()

    def _on_upgrade_clicked(self, *args):
        self.ac.upgrade_system(safe_mode=False, 
                               reply_handler=self._simulate_trans,
                               error_handler=self._on_error)

    def _on_update_clicked(self, *args):
        self.ac.update_cache(reply_handler=self._run_transaction,
                             error_handler=self._on_error)

    def _on_install_clicked(self, *args):
        self.ac.install_packages([self.package],
                                 reply_handler=self._simulate_trans,
                                 error_handler=self._on_error)

    def _on_install_file_clicked(self, *args):
        chooser = gtk.FileChooserDialog(parent=self.win,
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        chooser.set_local_only(True)
        chooser.run()
        chooser.hide()
        path = chooser.get_filename()
        self.ac.install_file(path, reply_handler=self._simulate_trans,
                             error_handler=self._on_error)

    def _on_remove_clicked(self, *args):
        self.ac.remove_packages([self.package],
                                reply_handler=self._simulate_trans,
                                error_handler=self._on_error)

    def __init__(self, package):
        self.win = gtk.Window()
        self.package = package
        self.win.set_resizable(False)
        self.win.set_title("Aptdaemon Demo")
        icon_theme = gtk.icon_theme_get_default()
        try:
            gtk.window_set_default_icon(icon_theme.load_icon("aptdaemon-setup",
                                                              32, 0))
        except (gobject.GError, AttributeError):
            pass
        button_update = gtk.Button(label="_Update")
        button_install = gtk.Button(label="_Install %s" % self.package)
        button_install_file = gtk.Button(label="Install _file...")
        button_remove = gtk.Button(label="_Remove %s" % self.package)
        button_upgrade = gtk.Button(label="Upgrade _System")
        button_update.connect("clicked", self._on_update_clicked)
        button_install.connect("clicked", self._on_install_clicked)
        button_install_file.connect("clicked", self._on_install_file_clicked)
        button_remove.connect("clicked", self._on_remove_clicked)
        button_upgrade.connect("clicked", self._on_upgrade_clicked)
        vbox = gtk.VBox()
        vbox.add(button_update)
        vbox.add(button_install)
        vbox.add(button_install_file)
        vbox.add(button_remove)
        vbox.add(button_upgrade)
        self.win.add(vbox)
        self.loop = gobject.MainLoop()
        self.win.connect("delete-event", lambda w, e: self.loop.quit())
        self.win.show_all()
        self.ac = aptdaemon.client.AptClient()

    def run(self):
        self.loop.run()


def main():
    parser = OptionParser()
    parser.add_option("-p", "--package", default="cw", action="store",
                      dest="package",
                      help="Use this package for installation and removal")
    parser.add_option("-d", "--debug", default=False, action="store_true",
                      help="Verbose debugging")
    options, args = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)

    demo = AptDaemonDemo(options.package)
    demo.run()

if __name__ == "__main__":
    main()

# vim:ts=4:sw=4:et
