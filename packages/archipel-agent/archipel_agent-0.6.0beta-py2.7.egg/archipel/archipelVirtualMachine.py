# -*- coding: utf-8 -*-
#
# archipelVirtualMachine.py
#
# Copyright (C) 2010 Antoine Mercadal <antoine.mercadal@inframonde.eu>
# Copyright, 2011 - Franck Villaume <franck.villaume@trivialdev.com>
# This file is part of ArchipelProject
# http://archipelproject.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains ArchipelVirtualMachine, the XMPP capable controller

This module contains the class ArchipelVirtualMachine that represents a virtual machine
linked to a libvirt domain and allowing other XMPP entities to control it using IQ.

The ArchipelVirtualMachine is able to register to any kind of XMPP compliant Server. These
Server MUST allow in-band registration, or you have to manually register VM before
launching them.

Also the JID of the virtual machine MUST be the UUID use in the libvirt domain, or it will
fail.
"""

import libvirt
import os
import shutil
import thread
import xmpp
import tempfile
import base64
import time
from threading import Timer

from archipelcore.archipelAvatarControllableEntity import TNAvatarControllableEntity
from archipelcore.archipelEntity import TNArchipelEntity
from archipelcore.archipelHookableEntity import TNHookableEntity
from archipelcore.archipelRosterQueryableEntity import TNRosterQueryableEntity
from archipelcore.archipelTaggableEntity import TNTaggableEntity
from archipelcore.utils import build_error_iq, build_error_message

from archipelLibvirtEntity import ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR, generate_mac_adress
import archipelLibvirtEntity


ARCHIPEL_ERROR_CODE_VM_CREATE = -1001
ARCHIPEL_ERROR_CODE_VM_SUSPEND = -1002
ARCHIPEL_ERROR_CODE_VM_RESUME = -1003
ARCHIPEL_ERROR_CODE_VM_DESTROY = -1004
ARCHIPEL_ERROR_CODE_VM_SHUTDOWN = -1005
ARCHIPEL_ERROR_CODE_VM_REBOOT = -1006
ARCHIPEL_ERROR_CODE_VM_DEFINE = -1007
ARCHIPEL_ERROR_CODE_VM_UNDEFINE = -1008
ARCHIPEL_ERROR_CODE_VM_INFO = -1009
ARCHIPEL_ERROR_CODE_VM_XMLDESC = -1011
ARCHIPEL_ERROR_CODE_VM_LOCKED = -1012
ARCHIPEL_ERROR_CODE_VM_MIGRATE = -1013
ARCHIPEL_ERROR_CODE_VM_IS_MIGRATING = -1014
ARCHIPEL_ERROR_CODE_VM_AUTOSTART = -1015
ARCHIPEL_ERROR_CODE_VM_MEMORY = -1016
ARCHIPEL_ERROR_CODE_VM_NETWORKINFO = -1017
ARCHIPEL_ERROR_CODE_VM_HYPERVISOR_CAPABILITIES = -1019
ARCHIPEL_ERROR_CODE_VM_FREE = -1020
ARCHIPEL_ERROR_CODE_VM_SCREENSHOT = -1021
ARCHIPEL_ERROR_CODE_VM_HYPERVISOR_NODE_INFO = -1022
ARCHIPEL_ERROR_CODE_VM_MIGRATING = -43

ARCHIPEL_NS_VM_CONTROL = "archipel:vm:control"
ARCHIPEL_NS_VM_DEFINITION = "archipel:vm:definition"

# XMPP shows
ARCHIPEL_XMPP_SHOW_RUNNING = "Running"
ARCHIPEL_XMPP_SHOW_PAUSED = "Paused"
ARCHIPEL_XMPP_SHOW_SHUTDOWN = "Off"
ARCHIPEL_XMPP_SHOW_SHUTTINGDOWN = "Shutting down..."
ARCHIPEL_XMPP_SHOW_BLOCKED = "Blocked"
ARCHIPEL_XMPP_SHOW_SHUTOFF = "Shut off"
ARCHIPEL_XMPP_SHOW_ERROR = "Error"
ARCHIPEL_XMPP_SHOW_NOT_DEFINED = "Not defined"
ARCHIPEL_XMPP_SHOW_CRASHED = "Crashed"


class TNArchipelVirtualMachine (TNArchipelEntity, TNHookableEntity, TNAvatarControllableEntity, TNTaggableEntity, TNRosterQueryableEntity):
    """
    This class represents an Virtual Machine, XMPP Capable.
    This class needs to already have .... end of story ? TODO fix the details
    """

    def __init__(self, jid, password, hypervisor, configuration, name, organizationInfo):
        """
        Contructor of the class.
        """
        TNArchipelEntity.__init__(self, jid, password, configuration, name)

        self.hypervisor = hypervisor
        self.libvirt_status = libvirt.VIR_DOMAIN_SHUTDOWN
        self.domain = None
        self.definition = None
        self.uuid = self.jid.getNode()
        self.vm_disk_base_path = self.configuration.get("VIRTUALMACHINE", "vm_base_path")
        self.folder = "%s/%s" % (self.vm_disk_base_path, self.uuid)
        self.vm_perm_base_path = self.vm_disk_base_path
        self.lock_timer = None
        self.maximum_lock_time = self.configuration.getint("VIRTUALMACHINE", "maximum_lock_time")
        self.is_migrating = False
        self.libvirt_event_callback_id = -1
        self.entity_type = "virtualmachine"
        self.default_avatar = self.configuration.get("VIRTUALMACHINE", "vm_default_avatar")
        self.vm_will_define_hooks = []
        self.vcard_infos = {}
        self.is_freeing = False
        self.inhibit_domain_event = False
        self.cputime_samples=[]
        self.cputime_sampling_Interval = 2.0
        self.cputime_sampling_timer(self.cputime_sampling_Interval)

        if self.configuration.has_option("VIRTUALMACHINE", "vm_perm_path"):
            self.vm_perm_base_path = self.configuration.get("VIRTUALMACHINE", "vm_perm_path")
        self.permfolder = "%s/%s" % (self.vm_perm_base_path, self.uuid)

        self.set_organization_info(organizationInfo, publish=False)

        # create VM folders if not exists
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        if not os.path.isdir(self.permfolder):
            os.makedirs(self.permfolder)

        # start the permission center
        self.permission_db_file = "%s/%s" % (self.permfolder, self.configuration.get("VIRTUALMACHINE", "vm_permissions_database_path"))
        self.permission_center.start(database_file=self.permission_db_file)
        self.init_permissions()

        # hooks
        self.create_hook("HOOK_VM_CREATE")
        self.create_hook("HOOK_VM_SHUTOFF")
        self.create_hook("HOOK_VM_STOP")
        self.create_hook("HOOK_VM_DESTROY")
        self.create_hook("HOOK_VM_SUSPEND")
        self.create_hook("HOOK_VM_RESUME")
        self.create_hook("HOOK_VM_UNDEFINE")
        self.create_hook("HOOK_VM_DEFINE")
        self.create_hook("HOOK_VM_INITIALIZE")
        self.create_hook("HOOK_VM_TERMINATE")
        self.create_hook("HOOK_VM_FREE")
        self.create_hook("HOOK_VM_CRASH")
        self.create_hook("HOOK_XMPP_CONNECT")
        self.create_hook("HOOK_VM_MIGRATED")

        # actions on auth
        self.register_hook("HOOK_ARCHIPELENTITY_XMPP_AUTHENTICATED", method=self.connect_domain)
        self.register_hook("HOOK_ARCHIPELENTITY_XMPP_AUTHENTICATED", method=self.manage_vcard_hook)

        # vocabulary
        self.init_vocabulary()

        # modules
        self.initialize_modules('archipel.plugin.core')
        self.initialize_modules('archipel.plugin.virtualmachine')


    ### Overrides

    def set_custom_vcard_information(self, vCard):
        """
        Put custom information in vCard
        """
        vCard.append(xmpp.Node("TITLE", payload=self.vcard_infos["TITLE"]))
        vCard.append(xmpp.Node("ORGNAME", payload=self.vcard_infos["ORGNAME"]))
        vCard.append(xmpp.Node("ORGUNIT", payload=self.vcard_infos["ORGUNIT"]))
        vCard.append(xmpp.Node("LOCALITY", payload=self.vcard_infos["LOCALITY"]))
        vCard.append(xmpp.Node("USERID", payload=self.vcard_infos["USERID"]))
        vCard.append(xmpp.Node("CATEGORIES", payload=self.vcard_infos["CATEGORIES"]))


    def get_custom_vcard_information(self, vCard):
        """
        Read custom info from vCard
        """
        if vCard.getTag("TITLE"):
            self.vcard_infos["TITLE"] = vCard.getTag("TITLE").getData()
        if vCard.getTag("ORGNAME"):
            self.vcard_infos["ORGNAME"] = vCard.getTag("ORGNAME").getData()
        if vCard.getTag("ORGUNIT"):
            self.vcard_infos["ORGUNIT"] = vCard.getTag("ORGUNIT").getData()
        if vCard.getTag("LOCALITY"):
            self.vcard_infos["LOCALITY"] = vCard.getTag("LOCALITY").getData()
        if vCard.getTag("USERID"):
            self.vcard_infos["USERID"] = vCard.getTag("USERID").getData()
        if vCard.getTag("CATEGORIES"):
            self.vcard_infos["CATEGORIES"] = vCard.getTag("CATEGORIES").getData()


    ### Utilities

    def init_vocabulary(self):
        """
        This method registers for user messages.
        """
        TNArchipelEntity.init_vocabulary(self)
        registrar_items = [
                            {  "commands" : ["start", "create", "boot", "play", "run"],
                                "parameters": [],
                                "method": self.message_create,
                                "permissions": ["create"],
                                "description": "I'll start" },
                            {  "commands" : ["shutdown", "stop"],
                                "parameters": [],
                                "method": self.message_shutdown,
                                "permissions": ["shutdown"],
                                "description": "I'll shutdown" },
                            {  "commands" : ["destroy"],
                                "parameters": [],
                                "method": self.message_destroy,
                                "permissions": ["destroy"],
                                "description": "I'll destroy myself" },
                            {  "commands" : ["pause", "suspend"],
                                "parameters": [],
                                "method": self.message_suspend,
                                "permissions": ["suspend"],
                                "description": "I'll suspend" },
                            {  "commands" : ["resume", "unpause"],
                                "parameters": [],
                                "method": self.message_resume,
                                "permissions": ["resume"],
                                "description": "I'll resume" },
                            {  "commands" : ["info", "how are you", "and you"],
                                "parameters": [],
                                "method": self.message_info,
                                "permissions": ["info"],
                                "description": "I'll give info about me" },
                            {  "commands" : ["desc", "xml"],
                                "parameters": [],
                                "permissions": ["xmldesc"],
                                "method": self.message_xmldesc,
                                "description": "I'll show my description" },
                            {  "commands" : ["net", "stat"],
                                "parameters": [],
                                "method": self.message_networkinfo,
                                "permissions": ["networkinfo"],
                                "description": "I'll show my network stats" },
                            {  "commands" : ["fuck", "asshole", "jerk", "stupid", "suck"],
                                "ignore": True,
                                "parameters": [],
                                "method": self.message_insult,
                                "description": "" },
                            {  "commands" : ["hello", "hey", "hi", "good morning", "yo"],
                                "ignore": True,
                                "parameters": [],
                                "method": self.message_hello,
                                "description": "" }
                        ]
        self.add_message_registrar_items(registrar_items)

    def init_permissions(self):
        """
        Initialize the permissions.
        """
        TNArchipelEntity.init_permissions(self)
        self.permission_center.create_permission("info", "Authorizes users to access virtual machine information", False)
        self.permission_center.create_permission("create", "Authorizes users to create (start) virtual machine", False)
        self.permission_center.create_permission("shutdown", "Authorizes users to shut down virtual machine", False)
        self.permission_center.create_permission("destroy", "Authorizes users to destroy virtual machine", False)
        self.permission_center.create_permission("reboot", "Authorizes users to reboot virtual machine", False)
        self.permission_center.create_permission("suspend", "Authorizes users to suspend virtual machine ", False)
        self.permission_center.create_permission("resume", "Authorizes users to resume virtual machine", False)
        self.permission_center.create_permission("xmldesc", "Authorizes users to access the XML description of the virtual machine", False)
        self.permission_center.create_permission("migrate", "Authorizes users to perform live migration", False)
        self.permission_center.create_permission("autostart", "Authorizes users to set the virtual machine autostart", False)
        self.permission_center.create_permission("memory", "Authorizes users to change memory in live", False)
        self.permission_center.create_permission("setvcpus", "Authorizes users to set the number of virtual CPU in live", False)
        self.permission_center.create_permission("networkinfo", "Authorizes users to access virtual machine's network informations", False)
        self.permission_center.create_permission("define", "Authorizes users to define virtual machine", False)
        self.permission_center.create_permission("undefine", "Authorizes users to undefine virtual machine", False)
        self.permission_center.create_permission("capabilities", "Authorizes users to access virtual machine's hypervisor capabilities", False)
        self.permission_center.create_permission("nodeinfo", "Authorizes users to access virtual machine's hypervisor node informations", False)
        self.permission_center.create_permission("free", "Authorizes users completly destroy the virtual machine", False)

    def add_vm_definition_hook(self, method):
        """
        Add a new definition hook. Methods registered here will
        be executed (random order) in order to let modules a chance to
        edit the XML description. The method will get the root <domain/>
        XML node and *MUST* return it.
        @type method: function
        @param method: the method to run before defining the VM
        """
        if not method in self.vm_will_define_hooks:
            self.vm_will_define_hooks.append(method)

    def register_handlers(self):
        """
        This method registers the events handlers.
        It is invoked by super class xmpp_connect() method.
        """
        TNArchipelEntity.register_handlers(self)
        self.xmppclient.RegisterHandler('iq', self.__process_iq_archipel_control, ns=ARCHIPEL_NS_VM_CONTROL)
        self.xmppclient.RegisterHandler('iq', self.__process_iq_archipel_definition, ns=ARCHIPEL_NS_VM_DEFINITION)

    def unregister_handlers(self):
        """
        Unregister the handlers.
        """
        TNArchipelEntity.unregister_handlers(self)
        self.xmppclient.UnregisterHandler('iq', self.__process_iq_archipel_control, ns=ARCHIPEL_NS_VM_CONTROL)
        self.xmppclient.UnregisterHandler('iq', self.__process_iq_archipel_definition, ns=ARCHIPEL_NS_VM_DEFINITION)

    def remove_folder(self):
        """
        Remove the folder of the virtual with all its contents.
        """
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        if os.path.exists(self.permfolder):
            shutil.rmtree(self.permfolder)

    def rename_virtual_machine(self, newname, publish=True):
        """
        Rename the virtual machine with the given name.
        @type newname: String
        @param newname: the new name of the VM
        @type publish: Boolean
        @param publish: If True, the vCard with new name will be published right away
        """
        self.hypervisor.libvirt_contains_domain_with_name(newname, raise_error=True)

        self.log.info("renaming VM from %s to %s" % (self.name, newname))
        self.change_name(newname, publish)

        if self.domain:
            self.inhibit_domain_event = True
            old_definition = self.definition
            self.undefine()
            self.definition = old_definition
            if self.definition:
                self.definition.getTag("name").setData(newname)
            self.inhibit_domain_event = False

    def set_automatic_libvirt_description(self, xmldesc):
        """
        Set the XML description's description of the VM.
        """
        if not xmldesc.getTag('description'):
            xmldesc.addChild(name='description')
        else:
            xmldesc.delChild("description")
            xmldesc.addChild(name='description')
        xmldesc.getTag('description').setData("%s::::%s" % (self.jid.getStripped(), self.password))

        provided_name_tag = xmldesc.getTag('name')

        if not provided_name_tag:
            xmldesc.addChild(name='name')
        elif self.definition and not provided_name_tag.getData() == self.name:
            self.rename_virtual_machine(provided_name_tag.getData(), publish=True)

        xmldesc.getTag('name').setData(self.name.encode("ascii", "replace"))
        ret = str(xmldesc).replace('xmlns="http://www.gajim.org/xmlns/undeclared" ', '')

        self.log.debug("Generated XML desc is : %s" % ret)
        return ret

    def set_presence_according_to_libvirt_info(self):
        """
        Set XMPP status according to libvirt status.
        """
        try:
            dominfo = self.domain.info()
            self.libvirt_status = dominfo[0]
            self.log.info("Virtual machine state is %d" % dominfo[0])
            if dominfo[0] == libvirt.VIR_DOMAIN_RUNNING or dominfo[0] == libvirt.VIR_DOMAIN_BLOCKED:
                self.change_presence("", ARCHIPEL_XMPP_SHOW_RUNNING)
            elif dominfo[0] == libvirt.VIR_DOMAIN_PAUSED:
                self.change_presence("away", ARCHIPEL_XMPP_SHOW_PAUSED)
            elif dominfo[0] == libvirt.VIR_DOMAIN_SHUTOFF:
                self.change_presence("xa", ARCHIPEL_XMPP_SHOW_SHUTDOWN)
            elif dominfo[0] == libvirt.VIR_DOMAIN_SHUTDOWN:
                self.change_presence("", ARCHIPEL_XMPP_SHOW_SHUTTINGDOWN)
            self.perform_hooks("HOOK_VM_INITIALIZE")
        except libvirt.libvirtError as ex:
            if ex.get_error_code() == 42:
                self.log.info("Exception raised %s : %s" % (ex.get_error_code(), ex))
                self.domain = None
                self.change_presence("xa", ARCHIPEL_XMPP_SHOW_NOT_DEFINED)
            else:
                self.log.error("Exception raised %s : %s" % (ex.get_error_code(), ex))

    def connect_domain(self, origin=None, user_info=None, arguments=None):
        """
        Initialize the connection to the libvirt first, and
        then to the domain by looking the uuid used as JID Node.
        Exit on any error.
        """
        try:
            self.domain = self.hypervisor.libvirt_connection.lookupByUUIDString(self.uuid)
        except:
            self.log.warning("LIBVIRT: Can't connect to domain with UUID %s" % self.uuid)
            self.domain = None
            self.change_presence("xa", ARCHIPEL_XMPP_SHOW_NOT_DEFINED)
            self.perform_hooks("HOOK_VM_INITIALIZE")
            return

        try:
            self.definition = xmpp.simplexml.NodeBuilder(data=str(self.domain.XMLDesc(0))).getDom()
            self.log.info("LIBVIRT: Successfully connect to domain uuid %s" % self.uuid)
        except Exception as ex:
            self.log.error("LIBVIRT: Exception while connecting to domain : %s" % str(ex))

        self.set_presence_according_to_libvirt_info()

    def on_domain_event(self, event, detail):
        """
        Called when a libvirt event is triggered.
        @type conn: libvirt.connection
        @param conn: the libvirt connection
        @type event: int
        @param event: the event
        @type detail: int
        @param detail: the detail associated to the event
        """
        self.log.info("LIBVIRTEVENT: Libvirt event received: %d with detail %s" % (event, detail))

        if self.is_migrating:
            self.log.info("LIBVIRTEVENT: Event received but virtual machine is migrating. Ignoring.")
            return

        if self.inhibit_domain_event:
            self.log.info("LIBVIRTEVENT: VM has inihibited its event reaction. Ignoring")
            return

        try:
            if event == libvirt.VIR_DOMAIN_EVENT_STARTED  and not detail == libvirt.VIR_DOMAIN_EVENT_STARTED_MIGRATED:
                self.change_presence("", ARCHIPEL_XMPP_SHOW_RUNNING)
                self.push_change("virtualmachine:control", "created")
                self.perform_hooks("HOOK_VM_CREATE")
            elif event == libvirt.VIR_DOMAIN_EVENT_SUSPENDED and not detail == libvirt.VIR_DOMAIN_EVENT_SUSPENDED_MIGRATED:
                self.change_presence("away", ARCHIPEL_XMPP_SHOW_PAUSED)
                self.push_change("virtualmachine:control", "suspended")
                self.perform_hooks("HOOK_VM_SUSPEND")
            elif event == libvirt.VIR_DOMAIN_EVENT_RESUMED and not detail == libvirt.VIR_DOMAIN_EVENT_RESUMED_MIGRATED:
                self.change_presence("", ARCHIPEL_XMPP_SHOW_RUNNING)
                self.push_change("virtualmachine:control", "resumed")
                self.perform_hooks("HOOK_VM_RESUME")
            elif event == libvirt.VIR_DOMAIN_EVENT_STOPPED and not detail == libvirt.VIR_DOMAIN_EVENT_STOPPED_MIGRATED:
                self.change_presence("xa", ARCHIPEL_XMPP_SHOW_SHUTDOWN)
                self.push_change("virtualmachine:control", "shutdown")
                self.perform_hooks("HOOK_VM_STOP")
            elif event == libvirt.VIR_DOMAIN_CRASHED:
                self.change_presence("xa", ARCHIPEL_XMPP_SHOW_CRASHED)
                self.push_change("virtualmachine:control", "crashed")
                self.perform_hooks("HOOK_VM_CRASH")
            elif event == libvirt.VIR_DOMAIN_SHUTOFF:
                self.change_presence("", ARCHIPEL_XMPP_SHOW_SHUTOFF)
                self.push_change("virtualmachine:control", "shutoff")
                self.perform_hooks("HOOK_VM_SHUTOFF")
            elif event == libvirt.VIR_DOMAIN_EVENT_UNDEFINED:
                self.change_presence("xa", ARCHIPEL_XMPP_SHOW_NOT_DEFINED)
                self.push_change("virtualmachine:definition", "undefined")
                self.perform_hooks("HOOK_VM_UNDEFINE")
                self.domain = None
                self.definition = None
            elif event == libvirt.VIR_DOMAIN_EVENT_DEFINED:
                self.set_presence_according_to_libvirt_info()
                self.push_change("virtualmachine:definition", "defined")
                self.perform_hooks("HOOK_VM_DEFINE")
        except Exception as ex:
            self.log.error("%s: Unable to change state %d:%d : %s" % (self.jid.getStripped(), event, detail, str(ex)))
        finally:
            if not event == libvirt.VIR_DOMAIN_EVENT_UNDEFINED and not event == libvirt.VIR_DOMAIN_EVENT_DEFINED:
                try:
                    self.libvirt_status = self.info()["state"]
                except:
                    pass  # the VM has been freed.

    def add_jid_hook(self, origin=None, user_info=None, arguments=None):
        """
        Hook to add a JID.
        """
        self.add_jid(xmpp.JID(user_info.getStripped()))

    def define_hook(self, origin=None, user_info=None, arguments=None):
        """
        Hook for defining on hook
        """
        self.define(user_info)

    def control_create_hook(self, origin=None, user_info=None, arguments=None):
        """
        Hook for creating (starting) the vm
        """
        self.create()

    def _listen_migration_progress(self):
        """
        Will periodically update the VM XMPP status with the migration progress
        """
        try:
            jobInfo = self.domain.jobInfo()
            total = jobInfo[3]
            remaining = jobInfo[5]
            progress = 0

            if (total == 0):
               progress = 0
            else:
                if remaining == 0:
                    progress = 100;
                else:
                    progress = int(float(100) - float(remaining) * float(100.0) / float(total))
                    if progress >= 100:
                        progress = 99
            if progress > 0: # we save une presence :)
                self.change_presence(presence_show=self.xmppstatusshow, presence_status="Migrating - %d%%" % progress)

            if self.is_migrating:
                Timer(3, self._listen_migration_progress, []).start()
        except Exception as ex:
            pass


    ### Process IQ

    def __process_iq_archipel_control(self, conn, iq):
        """
        Invoked when new archipel:vm:control IQ is received.
        It understands IQ of type:
            - info
            - create
            - shutdown
            - destroy
            - reboot
            - suspend
            - resume
            - xmldesc
            - migrate
            - autostart
            - memory
            - networkinfo
        @type conn: xmpp.Dispatcher
        @param conn: ths instance of the current connection that send the message
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        """
        reply = None
        if self.is_freeing:
            raise xmpp.protocol.NodeProcessed
        action = self.check_acp(conn, iq)
        self.check_perm(conn, iq, action, -1)
        if not self.hypervisor.libvirt_connection:
            self.log.info("Control action required but no libvirt connection.")
            raise xmpp.protocol.NodeProcessed
        if self.is_migrating and (not action in ("info", "xmldesc", "networkinfo")):
            reply = build_error_iq(self, "Virtual machine is migrating. Can't perform this control operation.", iq, ARCHIPEL_ERROR_CODE_VM_MIGRATING)
            conn.send(reply)
            raise xmpp.protocol.NodeProcessed
        if action == "info":
            reply = self.iq_info(iq)
        elif action == "create":
            reply = self.iq_create(iq)
        elif action == "shutdown":
            reply = self.iq_shutdown(iq)
        elif action == "destroy":
            reply = self.iq_destroy(iq)
        elif action == "reboot":
            reply = self.iq_reboot(iq)
        elif action == "suspend":
            reply = self.iq_suspend(iq)
        elif action == "resume":
            reply = self.iq_resume(iq)
        elif action == "xmldesc":
            reply = self.iq_xmldesc(iq)
        elif action == "migrate":
            reply = self.iq_migrate(iq)
        elif action == "autostart":
            reply = self.iq_autostart(iq)
        elif action == "memory":
            reply = self.iq_memory(iq)
        elif action == "setvcpus":
            reply = self.iq_setvcpus(iq)
        elif action == "networkinfo":
            reply = self.iq_networkinfo(iq)
        elif action == "free":
            reply = self.iq_free(iq)
        elif action == "screenshot":
            reply = self.iq_screenshot(iq)
        # elif action == "setpincpus":
        #     reply = self.iq_setcpuspin(iq)
        if reply:
            conn.send(reply)
            raise xmpp.protocol.NodeProcessed

    def __process_iq_archipel_definition(self, conn, iq):
        """
        Invoked when new archipel:define IQ is received.
        It understands IQ of type:
            - define (the domain xml must be sent as payload of IQ, and the uuid *MUST*, be the same as the JID of the client)
            - undefine (undefine a virtual machine domain)
            - capabilities
        @type conn: xmpp.Dispatcher
        @param conn: ths instance of the current connection that send the message
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        """
        reply = None
        if self.is_freeing:
            raise xmpp.protocol.NodeProcessed
        action = self.check_acp(conn, iq)
        self.check_perm(conn, iq, action, -1)

        if self.is_migrating and (not action in ("capabilities")):
            reply = build_error_iq(self, "Virtual machine is migrating. Can't perform this control operation.", iq, ARCHIPEL_ERROR_CODE_VM_MIGRATING)
            conn.send(reply)
            raise xmpp.protocol.NodeProcessed

        if action == "define":
            reply = self.iq_define(iq)
        elif action == "undefine":
            reply = self.iq_undefine(iq)
        elif action == "capabilities":
            reply = self.iq_capabilities(iq)

        if reply:
            conn.send(reply)
            raise xmpp.protocol.NodeProcessed


    ### libvirt controls

    def create(self):
        """
        Create the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.create()
        self.log.info("Virtual machine created.")
        return str(self.domain.ID())

    def shutdown(self):
        """
        Shutdown the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.shutdown()
        if self.info()["state"] == libvirt.VIR_DOMAIN_RUNNING or self.info()["state"] == libvirt.VIR_DOMAIN_BLOCKED:
            self.change_presence(self.xmppstatusshow, ARCHIPEL_XMPP_SHOW_SHUTTINGDOWN)
        self.log.info("Virtual machine shut down.")

    def destroy(self):
        """
        Destroy the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.destroy()
        self.log.info("Virtual machine destroyed.")

    def reboot(self):
        """
        Reboot the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.reboot(0)  # flags not used in libvirt but required.
        self.log.info("Virtual machine rebooted.")

    def suspend(self):
        """
        Suspend (pause) the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.suspend()
        self.log.info("Virtual machine suspended.")

    def resume(self):
        """
        Resume (unpause) the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.resume()
        self.log.info("Virtual machine resumed.")

    def screenshot(self, thumbnail=True):
        """
        take a screenshot of the virtualmachine and
        return image as base64encoded PNG
        @type thumbnail: Boolean
        @param thumbnail: if True, will send a thumbnail of the screenshot
        @rtype: string
        @return: base64 encoded PNG data
        """
        if self.configuration.has_option("VIRTUALMACHINE", "disable_screenshot"):
            if self.configuration.getboolean("VIRTUALMACHINE", "disable_screenshot"):
                return (None, (0, 0))

        if not self.domain:
            raise Exception("You need to first define the virtual machine")

        state = self.domain.info()[0]
        if hasattr(self.domain, "screenshot") and (state == libvirt.VIR_DOMAIN_PAUSED or state == libvirt.VIR_DOMAIN_RUNNING):
            try:
                from PIL import Image
            except:
                self.log.error("Cannot take screenshot because cannot use python imaging library (PIL). You need to install python-imaging")
                return (None, (0, 0))

            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()

            # temporary solution. screenshot API is not
            # working yet with python libvirt
            ret = os.system("virsh screenshot %s %s" % (self.uuid, f.name))
            if not ret == 0:
                self.log.error("Cannot use virsh to take screenshot: return code is %d" % ret)
                return None
            # end of temp technic
            pixmap = Image.open(f.name)
            if thumbnail:
                pixmap.thumbnail((216, 162), Image.ANTIALIAS)
            size = pixmap.size
            pixmap.save("%s.%s" % (f.name, "png"))
            png = open("%s.png" % f.name)
            data = base64.b64encode(png.read())
            png.close()
            os.unlink(f.name)
            os.unlink("%s.png" % f.name)
            return (data, size)
        return (None, (0, 0))

    def cputime_sampling_timer(self, interval):
        """
        Create a threaded timer to take timestamp,cputime samples from actual domain
        """
        if self.domain and not self.is_freeing and not self.is_migrating:
            try:
                self.cputime_samples.insert(0, (time.time(), self.domain.info()[4]))
                if len(self.cputime_samples) > 2:
                    self.cputime_samples.pop()
            except Exception as ex:
                # @TODO: I'm sure there is a better way to do this.
                # First, this thing should be only running when the VM is running
                # instead of trying for nothing is the VM is not defined and running.
                self.log.warning("It seems the VM is gone, certainly due to migration. Stopping cpu usage collector.")
                return

        if not self.is_migrating: # for some reason this is not working...
            Timer(interval, self.cputime_sampling_timer, [interval]).start()

    def compute_cpu_usage(self):
        """
        Return the vm CPU usage in percent between two samples
        """
        try:
            prtCPU = 100 * (self.cputime_samples[0][1] - self.cputime_samples[1][1]) / ((self.cputime_samples[0][0] - self.cputime_samples[1][0]) * self.hypervisor.get_nodeinfo()['nrCoreperSocket'] * 1000000000)
        except:
            prtCPU = 0

        if prtCPU > 0:
            return prtCPU
        else:
            return 0

    def info(self):
        """
        Return info of a domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")

        dominfo = self.domain.info()

        if (self.definition.getAttr("type") == "xen") and (self.definition.getTag("os").getTag("type").getData() == "hvm"):
            delta_memory = 4096
        else:
            delta_memory = 0

        try:
            autostart = self.domain.autostart()
        except:
            autostart = 0

        return {
            "state": dominfo[0],
            "maxMem": dominfo[1] - delta_memory,
            "memory": dominfo[2] - delta_memory,
            "nrVirtCpu": dominfo[3],
            "cpuPrct": self.compute_cpu_usage(),
            "hypervisor": self.hypervisor.jid,
            "autostart": str(autostart)}

    def network_info(self):
        """
        Get network statistics on the domain.
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        if not self.domain.info()[0] == libvirt.VIR_DOMAIN_RUNNING and not self.domain.info()[0] == libvirt.VIR_DOMAIN_BLOCKED:
            raise Exception('Virtual machine must be running.')

        desc = xmpp.simplexml.NodeBuilder(data=self.domain.XMLDesc(0)).getDom()
        interfaces_nodes = desc.getTag("devices").getTags("interface")
        netstats = []
        for nic in interfaces_nodes:
            target = nic.getTag("target").getAttr("dev")
            try:
                name = nic.getTag("alias").getAttr("name")
            except:
                name = target
            stats = self.domain.interfaceStats(target)
            netstats.append({
                "name": name,
                "rx_bytes": stats[0],
                "rx_packets": stats[1],
                "rx_errs": stats[2],
                "rx_drop": stats[3],
                "tx_bytes": stats[4],
                "tx_packets": stats[5],
                "tx_errs": stats[6],
                "tx_drop": stats[7]
            })
        return netstats

    def setMemory(self, value):
        """
        Set memory value for running domain.
        @type value: int
        @param value: the new amount of memory
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        value = long(value)
        if value < 10:
            value = 10
        self.domain.setMemory(value)
        t = Timer(1.0, self.memoryTimer, kwargs={"requestedMemory": value})
        t.start()

    def memoryTimer(self, requestedMemory, retry=3):
        """
        Timer called by setMemory() to check if action has been done.
        @type requestedMemory: int
        @param requestedMemory: the requested memory amount to check
        @type retry: int
        @param retry: number of retry before considering the action has failed
        """
        if requestedMemory / self.info()["memory"] in (0, 1):
            self.push_change("virtualmachine:control", "memory")
        elif retry > 0:
            t = Timer(1.0, self.memoryTimer, kwargs={"requestedMemory": requestedMemory, "retry": (retry - 1)})
            t.start()
        else:
            self.push_change("virtualmachine:control", "memory")

    def setVCPUs(self, value):
        """
        Set the number of CPU for the domain.
        @type value: int
        @param value: number of CPU to use
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        if value > self.domain.maxVcpus():
            raise Exception("Maximum vCPU is %d" % self.domain.maxVcpus())
        self.domain.setVcpus(int(value))

    # def setCPUsPin(self, vcpu, cpumap):
    #     self.domain.pinVcpu(int(value)) # no no non

    def setAutostart(self, flag):
        """
        Set autostart for the domain.
        @type flag: int
        @param flag: the value of autostart (1 or 0)
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        self.domain.setAutostart(flag)

    def xmldesc(self, mask_description=True):
        """
        Get the XML description of the domain.
        @rtype: xmpp.Node
        @return: the XML description
        """
        if not self.domain:
            raise Exception("You need to first define the virtual machine")
        xmldesc = self.domain.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        descnode = xmpp.simplexml.NodeBuilder(data=xmldesc).getDom()
        if mask_description and descnode.getTag("description"):
            descnode.delChild("description")
        return descnode

    def define(self, xmldesc, sender=None):
        """
        Define the domain from given XML description.
        @type xmldesc: xmpp.Node
        @param xmldesc: the XML description
        @rtype: xmpp.Node
        @return: the XML description
        """

        # Call Definition hooks to update XML if needed from modules
        for m in self.vm_will_define_hooks:
            xmldesc = m(sender, xmldesc)

        if self.configuration.has_option("VIRTUALMACHINE", "enable_block_device_access"):
            if not self.configuration.getboolean("VIRTUALMACHINE", "enable_block_device_access"):
                if xmldesc.getTag("devices"):
                    for disk in xmldesc.getTag("devices").getTags("disk"):
                        if disk.getAttr("type") == "block":
                            raise Exception("The agent policy doesn't allow to use block devices.")

        # if there is any error, catch it and strip down the <description> tag to avoid
        # sending back the password to build_error_iq, then forward the exception
        try:
            self.hypervisor.libvirt_connection.defineXML(self.set_automatic_libvirt_description(xmldesc))
        except Exception as ex:
            if xmldesc.getTag('description'):
                xmldesc.delChild("description")
            raise ex

        self.definition = xmldesc

        if not self.domain:
            self.connect_domain()
            # in that case no event handler will be triggered as we are
            # not connected to the domain, so force push and hook
            self.perform_hooks("HOOK_VM_DEFINE")
            self.push_change("virtualmachine:definition", "defined")

        return xmldesc

    def undefine(self):
        """
        Undefine the domain.
        """
        if not self.domain:
            self.log.warning("Virtual machine is already undefined.")
            return
        self.domain.undefine()
        self.domain = None
        self.log.info("Virtual machine undefined.")

    def undefine_and_disconnect(self):
        """
        Undefine the domain and disconnect from XMPP.
        """
        self.undefine()
        self.disconnect()
        self.log.info("Virtual machine undefined and disconnected.")

    def clone(self, origin, user_info, parameters):
        """
        Clone a vm from another
        user_info is a dict that contains following keys:
            - definition : the xml object containing the libvirt definition
            - path : the vm path to clone (will clone * in it)
            - parentvm : the origin virtual machine object
        @type origin: TNArchipelEntity
        @param origin: the origin of the hook
        @type user_info: object
        @param user_info: random user info
        @type parameters: object
        @param parameters: runtime arguments
        """
        xml = user_info["definition"]
        path = user_info["path"]
        parentvm = user_info["parentvm"]
        parentuuid = parentvm.uuid
        parentname = parentvm.name
        xmlstring = str(xml)
        xmlstring = xmlstring.replace(parentuuid, self.uuid)
        newxml = xmpp.simplexml.NodeBuilder(data=xmlstring).getDom()

        name_node = newxml.getTag("name")
        name_node.setData(self.name)

        nics_nodes = newxml.getTag("devices").getTags("interface")
        for nic in nics_nodes:
            mac = nic.getTag("mac")
            if mac:
                mac.setAttr("address", generate_mac_adress())

        self.log.debug("New XML description is now %s" % str(newxml))
        self.log.info("Starting to clone virtual machine %s from %s" % (self.uuid, parentuuid))
        self.change_presence(presence_show="dnd", presence_status="Cloning from %s" % parentname)
        parentvm.change_presence(presence_show="dnd", presence_status="Cloning to %s" % self.name)
        self.log.info("Starting threaded copy of base virtual repository from %s to %s" % (path, self.folder))
        thread.start_new_thread(self.perform_threaded_cloning, (path, newxml, parentvm))

    def migrate(self, destination_jid):
        """
        Migrate a virtual machine from this host to another.
        This step check is virtual machine can be migrated.
        Then ask for the destination_jid hypervisor what is his
        libvirt uri.
        """
        ### Sanity checks
        if not self.hypervisor.is_hypervisor((archipelLibvirtEntity.ARCHIPEL_HYPERVISOR_TYPE_QEMU)):
            raise Exception('Archipel only supports Live migration for QEMU/KVM domains at the moment.')
        if self.is_migrating:
            raise Exception('Virtual machine is already migrating.')
        if not self.definition:
            raise Exception('Virtual machine must be defined.')
        if self.domain.info()[0] == libvirt.VIR_DOMAIN_BLOCKED:
            raise Exception('Virtual machine is blocked.')
        if self.hypervisor.jid.getStripped() == destination_jid.getStripped():
            raise Exception('Virtual machine is already running on %s' % destination_jid.getStripped())

        if self.domain.info()[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            self.migrate_not_running_step1(destination_jid)
        else:
            self.migrate_running_step1(destination_jid)
        self._listen_migration_progress()

    def migrate_running_step1(self, destination_jid):
        """
        This step asks for the destination_jid hypervisor what is his
        libvirt uri.
        """

        self.is_migrating = True
        migration_destination_jid = destination_jid

        iq = xmpp.Iq(typ="get", queryNS="archipel:hypervisor:control", to=migration_destination_jid)
        iq.getTag("query").addChild(name="archipel", attrs={"action": "migrationinfo"})
        xmpp.dispatcher.ID += 1
        iq.setID("%s-%d" % (self.jid.getNode(), xmpp.dispatcher.ID))
        self.xmppclient.SendAndCallForResponse(iq, self.migrate_running_step2)

    def migrate_running_step2(self, conn, resp):
        """
        Once received the remote hypervisor URI, start libvirt migration in a thread.
        """
        try:
            remote_hypervisor_uri = resp.getTag("query").getTag("migration").getAttr("libvirt_uri")
            shared_folder = "%s/%s" % (resp.getTag("query").getTag("migration").getAttr("base_folder"), self.uuid)

            self.log.info("MIGRATION: remote info: libvirt URI is %s" % remote_hypervisor_uri)
            self.log.info("MIGRATION: remote info: shared folder is %s" % shared_folder)

            if not os.path.exists(shared_folder):
                self.is_migrating = False
                self.change_presence(presence_show=self.xmppstatusshow, presence_status="Migration aborted")
                self.shout("migration", "I can't migrate because remote hypervisor has no folder %s" % shared_folder)
                self.log.error("MIGRATION: migration aborted because remote hypervisor has no folder %s" % shared_folder)
                return

        except Exception as ex:
            self.log.error("MIGRATION: unable to get remote libvirt URI: %s" % str(ex))
            self.is_migrating = False

        self.change_presence(presence_show=self.xmppstatusshow, presence_status="Migrating - 0%")
        thread.start_new_thread(self.migrate_running_step3, (remote_hypervisor_uri, ))

    def migrate_running_step3(self, remote_hypervisor_uri):
        """
        Perform the migration.
        """
        ## DO NOT UNDEFINE DOMAIN HERE. the hypervisor is in charge of this. If undefined here, can't free XMPP client
        try: # libvirt 0.9.10+
            flags = libvirt.VIR_MIGRATE_PEER2PEER | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_UNSAFE
        except:
            flags = libvirt.VIR_MIGRATE_PEER2PEER | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_LIVE
        try:
            self.log.info("MIGRATION: starting to migrate domain %s" % remote_hypervisor_uri)
            self.domain.migrateToURI(remote_hypervisor_uri, flags, None, 0)
            self.log.info("MIGRATION: migration to %s is a SUCCESS" % remote_hypervisor_uri)
            self.perform_hooks("HOOK_VM_MIGRATED")
        except Exception as ex:
            self.is_migrating = False
            self.change_presence(presence_show=self.xmppstatusshow, presence_status="Can't migrate.")
            self.shout("migration", "I can't migrate to %s because exception has been raised: %s" % (remote_hypervisor_uri, str(ex)))
            self.log.error("Can't migrate to %s because of : %s" % (remote_hypervisor_uri, str(ex)))

    def migrate_not_running_step1(self, destination_jid):
        """
        Migrate vm which is not running.
        """
        self.is_migrating = True
        iq = xmpp.Iq(typ="get", queryNS="archipel:hypervisor:control", to=destination_jid)
        iq.getTag("query").addChild(name="archipel", attrs={"action": "soft_alloc"})
        iq.getTag("query").getTag("archipel").addChild(node=self.xmldesc(mask_description=False))
        xmpp.dispatcher.ID += 1
        iq.setID("%s-%d" % (self.jid.getNode(), xmpp.dispatcher.ID))
        self.xmppclient.SendAndCallForResponse(iq, self.migrate_not_running_step2)

    def migrate_not_running_step2(self, conn, resp):
        """
        After vm thread has been started and vm has been defined remotely,
        free locally.
        """
        if resp.getType() == "error":
            self.is_migrating = False
            self.shout("migration", "Cannot define vm on remote hypervisor")
            self.log.error("MIGRATION: cannot define vm on remote hypervisor: reply : %s" % resp)
            return
        else:
            self.perform_hooks("HOOK_HYPERVISOR_MIGRATEDVM_LEAVE", self.uuid)
            self.log.info("MIGRATION: migration is a SUCCESS")
            self.hypervisor.soft_free(self.uuid)

    def free(self):
        """
        Will run the hypervisor to free virtual machine.
        """

        self.perform_hooks("HOOK_VM_FREE")
        self.unregister_handlers()
        self.is_freeing = True
        self.hypervisor.free(self.jid)

    def set_organization_info(self, organizationInfo, publish=True):
        """
        Set the vCard fields for the organization
        """
        if not organizationInfo:
            return;

        if "ORGNAME" in organizationInfo:
            self.vcard_infos["ORGNAME"] = organizationInfo["ORGNAME"]
        if "ORGUNIT" in organizationInfo:
            self.vcard_infos["ORGUNIT"] = organizationInfo["ORGUNIT"]
        if "USERID" in organizationInfo:
            self.vcard_infos["USERID"] = organizationInfo["USERID"]
        if "LOCALITY" in organizationInfo:
            self.vcard_infos["LOCALITY"] = organizationInfo["LOCALITY"]
        if "CATEGORIES" in organizationInfo:
            self.vcard_infos["CATEGORIES"] = organizationInfo["CATEGORIES"]

        self.vcard_infos["TITLE"] = "Virtual machine (%s)" % self.hypervisor.current_hypervisor()

        if publish:
            self.set_vcard()


    ### Other stuffs

    def perform_threaded_cloning(self, src_path, newxml, parentvm):
        """
        Perform threaded copy of the virtual machine and then define it.
        @type src_path: string
        @param src_path: the path of the folder of the origin VM
        @type newxml: xmpp.Node
        @param newxml: the origin XML description
        @type parentvm: TNArchipelVirtualMachine
        @param parentvm: the parent virtual machine object
        """
        for token in os.listdir(src_path):
            self.log.debug("CLONING: copying item %s/%s to %s" % (src_path, token, self.folder))
            shutil.copy("%s/%s" % (src_path, token), self.folder)
        self.define(newxml)
        parentvm.change_presence("xa", ARCHIPEL_XMPP_SHOW_SHUTDOWN)

    def terminate(self, clean_files=True):
        """
        This method is called by hypervisor when VM is freed.
        It will perform HOOK_VM_TERMINATE, close databases,
        close libvirt connection and remove own folder.
        @type clean_files: boolean
        @param clean_files: if True, remove the permission file and folder
        """
        self.perform_hooks("HOOK_VM_TERMINATE")
        self.permission_center.close_database()
        if clean_files:
            os.unlink(self.permission_db_file)
            self.remove_folder()


    ### XMPP Controls

    def iq_migrate(self, iq):
        """
        Handle the migration request.
        @type iq: xmpp.Protocol.Iq
        @param iq: the iq containing request information
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            hyp_jid = xmpp.JID(iq.getTag("query").getTag("archipel").getAttr("hypervisorjid"))
            self.migrate(hyp_jid)
            reply = iq.buildReply("result")
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_MIGRATE)
        return reply

    def iq_create(self, iq):
        """
        Create a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            domid = self.create()
            reply = iq.buildReply("result")
            payload = xmpp.Node("domain", attrs={"id": domid})
            reply.setQueryPayload([payload])
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_CREATE)
        return reply

    def message_create(self, msg):
        """
        Handle message creation order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.create()
            return "I'm starting."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_shutdown(self, iq):
        """
        Shutdown a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            self.shutdown()
            reply = iq.buildReply("result")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_SHUTDOWN)
        return reply

    def message_shutdown(self, msg):
        """
        Handle message shutdown order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.shutdown()
            return "I'm shutting down."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_destroy(self, iq):
        """
        Destroy a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            self.destroy()
            reply = iq.buildReply("result")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_DESTROY)
        return reply

    def message_destroy(self, msg):
        """
        Handle message destroy order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.destroy()
            return "I've destroyed myself."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_reboot(self, iq):
        """
        Reboot a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            self.reboot()
            reply = iq.buildReply("result")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code())
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_REBOOT)
        return reply

    def message_reboot(self, msg):
        """
        Handle message reboot order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.reboot()
            return "I try to reboot."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_suspend(self, iq):
        """
        Suspend (pause) a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            self.suspend()
            reply = iq.buildReply("result")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_SUSPEND)
        return reply

    def message_suspend(self, msg):
        """
        Handle message suspend order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.suspend()
            return "I'm suspended."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_resume(self, iq):
        """
        Resume (unpause) a domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            self.resume()
            reply = iq.buildReply("result")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_RESUME)
        return reply

    def message_resume(self, msg):
        """
        Handle message resume order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            self.resume()
            return "I'm resumed."
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_info(self, iq):
        """
        Return an IQ containing the info of the domain using libvirt connection.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            if not self.domain:
                return iq.buildReply("ignore")

            reply = iq.buildReply("result")
            infos = self.info()
            response = xmpp.Node(tag="info", attrs=infos)
            reply.setQueryPayload([response])
        except libvirt.libvirtError as ex:
            if ex.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return iq.buildReply("result")
            else:
                reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_INFO)
        return reply

    def message_info(self, msg):
        """
        Handle message info order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            i = self.info()
            states = ("no state", "running", "blocked", "paused", "shutdown", "shut off", "crashed")
            state = states[i["state"]]
            mem = int(i["memory"]) / 1024
            if i["nrVirtCpu"] < 2:
                cpuorth = "CPU"
            else:
                cpuorth = "CPUs"
            return "I'm in state %s, I use %d MB of memory. I've got %d %s and I'm consuming %d percent(s) of my allocated ressources on %s." % (state, mem, i["nrVirtCpu"], cpuorth, i["cpuPrct"], i["hypervisor"])
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_xmldesc(self, iq):
        """
        Get the XML Desc of the virtual machine.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        reply = iq.buildReply("result")
        try:
            if not self.domain:
                reply.setQueryPayload([xmpp.Node("not-defined")])
                return reply
            xmldescnode = self.xmldesc()
            reply.setQueryPayload([xmldescnode])
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_XMLDESC)
        return reply

    def message_xmldesc(self, msg):
        """
        Handle message xmldesc order.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        return str(self.xmldesc())


    # iq definition

    def iq_define(self, iq):
        """
        Define a virtual machine in the libvirt according to the XML data.
        domain passed in argument
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        reply = iq.buildReply("result")
        try:
            domain_node = iq.getTag("query").getTag("archipel").getTag("domain")
            domain_uuid = domain_node.getTag("uuid").getData()

            if domain_uuid != self.jid.getNode():
                raise Exception('IncorrectUUID', "Given UUID %s doesn't match JID %s" % (domain_uuid, self.jid.getNode()))

            self.define(domain_node, iq.getFrom())
            self.log.info("Virtual machine XML is defined.")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_DEFINE)
        return reply

    def iq_undefine(self, iq):
        """
        Undefine a virtual machine in the libvirt according to the XML data.
        domain passed in argument
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            self.undefine()
            self.log.info("Virtual machine is undefined.")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_DESTROY)
        return reply

    def iq_autostart(self, iq):
        """
        Set if machine should start with host.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            autostart = int(iq.getTag("query").getTag("archipel").getAttr("value"))
            self.setAutostart(autostart)
            self.log.info("Virtual autostart is set to %d" % autostart)
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_AUTOSTART)
        return reply

    def iq_memory(self, iq):
        """
        Balloon memory.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            memory = long(iq.getTag("query").getTag("archipel").getAttr("value"))
            self.setMemory(memory)
            self.log.info("Virtual machine memory is set to %d" % memory)
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_MEMORY)
        return reply

    def iq_setvcpus(self, iq):
        """
        Set number of virtual cpus.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            cpus = int(iq.getTag("query").getTag("archipel").getAttr("value"))
            self.setVCPUs(cpus)
            self.log.info("Virtual machine number of cpus is set to %d" % cpus)
            self.push_change("virtualmachine:control", "nvcpu")
            self.push_change("virtualmachine:definition", "nvcpu")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_MEMORY)
        return reply

    def iq_networkinfo(self, iq):
        """
        Return info about network.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            if not self.domain:
                return iq.buildReply("ignore")
            reply = iq.buildReply("result")
            infos = self.network_info()
            stats = []
            for info in infos:
                stats.append(xmpp.Node(tag="network", attrs=info))
            reply.setQueryPayload(stats)
        except libvirt.libvirtError as ex:
            if ex.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return iq.buildReply("result")
            else:
                reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_NETWORKINFO)
        return reply

    def message_networkinfo(self, msg):
        """
        Handle the message that asks for network information.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        try:
            s = self.network_info()
            resp = "My network infos are :\n"
            for i in s:
                resp = resp + "%s : rx_bytes:%s rx_packets:%s rx_errs:%d rx_drop:%s / tx_bytes:%s tx_packets:%s tx_errs:%d tx_drop:%s" % (i["name"], i["rx_bytes"], i["rx_packets"], i["rx_errs"], i["rx_drop"], i["tx_bytes"], i["tx_packets"], i["tx_errs"], i["tx_drop"])
            return resp
        except Exception as ex:
            return build_error_message(self, ex, msg)

    def iq_capabilities(self, iq):
        """
        Send the virtual machine's hypervisor capabilities.
        @type iq: xmpp.Protocol.Iq
        @param iq: the sender request IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready-to-send IQ containing the results
        """
        try:
            reply = iq.buildReply("result")
            reply.setQueryPayload([self.hypervisor.capabilities])
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_HYPERVISOR_CAPABILITIES)
        return reply

    def iq_nodeinfo(self, iq):
        """
        Send the virtual machine's hypervisor node informations.
        @type iq: xmpp.Protocol.Iq
        @param iq: the sender request IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready-to-send IQ containing the results
        """
        try:
            reply = iq.buildReply("result")
            reply.setQueryPayload([self.hypervisor.nodeinfo])
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_HYPERVISOR_NODE_INFO)
        return reply

    def message_insult(self, msg):
        """
        Handle insulting message.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        return "Please, don't be so rude with me. I try to do my best everyday for you."

    def message_hello(self, msg):
        """
        Handle the hello message.
        @type msg: xmpp.Protocol.Message
        @param msg: the received message
        @rtype: xmpp.Protocol.Message
        @return: a ready to send Message containing the result of the action
        """
        return "Hello %s! How are you today?" % msg.getFrom().getNode()

    def iq_setcpuspin(self, iq):
        """
        Set number of virtual cpus.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            cpus = int(iq.getTag("query").getTag("archipel").getAttr("value"))
            self.setVCPUs(cpus)
            self.log.info("Virtual machine number of cpus is set to %d" % cpus)
            self.push_change("virtualmachine:control", "nvcpu")
        except libvirt.libvirtError as ex:
            reply = build_error_iq(self, ex, iq, ex.get_error_code(), ns=ARCHIPEL_NS_LIBVIRT_GENERIC_ERROR)
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_MEMORY)
        return reply

    def iq_free(self, iq):
        """
        Free a virtual machine in the libvirt according to the XML data.
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            self.log.info("Virtual machine will be freed now")
            self.free()
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_FREE)
        return reply

    def iq_screenshot(self, iq):
        """
        Returns base64 encoded screenshot of the screen of the virtual machine
        @type iq: xmpp.Protocol.Iq
        @param iq: the received IQ
        @rtype: xmpp.Protocol.Iq
        @return: a ready to send IQ containing the result of the action
        """
        try:
            reply = iq.buildReply("result")
            self.log.info("Screenshot sent")
            if iq.getTag("query").getTag("archipel").getAttr("size") == "thumbnail":
                thumb = True
            else:
                thumb = False
            data, size = self.screenshot(thumb)
            if data:
                node = xmpp.Node("screenshot", attrs={"mime": "image/png", "width": size[0], "height": size[1]})
                node.setData(data)
                reply.setQueryPayload([node])
        except Exception as ex:
            reply = build_error_iq(self, ex, iq, ARCHIPEL_ERROR_CODE_VM_SCREENSHOT)
        return reply
