"""Tests for the sync_upstream.py helper functions."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the scripts directory to sys.path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "awesome-design-md" / "scripts"))

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
