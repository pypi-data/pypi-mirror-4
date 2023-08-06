#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides a limited compatibility layer to PackageKit

Copyright (C) 2007 Ali Sabil <ali.sabil@gmail.com>
Copyright (C) 2007 Tom Parker <palfrey@tevp.net>
Copyright (C) 2008-2011 Sebastian Heinlein <glatzor@ubuntu.com>

Licensed under the GNU General Public License Version 2

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = "Sebastian Heinlein <devel@glatzor.de>"

import datetime
import glob
import gzip
import locale
import logging
import os
import platform
import re
import subprocess
import tempfile
import time
import uuid

import apt_pkg
from defer import inline_callbacks, return_value
from defer.utils import dbus_deferred_method
import dbus
from gi.repository import GObject, GLib

# for optional plugin support
try:
    import pkg_resources
except ImportError:
    pkg_resources = None

from . import policykit1
from . import core
from .core import APTDAEMON_TRANSACTION_DBUS_INTERFACE
from . import enums as aptd_enums
from .errors import TransactionFailed
from . import errors
from .progress import DaemonAcquireProgress
from . import worker
from . import networking
from . import pkenums as pk_enums

GObject.threads_init()

pklog = logging.getLogger("AptDaemon.PackageKit")

# Check if update-manager-core is installed to get aware of the
# latest distro releases
try:
    from UpdateManager.Core.MetaRelease import MetaReleaseCore
except ImportError:
    META_RELEASE_SUPPORT = False
else:
    META_RELEASE_SUPPORT = True

# Xapian database is optionally used to speed up package description search
XAPIAN_DB_PATH = os.environ.get("AXI_DB_PATH", "/var/lib/apt-xapian-index")
XAPIAN_DB = XAPIAN_DB_PATH + "/index"
XAPIAN_DB_VALUES = XAPIAN_DB_PATH + "/values"
XAPIAN_SUPPORT = False
try:
    import xapian
except ImportError:
    pass
else:
    if os.access(XAPIAN_DB, os.R_OK):
        pklog.debug("Use XAPIAN for the search")
        XAPIAN_SUPPORT = True

# Regular expressions to detect bug numbers in changelogs according to the
# Debian Policy Chapter 4.4. For details see the footnote 16:
# http://www.debian.org/doc/debian-policy/footnotes.html#f16
MATCH_BUG_CLOSES_DEBIAN = (
    r"closes:\s*(?:bug)?\#?\s?\d+(?:,\s*(?:bug)?\#?\s?\d+)*")
MATCH_BUG_NUMBERS = r"\#?\s?(\d+)"
# URL pointing to a bug in the Debian bug tracker
HREF_BUG_DEBIAN = "http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=%s"

MATCH_BUG_CLOSES_UBUNTU = r"lp:\s+\#\d+(?:,\s*\#\d+)*"
HREF_BUG_UBUNTU = "https://bugs.launchpad.net/bugs/%s"

# Regular expression to find cve references
MATCH_CVE = "CVE-\d{4}-\d{4}"
HREF_CVE = "http://web.nvd.nist.gov/view/vuln/detail?vulnId=%s"

# Map Debian sections to the PackageKit group name space
SECTION_GROUP_MAP = {
    "admin": pk_enums.GROUP_ADMIN_TOOLS,
    "base": pk_enums.GROUP_SYSTEM,
    "comm": pk_enums.GROUP_COMMUNICATION,
    "devel": pk_enums.GROUP_PROGRAMMING,
    "doc": pk_enums.GROUP_DOCUMENTATION,
    "editors": pk_enums.GROUP_PUBLISHING,
    "electronics": pk_enums.GROUP_ELECTRONICS,
    "embedded": pk_enums.GROUP_SYSTEM,
    "games": pk_enums.GROUP_GAMES,
    "gnome": pk_enums.GROUP_DESKTOP_GNOME,
    "graphics": pk_enums.GROUP_GRAPHICS,
    "hamradio": pk_enums.GROUP_COMMUNICATION,
    "interpreters": pk_enums.GROUP_PROGRAMMING,
    "kde": pk_enums.GROUP_DESKTOP_KDE,
    "libdevel": pk_enums.GROUP_PROGRAMMING,
    "libs": pk_enums.GROUP_SYSTEM,
    "mail": pk_enums.GROUP_INTERNET,
    "math": pk_enums.GROUP_SCIENCE,
    "misc": pk_enums.GROUP_OTHER,
    "net": pk_enums.GROUP_NETWORK,
    "news": pk_enums.GROUP_INTERNET,
    "oldlibs": pk_enums.GROUP_LEGACY,
    "otherosfs": pk_enums.GROUP_SYSTEM,
    "perl": pk_enums.GROUP_PROGRAMMING,
    "python": pk_enums.GROUP_PROGRAMMING,
    "science": pk_enums.GROUP_SCIENCE,
    "shells": pk_enums.GROUP_SYSTEM,
    "sound": pk_enums.GROUP_MULTIMEDIA,
    "tex": pk_enums.GROUP_PUBLISHING,
    "text": pk_enums.GROUP_PUBLISHING,
    "utils": pk_enums.GROUP_ACCESSORIES,
    "web": pk_enums.GROUP_INTERNET,
    "x11": pk_enums.GROUP_DESKTOP_OTHER,
    "unknown": pk_enums.GROUP_UNKNOWN,
    "alien": pk_enums.GROUP_UNKNOWN,
    "translations": pk_enums.GROUP_LOCALIZATION,
    "metapackages": pk_enums.GROUP_COLLECTIONS}

PACKAGEKIT_DBUS_INTERFACE = "org.freedesktop.PackageKit"
PACKAGEKIT_DBUS_SERVICE = "org.freedesktop.PackageKit"
PACKAGEKIT_DBUS_PATH = "/org/freedesktop/PackageKit"

PACKAGEKIT_TRANS_DBUS_INTERFACE = "org.freedesktop.PackageKit.Transaction"
PACKAGEKIT_TRANS_DBUS_SERVICE = "org.freedesktop.PackageKit.Transaction"

MAP_EXIT_ENUM = {
    aptd_enums.EXIT_SUCCESS: pk_enums.EXIT_SUCCESS,
    aptd_enums.EXIT_CANCELLED: pk_enums.EXIT_CANCELLED,
    aptd_enums.EXIT_FAILED: pk_enums.EXIT_FAILED,
    aptd_enums.EXIT_FAILED: pk_enums.EXIT_FAILED,
    aptd_enums.EXIT_PREVIOUS_FAILED:
    pk_enums.EXIT_FAILED}

MAP_STATUS_ENUM = {
    aptd_enums.STATUS_WAITING: pk_enums.STATUS_WAIT,
    aptd_enums.STATUS_RUNNING: pk_enums.STATUS_RUNNING,
    aptd_enums.STATUS_CANCELLING: pk_enums.STATUS_CANCEL,
    aptd_enums.STATUS_CLEANING_UP: pk_enums.STATUS_CLEANUP,
    aptd_enums.STATUS_COMMITTING: pk_enums.STATUS_COMMIT,
    aptd_enums.STATUS_DOWNLOADING: pk_enums.STATUS_DOWNLOAD,
    aptd_enums.STATUS_DOWNLOADING_REPO: pk_enums.STATUS_DOWNLOAD_REPOSITORY,
    aptd_enums.STATUS_FINISHED: pk_enums.STATUS_FINISHED,
    aptd_enums.STATUS_LOADING_CACHE: pk_enums.STATUS_LOADING_CACHE,
    aptd_enums.STATUS_RESOLVING_DEP: pk_enums.STATUS_DEP_RESOLVE,
    aptd_enums.STATUS_RUNNING: pk_enums.STATUS_RUNNING,
    aptd_enums.STATUS_WAITING_LOCK: pk_enums.STATUS_WAITING_FOR_LOCK,
    aptd_enums.STATUS_WAITING_MEDIUM: pk_enums.STATUS_UNKNOWN,
    aptd_enums.STATUS_WAITING_CONFIG_FILE_PROMPT: pk_enums.STATUS_UNKNOWN}

MAP_ERROR_ENUM = {
    aptd_enums.ERROR_CACHE_BROKEN: pk_enums.ERROR_NO_CACHE,
    aptd_enums.ERROR_DEP_RESOLUTION_FAILED: (
        pk_enums.ERROR_DEP_RESOLUTION_FAILED),
    aptd_enums.ERROR_INCOMPLETE_INSTALL: pk_enums.ERROR_NO_CACHE,
    aptd_enums.ERROR_INVALID_PACKAGE_FILE: (
        pk_enums.ERROR_PACKAGE_CORRUPT),
    aptd_enums.ERROR_KEY_NOT_INSTALLED: pk_enums.ERROR_GPG_FAILURE,
    aptd_enums.ERROR_KEY_NOT_REMOVED: pk_enums.ERROR_GPG_FAILURE,
    aptd_enums.ERROR_NOT_REMOVE_ESSENTIAL_PACKAGE: (
        pk_enums.ERROR_PACKAGE_FAILED_TO_REMOVE),
    aptd_enums.ERROR_NO_CACHE: pk_enums.ERROR_NO_CACHE,
    aptd_enums.ERROR_NO_LOCK: pk_enums.ERROR_CANNOT_GET_LOCK,
    aptd_enums.ERROR_NO_PACKAGE: pk_enums.ERROR_PACKAGE_NOT_FOUND,
    aptd_enums.ERROR_PACKAGE_ALREADY_INSTALLED: (
        pk_enums.ERROR_PACKAGE_ALREADY_INSTALLED),
    aptd_enums.ERROR_PACKAGE_DOWNLOAD_FAILED: (
        pk_enums.ERROR_PACKAGE_DOWNLOAD_FAILED),
    aptd_enums.ERROR_PACKAGE_MANAGER_FAILED: (
        pk_enums.ERROR_TRANSACTION_ERROR),
    aptd_enums.ERROR_PACKAGE_NOT_INSTALLED: (
        pk_enums.ERROR_PACKAGE_NOT_INSTALLED),
    aptd_enums.ERROR_PACKAGE_UNAUTHENTICATED: (
        pk_enums.ERROR_BAD_GPG_SIGNATURE),
    aptd_enums.ERROR_PACKAGE_UPTODATE: (
        pk_enums.ERROR_NO_PACKAGES_TO_UPDATE),
    aptd_enums.ERROR_REPO_DOWNLOAD_FAILED: (
        pk_enums.ERROR_REPO_NOT_AVAILABLE),
    aptd_enums.ERROR_UNREADABLE_PACKAGE_FILE: (
        pk_enums.ERROR_INVALID_PACKAGE_FILE),
    aptd_enums.ERROR_SYSTEM_ALREADY_UPTODATE: (
        pk_enums.ERROR_NO_PACKAGES_TO_UPDATE),
    aptd_enums.ERROR_NOT_AUTHORIZED: pk_enums.ERROR_NOT_AUTHORIZED,
    aptd_enums.ERROR_AUTH_FAILED: pk_enums.ERROR_NOT_AUTHORIZED}

MAP_PACKAGE_ENUM = {
    aptd_enums.PKG_CONFIGURING: pk_enums.INFO_INSTALLING,
    aptd_enums.PKG_DISAPPEARING: pk_enums.INFO_UNKNOWN,
    aptd_enums.PKG_INSTALLED: pk_enums.INFO_FINISHED,
    aptd_enums.PKG_INSTALLING: pk_enums.INFO_INSTALLING,
    aptd_enums.PKG_PREPARING_INSTALL: pk_enums.INFO_PREPARING,
    aptd_enums.PKG_PREPARING_PURGE: pk_enums.INFO_PREPARING,
    aptd_enums.PKG_PREPARING_REMOVE: pk_enums.INFO_PREPARING,
    aptd_enums.PKG_PURGED: pk_enums.INFO_FINISHED,
    aptd_enums.PKG_PURGING: pk_enums.INFO_REMOVING,
    aptd_enums.PKG_REMOVED: pk_enums.INFO_FINISHED,
    aptd_enums.PKG_REMOVING: pk_enums.INFO_REMOVING,
    aptd_enums.PKG_RUNNING_TRIGGER: pk_enums.INFO_CLEANUP,
    aptd_enums.PKG_UNKNOWN: pk_enums.INFO_UNKNOWN,
    aptd_enums.PKG_UNPACKING: pk_enums.INFO_DECOMPRESSING,
    aptd_enums.PKG_UPGRADING: pk_enums.INFO_UPDATING}


