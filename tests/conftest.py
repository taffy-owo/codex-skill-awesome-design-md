"""Shared fixtures for awesome-design-md tests."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "awesome-design-md"
TEMPLATES_DIR = SKILL_DIR / "references" / "templates"
MANIFEST_PATH = TEMPLATES_DIR / "manifest.json"

SAMPLE_MANIFEST = [
    {
        "brand": "vercel",
        "file": "vercel.md",
        "description": "Frontend deployment. Black and white precision, Geist font.",
        "templateHash": "sha256:aaa",
        "sourceCommit": "abc123",
        "sourceUpdatedAt": "2026-04-09T18:04:01+03:00",
    },
    {
        "brand": "stripe",
        "file": "stripe.md",
        "description": "Payment infrastructure. Signature purple gradients, weight-300 elegance.",
        "templateHash": "sha256:bbb",
        "sourceCommit": "def456",
        "sourceUpdatedAt": "2026-04-09T18:04:01+03:00",
    },
    {
        "brand": "linear.app",
        "file": "linear.app.md",
        "description": "Project management. Ultra-minimal, precise, purple accent.",
        "templateHash": "sha256:ccc",
        "sourceCommit": "ghi789",
        "sourceUpdatedAt": "2026-04-09T18:04:01+03:00",
    },
    {
        "brand": "x.ai",
        "file": "x.ai.md",
        "description": "Elon Musk's AI lab. Stark monochrome, futuristic minimalism.",
        "templateHash": "sha256:ddd",
        "sourceCommit": "jkl012",
        "sourceUpdatedAt": "2026-04-09T18:04:01+03:00",
    },
]


@pytest.fixture()
def tmp_templates(tmp_path: Path) -> Path:
    """Create a temporary templates directory with sample manifest and files."""
    templates_dir = tmp_path / "references" / "templates"
    templates_dir.mkdir(parents=True)

    manifest_path = templates_dir / "manifest.json"
    manifest_path.write_text(json.dumps(SAMPLE_MANIFEST, indent=2), encoding="utf-8")

    for entry in SAMPLE_MANIFEST:
        md_file = templates_dir / entry["file"]
        md_file.write_text(
            f"# {entry['brand']} DESIGN.md\n\n{entry['description']}\n",
            encoding="utf-8",
        )

    return tmp_path


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory for install tests."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir(parents=True)
    return project_dir


@pytest.fixture()
def real_manifest() -> list[dict]:
    """Load the real manifest from the skill directory."""
    if not MANIFEST_PATH.exists():
        pytest.skip("Real manifest not found — run sync first")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
