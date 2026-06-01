"""Tests for the apply_template.py CLI script."""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the scripts directory to sys.path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "awesome-design-md" / "scripts"))

from apply_template import (
    ALIASES,
    TemplateEntry,
    build_index,
    build_parser,
    load_manifest,
    normalize_token,
    resolve_brand,
)


# ---------------------------------------------------------------------------
# normalize_token tests
# ---------------------------------------------------------------------------


class TestNormalizeToken:
    def test_basic(self):
        assert normalize_token("Stripe") == "stripe"

    def test_with_dots(self):
        assert normalize_token("linear.app") == "linearapp"

    def test_with_spaces(self):
        assert normalize_token("  Hello World  ") == "helloworld"

    def test_with_special_chars(self):
        assert normalize_token("x.ai-lab_2") == "xailab2"

    def test_empty(self):
        assert normalize_token("") == ""

    def test_already_normalized(self):
        assert normalize_token("vercel") == "vercel"


# ---------------------------------------------------------------------------
# TemplateEntry tests
# ---------------------------------------------------------------------------


class TestTemplateEntry:
    def test_creation(self):
        entry = TemplateEntry(
            brand="vercel",
            file="vercel.md",
            description="Frontend deployment.",
        )
        assert entry.brand == "vercel"
        assert entry.file == "vercel.md"
        assert entry.template_hash is None

    def test_path_property(self):
        entry = TemplateEntry(brand="stripe", file="stripe.md", description="Payments.")
        assert entry.path.name == "stripe.md"
        assert "templates" in str(entry.path)

    def test_frozen(self):
        entry = TemplateEntry(brand="test", file="test.md", description="Test.")
        with pytest.raises(AttributeError):
            entry.brand = "other"


# ---------------------------------------------------------------------------
# build_index tests
# ---------------------------------------------------------------------------


class TestBuildIndex:
    def test_index_by_brand(self):
        entries = [
            TemplateEntry(brand="linear.app", file="linear.app.md", description="PM."),
        ]
        index = build_index(entries)
        assert "linear.app" in index
        assert "linearapp" in index

    def test_multiple_entries(self):
        entries = [
            TemplateEntry(brand="vercel", file="vercel.md", description="Deploy."),
            TemplateEntry(brand="stripe", file="stripe.md", description="Pay."),
        ]
        index = build_index(entries)
        assert "vercel" in index
        assert "stripe" in index


# ---------------------------------------------------------------------------
# resolve_brand tests
# ---------------------------------------------------------------------------


class TestResolveBrand:
    @pytest.fixture()
    def entries(self):
        return [
            TemplateEntry(brand="vercel", file="vercel.md", description="Deploy."),
            TemplateEntry(brand="stripe", file="stripe.md", description="Pay."),
            TemplateEntry(brand="linear.app", file="linear.app.md", description="PM."),
            TemplateEntry(brand="x.ai", file="x.ai.md", description="AI."),
        ]

    def test_exact_match(self, entries):
        result = resolve_brand("vercel", entries)
        assert result.brand == "vercel"

    def test_case_insensitive(self, entries):
        result = resolve_brand("Vercel", entries)
        assert result.brand == "vercel"

    def test_alias_linear(self, entries):
        result = resolve_brand("linear", entries)
        assert result.brand == "linear.app"

    def test_alias_xai(self, entries):
        result = resolve_brand("xai", entries)
        assert result.brand == "x.ai"

    def test_unknown_brand(self, entries):
        with pytest.raises(ValueError, match="unknown brand"):
            resolve_brand("nonexistent", entries)

    def test_empty_brand(self, entries):
        with pytest.raises(ValueError, match="brand cannot be empty"):
            resolve_brand("", entries)

    def test_whitespace_brand(self, entries):
        with pytest.raises(ValueError, match="brand cannot be empty"):
            resolve_brand("   ", entries)

    def test_partial_match_unique(self, entries):
        result = resolve_brand("verc", entries)
        assert result.brand == "vercel"

    def test_partial_match_ambiguous(self):
        entries = [
            TemplateEntry(brand="foobar-alpha", file="foobar-alpha.md", description="Alpha."),
            TemplateEntry(brand="foobar-beta", file="foobar-beta.md", description="Beta."),
        ]
        with pytest.raises(ValueError, match="ambiguous brand"):
            resolve_brand("foobar", entries)


# ---------------------------------------------------------------------------
# ALIASES tests
# ---------------------------------------------------------------------------


