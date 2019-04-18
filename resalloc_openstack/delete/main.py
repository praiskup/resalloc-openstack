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
import novaclient.exceptions
from time import sleep

log = get_log(__name__)

from keystoneauth1.exceptions import ConnectionError

def gather_tasks(gc):
    args = parser.parse_args()

    try:
        server = Server(nova, args.name)
    except novaclient.exceptions.NotFound:
        log.error('vm %s not found', args.name)
        return False


    if args.delete_everything:
        # Find the first floating ip address.
        addresses = []
        for key in server.nova_o.addresses:
            for a in server.nova_o.addresses[key]:
                if a['OS-EXT-IPS:type'] == 'floating':
                    addresses.append(a['addr'])


        floating_ips = []
        try:
            floating_ips = neutron.list_floatingips()['floatingips']
        except ConnectionError as err:
            log.warning("can not access floatingIP API" + str(err))

        for a in floating_ips:
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
    gathered = False
    for _ in range(0, 5):
        try:
            gc = GarbageCollector()
            gather_tasks(gc)
            gathered = True
            break
        except Exception as e:
            # we want to try to delete everything anyways
            log.exception(e)
            pass

    if not gathered:
        log.error("can't even gather info about the instance")
        return 1

    gc.do()
    return 0
