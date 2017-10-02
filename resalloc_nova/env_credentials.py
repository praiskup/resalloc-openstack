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
from keystoneauth1 import loading, session

loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(
    auth_url=os.environ["OS_AUTH_URL"],
    username=os.environ["OS_USERNAME"],
    password=os.environ["OS_PASSWORD"],
    project_id=os.environ["OS_TENANT_ID"])

session = session.Session(auth=auth)
