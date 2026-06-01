#!/usr/bin/env python3
"""Install or update the awesome-design-md skill into Antigravity.

Usage:
    python scripts/install_to_antigravity.py
    python scripts/install_to_antigravity.py --antigravity-home "C:/Users/me/.gemini/antigravity"
    python scripts/install_to_antigravity.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "references" / "templates"
SKILL_MD_SOURCE = SKILL_DIR / "SKILL.md"

DEFAULT_ANTIGRAVITY_HOME = Path.home() / ".gemini" / "antigravity"
TARGET_SKILL_NAME = "awesome-design-md"


def detect_antigravity_home() -> Path:
    env = os.environ.get("ANTIGRAVITY_HOME")
    if env:
        return Path(env).resolve()
    if DEFAULT_ANTIGRAVITY_HOME.exists():
        return DEFAULT_ANTIGRAVITY_HOME
    raise FileNotFoundError(
        f"Cannot find Antigravity home directory. "
        f"Tried $ANTIGRAVITY_HOME and {DEFAULT_ANTIGRAVITY_HOME}. "
        f"Use --antigravity-home to specify the path."
    )


def generate_antigravity_skill_md(template_count: int) -> str:
    """Generate a SKILL.md tailored for Antigravity's directory layout."""
    brands_section = ""
    try:
        manifest = json.loads(TEMPLATES_DIR.joinpath("manifest.json").read_text("utf-8"))
        categories: dict[str, list[str]] = {}
        # Group by rough category based on description keywords
        for entry in manifest:
            brands_section += ""  # We'll just list all brands
        brand_list = ", ".join(e["brand"] for e in manifest)
    except Exception:
        brand_list = "(run sync to populate)"

    return f"""---
name: awesome-design-md
description: Use when the user wants to build a web page, landing page, dashboard, or UI component that matches a real-world brand's visual identity. Provides {template_count} complete DESIGN.md files (Google Stitch format) with exact color palettes, typography rules, component specifications, shadow systems, layout principles, and responsive behavior. All data is local Markdown in the resources/ directory — no API or network access needed.
---

# Awesome Design MD

## Overview

A fully local AI-native design system skill. Contains {template_count} brand DESIGN.md templates (Google Stitch format), each a complete design specification document. Read the Markdown directly to generate pixel-accurate UI. No Figma, no JSON schema, no API needed.

Source: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)

## When to Use

- User asks to build a page that "looks like X brand" (e.g., "Stripe-style page", "Apple's design language")
- User needs high-quality, brand-inspired Web design instead of generic templates
- User needs a complete visual system for a Web project (colors, fonts, shadows, component specs)
- User mentions DESIGN.md, Google Stitch, or getdesign
- Do NOT force-apply when the user is doing normal feature dev, bug fixes, or scripting

## Available Brands

{brand_list}

## How to Apply

1. Match brand based on user's request. If unspecified, recommend based on project type (fintech→stripe, dev tools→vercel/cursor, content→notion).
2. Read the `resources/<brand>.md` file.
3. Each file has 9 standard sections:
   - `## 1. Visual Theme & Atmosphere` — overall aesthetics
   - `## 2. Color Palette & Roles` — exact hex/rgba values
   - `## 3. Typography Rules` — font family, size, weight
   - `## 4. Component Stylings` — buttons, cards, badges, inputs
   - `## 5. Layout Principles` — spacing, grid, whitespace
   - `## 6. Depth & Elevation` — shadow system
   - `## 7. Do's and Don'ts` — brand guardrails
   - `## 8. Responsive Behavior` — breakpoints and collapse strategy
   - `## 9. Agent Prompt Guide` — quick reference and example prompts
4. Apply tokens directly to output HTML/CSS/React code.
5. Mixing is allowed: Brand A typography + Brand B palette, but explain.

## Quick Reference — Popular Brands

| Brand | Slug | Vibe |
|-------|------|------|
| Stripe | stripe | Signature purple gradients, weight-300 elegance |
| Apple | apple | Premium whitespace, SF Pro, cinematic imagery |
| Vercel | vercel | Black-white precision, Geist font |
| Linear | linear.app | Ultra-minimal, precise, purple |
| Notion | notion | Warm minimalism, serif headings |
| SpaceX | spacex | Black-white, full-bleed images, futuristic |
| Nike | nike | Monochrome UI, massive uppercase Futura |
| Spotify | spotify | Green-on-dark, bold typography |
| Tesla | tesla | Radical subtraction, cinematic photography |
| Supabase | supabase | Dark emerald, code-first |
| Cursor | cursor | Dark interface, gradient accents |
| Framer | framer | Bold black-blue, motion-first |

## Risks and Misuse

- Do not force-apply brand design systems during pure functional dev/bug fixes
- Do not paste entire DESIGN.md to user — extract only tokens needed for current task
- Do not claim these are official design systems — they are reference docs extracted from public CSS
- Brand fonts (e.g., sohne-var, SF Pro) may not be freely available — remind user to use fallbacks

## Security & Privacy

- No code execution, no network requests
- All data from local resources/ directory Markdown files
- No API keys or environment variables needed
- No data collection or upload
"""


def install(antigravity_home: Path, dry_run: bool = False) -> int:
    skills_dir = antigravity_home / "skills"
    target_dir = skills_dir / TARGET_SKILL_NAME
    target_resources = target_dir / "resources"

    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    manifest_path = TEMPLATES_DIR / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}. Run sync_upstream.py first.", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text("utf-8"))
    template_count = len(manifest)

    if dry_run:
        print(f"[DRY RUN] Would install {template_count} templates to {target_dir}")
        print(f"[DRY RUN] Would write SKILL.md to {target_dir / 'SKILL.md'}")
        print(f"[DRY RUN] Would copy templates to {target_resources}")
        return 0

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_md_content = generate_antigravity_skill_md(template_count)
    (target_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")
    print(f"Wrote SKILL.md ({template_count} brands)")

    # Copy templates to resources/ (Antigravity convention)
    if target_resources.exists():
        shutil.rmtree(target_resources)
    shutil.copytree(TEMPLATES_DIR, target_resources)
    print(f"Copied {template_count} templates to {target_resources}")

    print(f"\nInstalled awesome-design-md skill to: {target_dir}")
    print("Restart Antigravity to activate.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install awesome-design-md into Antigravity.")
    parser.add_argument(
        "--antigravity-home",
        help=f"Path to Antigravity home directory (default: {DEFAULT_ANTIGRAVITY_HOME})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    args = parser.parse_args()

    try:
        home = Path(args.antigravity_home) if args.antigravity_home else detect_antigravity_home()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return install(home.resolve(), dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
