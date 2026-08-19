"""Digest and dashboard rendering.

Summaries are the publisher's own words, truncated - never paraphrased and
never generated. If a source gave us no description, the digest says so rather
than filling the gap.
"""

from __future__ import annotations

import html
import json
import sqlite3
from collections import OrderedDict
from datetime import datetime, timezone

JURIS_ORDER = ["UK", "EU", "Global"]
CAT_ORDER = [
    "Legislation", "Sanctions", "Enforcement", "Guidance", "Consultation",
    "Typology", "Regulator", "Supervision", "Policy", "Registry",
    "Standards", "Commentary", "News",
]
PRIORITY_MARK = {"High": "!!", "Medium": "!", "Low": ""}


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "date not stated by source"
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except ValueError:
        return iso[:10]


def _group(rows: list[sqlite3.Row]) -> OrderedDict:
    out: OrderedDict = OrderedDict()
    for j in JURIS_ORDER:
        block = [r for r in rows if r["jurisdiction"] == j]
        if not block:
            continue
        cats: OrderedDict = OrderedDict()
        for c in CAT_ORDER:
            sub = [r for r in block if r["category"] == c]
            if sub:
                cats[c] = sub
        placed = {id(r) for sub in cats.values() for r in sub}
        rest = [r for r in block if id(r) not in placed]
        if rest:
            cats.setdefault("Other", []).extend(rest)
        out[j] = cats
    placed_j = {id(r) for cats in out.values() for sub in cats.values() for r in sub}
    leftovers = [r for r in rows if id(r) not in placed_j]
    if leftovers:
        out["Other"] = OrderedDict({"Other": leftovers})
    return out


# ------------------------------------------------------------------ markdown

def render_markdown(
    rows: list[sqlite3.Row],
    kind: str,
    generated: str,
    typology_names: dict[str, str],
    window_note: str = "",
    held_back: int = 0,
) -> str:
    date_str = datetime.now(timezone.utc).strftime("%A %d %B %Y")
    L: list[str] = []
    L.append(f"# Argus FinCrime - {kind} digest")
    L.append(f"**{date_str}**  ·  {len(rows)} item(s)"
             + (f"  ·  {window_note}" if window_note else ""))
    L.append("")
    if held_back:
        L.append(f"> {held_back} further lower-priority item(s) were collected and are "
                 "not shown here, to keep this readable. They are all in "
                 "`dashboard.html` (searchable), or raise the cap with "
                 "`python argus.py digest --limit 0`.")
        L.append("")

    if not rows:
        L.append("No new relevant items since the last run. Sources were polled "
                 "successfully; nothing crossed the relevance threshold.")
        L.append("")
        L.append("---")
        L.append(f"<sub>Generated {generated} · every item links to its original "
                 "source · no text is AI-generated</sub>")
        return "\n".join(L)

    high = [r for r in rows if r["priority"] == "High"]
    if high:
        L.append("## Read first")
        L.append("")
        for r in high[:8]:
            L.append(f"- **[{r['title']}]({r['url']})** — {r['source_name']}"
                     + ("  ⏱ *has a date/deadline*" if r["has_deadline"] else ""))
        L.append("")

    grouped = _group(rows)
    for juris, cats in grouped.items():
        L.append(f"## {juris}")
        L.append("")
        for cat, items in cats.items():
            L.append(f"### {cat}")
            L.append("")
            for r in items:
                mark = PRIORITY_MARK.get(r["priority"], "")
                head = f"**[{r['title']}]({r['url']})**"
                if mark:
                    head = f"{mark} {head}"
                L.append(f"- {head}")
                meta = [r["source_name"], _fmt_date(r["published_at"])]
                if r["publisher"] and r["publisher"] not in r["source_name"]:
                    meta.append(r["publisher"])
                L.append(f"  <br>`{' · '.join(meta)}`")
                if r["summary_raw"]:
                    L.append(f"  <br>{r['summary_raw']}")
                else:
                    L.append("  <br>*(source published no summary text — open the link)*")
                tids = json.loads(r["typologies"] or "[]")
                if tids:
                    names = ", ".join(
                        f"`{typology_names.get(t, t)}`" for t in tids
                    )
                    ids = " ".join(tids)
                    L.append(f"  <br>↳ Related typology: {names} "
                             f"— explain with `python argus.py explain {tids[0]}`")
                L.append("")
        L.append("")

    L.append("---")
    L.append("")
    L.append("**Legend** — `!!` high priority (tier-1 regulator legislation, "
             "enforcement or sanctions) · `!` medium · ⏱ contains a date or deadline.")
    L.append("")
    L.append(f"<sub>Generated {generated}. Every item links to its original source. "
             "Summary text is quoted verbatim from the publisher's own feed and is "
             "not AI-generated or paraphrased.</sub>")
    return "\n".join(L)


