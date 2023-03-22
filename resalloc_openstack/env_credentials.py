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


if 'OS_TENANT_ID' in os.environ:
    loader = loading.get_plugin_loader('password')
    # v2 config, since OS_TENANT_ID is not in v3 anymore
    auth = loader.load_from_options(
        auth_url=os.environ["OS_AUTH_URL"],
        username=os.environ["OS_USERNAME"],
        password=os.environ["OS_PASSWORD"],
        project_id=os.environ["OS_TENANT_ID"])
elif 'OS_PROJECT_NAME' in os.environ:
    # v3 config
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=os.environ["OS_AUTH_URL"],
        username=os.environ["OS_USERNAME"],
        password=os.environ["OS_PASSWORD"],
        user_domain_name=os.environ["OS_USER_DOMAIN_NAME"],
        project_domain_id=os.environ["OS_PROJECT_DOMAIN_ID"],
        project_name=os.environ["OS_PROJECT_NAME"])
elif 'OS_APPLICATION_CREDENTIAL_ID' in os.environ:
    loader = loading.get_plugin_loader('v3applicationcredential')
    auth = loader.load_from_options(
        auth_url=os.environ["OS_AUTH_URL"],
        application_credential_id=os.environ["OS_APPLICATION_CREDENTIAL_ID"],
        application_credential_secret=os.environ["OS_APPLICATION_CREDENTIAL_SECRET"],
    )
else:
    raise Exception("No credentials provided in environment")

session = session.Session(auth=auth)
