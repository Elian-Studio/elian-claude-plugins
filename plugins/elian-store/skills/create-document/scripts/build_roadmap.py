#!/usr/bin/env python3
"""build_roadmap.py — roadmap.json → self-contained index.html renderer.

Called by design-feature Phase 5. Validates roadmap.json against
roadmap.schema.json, then renders a single-file HTML hub with:
  - summary bar (progress %)
  - vertical timeline (phases → task cards)
  - click-to-open task drawer (criteria, subs, deps, links, activity)
  - Mermaid diagram support in task desc (```mermaid blocks)
  - generated document cards + stakeholder matrix

No external Python dependencies — stdlib only.

Usage:
  python3 build_roadmap.py roadmap.json [--out index.html]
  python3 build_roadmap.py roadmap.json --skip-validate
"""

import argparse
import html
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate import validate  # noqa: E402

SCHEMA_PATH = SCRIPT_DIR.parent / "schemas" / "roadmap.schema.json"

PALETTE = ["#6366f1", "#8b5cf6", "#ec4899", "#3b82f6",
           "#f59e0b", "#14b8a6", "#10b981", "#0ea5e9"]


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def phase_stats(tasks):
    active = [t for t in tasks if not t.get("hold") and t.get("status") != "dropped"]
    done = sum(1 for t in active if t.get("status") == "done")
    doing = sum(1 for t in active if t.get("status") == "doing")
    total = len(active)
    dropped = sum(1 for t in tasks if t.get("status") == "dropped" and not t.get("hold"))
    return {"done": done, "doing": doing, "total": total,
            "held": sum(1 for t in tasks if t.get("hold")),
            "dropped": dropped,
            "pct": round(done / total * 100) if total else 0}


def overall_stats(phases):
    d = g = tot = held = dropped = 0
    for p in phases:
        s = phase_stats(p.get("tasks", []))
        d += s["done"]; g += s["doing"]; tot += s["total"]
        held += s["held"]; dropped += s["dropped"]
    return {"done": d, "doing": g, "todo": tot - d - g, "total": tot,
            "held": held, "dropped": dropped,
            "pct": round(d / tot * 100) if tot else 0}


def render_doc_card(d):
    href = d.get("href", "#")
    layer = f'<span class="lyr">{esc(d["layer"])}</span>' if d.get("layer") else ""
    reader = f'<div class="rdr">읽는 사람: {esc(d["reader"])}</div>' if d.get("reader") else ""
    return (f'<a class="doc" href="{esc(href)}">'
            f'<div class="doc-h"><span class="doc-label">{esc(d.get("label", "문서"))}</span>{layer}</div>'
            f'<div class="doc-href">{esc(href)}</div>{reader}</a>')


def render_docs(docs):
    if not docs:
        return ('<div class="seclab">생성된 문서</div>'
                '<div class="panel"><div class="empty">No documents linked yet.</div></div>')
    return ('<div class="seclab">생성된 문서</div><div class="docs">'
            + "".join(render_doc_card(d) for d in docs) + '</div>')


def render_stakeholders(rows):
    if not rows:
        return ""
    body = "".join(
        f'<tr><td class="role">{esc(r.get("role", ""))}</td>'
        f'<td>{esc(r.get("docs", ""))}</td></tr>'
        for r in rows)
    return ('<div class="seclab">Stakeholder 접근 경로</div>'
            '<div class="panel pad"><table class="mtx">'
            '<thead><tr><th>역할</th><th>읽을 문서</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#eceef1;color:#15181d;
  font-family:'Pretendard Variable',Pretendard,-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;line-height:1.6}