class TestAliases:
    def test_all_aliases_are_lowercase(self):
        for key, value in ALIASES.items():
            assert key == key.lower(), f"Alias key '{key}' is not lowercase"

    def test_known_aliases(self):
        assert ALIASES["linear"] == "linear.app"
        assert ALIASES["xai"] == "x.ai"
        assert ALIASES["mistral"] == "mistral.ai"
        assert ALIASES["together"] == "together.ai"
        assert ALIASES["opencode"] == "opencode.ai"


# ---------------------------------------------------------------------------
# load_manifest tests (using real manifest)
# ---------------------------------------------------------------------------


class TestLoadManifest:
    def test_loads_real_manifest(self, real_manifest):
        entries = load_manifest()
        assert len(entries) >= 69  # at least the original count
        brands = {e.brand for e in entries}
        assert "vercel" in brands
        assert "stripe" in brands
        assert "apple" in brands

    def test_entries_have_required_fields(self, real_manifest):
        entries = load_manifest()
        for entry in entries:
            assert entry.brand, "brand must not be empty"
            assert entry.file, "file must not be empty"
            assert entry.description, "description must not be empty"

    def test_all_template_files_exist(self, real_manifest):
        entries = load_manifest()
        for entry in entries:
            assert entry.path.exists(), f"Template file missing: {entry.path}"


# ---------------------------------------------------------------------------
# command_list tests (integration)
# ---------------------------------------------------------------------------


class TestCommandList:
    def test_list_text_output(self, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["list"])
        captured = StringIO()
        with patch("sys.stdout", captured):
            result = args.func(args)
        assert result == 0
        output = captured.getvalue()
        assert "vercel" in output
        assert "stripe" in output

    def test_list_json_output(self, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["list", "--json"])
        captured = StringIO()
        with patch("sys.stdout", captured):
            result = args.func(args)
        assert result == 0
        data = json.loads(captured.getvalue())
        assert isinstance(data, list)
        assert len(data) >= 69
        brands = {item["brand"] for item in data}
        assert "vercel" in brands

    def test_list_with_match(self, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["list", "--match", "stripe"])
        captured = StringIO()
        with patch("sys.stdout", captured):
            result = args.func(args)
        assert result == 0
        output = captured.getvalue()
        assert "stripe" in output
        # vercel should not be in the output since we're filtering
        assert "vercel" not in output


# ---------------------------------------------------------------------------
# command_install tests (integration)
# ---------------------------------------------------------------------------


class TestCommandInstall:
    def test_install_to_project(self, tmp_project, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["install", "vercel", "--project", str(tmp_project)])
        result = args.func(args)
        assert result == 0
        design_md = tmp_project / "DESIGN.md"
        assert design_md.exists()
        content = design_md.read_text(encoding="utf-8")
        assert len(content) > 100

    def test_install_with_out_path(self, tmp_project, real_manifest):
        out_path = tmp_project / "docs" / "DESIGN.md"
        parser = build_parser()
        args = parser.parse_args(["install", "stripe", "--out", str(out_path)])
        result = args.func(args)
        assert result == 0
        assert out_path.exists()

    def test_install_refuses_overwrite_without_force(self, tmp_project, real_manifest):
        design_md = tmp_project / "DESIGN.md"
        design_md.write_text("existing content", encoding="utf-8")
        parser = build_parser()
        args = parser.parse_args(["install", "vercel", "--project", str(tmp_project)])
        captured = StringIO()
        with patch("sys.stderr", captured):
            result = args.func(args)
        assert result == 1
        assert design_md.read_text(encoding="utf-8") == "existing content"

    def test_install_with_force(self, tmp_project, real_manifest):
        design_md = tmp_project / "DESIGN.md"
        design_md.write_text("existing content", encoding="utf-8")
        parser = build_parser()
        args = parser.parse_args(["install", "vercel", "--project", str(tmp_project), "--force"])
        result = args.func(args)
        assert result == 0
        assert design_md.read_text(encoding="utf-8") != "existing content"

    def test_install_alias(self, tmp_project, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["install", "linear", "--project", str(tmp_project)])
        result = args.func(args)
        assert result == 0
        assert (tmp_project / "DESIGN.md").exists()

    def test_install_unknown_brand(self, tmp_project, real_manifest):
        parser = build_parser()
        args = parser.parse_args(["install", "nonexistent", "--project", str(tmp_project)])
        captured = StringIO()
        with patch("sys.stderr", captured):
            result = args.func(args)
        assert result == 1