class PackageKit(core.DBusObject):

    """Provides a limited set of the PackageKit system D-Bus API."""

    SUPPORTED_ROLES = [pk_enums.ROLE_REFRESH_CACHE,
                       pk_enums.ROLE_UPDATE_SYSTEM,
                       pk_enums.ROLE_SIMULATE_UPDATE_PACKAGES,
                       pk_enums.ROLE_UPDATE_PACKAGES,
                       pk_enums.ROLE_SIMULATE_REMOVE_PACKAGES,
                       pk_enums.ROLE_INSTALL_PACKAGES,
                       pk_enums.ROLE_SIMULATE_INSTALL_PACKAGES,
                       pk_enums.ROLE_INSTALL_PACKAGES,
                       pk_enums.ROLE_GET_UPDATES,
                       pk_enums.ROLE_GET_UPDATE_DETAIL,
                       pk_enums.ROLE_GET_PACKAGES,
                       pk_enums.ROLE_GET_DETAILS,
                       pk_enums.ROLE_GET_DEPENDS,
                       pk_enums.ROLE_GET_REQUIRES,
                       pk_enums.ROLE_SEARCH_NAME,
                       pk_enums.ROLE_SEARCH_DETAILS,
                       pk_enums.ROLE_SEARCH_GROUP,
                       pk_enums.ROLE_SEARCH_FILE,
                       pk_enums.ROLE_WHAT_PROVIDES,
                       pk_enums.ROLE_REPO_ENABLE,
                       pk_enums.ROLE_INSTALL_SIGNATURE,
                       pk_enums.ROLE_DOWNLOAD_PACKAGES]
    if META_RELEASE_SUPPORT:
        SUPPORTED_ROLES.append(pk_enums.ROLE_GET_DISTRO_UPGRADES)

    SUPPORTED_FILTERS = [pk_enums.FILTER_INSTALLED,
                         pk_enums.FILTER_NOT_INSTALLED,
                         pk_enums.FILTER_FREE,
                         pk_enums.FILTER_NOT_FREE,
                         pk_enums.FILTER_GUI,
                         pk_enums.FILTER_NOT_GUI,
                         pk_enums.FILTER_COLLECTIONS,
                         pk_enums.FILTER_NOT_COLLECTIONS,
                         pk_enums.FILTER_SUPPORTED,
                         pk_enums.FILTER_NOT_SUPPORTED,
                         pk_enums.FILTER_NEWEST]

    def __init__(self, queue, connect=True, bus=None):
        """Initialize a new PackageKit compatibility layer.

        Keyword arguments:
        connect -- if the daemon should connect to the D-Bus (default is True)
        bus -- the D-Bus to connect to (defaults to the system bus)
        """
        pklog.info("Initializing PackageKit compat layer")
        bus_name = None
        bus_path = None
        if connect is True:
            if bus is None:
                bus = dbus.SystemBus()
            self.bus = bus
            bus_path = PACKAGEKIT_DBUS_PATH
            bus_name = dbus.service.BusName(PACKAGEKIT_DBUS_SERVICE, self.bus)
        core.DBusObject.__init__(self, bus_name, bus_path)
        self._updates_changed_timeout_id = None
        self._updates_changed = False
        self.queue = queue
        self.queue.worker.connect("transaction-done",
                                  self._on_transaction_done)
        self.queue.connect("queue-changed", self._on_queue_changed)
        self._distro_id = None
        self.netmon = networking.get_network_monitor()
        self.netmon.connect("network-state-changed",
                            self._on_network_state_changed)
        self._get_network_state()

    @inline_callbacks
    def _get_network_state(self):
        """Helper to defer the network state checking."""
        yield self.netmon.get_network_state()

    # SIGNALS

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_DBUS_INTERFACE,
                         signature="")
    def RestartSchedule(self):
        """A system restart has been sceduled."""
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_DBUS_INTERFACE,
                         signature="as")
    def TransactionListChanged(self, transactions):
        """The transaction list has changed, because either a transaction
        has finished or a new transaction created.

        :param transactions: A list of transaction ID's.
        :type transactions: as
        """
        pklog.debug("Emitting TransactionListChanged signal: %s", transactions)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_DBUS_INTERFACE,
                         signature="")
    def UpdatesChanged(self):
        """This signal is emitted when the number of updates has changed."""
        pklog.debug("Emitting UpdatesChanged signal")

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_DBUS_INTERFACE,
                         signature="")
    def RepoListChanged(self):
        """This signal is emitted when the repository list has changed."""
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_DBUS_INTERFACE,
                         signature="")
    def Changed(self):
        """This signal is emitted when a property on the interface changes."""
        pklog.debug("Emitting PackageKit Changed()")

    # METHODS

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_DBUS_INTERFACE,
                         in_signature="s", out_signature="s")
    def CanAuthorize(self, action_id):
        """Allows a client to find out if it would be allowed to authorize
        an action.

        :param action_id: The action ID, e.g.
                org.freedesktop.packagekit.system-network-proxy-configure
        :returns: The result, either yes, no or interactive.
        """
        #FIXME: We need to map packagekit and aptdaemon polices
        return "interactive"

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_DBUS_INTERFACE,
                         in_signature="s", out_signature="")
    def StateHasChanged(self, reason):
        """This method suggests to PackageKit that the package backend state
        may have changed. This allows plugins to the native package manager
        to suggest that PackageKit drops it's caches.

        :param reason:
            The reason of the state change. Valid reasons are resume or
            posttrans. Resume is given a lower priority than posttrans.
        """
        pklog.debug("StateHasChanged() was called: %s", reason)
        self._updates_changed = True
        if reason == "cache-update":
            self._check_updates_changed(timeout=30)
        elif reason == "resume":
            self._check_updates_changed(timeout=180)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_DBUS_INTERFACE,
                          in_signature="", out_signature="s",
                          sender_keyword="sender")
    def GetTid(self, sender):
        """Gets a new transaction ID from the daemon.

        :returns: The tid, e.g. 45_dafeca_checkpoint32
        """
        return self._get_tid(sender)

    @inline_callbacks
    def _get_tid(self, sender):
        pid, uid, cmdline = yield policykit1.get_proc_info_from_dbus_name(
            sender, self.bus)
        pktrans = PackageKitTransaction(pid, uid, cmdline, self.queue, sender)
        return_value(pktrans.tid)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_DBUS_INTERFACE,
                         in_signature="", out_signature="as")
    def GetTransactionList(self):
        """Gets the transaction list of any transactions that are in
        progress.

        :returns: A list of transaction ID's
        """
        pklog.debug("GetTransactionList() was called")
        return self._get_transaction_list()

    # HELPERS

    def _get_properties(self, iface):
        """Helper to get the properties of a D-Bus interface."""
        if iface == PACKAGEKIT_DBUS_INTERFACE:
            return {
                # Claim that we are a current version
                "VersionMajor": dbus.UInt32(7),
                "VersionMinor": dbus.UInt32(4),
                "VersionMicro": dbus.UInt32(0),
                "BackendName": dbus.String("aptdaemon"),
                "BackendDescription": dbus.String("Compatibility layer"),
                "BackendAuthor": dbus.String(__author__),
                "Filters": dbus.String(";".join(self.SUPPORTED_FILTERS)),
                "Groups": dbus.String(";".join(list(
                    SECTION_GROUP_MAP.values()))),
                "Roles": dbus.String(";".join(self.SUPPORTED_ROLES)),
                "Locked": dbus.Boolean(False),
                "NetworkState": dbus.String(self.netmon.state),
                "DistroId": dbus.String(self._get_distro_id())}
        else:
            return {}

    def _get_distro_id(self):
        """Return information about the distibution."""
        if self._distro_id is None:
            distro, version, _codename = platform.dist()
            arch = apt_pkg.get_architectures()[0]
            self._distro_id = "%s;%s;%s" % (distro or "unknown",
                                            version or "unknown",
                                            arch)
        return self._distro_id

    def _on_network_state_changed(self, mon, state):
        self.Changed()
        self.PropertiesChanged(PACKAGEKIT_DBUS_INTERFACE,
                               {"NetworkState": state}, [])

    def _on_queue_changed(self, queue):
        self.TransactionListChanged(self._get_transaction_list())
        self._check_updates_changed()

    def _get_transaction_list(self):
        pk_transactions = []
        for trans in self.queue.items:
            # We currently only emit PackageKit transaction
            #FIXME: Should we use MergedTransaction for all transactions and
            #       ROLE_UNKOWN for aptdaemon only transactions?
            try:
                pk_transactions.append(trans.pktrans.tid)
            except AttributeError:
                pass
        try:
            pk_transactions.append(self.queue.worker.trans.pktrans.tid)
        except AttributeError:
            pass
        return pk_transactions

    def _on_transaction_done(self, worker, trans):
        # If a cache modifing transaction is completed schedule an
        # UpdatesChanged signal
        if trans.role in (aptd_enums.ROLE_INSTALL_FILE,
                          aptd_enums.ROLE_INSTALL_PACKAGES,
                          aptd_enums.ROLE_REMOVE_PACKAGES,
                          aptd_enums.ROLE_UPGRADE_PACKAGES,
                          aptd_enums.ROLE_COMMIT_PACKAGES,
                          aptd_enums.ROLE_UPGRADE_SYSTEM,
                          aptd_enums.ROLE_FIX_BROKEN_DEPENDS):
            self._updates_changed = True
            self._check_updates_changed()
        elif trans.role == aptd_enums.ROLE_UPDATE_CACHE:
            self._updates_changed = True
            self._check_updates_changed(timeout=30)

    def _check_updates_changed(self, timeout=60):
        """After the queue was processed schedule a delayed UpdatesChanged
        signal if required.
        """
        if not self.queue.items and self._updates_changed:
            if self._updates_changed_timeout_id:
                # If we already have a scheduled UpdatesChanged signal
                # delay it even further
                pklog.debug("UpdatesChanged signal re-scheduled")
                GLib.source_remove(self._updates_changed_timeout_id)
            else:
                pklog.debug("UpdatesChanged signal scheduled")
            self._updates_changed_timeout_id = \
                GLib.timeout_add_seconds(timeout,
                                         self._delayed_updates_changed)

    def _delayed_updates_changed(self):
        """Emit the UpdatesChanged signal and clear the timeout."""
        self.UpdatesChanged()
        self._updates_changed_timeout_id = None
        self._updates_changed = False
        return False


class MergedTransaction(core.Transaction):

    """Overlay of an Aptdaemon transaction which also provides the
    PackageKit object and its interfaces.
    """

    def __init__(self, pktrans, role, queue, connect=True,
                 bus=None, packages=None, kwargs=None):
        core.Transaction.__init__(self, pktrans.tid[1:], role, queue,
                                  pktrans.pid, pktrans.uid,
                                  pktrans.cmdline, pktrans.sender,
                                  connect, bus, packages, kwargs)
        self.pktrans = pktrans
        self.run_time = 0

    @inline_callbacks
    def _run(self, sender):
        """Run the transaction and convert exceptions to PackageKit ones."""
        try:
            yield core.Transaction._run(self, sender)
        except errors.NotAuthorizedError as error:
            raise dbus.DBusException(
                error.get_message(),
                name="org.freedesktop.PackageKit.PermissionDenied")
        except Exception as error:
            raise error

    def _set_status(self, enum):
        core.Transaction._set_status(self, enum)
        self.pktrans.status = get_pk_status_enum(enum)

    status = property(core.Transaction._get_status, _set_status)

    def _set_progress(self, percent):
        core.Transaction._set_progress(self, percent)
        self.pktrans.percentage = self._progress

    progress = property(core.Transaction._get_progress, _set_progress)

    def _set_progress_details(self, details):
        core.Transaction._set_progress_details(self, details)
        self.pktrans.speed = int(details[4])
        self.pktrans.remaining_time = int(details[5])
        self.pktrans.elapsed_time = int(time.time() - self.pktrans.start_time)

    progress_details = property(core.Transaction._get_progress_details,
                                _set_progress_details)

    def _set_progress_package(self, progress):
        core.Transaction._set_progress_package(self, progress)
        pkg_name, enum = progress
        self.emit_package(get_pk_package_enum(enum),
                          get_pk_package_id(pkg_name),
                          "")

    progress_package = property(core.Transaction._get_progress_package,
                                _set_progress_package)

    def _set_exit(self, enum):
        core.Transaction._set_exit(self, enum)
        self.pktrans.exit = get_pk_exit_enum(enum)

    exit = property(core.Transaction._get_exit, _set_exit)

    def _set_error(self, excep):
        core.Transaction._set_error(self, excep)
        self.pktrans.ErrorCode(get_pk_error_enum(excep.code),
                               self._error_property[1])

    error = property(core.Transaction._get_error, _set_error)

    def _remove_from_connection_no_raise(self):
        core.Transaction._remove_from_connection_no_raise(self)
        self.pktrans.Destroy()
        try:
            self.pktrans.remove_from_connection()
        except LookupError as error:
            pklog.debug("remove_from_connection() raised LookupError: %s",
                        error)
        finally:
            self.pktrans.trans = None
            self.pktrans = None
        return False

    def emit_details(self, package_id, license, group, detail, url, size):
        self.pktrans.Details(package_id, license, group, detail, url, size)

    def emit_files(self, id, file_list):
        self.pktrans.Files(id, file_list)

    def emit_package(self, info, id, summary):
        self.pktrans.Package(info, id, summary)
        self.pktrans.last_package = id

    def emit_update_detail(self, package_id, updates, obsoletes, vendor_url,
                           bugzilla_url, cve_url, restart, update_text,
                           changelog, state, issued, updated):
        self.pktrans.UpdateDetail(package_id, updates, obsoletes, vendor_url,
                                  bugzilla_url, cve_url, restart, update_text,
                                  changelog, state, issued, updated)


