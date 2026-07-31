#!/usr/bin/env python3
"""render_before_after.py — Notion-look tabbed before/after HTML viewer.

Stdlib only — no build step, no Python dependencies. The output is a single
index.html with two tabs (Before / After) styled like Notion.

It is NOT fully self-contained: ```mermaid blocks are rendered by the mermaid
library loaded from a CDN, because vendoring it would add megabytes to every
report. The version is pinned exactly and carries an SRI hash, so a swapped CDN
payload fails to execute instead of running. Everything else (CSS, fonts, layout)
is inlined. Offline or under a strict CSP the page still opens and reads
correctly — diagrams degrade to their source with a visible notice rather than
failing silently.

Page bodies are untrusted: anyone with edit access to the source page writes
them, and the maintainer opens the result locally. Markdown is escaped, HTML
(inline blocks and .html inputs alike) goes through sanitize_html(), and mermaid
runs with securityLevel 'strict'.

Usage:
  render_before_after.py --after after.md --title "KEY-123 — worker delegation" --out out/index.html
  render_before_after.py --before before.html --after after.html --title "..." --out out/index.html

--before / --after accept a .md (Notion-flavored markdown subset) or .html
fragment. --before is optional (omit for after-only). /issue-close calls this
when an issue is closed.
"""
import argparse
import html
import re
import sys
from html.parser import HTMLParser

CSS = r"""
  :root{
    --text: rgb(55,53,47); --text-light: rgba(55,53,47,.65); --text-faint: rgba(55,53,47,.4);
    --border: rgb(233,233,231); --border-strong: rgb(221,221,219); --bg:#fff;
    --code-bg: rgba(135,131,120,.15); --code-text:#eb5757; --block-bg: rgb(247,246,243);
    --blue: rgb(35,131,226); --blue-bg: rgb(231,243,248); --yellow-bg: rgb(251,243,219); --gray-bg: rgb(241,241,239);
    --font: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Pretendard, "Apple SD Gothic Neo", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji";
    --mono: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", monospace;
  }
  *{ box-sizing: border-box; }
  html,body{ margin:0; padding:0; }
  body{ font-family: var(--font); color: var(--text); background: var(--bg); font-size:16px; line-height:1.5; -webkit-font-smoothing: antialiased; }
  .topbar{ position: sticky; top:0; z-index:50; background: rgba(255,255,255,.9); backdrop-filter: saturate(180%) blur(8px); border-bottom:1px solid var(--border); }
  .topbar-inner{ max-width:980px; margin:0 auto; padding:10px 24px 0; }
  .topbar h1{ font-size:13px; font-weight:600; color:var(--text-light); margin:0 0 8px; letter-spacing:.02em; text-transform:uppercase; }
  .tabs{ display:flex; gap:4px; }
  .tab{ appearance:none; border:0; background:transparent; cursor:pointer; font-family:inherit; font-size:15px; font-weight:600; color:var(--text-light); padding:8px 16px; border-bottom:2px solid transparent; border-radius:6px 6px 0 0; }
  .tab:hover{ background:var(--gray-bg); }
  .tab.active{ color:var(--text); border-bottom-color:var(--blue); }
  .subcap{ font-size:13px; color:var(--text-light); padding:8px 24px 10px; max-width:980px; margin:0 auto; }
  .subcap b{ color:var(--text); }
  .panel{ display:none; } .panel.active{ display:block; }
  .page{ max-width:900px; margin:0 auto; padding:28px 60px 140px; }
  @media (max-width:700px){ .page{ padding:20px 20px 100px; } .topbar-inner,.subcap{ padding-left:16px; padding-right:16px; } }
  .page-title{ font-size:40px; font-weight:700; line-height:1.2; margin:8px 0 12px; }
  h1{ font-size:32px; font-weight:700; line-height:1.2; margin:.4em 0 .3em; }
  h2{ font-size:1.5em; font-weight:600; line-height:1.3; margin:1.6em 0 .3em; }
  h3{ font-size:1.15em; font-weight:600; line-height:1.3; margin:1.3em 0 .2em; }
  h4{ font-size:1em; font-weight:600; margin:1.1em 0 .2em; }
  p{ margin:.35em 0; }
  ul,ol{ margin:.25em 0; padding-left:1.5em; }
  li{ margin:.15em 0; padding-left:2px; }
  a{ color:inherit; text-decoration:underline; text-decoration-color:var(--text-faint); }
  hr{ border:0; border-top:1px solid var(--border); margin:1.4em 0; }
  strong{ font-weight:600; }
  code{ font-family:var(--mono); font-size:.85em; background:var(--code-bg); color:var(--code-text); padding:.15em .4em; border-radius:3px; }
  pre{ background:var(--block-bg); border-radius:4px; padding:14px 16px; overflow:auto; margin:.6em 0; }
  pre code{ background:none; color:var(--text); padding:0; font-size:.85em; }
  blockquote{ margin:.6em 0; padding:2px 0 2px 14px; border-left:3px solid var(--text); }
  table{ border-collapse:collapse; margin:.6em 0; font-size:.92em; width:100%; }
  th,td{ border:1px solid var(--border-strong); padding:7px 10px; text-align:left; vertical-align:top; }
  table.headrow th{ background:var(--block-bg); font-weight:600; text-align:left; }
  .mermaid-offline{ font-size:13px; color:#8a6d3b; background:#fcf8e3; border:1px solid #faebcc;
                    border-radius:6px; padding:8px 12px; margin:12px 0 4px; }
  .callout{ display:flex; gap:10px; padding:16px; border-radius:4px; margin:.8em 0; align-items:flex-start; }
  .callout .ico{ font-size:18px; line-height:1.4; }
  .callout .body{ flex:1; }
  .callout .body > :first-child{ margin-top:0; } .callout .body > :last-child{ margin-bottom:0; }
  .callout.blue{ background:var(--blue-bg); } .callout.yellow{ background:var(--yellow-bg); } .callout.gray{ background:var(--gray-bg); }
  details{ margin:.5em 0; }
  summary{ cursor:pointer; font-weight:500; list-style:none; display:flex; gap:6px; align-items:center; }
  summary::before{ content:"\25b8"; color:var(--text-light); transition:transform .12s; display:inline-block; }
  details[open] summary::before{ transform:rotate(90deg); }
  img{ max-width:100%; height:auto; border-radius:4px; display:block; margin:.6em 0; }
  .mermaid{ background:#fff; margin:.8em 0; text-align:center; }
  .ribbon{ font-size:12px; font-weight:600; letter-spacing:.04em; text-transform:uppercase; padding:4px 10px; border-radius:4px; display:inline-block; margin-bottom:10px; }
  .ribbon.before{ background:rgb(253,235,236); color:rgb(180,35,24); }
  .ribbon.after{ background:rgb(219,237,219); color:rgb(28,107,38); }
  .empty{ color:var(--text-light); font-style:italic; padding:24px 0; }
"""

