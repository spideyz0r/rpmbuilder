%global nm_dispatcher_dir %{_prefix}/lib/NetworkManager
%global puppet_libdir %{ruby_vendorlibdir}

Name:           puppet
Version:        6.26.0
Release:        1%{?dist}
Summary:        Network tool for managing many disparate systems
License:        ASL 2.0
URL:            https://puppetlabs.com
Source0:        https://downloads.puppetlabs.com/puppet/%{name}-%{version}.tar.gz
Source1:        https://downloads.puppetlabs.com/puppet/%{name}-%{version}.tar.gz.asc
Source2:        RPM-GPG-KEY-puppet-20250406
Source3:        https://forge.puppet.com/v3/files/puppetlabs-mount_core-1.0.4.tar.gz
Source4:        https://forge.puppet.com/v3/files/puppetlabs-host_core-1.0.3.tar.gz
Source5:        https://forge.puppet.com/v3/files/puppetlabs-augeas_core-1.1.1.tar.gz
Source6:        https://forge.puppet.com/v3/files/puppetlabs-cron_core-1.0.4.tar.gz
Source7:        https://forge.puppet.com/v3/files/puppetlabs-scheduled_task-2.2.1.tar.gz
Source8:        https://forge.puppet.com/v3/files/puppetlabs-selinux_core-1.0.4.tar.gz
Source9:        https://forge.puppet.com/v3/files/puppetlabs-sshkeys_core-2.2.0.tar.gz
Source10:       https://forge.puppet.com/v3/files/puppetlabs-yumrepo_core-1.0.7.tar.gz
Source11:       https://forge.puppet.com/v3/files/puppetlabs-zfs_core-1.1.0.tar.gz
Source12:       https://forge.puppet.com/v3/files/puppetlabs-zone_core-1.0.3.tar.gz
Source13:       puppet-nm-dispatcher.systemd
Source14:       start-puppet-wrapper
Source15:       logrotate

BuildArch: noarch

# ruby-devel does not require the base package, but requires -libs instead
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: ruby-facter
BuildRequires: hiera
BuildRequires: systemd
Requires: hiera >= 3.3.1
Requires: facter >= 3.9.6
Requires: ruby-facter >= 3.9.6
Requires: rubygem-semantic_puppet >= 1.0.2
Requires: rubygem-puppet-resource_api
Requires: rubygem-deep_merge
Requires: rubygem-httpclient
Requires: rubygem-multi_json
Requires: rubygem-json
Requires: ruby-augeas >= 0.5.0
Requires: augeas >= 1.10.1
Requires: augeas-libs >= 1.10.1
Requires: cpp-hocon >= 0.2.1
Requires: rubygem-concurrent-ruby >= 1.0.5
Requires: ruby(selinux) libselinux-utils
Obsoletes: puppet-headless < 6.0.0
Obsoletes: puppet-server < 6.0.0
Obsoletes: puppet < 6.0.0

%description
Puppet lets you centrally manage every important aspect of your system using a
cross-platform specification language that manages all the separate elements
normally aggregated in different files, like users, cron jobs, and hosts,
along with obviously discrete elements like packages, services, and files.

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%autosetup
cp -a %{sources} .
for f in puppetlabs-*.tar*; do
  tar xvf $f
done
# Puppetlabs messed up with default paths
find -type f -exec \
  sed -i \
    -e 's|/opt/puppetlabs/puppet/bin|%{_bindir}|' \
    -e 's|/opt/puppetlabs/puppet/cache|%{_sharedstatedir}/puppet|' \
    -e 's|/opt/puppetlabs/puppet/share/locale|%{_datadir}/puppetlabs/puppet/locale|' \
    -e 's|/opt/puppetlabs/puppet/modules|%{_datadir}/puppetlabs/puppet/modules|' \
    -e 's|/opt/puppetlabs/puppet/vendor_modules|%{_datadir}/puppetlabs/puppet/vendor_modules|' \
  '{}' +

%install
ruby install.rb --destdir=%{buildroot} \
 --bindir=%{_bindir} \
 --logdir=%{_localstatedir}/log/puppetlabs/puppet \
 --rundir=%{_rundir}/puppet \
 --localedir=%{_datadir}/puppetlabs/puppet/locale \
 --vardir=%{_sharedstatedir}/puppet \
 --sitelibdir=%{puppet_libdir}

