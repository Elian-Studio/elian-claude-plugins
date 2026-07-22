#!/usr/bin/env python3
"""Render claudedocs/<label>/spec-coverage.json into a readable HTML view.

Usage:
  python3 render.py <label> [project_root] [--lang ko|en]

Input:  {project_root}/claudedocs/{label}/spec-coverage.json
Output: {project_root}/claudedocs/{label}/spec-coverage.html

The rendered labels default to Korean because the deliverable is read by
Korean-speaking teams; pass --lang en for an English view. Same idiom as
document-writer/scripts/build_doc.py.

Exit codes: 0 ok, 1 bad usage, 2 input JSON missing.
"""
import argparse
import html as htmlmod
import json
import sys
from pathlib import Path

UI = {
    "ko": {
        "status": {
            "pass": "✓ 통과",
            "partial": "◐ 부분",
            "fail": "✗ 막힘",
            "unchecked": "· 미점검",
            "skipped": "— 스킵",
        },
        "progress": "전체 진행률",
        "last_checked": "최근 점검",
        "leaf_total": "총 leaf",
        "count": "건",
        "of_total": "/ 총",
        "what": "무엇을 (what)",
        "where": "어디서 (where)",
        "how": "어떻게 검증 (how_to_verify)",
        "source": "출처",
        "expected": "기대값",
        "steps": "단계 검증",
        "th_id": "ID",
        "th_step": "단계",
        "th_status": "상태",
        "th_evidence": "근거",
        "unrecorded": "— (미기록)",
        "tests": "증명 테스트",
        "no_tests": "이 AC ID를 가진 테스트가 없습니다",
        "ac_headline": "테스트로 증명된 AC",
        "ac_manual": "사람이 주장 (테스트 없음)",
        "by_test": "기계 판정",
        "by_manual": "사람 주장",
        "undecided": "미판정",
        "truth_test": "테스트가 진실원",
        "truth_mixed": "테스트 우선 · 없으면 수동 증거",
        "truth_manual": "수동 증거만 (자동 판정 불가)",
        "back": "← 로드맵",
        "json_source": "JSON 진실원",
        "label": "라벨",
    },
    "en": {
        "status": {
            "pass": "✓ pass",
            "partial": "◐ partial",
            "fail": "✗ fail",
            "unchecked": "· unchecked",
            "skipped": "— skipped",
        },
        "progress": "Overall progress",
        "last_checked": "Last checked",
        "leaf_total": "Total leaves",
        "count": "",
        "of_total": "/ total",
        "what": "What",
        "where": "Where",
        "how": "How to verify",
        "source": "Source",
        "expected": "Expected",
        "steps": "Step verification",
        "th_id": "ID",
        "th_step": "Step",
        "th_status": "Status",
        "th_evidence": "Evidence",
        "unrecorded": "— (not recorded)",
        "tests": "Proving tests",
        "no_tests": "No test carries this AC ID",
        "ac_headline": "AC proven by tests",
        "ac_manual": "human-asserted (no test)",
        "by_test": "machine-verified",
        "by_manual": "human-asserted",
        "undecided": "undecided",
        "truth_test": "tests are the source of truth",
        "truth_mixed": "tests first, manual evidence otherwise",
        "truth_manual": "manual evidence only (not machine-checkable)",
        "back": "← Roadmap",
        "json_source": "JSON source of truth",
        "label": "Label",
    },
}

TRUTH_KEY = {"test": "truth_test", "test-or-manual": "truth_mixed", "manual": "truth_manual"}


def esc(s) -> str:
    return htmlmod.escape(str(s)) if s is not None else ""


def badge(status: str, t: dict) -> str:
    label = t["status"].get(status, "?")
    return f'<span class="badge b-{esc(status)}">{label}</span>'


