# Copyright (C) 2017 Red Hat, Inc.
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import signal
import string
import random
import logging
from time import sleep

from novaclient import client as nova_client
import novaclient.exceptions
from neutronclient.v2_0 import client as neutron_client
from cinderclient import client as cinder_client
import cinderclient.exceptions

from resalloc_openstack.env_credentials import session

find_id_broken = 'NOVA_BROKEN_SERVER_FIND_ID' in os.environ

neutron = neutron_client.Client(session=session)
nova = nova_client.Client(2, session=session)

try:
    cinder = cinder_client.Client(3, session=session)
except:  # pylint: disable=bare-except
    cinder = cinder_client.Client(2, session=session)

def get_log(name):
    level = logging.DEBUG
    logger = logging.getLogger(name)
    logger.setLevel(level)
    stderr = logging.StreamHandler()
    stderr.setLevel(level)
    logger.addHandler(stderr)
    return logger


log = get_log(__name__)

def random_id():
    return "resalloc_openstack_" \
        + ''.join(random.choice(string.ascii_uppercase + string.digits) \
            for _ in range(10))


class OSObject(object):
    max_delete_attempts = 5
    ignore_delete_errors = False
    attempt = 0

    def _handle_optional_arg(self, opt_arg, kwargs):
        opt_val = kwargs.pop(opt_arg, None)
        if opt_val is None:
            return
        setattr(self, opt_arg, opt_val)

    def __init__(self, *args, **kwargs):
        log.debug("initializing %s", self.__class__)
        self._handle_optional_arg("max_delete_attempts", kwargs)
        self._handle_optional_arg("ignore_delete_errors", kwargs)
        self.init(*args, **kwargs)

    def best_effort_delete(self):
        if self.attempt > self.max_delete_attempts:
            # what else we can do ...
            self.force_delete()
            return True

        self.attempt += 1
        try:
            self.delete()
            return True
        except Exception as e:
            log.exception(e)

        log.debug("failed to delete in #{0} attempt".format(self.attempt))
        return False

    def delete(self):
        """
        This method is called several times if any exception is raised.
        """
        raise NotImplementedError

    def force_delete(self):
        """
        This method is called only once, as a last resort.  All exceptions are
        ignored.
        """
        pass

    def init(self):
        raise NotImplementedError

class FloatingIP(OSObject):
    ip = ""
    id = ""
    client = None

    def init(self, client=None, network_id=None, ip=None):
        assert client
        assert network_id or ip

        self.client = client

        if ip:
            self.id = ip['id']
            self.ip = ip['floating_ip_address']

        else:
            body = {'floatingip': {'floating_network_id': network_id}}
            response = client.create_floatingip(body)

            self.ip = response['floatingip']['floating_ip_address']
            self.id = response['floatingip']['id']

    def __str__(self):
        return self.ip

    def delete(self):
        self.client.delete_floatingip(self.id)


class Server(OSObject):
    nova_o = None

    def init(self, client, id_or_name):
        self.client = client

        srvs = None
        try:
            srvs = client.servers.findall(name=id_or_name)
        except novaclient.exceptions.NotFound:
            pass

        if srvs:
            self.id = srvs[0].id
            self.nova_o = srvs[0]
        else:
            # "assert"
            self.nova_o = client.servers.find(id=id_or_name)
            self.id = id_or_name

    def delete(self):
        log.debug("deleting server " + self.id)

        try:
            self.client.servers.delete(self.id)
        except novaclient.exceptions.NotFound:
            return # deleted in the meantime, by previous attempt

        # Wait for the server shut-down before we attempt to delete volumes.
        for _ in range(5):
            sleep(5)

            key = 'name' if find_id_broken else 'id'
            value = self.nova_o.name if find_id_broken else self.id
            args = {key: value}

            all_servers = None
            try:
                all_servers = self.client.servers.findall(**args)
            # Older nova clients raised exception.
            except novaclient.exceptions.NotFound:
                pass

            if not all_servers:
                return

        raise Exception("delete request accepted, but errored")



class Volume(OSObject):
    def init(self, client, volume):
        self.id = volume.id
        self.info_str = "{} ({})".format(volume.name, volume.id)
        self.nova_o = volume
        self.client = client

    def delete(self):
        ignored_exceptions = (
            novaclient.exceptions.ClientException,
            cinderclient.exceptions.ClientException,
        )

        try:
            self.nova_o.detach()
        except ignored_exceptions:
            if not self.ignore_delete_errors:
                raise
            log.info("Failed to detach %s, ignored for now.",
                     self.info_str)

        try:
            self.client.volumes.delete(self.id)
        except novaclient.exceptions.NotFound:
            # has previous attempt-to-remove succeeded?
            log.debug("Volume %s not found", self.info_str)
        except ignored_exceptions:
            if not self.ignore_delete_errors:
                raise
            log.info("Failed remove %s, ignored for now.", self.info_str)


    def force_delete(self):
        try:
            self.nova_o.detach()
        except:
            log.debug("ignoring volume detach problems")

        try:
            self.client.volumes.delete(self.id)
        except:
            log.debug("ignoring volume delete problems")


class GarbageCollector(object):
    """
    Construct a sorted list of cleanup actions executed upon a request, or
    automatically upon a failure.
    """
    todo = {}

    def add(self, identifier, cleaner_obj):
        """
        Add a new cleanup action (CLEANER_OBJ), identified by IDENTIFIER.
        IDENTIFIER is only used to sort the cleaner objects correctly
        (alphabetically, by given identifiers - not in the order they are
        added).  So the IDENTIFIERs are mostly artificially picked strings to
        guarantee the correct order of cleanup actions.
        """
        self.todo[identifier] = cleaner_obj

    def do(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        if self.todo:
            log.debug("running cleanup")

        while self.todo:
            action_id = sorted(self.todo)[0]
            obj = self.todo[action_id]
            log.debug("cleaning " + action_id)
            if obj.best_effort_delete():
                self.todo.pop(action_id)
            else:
                # Give it some time to recover
                sleep(5)
