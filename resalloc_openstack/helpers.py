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

import signal
import string
import random
import logging
from time import sleep

from novaclient import client as nova_client
from neutronclient.v2_0 import client as neutron_client
from cinderclient import client as cinder_client

from resalloc_openstack.env_credentials import session

neutron = neutron_client.Client(session=session)
nova = nova_client.Client(2, session=session)
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
    attempt = 0

    def best_effort_delete(self):
        if self.attempt > 5:
            # what else we can do ...
            return True

        self.attempt += 1
        try:
            self.delete()
            return True
        except Exception as e:
            log.exception(e)

        log.debug("failed to delte in #{0} attempt".format(self.attempt))
        return False

    def delete(self):
        raise NotImplementedError


class FloatingIP(OSObject):
    ip = ""
    id = ""
    client = None

    def __init__(self, client=None, network_id=None, ip=None):
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

    def __init__(self, client, id_or_name):
        self.client = client

        srvs = client.servers.findall(name=id_or_name)
        if srvs:
            self.id = srvs[0].id
            self.nova_o = srvs[0]
        else:
            # "assert"
            self.nova_o = client.servers.find(id=id_or_name)
            self.id = id_or_name

    def delete(self):
        log.debug("deleting server " + self.id)
        self.client.servers.delete(self.id)
        # Wait for the server shut-down before we attempt to delete volumes.
        while self.client.servers.findall(id=self.id):
            sleep(2)


class Volume(OSObject):
    def __init__(self, client, volume):
        self.id = volume.id
        self.nova_o = volume
        self.client = client

    def delete(self):
        # TODO:
        try:
            self.nova_o.detach()
        except:
            log.debug("can't detach volume " + self.id)

        self.client.volumes.delete(self.id)


class GarbageCollector(object):
    todo = {}
    def add(self, item, obj):
        self.todo[item] = obj

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
