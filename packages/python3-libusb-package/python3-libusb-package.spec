Name:           python3-libusb-package
Version:        1.0.30.1
Release:        0
Summary:        Python package locating a libusb library for pyusb
License:        Apache-2.0
URL:            https://github.com/pyocd/libusb-package
Source0:        libusb-package-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-base
BuildRequires:  python3-rpm-macros
BuildRequires:  libusb-1_0-0
# usb.core import in the %check backend test
BuildRequires:  python3-pyusb
Requires:       libusb-1_0-0
Requires:       python3-pyusb

%description
Python package that provides the libusb shared library so it can be installed
via Python package managers. This build ships the pure-Python part only: with
no bundled library, find_library() falls back to ctypes and uses the system
libusb.

%prep
%autosetup -n libusb-package-%{version} -p1
# empty submodule mountpoint
rm -rf src/libusb
# drop the importlib_resources backport dep
sed -i 's/^import importlib_resources$/import importlib.resources as importlib_resources/' src/libusb_package/__init__.py

%install
# setup.py unconditionally compiles libusb: hand-install the module instead
# (no wheel is built, so the multi-flavor %python3_* machinery does not apply;
# %{python3_sitelib} still resolves to the default flavor's site-packages)
sitedir=%{buildroot}%{python3_sitelib}/libusb_package
install -Dpm644 src/libusb_package/__init__.py "$sitedir/__init__.py"
install -Dpm644 src/libusb_package/py.typed "$sitedir/py.typed"
printf 'version = "%{version}"\n' > "$sitedir/_version.py"
distinfo=%{buildroot}%{python3_sitelib}/libusb_package-%{version}.dist-info
mkdir -p "$distinfo"
cat > "$distinfo/METADATA" <<EOF
Metadata-Version: 2.1
Name: libusb-package
Version: %{version}
Summary: Package containing libusb so it can be installed via Python package managers
License-Expression: Apache-2.0
EOF
{
  echo "libusb_package/__init__.py,,"
  echo "libusb_package/_version.py,,"
  echo "libusb_package/py.typed,,"
  echo "libusb_package-%{version}.dist-info/METADATA,,"
  echo "libusb_package-%{version}.dist-info/RECORD,,"
} > "$distinfo/RECORD"

%check
PYTHONPATH=%{buildroot}%{python3_sitelib} python3 - <<'EOF'
import libusb_package
assert libusb_package.find_library("usb-1.0"), "system libusb not found"
assert libusb_package.get_libusb1_backend() is not None
EOF

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/libusb_package/
%{python3_sitelib}/libusb_package-%{version}.dist-info/

%changelog
