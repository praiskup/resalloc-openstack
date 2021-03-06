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
Terminate VM started by resalloc-nova-new including all resources
""".strip()

parser = argparse.ArgumentParser(
    prog='resalloc-openstack-delete',
    description=description,
)

parser.man_short_description \
        = "drop resources allocated by resalloc-openstack-new"

parser.add_argument(
    "name",
    help="Name of the VM to be terminated",
)

parser.add_argument(
    "--delete-everything",
    action='store_true',
    help="delete also attached floating IPs or cinder volumes",
)