class PackageKitTransaction(core.DBusObject):

    """Provides a PackageKit transaction object."""

    def __init__(self, pid, uid, cmdline, queue, sender,
                 connect=True, bus=None):
        pklog.info("Initializing PackageKit transaction")
        bus_name = None
        bus_path = None
        self.tid = "/%s" % uuid.uuid4().hex
        if connect is True:
            if bus is None:
                bus = dbus.SystemBus()
            self.bus = bus
            bus_path = self.tid
            bus_name = dbus.service.BusName(PACKAGEKIT_DBUS_SERVICE, bus)
        core.DBusObject.__init__(self, bus_name, bus_path)
        self.queue = queue
        self.hints = {}
        self.start_time = time.time()
        self._elapsed_time = dbus.UInt32(0)
        self._remaining_time = dbus.UInt32(0)
        self._speed = dbus.UInt32(0)
        self._caller_active = True
        self._allow_cancel = False
        self._percentage = dbus.UInt32(0)
        self._subpercentage = dbus.UInt32(0)
        self._status = pk_enums.STATUS_SETUP
        self._last_package = ""
        self.uid = dbus.UInt32(uid)
        self.pid = pid
        self.cmdline = cmdline
        self.role = pk_enums.ROLE_UNKNOWN
        self.sender = sender
        self.trans = None

    @property
    def allow_cancel(self):
        return self._allow_cancel

    @allow_cancel.setter
    def allow_cancel(self, value):
        self._allow_cancel = dbus.Boolean(value)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"AllowCancel": self._allow_cancel}, [])
        self.Changed()

    @property
    def last_package(self):
        return self._last_package

    @last_package.setter
    def last_package(self, value):
        self._last_package = dbus.String(value)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"LastPackage": self._last_package}, [])
        self.Changed()

    @property
    def caller_active(self):
        return self._caller_active

    @caller_active.setter
    def caller_active(self, value):
        self._caller_active = dbus.Boolean(value)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"CallerActive": self._caller_active}, [])
        self.Changed()

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, progress):
        self._percentage = dbus.UInt32(progress)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"Percentage": self._percentage}, [])
        self.Changed()

    @property
    def subpercentage(self):
        return self._subpercentage

    @subpercentage.setter
    def subpercentage(self, progress):
        self._subpercentage = dbus.UInt32(progress)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"SubPercentage": self._subpercentage}, [])
        self.Changed()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, enum):
        self._status = dbus.String(enum)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"Status": self._status}, [])
        self.Changed()

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, ela):
        self._elpased_time = dbus.UInt32(ela)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"ElapsedTime": self._elapsed_time}, [])
        self.Changed()

    @property
    def remaining_time(self):
        return self._remaining_time

    @remaining_time.setter
    def remaining_time(self, value):
        self._elpased_time = dbus.UInt32(value)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"RemainingTime": self._remaining_time}, [])
        self.Changed()

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = dbus.UInt32(speed)
        self.PropertiesChanged(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                               {"Speed": self._speed}, [])
        self.Changed()

    @property
    def exit(self):
        return self._exit

    @exit.setter
    def exit(self, enum):
        self._exit = exit
        self.run_time = int((time.time() - self.start_time) * 1000)
        # The time could go backwards ...
        if self.run_time < 0:
            self.run_time = 0
        if enum == pk_enums.EXIT_CANCELLED:
            self.ErrorCode(pk_enums.ERROR_TRANSACTION_CANCELLED, "")
        self.status = pk_enums.STATUS_FINISHED
        self.Finished(enum, self.run_time)

    # SIGNALS

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ssbsusus")
    def Transaction(self, old_tid, timespec, succeeded, role, duration, data,
                    uid, cmdline):
        """This signal is sent when more details are required about a
        specific transaction.

        :param old_tid: The transaction ID of the old transaction.
        :param timespec: The timespec of the old transaction in ISO8601 format.
        :param succeeded: If the transaction succeeded.
        :param role: The role enumerated type.
        :param duration: The duration of the transaction in milliseconds.
        :param data: Any data associated
        :param uid: The user ID of the user that scheduled the action.
        :param cmdline: The command line of the tool that scheduled the action,
            e.g. /usr/bin/gpk-application.
        """
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ss")
    def ErrorCode(self, code, details):
        """This signal is used to report errors back to the session program.
        Errors should only be send on fatal abort.

        :param code: Enumerated type, e.g. no-network.
        :param details: Long description or error, e.g. "failed to connect"

        :type code: s
        :type details: s
        """
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="")
    def Changed(self):
        """This signal is emitted when a property on the interface changes."""
        pklog.debug("Emitting PackageKitTransaction Changed()")

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="")
    def Destroy(self):
        """This signal is sent when the transaction has been destroyed
        and is no longer available for use."""
        pklog.debug("Emmitting Destroy()")

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="su")
    def Finished(self, exit, runtime):
        """This signal is used to signal that the transaction has finished.
        :param exit: The PkExitEnum describing the exit status of the
            transaction.
        :param runtime: The amount of time in milliseconds that the
            transaction ran for.

        :type exit: s
        :type runtime: u
        """
        pklog.debug("Emitting Finished: %s, %s", exit, runtime)
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ssssst")
    def Details(self, package_id, license, group, detail, url, size):
        """This signal allows the backend to convey more details about the
        package.

        :param package_id: The package ID

        :param license:
            The license string, e.g. GPLv2+ or BSD and (MPLv1.1 or GPLv2+).
            Moredetails about the correct way to format licensing strings can
            be found on the Fedora packaging wiki.
        :param group:
            The enumerated package group description
        :param detail:
            The multi-line package description. If formatting is required,
            then markdown syntax should be used, e.g. This is **critically**
            important
        :param url:
            The upstream project homepage
        :param size:
            The size of the package in bytes. This should be the size of the
            entire package file, not the size of the files installed on the
            system. If the package is not installed, and already downloaded
            and present in the package manager cache, then this value should
            be set to zero.
        """
        pklog.debug("Emmitting Details signal for %s", package_id)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ss")
    def Files(self, package_id, file_list):
        """This signal is used to push file lists from the backend to the
        session.

        :param package_id:
            The Package ID that called the method.
        :param file_list:
            The file list, with each file seporated with ;.
        """
        pklog.debug("Emitting Files signal: %s, %s", package_id, file_list)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ssssssssssss")
    def UpdateDetail(self, package_id, updates, obsoletes, vendor_url,
                     bugzilla_url, cve_url, restart, update_text, changelog,
                     state, issued, updated):
        """This signal is sent when more details are required about a
        specific update.

        :param package_id: The package ID
        :param updates:
            A list of package_id's that are to be updated, seporated by
            &. This odd delimited was chosen as \t is already being used
            in the spawned backends, and & is a banned character in a
            package_id.
        :param obsoletes:
            A list of package_id's that are to be obsoleted, separated by &
        :param vendor_url:
            A URL with more details on the update, e.g. a page with more
            information on the update. The format of this command should
            be http://www.foo.org/page.html?4567;Update to SELinux
        :param bugzilla_url:
            A bugzilla URL with more details on the update. If no URL is
            available then this field should be left empty.
        :param cve_url:
            A CVE URL with more details on the security advisory.
        :param restart:
            A valid restart type, e.g. system.
        :param update_text:
            The update text describing the update. If formatting is required,
            then markdown syntax should be used, e.g. This is **critically**
            important.
        :param changelog:
            The ChangeLog text describing the changes since the last version.
        :param state:
            The state of the update, e.g. stable or testing.
        :param issued:
            The ISO8601 encoded date that the update was issued.
        :param updated:
            The ISO8601 encoded date that the update was updated.
        """
        pklog.debug("Emmitting UpdateDetail signal for %s", package_id)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="sss")
    def Package(self, info, package_id, summary):
        """This signal allows the backend to communicate packages to the
        session.

        If updating, as packages are updated then emit them to the screen.
        This allows a summary to be presented after the transaction.
        When returning results from a search always return installed
        before available for the same package name.

        :param info: A valid info string enumerated type
        :param package_id: This identifier is of the form
            name;version;arch;data in a single string and is meant to
            represent a single package unique across all local and remote
            data stores. For a remote, not-installed package the data
            field should be set as the repository identifier or repository
            name. The data field for an installed package must be prefixed
            with installed as this is used to identify which packages are
            installable or installed in the client tools. As a special
            extension, if the package manager is able to track which
            repository a package was originally installed from, then the data
            field can be set to installed:REPO-NAME which allows the frontend
            client to advise the user of the package origin. The data field
            for a non-installed local package must be local as this signifies
            a repository name is not available and that package resides
            locally on the client system rather than in any specific
            repository.
        :param summary: The one line package summary, e.g. Clipart for
            OpenOffice
        """
        pklog.debug("Emmitting Package signal: info=%s id=%s summary='%s'",
                    info, package_id, summary[:10])

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="sss")
    def DistroUpgrade(self, type, name, summary):
        """This signal allows the backend to communicate distribution upgrades
        to the session.
        :param type: A valid upgrade string enumerated type, e.g. stable
            or unstable
        :param name: The short name of the distribution, e.g. Fedora Core
            10 RC1
        :param summary: The multi-line description of the release
        """
        pass

    # pylint: disable-msg=C0103,C0322
    @dbus.service.signal(dbus_interface=PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         signature="ss")
    def RequireRestart(self, restart_type, package_id):
        """This signal is sent when the session client should notify the user
        that a restart is required to get all changes into effect.

        :param package_id:
            The Package ID of the package tiggering the restart
        :param file_list:
            One of system, application or session
        """
        pklog.debug("Emitting RequireRestart signal: %s, %s",
                    restart_type, package_id)

    # METHODS

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="as", out_signature="")
    def SetHints(self, hints):
        """This method allows the calling session to set transaction hints
        for the package manager which can change as the transaction runs.

        This method can be sent before the transaction has been run or
        whilst it is running. There is no limit to the number of times
        this method can be sent, although some backends may only use the
        values that were set before the transaction was started.

        Each parameter value is optional.

        :param hints: The values as an array of strings, for example
            ['locale=en_GB.utf8','interactive=false','cache-age=3600']
        """
        for hint in hints:
            key, value = hint.split("=", 1)
            if key not in ["locale", "idle", "background", "interactive",
                           "cache-age", "frontend-socket"]:
                raise Exception("Invalid option %s" % key)
            self.hints[key] = value

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="", out_signature="",
                          sender_keyword="sender")
    def Cancel(self, sender):
        """This method cancels a transaction that is already running."""
        if self.trans:
            return self.trans._cancel(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="asbb", out_signature="",
                          sender_keyword="sender")
    def RemovePackages(self, package_ids, allow_deps, autoremove, sender):
        """This method removes packages from the local system.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be downloading, updating,
        installing or removing.

        :param package_ids: An array of package IDs.
        :param allow_deps:
            Either true or false. If true allow other packages to be removed
            with the package, but false should cause the script to abort if
            other packages are dependant on the package.
        :param autoremove:
            Either true or false. This option is only really interesting on
            embedded devices with a limited amount of flash storage. It
            suggests to the packagekit backend that dependencies installed at
            the same time as the package should also be removed if they are not
            required by anything else. For instance, if you install OpenOffice,
            it might download libneon as a dependency. When auto_remove is set
            to true, and you remove OpenOffice then libneon will also get
            removed automatically.
        """
        pklog.debug("RemovePackages() was called")
        self.role = pk_enums.ROLE_REMOVE_PACKAGES
        return self._remove_packages(package_ids, allow_deps, autoremove,
                                     sender)

    @inline_callbacks
    def _remove_packages(self, package_ids, allow_deps, autoremove, sender):
        self.trans = self._get_merged_trans(aptd_enums.ROLE_REMOVE_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_REMOVE)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "RemoveObsoletedDepends", autoremove,
                                       sender)
        try:
            yield self.trans._simulate(sender)
        except TransactionFailed:
            raise StopIteration
        for pkgs in self.trans.depends:
            if pkgs:
                error_code = pk_enums.ERROR_DEP_RESOLUTION_FAILED
                self.trans.pktrans.ErrorCode(
                    error_code, "Would change additional packages")
                self.trans.pktrans.exit = pk_enums.EXIT_FAILED
        yield self.trans._run(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="asb", out_signature="",
                         sender_keyword="sender")
    def SimulateRemovePackages(self, package_ids, autoremove, sender):
        """This method simulates a package update emitting packages
        required to be installed, removed, updated, reinstalled,
        downgraded, obsoleted or untrusted. The latter is used to present
        the user untrusted packages that are about to be installed.

        This method typically emits Error and Package.

        :param package_ids: An array of package IDs.
        :param autoremove:
            Either true or false. This option is only really interesting on
            embedded devices with a limited amount of flash storage. It
            suggests to the packagekit backend that dependencies installed at
            the same time as the package should also be removed if they are not
            required by anything else. For instance, if you install OpenOffice,
            it might download libneon as a dependency. When auto_remove is set
            to true, and you remove OpenOffice then libneon will also get
            removed automatically.
         """
        pklog.debug("SimulateRemovePackages() was called")
        GLib.idle_add(defer_idle, self._simulate_remove_packages,
                      package_ids, autoremove, sender)

    @inline_callbacks
    def _simulate_remove_packages(self, package_ids, autoremove, sender):
        self.role = pk_enums.ROLE_SIMULATE_REMOVE_PACKAGES
        self.status = pk_enums.STATUS_DEP_RESOLVE
        self.trans = self._get_merged_trans(aptd_enums.ROLE_REMOVE_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_REMOVE)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "RemoveObsoletedDepends", autoremove,
                                       sender)
        yield self._simulate_and_emit_packages(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="bas", out_signature="",
                          sender_keyword="sender")
    def UpdatePackages(self, only_trusted, package_ids, sender):
        """This method updates existing packages on the local system.

        The installer should always update extra packages automatically
        to fulfil dependencies.

        This should allow an application to find out what package owns a
        file on the system.

        This method typically emits Progress, Status and Error and Package.

        :param only_trusted:
            If the transaction is only allowed to install trusted packages.
            Unsigned packages should not be installed if this parameter is
            TRUE. If this method is can only install trusted packages, and
            the packages are unsigned, then the backend will send a
            ErrorCode(missing-gpg-signature). On recieving this error, the
            client may choose to retry with only_trusted FALSE after
            gaining further authentication.
        : param package_ids: An array of package IDs.
        """
        pklog.debug("UpdatePackages() was called")
        return self._update_packages(only_trusted, package_ids, sender)

    @inline_callbacks
    def _update_packages(self, only_trusted, package_ids, sender):
        self.role = pk_enums.ROLE_UPDATE_PACKAGES
        self.trans = self._get_merged_trans(aptd_enums.ROLE_UPGRADE_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_UPGRADE)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "AllowUnauthenticated",
                                       not only_trusted, sender)
        yield self.trans._run(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="as", out_signature="",
                         sender_keyword="sender")
    def SimulateUpdatePackages(self, package_ids, sender):
        """This method simulates a package update emitting packages
        required to be installed, removed, updated, reinstalled,
        downgraded, obsoleted or untrusted. The latter is used to present
        the user untrusted packages that are about to be installed.

        This method typically emits Error and Package.

        :param package_ids: An array of package IDs.
        """
        pklog.debug("SimulateUpdatePackages() was called")
        self.role = pk_enums.ROLE_SIMULATE_UPDATE_PACKAGES
        GLib.idle_add(defer_idle, self._simulate_update_packages,
                      package_ids, sender)

    @inline_callbacks
    def _simulate_update_packages(self, package_ids, sender):
        self.status = pk_enums.STATUS_RUNNING
        self.trans = self._get_merged_trans(aptd_enums.ROLE_UPGRADE_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_UPGRADE)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "AllowUnauthenticated", True, sender)
        yield self._simulate_and_emit_packages(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="bas", out_signature="",
                          sender_keyword="sender")
    def InstallPackages(self, only_trusted, package_ids, sender):
        """This method installs new packages on the local system.

        The installer should always install extra packages automatically
        as the use could call GetDepends prior to the install if a
        confirmation is required in the UI.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be downloading, updating,
        installing or removing.

        :param only_trusted:
            If the transaction is only allowed to install trusted packages.
            Unsigned packages should not be installed if this parameter is
            TRUE. If this method is can only install trusted packages, and
            the packages are unsigned, then the backend will send a
            ErrorCode(missing-gpg-signature). On recieving this error, the
            client may choose to retry with only_trusted FALSE after
            gaining further authentication.
        : param package_ids: An array of package IDs.
        """
        pklog.debug("InstallPackages() was called")
        self.role = pk_enums.ROLE_INSTALL_PACKAGES
        return self._install_packages(only_trusted, package_ids, sender)

    @inline_callbacks
    def _install_packages(self, only_trusted, package_ids, sender):
        self.trans = self._get_merged_trans(aptd_enums.ROLE_INSTALL_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_INSTALL)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "AllowUnauthenticated",
                                       not only_trusted, sender)
        yield self.trans._run(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="as", out_signature="",
                         sender_keyword="sender")
    def SimulateInstallPackages(self, package_ids, sender):
        """This method simulates a package instalation emitting packages
        required to be installed, removed, updated, reinstalled, downgraded,
        obsoleted or untrusted. The latter is used to present the user
        untrusted packages that are about to be installed.

        This method typically emits Error and Package.

        :param package_ids: An array of package IDs.
        """
        pklog.debug("SimulateInstallPackages() was called")
        self.role = pk_enums.ROLE_SIMULATE_INSTALL_PACKAGES
        GLib.idle_add(defer_idle, self._simulate_install_packages,
                      package_ids, sender)

    @inline_callbacks
    def _simulate_install_packages(self, package_ids, sender):
        self.status = pk_enums.STATUS_RUNNING
        self.trans = self._get_merged_trans(aptd_enums.ROLE_INSTALL_PACKAGES,
                                            pkg_ids=package_ids,
                                            pkg_type=aptd_enums.PKGS_INSTALL)
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "AllowUnauthenticated", True, sender)
        yield self._simulate_and_emit_packages(sender)

    @inline_callbacks
    def _simulate_and_emit_packages(self, sender, update_info=None):
        try:
            yield self.trans._simulate(sender)
        except:
            raise StopIteration
        for pkg in self.trans.depends[aptd_enums.PKGS_INSTALL]:
            self.Package(pk_enums.INFO_INSTALLING,
                         get_pk_package_id(pkg), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_REINSTALL]:
            self.Package(pk_enums.INFO_REINSTALLING,
                         get_pk_package_id(pkg, "installed"), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_REMOVE]:
            self.Package(pk_enums.INFO_REMOVING,
                         get_pk_package_id(pkg, "installed"), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_PURGE]:
            self.Package(pk_enums.INFO_REMOVING,
                         get_pk_package_id(pkg, "installed"), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_UPGRADE]:
            self.Package(update_info or pk_enums.INFO_UPDATING,
                         get_pk_package_id(pkg, None), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_DOWNGRADE]:
            self.Package(pk_enums.INFO_DOWNGRADING,
                         get_pk_package_id(pkg), "")
        for pkg in self.trans.depends[aptd_enums.PKGS_KEEP]:
            self.Package(pk_enums.INFO_BLOCKED,
                         get_pk_package_id(pkg), "")
        self.status = pk_enums.STATUS_FINISHED
        self.Finished(pk_enums.EXIT_SUCCESS, 0)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="b", out_signature="",
                          sender_keyword="sender")
    def RefreshCache(self, force, sender):
        """This method should fetch updated meta-data for all enabled
        repositories.

        When fetching each software source, ensure to emit RepoDetail for
        the current source to give the user interface some extra details.
        Be sure to have the "enabled" field set to true, otherwise you
        wouldn't be fetching that source.

        This method typically emits Progress, Error and RepoDetail.

        :param force: If the caches should be cleaned and reloaded even if
            there is valid, up to date data.
        """
        pklog.debug("RefreshCache() was called")
        self.role = pk_enums.ROLE_REFRESH_CACHE
        return self._refresh_cache(force, sender)

    @inline_callbacks
    def _refresh_cache(self, force, sender):
        self.trans = self._get_merged_trans(aptd_enums.ROLE_UPDATE_CACHE,
                                            kwargs={"sources_list": None})
        yield self.trans._run(sender)

    # pylint: disable-msg=C0103,C0322
    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="b", out_signature="",
                          sender_keyword="sender")
    def UpdateSystem(self, only_trusted, sender):
        """This method updates all packages on the system to thier newest
        versions.

        The installer should update all the updateable packages on the
        system, including automatically installing any new packages that
        are needed for dependancies.

        :param only_trusted:
            If the transaction is only allowed to install trusted packages.
            Unsigned packages should not be installed if this parameter is
            TRUE. If this method is can only install trusted packages, and
            the packages are unsigned, then the backend will send a
            ErrorCode(missing-gpg-signature). On recieving this error, the
            client may choose to retry with only_trusted FALSE after
            gaining further authentication.
        : param package_ids: An array of package IDs.
        """
        pklog.debug("UpdateSystem() was called")
        return self._update_system(only_trusted, sender)

    @inline_callbacks
    def _update_system(self, only_trusted, sender):
        self.role = pk_enums.ROLE_UPDATE_SYSTEM
        self.trans = self._get_merged_trans(aptd_enums.ROLE_UPGRADE_SYSTEM,
                                            kwargs={"safe_mode": False})
        yield self.trans._set_property(APTDAEMON_TRANSACTION_DBUS_INTERFACE,
                                       "AllowUnauthenticated",
                                       not only_trusted, sender)
        yield self.trans._run(sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="as", out_signature="",
                          sender_keyword="sender")
    def GetUpdateDetail(self, package_ids, sender):
        """This method returns details about a specific update.

        This method typically emits UpdateDetail and Error

        :param package_ids: An array of package IDs.
        """
        pklog.debug("GetUpdateDetail() was called")
        self.role = pk_enums.ROLE_GET_UPDATE_DETAIL
        kwargs = {"package_ids": package_ids}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="s", out_signature="",
                          sender_keyword="sender")
    def GetUpdates(self, filter, sender):
        """This method should return a list of packages that are installed
        and are upgradable. It should only return the newest update for
        each installed package.

        This method typically emits Progress, Error and Package.

        :param filter: A correct filter, e.g. none or installed;~devel
        """
        pklog.debug("GetUpdates() was called")
        self.role = pk_enums.ROLE_GET_UPDATES
        kwargs = {"filters": filter.split(";")}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="", out_signature="",
                         sender_keyword="sender")
    def GetDistroUpgrades(self, sender):
        """This method should return a list of distribution upgrades that are
        available. It should not return updates, only major upgrades.

        This method typically emits DistroUpgrade, Error
        """
        pklog.debug("GetDistroUpgrades() was called")
        self.role = pk_enums.ROLE_GET_DISTRO_UPGRADES
        self.status = pk_enums.STATUS_RUNNING
        GLib.idle_add(defer_idle, self._get_distro_upgrades)

    def _get_distro_upgrades(self):
        #FIXME: Should go into the worker after the threading branch is merged
        #       It allows to run a nested loop until the download is finished
        self.allow_cancel = False
        self.percentage = 101
        self.status = pk_enums.STATUS_DOWNLOAD_UPDATEINFO

        if META_RELEASE_SUPPORT is False:
            self.ErrorCode(pk_enums.ERROR_INTERNAL_ERROR,
                           "Please make sure that update-manager-core is"
                           "correctly installed.")
            self.exit = pk_enums.EXIT_FAILED
            return

        #FIXME Evil to start the download during init
        meta_release = GMetaRelease()
        meta_release.connect("download-done",
                             self._on_distro_upgrade_download_done)

    def _on_distro_upgrade_download_done(self, meta_release):
        #FIXME: Add support for description
        if meta_release.new_dist is not None:
            self.DistroUpgrade("stable",
                               "%s %s" % (meta_release.new_dist.name,
                                          meta_release.new_dist.version),
                               "The latest stable release")
        self.exit = pk_enums.EXIT_SUCCESS

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sas", out_signature="",
                          sender_keyword="sender")
    def Resolve(self, filter, packages, sender):
        """This method turns a single package name into a package_id suitable
        for the other methods.

        If the package is a fully formed package_id, then this should be
        treated as an exact package match. This is useful to find the summary
        or installed status of a package_id returned from other methods.

        This method typically emits Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param packages:
            An array of package names, e.g. scribus-clipart. The package
            names are case sensitive, so for instance: Resolve('Packagekit')
            would not match PackageKit. As a special case, if Resolve() is
            called with a name prefixed with @ then this should be treated as
            a category, for example: @web-development. In this instance, a
            meta-package should be emitted, for example:
            web-development;;;meta with the correct installed status and
            summary for the category.
        """
        pklog.debug("Resolve() was called")
        self.role = pk_enums.ROLE_RESOLVE
        kwargs = {"filters": filter.split(";"), "packages": packages}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="s", out_signature="",
                          sender_keyword="sender")
    def GetPackages(self, filter, sender):
        """This method returns all the packages without a search term.

        This method typically emits Progress, Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        """
        pklog.debug("GetPackages() was called")
        self.role = pk_enums.ROLE_GET_PACKAGES
        kwargs = {"filters": filter.split(";")}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="as", out_signature="",
                          sender_keyword="sender")
    def GetDetails(self, package_ids, sender):
        """This method should return all the details about a specific
        package_id.

        This method typically emits Progress, Status and Error and Details.

        :param package_ids: An array of package IDs.
        """
        pklog.debug("GetDetails() was called")
        self.role = pk_enums.ROLE_GET_DETAILS
        kwargs = {"package_ids": package_ids}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="as", out_signature="",
                          sender_keyword="sender")
    def GetFiles(self, package_ids, sender):
        """This method should return the file list of the package_id.

        This method typically emits Progress, Status and Error and Files.

        :param package_ids: An array of package IDs.
        """
        pklog.debug("GetFiles() was called")
        self.role = pk_enums.ROLE_GET_FILES
        kwargs = {"package_ids": package_ids}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sas", out_signature="",
                          sender_keyword="sender")
    def SearchFiles(self, filter, values, sender):
        """This method searches for files on the local system and files in
        available packages.

        This should search for files. This should allow an application to
        find out what package owns a file on the system.

        This method typically emits Progress, Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param values:
            A filename or fully qualified path and filename on the system.
            If the search term begins with a / it will be assumed the entire
            path has been given and only packages that contain this exact
            path and filename will be returned. If the search term does not
            start with / then it should be treated as a single filename,
            which can be in any directory. The search is case sensitive,
            and should not be escaped or surrounded in quotes.
        """
        pklog.debug("SearchFiles() was called")
        self.role = pk_enums.ROLE_SEARCH_FILE
        kwargs = {"filters": filter.split(";"),
                  "values": values}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sas", out_signature="",
                          sender_keyword="sender")
    def SearchDetails(self, filter, values, sender):
        """This method allows deeper searching than SearchName().

        Do not refresh the package cache. This should be fast. This is very
        similar to search-name. This should search as much data as possible,
        including, if possible repo names, package summaries, descriptions,
        licenses and URLs.

        Try to emit installed before available packages first, as it allows
        the client program to perform the GUI filtering and matching whilst
        the daemon is running the transaction.

        If the backend includes installed and available versions of the same
        package when searching then the available version will have to be
        filtered in the backend.

        This method typically emits Progress, Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param values:
            A single word search term with no wildcard chars. The search term
            can contain many words separated by spaces. In this case, the
            search operator is AND. For example, search of gnome power should
            returns gnome-power-manager but not gnomesword or powertop.
            The search should not be treated as case sensitive.
        """
        pklog.debug("SearchDetails() was called")
        self.role = pk_enums.ROLE_SEARCH_DETAILS
        kwargs = {"filters": filter.split(";"),
                  "values": values}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sas", out_signature="",
                          sender_keyword="sender")
    def SearchGroups(self, filter, values, sender):
        """This method returns packages from a given group enumerated type.

        Do not refresh the package cache. This should be fast.

        Try to emit installed before available packages first, as it
        allows the client program to perform the GUI filtering and matching
        whilst the daemon is running the transaction.

        If the backend includes installed and available versions of the same
        package when searching then the available version will have to be
        filtered in the backend.

        This method typically emits Progress, Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param values:
            An enumerated group type, or unknown. The search cannot contain
            spaces. The following recommendations are made below: If the values
            strings are prefixed with category: then the request is treated
            as a 'category search', for example: category:web-development.
            Note: the old nomenclature for a 'category search' suggested using
            a @ prefix for the values options. This is still supported, and
            backends should continue to support category searches like
            @web-development. If the values strings are prefixed with
            repo: then the request is treated as a 'repository search', for
            example: repo:fedora-debuginfo. In this instance all packages that
            were either installed from, or can be installed from the
            fedora-debuginfo source would be returned.
        """
        pklog.debug("SearchGroups() was called")
        self.role = pk_enums.ROLE_SEARCH_GROUP
        kwargs = {"filters": filter.split(";"),
                  "values": values}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sas", out_signature="",
                          sender_keyword="sender")
    def SearchNames(self, filter, values, sender):
        """This method searches the package database by package name.

        Try to emit installed before available packages first, as it
        allows the client program to perform the GUI filtering and matching
        whilst the daemon is running the transaction.

        If the backend includes installed and available versions of the same
        package when searching then the available version will have to be
        filtered in the backend.

        The search methods should return all results in all repositories.
        This may mean that multiple versions of package are returned. If this
        is not what is wanted by the client program, then the newest filter
        should be used.

        This method typically emits Progress, Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param values:
            A single word search term with no wildcard chars. The search term
            can contain many words separated by spaces. In this case, the
            search operator is AND. For example, search of gnome power should
            returns gnome-power-manager but not gnomesword or powertop.
            The search should not be treated as case sensitive.
        """
        pklog.debug("SearchNames() was called")
        self.role = pk_enums.ROLE_SEARCH_NAME
        kwargs = {"filters": filter.split(";"),
                  "values": values}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="s", out_signature="",
                         sender_keyword="sender")
    def AcceptEula(self, eula_id, sender):
        """This method allows the user to accept a end user licence agreement.

        :param eula_id: A valid EULA ID
        """
        self.role = pk_enums.ROLE_ACCEPT_EULA
        GLib.idle_add(self._fail_not_implemented)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="bas", out_signature="",
                          sender_keyword="sender")
    def DownloadPackages(self, store_in_cache, package_ids, sender):
        """This method downloads packages into a temporary directory.

        This method should emit one Files signal for each package that
        is downloaded, with the file list set as the name of the complete
        downloaded file and directory, so for example:

        DownloadPackages('hal;0.1.2;i386;fedora',
        'hal-info;2009-09-07;no-arch;updates') should send two signals,
        e.g. Files('hal;0.1.2;i386;fedora', '/tmp/hal-0.1.2.i386.rpm')
        and Files('hal-info;2009-09-07;no-arch;updates',
        '/tmp/hal-info-2009-09-07.noarch.rpm').

        :param store_in_cache:
            If the downloaded files should be stored in the system package
            cache rather than copied into a newly created directory. See the
            developer docs for more details on how this is supposed to work.
        :param package_ids: An array of package IDs.
        """
        self.role = pk_enums.ROLE_DOWNLOAD_PACKAGES
        kwargs = {"store_in_cache": store_in_cache,
                  "package_ids": package_ids}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="u", out_signature="",
                         sender_keyword="sender")
    def GetOldTransactions(self, number, sender):
        """This method allows a client to view details for old transactions.

        :param number:
            The number of past transactions, or 0 for all known transactions.
        """
        self.role = pk_enums.ROLE_GET_OLD_TRANSACTIONS
        GLib.idle_add(self._fail_not_implemented)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="s", out_signature="",
                         sender_keyword="sender")
    def GetRepoList(self, filter, sender):
        """This method returns the list of repositories used in the system.

        This method should emit RepoDetail.

        :param filter: A correct filter, e.g. none or installed;~devel
        """
        self.role = pk_enums.ROLE_GET_REPO_LIST
        GLib.idle_add(self._fail_not_implemented)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="as", out_signature="",
                         sender_keyword="sender")
    def SimulateInstallFiles(self, full_paths, sender):
        """This method simulates a package file instalation emitting packages
        required to be installed, removed, updated, reinstalled, downgraded,
        obsoleted or untrusted. The latter is used to present the user
        untrusted packages that are about to be installed.

        This method typically emits Error and Package.

        :param full_paths:
            An array of full path and filenames to packages.
        """
        self.role = pk_enums.ROLE_SIMULATE_INSTALL_FILES
        GLib.idle_add(self._fail_not_implemented)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="bas", out_signature="",
                         sender_keyword="sender")
    def InstallFiles(self, only_trusted, full_paths, sender):
        """This method installs local package files onto the local system.

        The installer should always install extra dependant packages
        automatically.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be downloading, updating, installing
        or removing.

        :param only_trusted:
            If the transaction is only allowed to install trusted files.
            Unsigned files should not be installed if this parameter is TRUE.
            If this method is can only install trusted files, and the files
            are unsigned, then the backend will send a
            ErrorCode(missing-gpg-signature). On recieving this error, the
            client may choose to retry with only_trusted FALSE after gaining
            further authentication.
        :param full_paths: An array of full path and filenames to packages.
        """
        self.role = pk_enums.ROLE_INSTALL_FILES
        GLib.idle_add(self._fail_not_implemented)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sss", out_signature="",
                          sender_keyword="sender")
    def InstallSignature(self, sig_type, key_id, package_id, sender):
        """This method allows us to install new security keys.

        :param sig_type: A key type, e.g. gpg
        :param key_id: A key ID, e.g. BB7576AC
        :param package_id:
            A PackageID for the package that the user is trying to install
            (ignored)
        """
        self.role = pk_enums.ROLE_INSTALL_SIGNATURE
        kwargs = {"sig_type": sig_type,
                  "key_id": key_id,
                  "package_id": package_id}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="sss", out_signature="",
                         sender_keyword="sender")
    def RepoSetData(self, repo_id, parameter, value, sender):
        """This method allows arbitary data to be passed to the repository
        handler.

        :param repo_id:
            A repository identifier, e.g. fedora-development-debuginfo
        :param parameter:
            The backend specific value, e.g. set-download-url.
        :param value:
            The backend specific value, e.g. http://foo.bar.org/baz.
        """
        self.role = pk_enums.ROLE_REPO_SET_DATA
        GLib.idle_add(self._fail_not_implemented)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sb", out_signature="",
                          sender_keyword="sender")
    def RepoEnable(self, repo_id, enabled, sender):
        """This method enables the repository specified.

        :param repo_id:
            A repository identifier, e.g. fedora-development-debuginfo or an
            apt source ("deb http://... unstable main")
        :param enabled: true if enabled, false if disabled.
        """
        self.role = pk_enums.ROLE_REPO_ENABLE
        kwargs = {"repo_id": repo_id,
                  "enabled": enabled}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="s", out_signature="",
                         sender_keyword="sender")
    def Rollback(self, transaction_id, sender):
        """This method rolls back the package database to a previous
        transaction.

        :param transaction_id: A valid transaction ID.
        """
        self.role = pk_enums.ROLE_GET_CATEGORIES
        GLib.idle_add(self._fail_not_implemented)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="ssas", out_signature="",
                          sender_keyword="sender")
    def WhatProvides(self, filter, type, values, sender):
        """This method returns packages that provide the supplied attributes.
        This method is useful for finding out what package(s) provide a
        modalias or GStreamer codec string.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be available or installed.

        :param filter:
            A correct filter, e.g. none or installed;~devel
        :param type:
            A PkProvideType, e.g. PK_PROVIDES_ENUM_CODEC.
        :param values:
            The data to send to the backend to get the packages. Note: This
            is backend specific.
        """
        self.role = pk_enums.ROLE_WHAT_PROVIDES
        kwargs = {"filters": filter.split(";"),
                  "type": type,
                  "values": values}
        return self._run_query(kwargs, sender)

    @dbus.service.method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                         in_signature="", out_signature="",
                         sender_keyword="sender")
    def GetCategories(self, sender):
        """This method return the collection categories"""
        self.role = pk_enums.ROLE_GET_CATEGORIES
        GLib.idle_add(self._fail_not_implemented)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sasb", out_signature="",
                          sender_keyword="sender")
    def GetRequires(self, filter, package_ids, recursive, sender):
        """This method returns packages that depend on this package. This is
        useful to know, as if package_id is being removed, we can warn the
        user what else would be removed.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param package_ids: An array of package IDs.
        :param recursive:
            Either true or false. If yes then the requirements should be
            returned for all packages returned. This means if
            gnome-power-manager depends on NetworkManager and NetworkManager
            depends on HAL, then GetRequires on HAL should return both
            gnome-power-manager and NetworkManager.
        """
        self.role = pk_enums.ROLE_GET_REQUIRES
        kwargs = {"filters": filter.split(";"),
                  "package_ids": package_ids,
                  "recursive": recursive}
        return self._run_query(kwargs, sender)

    @dbus_deferred_method(PACKAGEKIT_TRANS_DBUS_INTERFACE,
                          in_signature="sasb", out_signature="",
                          sender_keyword="sender")
    def GetDepends(self, filter, package_ids, recursive, sender):
        """This method returns packages that this package depends on.

        This method typically emits Progress, Status and Error and Package.

        Package enumerated types should be available or installed.

        :param filter: A correct filter, e.g. none or installed;~devel
        :param package_ids: An array of package IDs.
        :param recursive:
            Either true or false. If yes then the requirements should be
            returned for all packages returned. This means if
            gnome-power-manager depends on NetworkManager and NetworkManager
            depends on HAL, then GetDepends on gnome-power-manager should
            return both HAL and NetworkManager.
        """
        self.role = pk_enums.ROLE_GET_DEPENDS
        kwargs = {"filters": filter.split(";"),
                  "package_ids": package_ids,
                  "recursive": recursive}
        return self._run_query(kwargs, sender)

    # HELPERS

    def _fail_not_implemented(self):
        self.ErrorCode(pk_enums.ERROR_NOT_SUPPORTED, "Unimplemented method")
        self.exit = pk_enums.EXIT_FAILED
        return False

    def _get_properties(self, iface):
        """Helper to get the properties of a D-Bus interface."""
        if iface == PACKAGEKIT_TRANS_DBUS_INTERFACE:
            return {"Role": dbus.String(self.role),
                    "Status": dbus.String(self.status),
                    "LastPackage": dbus.String(self.last_package),
                    "Uid": dbus.UInt32(self.uid),
                    "Percentage": dbus.UInt32(self.percentage),
                    "Subpercentage": dbus.UInt32(self.subpercentage),
                    "AllowCancel": dbus.Boolean(self.allow_cancel),
                    "CallerActive": dbus.Boolean(self.caller_active),
                    "ElapsedTime": dbus.UInt32(self.elapsed_time),
                    "RemainingTime": dbus.UInt32(self.remaining_time),
                    "Speed": dbus.UInt32(self.speed)
                    }
        else:
            return {}

    @inline_callbacks
    def _run_query(self, kwargs, sender):
        self.trans = self._get_merged_trans(aptd_enums.ROLE_PK_QUERY,
                                            kwargs=kwargs)
        yield self.trans._run(sender)

    def _get_merged_trans(self, role, pkg_ids=None, pkg_type=None,
                          kwargs=None):
        if pkg_ids:
            packages = [[], [], [], [], [], []]
            packages[pkg_type] = [get_aptd_package_id(pkg) for pkg in pkg_ids]
        else:
            packages = None
        if self.trans:
            raise Exception("%s: Transaction may only run once." %
                            pk_enums.ERROR_TRANSACTION_FAILED)
        trans = MergedTransaction(self, role, self.queue,
                                  packages=packages, kwargs=kwargs)
        try:
            trans._set_locale(self.hints["locale"])
        except (KeyError, ValueError):
            # If the locale isn't vaild or supported a ValueError
            # will be raised
            pass
        try:
            trans._set_debconf(self.hints["frontend-socket"])
        except KeyError:
            pass
        self.queue.limbo[trans.tid] = trans
        return trans


