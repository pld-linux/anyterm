%define 	apxs		/usr/sbin/apxs
Summary:	Terminal emulator in a web browser
Name:		anyterm
Version:	1.1.4
Release:	0.3
Epoch:		0
License:	GPL
Group:		Networking/Daemons
Source0:	http://anyterm.org/download/%{name}-%{version}.tbz2
# Source0-md5:	cf841703b7438866e573f5a33137ff6f
Patch0:		%{name}-makefile.patch
URL:		http://anyterm.org/
BuildRequires:	apache-devel >= 2.0.52-2
BuildRequires:	apr-devel
BuildRequires:	rote-devel >= 0.2.8
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	%{apxs}
Requires:	apache >= 2.0.52-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir /etc/httpd

%description
An apache module plus scripts to make a terminal within a web browser.

%prep
%setup -q
%patch0 -p1
mv -f browser/.htaccess htaccess

%build
%{__make} -C apachemod \
	INCLUDES='-I%{_includedir}/apr-util' \
	APXS2=%{apxs} \
	APR_CONFIG=apr-1-config
%{__make} -C anygetty

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/httpd.conf,%{_pkglibdir},%{_mandir}/man8,%{_appdir}}

cat > $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/70_anyterm.conf <<END
LoadModule anyterm modules/%{name}.so
<IfModule anyterm>
	Alias /%{name} "%{_appdir}"
	anyterm_command '%{_sbindir}/anygetty --remotehost "Anyterm: %h"'

	<Files anyterm-module>
		SetHandler anyterm
	</Files>
</IfModule>
# vim: filetype=apache ts=4 sw=4 et
END

install apachemod/.libs/%{name}.so $RPM_BUILD_ROOT%{_pkglibdir}/%{name}.so
cp -a browser/* $RPM_BUILD_ROOT%{_appdir}
install anygetty/anygetty $RPM_BUILD_ROOT/%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service httpd restart

%banner %{name} <<EOF
For full function, setuid %{_sbindir}/anygetty.
EOF

%preun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc README CHANGELOG htaccess
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*
%attr(755,root,root) %{_pkglibdir}/%{name}.so
%attr(755,root,root) %{_sbindir}/anygetty
%{_appdir}
