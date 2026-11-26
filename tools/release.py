#!/usr/bin/env python3
"""Cut a release: set the version everywhere, commit, and tag vX.Y.Z.

    python3 tools/release.py 0.3.0          # commit + tag locally
    python3 tools/release.py 0.3.0 --push   # ...and push main and the tag

Claude Code reads the version from .claude-plugin/plugin.json and only offers
users an update when it changes, so the tag and that field must always agree.
The release workflow in .github/workflows/release.yml checks this on push.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
PYPROJECT = ROOT / "pyproject.toml"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def fail(msg: str) -> None:
    sys.exit(f"release: {msg}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    push = "--push" in sys.argv[1:]
    if len(args) != 1 or not SEMVER.match(args[0]):
        fail("usage: tools/release.py X.Y.Z [--push]")
    version = args[0]
    tag = f"v{version}"

    if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
        fail("releases are cut from main; check it out first")
    if git("status", "--porcelain"):
        fail("working tree is not clean; commit or stash first")
    if git("tag", "--list", tag):
        fail(f"tag {tag} already exists")

    plugin = json.loads(PLUGIN_JSON.read_text())
    current = plugin.get("version", "0.0.0")
    if tuple(map(int, version.split("."))) <= tuple(map(int, current.split("."))):
        fail(f"{version} is not newer than the current version {current}")

    plugin["version"] = version
    PLUGIN_JSON.write_text(json.dumps(plugin, indent=2) + "\n")
    PYPROJECT.write_text(
        re.sub(r'(?m)^version = ".*"$', f'version = "{version}"', PYPROJECT.read_text(), count=1)
    )

    git("add", str(PLUGIN_JSON), str(PYPROJECT))
    git("commit", "-m", f"Release {tag}")
    git("tag", "-a", tag, "-m", f"Release {tag}")
    print(f"Committed and tagged {tag} (was {current}).")

    if push:
        git("push", "origin", "main", tag)
        print(f"Pushed main and {tag}.")
    else:
        print(f"Push with: git push origin main {tag}")


if __name__ == "__main__":
    main()
