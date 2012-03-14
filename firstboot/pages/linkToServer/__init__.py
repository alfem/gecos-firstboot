# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# This file is part of Guadalinex
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__ = "Antonio Hernández <ahernandez@emergya.com>"
__copyright__ = "Copyright (C) 2011, Junta de Andalucía <devmaster@guadalinex.org>"
__license__ = "GPL-2"


import os
from gi.repository import Gtk

import firstboot.pages
import LinkToServerConfEditorPage
from firstboot_lib import PageWindow
from firstboot import serverconf

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = True

__TITLE__ = _('Select authentication method')

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3

__LDAP__ = 'ldap'
__AD__ = 'ad'


def get_page(main_window):

    page = LinkToServerPage(main_window)
    return page


class LinkToServerPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerPage"

    def finish_initializing(self):

        self.show_status()

        self.json_cached = serverconf.json_is_cached()
        self.unlink_ldap = False
        self.unlink_ad = False

        self.ldap_is_configured = serverconf.ldap_is_configured()
        self.ad_is_configured = serverconf.ad_is_configured()
        is_configured = self.ldap_is_configured or self.ad_is_configured

        self.ui.boxOptionsSection.set_visible(not self.json_cached or is_configured)
        self.ui.boxUnlinkOptions.set_visible(is_configured)
        self.ui.boxLinkOptions.set_visible(not is_configured)
        self.ui.boxAuthSection.set_visible(not is_configured)
        self.main_window.btnNext.set_sensitive(True)

        self.ui.chkUnlinkLDAP.set_visible(self.ldap_is_configured)
        self.ui.chkUnlinkAD.set_visible(self.ad_is_configured)

        url_config = self.fbe.get_url()
        url = self.cmd_options.url

        if url == None or len(url) == 0:
            url = url_config

        if url == None or len(url) == 0:
            url = ''

        self.ui.txtUrl.set_text(url)

    def translate(self):
        desc = _('When a workstation is linked to an authentication server \
existing users in the server can login into this workstation.\n\n')

        if self.ldap_is_configured:
            desc1 = _('This workstation is currently linked to a LDAP \
server.')
        elif self.ad_is_configured:
            desc1 = _('This workstation is currently linked to an Active Directory \
server.')
        else:
            desc1 = _('You can type the options manually or download \
a default configuration from the server.')

        desc2 = _('Select the authentication method you would like to use:')

        self.ui.lblDescription.set_text(desc)
        self.ui.lblDescription1.set_text(desc1)
        self.ui.lblDescription2.set_text(desc2)
        self.ui.chkUnlinkLDAP.set_label(_('Unlink from LDAP'))
        self.ui.chkUnlinkLDAP.set_label(_('Unlink from LDAP'))
        self.ui.chkUnlinkAD.set_label(_('Unlink from Active Directory'))
        self.ui.radioOmit.set_label(_('Omit'))
        self.ui.radioManual.set_label(_('Manual'))
        self.ui.radioAuto.set_label(_('Automatic'))
        self.ui.radioLDAP.set_label(_('LDAP'))
        self.ui.radioAD.set_label(_('Active Directory'))

    def on_chkUnlinkLDAP_toggle(self, button):
        active = button.get_active()
        self.unlink_ldap = active
        self.main_window.btnNext.set_sensitive(active)

    def on_chkUnlinkAD_toggle(self, button):
        active = button.get_active()
        self.unlink_ad = active
        self.main_window.btnNext.set_sensitive(active)

    def on_radioOmit_toggled(self, button):
        self.ui.boxAutoOptionsDetails.set_visible(False)
        self.ui.boxAuthSection.set_visible(False)
        self.show_status()

    def on_radioManual_toggled(self, button):
        self.ui.boxAutoOptionsDetails.set_visible(False)
        self.ui.boxAuthSection.set_visible(True)
        self.show_status()

    def on_radioAutomatic_toggled(self, button):
        self.ui.boxAutoOptionsDetails.set_visible(True)
        self.ui.boxAuthSection.set_visible(True)
        self.show_status()

    def get_auth_method(self):
        if self.ui.radioLDAP.get_active():
            return __LDAP__

        elif self.ui.radioAD.get_active():
            return __AD__

    def show_status(self, status=None, exception=None):

        icon_size = Gtk.IconSize.BUTTON

        if status == None:
            self.ui.imgStatus.set_visible(False)
            self.ui.lblStatus.set_visible(False)

        elif status == __STATUS_TEST_PASSED__:
            self.ui.imgStatus.set_from_stock(Gtk.STOCK_APPLY, icon_size)
            self.ui.imgStatus.set_visible(True)
            self.ui.lblStatus.set_label(_('The configuration file is valid.'))
            self.ui.lblStatus.set_visible(True)

        elif status == __STATUS_CONFIG_CHANGED__:
            self.ui.imgStatus.set_from_stock(Gtk.STOCK_APPLY, icon_size)
            self.ui.imgStatus.set_visible(True)
            self.ui.lblStatus.set_label(_('The configuration was updated successfully.'))
            self.ui.lblStatus.set_visible(True)

        elif status == __STATUS_ERROR__:
            self.ui.imgStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR, icon_size)
            self.ui.imgStatus.set_visible(True)
            self.ui.lblStatus.set_label(str(exception))
            self.ui.lblStatus.set_visible(True)

        elif status == __STATUS_CONNECTING__:
            self.ui.imgStatus.set_from_stock(Gtk.STOCK_CONNECT, icon_size)
            self.ui.imgStatus.set_visible(True)
            self.ui.lblStatus.set_label(_('Trying to connect...'))
            self.ui.lblStatus.set_visible(True)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.pcLabel)

    def next_page(self, load_page_callback):
        if self.unlink_ldap == True or self.unlink_ad == True:
            server_conf = None
            result, messages = serverconf.setup_server(
                server_conf=server_conf,
                unlink_ldap=self.unlink_ldap,
                unlink_ad=self.unlink_ad
            )

            load_page_callback(LinkToServerResultsPage, {
                'result': result,
                'server_conf': server_conf,
                'messages': messages
            })
            return

        if self.ui.radioOmit.get_active() or (self.ldap_is_configured or self.ad_is_configured):
            self.emit('status-changed', 'linkToServer', True)
            load_page_callback(firstboot.pages.linkToChef)
            return

        self.show_status()

        try:
            server_conf = None
            if self.ui.radioAuto.get_active():
                url = self.ui.txtUrl.get_text()
                server_conf = serverconf.get_server_conf(url)

            load_page_callback(LinkToServerConfEditorPage, {
                'server_conf': server_conf,
                'ldap_is_configured': self.ldap_is_configured,
                'auth_method': self.get_auth_method(),
                'ad_is_configured': self.ad_is_configured,
            })

        except serverconf.ServerConfException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            self.show_status(__STATUS_ERROR__, e)
