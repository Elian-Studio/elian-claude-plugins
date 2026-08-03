#!/usr/bin/env python3
"""
build_doc.py — assemble a self-contained, house-styled HTML document.

Why this exists: every document should look like it came from the same desk.
Claude writes content in Markdown (its strength); this script renders it with
the fixed house stylesheet inlined into a single portable .html file. Rich
components (callouts, KPI tiles, cards, comparison grids) can be dropped into
the Markdown as raw HTML — the converter passes block-level HTML through
untouched, so you get both Markdown's ergonomics and bespoke layout.

Zero external dependencies on purpose: stdlib only, so it runs anywhere and
never trips supply-chain release-age policies.

Usage:
    python build_doc.py CONTENT.md --title "Document title" [options]

Options:
    --title TEXT        Document title. If omitted, the first '# H1' in the
                        Markdown is used (and removed from the body).
    --subtitle TEXT     One-line subtitle under the title.
    --meta "k=v"        Repeatable meta chip, e.g. --meta "Date=2026-06-07".
                        A bare "--meta value" renders a value-only chip.
    --toc               Insert an auto table of contents (from H2/H3).
    --lang CODE         <html lang>. Default: ko.
    --out PATH          Output file. Default: <slug-of-title>.html in cwd.
    --css PATH          Override stylesheet. Default: ../assets/house-style.css.
    --body-html PATH    Use a raw HTML body fragment instead of Markdown.
    --selftest          Run an internal conversion self-check and exit.
"""

import argparse
import html
import os
import re
import sys

# ----------------------------------------------------------------------------
# Inline Markdown
# ----------------------------------------------------------------------------

def _slug(text, used):
    s = re.sub(r"<[^>]+>", "", text)          # drop any tags
    s = s.strip().lower()
    s = re.sub(r"[^\w가-힣\- ]", "", s)  # keep word chars, hangul, dash, space
    s = re.sub(r"\s+", "-", s).strip("-")
    if not s:
        s = "section"
    base, n = s, 1
    while s in used:
        n += 1
        s = f"{base}-{n}"
    used.add(s)
    return s


_UNSAFE_URL_SCHEME = re.compile(r"^\s*(?:javascript|vbscript|data):", re.I)


def _safe_url(url):
    """Escape a URL for an HTML attribute and drop script-capable schemes.

    Without this, a Markdown link like [x](a"onclick="alert(1)) breaks out of
    the href attribute, and [x](javascript:alert(1)) yields a clickable script
    URL — both are XSS in the rendered document.
    """
    if _UNSAFE_URL_SCHEME.match(url):
        return ""
    return html.escape(url, quote=True)


def inline(text):
    """Convert inline Markdown to HTML. Inline raw HTML is passed through."""
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    # 1) code spans first, so their contents are never re-formatted
    text = re.sub(r"`([^`]+)`", stash, text)

    # 2) images, then links
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
        lambda m: f'<img src="{_safe_url(m.group(2))}" alt="{html.escape(m.group(1))}"'
                  + (f' title="{html.escape(m.group(3))}"' if m.group(3) else "")
                  + ">",
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
        lambda m: f'<a href="{_safe_url(m.group(2))}"'
                  + (f' title="{html.escape(m.group(3))}"' if m.group(3) else "")
                  + f">{m.group(1)}</a>",
        text,
    )

    # 3) emphasis — bold before italic so ** is consumed first
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)

    # 4) restore code spans (escaped)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: f"<code>{html.escape(spans[int(m.group(1))])}</code>",
                  text)
    return text


# ----------------------------------------------------------------------------
# Block-level Markdown
# ----------------------------------------------------------------------------

CALLOUT = {
    "NOTE":      ("callout-note",   "📝", "Note"),
    "TIP":       ("callout-tip",    "💡", "Tip"),
    "IMPORTANT": ("callout-note",   "📌", "Important"),
    "WARNING":   ("callout-warn",   "⚠️", "Warning"),
    "CAUTION":   ("callout-danger", "🚫", "Caution"),
    "INFO":      ("callout-info",   "ℹ️", "Info"),
}

HTML_BLOCK_START = re.compile(r"^\s*<([a-zA-Z][\w-]*)")
VOID_TAGS = {"img", "hr", "br", "input", "meta", "link", "source"}
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # split on unescaped pipes
    cells, buf, esc = [], "", False
    for ch in line:
        if esc:
            buf += ch; esc = False
        elif ch == "\\":
            buf += ch; esc = True
        elif ch == "|":
            cells.append(buf); buf = ""
        else:
            buf += ch
    cells.append(buf)
    return [c.strip() for c in cells]


def _aligns(sep):
    out = []
    for c in _split_row(sep):
        l, r = c.startswith(":"), c.endswith(":")
        out.append("center" if l and r else "right" if r else "left" if l else "")
    return out


