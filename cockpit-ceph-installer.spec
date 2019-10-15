Name: cockpit-ceph-installer
Version: 0.9
Release: 2%{?dist}
Summary: Cockpit plugin for Ceph cluster installation
License: LGPLv2+

Source: ceph-installer-%{version}.tar.gz
BuildArch: noarch

Requires: ceph-ansible >= 3.1
Requires: cockpit
Requires: libcdio
Requires: cockpit-bridge

%if "%{?dist}" == ".el7" || "%{rhel}" == "7"
%define containermgr    docker
%else
%define containermgr    podman
%endif

Requires: %{containermgr}

%description
This package installs a cockpit plugin that provides a graphical interface to install a Ceph cluster. The plugin itself handles UI interaction and depends on the ansible-runner-service API to handle the configuration and management of the ansible inventory and playbooks.
In addition to the plugin, the installation process also enables docker/podman which is required for the ansible-runner-service API.

Once installed, a helper script called ansible-runner-service.sh is available to handle the installation and configuration of the ansible-runner-service daemon (container).

%prep
%setup -q -n ceph-installer-%{version}

%install
mkdir -p %{buildroot}%{_datadir}/cockpit/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/ceph-ansible/library
install -m 0644 dist/* %{buildroot}%{_datadir}/cockpit/%{name}/
install -m 0755 utils/ansible-runner-service.sh %{buildroot}%{_bindir}/
install -m 0644 utils/ansible/library/ceph_check_role.py %{buildroot}%{_datadir}/ceph-ansible/library/
install -m 0644 utils/ansible/checkrole.yml %{buildroot}%{_datadir}/ceph-ansible/
mkdir -p %{buildroot}%{_datadir}/metainfo/
install -m 0644 ./org.cockpit-project.%{name}.metainfo.xml %{buildroot}%{_datadir}/metainfo/


%post
if [ "$1" = 1 ]; then
  systemctl enable --now cockpit.service

# copy the ceph-ansible sample playbooks, so they're available to the runner-service
  cp %{_datadir}/ceph-ansible/site.yml.sample %{_datadir}/ceph-ansible/site.yml 
  cp %{_datadir}/ceph-ansible/site-docker.yml.sample %{_datadir}/ceph-ansible/site-docker.yml 
  cp %{_datadir}/ceph-ansible/site-docker.yml.sample %{_datadir}/ceph-ansible/site-container.yml 

# If this is a docker environment, start the daemon
  if  [ "%{containermgr}" == "docker" ]; then 
    systemctl enable --now %{containermgr}.service
  fi

fi

%files
%{_datadir}/cockpit/*
%{_datadir}/metainfo/*
%{_bindir}/ansible-runner-service.sh
%{_datadir}/ceph-ansible/library/ceph_check_role.py
%{_datadir}/ceph-ansible/checkrole.yml

# exclude the compiled/optimized py files generated by the helper scripts
%exclude %{_datadir}/ceph-ansible/library/*.pyo
%exclude %{_datadir}/ceph-ansible/library/*.pyc

%changelog
* Tue Oct 15 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-2
- improve handling of container image names that include a tag
- provide ceph.conf overrides for All-in-One clusters BZ1761616
- fix removal of runner-service container BZ1761608
- add missing iso directory to runner-service directory structure BZ1761610
* Sun Sep 15 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-1
- minor UI improvements
- add ISO installation option
- exclude loop back devices from device discovery in checkrole playbook (EL8 issue)
- fix port conflict when the metrics host is the same as the installer host
* Wed Jul 24 2019 Paul Cuzner <pcuzner@redhat.com> 0.9-0
- ceph-check-role ansible module and playbook included
* Wed Jul 17 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-8
- remove ansible-runner-service rpm dependency
- handle podman/docker for el7/el8
- ensure the ansible-runner-service setup script is installed
* Thu Mar 21 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-7
- Return error if the probe task fails in some way
- Add visual cue (spinner) when the probe task is running
* Sun Mar 17 2019 Paul Cuzner <pcuzner@redhat.com> 0.8-6
- Added 'save' step in deploy workflow, enabling ansible vars to be manually updated
* Sun Dec 16 2018 Paul Cuzner <pcuzner@redhat.com> 0.8
- Initial rpm build
- First functionally complete version