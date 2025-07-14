# TODO
# - anygetty hangs due /bin/login calling vhangup()
#   http://anyterm.org/1.0/config.html
# - put anygetty to separate package?
%define 	apxs		/usr/sbin/apxs
Summary:	Terminal emulator in a web browser
Summary(pl.UTF-8):	Emulator terminala działający w przeglądarce WWW
Name:		anyterm
Version:	1.1.4
Release:	0.10
Epoch:		0
License:	GPL
Group:		Networking/Daemons
Source0:	http://anyterm.org/download/%{name}-%{version}.tbz2
# Source0-md5:	cf841703b7438866e573f5a33137ff6f
Patch0:		%{name}-makefile.patch
URL:		http://anyterm.org/
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0.52-2
BuildRequires:	apr-devel
BuildRequires:	rote-devel >= 0.2.8
BuildRequires:	rpmbuild(macros) >= 1.228
Requires:	apache >= 2.0.52-2
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
An Apache module plus scripts to make a terminal within a web browser.

%description -l pl.UTF-8
Moduł Apache'a i skrypty tworzące terminal w przeglądarce WWW.

%prep
%setup -q
%patch -P0 -p1
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

cat > $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/70_anyterm.conf <<'END'
LoadModule anyterm modules/%{name}.so
<IfModule anyterm>
	Alias /%{name} "%{_appdir}"
	# hangs on login:
#	anyterm_command '%{_sbindir}/anygetty --remotehost "Anyterm: %h"'
	# works for me:
	anyterm_command "USER=%u; exec /usr/bin/ssh ${USER:+$USER@}localhost"

	<Files anyterm-module>
		SetHandler anyterm
		<IfModule mod_setenv.c>
			# for this to work you need to change CustomLog:
			# CustomLog /path/to/logfile combined env=!DONTLOG
			# http://anyterm.org/security.html
			SetEnv DONTLOG
		</IfModule>
	</Files>

	<IfModule !mod_auth.c>
		<Location /%{name}>
			allow from all
		</Location>
	</IfModule>

	<IfModule mod_auth.c>
		<Location /%{name}>
			AuthType Basic
			AuthUserFile /etc/httpd/user
			AuthGroupFile /etc/httpd/group
			AuthName "AnyTerm"
			require group anyterm
			satisfy any
			order allow,deny
		</Location>
	</IfModule>
</IfModule>
# vim: filetype=apache ts=4 sw=4 et
END

install apachemod/.libs/%{name}.so $RPM_BUILD_ROOT%{_pkglibdir}/%{name}.so
cp -a browser/* $RPM_BUILD_ROOT%{_appdir}
install anygetty/anygetty $RPM_BUILD_ROOT%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service httpd restart

%banner %{name} <<-EOF
To use anygetty, you need to setuid it:
chmod 4755 %{_sbindir}/anygetty
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
