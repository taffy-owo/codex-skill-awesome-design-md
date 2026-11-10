#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"
UPSTREAM_DIR = REFERENCES_DIR / "upstream"
TEMPLATES_DIR = REFERENCES_DIR / "templates"
SOURCES_PATH = UPSTREAM_DIR / "sources.json"

REPO_URL = "https://github.com/VoltAgent/awesome-design-md.git"
REPO_BRANCH = "main"
PACKAGE_SPEC = "getdesign@latest"
VERCEL_0626_HASH = "sha256:12d363de1be5656965c0dffc127dab1763d44970d0caf86feee887ad46073127"


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


def ensure_within(base: Path, target: Path) -> None:
    target.resolve().relative_to(base.resolve())


def replace_tree(src: Path, dst: Path) -> None:
    ensure_within(SKILL_DIR, dst)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def fetch_github_commit() -> str:
    remote_ref = run(
        [GIT_BIN, "ls-remote", "--exit-code", REPO_URL, f"refs/heads/{REPO_BRANCH}"],
        capture=True,
    ).stdout
    return remote_ref.split()[0]


def sync_package() -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix="awesome-design-md-sync-") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        tarball_name = run(
            [NPM_BIN, "pack", "--silent", "--ignore-scripts", PACKAGE_SPEC],
            cwd=temp_dir,
            capture=True,
        ).stdout.strip().splitlines()[-1]
        tarball_path = temp_dir / tarball_name
        staged_templates = temp_dir / "templates"
        staged_templates.mkdir()

        with tarfile.open(tarball_path, "r:gz") as archive:
            package_json = json.load(archive.extractfile("package/package.json"))
            manifest_bytes = archive.extractfile("package/templates/manifest.json").read()
            manifest = json.loads(manifest_bytes)
            if not manifest:
                raise ValueError("Upstream template manifest is empty")
            filenames = set()
            for entry in manifest:
                filename = entry["file"]
                if (
                    "/" in filename
                    or "\\" in filename
                    or ":" in filename
                    or not filename.endswith(".md")
                    or filename in filenames
                ):
                    raise ValueError(f"Invalid upstream template filename: {filename}")
                filenames.add(filename)
                member = archive.getmember(f"package/templates/{filename}")
                if not member.isfile():
                    raise ValueError(f"Upstream template must be a regular file: {filename}")
                template_bytes = archive.extractfile(member).read()
                template_hash = "sha256:" + hashlib.sha256(template_bytes).hexdigest()
                if template_hash != entry["templateHash"]:
                    raise ValueError(f"Upstream template hash mismatch: {filename}")
                # This published Vercel revision contains stray prose in a numeric weight.
                # Match its full hash so future upstream revisions pass through unchanged.
                if template_hash == VERCEL_0626_HASH:
                    template_bytes = template_bytes.replace(
                        b"    fontWeight: 500 burada komikledin mi yani son DESIGN.md'leri? \n",
                        b"    fontWeight: 500\n",
                    )
                    entry["upstreamTemplateHash"] = template_hash
                    entry["templateHash"] = "sha256:" + hashlib.sha256(template_bytes).hexdigest()
                (staged_templates / filename).write_bytes(template_bytes)
            manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            (staged_templates / "manifest.json").write_bytes(manifest_bytes)

        version = str(package_json["version"])
        replace_tree(staged_templates, TEMPLATES_DIR)
        return version, tarball_name


def write_sources(github_sha: str, package_version: str, tarball_name: str) -> None:
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((TEMPLATES_DIR / "manifest.json").read_text(encoding="utf-8"))
    payload = {
        "github": {
            "repoUrl": REPO_URL,
            "branch": REPO_BRANCH,
            "commit": github_sha,
        },
        "package": {
            "spec": PACKAGE_SPEC,
            "version": package_version,
            "tarball": tarball_name,
        },
        "templates": {
            "path": skill_relative(TEMPLATES_DIR),
            "count": len(manifest),
        },
    }
    if SOURCES_PATH.exists():
        previous_sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
        previous_sources.pop("syncedAt", None)
        if previous_sources == payload:
            return
    payload = {"syncedAt": datetime.now(timezone.utc).isoformat(), **payload}
    SOURCES_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
    github_sha = fetch_github_commit()
    package_version, tarball_name = sync_package()
    write_sources(github_sha, package_version, tarball_name)
    manifest = json.loads((TEMPLATES_DIR / "manifest.json").read_text(encoding="utf-8"))
    print(f"GitHub source recorded at {github_sha}")
    print(f"getdesign package synced at {package_version}")
    print(f"Vendored {len(manifest)} templates into {TEMPLATES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
