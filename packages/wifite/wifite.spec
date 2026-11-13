Name:           wifite
Version:        2.2.5
Release:        0
Summary:        Automated wireless attack tool
License:        GPL-2.0-only
URL:            https://github.com/derv82/wifite2
Source0:        wifite-%{version}.tar.gz
Source1:        wifite-completion
BuildArch:      noarch

BuildRequires:  python3-base
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-rpm-macros

# No runtime Python deps: wifite shells out to external tools (soft
# dependency wrappers in wifite/tools/, warns when one is missing).
Requires:       aircrack-ng
# net-tools provides ifconfig
Requires:       net-tools
# iproute2 provides ip
Requires:       iproute2
Requires:       iw
Requires:       hashcat
Requires:       john
# wireshark ships tshark/dumpcap (Fedora's wireshark-cli equivalent)
Requires:       wireshark
Requires:       hcxtools
Requires:       hcxdumptool
# used by the --random-mac flag
Requires:       macchanger
Requires:       bully
# Still not packaged in Tumbleweed (upstream treats them as optional,
# warns and skips): pixiewps, reaver, cowpatty.

%description
Wifite is an automated wireless attack tool. It wraps the auditing
toolchain (aircrack-ng, hashcat, hcxtools and friends), scanning for
networks and running the supported attacks (WPS pixie-dust and
brute-force, WPA handshake and PMKID capture, WEP attacks) with
sensible defaults and a single interface.

%prep
%autosetup -n wifite2-%{version}
# console_scripts names a nonexistent module; real entry is wifite.__main__
sed -i 's/wifite\.wifite:entry_point/wifite.__main__:entry_point/' setup.py

%build
%python3_pyproject_wheel

%install
%python3_pyproject_install
install -Dpm755 %{SOURCE1} %{buildroot}%{_datadir}/bash-completion/completions/wifite

%check
export PYTHONPATH=%{buildroot}%{python3_sitelib}
%{buildroot}%{_bindir}/wifite --help > /dev/null

%files
%license LICENSE
%doc README.md
%{_bindir}/wifite
%{_datadir}/bash-completion/completions/wifite
# bundled probable-password wordlist (data_files in setup.py)
%{_datadir}/dict/wordlist-top4800-probable.txt
%{python3_sitelib}/wifite/
%{python3_sitelib}/wifite-*.dist-info/

%changelog