def _list_block(lines, used):
    """Render a (possibly nested) list from consecutive list lines."""
    items = []  # (indent, ordered, content)
    for ln in lines:
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
        indent = len(m.group(1).replace("\t", "    "))
        ordered = not m.group(2)[0] in "-*+"
        items.append((indent, ordered, m.group(3)))

    def build(idx, base_indent):
        ordered = items[idx][1]
        tag = "ol" if ordered else "ul"
        html_out = [f"<{tag}>"]
        i = idx
        while i < len(items):
            indent, _, content = items[i]
            if indent < base_indent:
                break
            if indent > base_indent:
                i = i  # handled by recursion below
                break
            li = inline(content)
            # nested children?
            j = i + 1
            if j < len(items) and items[j][0] > base_indent:
                child_html, j = build(j, items[j][0])
                li += child_html
            html_out.append(f"<li>{li}</li>")
            i = j
        html_out.append(f"</{tag}>")
        return "".join(html_out), i

    out, _ = build(0, items[0][0])
    return out


def render_markdown(md, used_ids):
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]

        # blank
        if not line.strip():
            i += 1
            continue

        # fenced code block
        fence = re.match(r"^\s*(`{3,}|~{3,})\s*([\w+-]*)\s*$", line)
        if fence:
            marker, lang = fence.group(1)[0] * 3, fence.group(2)
            buf, i = [], i + 1
            while i < n and not re.match(rf"^\s*{re.escape(marker)}", lines[i]):
                buf.append(lines[i]); i += 1
            i += 1  # closing fence
            if lang:
                out.append(f'<div class="code-label">{html.escape(lang)}</div>')
            out.append(f"<pre><code>{html.escape(chr(10).join(buf))}</code></pre>")
            continue

        # raw block-level HTML — pass through, tracking tag balance
        hm = HTML_BLOCK_START.match(line)
        if hm:
            tag = hm.group(1).lower()
            buf = [line]
            if tag in VOID_TAGS or re.search(r"/>\s*$", line):
                out.append(line); i += 1
                continue
            opens = len(re.findall(rf"<{tag}\b", line, re.I))
            closes = len(re.findall(rf"</{tag}>", line, re.I))
            i += 1
            while i < n and opens > closes:
                buf.append(lines[i])
                opens += len(re.findall(rf"<{tag}\b", lines[i], re.I))
                closes += len(re.findall(rf"</{tag}>", lines[i], re.I))
                i += 1
            out.append("\n".join(buf))
            continue

        # heading
        hm = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if hm:
            level, text = len(hm.group(1)), inline(hm.group(2))
            if level in (2, 3):
                sid = _slug(hm.group(2), used_ids)
                out.append(f'<h{level} id="{sid}">{text}</h{level}>')
            else:
                out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # table
        if "|" in line and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            header = _split_row(line)
            aligns = _aligns(lines[i + 1])
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(_split_row(lines[i])); i += 1
            t = ["<table><thead><tr>"]
            for k, h in enumerate(header):
                a = f' style="text-align:{aligns[k]}"' if k < len(aligns) and aligns[k] else ""
                t.append(f"<th{a}>{inline(h)}</th>")
            t.append("</tr></thead><tbody>")
            for row in body:
                t.append("<tr>")
                for k, c in enumerate(row):
                    a = f' style="text-align:{aligns[k]}"' if k < len(aligns) and aligns[k] else ""
                    t.append(f"<td{a}>{inline(c)}</td>")
                t.append("</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # blockquote / callout
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            cm = re.match(r"^\[!(\w+)\]\s*(.*)$", buf[0]) if buf else None
            if cm and cm.group(1).upper() in CALLOUT:
                cls, ico, default_lead = CALLOUT[cm.group(1).upper()]
                rest = ([cm.group(2)] if cm.group(2).strip() else []) + buf[1:]
                inner = render_markdown("\n".join(rest), used_ids)
                out.append(
                    f'<div class="callout {cls}"><span class="ico">{ico}</span>'
                    f'<div class="body">{inner}</div></div>'
                )
            else:
                inner = render_markdown("\n".join(buf), used_ids)
                out.append(f"<blockquote>{inner}</blockquote>")
            continue

        # list
        if re.match(r"^\s*([-*+]|\d+[.)])\s+", line):
            buf = []
            while i < n and (re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i])
                             or (lines[i].strip() and lines[i].startswith((" ", "\t")))):
                buf.append(lines[i]); i += 1
            out.append(_list_block(buf, used_ids))
            continue

        # paragraph
        buf = []
        while i < n and lines[i].strip() and not _para_break(lines[i], lines, i):
            buf.append(lines[i]); i += 1
        text = " ".join(s.strip() for s in buf)
        out.append(f"<p>{inline(text)}</p>")

    return "\n".join(out)


def _para_break(line, lines, i):
    """A paragraph ends when the next line starts a new block construct."""
    if re.match(r"^\s*(#{1,6})\s", line):
        return True
    if HTML_BLOCK_START.match(line):
        return True
    if re.match(r"^\s*(`{3,}|~{3,})", line):
        return True
    if re.match(r"^\s*([-*+]|\d+[.)])\s+", line):
        return True
    if line.lstrip().startswith(">"):
        return True
    if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
        return True
    if "|" in line and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]):
        return True
    return False


