#!/usr/bin/env python3
"""BSP layer validation tool for Yocto/OpenEmbedded layers.

Validates recipe syntax, dependency references, Yocto release compatibility,
bbappend targets, configuration variables, layer priority, and include paths.
"""

import argparse
import os
import re
import sys
from pathlib import Path


KNOWN_YOCTO_RELEASES = [
    "dunfell",
    "gatesgarth",
    "hardknott",
    "honister",
    "kirkstone",
    "langdale",
    "mickledore",
    "nanbield",
    "scarthgap",
    "walnascar",
    "whinlatter",
    "master",
]

REQUIRED_LAYER_CONF_VARS = [
    "BBFILE_COLLECTIONS",
    "BBFILE_PATTERN",
    "BBFILE_PRIORITY",
]

PRIORITY_MIN = 1
PRIORITY_MAX = 99


def find_files(layer_path, extensions):
    """Find all files matching given extensions under layer_path."""
    results = []
    for root, _dirs, files in os.walk(layer_path):
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                results.append(os.path.join(root, f))
    return results


def check_recipe_syntax(layer_path):
    """Check .bb and .bbappend files for common syntax errors."""
    errors = []
    recipe_files = find_files(layer_path, [".bb", ".bbappend"])

    for filepath in recipe_files:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        in_function = False
        func_name = None
        func_start_line = 0

        for lineno, line in enumerate(lines, start=1):
            stripped = line.rstrip("\n")

            # Check for unclosed quotes on non-continuation lines
            if not stripped.endswith("\\"):
                single_quotes = stripped.count("'")
                double_quotes = stripped.count('"')
                if double_quotes % 2 != 0:
                    errors.append(
                        f"{filepath}:{lineno}: Unmatched double quote"
                    )

            # Check for function open/close
            func_open = re.match(
                r"^([a-zA-Z_]\w*)\s*\(\)\s*\{", stripped
            )
            if func_open:
                if in_function:
                    errors.append(
                        f"{filepath}:{lineno}: Nested function "
                        f"'{func_open.group(1)}' inside '{func_name}' "
                        f"(opened at line {func_start_line})"
                    )
                in_function = True
                func_name = func_open.group(1)
                func_start_line = lineno

            if stripped.strip() == "}" and in_function:
                in_function = False
                func_name = None

            # Check for invalid variable assignments (must use = += .= etc.)
            var_assign = re.match(
                r'^([A-Z_][A-Z0-9_]*(?::[a-z\-]+)?)\s+([^=+.<>!?])',
                stripped,
            )
            if var_assign and not stripped.strip().startswith("#"):
                # Lines that look like VAR something (no operator)
                potential_var = var_assign.group(1)
                if potential_var not in ("inherit", "require", "include",
                                        "EXPORT_FUNCTIONS", "addtask",
                                        "deltask", "addhandler"):
                    errors.append(
                        f"{filepath}:{lineno}: Possible missing assignment "
                        f"operator for '{potential_var}'"
                    )

        if in_function:
            errors.append(
                f"{filepath}: Unclosed function '{func_name}' "
                f"(opened at line {func_start_line})"
            )

    return errors


def check_dependencies(layer_path):
    """Check that DEPENDS and RDEPENDS references look valid."""
    errors = []
    recipe_files = find_files(layer_path, [".bb", ".bbappend", ".inc"])

    known_recipes = set()
    for fp in find_files(layer_path, [".bb"]):
        basename = os.path.basename(fp)
        name = re.sub(r"_.*$", "", basename.replace(".bb", ""))
        known_recipes.add(name)

    dep_pattern = re.compile(
        r'(?:DEPENDS|RDEPENDS[_:]\S*)\s*[+=.?]+\s*"([^"]*)"'
    )

    for filepath in recipe_files:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        for match in dep_pattern.finditer(content):
            deps_str = match.group(1)
            deps = deps_str.split()
            for dep in deps:
                dep_clean = re.sub(r"\$\{[^}]+\}", "", dep).strip()
                if not dep_clean or dep_clean.startswith("$"):
                    continue
                if dep_clean.startswith("virtual/"):
                    continue
                # Only warn if it contains obviously wrong chars
                if re.search(r"[^a-zA-Z0-9\-_+.]", dep_clean):
                    errors.append(
                        f"{filepath}: Suspicious dependency name "
                        f"'{dep_clean}'"
                    )

    return errors


