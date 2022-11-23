%global srcname resalloc-openstack
%global pkgname resalloc_openstack

%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_with python2
%global default_sitelib %python3_sitelib
%global python python3
%global pythonpfx python3
%else
%bcond_without python2
%global default_sitelib %python2_sitelib
%global python python2
%global pythonpfx python
%endif

Name:       %srcname
Summary:    Resource allocator scripts for OpenStack
Version:    @VERSION@
Release:    1%{?dist}
License:    GPLv2+
URL:        https://github.com/praiskup/resalloc-openstack
BuildArch:  noarch


BuildRequires: %pythonpfx-devel
BuildRequires: %pythonpfx-setuptools
BuildRequires: %python-argparse-manpage

Requires: %pythonpfx-cinderclient
Requires: %pythonpfx-glanceclient
Requires: %pythonpfx-keystoneauth1
Requires: %pythonpfx-neutronclient
Requires: %pythonpfx-novaclient

Source0: https://github.com/praiskup/%name/releases/download/v%version/%name-@TARBALL_VERSION@.tar.gz

%description
Resource allocator spawner/terminator scripts for OpenStack virtual machines,
designed so they either allocate all the sub-resources, or nothing (in case of
some failure).  This is especially useful if working with older OpenStack
deployments which all the time keep orphaned servers, floating IPs, volumes,
etc. dangling around.

These scripts are primarily designed to be used with resalloc-server.rpm, but in
general might be used separately.


%prep
%setup -q -n %name-@TARBALL_VERSION@


%build
%if %{with python2}
%py2_build
%else
%py3_build
%endif


%install
%if %{with python2}
%py2_install
%else
%py3_install
%endif


%check


%files
%license COPYING
%doc README
%{_bindir}/%{name}-*
%_mandir/man1/%{name}-*.1*
%{default_sitelib}/%{pkgname}
%{default_sitelib}/%{pkgname}-*.egg-info


%changelog
* Wed Jul 17 2019 Pavel Raiskup <praiskup@redhat.com>
- no more rpm changelog in upstream spec file
