# gen_api_check.py - runs on the PC (CPython 3.9+), NOT on the device.
#
# Scans the firmware code (app/ + src/) for every API it uses from modules
# that the MicroPython firmware itself provides (machine, esp32, os, time,
# bluetooth...), and writes api_check.py: a script to run ON THE DEVICE with
# a new firmware that checks every one of them exists.
#
# Normally run by tools/build_firmware.sh. Standalone:
#   python tools/gen_api_check.py [--repo DIR] [--out FILE]
# Then upload the generated api_check.py to the device and run: import api_check
#
# Limitations: it checks that names exist (hasattr), not that keyword
# arguments or behaviour are unchanged. Instance methods are found with a
# simple "x = Pin(...); x.foo()" heuristic, so a FAIL there may be a false
# positive if the same variable name is reused for another type.

import argparse
import ast
import datetime
import os
import subprocess

# Classes whose instance attributes are defined at runtime, not on the class.
DYNAMIC_ATTR_CLASSES = {("uctypes", "struct")}


def project_top_names(repo):
    """Top-level import names that belong to the project, not the firmware."""
    names = {"modules", "lib", "app", "user_script"}  # user_script: user's file on the device FS
    for d in ("app", os.path.join("src", "lib"), os.path.join("src", "modules")):
        full = os.path.join(repo, d)
        if not os.path.isdir(full):
            continue
        for entry in os.listdir(full):
            if entry.endswith(".py"):
                names.add(entry[:-3])
            elif os.path.isdir(os.path.join(full, entry)):
                names.add(entry)
    return names