def render_step(step: dict, t: dict) -> str:
    evidence = esc(step.get("evidence", ""))
    evidence_html = f'<div class="evidence">{evidence}</div>' if evidence else ""
    return f'''
      <tr class="step-row status-{esc(step["status"])}">
        <td class="step-id">{esc(step["id"])}</td>
        <td class="step-desc">{esc(step["desc"])}</td>
        <td class="step-status">{badge(step["status"], t)}</td>
        <td class="step-evidence">{evidence_html}</td>
      </tr>
    '''


def render_where(where: dict, t: dict) -> str:
    rows = [
        f'<div class="where-row"><span class="where-key">{esc(k)}</span><code>{esc(v)}</code></div>'
        for k, v in (where or {}).items() if v
    ]
    if not rows:
        return f'<div class="where-empty">{esc(t["unrecorded"])}</div>'
    return "\n".join(rows)


def render_verify(verify_list: list) -> str:
    rows = []
    for v in verify_list or []:
        vtype = v.get("type", "")
        if vtype == "grep":
            rows.append(f'<span class="verify-tag t-grep">grep <code>{esc(v.get("keyword",""))}</code> @ {esc(v.get("path",""))}</span>')
        elif vtype == "sql":
            rows.append(f'<span class="verify-tag t-sql">SQL {esc(v.get("ref",""))}</span>')
        elif vtype in ("scenario", "backlog", "doc"):
            rows.append(f'<span class="verify-tag t-scenario">{esc(vtype)} {esc(v.get("ref",""))}</span>')
        else:
            rows.append(f'<span class="verify-tag">{esc(json.dumps(v, ensure_ascii=False))}</span>')
    return " ".join(rows)


def render_decided(item: dict, t: dict) -> str:
    """The visual line between what a machine checked and what a human claimed."""
    by = item.get("decided_by", "")
    if by == "test":
        return f'<span class="decided d-test">{esc(t["by_test"])}</span>'
    if by == "manual":
        return f'<span class="decided d-manual">{esc(t["by_manual"])}</span>'
    return f'<span class="decided d-none">{esc(t["undecided"])}</span>'


def render_tests(item: dict, t: dict) -> str:
    tests = item.get("tests") or []
    if tests:
        rows = "".join(f'<li><code>{esc(x)}</code></li>' for x in tests)
        return f'''
        <div class="tests-section">
          <div class="section-label">{esc(t["tests"])}</div>
          <ul class="tests-list">{rows}</ul>
        </div>'''
    if item.get("ac"):
        return f'<div class="tests-missing">{esc(t["no_tests"])}: <code>{esc(", ".join(item["ac"]))}</code></div>'
    return ""


def render_item(item: dict, t: dict) -> str:
    cls = item["status"]
    show_steps = item["steps"] and item.get("decided_by") != "test"
    steps_html = ""
    if show_steps:
        steps_html = f'''
        <div class="steps-section">
          <div class="section-label">{esc(t["steps"])}</div>
          <table class="steps-table">
            <thead><tr><th>{esc(t["th_id"])}</th><th>{esc(t["th_step"])}</th><th>{esc(t["th_status"])}</th><th>{esc(t["th_evidence"])}</th></tr></thead>
            <tbody>{"".join(render_step(s, t) for s in item["steps"])}</tbody>
          </table>
        </div>
        '''
    blocker_html = f'<div class="blocker">⚠ {esc(item["blocker"])}</div>' if item.get("blocker") else ""
    note_html = f'<div class="note">📝 {esc(item["note"])}</div>' if item.get("note") else ""
    last_checked = item.get("last_checked", "")
    checked_html = (f'<span class="last-checked">{esc(t["last_checked"])} {esc(last_checked)}</span>'
                    if last_checked else "")
    expected_html = ""
    if item.get("expected"):
        expected_html = f'''
          <div class="info-block">
            <div class="section-label">{esc(t["expected"])}</div>
            <div class="info-value"><code>{esc(item["expected"])}</code></div>
          </div>'''

    return f'''
    <article class="item status-{esc(cls)} by-{esc(item.get("decided_by") or "none")}" id="item-{esc(item["id"])}">
      <header class="item-head" onclick="toggleItem(this)">
        <span class="item-id">{esc(item["id"])}</span>
        <span class="item-title">{esc(item["title"])}</span>
        {render_decided(item, t)}
        {badge(cls, t)}
        {checked_html}
        <span class="chevron">▶</span>
      </header>
      <div class="item-body">
        <div class="info-grid">
          <div class="info-block">
            <div class="section-label">{esc(t["what"])}</div>
            <div class="info-value">{esc(item.get("what",""))}</div>
          </div>
          <div class="info-block">
            <div class="section-label">{esc(t["where"])}</div>
            <div class="info-value">{render_where(item.get("where", {}), t)}</div>
          </div>
          <div class="info-block">
            <div class="section-label">{esc(t["how"])}</div>
            <div class="info-value">{render_verify(item.get("how_to_verify", []))}</div>
          </div>
          <div class="info-block">
            <div class="section-label">{esc(t["source"])}</div>
            <div class="info-value"><code>{esc(item.get("source_doc",""))}</code></div>
          </div>
          {expected_html}
        </div>
        {render_tests(item, t)}
        {blocker_html}
        {note_html}
        {steps_html}
      </div>
    </article>
    '''


