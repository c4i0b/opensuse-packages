Name:           wifit3
Version:        0.7.1
Release:        0
Summary:        Wireless auditor TUI talking to USB Wi-Fi adapters from userland
License:        GPL-2.0-only
URL:            https://github.com/derv82/wifit3
Source0:        wifit3-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-base
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-hatchling
BuildRequires:  python3-rpm-macros

Requires:       hashcat
Requires:       python3-platformdirs
Requires:       python3-pyusb
Requires:       python3-rich
Requires:       python3-textual
# libusb-package (bundled libusb-1.0 lookup helper) has no Tumbleweed
# package; flagged upstream of this repo — add python3-libusb-package here
# once it exists.

%description
Wifit3 talks to USB Wi-Fi adapters directly from userland with its own chip
drivers, so it needs no kernel drivers or airmon-ng. Captures handshakes and
feeds hashlines to hashcat.

%prep
%autosetup -n wifit3-%{version}
# Windows-only installer; removing it pre-wheel keeps the RECORD valid
rm -rf src/wifit3/setup/bin
# Fedora needs a sed here dropping Static.update(layout=...): the kwarg is
# textual>=5.0.0 and Fedora ships 4.x. Tumbleweed ships textual 8.x, so the
# sed is intentionally absent here.

%build
%python3_pyproject_wheel

%install
%python3_pyproject_install

%check
export PYTHONPATH=%{buildroot}%{python3_sitelib}
%{buildroot}%{_bindir}/wifit3 --version

%files
%license LICENSE
%{_bindir}/wifit3
%{python3_sitelib}/wifit3/
%{python3_sitelib}/wifit3-*.dist-info/

%changelog