def target_key(node):
    """'x' for Name x, 'self.x' for Attribute(self, x); None otherwise."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id + "." + node.attr
    return None


def in_import_error_try(node, parents):
    p = parents.get(node)
    while p is not None:
        if isinstance(p, ast.Try):
            for h in p.handlers:
                names = []
                if isinstance(h.type, ast.Name):
                    names = [h.type.id]
                elif isinstance(h.type, ast.Tuple):
                    names = [e.id for e in h.type.elts if isinstance(e, ast.Name)]
                if h.type is None or "ImportError" in names or "Exception" in names:
                    return True
        p = parents.get(p)
    return False


def scan_file(path, rel, project, mod_attrs, cls_attrs, optional):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), rel)
    except SyntaxError as e:
        print("  skipped (syntax error):", rel, e)
        return
    parents = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            parents[c] = n

    def where(node):
        return "{}:{}".format(rel, getattr(node, "lineno", "?"))

    def is_fw(modname):
        return modname and modname.split(".")[0] not in project

    mod_alias = {}   # local name -> firmware module ("import machine as m")
    cls_alias = {}   # local name -> (module, name) ("from machine import Pin")
    instances = {}   # 'uart' / 'self.uart' -> (module, class)

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if is_fw(a.name):
                    mod_alias[a.asname or a.name.split(".")[0]] = a.name
                    mod_attrs.setdefault(a.name, {})
                    if in_import_error_try(n, parents):
                        optional.add(a.name)
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and is_fw(n.module):
            opt = in_import_error_try(n, parents)
            for a in n.names:
                if a.name == "*":
                    continue
                mod_attrs.setdefault(n.module, {}).setdefault(a.name, where(n))
                cls_alias[a.asname or a.name] = (n.module, a.name)
                if opt:
                    optional.add("{}.{}".format(n.module, a.name))

    for n in ast.walk(tree):
        # x = Pin(...) / self.x = machine.UART(...)
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            f = n.value.func
            cls = None
            if isinstance(f, ast.Name) and f.id in cls_alias:
                cls = cls_alias[f.id]
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in mod_alias:
                cls = (mod_alias[f.value.id], f.attr)
            if cls:
                for t in n.targets:
                    k = target_key(t)
                    if k:
                        instances[k] = cls

    # MicroPython never evaluates annotations, so names used only there aren't needed.
    in_annotation = set()
    for n in ast.walk(tree):
        anns = []
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            anns = [n.returns] + [a.annotation for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs]
        elif isinstance(n, ast.AnnAssign):
            anns = [n.annotation]
        for a in anns:
            if a is not None:
                in_annotation.update(ast.walk(a))

    for n in ast.walk(tree):
        if not isinstance(n, ast.Attribute) or n in in_annotation:
            continue
        v = n.value
        if isinstance(v, ast.Name) and v.id in mod_alias:          # machine.deepsleep
            mod_attrs.setdefault(mod_alias[v.id], {}).setdefault(n.attr, where(n))
        elif isinstance(v, ast.Name) and v.id in cls_alias:        # Pin.OUT, Partition.RUNNING
            cls_attrs.setdefault(cls_alias[v.id], {}).setdefault(n.attr, where(n))
        elif (isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name)
              and v.value.id in mod_alias):                        # esp32.Partition.BOOT
            key = (mod_alias[v.value.id], v.attr)
            cls_attrs.setdefault(key, {}).setdefault(n.attr, where(n))
        else:
            k = target_key(v)                                      # uart.deinit()
            if k in instances and instances[k] not in DYNAMIC_ATTR_CLASSES:
                cls_attrs.setdefault(instances[k], {}).setdefault(n.attr, where(n))


def main():
    parser = argparse.ArgumentParser(description="Generate api_check.py for the device.")
    parser.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help="firmware repo root (default: the repo this script lives in)")
    parser.add_argument("--out", default="api_check.py", help="output file (default: ./api_check.py)")
    args = parser.parse_args()
    repo, output = os.path.abspath(args.repo), os.path.abspath(args.out)
    project = project_top_names(repo)
    mod_attrs, cls_attrs, optional = {}, {}, set()

    files = []
    for d in ("app", "src"):
        for root, _, names in os.walk(os.path.join(repo, d)):
            files += [os.path.join(root, f) for f in names if f.endswith(".py")]
    for path in sorted(files):
        scan_file(path, os.path.relpath(path, repo).replace(os.sep, "/"), project, mod_attrs, cls_attrs, optional)

    try:
        commit = subprocess.check_output(["git", "-C", repo, "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"

    lines = [
        "# api_check.py - GENERATED by gen_api_check.py, do not edit by hand.",
        "# Source: {} @ {} on {}".format(repo, commit, datetime.date.today()),
        "# Run ON THE DEVICE with the new firmware: import api_check",
        "",
        "MODULE_ATTRS = {",
    ]
    for m in sorted(mod_attrs):
        lines.append("    {!r}: {!r},".format(m, sorted(mod_attrs[m].items())))
    lines += ["}", "", "CLASS_ATTRS = {"]
    for k in sorted(cls_attrs):
        lines.append("    {!r}: {!r},".format(k, sorted(cls_attrs[k].items())))
    lines += ["}", "", "OPTIONAL = {!r}".format(sorted(optional)), ""]
    lines += [line for line in DEVICE_RUNNER.splitlines()]

    with open(output, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    n_mod = sum(len(v) for v in mod_attrs.values())
    n_cls = sum(len(v) for v in cls_attrs.values())
    print("Scanned {} files from {} @ {}".format(len(files), repo, commit))
    print("{} firmware modules, {} module attributes, {} class/instance attributes".format(len(mod_attrs), n_mod, n_cls))
    print("Written:", output)


DEVICE_RUNNER = '''
def _run():
    import gc
    fails, warns, oks = [], [], 0
    mods = {}
    for m, attrs in MODULE_ATTRS.items():
        try:
            mods[m] = __import__(m)
            for part in m.split(".")[1:]:
                mods[m] = getattr(mods[m], part)
        except ImportError as e:
            (warns if m in OPTIONAL else fails).append("import {} -> {}".format(m, e))
            continue
        for name, where in attrs:
            if hasattr(mods[m], name):
                oks += 1
            else:
                (warns if "{}.{}".format(m, name) in OPTIONAL else fails).append("{}.{}   (used in {})".format(m, name, where))
    for (m, cls), attrs in CLASS_ATTRS.items():
        obj = getattr(mods.get(m), cls, None) if m in mods else None
        if not isinstance(obj, type):
            continue  # Only real classes: for factory functions (requests.get, re.compile...) the attrs belong to what they return.
        for name, where in attrs:
            if hasattr(obj, name):
                oks += 1
            else:
                fails.append("{}.{}.{}   (used in {})".format(m, cls, name, where))
        gc.collect()
    print("\\n=== API check: {} OK, {} FAIL, {} WARN (optional) ===".format(oks, len(fails), len(warns)))
    for f in fails:
        print("FAIL", f)
    for w in warns:
        print("WARN", w)
    if not fails:
        print("All firmware APIs used by the code exist in this firmware.")

_run()
'''

if __name__ == "__main__":
    main()