mkdir -p %{buildroot}/usr/share/puppetlabs/puppet/vendor_modules
for d in $(find -mindepth 1 -maxdepth 1 -type d -name 'puppetlabs-*'); do
  modver=${d#*-}
  mod=${modver%-*}
  cp -a $d %{buildroot}%{_datadir}/puppetlabs/puppet/vendor_modules/$mod
done

install -Dp -m0644 %{SOURCE15} %{buildroot}%{_sysconfdir}/logrotate.d/puppet

%{__install} -d -m0755 %{buildroot}%{_unitdir}
install -Dp -m0644 ext/systemd/puppet.service %{buildroot}%{_unitdir}/puppet.service
ln -s %{_unitdir}/puppet.service %{buildroot}%{_unitdir}/puppetagent.service

install -Dpv -m0755 %{SOURCE13} \
 %{buildroot}%{nm_dispatcher_dir}/dispatcher.d/98-%{name}

# Install the ext/ directory to %%{_datadir}/puppetlabs/%%{name}
install -d %{buildroot}%{_datadir}/puppetlabs/%{name}
cp -a ext/ %{buildroot}%{_datadir}/puppetlabs/%{name}

# Install wrappers for SELinux
install -Dp -m0755 %{SOURCE14} %{buildroot}%{_bindir}/start-puppet-agent
sed -i 's|^ExecStart=.*/bin/puppet|ExecStart=%{_bindir}/start-puppet-agent|' \
 %{buildroot}%{_unitdir}/puppet.service

# Setup tmpfiles.d config
mkdir -p %{buildroot}%{_tmpfilesdir}
echo "D %{_rundir}/%{name} 0755 %{name} %{name} -" > \
 %{buildroot}%{_tmpfilesdir}/%{name}.conf

# Unbundle
# Note(hguemar): remove unrelated OS/distro specific folders
# These mess-up with RPM automatic dependencies compute by adding
# unnecessary deps like /sbin/runscripts
# some other things were removed with the patch
rm -r %{buildroot}%{_datadir}/puppetlabs/puppet/ext/{debian,solaris,suse,windows}
rm %{buildroot}%{_datadir}/puppetlabs/puppet/ext/redhat/*.init
rm %{buildroot}%{_datadir}/puppetlabs/puppet/ext/{build_defaults.yaml,project_data.yaml}

%files
%attr(-, puppet, puppet) %{_localstatedir}/log/puppetlabs
%attr(-, puppet, puppet) %{_datadir}/puppetlabs/puppet
%dir %attr(-, puppet, puppet) %{_datadir}/puppetlabs
%{_unitdir}/puppet.service
%{_unitdir}/puppetagent.service
%{_tmpfilesdir}/%{name}.conf
%dir %{nm_dispatcher_dir}
%dir %{nm_dispatcher_dir}/dispatcher.d
%{nm_dispatcher_dir}/dispatcher.d/98-puppet
%{_bindir}/start-puppet-agent

%doc README.md examples
%license LICENSE
%{_datadir}/ruby/vendor_ruby/hiera
%{_datadir}/ruby/vendor_ruby/hiera_puppet.rb
%{_datadir}/ruby/vendor_ruby/puppet
%{_datadir}/ruby/vendor_ruby/puppet_pal.rb
%{_datadir}/ruby/vendor_ruby/puppet.rb
%{_datadir}/ruby/vendor_ruby/puppet_x.rb
%{_sharedstatedir}/puppet
%{_bindir}/puppet
%{_mandir}/man5/puppet.conf.5*
%{_mandir}/man8/puppet-plugin.8*
%{_mandir}/man8/puppet-report.8*
%{_mandir}/man8/puppet-resource.8*
%{_mandir}/man8/puppet-script.8*
%{_mandir}/man8/puppet-ssl.8*
%{_mandir}/man8/puppet-status.8*
%{_mandir}/man8/puppet-agent.8*
%{_mandir}/man8/puppet.8*
%{_mandir}/man8/puppet-apply.8*
%{_mandir}/man8/puppet-catalog.8*
%{_mandir}/man8/puppet-config.8*
%{_mandir}/man8/puppet-describe.8*
%{_mandir}/man8/puppet-device.8*
%{_mandir}/man8/puppet-doc.8*
%{_mandir}/man8/puppet-epp.8*
%{_mandir}/man8/puppet-facts.8*
%{_mandir}/man8/puppet-filebucket.8*
%{_mandir}/man8/puppet-generate.8*
%{_mandir}/man8/puppet-help.8*
%{_mandir}/man8/puppet-key.8*
%{_mandir}/man8/puppet-lookup.8*
%{_mandir}/man8/puppet-man.8*
%{_mandir}/man8/puppet-module.8*
%{_mandir}/man8/puppet-node.8*
%{_mandir}/man8/puppet-parser.8*

%config(noreplace) %attr(-, puppet, puppet) %dir %{_sysconfdir}/puppetlabs
%config(noreplace) %attr(-, puppet, puppet) %dir %{_sysconfdir}/puppetlabs/puppet
%config(noreplace) %attr(-, puppet, puppet) %dir %{_sysconfdir}/puppetlabs/code
%config(noreplace) %attr(644, puppet, puppet) %{_sysconfdir}/puppetlabs/puppet/auth.conf
%config(noreplace) %attr(644, puppet, puppet) %{_sysconfdir}/puppetlabs/puppet/puppet.conf
%config(noreplace) %attr(644, puppet, puppet) %{_sysconfdir}/puppetlabs/puppet/hiera.yaml
%config(noreplace) %attr(644, root, root) %{_sysconfdir}/logrotate.d/%{name}

%ghost %attr(755, puppet, puppet) %{_rundir}/%{name}

%pre
getent group puppet &>/dev/null || groupadd -r puppet -g 52 &>/dev/null
getent passwd puppet &>/dev/null || \
useradd -r -u 52 -g puppet -d /usr/local/puppetlabs -s /sbin/nologin \
 -c "Puppet" puppet &>/dev/null

%post
%systemd_post puppet.service

%postun
%systemd_postun_with_restart puppet.service


%changelog
* Wed Jan 26 2022 Breno Brand Fernandes <brandfbb@gmail.com> - 6.26.0-1
- Update to 6.26.0

* Thu Nov 18 2021 Breno Brand Fernandes <brandfbb@gmail.com> - 6.25.1-1
- Update to 6.25.1

* Thu Oct 22 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 6.19.0-1
- Update to 6.19.0

* Sat Sep 26 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 6.18.0-1
- Update to 6.18.0

* Fri Aug 28 2020 Igor Raits <ignatenkobrain@fedoraproject.org> - 6.17.0-1
- Update to 6.17.0
- Verify GPG key of the main tarball
- Drop unneeded BuildRequires
- Trivial fixes in packaging

* Mon Jul 13 2020 Breno Brand Fernandes <brandfbb@gmail.com> - 6.14.0-1
- Build of puppet 6.