# ---------------------------------------------------------------- dashboard

_CSS = """
:root{--bg:#fbfbfa;--panel:#fff;--ink:#1a1a18;--muted:#63635e;--line:#e4e4df;
--accent:#8a4b2a;--hi:#a33520;--med:#8a6d1f;--chip:#f0efeb;--shadow:0 1px 2px rgba(0,0,0,.05)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#16150f;--panel:#1e1d17;
--ink:#eceae2;--muted:#a2a096;--line:#33322a;--accent:#d99b6c;--hi:#e8836a;--med:#d8b65e;
--chip:#2a291f;--shadow:0 1px 2px rgba(0,0,0,.3)}}
:root[data-theme=dark]{--bg:#16150f;--panel:#1e1d17;--ink:#eceae2;--muted:#a2a096;
--line:#33322a;--accent:#d99b6c;--hi:#e8836a;--med:#d8b65e;--chip:#2a291f;--shadow:0 1px 2px rgba(0,0,0,.3)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:1.5rem;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:.85rem;margin-bottom:20px}
.controls{position:sticky;top:0;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--line);
margin-bottom:18px;z-index:5;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input[type=search]{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--line);
border-radius:8px;background:var(--panel);color:var(--ink);font-size:.9rem}
button{padding:7px 12px;border:1px solid var(--line);border-radius:999px;background:var(--panel);
color:var(--muted);font-size:.8rem;cursor:pointer}
button.on{background:var(--accent);color:var(--bg);border-color:var(--accent);font-weight:600}
.item{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;
margin-bottom:10px;box-shadow:var(--shadow)}
.item.p-High{border-left:3px solid var(--hi)}
.item.p-Medium{border-left:3px solid var(--med)}
.item a.t{color:var(--ink);text-decoration:none;font-weight:600;font-size:.98rem}
.item a.t:hover{color:var(--accent);text-decoration:underline}
.meta{color:var(--muted);font-size:.76rem;margin:5px 0 7px;font-variant-numeric:tabular-nums}
.desc{font-size:.87rem;color:var(--ink);opacity:.9}
.chips{margin-top:8px;display:flex;gap:5px;flex-wrap:wrap}
.chip{background:var(--chip);color:var(--muted);border-radius:999px;padding:2px 9px;font-size:.7rem}
.chip.ty{color:var(--accent);font-weight:600}
.sec{margin:26px 0 10px;font-size:.75rem;letter-spacing:.09em;text-transform:uppercase;
color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:5px}
.empty{color:var(--muted);padding:30px;text-align:center;border:1px dashed var(--line);border-radius:10px}
footer{margin-top:40px;color:var(--muted);font-size:.76rem;border-top:1px solid var(--line);padding-top:14px}
a{color:var(--accent)}
"""

