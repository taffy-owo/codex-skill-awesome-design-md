#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
CODEX_HOME = SKILL_DIR.parent.parent
REFERENCES_DIR = SKILL_DIR / "references"
UPSTREAM_DIR = REFERENCES_DIR / "upstream"
TEMPLATES_DIR = REFERENCES_DIR / "templates"
VENDOR_IMPORTS_DIR = CODEX_HOME / "vendor_imports"
GITHUB_REPO_DIR = VENDOR_IMPORTS_DIR / "awesome-design-md"
GITHUB_SNAPSHOT_DIR = UPSTREAM_DIR / "github-repo"
PACKAGE_SNAPSHOT_DIR = UPSTREAM_DIR / "getdesign-package"
SOURCES_PATH = UPSTREAM_DIR / "sources.json"

REPO_URL = "https://github.com/VoltAgent/awesome-design-md.git"
REPO_BRANCH = "main"
PACKAGE_SPEC = "getdesign@latest"


def resolve_executable(name: str) -> str:
    candidates = [name]
    if os.name == "nt":
        candidates = [f"{name}.cmd", f"{name}.exe", name]

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    raise FileNotFoundError(f"Could not find executable: {name}")


GIT_BIN = resolve_executable("git")
NPM_BIN = resolve_executable("npm")


def run(command: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=capture,
    )


def skill_relative(path: Path) -> str:
    return path.resolve().relative_to(SKILL_DIR.resolve()).as_posix()


def codex_home_relative(path: Path) -> str:
    return path.resolve().relative_to(CODEX_HOME.resolve()).as_posix()


def ensure_within(base: Path, target: Path) -> None:
    target.resolve().relative_to(base.resolve())


def replace_tree(src: Path, dst: Path, ignore=None) -> None:
    ensure_within(SKILL_DIR, dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore)


def replace_file(src: Path, dst: Path) -> None:
    ensure_within(SKILL_DIR, dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def sync_github_repo() -> str:
    GITHUB_REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    if GITHUB_REPO_DIR.exists():
        run([GIT_BIN, "-C", str(GITHUB_REPO_DIR), "fetch", "--all", "--tags", "--prune"])
        run([GIT_BIN, "-C", str(GITHUB_REPO_DIR), "checkout", REPO_BRANCH])
        run([GIT_BIN, "-C", str(GITHUB_REPO_DIR), "pull", "--ff-only", "origin", REPO_BRANCH])
    else:
        run([GIT_BIN, "clone", "--branch", REPO_BRANCH, REPO_URL, str(GITHUB_REPO_DIR)])

    sha = run([GIT_BIN, "-C", str(GITHUB_REPO_DIR), "rev-parse", "HEAD"], capture=True).stdout.strip()
    replace_tree(GITHUB_REPO_DIR, GITHUB_SNAPSHOT_DIR, ignore=shutil.ignore_patterns(".git"))
    return sha


def sync_package() -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="awesome-design-md-sync-") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        tarball_name = run(
            [NPM_BIN, "pack", "--silent", PACKAGE_SPEC],
            cwd=temp_dir,
            capture=True,
        ).stdout.strip().splitlines()[-1]
        tarball_path = temp_dir / tarball_name
        extract_dir = temp_dir / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(tarball_path, "r:gz") as archive:
            archive.extractall(extract_dir)

        package_root = extract_dir / "package"
        package_json = json.loads((package_root / "package.json").read_text(encoding="utf-8"))
        version = str(package_json["version"])

        replace_tree(package_root, PACKAGE_SNAPSHOT_DIR)
        replace_tree(package_root / "templates", TEMPLATES_DIR)
        return version, tarball_name


def write_sources(github_sha: str, package_version: str, tarball_name: str) -> None:
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((TEMPLATES_DIR / "manifest.json").read_text(encoding="utf-8"))
    payload = {
        "syncedAt": datetime.now(timezone.utc).isoformat(),
        "github": {
            "repoUrl": REPO_URL,
            "branch": REPO_BRANCH,
            "mirrorPath": codex_home_relative(GITHUB_REPO_DIR),
            "snapshotPath": skill_relative(GITHUB_SNAPSHOT_DIR),
            "commit": github_sha,
        },
        "package": {
            "spec": PACKAGE_SPEC,
            "version": package_version,
            "tarball": tarball_name,
            "snapshotPath": skill_relative(PACKAGE_SNAPSHOT_DIR),
        },
        "templates": {
            "path": skill_relative(TEMPLATES_DIR),
            "count": len(manifest),
        },
    }
    SOURCES_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
    github_sha = sync_github_repo()
    package_version, tarball_name = sync_package()
    write_sources(github_sha, package_version, tarball_name)
    manifest = json.loads((TEMPLATES_DIR / "manifest.json").read_text(encoding="utf-8"))
    print(f"GitHub mirror synced at {github_sha}")
    print(f"getdesign package synced at {package_version}")
    print(f"Vendored {len(manifest)} templates into {TEMPLATES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