def cat_summary(cat: dict) -> dict:
    counts = {"pass": 0, "partial": 0, "fail": 0, "unchecked": 0, "skipped": 0}
    for it in cat["items"]:
        if it["steps"] and it.get("decided_by") != "test":
            for s in it["steps"]:
                counts[s["status"]] = counts.get(s["status"], 0) + 1
        else:
            counts[it["status"]] = counts.get(it["status"], 0) + 1
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    return counts


def render_nav_link(cat: dict, t: dict) -> str:
    counts = cat_summary(cat)
    progress = (counts["pass"] / counts["total"] * 100) if counts["total"] else 0
    return f'''
      <a class="nav-link" href="#cat-{esc(cat["id"])}">
        <div class="nav-link-head">
          <span class="nav-cat-id">{esc(cat["id"])}</span>
          <span class="nav-cat-name">{esc(cat["name"][:24])}</span>
        </div>
        <div class="nav-link-meta">
          <span class="nav-count">{counts["total"]}{esc(t["count"])}</span>
          <span class="badge b-pass">✓{counts["pass"]}</span>
          <span class="badge b-fail">✗{counts["fail"]}</span>
          <span class="badge b-unchecked">·{counts["unchecked"]}</span>
        </div>
        <div class="mini-bar"><div class="mini-fill" style="width:{progress:.0f}%"></div></div>
      </a>
    '''


def render_category(cat: dict, t: dict) -> str:
    counts = cat_summary(cat)
    items_html = "\n".join(render_item(it, t) for it in cat["items"])
    truth = t[TRUTH_KEY.get(cat.get("truth_source", "manual"), "truth_manual")]
    truth_cls = "truth-" + esc(cat.get("truth_source", "manual"))
    return f'''
    <section class="category" id="cat-{esc(cat["id"])}">
      <header class="cat-head">
        <h2><span class="cat-id-tag">{esc(cat["id"])}</span> {esc(cat["name"])}
          <span class="truth {truth_cls}">{esc(truth)}</span></h2>
        <div class="cat-summary">
          <span class="badge b-pass">✓ {counts["pass"]}</span>
          <span class="badge b-partial">◐ {counts["partial"]}</span>
          <span class="badge b-fail">✗ {counts["fail"]}</span>
          <span class="badge b-unchecked">· {counts["unchecked"]}</span>
          <span class="badge b-skipped">— {counts["skipped"]}</span>
          <span class="cat-total">{esc(t["of_total"])} {counts["total"]}</span>
        </div>
      </header>
      <div class="items-list">{items_html}</div>
    </section>
    '''