JS = r"""
(function(){
  var caps = { before: '<b>Before</b> — state prior to the change.', after: '<b>After</b> — state following the change.' };
  var subcap = document.getElementById('subcap');
  var tabs = document.querySelectorAll('.tab');
  var panels = document.querySelectorAll('.panel');
  // Mermaid must render only when its panel is visible (hidden flowcharts render 0-width).
  function renderMermaid(scope){
    if (!scope) return;
    var nodes = Array.prototype.slice.call(scope.querySelectorAll('.mermaid:not([data-processed])'));
    if (!nodes.length) return;
    // Mermaid comes from a CDN. Offline, or under a strict CSP, it never loads — say so
    // instead of leaving raw diagram source that looks like a broken document.
    if (!window.mermaid) {
      nodes.forEach(function(n){
        if (n.getAttribute('data-nomermaid')) return;
        n.setAttribute('data-nomermaid', '1');
        var note = document.createElement('div');
        note.className = 'mermaid-offline';
        note.textContent = 'Diagram not rendered — the Mermaid library could not be loaded (offline or blocked). The source is shown below.';
        n.parentNode.insertBefore(note, n);
      });
      return;
    }
    try { window.mermaid.run({ nodes: nodes }); } catch(e){ console.error(e); }
  }
  if (window.mermaid) { try { window.mermaid.initialize({ startOnLoad:false, theme:'neutral', securityLevel:'strict' }); } catch(e){} }
  renderMermaid(document.querySelector('.panel.active'));
  tabs.forEach(function(t){
    t.addEventListener('click', function(){
      var target = t.getAttribute('data-target');
      tabs.forEach(function(x){ x.classList.toggle('active', x === t); });
      panels.forEach(function(p){ p.classList.toggle('active', p.id === target); });
      if (subcap && caps[target]) subcap.innerHTML = caps[target];
      renderMermaid(document.getElementById(target));
      window.scrollTo({ top: 0 });
    });
  });
})();
"""

