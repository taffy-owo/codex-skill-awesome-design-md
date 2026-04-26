---
name: awesome-design-md
description: Use when the user wants a DESIGN.md file, wants a frontend to match a known product aesthetic like Vercel, Linear, Notion, Stripe, or Apple, or wants to browse and install the local awesome-design-md template library backed by the official getdesign package.
---

# Awesome Design MD

## Overview

This skill installs and applies locally vendored `DESIGN.md` templates from the official `getdesign` package. Use it for frontend redesigns, landing pages, dashboards, or component work when the user wants a specific brand-inspired visual system or asks for a `DESIGN.md`.

## When to use this skill

- The user asks for a `DESIGN.md`.
- The user asks to make a page look like a known product or brand.
- The user wants a curated design direction before you implement UI.
- The user wants to browse, list, or install templates from the awesome-design-md library.

## Core workflow

### 1. Pick the right template

- If the user names a brand, resolve it with `python scripts/apply_template.py list`.
- If the user describes a vibe instead of a brand, shortlist 2-4 candidates from `references/templates/manifest.json` and explain the tradeoffs briefly.
- Do not load every template into context. Read only the chosen template file from `references/templates/<brand>.md`.

### 2. Install `DESIGN.md` into the target project

- Run `python scripts/apply_template.py install <brand> --project <project-root>`.
- By default this writes `<project-root>/DESIGN.md`.
- Do not overwrite an existing `DESIGN.md` unless the user explicitly wants replacement or you pass `--force`.

### 3. Use the template during implementation

- Read the installed `DESIGN.md` before changing UI.
- Treat the template as directional guidance, not a reason to break product semantics, accessibility, or the existing information architecture.
- Preserve an established design system unless the user asked for a stronger visual reset.

### 4. Refresh upstream when needed

- Run `python scripts/sync_upstream.py` from this skill directory to refresh:
  - the GitHub mirror of `VoltAgent/awesome-design-md`
  - the official `getdesign` npm package snapshot
  - the locally vendored template set in `references/templates/`

## Fast selection guide

- Developer infra and precise monochrome: `vercel`, `hashicorp`, `replicate`, `warp`, `ibm`
- Minimal SaaS and productivity: `linear.app`, `notion`, `mintlify`, `cal`
- Dark AI and builder products: `claude`, `cursor`, `supabase`, `raycast`, `resend`
- Motion-heavy or marketing-forward: `framer`, `stripe`, `clay`, `spotify`, `renault`
- Editorial or luxury: `apple`, `tesla`, `ferrari`, `bugatti`, `airbnb`

## Local resources

- Template manifest: `references/templates/manifest.json`
- Actual templates: `references/templates/*.md`
- Upstream GitHub snapshot: `references/upstream/github-repo/`
- Upstream `getdesign` package snapshot: `references/upstream/getdesign-package/`
- Source metadata from the last sync: `references/upstream/sources.json`

## Commands

```bash
python scripts/apply_template.py list
python scripts/apply_template.py install vercel --project /path/to/app
python scripts/apply_template.py install linear --project /path/to/app
python scripts/apply_template.py install stripe --out /path/to/app/docs/DESIGN.md
python scripts/sync_upstream.py
```

## Notes

- The GitHub repository currently mirrors template entries but not the full template bodies, so the official `getdesign` npm package is the authoritative source for actual template content.
- The install script supports aliases such as `linear -> linear.app`, `mistral -> mistral.ai`, and `xai -> x.ai`.
