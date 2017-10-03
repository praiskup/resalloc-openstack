import string
import random
import logging

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
    return logger


def random_id():
    return "resalloc_openstack_" \
        + ''.join(random.choice(string.ascii_uppercase + string.digits) \
            for _ in range(10))


class OSObject(object):
    def delete(self):
        raise NotImplementedError


class FloatingIP(OSObject):
    ip = ""
    id = ""
    client = None

    def __init__(self, client=None, network_id=None):
        assert client
        assert network_id

        self.client = client

        body = {'floatingip': {'floating_network_id': network_id}}
        response = client.create_floatingip(body)

        self.ip = response['floatingip']['floating_ip_address']
        self.id = response['floatingip']['id']

    def __str__(self):
        return self.ip


    def delete(self):
        self.client.delete_floatingip(self.id)


class Server(OSObject):
    def __init__(self, client, id):
        self.id = id
        self.client = client

    def delete(self):
        self.client.servers.delete(self.id)


class Volume(OSObject):
    def __init__(self, client, id):
        self.id = id
        self.client = client

    def delete(self):
        self.client.volumes.delete(self.id)
