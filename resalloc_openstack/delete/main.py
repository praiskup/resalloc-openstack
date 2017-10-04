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

from sys import exit
from .arg_parser import parser
from resalloc_openstack.helpers \
    import nova, cinder, neutron, get_log, Server, FloatingIP,\
           GarbageCollector, Volume
from time import sleep

log = get_log(__name__)


def cleanup(gc):
    args = parser.parse_args()

    server = Server(nova, args.name)

    if args.delete_everything:
        # Find the first floating ip address.
        addresses = []
        for key in server.nova_o.addresses:
            for a in server.nova_o.addresses[key]:
                if a['OS-EXT-IPS:type'] == 'floating':
                    addresses.append(a['addr'])

        for a in neutron.list_floatingips()['floatingips']:
            address = a['floating_ip_address']
            if address in addresses:
                gc.add('01_ip_' + address,
                       FloatingIP(client=neutron, ip=a))

        for volume in cinder.volumes.list():
            if not volume.attachments:
                continue

            # FIXME: do we need to check IDs != 0?
            if volume.attachments[0]['server_id'] != server.id:
                continue

            gc.add('05_volume_' + volume.id,
                   Volume(cinder, volume))

    gc.add('10_server', server)


def main():
    gc = GarbageCollector()
    try:
        cleanup(gc)
    finally:
        gc.do()
    return 0