def check_layerseries_compat(layer_path):
    """Check LAYERSERIES_COMPAT against known Yocto releases."""
    errors = []
    layer_conf = os.path.join(layer_path, "conf", "layer.conf")

    if not os.path.isfile(layer_conf):
        errors.append(f"{layer_path}: Missing conf/layer.conf")
        return errors

    with open(layer_conf, "r", encoding="utf-8") as f:
        content = f.read()

    compat_match = re.search(
        r'LAYERSERIES_COMPAT_\S+\s*=\s*"([^"]*)"', content
    )
    if not compat_match:
        errors.append(
            f"{layer_conf}: LAYERSERIES_COMPAT not defined"
        )
        return errors

    releases = compat_match.group(1).split()
    for release in releases:
        if release not in KNOWN_YOCTO_RELEASES:
            errors.append(
                f"{layer_conf}: Unknown Yocto release "
                f"'{release}' in LAYERSERIES_COMPAT"
            )

    return errors


def check_bbappend_targets(layer_path):
    """Verify .bbappend files have corresponding .bb recipes in the layer."""
    errors = []
    bb_files = find_files(layer_path, [".bb"])
    bbappend_files = find_files(layer_path, [".bbappend"])

    bb_basenames = set()
    for bb in bb_files:
        basename = os.path.basename(bb)
        name = basename.replace(".bb", "")
        bb_basenames.add(name)
        # Also add wildcard-matchable base name (without version)
        base_name = re.sub(r"_.*$", "", name)
        bb_basenames.add(base_name)

    for bbappend in bbappend_files:
        basename = os.path.basename(bbappend)
        name = basename.replace(".bbappend", "")
        # Handle % wildcard in bbappend names
        name_pattern = name.replace("%", ".*")
        matched = False
        for bb_name in bb_basenames:
            if re.fullmatch(name_pattern, bb_name):
                matched = True
                break
        if not matched:
            # Not necessarily an error - the .bb may be in another layer
            errors.append(
                f"{bbappend}: No matching .bb recipe found in this layer "
                f"for '{basename}' (may exist in another layer)"
            )

    return errors


def check_conf_variables(layer_path):
    """Validate conf/layer.conf variables."""
    errors = []
    layer_conf = os.path.join(layer_path, "conf", "layer.conf")

    if not os.path.isfile(layer_conf):
        errors.append(f"{layer_path}: Missing conf/layer.conf")
        return errors

    with open(layer_conf, "r", encoding="utf-8") as f:
        content = f.read()

    for var in REQUIRED_LAYER_CONF_VARS:
        if var not in content:
            errors.append(
                f"{layer_conf}: Required variable '{var}' not found"
            )

    # Check BBFILE_COLLECTIONS has a value
    coll_match = re.search(
        r'BBFILE_COLLECTIONS\s*\+=\s*"([^"]*)"', content
    )
    if coll_match:
        collection_name = coll_match.group(1).strip()
        if not collection_name:
            errors.append(
                f"{layer_conf}: BBFILE_COLLECTIONS is empty"
            )
        else:
            # Verify BBFILE_PATTERN uses the collection name
            pattern_var = f"BBFILE_PATTERN_{collection_name}"
            if pattern_var not in content:
                errors.append(
                    f"{layer_conf}: {pattern_var} not defined for "
                    f"collection '{collection_name}'"
                )

    return errors


