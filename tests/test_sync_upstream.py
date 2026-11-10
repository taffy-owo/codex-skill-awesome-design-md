"""Tests for the sync_upstream.py helper functions."""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the scripts directory to sys.path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "awesome-design-md" / "scripts"))

import sync_upstream
from sync_upstream import (
    SKILL_DIR,
    ensure_within,
    resolve_executable,
    skill_relative,
)


# ---------------------------------------------------------------------------
# resolve_executable tests
# ---------------------------------------------------------------------------


class TestResolveExecutable:
    def test_finds_python(self):
        result = resolve_executable("python")
        assert result is not None
        assert "python" in result.lower()

    def test_finds_git(self):
        result = resolve_executable("git")
        assert result is not None

    def test_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError, match="Could not find executable"):
            resolve_executable("this_definitely_does_not_exist_xyz_42")


# ---------------------------------------------------------------------------
# skill_relative tests
# ---------------------------------------------------------------------------


class TestSkillRelative:
    def test_relative_to_skill_dir(self):
        target = SKILL_DIR / "references" / "templates" / "vercel.md"
        result = skill_relative(target)
        assert result == "references/templates/vercel.md"

    def test_uses_posix_separators(self):
        target = SKILL_DIR / "scripts" / "apply_template.py"
        result = skill_relative(target)
        assert "\\" not in result
        assert result == "scripts/apply_template.py"


# ---------------------------------------------------------------------------
# ensure_within tests
# ---------------------------------------------------------------------------


class TestEnsureWithin:
    def test_valid_path(self, tmp_path: Path):
        child = tmp_path / "subdir" / "file.txt"
        # Should not raise
        ensure_within(tmp_path, child)

    def test_path_outside_base_raises(self, tmp_path: Path):
        outside = tmp_path.parent / "outside" / "file.txt"
        with pytest.raises(ValueError):
            ensure_within(tmp_path, outside)

    def test_same_path(self, tmp_path: Path):
        # Path is the base itself — should be valid
        ensure_within(tmp_path, tmp_path)


# ---------------------------------------------------------------------------
# SKILL_DIR validation
# ---------------------------------------------------------------------------


class TestModulePaths:
    def test_skill_dir_exists(self):
        assert SKILL_DIR.exists(), f"SKILL_DIR does not exist: {SKILL_DIR}"

    def test_skill_dir_has_skill_md(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_dir_has_scripts(self):
        assert (SKILL_DIR / "scripts").is_dir()

    def test_skill_dir_has_references(self):
        assert (SKILL_DIR / "references").is_dir()


@pytest.fixture()
def package_archive(tmp_path: Path):
    def write_package(
        filename: str = "sample.md",
        template_hash: str | None = None,
        template_bytes: bytes = b"# Sample design\n\nA verified template.\n",
    ) -> Path:
        manifest = [{
            "brand": "sample",
            "file": filename,
            "description": "Sample design",
            "templateHash": template_hash or "sha256:" + hashlib.sha256(template_bytes).hexdigest(),
        }]
        archive_path = tmp_path / "getdesign-test.tgz"
        archive_files = {
            "package/package.json": b'{"version": "1.0.0"}',
            "package/templates/manifest.json": json.dumps(manifest).encode(),
            f"package/templates/{filename}": template_bytes,
            "package/templates/unlisted.md": b"Not part of the published manifest",
            "package/bin/cli.mjs": b"Unneeded upstream executable",
            "../../outside.txt": b"Must never be extracted",
        }
        with tarfile.open(archive_path, "w:gz") as archive:
            for member_name, member_bytes in archive_files.items():
                member = tarfile.TarInfo(member_name)
                member.size = len(member_bytes)
                archive.addfile(member, io.BytesIO(member_bytes))
        return archive_path

    return write_package


@pytest.fixture()
def isolated_sync(tmp_path: Path, monkeypatch):
    skill_dir = tmp_path / "skill"
    templates_dir = skill_dir / "references" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "previous.md").write_text("Previous template", encoding="utf-8")
    monkeypatch.setattr(sync_upstream, "SKILL_DIR", skill_dir)
    monkeypatch.setattr(sync_upstream, "TEMPLATES_DIR", templates_dir)
    monkeypatch.setattr(sync_upstream, "UPSTREAM_DIR", skill_dir / "references" / "upstream")
    monkeypatch.setattr(sync_upstream, "SOURCES_PATH", sync_upstream.UPSTREAM_DIR / "sources.json")
    return templates_dir


