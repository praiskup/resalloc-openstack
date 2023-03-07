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
from resalloc_openstack.helpers import cinder, nova, neutron, find_id_broken
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

        if args.key_pair_id:
            key = args.key_pair_id
        else:
            key = nova.keypairs.find()
            key = key.id

        nics = None
        if args.nics:
            nics = []
            for nic in args.nics:
                nic_dict = {}
                nic_args = nic.split(',')
                for arg in nic_args:
                    k, v = arg.split('=')
                    nic_dict[k] = v
                nics.append(nic_dict)

        try:
            image = nova.glance.find_image(args.image)
        except AttributeError:
            # older novaclient
            try:
                image = nova.images.get(args.image)
            except:
                image = nova.images.find(name=args.image)

        vm_stub = nova.servers.create(
            server_name,
            image.id,
            args.flavor,
            key_name=key,
            nics=nics,
            security_groups=args.security_groups or None,
        )

        if find_id_broken:
            gc.add('10_server', Server(nova, server_name))
        else:
            gc.add('10_server', Server(nova, vm_stub.id))

        server = None
        while True:
            if find_id_broken:
                server = nova.servers.find(name=server_name)
            else:
                server = nova.servers.find(id=vm_stub.id)
            status = getattr(server, "status", "unknown")
            if status.lower() == "active":
                log.info("booted server " + server.id)
                break

            if status.lower() == "error":
                raise Exception("server errored while being booted")

            log.debug("status: " + str(status))
            sleep(3)

        ipaddr = None
        # Server booted!  Assign the IP.
        if ip:
            server.add_floating_ip(ip.ip)
            ipaddr = ip.ip
        else:
            for net_id in server.addresses:
                for ip in server.addresses[net_id]:
                    ipaddr = ip['addr']
                    break
                if ipaddr:
                    break

        for volume in volumes:
            log.debug("attaching volume " + volume.id)
            nova.volumes.create_server_volume(server.id, volume.id)

        if args.command:
            env = os.environ
            env['RESALLOC_OS_NAME'] = server_name
            env['RESALLOC_OS_IP'] = ipaddr
            check_call(args.command, env=env, shell=True)

        if args.print_ip:
            print(ipaddr)

    except:
        gc.do()
        raise

    return 0
