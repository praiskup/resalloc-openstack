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
from resalloc_openstack.helpers import nova, neutron, get_log
from time import sleep

log = get_log(__name__)

def main():
    args = parser.parse_args()
    servers = nova.servers.findall(name=args.name)
    if not servers:
        servers = nova.servers.findall(id=args.name)

    if not servers:
        log.fatal("server " + args.name + " not found")
        exit(1)

    server = servers[0]
    postpone_volume_deletes = []

    if args.delete_everything:
        # Find the first floating ip address.
        address = None
        for key in server.addresses:
            for a in server.addresses[key]:
                if a['OS-EXT-IPS:type'] == 'floating':
                    address = a['addr']

        for a in neutron.list_floatingips()['floatingips']:
            if a['floating_ip_address'] == address:
                log.info("deleting ip " + address)
                neutron.delete_floatingip(a['id'])

        for volume in nova.volumes.get_server_volumes(server.id):
            log.info("deleting volume " + volume.id)
            postpone_volume_deletes.append(volume.id)

    log.debug("deleting server " + server.id)
    nova.servers.delete(server)
    while nova.servers.findall(id=server.id):
        sleep(3)

    for volume_id in postpone_volume_deletes:
        log.debug("deleting volume " + volume_id)
        cinder.volumes.delete(volume_id)