_JS = """
const items=[...document.querySelectorAll('.item')];
const q=document.getElementById('q');
let f={j:'all',p:'all'};
function apply(){
  const s=(q.value||'').toLowerCase().trim();
  let n=0;
  items.forEach(el=>{
    const okJ=f.j==='all'||el.dataset.j===f.j;
    const okP=f.p==='all'||el.dataset.p===f.p;
    const okS=!s||el.dataset.search.includes(s);
    const show=okJ&&okP&&okS;
    el.style.display=show?'':'none';
    if(show)n++;
  });
  document.querySelectorAll('.sec').forEach(h=>{
    let sib=h.nextElementSibling,any=false;
    while(sib&&!sib.classList.contains('sec')){
      if(sib.classList.contains('item')&&sib.style.display!=='none')any=true;
      sib=sib.nextElementSibling;
    }
    h.style.display=any?'':'none';
  });
  document.getElementById('count').textContent=n+' shown';
  document.getElementById('none').style.display=n?'none':'';
}
q.addEventListener('input',apply);
document.querySelectorAll('button[data-k]').forEach(b=>{
  b.addEventListener('click',()=>{
    const k=b.dataset.k;
    document.querySelectorAll(`button[data-k="${k}"]`).forEach(x=>x.classList.remove('on'));
    b.classList.add('on');f[k]=b.dataset.v;apply();
  });
});
apply();
"""


def render_dashboard(
    rows: list[sqlite3.Row],
    generated: str,
    typology_names: dict[str, str],
    title: str = "Argus FinCrime",
) -> str:
    e = html.escape
    parts: list[str] = []
    parts.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    parts.append(f"<title>{e(title)}</title><style>{_CSS}</style></head><body><div class='wrap'>")
    parts.append(f"<h1>{e(title)}</h1>")
    parts.append(f"<div class='sub'>{len(rows)} relevant item(s) · generated {e(generated)} · "
                 "every entry links to its original source</div>")

    parts.append("<div class='controls'>")
    parts.append("<input type='search' id='q' placeholder='Search titles, summaries, typologies…'>")
    for k, label, vals in [
        ("j", "Jurisdiction", ["all", "UK", "EU", "Global"]),
        ("p", "Priority", ["all", "High", "Medium", "Low"]),
    ]:
        for v in vals:
            on = " on" if v == "all" else ""
            parts.append(f"<button class='{on.strip()}' data-k='{k}' data-v='{v}'>"
                         f"{e(v if v != 'all' else 'All ' + label.lower())}</button>")
    parts.append("<span class='chip' id='count'></span></div>")

    grouped = _group(rows)
    for juris, cats in grouped.items():
        for cat, group in cats.items():
            parts.append(f"<div class='sec'>{e(juris)} · {e(cat)}</div>")
            for r in group:
                tids = json.loads(r["typologies"] or "[]")
                blob = " ".join(filter(None, [
                    r["title"], r["summary_raw"] or "", r["source_name"],
                    r["publisher"] or "", " ".join(typology_names.get(t, t) for t in tids),
                ])).lower()
                parts.append(
                    f"<div class='item p-{e(r['priority'])}' data-j='{e(r['jurisdiction'])}' "
                    f"data-p='{e(r['priority'])}' data-search='{e(blob)}'>"
                )
                parts.append(f"<a class='t' href='{e(r['url'])}' target='_blank' rel='noopener'>"
                             f"{e(r['title'])}</a>")
                meta = [r["source_name"], _fmt_date(r["published_at"])]
                if r["publisher"] and r["publisher"] not in r["source_name"]:
                    meta.append(r["publisher"])
                parts.append(f"<div class='meta'>{e(' · '.join(meta))}"
                             + (" · ⏱ date/deadline" if r["has_deadline"] else "") + "</div>")
                if r["summary_raw"]:
                    parts.append(f"<div class='desc'>{e(r['summary_raw'])}</div>")
                else:
                    parts.append("<div class='desc' style='opacity:.55'>"
                                 "(source published no summary — open the link)</div>")
                parts.append("<div class='chips'>")
                parts.append(f"<span class='chip'>{e(r['priority'])}</span>")
                parts.append(f"<span class='chip'>{e(r['category'])}</span>")
                for t in tids:
                    parts.append(f"<span class='chip ty'>{e(typology_names.get(t, t))}</span>")
                parts.append("</div></div>")

    parts.append("<div class='empty' id='none' style='display:none'>Nothing matches those filters.</div>")
    parts.append("<footer>Summary text is quoted verbatim from each publisher's own feed. "
                 "Nothing on this page is AI-generated or paraphrased. Run "
                 "<code>python argus.py verify</code> to re-check that every cited link is live."
                 "</footer>")
    parts.append(f"</div><script>{_JS}</script></body></html>")
    return "".join(parts)
