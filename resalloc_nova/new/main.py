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
from time import sleep

from .arg_parser import parser
from resalloc_nova.env_credentials import session
from novaclient import client as nova_client
from neutronclient.v2_0 import client as neutron_client
from resalloc_nova.helpers import FloatingIP, random_id, Server, get_log

log = get_log(__name__)

# Cleaned up in alphabetical order.
cleanup_items = {}

neutron = neutron_client.Client(session=session)
nova = nova_client.Client(2, session=session)

def cleanup():
    log.info("running cleanup")
    for key, obj in sorted(cleanup_items.items()):
        log.info("cleaning " + key)
        try:
            obj.delete()
        except Exception as e:
            log.exception("can't delete " + key)

def main():
    try:
        args = parser.parse_args()
        ip = None
        if args.floating_ip_network:
            ip = FloatingIP(neutron, args.floating_ip_network)
            cleanup_items['01_IP'] = ip
            print(ip)

        flavor = nova.flavors.find(id=args.flavor)
        key = nova.keypairs.find()

        vm_stub = nova.servers.create(
            args.name or random_id(),
            args.image,
            args.flavor,
            key_name=key.id,
        )

        cleanup_items['05_server'] = Server(nova, vm_stub.id)

        server = None
        while True:
            server = nova.servers.find(id=vm_stub.id)
            status = getattr(server, "status", "unknown")
            if status.lower() == "active":
                log.info("booted server " + server.id)
                break
            log.debug("status: " + str(status))
            sleep(3)

        # Server booted!  Assign the IP.
        if ip:
            server.add_floating_ip(ip.ip)

    except:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        cleanup()
        raise