@keyframes drawerIn{from{transform:translateX(100%)}to{transform:translateX(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.wrap{max-width:1120px;margin:0 auto;padding:44px 36px 80px}
.klabel{font-size:12px;font-weight:600;letter-spacing:.08em;color:#9095a0;text-transform:uppercase;margin-bottom:10px}
h1{font-size:28px;font-weight:700;margin:0 0 8px;letter-spacing:-.015em}
.lead{font-size:14px;line-height:1.65;color:#646a75;margin:0;max-width:860px;text-wrap:pretty}
.panel{background:#fff;border-radius:18px;box-shadow:0 1px 2px rgba(16,24,40,.05),0 18px 44px -20px rgba(16,24,40,.14)}
.panel.pad{padding:8px 6px}
.seclab{font-size:12px;font-weight:600;letter-spacing:.02em;color:#6b7280;margin:46px 0 13px 2px}
.summary{display:flex;align-items:center;gap:24px;margin-top:24px;background:#fff;border:1px solid #e5e8ec;
  border-radius:16px;padding:20px 24px;box-shadow:0 1px 2px rgba(16,24,40,.04);flex-wrap:wrap}
.summary .pg{flex:1;min-width:300px}
.summary .pg .r{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.summary .pg .r .l{font-size:13px;color:#646a75;font-weight:500}
.summary .pg .r .v{font-size:14px;font-weight:700;font-variant-numeric:tabular-nums}
.track{height:8px;background:#eceef1;border-radius:99px;overflow:hidden}
.track>i{display:block;height:100%;background:#15181d;border-radius:99px;transition:width .35s}
.chips{display:flex;gap:10px;flex:none;flex-wrap:wrap}
.chip{display:flex;align-items:center;gap:9px;background:#f6f7f9;border:1px solid #eceef1;border-radius:11px;padding:9px 14px}
.chip i{width:9px;height:9px;border-radius:99px;flex:none}
.chip .lb{font-size:13px;color:#3a4049}
.chip .n{font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}
.focus{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.focus .fc{flex:1;min-width:280px;display:flex;gap:11px;align-items:flex-start;background:#fff;
  border:1px solid #e5e8ec;border-radius:14px;padding:14px 16px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.focus .fc.block{border-color:#f0d3cf;background:#fdf6f5}
.focus .fc .ic{font-size:15px;line-height:1.5;flex:none}
.focus .fc .bd{min-width:0}
.focus .fc .k{font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:#9095a0;margin-bottom:5px}
.focus .fc.block .k{color:#a4352c}
.focus .fc .v{font-size:14px;color:#2b3038;line-height:1.6;font-weight:500}
.board{padding:32px 34px}
.row{display:flex;gap:20px}
.rail{display:flex;flex-direction:column;align-items:center;flex:none;width:36px}
.node{width:36px;height:36px;border-radius:99px;color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex:none}
.line{width:2px;flex:1;background:#e7eaee;margin:6px 0;min-height:14px}
.row:last-child .line{display:none}
.pbody{flex:1;min-width:0;padding-bottom:26px}
.ph{display:flex;align-items:baseline;gap:12px;margin-bottom:11px}
.ph .nm{font-size:17px;font-weight:700;color:#1c2128;letter-spacing:-.01em}
.ph .ct{font-size:12.5px;color:#9095a0;font-variant-numeric:tabular-nums}
.pbar{height:5px;background:#eceef1;border-radius:99px;overflow:hidden;margin-bottom:13px}
.pbar>i{display:block;height:100%;border-radius:99px;transition:width .35s}
.list{background:#fff;border:1px solid #edeff2;border-radius:13px;overflow:hidden}
.task{display:flex;align-items:center;gap:13px;padding:13px 16px;border-top:1px solid #f1f3f5;cursor:pointer;transition:background .15s}
.list .task:first-child{border-top:none}
.task:hover{background:#fafbfc}
.chk{width:19px;height:19px;border-radius:6px;display:flex;align-items:center;justify-content:center;flex:none;transition:all .15s}
.chk.done{border:1px solid var(--c)}
.chk.done span{color:#fff;font-size:11px;font-weight:800;line-height:1}
.chk.doing{background:#fff;border:1.5px solid var(--c)}
.chk.doing span{font-size:16px;font-weight:800;line-height:1;margin-top:-1px}
.chk.todo{background:#fff;border:1.5px solid #d3d7dd}
.chk.held{background:#fff;border:1.5px dashed #d8b878}
.chk.dropped{background:#fbeae8;border:1.5px solid #a4352c}
.chk.dropped span{color:#a4352c;font-size:11px;font-weight:800;line-height:1}
.txt{font-size:13.5px;line-height:1.5;color:#363c44}
.txt.done{color:#a7adb6;text-decoration:line-through;text-decoration-color:#ccd2d9}
.sp{flex:1}
.per{font-size:11.5px;color:#9095a0;font-variant-numeric:tabular-nums;white-space:nowrap}
.bdg{font-size:11.5px;font-weight:600;padding:3px 9px;border-radius:7px;white-space:nowrap;line-height:1.4;flex:none}
.bdg.done{background:#e8f6ee;color:#15924f}
.bdg.doing{background:#e9f1fe;color:#1f6fe0}
.bdg.todo{background:#eef0f3;color:#828a96}
.bdg.held{background:#fbf2df;color:#9a6b1e}
.bdg.dropped{background:#fbeae8;color:#a4352c}
.chev{color:#c4c9d0;font-size:17px;line-height:1;flex:none}
.empty{padding:26px;text-align:center;color:#9095a0;font-size:13.5px}
.overlay{position:fixed;inset:0;background:rgba(20,24,29,.34);z-index:40;animation:fadeIn .18s ease}
.drawer{position:fixed;top:0;right:0;height:100vh;width:480px;max-width:92vw;background:#fff;z-index:41;
  box-shadow:-14px 0 44px -14px rgba(16,24,40,.3);display:flex;flex-direction:column;animation:drawerIn .26s cubic-bezier(.22,.61,.36,1)}
.dhead{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;border-bottom:1px solid #eef0f3;flex:none}
.dhead .pl{display:flex;align-items:center;gap:9px}
.dhead .pl i{width:9px;height:9px;border-radius:99px}
.dhead .pl span{font-size:13px;font-weight:600;color:#646a75}
.dclose{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:#9095a0;font-size:16px}
.dclose:hover{background:#f3f5f8}
.dbody{flex:1;overflow-y:auto;padding:24px}
.tags{display:flex;align-items:center;gap:9px;margin-bottom:11px;flex-wrap:wrap}
.tkt{font-size:12px;font-weight:600;color:#9aa1ac;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.prio{font-size:11px;font-weight:700;padding:2px 9px;border-radius:6px;letter-spacing:.02em}
.prio.p0{background:#fbeae8;color:#a4352c}.prio.p1{background:#fbf2df;color:#9a6b1e}
.prio.p2{background:#e9f1fe;color:#1f6fe0}
.lab{background:#f1f3f5;color:#6b7280;padding:3px 9px;border-radius:6px;font-size:11.5px;font-weight:500}
.dbody h2{font-size:20px;font-weight:700;margin:0 0 18px;line-height:1.4;letter-spacing:-.01em;text-wrap:pretty}
.sbtns{display:flex;gap:6px;margin-bottom:22px}
.sbtn{flex:1;text-align:center;cursor:pointer;user-select:none;padding:9px 0;border-radius:9px;font-size:13px;font-weight:600;
  transition:all .15s;background:#f6f7f9;color:#9aa1ac;border:1.5px solid transparent}
.sbtn.on.done{background:#e8f6ee;color:#15924f;border-color:#15924f33}
.sbtn.on.doing{background:#e9f1fe;color:#1f6fe0;border-color:#1f6fe033}
.sbtn.on.todo{background:#eef0f3;color:#828a96;border-color:#828a9633}
.meta{display:flex;flex-direction:column;gap:13px;margin-bottom:24px;padding-bottom:22px;border-bottom:1px solid #eef0f3}
.mr{display:flex;align-items:center;gap:14px}
.mr .k{font-size:13px;color:#9095a0;width:64px;flex:none}
.mr .mv{font-size:14px;color:#2b3038;font-weight:500}
.dsec{margin-bottom:26px}
.dsec>.k{font-size:13px;color:#9095a0;margin-bottom:9px}
.dsec .kh{display:flex;align-items:center;justify-content:space-between;margin-bottom:11px}
.dsec .kh .k{font-size:13px;color:#9095a0}
.dsec .kh .c{font-size:12px;color:#9095a0;font-variant-numeric:tabular-nums}
.dsec p{font-size:14px;line-height:1.72;color:#3a4049;margin:0 0 11px;text-wrap:pretty}
.dsec .mermaid{margin:14px 0;max-width:100%;overflow-x:auto}
.ck{display:flex;align-items:flex-start;gap:11px;padding:8px 0;cursor:pointer}
.ck .b{width:18px;height:18px;border-radius:5px;display:flex;align-items:center;justify-content:center;flex:none;margin-top:1px}
.ck .b.on{border:1px solid var(--c)}.ck .b.on span{color:#fff;font-size:10px;font-weight:800;line-height:1}
.ck .b.off{background:#fff;border:1.5px solid #d3d7dd}
.ck .t{font-size:13.5px;line-height:1.5;color:#363c44}
.ck .t.on{color:#a7adb6;text-decoration:line-through;text-decoration-color:#ccd2d9}
.fgrp{margin-bottom:14px}
.fgh{font-size:12px;font-weight:600;letter-spacing:.02em;color:#9095a0;margin-bottom:7px}
.frow{display:flex;align-items:flex-start;gap:10px;padding:5px 0}
.frow .fic{font-size:13px;line-height:1.5;flex:none;margin-top:1px;color:#9095a0}
.frow .fic.on{color:#15924f}
.frow .fbd{min-width:0}
.frow .ft{font-size:13.5px;line-height:1.5;color:#363c44}
.fsub{margin:4px 0 0;padding-left:16px;list-style:disc}
.fsub li{font-size:12.5px;line-height:1.55;color:#828a96;margin:1px 0}
.dep{display:flex;align-items:flex-start;gap:10px;background:#fbfbfc;border:1px solid #eef0f3;border-radius:9px;padding:10px 12px;margin-bottom:8px}
.dep .tg{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;white-space:nowrap;flex:none}
.dep .tg.blocker{background:#fbeae8;color:#a4352c}.dep .tg.dep{background:#fbf2df;color:#9a6b1e}
.dep .tx{font-size:13px;line-height:1.5;color:#3a4049}
.lnk{display:flex;align-items:center;gap:10px;text-decoration:none;background:#fbfbfc;border:1px solid #eef0f3;border-radius:9px;padding:10px 12px;margin-bottom:7px}
.lnk:hover{background:#f3f5f8;border-color:#e0e3e8}
.lnk .lb2{font-size:13.5px;color:#2b3038;font-weight:500;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lnk .ar{color:#c4c9d0;font-size:13px;flex:none}
.act{display:flex;gap:12px}
.act .col{display:flex;flex-direction:column;align-items:center;flex:none;width:8px;padding-top:4px}
.act .dot{width:8px;height:8px;border-radius:99px;flex:none}
.act .ln{width:2px;flex:1;background:#eef0f3;margin-top:4px;min-height:10px}
.act .bd{flex:1;min-width:0;padding-bottom:16px}
.act .hd{display:flex;align-items:baseline;gap:8px;margin-bottom:3px}
.act .who{font-size:13px;font-weight:600;color:#2b3038}
.act .dt{font-size:11.5px;color:#aab0ba;font-variant-numeric:tabular-nums}
.act .tx{font-size:13px;line-height:1.55;color:#5a616b}
.docs{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:13px}
.doc{display:block;text-decoration:none;background:#fff;border:1px solid #e5e8ec;border-radius:13px;padding:15px 16px;
  box-shadow:0 1px 2px rgba(16,24,40,.04);transition:border-color .15s,box-shadow .15s,transform .12s}
.doc:hover{border-color:#cfd6df;box-shadow:0 6px 20px -10px rgba(16,24,40,.2);transform:translateY(-1px)}
.doc-h{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.doc-label{font-size:14.5px;font-weight:650;color:#1c2128}
.lyr{font-size:11px;font-weight:600;color:#6b7280;background:#f1f3f5;border-radius:6px;padding:2px 8px;white-space:nowrap}
.doc-href{font-family:'JetBrains Mono','SF Mono',ui-monospace,Menlo,monospace;font-size:11.5px;color:#7a828e;word-break:break-all}
.rdr{font-size:12px;color:#9095a0;margin-top:7px}
.mtx{border-collapse:collapse;width:100%;font-size:13.5px}
.mtx th{text-align:left;font-size:11.5px;letter-spacing:.03em;text-transform:uppercase;color:#9095a0;font-weight:600;padding:10px 14px;border-bottom:1px solid #e7eaee}
.mtx td{padding:11px 14px;border-bottom:1px solid #f1f3f5;color:#3a4049;vertical-align:top}
.mtx tr:last-child td{border-bottom:none}
.mtx td.role{font-weight:600;color:#1c2128;white-space:nowrap}
.foot{margin-top:38px;font-size:12px;color:#8a909b;line-height:1.65}
.foot code{font-family:'JetBrains Mono','SF Mono',ui-monospace,Menlo,monospace;font-size:11.5px;
  background:#fff;border:1px solid #e3e5e9;color:#5a6470;padding:1px 6px;border-radius:5px}
@media(max-width:760px){.wrap{padding:28px 16px 70px}.board{padding:22px 16px}.drawer{width:100%}}
"""


# paras() detects ```mermaid blocks and renders them as Mermaid divs.
# All other items render as escaped <p> tags.
JS = r"""
const DATA = __DATA_JSON__;
const PALETTE = ["#6366f1","#8b5cf6","#ec4899","#3b82f6","#f59e0b","#14b8a6","#10b981","#0ea5e9"];
const BADGE = { done:{label:'완료',bg:'#e8f6ee',fg:'#15924f'},
                doing:{label:'진행중',bg:'#e9f1fe',fg:'#1f6fe0'},
                todo:{label:'대기',bg:'#eef0f3',fg:'#828a96'},
                dropped:{label:'폐기',bg:'#fbeae8',fg:'#a4352c'} };
const NEXT = { todo:'doing', doing:'done', done:'todo' };
let sel = null;

function esc(s){ return (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function colorOf(p,i){ return p.color || PALETTE[i % PALETTE.length]; }
function pstats(p){
  const active = p.tasks.filter(t=>!t.hold && t.status!=='dropped');
  const done = active.filter(t=>t.status==='done').length;
  const doing = active.filter(t=>t.status==='doing').length;
  const total = active.length;
  const held = p.tasks.filter(t=>t.hold).length;
  const dropped = p.tasks.filter(t=>t.status==='dropped' && !t.hold).length;
  return { done, doing, total, held, dropped, pct: total?Math.round(done/total*100):0 };
}
function overall(){
  let d=0,g=0,tot=0,held=0,dropped=0;
  DATA.phases.forEach(p=>{ const s=pstats(p); d+=s.done; g+=s.doing; tot+=s.total; held+=s.held; dropped+=s.dropped; });
  return { done:d, doing:g, todo:tot-d-g, total:tot, held, dropped, pct: tot?Math.round(d/tot*100):0 };
}
function chk(status, hold, color){
  if(hold) return `<div class="chk held"></div>`;
  if(status==='dropped') return `<div class="chk dropped"><span>✕</span></div>`;
  if(status==='done') return `<div class="chk done" style="background:${color}"><span>✓</span></div>`;
  if(status==='doing') return `<div class="chk doing" style="color:${color}"><span>•</span></div>`;
  return `<div class="chk todo"></div>`;
}
function badge(status, hold){
  if(hold) return `<span class="bdg held">보류</span>`;
  const b = BADGE[status] || BADGE.todo;
  return `<span class="bdg ${status}">${b.label}</span>`;
}

function paras(desc){
  if(!desc) return '';
  const arr = Array.isArray(desc) ? desc : [desc];
  return arr.map(d => {
    const m = d.match(/^```mermaid\s*\n([\s\S]+?)\n```\s*$/);
    if (m) return `<div class="mermaid">${esc(m[1])}</div>`;
    return `<p>${esc(d)}</p>`;
  }).join('');
}

function checklist(items, color, kind){
  return items.map((it,i)=>{
    const on = !!it.done;
    return `<div class="ck" data-${kind}="${i}" style="--c:${color}">
      <div class="b ${on?'on':'off'}" ${on?`style="background:${color}"`:''}><span>${on?'✓':''}</span></div>
      <span class="t ${on?'on':''}">${esc(it.text)}</span></div>`;
  }).join('');
}

function featureView(groups){
  return groups.map(g=>{
    const rows = (g.items||[]).map(it=>{
      const on = !!it.done;
      const subs = (it.sub||[]).length
        ? `<ul class="fsub">${it.sub.map(s=>`<li>${esc(s)}</li>`).join('')}</ul>` : '';
      return `<div class="frow"><span class="fic ${on?'on':''}">${on?'✓':'◐'}</span>
        <div class="fbd"><span class="ft">${esc(it.t)}</span>${subs}</div></div>`;
    }).join('');
    return `<div class="fgrp"><div class="fgh">${esc(g.name||'')}</div>${rows}</div>`;
  }).join('');
}

function renderSummary(){
  const m = overall();
  const heldChip = m.held ? `<div class="chip"><i style="background:#d8b878"></i><span class="lb">보류</span><span class="n">${m.held}</span></div>` : '';
  const droppedChip = m.dropped ? `<div class="chip"><i style="background:#a4352c"></i><span class="lb">폐기</span><span class="n">${m.dropped}</span></div>` : '';
  const start = DATA.startDate ? `<div class="chip"><span class="lb">시작</span><span class="n" style="font-size:13px">${esc(DATA.startDate)}</span></div>` : '';
  document.getElementById('summary').innerHTML = `
    <div class="summary">
      <div class="pg">
        <div class="r"><span class="l">전체 진행률</span><span class="v">${m.done}/${m.total} 완료 · ${m.pct}%</span></div>
        <div class="track"><i style="width:${m.pct}%"></i></div>
      </div>
      <div class="chips">
        <div class="chip"><i style="background:#15924f"></i><span class="lb">완료</span><span class="n">${m.done}</span></div>
        <div class="chip"><i style="background:#1f6fe0"></i><span class="lb">진행중</span><span class="n">${m.doing}</span></div>
        <div class="chip"><i style="background:#9aa1ac"></i><span class="lb">대기</span><span class="n">${m.todo}</span></div>
        ${heldChip}${droppedChip}${start}
      </div>
    </div>`;
}

function renderFocus(){
  const focusEl = document.getElementById('focus');
  const blockers = [], nexts = [];
  DATA.phases.forEach(p => p.tasks.forEach(t => {
    if(t.hold) return;
    if((t.deps||[]).some(d=>d.tag==='blocker')) blockers.push(t.title);
    if(t.status==='doing') nexts.push(t.title);
  }));
  if(!blockers.length && !nexts.length){ focusEl.innerHTML=''; return; }
  const bHtml = blockers.length ? `<div class="fc block"><span class="ic">🚫</span><div class="bd"><div class="k">블로커</div>
    <div class="v">${blockers.slice(0,2).map(esc).join('<br>')}</div></div></div>` : '';
  const nHtml = nexts.length ? `<div class="fc"><span class="ic">▶</span><div class="bd"><div class="k">진행중</div>
    <div class="v">${nexts.slice(0,3).map(esc).join('<br>')}</div></div></div>` : '';
  focusEl.innerHTML = `<div class="focus">${bHtml}${nHtml}</div>`;
}

function renderBoard(){
  document.getElementById('board').innerHTML = DATA.phases.map((p,pi)=>{
    const color = colorOf(p, pi);
    const s = pstats(p);
    const held = (s.held ? ` · 보류 ${s.held}` : '') + (s.dropped ? ` · 폐기 ${s.dropped}` : '');
    const tasks = (p.tasks||[]).map((t,ti)=>{
      const period = t.period ? `<span class="per">${esc(t.period)}</span>` : '';
      return `<div class="task" data-open="${pi}.${ti}">
        <div data-check="${pi}.${ti}" style="--c:${color}">${chk(t.status, t.hold, color)}</div>
        <span class="txt ${t.hold?'':''}${t.status==='done'?'done':''}">${esc(t.title)}</span>
        <span class="sp"></span>${period}${badge(t.status, t.hold)}
        <span class="chev">›</span></div>`;
    }).join('');
    return `<div class="row">
      <div class="rail"><div class="node" style="background:${color}">${pi+1}</div><div class="line"></div></div>
      <div class="pbody">
        <div class="ph"><span class="nm">${esc(p.name||'')}</span><span class="ct">${s.done}/${s.total} 완료 · ${s.pct}%${held}</span></div>
        <div class="pbar"><i style="width:${s.pct}%;background:${color}"></i></div>
        <div class="list">${tasks}</div>
      </div></div>`;
  }).join('');
}

function renderDrawer(){
  const host = document.getElementById('drawer');
  if(!sel){ host.innerHTML=''; return; }
  const p = DATA.phases[sel.pi], t = p.tasks[sel.ti], color = colorOf(p, sel.pi);

  const tags = [];
  if(t.ticket) tags.push(`<span class="tkt">${esc(t.ticket)}</span>`);
  if(t.priority){ const k=({P0:'p0',P1:'p1',P2:'p2'})[t.priority]||''; tags.push(`<span class="prio ${k}">${esc(t.priority)}</span>`); }
  (t.labels||[]).forEach(l=>tags.push(`<span class="lab">${esc(l)}</span>`));
  const tagsRow = tags.length ? `<div class="tags">${tags.join('')}</div>` : '';

  const sbtns = ['todo','doing','done'].map(st=>
    `<div class="sbtn ${t.status===st?'on '+st:''}" data-status="${st}">${BADGE[st].label}</div>`).join('');

  const meta = [];
  if(t.owner) meta.push(`<div class="mr"><span class="k">담당자</span><span class="mv">${esc(t.owner)}</span></div>`);
  if(t.period) meta.push(`<div class="mr"><span class="k">기간</span><span class="mv">${esc(t.period)}</span></div>`);
  if(t.estimate) meta.push(`<div class="mr"><span class="k">예상 공수</span><span class="mv">${esc(t.estimate)}</span></div>`);
  if(t.reason) meta.push(`<div class="mr"><span class="k">사유</span><span class="mv">${esc(t.reason)}</span></div>`);
  const metaBlock = meta.length ? `<div class="meta">${meta.join('')}</div>` : '';

  const descBlock = t.desc ? `<div class="dsec"><div class="k">설명</div>${paras(t.desc)}</div>` : '';

  const crit = (t.criteria||[]);
  const critBlock = crit.length ? `<div class="dsec">
    <div class="kh"><span class="k">인수 조건</span><span class="c">${crit.filter(c=>c.done).length}/${crit.length}</span></div>
    ${checklist(crit, color, 'crit')}</div>` : '';

  const subs = (t.subs||[]);
  const subBlock = subs.length ? `<div class="dsec">
    <div class="kh"><span class="k">세부 작업</span><span class="c">${subs.filter(s=>s.done).length}/${subs.length}</span></div>
    ${checklist(subs, color, 'sub')}</div>` : '';

  const feats = (t.features||[]);
  const featItems = feats.flatMap(g=>g.items||[]);
  const featBlock = feats.length ? `<div class="dsec">
    <div class="kh"><span class="k">실제 기능</span><span class="c">${featItems.filter(f=>f.done).length}/${featItems.length}</span></div>
    ${featureView(feats)}</div>` : '';

  const deps = (t.deps||[]);
  const depBlock = deps.length ? `<div class="dsec"><div class="k">의존성 · 블로커</div>
    ${deps.map(d=>{const k=d.tag==='blocker'?'blocker':'dep';
      return `<div class="dep"><span class="tg ${k}">${esc(d.tag||'관련')}</span><span class="tx">${esc(d.text)}</span></div>`;}).join('')}</div>` : '';

  const links = (t.links||[]);
  const linkBlock = links.length ? `<div class="dsec"><div class="k">연결된 항목</div>
    ${links.map(l=>`<a class="lnk" href="${esc(l.url||'#')}" target="_blank" rel="noopener">
      <span class="lb2">${esc(l.label||l.url||'')}</span><span class="ar">↗</span></a>`).join('')}</div>` : '';

  const act = (t.activity||[]);
  const actBlock = act.length ? `<div class="dsec"><div class="k">활동</div>
    ${act.map((a,i)=>`<div class="act"><div class="col"><span class="dot" style="background:${color}"></span>${i<act.length-1?'<span class="ln"></span>':''}</div>
      <div class="bd"><div class="hd"><span class="who">${esc(a.who||'')}</span><span class="dt">${esc(a.date||'')}</span></div><div class="tx">${esc(a.text||'')}</div></div></div>`).join('')}</div>` : '';

  host.innerHTML = `
    <div class="overlay" data-close></div>
    <div class="drawer">
      <div class="dhead"><div class="pl"><i style="background:${color}"></i><span>${esc(p.name)} 단계</span></div>
        <div class="dclose" data-close>✕</div></div>
      <div class="dbody">
        ${tagsRow}<h2>${esc(t.title||'')}</h2>
        <div class="sbtns">${sbtns}</div>
        ${metaBlock}${descBlock}${critBlock}${subBlock}${featBlock}${depBlock}${linkBlock}${actBlock}
      </div>
    </div>`;
  // Re-initialize Mermaid for newly injected diagrams
  if(window.mermaid) mermaid.run({ nodes: host.querySelectorAll('.mermaid') });
}

function render(){ renderSummary(); renderFocus(); renderBoard(); renderDrawer(); }

document.addEventListener('click', e=>{
  if(e.target.closest('[data-close]')){ sel=null; renderDrawer(); return; }
  if(sel){
    const sb = e.target.closest('[data-status]');
    if(sb){ DATA.phases[sel.pi].tasks[sel.ti].status = sb.dataset.status; render(); return; }
    const cr = e.target.closest('[data-crit]');
    if(cr){ const c=DATA.phases[sel.pi].tasks[sel.ti].criteria[+cr.dataset.crit]; c.done=!c.done; renderDrawer(); return; }
    const su = e.target.closest('[data-sub]');
    if(su){ const s=DATA.phases[sel.pi].tasks[sel.ti].subs[+su.dataset.sub]; s.done=!s.done; renderDrawer(); return; }
  }
  const cyc = e.target.closest('[data-check]');
  if(cyc){ const [pi,ti]=cyc.dataset.check.split('.').map(Number); const t=DATA.phases[pi].tasks[ti];
    if(!t.hold && NEXT[t.status]){ t.status = NEXT[t.status]; render(); } return; }
  const open = e.target.closest('[data-open]');
  if(open){ const [pi,ti]=open.dataset.open.split('.').map(Number); sel={pi,ti}; renderDrawer(); return; }
});
document.addEventListener('keydown', e=>{ if(e.key==='Escape' && sel){ sel=null; renderDrawer(); } });
render();
if(window.mermaid) mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
"""


def build_html(data: dict) -> str:
    label = data.get("label", data.get("issue", ""))
    title = data.get("title", label or "Feature Roadmap")
    lead = data.get("lead", "Click any task to see details. Checkboxes cycle todo → doing → done (browser-only).")
    klabel = f"Feature Roadmap · {esc(label)}" if label else "Feature Roadmap"
    lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
    docs_html = render_docs(data.get("docs") or [])
    stake_html = render_stakeholders(data.get("stakeholders") or [])

    safe_json = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
    script = JS.replace("__DATA_JSON__", safe_json)

    return (
        f'<!DOCTYPE html>\n<html lang="ko">\n<head>\n'
        f'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{esc(label + " — " if label else "")}{esc(title)} · 로드맵</title>\n'
        f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css">\n'
        f'<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>\n'
        f'<style>{CSS}</style>\n</head>\n<body>\n'
        f'<div class="wrap">\n'
        f'  <div class="klabel">{klabel}</div>\n'
        f'  <h1>{esc(title)}</h1>\n'
        f'  {lead_html}\n'
        f'  <div id="summary"></div>\n'
        f'  <div id="focus"></div>\n'
        f'  <div class="seclab">기능 개발 로드맵</div>\n'
        f'  <div class="panel"><div class="board" id="board"></div></div>\n'
        f'  {docs_html}\n'
        f'  {stake_html}\n'
        f'  <div class="foot">Checkbox state is preview-only and not saved. '
        f'Regenerate after updating <code>roadmap.json</code>.</div>\n'
        f'</div>\n<div id="drawer"></div>\n'
        f'<script>{script}</script>\n</body>\n</html>'
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="roadmap.json → index.html renderer with Mermaid support")
    ap.add_argument("data", help="path to roadmap.json")
    ap.add_argument("--out", help="output path (default: index.html next to input)")
    ap.add_argument("--skip-validate", action="store_true", help="skip schema validation")
    args = ap.parse_args(argv)

    data_path = Path(args.data)
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"✗ not found: {data_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"✗ JSON parse error: {e}", file=sys.stderr)
        return 2

    if not args.skip_validate and SCHEMA_PATH.exists():
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        errors = validate(schema, data)
        if errors:
            print(f"✗ schema invalid ({len(errors)} errors):", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            return 1

    out = Path(args.out) if args.out else data_path.parent / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(data), encoding="utf-8")

    ov = overall_stats(data.get("phases") or [])
    print(f"✓ {out}  (phases={len(data.get('phases') or [])}, "
          f"docs={len(data.get('docs') or [])}, "
          f"progress={ov['done']}/{ov['total']} {ov['pct']}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
