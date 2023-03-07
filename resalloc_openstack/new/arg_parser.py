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

import argparse

description = """
Start a new VM in openstack, with some dependant resources (swap volumes or
floating IPs ATM).

The important thing is that the script aims to behave as atomically as possible,
in a sense that either everything is allocated as requested, or the script fails
(without any leftovers).
"""

parser = argparse.ArgumentParser(
    prog='resalloc-openstack-new',
    description=description,
)

parser.man_short_description \
        = "atomically allocate VM with additional resources in openstack"

parser.add_argument(
    "--name",
    help="Choose the name for the resulting VM")

parser.add_argument(
    "--image",
    required=True,
)

parser.add_argument(
    "--floating-ip-from",
    dest="floating_ip_network",
    help="allocate floating ip from network, check 'neutron net-list'",
)

parser.add_argument(
    "--flavor",
    required=True,
    help="openstack flavor, see 'nova flavor-list'",
)

parser.add_argument(
    "--alloc-volume",
    action='append',
    dest='volumes',
    help="allocate volumes by cinder",
)

parser.add_argument(
    "--post-command",
    dest='command',
    help=\
"""
run COMMAND after VM is started, and fail if the script fails too.  The
variables RESALLOC_OS_NAME and RESALLOC_OS_IP are exported into environment of
those scripts.
""".strip(),
)

parser.add_argument(
    "--print-ip",
    action="store_true",
    help="after successful allocation, print IP on standard output",
)

parser.add_argument(
    "--key-pair-id",
    help="use specific key, see ids (== names) in `nova keypair-list`",
)

parser.add_argument(
    "--nic",
    action='append',
    dest='nics',
    help="comma-separated, key=value,foo=baz arguments (see "
         "nova.servers.create(nics=...) help",
)

parser.add_argument(
    "--security-group",
    action="append",
    dest="security_groups",
    help="A security group name",
)