class PackageKitWorker(worker.AptWorker):

    _plugins = None

    """Process PackageKit Query transactions."""

    def query(self, trans):
        """Run the worker"""
        if trans.role != aptd_enums.ROLE_PK_QUERY:
            raise TransactionFailed(aptd_enums.ERROR_UNKNOWN,
                                    "The transaction doesn't seem to be "
                                    "a query")
        if trans.pktrans.role == pk_enums.ROLE_RESOLVE:
            self.resolve(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_UPDATES:
            self.get_updates(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_UPDATE_DETAIL:
            self.get_update_detail(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_PACKAGES:
            self.get_packages(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_FILES:
            self.get_files(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_SEARCH_NAME:
            self.search_names(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_SEARCH_GROUP:
            self.search_groups(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_SEARCH_DETAILS:
            self.search_details(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_SEARCH_FILE:
            self.search_files(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_DEPENDS:
            self.get_depends(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_REQUIRES:
            self.get_requires(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_GET_DETAILS:
            self.get_details(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_DOWNLOAD_PACKAGES:
            self.download_packages(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_WHAT_PROVIDES:
            self.what_provides(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_REPO_ENABLE:
            self.repo_enable(trans, **trans.kwargs)
        elif trans.pktrans.role == pk_enums.ROLE_INSTALL_SIGNATURE:
            self.install_signature(trans, **trans.kwargs)
        else:
            raise TransactionFailed(aptd_enums.ERROR_UNKNOWN,
                                    "Role %s isn't supported",
                                    trans.pktrans.role)

    def search_files(self, trans, filters, values):
        """Implement org.freedesktop.PackageKit.Transaction.SearchFiles()

        Works only for installed file if apt-file isn't installed.
        """
        trans.progress = 101

        result_names = set()
        # Optionally make use of apt-file's Contents cache to search for not
        # installed files. But still search for installed files additionally
        # to make sure that we provide up-to-date results
        if (os.path.exists("/usr/bin/apt-file") and
                pk_enums.FILTER_INSTALLED not in filters):
            #FIXME: Make use of rapt-file on Debian if the network is available
            #FIXME: Show a warning to the user if the apt-file cache is several
            #       weeks old
            pklog.debug("Using apt-file")
            filenames_regex = []
            for filename in values:
                if filename.startswith("/"):
                    pattern = "^%s$" % filename[1:].replace("/", "\/")
                else:
                    pattern = "\/%s$" % filename
                filenames_regex.append(pattern)
            cmd = ["/usr/bin/apt-file", "--regexp", "--non-interactive",
                   "--package-only", "find", "|".join(filenames_regex)]
            pklog.debug("Calling: %s" % cmd)
            apt_file = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            stdout, stderr = apt_file.communicate()
            if apt_file.returncode == 0:
                #FIXME: Actually we should check if the file is part of the
                #       candidate, e.g. if unstable and experimental are
                #       enabled and a file would only be part of the
                #       experimental version
                result_names.update(stdout.split())
                self._emit_visible_packages_by_name(trans, filters,
                                                    result_names)
            else:
                raise TransactionFailed(aptd_enums.ERROR_INTERNAL_ERROR,
                                        "%s %s" % (stdout, stderr))
        # Search for installed files
        filenames_regex = []
        for filename in values:
            if filename.startswith("/"):
                pattern = "^%s$" % filename.replace("/", "\/")
            else:
                pattern = ".*\/%s$" % filename
            filenames_regex.append(pattern)
        files_pattern = re.compile("|".join(filenames_regex))
        for pkg in self._iterate_packages():
            if pkg.name in result_names:
                continue
            for installed_file in self._get_installed_files(pkg):
                if files_pattern.match(installed_file):
                    self._emit_visible_package(trans, filters, pkg)
                    break

    def search_groups(self, trans, filters, values):
        """Implement org.freedesktop.PackageKit.Transaction.SearchGroups()"""
        #FIXME: Handle repo and category search
        trans.progress = 101

        for pkg in self._iterate_packages():
            if self._get_package_group(pkg) in values:
                self._emit_visible_package(trans, filters, pkg)

    def search_names(self, trans, filters, values):
        """Implement org.freedesktop.PackageKit.Transaction.SearchNames()"""
        def matches(searches, text):
            for search in searches:
                if not search in text:
                    return False
            return True
        pklog.info("Searching for package name: %s" % values)
        trans.progress = 101

        for pkg_name in list(self._cache.keys()):
            if matches(values, pkg_name):
                self._emit_all_visible_pkg_versions(trans, filters,
                                                    self._cache[pkg_name])

    def search_details(self, trans, filters, values):
        """Implement org.freedesktop.PackageKit.Transaction.SearchDetails()"""
        trans.progress = 101

        if XAPIAN_SUPPORT is True:
            search_flags = (xapian.QueryParser.FLAG_BOOLEAN |
                            xapian.QueryParser.FLAG_PHRASE |
                            xapian.QueryParser.FLAG_LOVEHATE |
                            xapian.QueryParser.FLAG_BOOLEAN_ANY_CASE)
            pklog.debug("Performing xapian db based search")
            db = xapian.Database(XAPIAN_DB)
            parser = xapian.QueryParser()
            parser.set_default_op(xapian.Query.OP_AND)
            query = parser.parse_query(" ".join(values), search_flags)
            enquire = xapian.Enquire(db)
            enquire.set_query(query)
            matches = enquire.get_mset(0, 1000)
            for pkg_name in (match.document.get_data()
                             for match in enquire.get_mset(0, 1000)):
                if pkg_name in self._cache:
                    self._emit_visible_package(trans, filters,
                                               self._cache[pkg_name])
        else:
            def matches(searches, text):
                for search in searches:
                    if not search in text:
                        return False
                return True
            pklog.debug("Performing apt cache based search")
            values = [val.lower() for val in values]
            for pkg in self._iterate_packages():
                txt = pkg.name
                try:
                    txt += pkg.candidate.raw_description.lower()
                    txt += pkg.candidate._translated_records.long_desc.lower()
                except AttributeError:
                    pass
                if matches(values, txt):
                    self._emit_visible_package(trans, filters, pkg)

    def get_updates(self, trans, filters):
        """Only report updates which can be installed safely: Which can depend
        on the installation of additional packages but which don't require
        the removal of already installed packages or block any other update.
        """
        def succeeds_security_update(pkg):
            """
            Return True if an update succeeds a previous security update

            An example would be a package with version 1.1 in the security
            archive and 1.1.1 in the archive of proposed updates or the
            same version in both archives.
            """
            for version in pkg.versions:
                # Only check versions between the installed and the candidate
                if (pkg.installed and
                    apt_pkg.version_compare(version.version,
                                            pkg.installed.version) <= 0 and
                    apt_pkg.version_compare(version.version,
                                            pkg.candidate.version) > 0):
                    continue
                for origin in version.origins:
                    if (origin.origin in ["Debian", "Ubuntu"] and
                            (origin.archive.endswith("-security") or
                             origin.label == "Debian-Security") and
                            origin.trusted):
                        return True
            return False
        #FIXME: Implment the basename filter
        pklog.info("Get updates()")
        self.cancellable = False
        self.progress = 101
        # Start with a safe upgrade
        try:
            self._cache.upgrade(dist_upgrade=True)
        except SystemError:
            pass
        for pkg in self._iterate_packages():
            if not pkg.is_upgradable:
                continue
            # This may occur on pinned packages which have been updated to
            # later version than the pinned one
            if not pkg.candidate.origins:
                continue
            if not pkg.marked_upgrade:
                #FIXME: Would be nice to all show why
                self._emit_package(trans, pkg, pk_enums.INFO_BLOCKED,
                                   force_candidate=True)
                continue
            # The update can be safely installed
            info = pk_enums.INFO_NORMAL
            # Detect the nature of the upgrade (e.g. security, enhancement)
            candidate_origin = pkg.candidate.origins[0]
            archive = candidate_origin.archive
            origin = candidate_origin.origin
            trusted = candidate_origin.trusted
            label = candidate_origin.label
            if origin in ["Debian", "Ubuntu"] and trusted is True:
                if archive.endswith("-security") or label == "Debian-Security":
                    info = pk_enums.INFO_SECURITY
                elif succeeds_security_update(pkg):
                    pklog.debug("Update of %s succeeds a security update. "
                                "Raising its priority." % pkg.name)
                    info = pk_enums.INFO_SECURITY
                elif archive.endswith("-backports"):
                    info = pk_enums.INFO_ENHANCEMENT
                elif archive.endswith("-updates"):
                    info = pk_enums.INFO_BUGFIX
            if origin in ["Backports.org archive"] and trusted is True:
                info = pk_enums.INFO_ENHANCEMENT
            self._emit_package(trans, pkg, info, force_candidate=True)
        self._emit_require_restart(trans)

    def _emit_require_restart(self, trans):
        """Emit RequireRestart if required."""
        # Check for a system restart
        if self.is_reboot_required():
            trans.pktrans.RequireRestart(pk_enums.RESTART_SYSTEM, "")

    def get_update_detail(self, trans, package_ids):
        """
        Implement the {backend}-get-update-details functionality
        """
        def get_bug_urls(changelog):
            """
            Create a list of urls pointing to closed bugs in the changelog
            """
            urls = []
            for r in re.findall(MATCH_BUG_CLOSES_DEBIAN, changelog,
                                re.IGNORECASE | re.MULTILINE):
                urls.extend([HREF_BUG_DEBIAN % bug for bug in
                             re.findall(MATCH_BUG_NUMBERS, r)])
            for r in re.findall(MATCH_BUG_CLOSES_UBUNTU, changelog,
                                re.IGNORECASE | re.MULTILINE):
                urls.extend([HREF_BUG_UBUNTU % bug for bug in
                             re.findall(MATCH_BUG_NUMBERS, r)])
            return urls

        def get_cve_urls(changelog):
            """
            Create a list of urls pointing to cves referred in the changelog
            """
            return [HREF_CVE % c for c in re.findall(MATCH_CVE, changelog,
                                                     re.MULTILINE)]

        pklog.info("Get update details of %s" % package_ids)
        trans.progress = 0
        trans.cancellable = False
        trans.pktrans.status = pk_enums.STATUS_DOWNLOAD_CHANGELOG
        total = len(package_ids)
        count = 1
        old_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "C")
        for pkg_id in package_ids:
            self._iterate_mainloop()
            trans.progress = count * 100 / total
            count += 1
            pkg = self._get_package_by_id(pkg_id)
            # FIXME add some real data
            if pkg.installed.origins:
                installed_origin = pkg.installed.origins[0].label
            else:
                installed_origin = ""
            updates = "%s;%s;%s;%s" % (pkg.name, pkg.installed.version,
                                       pkg.installed.architecture,
                                       installed_origin)
            obsoletes = ""
            vendor_url = ""
            restart = "none"
            update_text = ""
            state = ""
            issued = ""
            updated = ""
            #FIXME: make this more configurable. E.g. a dbus update requires
            #       a reboot on Ubuntu but not on Debian
            if (pkg.name.startswith("linux-image-") or
                    pkg.name in ["libc6", "dbus"]):
                restart == pk_enums.RESTART_SYSTEM
            changelog_dir = apt_pkg.config.find_dir("Dir::Cache::Changelogs")
            if changelog_dir == "/":
                changelog_dir = os.path.join(apt_pkg.config.find_dir("Dir::"
                                                                     "Cache"),
                                             "Changelogs")
            filename = os.path.join(changelog_dir,
                                    "%s_%s.gz" % (pkg.name,
                                                  pkg.candidate.version))
            changelog_raw = ""
            if os.path.exists(filename):
                pklog.debug("Reading changelog from cache")
                changelog_file = gzip.open(filename, "rb")
                try:
                    changelog_raw = changelog_file.read().decode("UTF-8")
                except:
                    pass
                finally:
                    changelog_file.close()
            if not changelog_raw:
                pklog.debug("Downloading changelog")
                changelog_raw = pkg.get_changelog()
                # The internal download error string of python-apt ist not
                # provided as unicode object
                if not isinstance(changelog_raw, str):
                    changelog_raw = changelog_raw.decode("UTF-8")
                # Cache the fetched changelog
                if not os.path.exists(changelog_dir):
                    os.makedirs(changelog_dir)
                # Remove old cached changelogs
                pattern = os.path.join(changelog_dir, "%s_*" % pkg.name)
                for old_changelog in glob.glob(pattern):
                    os.remove(os.path.join(changelog_dir, old_changelog))
                changelog_file = gzip.open(filename, mode="wb")
                try:
                    changelog_file.write(changelog_raw.encode("UTF-8"))
                finally:
                    changelog_file.close()
           # Convert the changelog to markdown syntax
            changelog = ""
            for line in changelog_raw.split("\n"):
                if line == "":
                    changelog += " \n"
                else:
                    changelog += "    %s  \n" % line
                if line.startswith(pkg.candidate.source_name):
                    match = re.match(r"(?P<source>.+) \((?P<version>.*)\) "
                                     "(?P<dist>.+); urgency=(?P<urgency>.+)",
                                     line)
                    update_text += "%s\n%s\n\n" % (match.group("version"),
                                                   "=" *
                                                   len(match.group("version")))
                elif line.startswith("  "):
                    update_text += "  %s  \n" % line
                elif line.startswith(" --"):
                    #FIXME: Add %z for the time zone - requires Python 2.6
                    update_text += "  \n"
                    match = re.match("^ -- (?P<maintainer>.+) (?P<mail><.+>)  "
                                     "(?P<date>.+) (?P<offset>[-\+][0-9]+)$",
                                     line)
                    if not match:
                        continue
                    try:
                        date = datetime.datetime.strptime(match.group("date"),
                                                          "%a, %d %b %Y "
                                                          "%H:%M:%S")
                    except ValueError:
                        continue
                    issued = date.isoformat()
                    if not updated:
                        updated = date.isoformat()
            if issued == updated:
                updated = ""
            bugzilla_url = ";;".join(get_bug_urls(changelog))
            cve_url = ";;".join(get_cve_urls(changelog))
            trans.emit_update_detail(pkg_id, updates, obsoletes, vendor_url,
                                     bugzilla_url, cve_url, restart,
                                     update_text, changelog,
                                     state, issued, updated)
        locale.setlocale(locale.LC_TIME, old_locale)

    def get_details(self, trans, package_ids):
        """Implement org.freedesktop.PackageKit.Transaction.GetDetails()"""
        trans.progress = 101

        for pkg_id in package_ids:
            version = self._get_version_by_id(pkg_id)
            #FIXME: We need more fine grained license information!
            origins = version.origins
            if (origins and
                    origins[0].component in ["main", "universe"] and
                    origins[0].origin in ["Debian", "Ubuntu"]):
                license = "free"
            else:
                license = "unknown"
            group = self._get_package_group(version.package)
            trans.emit_details(pkg_id, license, group, version.description,
                               version.homepage, version.size)

    def get_packages(self, trans, filters):
        """Implement org.freedesktop.PackageKit.Transaction.GetPackages()"""
        pklog.info("Get all packages")
        self.progress = 101

        for pkg in self._iterate_packages():
            if self._is_package_visible(pkg, filters):
                self._emit_package(trans, pkg)

    def resolve(self, trans, filters, packages):
        """Implement org.freedesktop.PackageKit.Transaction.Resolve()"""
        pklog.info("Resolve()")
        trans.status = aptd_enums.STATUS_QUERY
        trans.progress = 101
        self.cancellable = False

        for name_raw in packages:
            #FIXME: Python-apt doesn't allow unicode as key. See #542965
            name = str(name_raw)
            try:
                # Check if the name is a valid package id
                version = self._get_version_by_id(name)
            except ValueError:
                pass
            else:
                if self._package_is_visible(version.package, filters):
                    self._emit_pkg_version(trans, version)
                continue
            # The name seems to be a normal name
            try:
                self._emit_visible_package(trans, filters, self._cache[name])
            except KeyError:
                raise TransactionFailed(aptd_enums.ERROR_NO_PACKAGE,
                                        "Package name %s could not be "
                                        "resolved.", name)

    def get_depends(self, trans, filters, package_ids, recursive):
        """Emit all dependencies of the given package ids.

        Doesn't support recursive dependency resolution.
        """
        def emit_blocked_dependency(base_dependency, pkg=None,
                                    filters=""):
            """Send a blocked package signal for the given
            apt.package.BaseDependency.
            """
            if pk_enums.FILTER_INSTALLED in filters:
                return
            if pkg:
                summary = pkg.candidate.summary
                try:
                    filters.remove(pk_enums.FILTER_NOT_INSTALLED)
                except ValueError:
                    pass
                if not self._is_package_visible(pkg, filters):
                    return
            else:
                summary = ""
            if base_dependency.relation:
                version = "%s%s" % (base_dependency.relation,
                                    base_dependency.version)
            else:
                version = base_dependency.version
            trans.emit_package("%s;%s;;" % (base_dependency.name, version),
                               pk_enums.INFO_BLOCKED, summary)

        def check_dependency(pkg, base_dep):
            """Check if the given apt.package.Package can satisfy the
            BaseDepenendcy and emit the corresponding package signals.
            """
            if not self._is_package_visible(pkg, filters):
                return
            if base_dep.version:
                satisfied = False
                # Sort the version list to check the installed
                # and candidate before the other ones
                ver_list = list(pkg.versions)
                if pkg.installed:
                    ver_list.remove(pkg.installed)
                    ver_list.insert(0, pkg.installed)
                if pkg.candidate:
                    ver_list.remove(pkg.candidate)
                    ver_list.insert(0, pkg.candidate)
                for dep_ver in ver_list:
                    if apt_pkg.check_dep(dep_ver.version,
                                         base_dep.relation,
                                         base_dep.version):
                        self._emit_pkg_version(trans, dep_ver)
                        satisfied = True
                        break
                if not satisfied:
                    emit_blocked_dependency(base_dep, pkg, filters)
            else:
                self._emit_package(trans, pkg)

        # Setup the transaction
        pklog.info("Get depends (%s,%s,%s)" % (filter, package_ids, recursive))
        self.status = aptd_enums.STATUS_RESOLVING_DEP
        trans.progress = 101
        self.cancellable = True

        dependency_types = ["PreDepends", "Depends"]
        if apt_pkg.config["APT::Install-Recommends"]:
            dependency_types.append("Recommends")
        for id in package_ids:
            version = self._get_version_by_id(id)
            for dependency in version.get_dependencies(*dependency_types):
                # Walk through all or_dependencies
                for base_dep in dependency.or_dependencies:
                    if self._cache.is_virtual_package(base_dep.name):
                        # Check each proivider of a virtual package
                        for provider in self._cache.get_providing_packages(
                                base_dep.name):
                            check_dependency(provider, base_dep)
                    elif base_dep.name in self._cache:
                        check_dependency(self._cache[base_dep.name], base_dep)
                    else:
                        # The dependency does not exist
                        emit_blocked_dependency(trans, base_dep,
                                                filters=filters)

    def get_requires(self, trans, filters, package_ids, recursive):
        """Emit all packages which depend on the given ids.

        Recursive searching is not supported.
        """
        pklog.info("Get requires (%s,%s,%s)", filter, package_ids, recursive)
        self.status = aptd_enums.STATUS_RESOLVING_DEP
        self.progress = 101
        self.cancellable = True
        for id in package_ids:
            version = self._get_version_by_id(id)
            for pkg in self._iterate_packages():
                if not self._is_package_visible(pkg, filters):
                    continue
                if pkg.is_installed:
                    pkg_ver = pkg.installed
                elif pkg.candidate:
                    pkg_ver = pkg.candidate
                for dependency in pkg_ver.dependencies:
                    satisfied = False
                    for base_dep in dependency.or_dependencies:
                        if (version.package.name == base_dep.name or
                                base_dep.name in version.provides):
                            satisfied = True
                            break
                    if satisfied:
                        self._emit_package(trans, pkg)
                        break

    def download_packages(self, trans, store_in_cache, package_ids):
        """Implement the DownloadPackages functionality.

        The store_in_cache parameter gets ignored.
        """
        def get_download_details(ids):
            """Calculate the start and end point of a package download
            progress.
            """
            total = 0
            downloaded = 0
            versions = []
            # Check if all ids are vaild and calculate the total download size
            for id in ids:
                pkg_ver = self._get_version_by_id(id)
                if not pkg_ver.downloadable:
                    raise TransactionFailed(
                        aptd_enums.ERROR_PACKAGE_DOWNLOAD_FAILED,
                        "package %s isn't downloadable" % id)
                total += pkg_ver.size
                versions.append((id, pkg_ver))
            for id, ver in versions:
                start = downloaded * 100 / total
                end = start + ver.size * 100 / total
                yield id, ver, start, end
                downloaded += ver.size
        pklog.info("Downloading packages: %s" % package_ids)
        trans.status = aptd_enums.STATUS_DOWNLOADING
        trans.cancellable = True
        trans.progress = 10
        # Check the destination directory
        if store_in_cache:
            dest = apt_pkg.config.find_dir("Dir::Cache::archives")
        else:
            dest = tempfile.mkdtemp(prefix="aptdaemon-download")
        if not os.path.isdir(dest) or not os.access(dest, os.W_OK):
            raise TransactionFailed(aptd_enums.ERROR_INTERNAL_ERROR,
                                    "The directory '%s' is not writable" %
                                    dest)
        # Start the download
        for id, ver, start, end in get_download_details(package_ids):
            progress = DaemonAcquireProgress(trans, start, end)
            self._emit_pkg_version(trans, ver, pk_enums.INFO_DOWNLOADING)
            try:
                ver.fetch_binary(dest, progress)
            except Exception as error:
                raise TransactionFailed(
                    aptd_enums.ERROR_PACKAGE_DOWNLOAD_FAILED, str(error))
            else:
                trans.emit_files(id,
                                 os.path.join(dest,
                                              os.path.basename(ver.filename)))
                self._emit_pkg_version(trans, ver, pk_enums.INFO_FINISHED)

    def get_files(self, trans, package_ids):
        """Emit the Files signal which includes the files included in a package
        Apt only supports this for installed packages
        """
        for id in package_ids:
            pkg = self._get_package_by_id(id)
            files = ";".join(self._get_installed_files(pkg))
            trans.emit_files(id, files)

    def what_provides(self, trans, filters, type, values):
        """Emit all packages which provide the given type and search value."""
        self._init_plugins()

        supported_type = False

        # run plugins
        for plugin in self._plugins.get("what_provides", []):
            pklog.debug("calling what_provides plugin %s %s",
                        str(plugin), str(filters))
            for search_item in values:
                try:
                    for package in plugin(self._cache, type, search_item):
                        self._emit_visible_package(trans, filters, package)
                    supported_type = True
                except NotImplementedError:
                    # keep supported_type as False
                    pass

        if not supported_type and type != pk_enums.PROVIDES_ANY:
            # none of the plugins felt responsible for this type
            raise TransactionFailed(aptd_enums.ERROR_NOT_SUPPORTED,
                                    "Query type '%s' is not supported" % type)

    def repo_enable(self, trans, repo_id, enabled):
        """Enable or disable a repository."""
        if not enabled:
            raise TransactionFailed(aptd_enums.ERROR_NOT_SUPPORTED,
                                    "Disabling repositories is not "
                                    "implemented")

        fields = repo_id.split()
        if len(fields) < 3 or fields[0] not in ('deb', 'deb-src'):
            raise TransactionFailed(
                aptd_enums.ERROR_NOT_SUPPORTED,
                "Unknown repository ID format: %s" % repo_id)

        self.add_repository(trans, fields[0], fields[1], fields[2],
                            fields[3:], '', None)

    def install_signature(self, trans, sig_type, key_id, package_id):
        """Install an archive key."""
        if sig_type != "gpg":
            raise TransactionFailed(aptd_enums.ERROR_NOT_SUPPORTED,
                                    "Type %s is not supported" % sig_type)
        try:
            keyserver = os.environ["APTDAEMON_KEYSERVER"]
        except KeyError:
            if platform.dist()[0] == "Ubuntu":
                keyserver = "hkp://keyserver.ubuntu.com:80"
            else:
                keyserver = "hkp://keys.gnupg.net"
        self.add_vendor_key_from_keyserver(trans, key_id, keyserver)

    # Helpers

    def _get_id_from_version(self, version):
        """Return the package id of an apt.package.Version instance."""
        if version.origins:
            origin = version.origins[0].label
        else:
            origin = ""
        if version.architecture == (apt_pkg.config.find("APT::Architecture") or
                                    version.architecture == "all"):
            name = version.package.name
        else:
            name = version.package.name.split(":")[0]
        id = "%s;%s;%s;%s" % (name, version.version,
                              version.architecture, origin)
        return id

    def _emit_package(self, trans, pkg, info=None, force_candidate=False):
        """
        Send the Package signal for a given apt package
        """
        if (not pkg.is_installed or force_candidate) and pkg.candidate:
            self._emit_pkg_version(trans, pkg.candidate, info)
        elif pkg.is_installed:
            self._emit_pkg_version(trans, pkg.installed, info)
        else:
            pklog.debug("Package %s hasn't got any version." % pkg.name)

    def _emit_pkg_version(self, trans, version, info=None):
        """Emit the Package signal of the given apt.package.Version."""
        id = self._get_id_from_version(version)
        section = version.section.split("/")[-1]
        if not info:
            if version == version.package.installed:
                if section == "metapackages":
                    info = pk_enums.INFO_COLLECTION_INSTALLED
                else:
                    info = pk_enums.INFO_INSTALLED
            else:
                if section == "metapackages":
                    info = pk_enums.INFO_COLLECTION_AVAILABLE
                else:
                    info = pk_enums.INFO_AVAILABLE
        trans.emit_package(info, id, version.summary)

    def _emit_all_visible_pkg_versions(self, trans, filters, pkg):
        """Emit all available versions of a package."""
        if self._is_package_visible(pkg, filters):
            if pk_enums.FILTER_NEWEST in filters:
                if pkg.candidate:
                    self._emit_pkg_version(trans, pkg.candidate)
                elif pkg.installed:
                    self._emit_pkg_version(trans, pkg.installed)
            else:
                for version in pkg.versions:
                    self._emit_pkg_version(trans, version)

    def _emit_visible_package(self, trans, filters, pkg, info=None):
        """
        Filter and emit a package
        """
        if self._is_package_visible(pkg, filters):
            self._emit_package(trans, pkg, info)

    def _emit_visible_packages(self, trans, filters, pkgs, info=None):
        """
        Filter and emit packages
        """
        for pkg in pkgs:
            if self._is_package_visible(pkg, filters):
                self._emit_package(trans, pkg, info)

    def _emit_visible_packages_by_name(self, trans, filters, pkgs, info=None):
        """
        Find the packages with the given namens. Afterwards filter and emit
        them
        """
        for name_raw in pkgs:
            #FIXME: Python-apt doesn't allow unicode as key. See #542965
            name = str(name_raw)
            if (name in self._cache and
                    self._is_package_visible(self._cache[name], filters)):
                self._emit_package(trans, self._cache[name], info)

    def _is_package_visible(self, pkg, filters):
        """
        Return True if the package should be shown in the user interface
        """
        if filters == [pk_enums.FILTER_NONE]:
            return True
        for filter in filters:
            if ((filter == pk_enums.FILTER_INSTALLED and
                 not pkg.is_installed) or
                (filter == pk_enums.FILTER_NOT_INSTALLED and
                 pkg.is_installed) or
                (filter == pk_enums.FILTER_SUPPORTED and
                 not self._is_package_supported(pkg)) or
                (filter == pk_enums.FILTER_NOT_SUPPORTED and
                 self._is_package_supported(pkg)) or
                (filter == pk_enums.FILTER_FREE and
                 not self._is_package_free(pkg)) or
                (filter == pk_enums.FILTER_NOT_FREE and
                 not self._is_package_not_free(pkg)) or
                (filter == pk_enums.FILTER_GUI and
                 not self._has_package_gui(pkg)) or
                (filter == pk_enums.FILTER_NOT_GUI and
                 self._has_package_gui(pkg)) or
                (filter == pk_enums.FILTER_COLLECTIONS and
                 not self._is_package_collection(pkg)) or
                (filter == pk_enums.FILTER_NOT_COLLECTIONS and
                 self._is_package_collection(pkg)) or
                (filter == pk_enums.FILTER_DEVELOPMENT and
                 not self._is_package_devel(pkg)) or
                (filter == pk_enums.FILTER_NOT_DEVELOPMENT and
                 self._is_package_devel(pkg))):
                return False
        return True

    def _is_package_not_free(self, pkg):
        """Return True if we can be sure that the package's license isn't any
        free one
        """
        if not pkg.candidate:
            return False
        origins = pkg.candidate.origins
        return (origins and
                ((origins[0].origin == "Ubuntu" and
                  origins[0].component in ["multiverse", "restricted"]) or
                 (origins[0].origin == "Debian" and
                  origins[0].component in ["contrib", "non-free"])) and
                origins[0].trusted)

    def _is_package_collection(self, pkg):
        """Return True if the package is a metapackge
        """
        section = pkg.section.split("/")[-1]
        return section == "metapackages"

    def _is_package_free(self, pkg):
        """Return True if we can be sure that the package has got a free
        license
        """
        if not pkg.candidate:
            return False
        origins = pkg.candidate.origins
        return (origins and
                ((origins[0].origin == "Ubuntu" and
                  origins[0].component in ["main", "universe"]) or
                 (origins[0].origin == "Debian" and
                  origins[0].component == "main")) and
                origins[0].trusted)

    def _has_package_gui(self, pkg):
        #FIXME: should go to a modified Package class
        #FIXME: take application data into account. perhaps checking for
        #       property in the xapian database
        return pkg.section.split('/')[-1].lower() in ['x11', 'gnome', 'kde']

    def _is_package_devel(self, pkg):
        #FIXME: should go to a modified Package class
        return (pkg.name.endswith("-dev") or pkg.name.endswith("-dbg") or
                pkg.section.split('/')[-1].lower() in ['devel', 'libdevel'])

    def _is_package_supported(self, pkg):
        if not pkg.candidate:
            return False
        origins = pkg.candidate.origins
        return (origins and
                ((origins[0].origin == "Ubuntu" and
                  origins[0].component in ["main", "restricted"]) or
                 (origins[0].origin == "Debian" and
                  origins[0].component == "main")) and
                origins[0].trusted)

    def _get_package_by_id(self, id):
        """Return the apt.package.Package corresponding to the given
        package id.

        If the package isn't available error out.
        """
        version = self._get_version_by_id(id)
        return version.package

    def _get_version_by_id(self, id):
        """Return the apt.package.Version corresponding to the given
        package id.

        If the version isn't available error out.
        """
        name, version_string, arch, data = id.split(";", 4)
        if (arch and arch != apt_pkg.config.find("APT::Architecture") and
                arch != "all"):
            name += ":%s" % arch
        try:
            pkg = self._cache[name]
        except KeyError:
            raise TransactionFailed(aptd_enums.ERROR_NO_PACKAGE,
                                    "There isn't any package named %s",
                                    name)
        #FIXME:This requires a not yet released fix in python-apt
        try:
            version = pkg.versions[version_string]
        except:
            raise TransactionFailed(aptd_enums.ERROR_NO_PACKAGE,
                                    "Verion %s doesn't exist",
                                    version_string)
        if version.architecture != arch:
            raise TransactionFailed(aptd_enums.ERROR_NO_PACKAGE,
                                    "Version %s of %s isn't available "
                                    "for architecture %s",
                                    pkg.name, version.version, arch)
        return version

    def _get_installed_files(self, pkg):
        """
        Return the list of unicode names of the files which have
        been installed by the package

        This method should be obsolete by the
        apt.package.Package.installedFiles attribute as soon as the
        consolidate branch of python-apt gets merged
        """
        path = os.path.join(apt_pkg.config["Dir"],
                            "var/lib/dpkg/info/%s.list" % pkg.name)
        try:
            with open(path, 'rb') as f:
                files = f.read().decode('UTF-8').split("\n")
        except IOError:
            return []
        return files

    def _get_package_group(self, pkg):
        """
        Return the packagekit group corresponding to the package's section
        """
        section = pkg.section.split("/")[-1]
        if section in SECTION_GROUP_MAP:
            return SECTION_GROUP_MAP[section]
        else:
            pklog.debug("Unkown package section %s of %s" % (pkg.section,
                                                             pkg.name))
            return pk_enums.GROUP_UNKNOWN

    def _init_plugins(self):
        """Initialize PackageKit apt backend plugins.
        Do nothing if plugins are already initialized.
        """
        if self._plugins is not None:
            return

        if not pkg_resources:
            return

        self._plugins = {}  # plugin_name -> [plugin_fn1, ...]

        # just look in standard Python paths for now
        dists, errors = pkg_resources.working_set.find_plugins(
            pkg_resources.Environment())
        for dist in dists:
            pkg_resources.working_set.add(dist)
        for plugin_name in ["what_provides"]:
            for entry_point in pkg_resources.iter_entry_points(
                    "packagekit.apt.plugins", plugin_name):
                try:
                    plugin = entry_point.load()
                except Exception as e:
                    pklog.warning("Failed to load %s from plugin %s: %s" % (
                        plugin_name, str(entry_point.dist), str(e)))
                    continue
                pklog.debug("Loaded %s from plugin %s" % (
                    plugin_name, str(entry_point.dist)))
                self._plugins.setdefault(plugin_name, []).append(plugin)

    def _apply_changes(self, trans, fetch_range=(15, 50),
                       install_range=(50, 90)):
        """Apply changes and emit RequireRestart accordingly."""
        worker.AptWorker._apply_changes(self, trans,
                                        fetch_range,
                                        install_range)
        if (hasattr(trans, "pktrans") and
            (trans.role == aptd_enums.ROLE_UPGRADE_SYSTEM or
             trans.packages[aptd_enums.PKGS_UPGRADE] or
             trans.depends[aptd_enums.PKGS_UPGRADE])):
            self._emit_require_restart(trans)


if META_RELEASE_SUPPORT:

    class GMetaRelease(GObject.GObject, MetaReleaseCore):

        __gsignals__ = {"download-done": (GObject.SignalFlags.RUN_FIRST,
                                          None,
                                          ())}

        def __init__(self):
            GObject.GObject.__init__(self)
            MetaReleaseCore.__init__(self, False, False)

        def download(self):
            MetaReleaseCore.download(self)
            self.emit("download-done")


def get_pk_exit_enum(enum):
    try:
        return MAP_EXIT_ENUM[enum]
    except KeyError:
        return pk_enums.EXIT_UNKNOWN


def get_pk_status_enum(enum):
    try:
        return MAP_STATUS_ENUM[enum]
    except KeyError:
        return pk_enums.STATUS_UNKNOWN


def get_pk_package_enum(enum):
    try:
        return MAP_PACKAGE_ENUM[enum]
    except KeyError:
        return pk_enums.INFO_UNKNOWN


def get_pk_error_enum(enum):
    try:
        return MAP_ERROR_ENUM[enum]
    except KeyError:
        return pk_enums.ERROR_UNKNOWN


def get_aptd_package_id(pk_id):
    """Convert a PackageKit Package ID to the apt syntax.
    e.g. xterm;235;i386;installed to xterm:i386=235
    """
    name, version, arch, data = pk_id.split(";")
    id = name
    if arch != apt_pkg.config.find("APT::Architecture") and arch != "all":
        id += ":%s" % arch
    if version:
        id += "=%s" % version
    return id


def get_pk_package_id(pk_id, data=""):
    """Convert an AptDaemon package ID to the PackageKit syntax.
    e.g. xterm:i368=235; to xterm;235;i386;installed
    """
    #FIXME add arch support
    name, version, release = worker.AptWorker._split_package_id(pk_id)
    try:
        name, arch = name.split(":", 1)
    except ValueError:
        arch = ""
    if version is None:
        version = ""
    if release is None:
        release = ""
    return "%s;%s;%s;%s" % (name, version, arch, data or release)


def defer_idle(func, *args):
    func(*args)
    return False

# vim: ts=4 et sts=4