# ----------------------------------------------------------------------------
# Document assembly
# ----------------------------------------------------------------------------

def build_toc(body_html, lang="ko"):
    heads = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h[23]>', body_html, re.S)
    if not heads:
        return ""
    label = "목차" if lang.lower().startswith("ko") else "Contents"
    items = [f'<nav class="toc"><div class="toc-title">{label}</div><ul>']
    for level, sid, text in heads:
        text = re.sub(r"<[^>]+>", "", text)
        cls = "lvl-3" if level == "3" else "lvl-2"
        items.append(f'<li class="{cls}"><a href="#{sid}">{text}</a></li>')
    items.append("</ul></nav>")
    return "\n".join(items)


def build_header(title, subtitle, metas):
    parts = ['<header class="doc-header">', f"<h1>{inline(title)}</h1>"]
    if subtitle:
        parts.append(f'<p class="subtitle">{inline(subtitle)}</p>')
    if metas:
        chips = []
        for m in metas:
            if "=" in m:
                k, v = m.split("=", 1)
                chips.append(f'<span class="tag"><b>{html.escape(k.strip())}</b> {html.escape(v.strip())}</span>')
            else:
                chips.append(f'<span class="tag">{html.escape(m.strip())}</span>')
        parts.append('<div class="doc-meta">' + "".join(chips) + "</div>")
    parts.append("</header>")
    return "\n".join(parts)


def assemble(title, subtitle, metas, body_html, css, lang, toc):
    toc_html = build_toc(body_html, lang) if toc else ""
    page = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(re.sub(r'<[^>]+>', '', title))}</title>
<style>
{css}
</style>
</head>
<body>
<main class="doc">
{build_header(title, subtitle, metas)}
{toc_html}
{body_html}
</main>
</body>
</html>
"""
    return page


def default_css():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "assets", "house-style.css")


def run(args):
    used_ids = set()

    if args.body_html:
        with open(args.body_html, encoding="utf-8") as f:
            body = f.read()
        title = args.title or "Document"
    else:
        with open(args.content, encoding="utf-8") as f:
            md = f.read()
        title = args.title
        if not title:
            m = re.search(r"^#\s+(.*)$", md, re.M)
            if m:
                title = m.group(1).strip()
                md = md[: m.start()] + md[m.end():]
            else:
                title = "Document"
        body = render_markdown(md, used_ids)

    with open(args.css or default_css(), encoding="utf-8") as f:
        css = f.read()

    page = assemble(title, args.subtitle, args.meta or [], body,
                    css, args.lang, args.toc)

    out = args.out
    if not out:
        out = _slug(title, set()) + ".html"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(out)
    return out


def selftest():
    md = """# 제목
일부 **굵게** 와 *기울임* 그리고 `code` 와 [링크](https://x.io).

## 섹션 하나
- 항목 1
- 항목 2
  - 중첩 2-1

> [!WARNING]
> 조심하세요.

| A | B |
|---|--:|
| 1 | 2 |

```python
print("hi")
```

<div class="kpi-grid">
  <div class="kpi"><div class="num">42</div><div class="label">things</div></div>
</div>
"""
    ids = set()
    body = render_markdown(md, ids)
    checks = {
        "bold": "<strong>굵게</strong>" in body,
        "italic": "<em>기울임</em>" in body,
        "code": "<code>code</code>" in body,
        "link": '<a href="https://x.io">링크</a>' in body,
        "nested list": "<ul><li>중첩 2-1</li></ul>" in body,
        "callout": 'class="callout callout-warn"' in body,
        "table align": 'style="text-align:right"' in body,
        "code block": "<pre><code>print(&quot;hi&quot;)" in body,
        "raw html passthrough": '<div class="kpi-grid">' in body,
        "heading id": '<h2 id=' in body,
    }
    css_path = default_css()
    page = assemble("제목", "부제", ["작성일=2026-06-07", "리포트"], body,
                    open(css_path, encoding="utf-8").read(), "ko", True)
    checks["toc built"] = '<nav class="toc">' in page
    checks["meta chip"] = "작성일" in page
    checks["self-contained css"] = "--accent" in page

    ok = all(checks.values())
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print("SELFTEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description="Build a house-styled self-contained HTML document.")
    p.add_argument("content", nargs="?", help="Markdown content file")
    p.add_argument("--title")
    p.add_argument("--subtitle")
    p.add_argument("--meta", action="append")
    p.add_argument("--toc", action="store_true")
    p.add_argument("--lang", default="ko")
    p.add_argument("--out")
    p.add_argument("--css")
    p.add_argument("--body-html", dest="body_html")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not args.content and not args.body_html:
        p.error("provide a Markdown content file or --body-html")
    run(args)


if __name__ == "__main__":
    main()
