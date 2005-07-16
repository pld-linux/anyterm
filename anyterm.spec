#
%define 	apxs		/usr/sbin/apxs
Summary:	Terminal emulator in a web browser
Name:		anyterm
Version:	1.1.4
Release:	1
Epoch:		1
License:	GPL
Group:		Networking/Daemons
Source0:	http://anyterm.org/download/%{name}-%{version}.tbz2
# Source0-md5:	cf841703b7438866e573f5a33137ff6f
Patch0:	%{name}-makefile.patch
URL:		http://anyterm.org/
BuildRequires:	apache-devel >= 2.0.52-2
BuildRequires:	apr-devel
BuildRequires:	rote-devel >= 0.2.8
BuildRequires:	%{apxs}
Requires:	apache >= 2.0.52-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_httpdir	/home/services/httpd
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define   _sysconfdir /etc/httpd

%description
An apache module plus scripts to make a terminal within a web browser.

%prep
%setup -q
%patch0 -p1

%build
rm -rf $RPM_BUILD_ROOT
cd apachemod
%{__make} \
	INCLUDES='-I/usr/include/apr-util' \
	APXS2=apxs \
	APR_CONFIG=apr-1-config
cd ..
cd anygetty
%{__make}
cd ..

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_sysconfdir}/httpd.conf,%{_pkglibdir},%{_mandir}/man8,%{_httpdir}}

cat > $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/70_anyterm.conf <<END
LoadModule anyterm modules/%{name}.so
Alias /%{name} "%{_httpdir}/%{name}"
anyterm_command '/usr/sbin/anygetty --remotehost "Anyterm: %h"'
END

install apachemod/.libs/%{name}.so $RPM_BUILD_ROOT%{_pkglibdir}/%{name}.so
cp -a browser $RPM_BUILD_ROOT/%{_httpdir}/%{name}
install anygetty/anygetty $RPM_BUILD_ROOT/%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd.conf/*
%doc README
%attr(755,root,root) %{_pkglibdir}/%{name}.so
%attr(755,root,root) %{_sbindir}/anygetty
%{_httpdir}/%{name}

%post
%banner "for full function, setuid %{_sbindir}/anygetty"