# Pinned exact version with an integrity hash: a floating `mermaid@11` lets the CDN
# swap the script under a report that is kept as durable history, and without SRI the
# browser will run whatever comes back. Re-pin by downloading the file and running
# `openssl dgst -sha384 -binary mermaid.min.js | openssl base64 -A`.
MERMAID_VERSION = '11.12.0'
MERMAID_SRI = 'sha384-o+g/BxPwhi0C3RK7oQBxQuNimeafQ3GE/ST4iT2BxVI4Wzt60SH4pq9iXVYujjaS'
MERMAID_SCRIPT = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@%s/dist/mermaid.min.js"'
    ' integrity="%s" crossorigin="anonymous" referrerpolicy="no-referrer"></script>\n'
    % (MERMAID_VERSION, MERMAID_SRI)
)

CALLOUT_ICON = {'NOTE': '\U0001F4DD', 'TIP': '\U0001F4A1', 'WARNING': '⚠️',
                'CAUTION': '\U0001F6D1', 'IMPORTANT': '❗', 'INFO': 'ℹ️', 'TODO': '\U0001F4DD'}
CALLOUT_COLOR = {'NOTE': 'blue', 'TIP': 'blue', 'INFO': 'blue', 'IMPORTANT': 'blue',
                 'WARNING': 'yellow', 'CAUTION': 'yellow', 'TODO': 'yellow'}


# A page body is untrusted input: anyone with edit access to the source page can put
# anything in it, and the maintainer opens the result in a browser. Only http(s), mailto,
# and relative URLs survive; everything else (javascript:, data:, vbscript:) becomes inert.
SAFE_URL_RE = re.compile(r'^(?:https?:|mailto:|[^a-zA-Z]|[a-zA-Z0-9._~%+-]+(?:[/?#]|$))')

# Block-level HTML the template and Notion exports actually emit. Anything else starting
# with '<' is prose (a template placeholder), not markup.
RAW_HTML_TAGS = (
    'div', 'details', 'summary', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'p', 'blockquote', 'ul', 'ol', 'li', 'img', 'a', 'span', 'pre', 'code',
    'section', 'article', 'figure', 'figcaption', 'hr', 'br', 'h1', 'h2', 'h3', 'h4',
)
RAW_HTML_RE = re.compile(r'^<(?:!--|/?(?:%s)\b)' % '|'.join(RAW_HTML_TAGS), re.I)


def safe_url(url):
    """Return an attribute-safe URL, or '#' when the scheme is not allowlisted."""
    u = url.strip()
    # &#x27; etc. can arrive here because escape() already ran on the surrounding text.
    probe = u.replace('&#x27;', "'").replace('&quot;', '"').replace('&amp;', '&')
    if not SAFE_URL_RE.match(probe):
        return '#'
    return html.escape(u, quote=True)


SAFE_ATTRS = {'href', 'src', 'alt', 'title', 'class', 'colspan', 'rowspan', 'open', 'lang'}
URL_ATTRS = {'href', 'src'}
VOID_TAGS = {'img', 'br', 'hr'}


class _Sanitizer(HTMLParser):
    """Reduce an HTML fragment to the tags and attributes this viewer renders.

    Everything that is not in RAW_HTML_TAGS is escaped rather than dropped, so a
    template placeholder written as `<Why this work was needed>` still shows up as
    text instead of being swallowed by the browser. Attributes outside SAFE_ATTRS —
    every `on*` handler among them — are removed, and `href`/`src` go through
    safe_url(), which is the same allowlist the markdown path uses.
    """

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []

    def _emit_tag(self, tag, attrs, self_closing):
        if tag.lower() not in RAW_HTML_TAGS:
            return False
        kept = []
        for name, value in attrs:
            name = name.lower()
            if name not in SAFE_ATTRS:
                continue
            if value is None:
                kept.append(name)
            elif name in URL_ATTRS:
                kept.append('%s="%s"' % (name, safe_url(value)))
            else:
                kept.append('%s="%s"' % (name, html.escape(value, quote=True)))
        close = ' /' if self_closing or tag.lower() in VOID_TAGS else ''
        self.out.append('<%s%s%s>' % (tag.lower(), ''.join(' ' + a for a in kept), close))
        return True

    def handle_starttag(self, tag, attrs):
        if not self._emit_tag(tag, attrs, False):
            self.out.append(html.escape(self.get_starttag_text() or '', quote=False))

    def handle_startendtag(self, tag, attrs):
        if not self._emit_tag(tag, attrs, True):
            self.out.append(html.escape(self.get_starttag_text() or '', quote=False))

    def handle_endtag(self, tag):
        if tag.lower() in RAW_HTML_TAGS:
            self.out.append('</%s>' % tag.lower())
        else:
            self.out.append(html.escape('</%s>' % tag, quote=False))

    def handle_data(self, data):
        self.out.append(html.escape(data, quote=False))

    def handle_entityref(self, name):
        self.out.append('&%s;' % name)

    def handle_charref(self, name):
        self.out.append('&#%s;' % name)

    def handle_comment(self, data):
        self.out.append('<!--%s-->' % data.replace('--', '- -'))


