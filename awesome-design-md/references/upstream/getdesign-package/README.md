# getdesign.md

> A CLI for dropping `DESIGN.md` files into your project so your AI coding agent has a real design system to follow.

`DESIGN.md` is a single markdown file that captures a visual language (colors, type scale, spacing, components, motion) in a format that Cursor, Claude Code, v0, Lovable, Windsurf, and other agents read easily. Hand it to your agent before you ask for UI, and the output stops looking generic.

Browse the full catalog at **[getdesign.md](https://getdesign.md)**.

## Quick start

```bash
npx getdesign list
npx getdesign add <slug>
```

`list` shows every available template. `add` writes `./DESIGN.md` at your project root using the slug you pick. Then tell your coding agent:

> Read `DESIGN.md` before writing any UI. Match the tokens, type scale, and component patterns defined there.

That's the whole flow.

## Install

No install needed. `npx` is the recommended entry point:

```bash
npx getdesign add <slug>
```

If you'd rather have it on your `PATH`:

```bash
npm install -g getdesign
```

Requires Node.js 18 or newer.

## Commands

### `add <slug>`

Install a template to your project root as `DESIGN.md`.

```bash
npx getdesign add <slug>
```

Slugs are listed by `npx getdesign list` or on [getdesign.md/design-md](https://getdesign.md/design-md).

If a `DESIGN.md` already exists at the root, the new template is saved into a nested folder (e.g. `<slug>/DESIGN.md`) so nothing is overwritten by accident. Use `--force` to replace, or `--out` to pick a custom path.

### `list`

Print every available template with a one-line description.

```bash
npx getdesign list
```

## Options

| Flag | Description |
|---|---|
| `--force` | Overwrite the existing `DESIGN.md` at the target path |
| `--out <path>` | Write to a custom path instead of the project root |

Examples:

```bash
npx getdesign add <slug> --force
npx getdesign add <slug> --out ./docs/design.md
```

## What's in a DESIGN.md?

Each template is an original, independently authored synthesis of a visual style. Inside, you'll find:

- **Color tokens**: surface, ink, accent, semantic, with hex values and the role each plays
- **Type scale**: display, heading, body, label sizes with line-height and tracking
- **Spacing & layout**: grid, gutters, container widths, component padding
- **Component patterns**: buttons, cards, navs, forms, modals, described in prose your agent can apply
- **Motion**: durations, easings, hover and entrance patterns
- **Responsive strategy**: how the system collapses across breakpoints

These are **inspiration files**, not official design systems. They're written to give AI agents a concrete style to anchor against, so your output has a point of view instead of defaulting to generic tailwind.

## Browse the catalog

The full catalog with previews and the underlying markdown lives at **[getdesign.md/design-md](https://getdesign.md/design-md)**.

Templates span product, marketing, dev-tool, fintech, marketplace, fashion, automotive, and consumer-electronics looks. Run `npx getdesign list` to see every available slug.

## How to use it with your AI agent

The TL;DR: tell your agent to read `DESIGN.md` first.

**Cursor / Windsurf / Claude Code**

Add this to your project rules or system prompt:

> Before writing or changing any UI in this project, read `DESIGN.md` at the root. Match the tokens, type scale, spacing, and component patterns defined there. Treat it as the source of truth for visual decisions.

**v0 / Lovable / Bolt**

Paste the contents of `DESIGN.md` at the start of your prompt, or upload it as a reference file. Then describe the screen you want.

**ChatGPT / Claude (web)**

Attach `DESIGN.md` to the conversation and reference it: *"Using the design system in the attached file, build a pricing page..."*


