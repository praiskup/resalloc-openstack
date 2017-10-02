import string
import random
import logging


def get_log(name):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)


def random_id():
    return "resalloc_nova_" \
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