def sanitize_html(fragment):
    """Strip scripts, handlers, and unknown tags out of an untrusted HTML fragment."""
    # <script>/<style> bodies are never markup this viewer renders, and HTMLParser hands
    # them over as raw data. Drop them wholesale before parsing so their contents cannot
    # survive as text that a later paste re-activates.
    fragment = re.sub(r'<\s*(script|style)\b.*?<\s*/\s*\1\s*>', '', fragment,
                      flags=re.I | re.S)
    parser = _Sanitizer()
    parser.feed(fragment)
    parser.close()
    return ''.join(parser.out)


def inline(s):
    """Render inline markdown to HTML (code-protected, then escaped)."""
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return '\x00%d\x00' % (len(codes) - 1)

    s = re.sub(r'`([^`]+)`', stash, s)
    s = html.escape(s, quote=True)
    s = re.sub(r'!\[(.*?)\]\((.*?)\)', lambda m: '<img alt="%s" src="%s">' % (m.group(1), safe_url(m.group(2))), s)
    s = re.sub(r'\[(.*?)\]\((.*?)\)', lambda m: '<a href="%s">%s</a>' % (safe_url(m.group(2)), m.group(1)), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: '<code>' + html.escape(codes[int(m.group(1))], quote=False) + '</code>', s)
    return s


_BLOCK_START = re.compile(r'^\s*(#{1,6}\s|[-*]\s|\d+\.\s|>|```|\||<|---\s*$)')


