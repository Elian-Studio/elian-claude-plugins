#!/usr/bin/env python3
"""Render a kanban board.json into the self-contained kanban-board-template.html.

Stdlib only. Validates cross-references (list->card, card->member, card->label)
before rendering so a dangling id fails loudly here instead of rendering as a
silently blank chip in the browser.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = SCRIPT_DIR.parent / "assets" / "kanban-board-template.html"
PLACEHOLDER = "__BOARD_DATA_JSON__"
VALID_THEMES = {"cobalt", "sage", "grape"}


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "board"


def validate(data):
    errors = []

    if not isinstance(data.get("title"), str) or not data["title"].strip():
        errors.append("top-level 'title' must be a non-empty string")

    lists = data.get("lists")
    if not isinstance(lists, list) or not lists:
        errors.append("top-level 'lists' must be a non-empty array")
        lists = []

    cards = data.get("cards")
    if not isinstance(cards, dict):
        errors.append("top-level 'cards' must be an object keyed by card id")
        cards = {}

    members = data.get("members", [])
    labels = data.get("labels", [])
    member_ids = {m.get("id") for m in members if isinstance(m, dict)}
    label_ids = {l.get("id") for l in labels if isinstance(l, dict)}

    list_ids = set()
    card_owner = {}
    for i, lst in enumerate(lists):
        if not isinstance(lst, dict) or not lst.get("id") or not lst.get("title"):
            errors.append(f"lists[{i}] must have 'id' and 'title'")
            continue
        if lst["id"] in list_ids:
            errors.append(f"duplicate list id '{lst['id']}'")
        list_ids.add(lst["id"])
        for cid in lst.get("cardIds", []):
            if cid not in cards:
                errors.append(f"list '{lst['id']}' references unknown card id '{cid}'")
            elif cid in card_owner:
                errors.append(f"card '{cid}' appears in both list '{card_owner[cid]}' and '{lst['id']}'")
            else:
                card_owner[cid] = lst["id"]

    for cid, card in cards.items():
        if not isinstance(card, dict) or not card.get("title"):
            errors.append(f"cards['{cid}'] must have a non-empty 'title'")
            continue
        assignee = card.get("assignee")
        if assignee is not None and assignee not in member_ids:
            errors.append(f"cards['{cid}'].assignee '{assignee}' is not in members[]")
        for lid in card.get("labels", []) or []:
            if lid not in label_ids:
                errors.append(f"cards['{cid}'].labels references unknown label id '{lid}'")
        if cid not in card_owner:
            errors.append(f"cards['{cid}'] is not referenced by any list (orphan card)")

    theme = data.get("theme", "cobalt")
    if theme not in VALID_THEMES:
        errors.append(f"theme '{theme}' must be one of {sorted(VALID_THEMES)}")

    return errors


def build(data_path: Path, out_path: Path, template_path: Path):
    data = json.loads(data_path.read_text(encoding="utf-8"))

    errors = validate(data)
    if errors:
        print("board.json failed validation:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    data.setdefault("id", slugify(data["title"]))
    data.setdefault("theme", "cobalt")
    data.setdefault("members", [])
    data.setdefault("labels", [])

    template = template_path.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        print(
            f"template must contain exactly one {PLACEHOLDER} placeholder, "
            f"found {template.count(PLACEHOLDER)} in {template_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    json_text = json.dumps(data, ensure_ascii=False)
    # Avoid a literal "</script" inside the JSON prematurely closing the
    # embedding <script> tag when this gets parsed as HTML.
    json_text = re.sub(r"</(script)", r"<\\/\1", json_text, flags=re.IGNORECASE)

    out_html = template.replace(PLACEHOLDER, json_text)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_html, encoding="utf-8")
    print(f"wrote {out_path} (board id: {data['id']})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path, help="path to board.json")
    parser.add_argument("--out", required=True, type=Path, help="path to write board.html")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="template html to render into")
    args = parser.parse_args()

    if not args.data.exists():
        print(f"no such data file: {args.data}", file=sys.stderr)
        sys.exit(1)
    if not args.template.exists():
        print(f"no such template file: {args.template}", file=sys.stderr)
        sys.exit(1)

    build(args.data, args.out, args.template)


if __name__ == "__main__":
    main()
