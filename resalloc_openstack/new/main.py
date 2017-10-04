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
from time import sleep

from .arg_parser import parser
from resalloc_openstack.env_credentials import session
from resalloc_openstack.helpers \
        import FloatingIP, random_id, Server, get_log, Volume, GarbageCollector
from resalloc_openstack.helpers import cinder, nova, neutron
from subprocess import check_call

log = get_log(__name__)

gc = GarbageCollector()
def main():
    args = parser.parse_args()
    server_name = args.name or random_id()

    try:
        ip = None
        if args.floating_ip_network:
            ip = FloatingIP(neutron, args.floating_ip_network)
            gc.add('01_IP', ip)

        number = 0
        volumes = []
        for v in args.volumes or []:
            number += 1
            volume_name = "{0}_{1}".format(server_name, number)
            volume = cinder.volumes.create(size=int(v), name=volume_name)
            volumes.append(volume)
            gc.add('05_' + volume_name, Volume(cinder, volume))

        flavor = nova.flavors.find(id=args.flavor)
        key = nova.keypairs.find()

        vm_stub = nova.servers.create(
            server_name,
            args.image,
            args.flavor,
            key_name=key.id,
        )

        gc.add('10_server', Server(nova, vm_stub.id))

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

        for volume in volumes:
            log.debug("attaching volume " + volume.id)
            cinder.volumes.attach(volume, server.id, '/dev/vda')

        if args.command:
            env = os.environ
            env['RESALLOC_OS_NAME'] = server_name
            env['RESALLOC_OS_IP'] = ip.ip
            check_call(args.command, env=env, shell=True)

    except:
        gc.do()
        raise

    return 0
