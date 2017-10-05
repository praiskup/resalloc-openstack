%global srcname resalloc-openstack
%global pkgname resalloc_openstack
%global postrel .dev0

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
Version:    0%{?postrel}
Release:    1%{?dist}
License:    GPLv2+
URL:        https://github.com/praiskup/resalloc-openstack
BuildArch:  noarch


BuildRequires: %pythonpfx-devel
BuildRequires: %pythonpfx-setuptools

Requires: %pythonpfx-cinderclient
Requires: %pythonpfx-neutronclient
Requires: %pythonpfx-novaclient

Source0:    %{name}-%{version}.tar.gz

%description
Resource allocator spawner/terminator scripts for OpenStack


%prep
%setup -q


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
%{_bindir}/%{name}-*
%_mandir/man1/%{name}-*.1*
%{default_sitelib}/%{pkgname}
%{default_sitelib}/%{pkgname}-*.egg-info


%changelog
* Thu Oct 05 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-1
- add handler explicitly for python2

* Wed Oct 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-0
- initial build
