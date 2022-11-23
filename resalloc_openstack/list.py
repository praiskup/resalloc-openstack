# Copyright (C) 2022 Red Hat, Inc.
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
import logging
import os
import re
import sys

from resalloc_openstack.helpers import nova, cinder

DESCRIPTION = """
List a set of OpenStack VMs given the --pool NAME (starting part of the VM
name), and print them on the standard output.

This command is typically called by the Resalloc server via `cmd_list`, and all
the VMs printed out but not known by the Resalloc server will be removed.
"""

def get_parser():
    """ Get the argparser object """
    parser = argparse.ArgumentParser(
        prog='resalloc-openstack-new',
        description=DESCRIPTION,
    )

    parser.add_argument(
        "--pool",
        default=os.getenv("RESALLOC_POOL_ID"),
        help="Choose the pool name, alternatively $RESALLOC_POOL_ID",
    )

    return parser

def main():
    """ entrypoint for resalloc-openstack-list """
    log = logging.getLogger(__name__)
    hdlr = logging.StreamHandler()
    log.addHandler(hdlr)
    log.setLevel(logging.INFO)
    args = get_parser().parse_args()

    if not args.pool:
        log.fatal("$RESALLOC_POOL_ID env var or --pool required")
        sys.exit(1)

    if args.pool.endswith("_"):
        log.fatal("Pool name should not end with underscore: %s", args.pool)
        sys.exit(1)

    servers = set()

    for server in nova.servers.list():
        if server.name.startswith(args.pool):
            servers.add(server.name)

    for volume in cinder.volumes.list():
        if volume.name.startswith(args.pool):
            # for pool
            # copr_vm_devel_psi_os
            # the volume name typically looks like
            # copr_vm_devel_psi_os_00291123_20220829_033127...
            suffix = volume.name
            suffix = suffix.split(args.pool + "_")[1]
            found = re.match("^([0-9]{8}_[0-9]{8}_[0-9]{6})", suffix)
            if found:
                servers.add(args.pool + "_" + found[0])

    for srv in servers:
        print(srv)