def mock_package_download(monkeypatch, archive_path: Path) -> None:
    def download_package(command, cwd, capture):
        assert "--ignore-scripts" in command
        shutil.copyfile(archive_path, cwd / archive_path.name)
        return subprocess.CompletedProcess(command, 0, stdout=archive_path.name + "\n")

    monkeypatch.setattr(sync_upstream, "run", download_package)


def test_sync_publishes_only_manifest_templates(package_archive, isolated_sync, monkeypatch):
    mock_package_download(monkeypatch, package_archive())

    assert sync_upstream.sync_package() == ("1.0.0", "getdesign-test.tgz")
    assert {path.name for path in isolated_sync.iterdir()} == {"sample.md", "manifest.json"}
    assert {path.relative_to(sync_upstream.SKILL_DIR).as_posix()
            for path in sync_upstream.SKILL_DIR.rglob("*") if path.is_file()} == {
        "references/templates/sample.md", "references/templates/manifest.json",
    }


@pytest.mark.parametrize("filename", ["../escape.md", "nested/escape.md", "C:escape.md", "nested\\escape.md"])
def test_sync_rejects_unsafe_paths_before_replacing_library(
    filename, package_archive, isolated_sync, monkeypatch,
):
    mock_package_download(monkeypatch, package_archive(filename=filename))

    with pytest.raises(ValueError, match="Invalid upstream template filename"):
        sync_upstream.sync_package()
    assert (isolated_sync / "previous.md").read_text(encoding="utf-8") == "Previous template"


def test_sync_rejects_corrupt_template_before_replacing_library(
    package_archive, isolated_sync, monkeypatch,
):
    mock_package_download(monkeypatch, package_archive(template_hash="sha256:incorrect"))

    with pytest.raises(ValueError, match="hash mismatch"):
        sync_upstream.sync_package()
    assert (isolated_sync / "previous.md").exists()


def test_unchanged_sources_do_not_create_weekly_changes(isolated_sync):
    (isolated_sync / "manifest.json").write_text('[{"brand": "sample"}]', encoding="utf-8")
    sync_upstream.write_sources("abc123", "1.0.0", "getdesign-1.0.0.tgz")
    previous_sources = sync_upstream.SOURCES_PATH.read_bytes()

    sync_upstream.write_sources("abc123", "1.0.0", "getdesign-1.0.0.tgz")

    assert sync_upstream.SOURCES_PATH.read_bytes() == previous_sources
    assert b"snapshotPath" not in previous_sources


def test_vercel_weight_correction_records_original_hash(package_archive, isolated_sync, monkeypatch):
    published_template = b"typography:\n  label-sm:\n    fontWeight: 500 burada komikledin mi yani son DESIGN.md'leri? \n"
    published_hash = "sha256:" + hashlib.sha256(published_template).hexdigest()
    monkeypatch.setattr(sync_upstream, "VERCEL_0626_HASH", published_hash)
    mock_package_download(monkeypatch, package_archive(filename="vercel.md", template_bytes=published_template))

    sync_upstream.sync_package()

    corrected_template = (isolated_sync / "vercel.md").read_bytes()
    assert corrected_template == b"typography:\n  label-sm:\n    fontWeight: 500\n"
    published_entry = json.loads((isolated_sync / "manifest.json").read_text(encoding="utf-8"))[0]
    assert published_entry["upstreamTemplateHash"] == published_hash
    assert published_entry["templateHash"] == "sha256:" + hashlib.sha256(corrected_template).hexdigest()


def test_bundled_templates_match_recorded_hashes():
    templates_dir = SKILL_DIR / "references" / "templates"
    manifest = json.loads((templates_dir / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest:
        template_bytes = (templates_dir / entry["file"]).read_bytes()
        assert "sha256:" + hashlib.sha256(template_bytes).hexdigest() == entry["templateHash"], entry["brand"]
