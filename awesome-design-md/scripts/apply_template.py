#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "references" / "templates"
MANIFEST_PATH = TEMPLATES_DIR / "manifest.json"

ALIASES = {
    "linear": "linear.app",
    "linear-app": "linear.app",
    "mistral": "mistral.ai",
    "mistral-ai": "mistral.ai",
    "opencode": "opencode.ai",
    "opencode-ai": "opencode.ai",
    "together": "together.ai",
    "together-ai": "together.ai",
    "xai": "x.ai",
    "x-ai": "x.ai",
}


@dataclass(frozen=True)
class TemplateEntry:
    brand: str
    file: str
    description: str
    template_hash: str | None = None
    source_commit: str | None = None
    source_updated_at: str | None = None

    @property
    def path(self) -> Path:
        return TEMPLATES_DIR / self.file


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def normalize_token(value: str) -> str:
    chars: list[str] = []
    for ch in value.strip().lower():
        if ch.isalnum():
            chars.append(ch)
    return "".join(chars)


def load_manifest() -> list[TemplateEntry]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries: list[TemplateEntry] = []
    for item in raw:
        entries.append(
            TemplateEntry(
                brand=item["brand"],
                file=item["file"],
                description=item["description"],
                template_hash=item.get("templateHash"),
                source_commit=item.get("sourceCommit"),
                source_updated_at=item.get("sourceUpdatedAt"),
            )
        )
    return entries


def build_index(entries: Iterable[TemplateEntry]) -> dict[str, TemplateEntry]:
    index: dict[str, TemplateEntry] = {}
    for entry in entries:
        normalized_brand = normalize_token(entry.brand)
        normalized_file = normalize_token(Path(entry.file).stem)
        index[entry.brand.lower()] = entry
        index[normalized_brand] = entry
        index[normalized_file] = entry
    return index


def resolve_brand(query: str, entries: list[TemplateEntry]) -> TemplateEntry:
    if not query.strip():
        raise ValueError("brand cannot be empty")

    alias = ALIASES.get(query.strip().lower(), query.strip())
    index = build_index(entries)

    exact = index.get(alias.lower()) or index.get(normalize_token(alias))
    if exact:
        return exact

    normalized_query = normalize_token(alias)
    partial_matches = [
        entry
        for entry in entries
        if normalized_query
        and normalized_query in normalize_token(entry.brand)
    ]
    if len(partial_matches) == 1:
        return partial_matches[0]
    if len(partial_matches) > 1:
        brands = ", ".join(entry.brand for entry in partial_matches)
        raise ValueError(f"ambiguous brand '{query}'. Matches: {brands}")

    raise ValueError(f"unknown brand '{query}'")


def command_list(args: argparse.Namespace) -> int:
    entries = load_manifest()
    filtered = entries
    if args.match:
        token = normalize_token(args.match)
        filtered = [
            entry
            for entry in entries
            if token in normalize_token(entry.brand)
            or token in normalize_token(entry.description)
        ]

    if args.json:
        payload = [
            {
                "brand": entry.brand,
                "file": entry.file,
                "description": entry.description,
                "templateHash": entry.template_hash,
                "sourceCommit": entry.source_commit,
                "sourceUpdatedAt": entry.source_updated_at,
            }
            for entry in filtered
        ]
        print(json.dumps(payload, indent=2))
        return 0

    for entry in filtered:
        print(f"{entry.brand}\t{entry.description}")
    return 0


def target_path_from_args(args: argparse.Namespace) -> Path:
    if args.out:
        return Path(args.out).expanduser().resolve()
    project_dir = Path(args.project).expanduser().resolve()
    return project_dir / "DESIGN.md"


def command_install(args: argparse.Namespace) -> int:
    entries = load_manifest()
    try:
        entry = resolve_brand(args.brand, entries)
    except ValueError as exc:
        return fail(str(exc))

    source_path = entry.path
    if not source_path.exists():
        return fail(f"template file not found: {source_path}")

    target_path = target_path_from_args(args)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists() and not args.force:
        return fail(f"target already exists: {target_path}. Re-run with --force to overwrite.")

    shutil.copyfile(source_path, target_path)
    print(f"Installed {entry.brand} -> {target_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List and install locally vendored DESIGN.md templates.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available templates.")
    list_parser.add_argument("--match", help="Filter by brand or description.")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    list_parser.set_defaults(func=command_list)

    install_parser = subparsers.add_parser("install", help="Install a template as DESIGN.md.")
    install_parser.add_argument("brand", help="Brand slug or alias, for example 'vercel' or 'linear'.")
    install_parser.add_argument(
        "--project",
        default=".",
        help="Project root used when writing the default DESIGN.md path.",
    )
    install_parser.add_argument(
        "--out",
        help="Explicit output file path. Overrides --project for the destination.",
    )
    install_parser.add_argument("--force", action="store_true", help="Overwrite an existing target file.")
    install_parser.set_defaults(func=command_install)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
