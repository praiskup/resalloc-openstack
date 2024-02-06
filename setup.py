# Resalloc setup script.
# Copyright (C) 2019 Red Hat, Inc.
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

from setuptools import setup, find_packages

from build_manpages import build_manpages, get_build_py_cmd, get_install_cmd

project = "resalloc-openstack"

def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

long_description="""
Resource allocator spawner/terminator scripts for OpenStack
""".strip()

setup(
    name=project,
    version='9.7',
    description='Spawning/terminating scripts for openstack',
    long_description=long_description,
    author='Pavel Raiskup',
    author_email='praiskup@redhat.com',
    license='GPLv2+',
    url='https://github.com/praiskup/resalloc-openstack',
    platforms=['any'],
    packages=find_packages(),
    scripts=[
        'bin/resalloc-openstack-new',
        'bin/resalloc-openstack-delete',
        'bin/resalloc-openstack-cleanup-broken-images',
        'bin/resalloc-openstack-cleanup-orphaned-instances',
        'bin/resalloc-openstack-list',
    ],
    install_requires=get_requirements(),
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(),
        'install': get_install_cmd(),
    },
)
