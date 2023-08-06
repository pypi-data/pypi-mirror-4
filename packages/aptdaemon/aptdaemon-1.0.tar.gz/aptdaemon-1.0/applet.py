#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Demo applet which monitors the state of aptdaemon transactions"""
# Copyright (C) 2008 Sebastian Heinlein <devel@glatzor.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

__author__  = "Sebastian Heinlein <devel@glatzor.de>"

import logging

import gobject
import gtk
import pango

import aptdaemon.client
import aptdaemon.gtkwidgets

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("AptStatusIcon")

class AptStatusIcon(object):

    """Shows an icon in the notification bar which provides a menu to access
    the currently running and queued transactions.
    """

    def __init__(self):
        """Initialize a new AptStatusIcon instance."""
        self._client = aptdaemon.client.AptClient()
        self.loop = gobject.MainLoop()
        self.icon = gtk.status_icon_new_from_icon_name("update-notifier")
        self.icon.set_visible(False)
        self.icon.connect("popup-menu", self._on_popup_menu)
        self.icon.connect("activate", self._on_icon_activated)
        self._daemon = aptdaemon.client.get_aptdaemon()
        self._daemon.connect_to_signal("ActiveTransactionsChanged",
                                       self._on_transactions_changed)

    def run(self):
        """Run the status icon application."""
        log.debug("Run")
        self.loop.run()

    def quit(self):
        """Quit the status icon application."""
        log.debug("Quit")
        self.quit()

    def _on_transactions_changed(self, current, queued):
        """Callback if the active transactions of the daemon changed.

        Hide the icon if there isn't any active or queued transaction.
        """
        if current or queued:
            self.icon.set_visible(True)
        else:
            self.icon.set_visible(False)

    def _on_popup_menu(self, status_icon, button, time):
        """Callback if the status icon popup menu is requested (usually a right
        click.

        Shows a popup menu containg the currently running and all queued
        transactions.
        """
        log.debug("Popup menu")
        menu = gtk.Menu()
        current, queued = self._daemon.GetActiveTransactions()
        if current:
            log.debug("current: %s", current)
            menu.append(self._get_transaction_menu_item(current))
            if queued:
                menu.append(gtk.SeparatorMenuItem())
        for tid in queued:
            log.debug("queued: %s", tid)
            menu.append(self._get_transaction_menu_item(tid))
        menu.popup(None, None, gtk.status_icon_position_menu, button, time,
                   status_icon)
        menu.show_all()

    def _get_transaction_menu_item(self, tid):
        """Return a menu item for the given transaction id which monitors
        the transaction progress."""
        trans = aptdaemon.client.get_transaction(tid)
        item = gtk.MenuItem()
        box = gtk.HBox(spacing=6)
        icon = aptdaemon.gtkwidgets.AptStatusIcon(trans, gtk.ICON_SIZE_MENU)
        box.pack_start(icon, expand=False)
        label = aptdaemon.gtkwidgets.AptRoleLabel(trans)
        label.set_ellipsize(pango.ELLIPSIZE_NONE)
        box.pack_start(label, expand=True, fill=True)
        item.add(box)
        item.connect("activate", self._on_menu_item_activated, trans)
        return item

    def _on_menu_item_activated(self, item, trans):
        """Callback if a menu item gets activated.

        Show a progress dialog for the transaction of the activated
        menu item."""
        dialog = aptdaemon.gtkwidgets.AptProgressDialog(trans, terminal=False,
                                                        debconf=False)
        dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        dialog.run(attach=True)
        dialog.hide()

    def _on_icon_activated(self, status_icon):
        """Callback if the status icon gets activated.

        This method will call the popup_menu callback to show the menu.
        """
        log.debug("Activated")
        time = gtk.get_current_event_time()
        self._on_popup_menu(status_icon, 3, time)

if __name__ == "__main__":
    asi = AptStatusIcon()
    asi.run()
