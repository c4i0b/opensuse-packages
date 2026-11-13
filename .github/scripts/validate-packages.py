#!/usr/bin/env python3
"""Version/asset gate shared by validate.yml (PRs) and autoupdate.yml
(in-job bump gate). Reads PACKAGES (comma-separated package dirs) from the
environment; non-zero exit on any failure."""
import glob
import os
import re
import sys
import urllib.error
import urllib.request

pkgs = [p for p in os.environ["PACKAGES"].split(",") if p]
failures = []

for pkg in pkgs:
    specs = glob.glob(os.path.join(pkg, "*.spec"))
    svc = os.path.join(pkg, "_service")
    if not specs:
        failures.append(f"{pkg}: no spec")
        continue
    if not os.path.isfile(svc):
        failures.append(f"{pkg}: no _service (a bump must update it)")
        continue

    ver = None
    for line in open(specs[0]):
        m = re.match(r"^Version:\s*(\S+)", line)
        if m:
            ver = m.group(1)
            break
    if not ver:
        failures.append(f"{pkg}: no Version in {specs[0]}")
        continue

    xml = open(svc).read()
    def param(name):
        m = re.search(r'<param name="%s">([^<]*)</param>' % name, xml)
        return m.group(1) if m else None
    url = "".join(x for x in [param("protocol"), "://", param("host"), param("path")] if x)
    if not url.startswith(("http://", "https://")):
        # git-tag packages (tar_scm/obs_scm): the version comes from
        # the tag, validated against the revision param instead of a
        # download URL
        if re.search(r'<service name="(tar_scm|obs_scm)"', xml):
            rev = param("revision") or ""
            if not re.search(r"(^|[/_.-])v?" + re.escape(ver) + r"([/_.-]|$)", rev):
                failures.append(f"{pkg}: tar_scm revision ({rev!r}) does not reference version {ver}")
            else:
                print(f"{pkg}: Version {ver}, tar_scm tag {rev} matches")
            continue
        failures.append(f"{pkg}: could not parse _service download URL")
        continue

    # Date-tagged upstreams (vinceliuice icon themes): the git tag in the
    # download path carries '-' while Version is the dot-sanitized form,
    # so the version reference may live in the renamed filename param.
    fn = param("filename") or ""
    if not (re.search(r"(^|[/_.-])v?" + re.escape(ver) + r"([/_.-]|$)", url)
            or re.search(r"(^|[_.-])v?" + re.escape(ver) + r"([_.-]|$)", fn)):
        failures.append(f"{pkg}: _service URL ({url}, filename {fn!r}) does not reference version {ver}")

    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        failures.append(f"{pkg}: could not HEAD {url}: {e}")
        continue
    if not (200 <= code < 400):
        failures.append(f"{pkg}: HEAD {url} -> HTTP {code}")
    print(f"{pkg}: Version {ver}, upstream asset HTTP {code}")

if failures:
    print("FAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print(f"OK: {len(pkgs)} package(s) validated")