CSS = """
:root {
  --bg:#0f1419; --panel:#1a1f2e; --panel-2:#232938; --border:#2d3548;
  --text:#e8eaed; --text-dim:#9aa0a6; --text-muted:#5f6368;
  --accent:#4f8cff; --green:#34a853; --yellow:#fbbc04; --red:#ea4335;
  --blue:#4285f4; --gray:#6c757d; --purple:#a78bfa;
  --green-bg:rgba(52,168,83,.12); --yellow-bg:rgba(251,188,4,.12);
  --red-bg:rgba(234,67,53,.12); --blue-bg:rgba(66,133,244,.12);
  --gray-bg:rgba(108,117,125,.12); --purple-bg:rgba(167,139,250,.12);
}
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Pretendard,"Apple SD Gothic Neo","Noto Sans KR",sans-serif; background:var(--bg); color:var(--text); line-height:1.55; font-size:14px; }
.layout { display:grid; grid-template-columns:300px 1fr; min-height:100vh; }
nav.side { background:var(--panel); border-right:1px solid var(--border); padding:20px 14px; position:sticky; top:0; height:100vh; overflow-y:auto; }
nav.side h1 { font-size:13px; margin:0 0 4px; color:var(--accent); letter-spacing:.5px; }
nav.side .sub { font-size:11px; color:var(--text-dim); margin-bottom:14px; }
.back-link { display:inline-block; font-size:11px; color:var(--text-dim); text-decoration:none; margin-bottom:10px; padding:3px 8px; border:1px solid var(--border); border-radius:5px; }
.back-link:hover { color:var(--accent); border-color:var(--accent); }
.headline { background:var(--panel-2); border-radius:8px; padding:12px; margin-bottom:12px; text-align:center; }
.headline-num { font-size:26px; font-weight:700; color:var(--green); font-family:"SF Mono",monospace; }
.headline-num.zero { color:var(--red); }
.headline-label { font-size:10px; color:var(--text-dim); text-transform:uppercase; letter-spacing:.5px; margin-top:2px; }
.headline-manual { font-size:10px; color:var(--amber,#b7791f); margin-top:2px; }
.headline-split { font-size:10px; color:var(--text-muted); margin-top:6px; }
.side-progress { background:var(--panel-2); border-radius:8px; padding:10px 12px; margin-bottom:16px; }
.side-progress-label { font-size:11px; color:var(--text-dim); margin-bottom:6px; display:flex; justify-content:space-between; }
.side-progress-bar { height:8px; background:var(--bg); border-radius:4px; overflow:hidden; display:flex; }
.spb-pass { background:var(--green); }
.spb-partial { background:var(--yellow); }
.spb-fail { background:var(--red); }
.spb-skipped { background:var(--gray); }
.spb-unchecked { background:var(--panel); }
.side-progress-stats { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; font-size:10px; }
.nav-link { display:block; padding:8px 10px; margin-bottom:4px; color:var(--text-dim); text-decoration:none; border-radius:6px; font-size:12px; transition:all .15s; border:1px solid transparent; }
.nav-link:hover { background:var(--panel-2); color:var(--text); border-color:var(--border); }
.nav-link-head { display:flex; align-items:center; gap:6px; margin-bottom:4px; }
.nav-cat-id { background:var(--panel-2); padding:1px 6px; border-radius:3px; font-size:10px; font-family:"SF Mono",monospace; color:var(--accent); }
.nav-cat-name { font-size:12px; font-weight:500; color:var(--text); }
.nav-link-meta { display:flex; gap:4px; font-size:10px; align-items:center; flex-wrap:wrap; margin-bottom:4px; }
.nav-count { color:var(--text-muted); }
.mini-bar { height:3px; background:var(--bg); border-radius:2px; overflow:hidden; }
.mini-fill { height:100%; background:linear-gradient(90deg,var(--green),#2d9947); }
main { padding:32px 40px; max-width:1200px; }
header.page-head { margin-bottom:32px; padding-bottom:20px; border-bottom:1px solid var(--border); }
header.page-head h1 { margin:0 0 6px; font-size:24px; }
header.page-head .meta { display:flex; gap:16px; color:var(--text-dim); font-size:12px; flex-wrap:wrap; }
header.page-head .meta span::before { content:"·"; margin-right:8px; color:var(--text-muted); }
header.page-head .meta span:first-child::before { content:""; margin:0; }
.category { margin-bottom:48px; }
.cat-head { display:flex; justify-content:space-between; align-items:center; padding-bottom:10px; border-bottom:1px solid var(--border); margin-bottom:16px; gap:12px; flex-wrap:wrap; }
.cat-head h2 { margin:0; font-size:18px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.cat-id-tag { background:var(--panel-2); color:var(--accent); padding:2px 10px; border-radius:6px; font-size:13px; font-family:"SF Mono",monospace; }
.truth { font-size:10px; font-weight:500; padding:2px 8px; border-radius:10px; }
.truth-test { background:var(--purple-bg); color:var(--purple); }
.truth-test-or-manual { background:var(--blue-bg); color:var(--blue); }
.truth-manual { background:var(--gray-bg); color:var(--text-dim); }
.cat-summary { display:flex; gap:6px; align-items:center; }
.cat-total { color:var(--text-dim); font-size:12px; margin-left:8px; }
.items-list { display:flex; flex-direction:column; gap:8px; }
.item { background:var(--panel); border:1px solid var(--border); border-left-width:3px; border-radius:8px; overflow:hidden; transition:border-color .15s; }
.item.status-pass { border-left-color:var(--green); }
.item.status-partial { border-left-color:var(--yellow); }
.item.status-fail { border-left-color:var(--red); }
.item.status-unchecked { border-left-color:var(--gray); }
.item.status-skipped { border-left-color:var(--gray); opacity:.6; }
.item-head { display:flex; align-items:center; gap:10px; padding:12px 16px; cursor:pointer; user-select:none; }
.item-head:hover { background:var(--panel-2); }
.item-id { background:var(--panel-2); padding:2px 8px; border-radius:4px; font-size:11px; font-family:"SF Mono",monospace; color:var(--text-dim); min-width:60px; text-align:center; }
.item-title { flex:1; font-size:13px; font-weight:500; }
.decided { font-size:9px; padding:2px 7px; border-radius:9px; letter-spacing:.3px; white-space:nowrap; text-transform:uppercase; }
.d-test { background:var(--purple-bg); color:var(--purple); border:1px solid rgba(167,139,250,.35); }
.d-manual { background:var(--gray-bg); color:var(--text-dim); border:1px dashed var(--border); }
.d-none { background:transparent; color:var(--text-muted); border:1px dotted var(--border); }
.last-checked { font-size:10px; color:var(--text-muted); }
.chevron { color:var(--text-muted); font-size:10px; transition:transform .2s; }
.item.open .chevron { transform:rotate(90deg); }
.item-body { display:none; padding:0 16px 16px; border-top:1px solid var(--border); }
.item.open .item-body { display:block; }
.info-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:16px 0; }
.info-block { background:var(--panel-2); padding:10px 12px; border-radius:6px; }
.section-label { font-size:10px; color:var(--text-dim); text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; }
.info-value { font-size:12px; color:var(--text); }
.info-value code { background:var(--bg); padding:1px 6px; border-radius:3px; color:var(--accent); font-size:11px; }
.where-row { margin:2px 0; display:flex; gap:6px; align-items:baseline; }
.where-key { font-size:10px; color:var(--text-dim); min-width:60px; text-transform:uppercase; }
.where-empty { color:var(--text-muted); font-size:11px; font-style:italic; }
.verify-tag { display:inline-block; background:var(--bg); padding:2px 8px; border-radius:4px; font-size:11px; margin:2px 2px 2px 0; }
.verify-tag.t-scenario { color:var(--accent); }
.verify-tag.t-grep { color:var(--green); }
.verify-tag.t-sql { color:var(--yellow); }
.verify-tag code { background:transparent; padding:0; color:inherit; }
.tests-section { background:var(--purple-bg); border-left:3px solid var(--purple); border-radius:0 6px 6px 0; padding:8px 12px; margin-top:8px; }
.tests-list { margin:0; padding-left:18px; font-size:11px; }
.tests-list code { background:var(--bg); padding:1px 5px; border-radius:3px; color:var(--purple); }
.tests-missing { background:var(--red-bg); border-left:3px solid var(--red); padding:8px 12px; margin-top:8px; border-radius:0 6px 6px 0; font-size:12px; color:var(--red); }
.tests-missing code { background:var(--bg); padding:1px 5px; border-radius:3px; }
.steps-section { background:var(--panel-2); border-radius:6px; padding:10px 12px; margin-top:8px; }
.steps-table { width:100%; border-collapse:collapse; font-size:11px; }
.steps-table th { text-align:left; padding:6px; color:var(--text-dim); font-weight:600; border-bottom:1px solid var(--border); }
.steps-table td { padding:6px; vertical-align:top; border-bottom:1px solid rgba(45,53,72,.4); }
.steps-table tr:last-child td { border-bottom:none; }
.step-id { font-family:"SF Mono",monospace; color:var(--text-muted); width:80px; }
.step-desc { color:var(--text); }
.step-status { width:80px; text-align:center; }
.step-evidence { color:var(--text-dim); }
.step-evidence .evidence { font-family:"SF Mono",monospace; font-size:10px; background:var(--bg); padding:2px 4px; border-radius:3px; word-break:break-all; }
.blocker { background:var(--red-bg); border-left:3px solid var(--red); padding:8px 12px; margin-top:8px; border-radius:0 6px 6px 0; font-size:12px; color:var(--red); }
.note { background:var(--blue-bg); border-left:3px solid var(--blue); padding:8px 12px; margin-top:8px; border-radius:0 6px 6px 0; font-size:12px; color:var(--text); }
.badge { display:inline-block; padding:1px 8px; border-radius:10px; font-size:10px; font-weight:600; letter-spacing:.3px; white-space:nowrap; }
.b-pass { background:var(--green-bg); color:var(--green); }
.b-partial { background:var(--yellow-bg); color:var(--yellow); }
.b-fail { background:var(--red-bg); color:var(--red); }
.b-unchecked { background:var(--gray-bg); color:var(--text-dim); }
.b-skipped { background:var(--gray-bg); color:var(--text-muted); }
@media (max-width:900px) {
  .layout { grid-template-columns:1fr; }
  nav.side { position:relative; height:auto; }
  main { padding:20px 16px; }
  .info-grid { grid-template-columns:1fr; }
}
"""


