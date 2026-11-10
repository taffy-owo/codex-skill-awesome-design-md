# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- 13 templates from `getdesign@0.6.26`: `1win`, `aljazeera`, `discord`, `dji`, `jobright`, `mercury`, `mobbin`, `mydealz`, `nerdwallet`, `nintendo-2001`, `oracle`, `oura`, and `sap` (73 → 86 templates)
- Lightweight SVG banner and six illustrative design studies for the bilingual README
- Sync regression coverage for manifest-only publishing, unsafe paths, content hashes, and unchanged source metadata
- **Test suite** — `pytest` tests for `apply_template.py` and `sync_upstream.py` (`tests/`)
- **GitHub Actions CI** — automated testing on push/PR across Python 3.10–3.12 and Ubuntu/Windows (`.github/workflows/test.yml`)
- **Automated upstream sync** — weekly GitHub Actions workflow that creates PRs when templates change (`.github/workflows/sync-upstream.yml`)
- **Antigravity installer** — `scripts/install_to_antigravity.py` for one-command skill installation
- New brands from upstream: `bmw-m`, `dell-1996`, `hp`, `slack`

### Changed
- Refreshed Notion and Vercel templates from `getdesign@0.6.26`
- Corrected stray prose in the published Vercel `fontWeight` token at the import boundary; the manifest retains its original upstream hash
- Reorganized both READMEs around previews, working repository-root commands, and product-focused template selection
- Upstream sync stages downloads temporarily and publishes only verified manifest templates plus source metadata; scheduled PRs use an explicit file allowlist
- **Upstream sync** — templates updated from `getdesign@0.6.8` to `0.6.21` (69 → 73 templates)
- All existing templates updated with upstream v2 content improvements
- Updated README and README_EN with multi-platform installation instructions

### Removed
- Duplicate upstream GitHub and npm package snapshots (about 5 MB); template content remains in `references/templates/`

## [0.1.0] — 2026-04-26

### Added
- Initial release with 69 brand DESIGN.md templates
- `apply_template.py` CLI — `list` and `install` commands with alias support
- `sync_upstream.py` — upstream sync from VoltAgent GitHub repo and `getdesign` npm package
- OpenAI Agent YAML configuration
- Bilingual README (中文 / English)
