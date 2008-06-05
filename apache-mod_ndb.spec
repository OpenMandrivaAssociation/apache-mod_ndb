#Module-Specific definitions
%define mod_name mod_ndb
%define mod_conf A94_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	An Apache module to access NDB Cluster
Name:		apache-%{mod_name}
Version:	1.0
Release:	%mkrel 0.rc.3
Group:		System/Servers
License:	GPL
URL:		http://code.google.com/p/mod-ndb/
Source0:	http://mod-ndb.googlecode.com/files/%{mod_name}-%{version}-rc.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
Requires:	mysql-max >= 5.0.33
Requires:	mysql-ndb-extra >= 5.0.33
Requires:	mysql-ndb-management >= 5.0.33
Requires:	mysql-ndb-storage >= 5.0.33
Requires:	mysql-ndb-tools >= 5.0.33
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	mysql-devel >= 5.0.33
BuildRequires:	mysql-static-devel >= 5.0.33
BuildRequires:	apache-ssl-devel
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Mod_ndb is an Apache module that provides a Web Services API for MySQL Cluster.
It creates a direct connection from an Apache Web server to the NDB data nodes
in a MySQL Cluster (bypassing mysqld, and eliminating the need to create or
parse SQL queries). This allows you to query and modify a database over HTTP
using GET, POST, and DELETE requests, and retrieve results in a variety of
formats, including JSON results that can go 'direct to the browser' in an AJAX
application. Mod_ndb is also scriptable, using Apache's subrequest API, so that
complex multi-table transactions or joins (even including sort-merge join plans
that are currently not possible in MySQL) can be easily created in PHP or Perl.

%prep

%setup -q -n %{mod_name}-%{version}-rc

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;
		
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

head -16 mod_ndb_ap20.cc > LICENSE

%build

./configure \
    --mysql=%{_bindir}/mysql_config \
    --apxs=%{_sbindir}/apxs \
    --apxs1=%{_sbindir}/httpsd-apxs \
    --aprconfig=%{_bindir}/apr-1-config \
    --thread-safe

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 %{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc Tests example-scripts README test.conf httpd.conf Architecture.pdf LICENSE
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
