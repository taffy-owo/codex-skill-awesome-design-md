<div align="center">

# 🎨 Codex Skill: Awesome Design MD

**Give your AI coding assistant brand-level design intuition**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Templates](https://img.shields.io/badge/Brand_Templates-73-blueviolet)](awesome-design-md/references/templates/)
[![Upstream](https://img.shields.io/badge/Upstream-VoltAgent%2Fawesome--design--md-orange)](https://github.com/VoltAgent/awesome-design-md)
[![CI](https://github.com/taffy-owo/codex-skill-awesome-design-md/actions/workflows/test.yml/badge.svg)](https://github.com/taffy-owo/codex-skill-awesome-design-md/actions/workflows/test.yml)

**English** | [中文](README.md)

</div>

---

## 📖 About

A standalone, publishable [Codex](https://github.com/openai/codex) skill package that enables your AI coding assistant to automatically apply complete design specifications (`DESIGN.md`) from **73 well-known brands** when generating frontend UI — instead of generic default styling.

Each `DESIGN.md` follows the [Google Stitch](https://github.com/nicepkg/nice-getdesign) format with 9 standardized sections:

| # | Section | Content |
|---|---------|---------|
| 1 | Visual Theme & Atmosphere | Overall visual style and aesthetic tone |
| 2 | Color Palette & Roles | Exact HEX / RGBA values and usage rules |
| 3 | Typography Rules | Font families, sizes, weights |
| 4 | Component Stylings | Buttons, cards, inputs, etc. |
| 5 | Layout Principles | Spacing, grids, whitespace system |
| 6 | Depth & Elevation | Shadow and layer hierarchy |
| 7 | Do's and Don'ts | Brand design guardrails |
| 8 | Responsive Behavior | Breakpoints and responsive strategy |
| 9 | Agent Prompt Guide | AI-specific quick reference |

## ✨ Highlights

- 🏢 **73 Brands** — Covering AI, dev tools, SaaS, fintech, automotive, consumer tech, and more
- 📦 **Fully Local** — No API keys, no network access. Pure Markdown, ready to use
- 🔧 **CLI Tools** — `list` / `install` one-command operations
- 🔄 **Upstream Sync** — Script auto-fetches latest templates from VoltAgent repo and `getdesign` npm package
- 🤖 **Multi-Agent Support** — Includes OpenAI Agent YAML config
- ✅ **CI/CD** — GitHub Actions for automated testing + weekly upstream sync
- 🧪 **Test Coverage** — pytest unit and integration tests

## 🏷️ Supported Brands

<details>
<summary>View all 73 brands</summary>

### AI & LLM Platforms
`claude` · `cohere` · `elevenlabs` · `minimax` · `mistral.ai` · `ollama` · `opencode.ai` · `replicate` · `runwayml` · `together.ai` · `voltagent` · `x.ai`

### Dev Tools & IDEs
`cursor` · `expo` · `lovable` · `raycast` · `superhuman` · `vercel` · `warp`

### Backend, Databases & DevOps
`clickhouse` · `composio` · `hashicorp` · `mongodb` · `posthog` · `sanity` · `sentry` · `supabase`

### Productivity & SaaS
`cal` · `intercom` · `linear.app` · `mintlify` · `notion` · `resend` · `zapier`

### Design & Creative Tools
`airtable` · `clay` · `figma` · `framer` · `miro` · `webflow`

### Fintech & Crypto
`binance` · `coinbase` · `kraken` · `mastercard` · `revolut` · `stripe` · `wise`

### Collaboration & Communication
`slack`

### E-commerce & Retail
`airbnb` · `meta` · `nike` · `shopify` · `starbucks`

### Media & Consumer Tech
`apple` · `dell-1996` · `hp` · `ibm` · `nvidia` · `pinterest` · `playstation` · `spacex` · `spotify` · `theverge` · `uber` · `vodafone` · `wired`

### Automotive
`bmw` · `bmw-m` · `bugatti` · `ferrari` · `lamborghini` · `renault` · `tesla`

</details>

## 🚀 Installation

### Option 1: Via Codex built-in skill-installer

```bash
python <CODEX_HOME>/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo taffy-owo/codex-skill-awesome-design-md \
  --path awesome-design-md
```

### Option 2: Direct GitHub URL (Codex)

```bash
python <CODEX_HOME>/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/taffy-owo/codex-skill-awesome-design-md/tree/main/awesome-design-md
```

### Option 3: Antigravity (Gemini)

```bash
python awesome-design-md/scripts/install_to_antigravity.py
# Or specify a custom path:
python awesome-design-md/scripts/install_to_antigravity.py --antigravity-home ~/.gemini/antigravity
```

### Option 4: Manual Install (Universal)

Copy the `awesome-design-md/` directory into your AI coding assistant's skills directory.

Restart your AI coding assistant after installation to activate the skill.

## 📋 Usage

### List available templates

```bash
python scripts/apply_template.py list
python scripts/apply_template.py list --match stripe   # fuzzy search
python scripts/apply_template.py list --json            # JSON output
```

### Install a template into your project

```bash
# Install Vercel style to a project
python scripts/apply_template.py install vercel --project /path/to/app

# Install Linear style to a specific output path
python scripts/apply_template.py install linear --out /path/to/app/docs/DESIGN.md

# Force overwrite an existing DESIGN.md
python scripts/apply_template.py install stripe --project . --force
```

Aliases are supported: `linear` → `linear.app`, `mistral` → `mistral.ai`, `xai` → `x.ai`, etc.

### Sync upstream updates

```bash
python scripts/sync_upstream.py
```

Automatically fetches the latest templates from the VoltAgent GitHub repo and the `getdesign` npm package.

## 🗂️ Repository Structure

```
.
├── awesome-design-md/              # Codex skill directory (install this)
│   ├── SKILL.md                    # Skill definition file
│   ├── agents/
│   │   └── openai.yaml             # OpenAI Agent integration config
│   ├── scripts/
│   │   ├── apply_template.py       # Template list / install CLI
│   │   ├── sync_upstream.py        # Upstream sync script
│   │   └── install_to_antigravity.py  # Antigravity install script
│   └── references/
│       ├── templates/              # 73 DESIGN.md templates + manifest.json
│       └── upstream/               # Upstream snapshots and sync metadata
├── tests/                          # pytest test suite
├── .github/workflows/              # CI/CD workflows
│   ├── test.yml                    # Automated testing
│   └── sync-upstream.yml           # Weekly upstream sync
├── CHANGELOG.md                    # Change log
├── LICENSE
├── README.md                       # Chinese version (main)
└── README_EN.md                    # ← You are here (English)
```

## 🎯 Quick Selection Guide

| Style Direction | Recommended Brands |
|----------------|-------------------|
| Developer Infrastructure / Precise Monochrome | `vercel` · `hashicorp` · `replicate` · `warp` · `ibm` |
| Minimal SaaS / Productivity | `linear.app` · `notion` · `mintlify` · `cal` |
| Dark AI / Builder Products | `claude` · `cursor` · `supabase` · `raycast` · `resend` |
| Motion-Heavy / Marketing-Forward | `framer` · `stripe` · `clay` · `spotify` · `renault` |
| Editorial / Luxury | `apple` · `tesla` · `ferrari` · `bugatti` · `airbnb` |

## 📄 License

This project is licensed under the [MIT License](LICENSE).

Template content is derived from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) and the official [`getdesign`](https://www.npmjs.com/package/getdesign) npm package.

## 🙏 Acknowledgments

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — Original brand design template collection
- [getdesign](https://www.npmjs.com/package/getdesign) — Official npm package, authoritative source for template content
- [OpenAI Codex](https://github.com/openai/codex) — AI coding assistant platform
