Name:           crunch
Version:        3.6
Release:        0
Summary:        Wordlist generator with configurable character sets
License:        GPL-2.0-only
URL:            https://github.com/crunchsec/crunch
Source0:        crunch-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make

%description
Crunch is a wordlist generator where you can specify a standard or custom
character set. It generates all possible combinations of the given charset,
with size and pattern constraints.

%prep
%autosetup

%build
# Makefile defaults to -g -o0 via OPTFLAGS; the distro flags must come in
# as a command-line CFLAGS override (they are appended after CFLAGS_STD).
%make_build CFLAGS="%{optflags}"

%install
# INSTALL defaults to "sudo install", INSTALL_OPTIONS to "-g root -o root".
# The Makefile hardcodes /usr/share/doc/crunch (not the openSUSE
# /usr/share/doc/packages dir); the COPYING there is covered by %license.
%make_install PREFIX=%{_prefix} INSTALL=install INSTALL_OPTIONS=
rm -f %{buildroot}%{_datadir}/doc/crunch/COPYING

%files
%license COPYING
%{_bindir}/crunch
%dir %{_datadir}/crunch
%{_datadir}/crunch/charset.lst
%{_mandir}/man1/crunch.1%{?ext_man}

%changelog