def md_to_html(md):
    lines = md.replace('\r\n', '\n').split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # fenced code / mermaid
        if stripped.startswith('```'):
            lang = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            code = '\n'.join(buf)
            if lang == 'mermaid':
                out.append('<div class="mermaid">\n' + code + '\n</div>')
            else:
                out.append('<pre><code>' + html.escape(code, quote=False) + '</code></pre>')
            continue
        # hr
        if re.match(r'^---+\s*$', stripped):
            out.append('<hr>')
            i += 1
            continue
        # heading
        m = re.match(r'(#{1,6})\s+(.*)', stripped)
        if m:
            lvl = min(len(m.group(1)), 4)
            out.append('<h%d>%s</h%d>' % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue
        # raw HTML block (callout/details/table written as HTML) -> passthrough until blank line.
        # Matched against a real tag name, not a bare '<': the narrative template seeds
        # placeholders like "<Why this work was needed — the problem and motivation.>", and
        # treating those as HTML makes the browser swallow the line, so a freshly seeded
        # section renders blank and looks like it was never written.
        if RAW_HTML_RE.match(stripped):
            buf = [line]
            i += 1
            while i < n and lines[i].strip():
                buf.append(lines[i])
                i += 1
            out.append(sanitize_html('\n'.join(buf)))
            continue
        # blockquote / GitHub callout
        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            first = buf[0] if buf else ''
            cm = re.match(r'\[!(\w+)\]\s*(.*)', first)
            if cm:
                kind = cm.group(1).upper()
                icon = CALLOUT_ICON.get(kind, '\U0001F4DD')
                color = CALLOUT_COLOR.get(kind, 'blue')
                body_lines = ([cm.group(2)] if cm.group(2) else []) + buf[1:]
                body = '<br>'.join(inline(b) for b in body_lines if b)
                out.append('<div class="callout %s"><div class="ico">%s</div><div class="body"><p>%s</p></div></div>' % (color, icon, body))
            else:
                out.append('<blockquote>%s</blockquote>' % '<br>'.join(inline(b) for b in buf))
            continue
        # pipe table (header row + separator row + body rows)
        if '|' in stripped and i + 1 < n and re.match(r'^[\s|:\-]+$', lines[i + 1].strip()) and '-' in lines[i + 1]:
            def cells(ln):
                return [c.strip() for c in ln.strip().strip('|').split('|')]
            rows = [cells(stripped)]
            i += 2
            while i < n and '|' in lines[i] and lines[i].strip():
                rows.append(cells(lines[i]))
                i += 1
            # Real <th scope="col"> for the header row: a screen reader announces the column
            # name with each cell. Faking it with CSS leaves the metadata table an unlabeled grid.
            t = ['<table class="headrow">']
            if rows:
                t.append('<thead><tr>' + ''.join('<th scope="col">%s</th>' % inline(c) for c in rows[0]) + '</tr></thead>')
            if len(rows) > 1:
                t.append('<tbody>')
                for r in rows[1:]:
                    t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>')
                t.append('</tbody>')
            t.append('</table>')
            out.append('\n'.join(t))
            continue
        # unordered list
        if re.match(r'^\s*[-*]\s+', line):
            items = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(inline(re.sub(r'^\s*[-*]\s+', '', lines[i])))
                i += 1
            out.append('<ul>' + ''.join('<li>%s</li>' % it for it in items) + '</ul>')
            continue
        # ordered list
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(inline(re.sub(r'^\s*\d+\.\s+', '', lines[i])))
                i += 1
            out.append('<ol>' + ''.join('<li>%s</li>' % it for it in items) + '</ol>')
            continue
        # paragraph
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not _BLOCK_START.match(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append('<p>%s</p>' % inline(' '.join(buf)))
    return '\n'.join(out)


def load(path):
    if path is None:
        return None
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if path.lower().endswith(('.html', '.htm')):
        return sanitize_html(text)
    return md_to_html(text)


def wrap(title, before_html, after_html):
    t = html.escape(title)
    if before_html is None:
        before_html = '<div class="empty">No "before" snapshot was provided.</div>'
    parts = [
        '<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        '<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n' % (t, CSS),
        '<div class="topbar"><div class="topbar-inner"><h1>%s</h1>' % t,
        '<div class="tabs">',
        '<button class="tab active" data-target="before">● Before</button>',
        '<button class="tab" data-target="after">● After</button>',
        '</div></div>',
        '<div class="subcap" id="subcap"><b>Before</b> — state prior to the change.</div></div>\n',
        '<main>\n',
        '<section id="before" class="panel active"><div class="page"><span class="ribbon before">Before</span>\n',
        before_html, '\n</div></section>\n',
        '<section id="after" class="panel"><div class="page"><span class="ribbon after">After</span>\n',
        after_html, '\n</div></section>\n',
        '</main>\n',
        MERMAID_SCRIPT,
        '<script>%s</script>\n</body>\n</html>\n' % JS,
    ]
    return ''.join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Notion-look tabbed before/after HTML viewer.')
    ap.add_argument('--before', help='before content (.md or .html). Optional.')
    ap.add_argument('--after', help='after content (.md or .html).')
    ap.add_argument('--title', help='document title (header + <title>).')
    ap.add_argument('--out', help='output html path.')
    ap.add_argument('--selftest', action='store_true', help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if args.selftest:
        sample = "## H\n- a\n- b\n\n| x | y |\n|---|---|\n| 1 | 2 |\n\n```mermaid\nflowchart LR\n  A-->B\n```\n> [!TODO] confirm\n"
        h = md_to_html(sample)
        assert '<table class="headrow">' in h and '<div class="mermaid">' in h and 'callout yellow' in h and '<ul>' in h

        hostile = ('<div class="x" onclick="steal()"><img src="x" onerror="alert(1)">'
                   '<a href="javascript:alert(1)">go</a><script>alert(1)</script></div>')
        s = sanitize_html(hostile)
        assert 'onclick' not in s and 'onerror' not in s and 'javascript:' not in s
        assert '<script' not in s and 'alert(1)' not in s
        assert '<div class="x">' in s and '<a href="#">go</a>' in s

        placeholder = '<Why this work was needed — the problem and motivation.>'
        assert sanitize_html(placeholder).startswith('&lt;Why')

        assert 'integrity="sha384-' in wrap('t', None, h)
        print('selftest OK')
        return 0

    missing = [k for k in ('after', 'title', 'out') if not getattr(args, k)]
    if missing:
        ap.error('the following arguments are required: ' + ', '.join('--' + k for k in missing))

    after_html = load(args.after)
    before_html = load(args.before)
    out = wrap(args.title, before_html, after_html)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote %s (%d bytes)' % (args.out, len(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
