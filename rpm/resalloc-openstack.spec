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
Version:    3
Release:    2%{?dist}
License:    GPLv2+
URL:        https://github.com/praiskup/resalloc-openstack
BuildArch:  noarch


BuildRequires: %pythonpfx-devel
BuildRequires: %pythonpfx-setuptools

Requires: %pythonpfx-cinderclient
Requires: %pythonpfx-glanceclient
Requires: %pythonpfx-keystoneauth1
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
%doc README
%{_bindir}/%{name}-*
%_mandir/man1/%{name}-*.1*
%{default_sitelib}/%{pkgname}
%{default_sitelib}/%{pkgname}-*.egg-info


%changelog
* Thu Apr 18 2019 Pavel Raiskup <praiskup@redhat.com> - 3-2
- add missing Requires

* Thu Apr 18 2019 Pavel Raiskup <praiskup@redhat.com> - 3-1
- more solid VM termination
- dump verbosely what is going on

* Sat Mar 23 2019 Pavel Raiskup <praiskup@redhat.com> - 2-1
- support v3 connection API

* Wed Oct 31 2018 Pavel Raiskup <praiskup@redhat.com> - 1-1
- rebuild for Python 3.7

* Tue Jan 30 2018 Pavel Raiskup <praiskup@redhat.com> - 1.dev0-0
- first tagged release

* Wed Jan 10 2018 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-4
- add 'resalloc-openstack --nic' option
- 'resalloc-openstack-new --image' accepts image name, too

* Fri Oct 13 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-3
- fix the volume attaching

* Thu Oct 05 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-2
- new: add --key-pair-id option

* Thu Oct 05 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-1
- add handler explicitly for python2

* Wed Oct 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0.dev0-0
- initial build
