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

from .arg_parser import parser
from resalloc_openstack.helpers import nova, neutron, get_log

log = get_log(__name__)

def main():
    args = parser.parse_args()
    servers = nova.servers.findall(name=args.name)
    if not servers:
        servers = nova.servers.findall(id=args.name)

    if not servers:
        log.error("server " + args.name + " not found")
    server = servers[0]

    if args.delete_everything:
        # Find the first floating ip address.
        address = None
        for key in server.addresses:
            for a in server.addresses[key]:
                if a['OS-EXT-IPS:type'] == 'floating':
                    address = a['addr']

        for a in neutron.list_floatingips()['floatingips']:
            if a['floating_ip_address'] == address:
                neutron.delete_floatingip(a['id'])

    nova.servers.delete(server)