def check_layer_priority(layer_path):
    """Check BBFILE_PRIORITY is set and within valid range."""
    errors = []
    layer_conf = os.path.join(layer_path, "conf", "layer.conf")

    if not os.path.isfile(layer_conf):
        errors.append(f"{layer_path}: Missing conf/layer.conf")
        return errors

    with open(layer_conf, "r", encoding="utf-8") as f:
        content = f.read()

    priority_match = re.search(
        r'BBFILE_PRIORITY_\S+\s*=\s*"(\d+)"', content
    )
    if not priority_match:
        errors.append(
            f"{layer_conf}: BBFILE_PRIORITY not defined"
        )
        return errors

    priority = int(priority_match.group(1))
    if priority < PRIORITY_MIN or priority > PRIORITY_MAX:
        errors.append(
            f"{layer_conf}: BBFILE_PRIORITY value {priority} "
            f"is outside valid range ({PRIORITY_MIN}-{PRIORITY_MAX})"
        )

    return errors


def check_missing_includes(layer_path):
    """Check that require/include statements reference existing files."""
    errors = []
    all_files = find_files(layer_path, [".bb", ".bbappend", ".inc", ".conf"])

    include_pattern = re.compile(
        r"^\s*(require|include)\s+(.+)$", re.MULTILINE
    )

    for filepath in all_files:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        for match in include_pattern.finditer(content):
            directive = match.group(1)
            inc_path = match.group(2).strip()

            # Skip paths with variables - can't resolve at parse time
            if "${" in inc_path:
                continue

            # Try resolving relative to the file's directory
            file_dir = os.path.dirname(filepath)
            candidate = os.path.join(file_dir, inc_path)

            # Also try relative to layer root
            candidate_layer = os.path.join(layer_path, inc_path)

            if not os.path.isfile(candidate) and not os.path.isfile(
                candidate_layer
            ):
                severity = "ERROR" if directive == "require" else "WARNING"
                errors.append(
                    f"{filepath}: {severity}: {directive} '{inc_path}' "
                    f"- file not found"
                )

    return errors


def validate_layer(layer_path):
    """Run all validation checks on a BSP layer."""
    all_errors = []

    checks = [
        ("Recipe syntax", check_recipe_syntax),
        ("Dependency references", check_dependencies),
        ("Layer series compatibility", check_layerseries_compat),
        ("BBAPPEND targets", check_bbappend_targets),
        ("Configuration variables", check_conf_variables),
        ("Layer priority", check_layer_priority),
        ("Missing includes", check_missing_includes),
    ]

    for name, check_func in checks:
        print(f"Running: {name}...")
        errors = check_func(layer_path)
        if errors:
            print(f"  Found {len(errors)} issue(s):")
            for err in errors:
                print(f"    - {err}")
        else:
            print("  OK")
        all_errors.extend(errors)

    return all_errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Yocto/OpenEmbedded BSP layer"
    )
    parser.add_argument(
        "layer_path",
        help="Path to the BSP layer directory to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code on any issue found",
    )
    parser.add_argument(
        "--check",
        choices=[
            "syntax",
            "deps",
            "compat",
            "bbappend",
            "conf",
            "priority",
            "includes",
        ],
        help="Run only a specific check",
    )

    args = parser.parse_args()
    layer_path = os.path.abspath(args.layer_path)

    if not os.path.isdir(layer_path):
        print(f"Error: '{layer_path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Validating layer: {layer_path}\n")

    if args.check:
        check_map = {
            "syntax": ("Recipe syntax", check_recipe_syntax),
            "deps": ("Dependency references", check_dependencies),
            "compat": ("Layer series compatibility", check_layerseries_compat),
            "bbappend": ("BBAPPEND targets", check_bbappend_targets),
            "conf": ("Configuration variables", check_conf_variables),
            "priority": ("Layer priority", check_layer_priority),
            "includes": ("Missing includes", check_missing_includes),
        }
        name, func = check_map[args.check]
        print(f"Running: {name}...")
        errors = func(layer_path)
        if errors:
            print(f"  Found {len(errors)} issue(s):")
            for err in errors:
                print(f"    - {err}")
        else:
            print("  OK")
    else:
        errors = validate_layer(layer_path)

    print(f"\nTotal issues: {len(errors)}")

    if args.strict and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