def render(data: dict, lang: str, back_link: bool) -> str:
    t = UI["ko"] if lang.lower().startswith("ko") else UI["en"]
    cats = data["categories"]
    summary = data["summary"]
    sc = summary["status_counts"]
    total = summary["total_leaf"]
    db = summary.get("decided_by_counts", {})
    ac_total = summary.get("ac_total", 0)
    ac_proven = summary.get("ac_proven", 0)

    def pct(n):
        return n / total * 100 if total else 0

    nav_links = "\n".join(render_nav_link(c, t) for c in cats)
    sections = "\n".join(render_category(c, t) for c in cats)
    label = data.get("label", "")
    back_html = f'<a class="back-link" href="index.html">{esc(t["back"])}</a>' if back_link else ""
    zero_cls = " zero" if ac_proven == 0 else ""
    ac_manual = summary.get("ac_claimed_manual", 0)
    manual_note = (f'<div class="headline-manual">+{ac_manual} {esc(t["ac_manual"])}</div>'
                   if ac_manual else "")

    return f'''<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(data["title"])} — spec coverage</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<nav class="side">
  {back_html}
  <h1>{esc(label)}</h1>
  <div class="sub">{esc(data["title"])}<br>{esc(t["last_checked"])} {esc(data["last_checked"])}</div>

  <div class="headline">
    <div class="headline-num{zero_cls}">{ac_proven} / {ac_total}</div>
    <div class="headline-label">{esc(t["ac_headline"])}</div>{manual_note}
    <div class="headline-split">{esc(t["by_test"])} {db.get("test", 0)} ·
      {esc(t["by_manual"])} {db.get("manual", 0)} ·
      {esc(t["undecided"])} {db.get("undecided", 0)}</div>
  </div>

  <div class="side-progress">
    <div class="side-progress-label">
      <span>{esc(t["progress"])}</span>
      <span><strong>{sc["pass"] + sc["partial"]}/{total}</strong> ({pct(sc["pass"] + sc["partial"]):.0f}%)</span>
    </div>
    <div class="side-progress-bar">
      <div class="spb-pass" style="width:{pct(sc["pass"])}%"></div>
      <div class="spb-partial" style="width:{pct(sc["partial"])}%"></div>
      <div class="spb-fail" style="width:{pct(sc["fail"])}%"></div>
      <div class="spb-skipped" style="width:{pct(sc["skipped"])}%"></div>
      <div class="spb-unchecked" style="width:{pct(sc["unchecked"])}%"></div>
    </div>
    <div class="side-progress-stats">
      <span class="badge b-pass">✓ {sc["pass"]}</span>
      <span class="badge b-partial">◐ {sc["partial"]}</span>
      <span class="badge b-fail">✗ {sc["fail"]}</span>
      <span class="badge b-unchecked">· {sc["unchecked"]}</span>
      <span class="badge b-skipped">— {sc["skipped"]}</span>
    </div>
  </div>

  {nav_links}
</nav>
<main>
  <header class="page-head">
    <h1>{esc(data["title"])}</h1>
    <div class="meta">
      <span>{esc(t["label"])} {esc(label)}</span>
      <span>{esc(t["ac_headline"])} <strong>{ac_proven}/{ac_total}</strong></span>
      <span>{esc(t["leaf_total"])} {total}</span>
      <span>{esc(t["last_checked"])} {esc(data["last_checked"])}</span>
      <span>{esc(t["json_source"])}: <code>spec-coverage.json</code></span>
    </div>
  </header>
  {sections}
</main>
</div>
<script>
function toggleItem(head) {{
  const item = head.closest('.item');
  item.classList.toggle('open');
}}
document.addEventListener('DOMContentLoaded', () => {{
  const first = document.querySelector('.item.status-fail') || document.querySelector('.item.status-unchecked');
  if (first) first.classList.add('open');
}});
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description="Render spec-coverage.json to HTML.")
    ap.add_argument("label")
    ap.add_argument("project_root", nargs="?", default=".")
    ap.add_argument("--lang", default="ko", help="rendered UI language (default: ko)")
    args = ap.parse_args()

    base = Path(args.project_root) / "claudedocs" / args.label
    json_path = base / "spec-coverage.json"
    html_path = base / "spec-coverage.html"

    if not json_path.exists():
        print(f"ERROR: no spec-coverage.json at {json_path}", file=sys.stderr)
        sys.exit(2)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    # Back-link only when the roadmap hub actually sits next to this file.
    html = render(data, args.lang, back_link=(base / "index.html").exists())
    html_path.write_text(html, encoding="utf-8")

    s = data["summary"]
    print(f"OK {html_path}")
    print(f"  AC proven: {s.get('ac_proven', 0)}/{s.get('ac_total', 0)}")
    print(f"  Total leaf: {s['total_leaf']}  {s['status_counts']}")


if __name__ == "__main__":
    main()
