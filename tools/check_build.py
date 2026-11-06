# check_build.py - runs on the PC (CPython 3.9+), after compiling, before flashing.
#
# Checks the APIs listed in api_check.py (generate it first with
# gen_api_check.py) against what a MicroPython build actually contains,
# using the files the build itself generates - so #if-guarded features that
# were compiled out (like esp32.gpio_deep_sleep_hold on IDF 5.5) show up.
#
# Normally run by tools/build_firmware.sh. Standalone:
#   python tools/check_build.py <build dir> [--api FILE]
# <build dir> is micropython/ports/esp32/build-ISURLOG_ESP32; --api defaults
# to the api_check.py inside it. Exits with status 1 if anything is MISSING.
#
# MISSING = not in the build at all: will fail on the device, for certain.
# Names that pass are very likely present, but not guaranteed (a name can
# exist for another module), so api_check.py on the device stays the final word.
#
# Attributes are only checked for modules implemented in C, against the C
# side's names: our own code is frozen into the same firmware, so every name
# it uses also appears among the frozen modules' names and would always "pass".
# For frozen Python modules (asyncio, requests...) only the module itself is checked.

import argparse
import ast
import os
import re
import sys


def load_api_lists(path):
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    ns = {}
    assigns = [n for n in tree.body if isinstance(n, ast.Assign)]
    exec(compile(ast.Module(body=assigns, type_ignores=[]), path, "exec"), ns)
    return ns["MODULE_ATTRS"], ns["CLASS_ATTRS"], set(ns["OPTIONAL"])


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Check a MicroPython build against api_check.py.")
    parser.add_argument("build", help="MicroPython build dir, e.g. micropython/ports/esp32/build-ISURLOG_ESP32")
    parser.add_argument("--api", help="api_check.py to check (default: the one inside the build dir)")
    args = parser.parse_args()
    build = os.path.abspath(args.build)
    api_file = os.path.abspath(args.api) if args.api else os.path.join(build, "api_check.py")
    if not os.path.isfile(api_file):
        sys.exit("Not found: {}\nGenerate it first: python tools/gen_api_check.py --out {}".format(api_file, api_file))
    qstr_h = os.path.join(build, "genhdr", "qstrdefs.generated.h")
    modules_h = os.path.join(build, "genhdr", "moduledefs.collected")
    frozen_c = os.path.join(build, "frozen_content.c")
    for p in (qstr_h, modules_h, frozen_c):
        if not os.path.isfile(p):
            sys.exit("Not found: {}\nIs this a finished build directory?".format(p))

    names = set(re.findall(r"MP_QSTR_(\w+)", read(qstr_h)))  # C side only, see header

    c_modules = set(re.findall(r"MP_REGISTER_\w*MODULE\(MP_QSTR_(\w+)", read(modules_h)))
    py_modules = set()
    for path in re.findall(r'"([\w/]+)\.py"', read(frozen_c)):  # frozen Python modules, e.g. "asyncio/core.py"
        parts = path.split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            py_modules.add(".".join(parts))

    def resolve(m):
        # MicroPython falls back from "ufoo" to "foo" on import.
        for cand in (m, m[1:] if m.startswith("u") else None):
            if cand in c_modules:
                return "c"
            if cand in py_modules:
                return "py"
        return None

    mod_attrs, cls_attrs, optional = load_api_lists(api_file)
    missing, warn, ok, unchecked = [], [], 0, 0

    for m, attrs in sorted(mod_attrs.items()):
        kind = resolve(m)
        if kind is None:
            (warn if m in optional else missing).append("module {}".format(m))
            continue
        if kind == "py":
            unchecked += len(attrs)
            continue
        for name, where in attrs:
            if name in names:
                ok += 1
            else:
                label = "{}.{}   (used in {})".format(m, name, where)
                (warn if "{}.{}".format(m, name) in optional else missing).append(label)

    for (m, cls), attrs in sorted(cls_attrs.items()):
        if resolve(m) != "c" or cls not in names:
            unchecked += len(attrs) if resolve(m) == "py" else 0
            continue
        for name, where in attrs:
            if name in names:
                ok += 1
            else:
                missing.append("{}.{}.{}   (used in {})".format(m, cls, name, where))

    print("Build: {}".format(build))
    print("=== Build check: {} present, {} MISSING, {} WARN (optional), {} only checkable on the device (frozen Python modules) ===".format(
        ok, len(missing), len(warn), unchecked))
    for x in missing:
        print("MISSING", x)
    for x in warn:
        print("WARN   ", x)
    if missing:
        sys.exit(1)
    print("No API used by the code is missing from this build. Confirm with api_check.py on the device.")


if __name__ == "__main__":
    main()
