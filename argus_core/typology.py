"""Typology library: load, match, explain, render."""

import html
import textwrap
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Typology:
    id: str
    name: str
    aka: list[str]
    family: str
    summary: str
    mechanics: list[str]
    bank_impact: str
    red_flags: list[str]
    how_to_spot: list[str]
    analyst_actions: list[str]
    keywords: list[str]
    sources: list[dict]


def load(path: str | Path) -> dict[str, Typology]:
    data = tomllib.load(open(path, "rb"))
    out: dict[str, Typology] = {}
    for t in data.get("typology", []):
        out[t["id"]] = Typology(
            id=t["id"],
            name=t["name"],
            aka=t.get("aka", []),
            family=t.get("family", "General"),
            summary=" ".join(t.get("summary", "").split()),
            mechanics=t.get("mechanics", []),
            bank_impact=" ".join(t.get("bank_impact", "").split()),
            red_flags=t.get("red_flags", []),
            how_to_spot=t.get("how_to_spot", []),
            analyst_actions=t.get("analyst_actions", []),
            keywords=t.get("keywords", []),
            sources=t.get("sources", []),
        )
    return out


def keyword_index(lib: dict[str, Typology]) -> dict[str, list[str]]:
    return {tid: t.keywords for tid, t in lib.items()}


def names(lib: dict[str, Typology]) -> dict[str, str]:
    return {tid: t.name for tid, t in lib.items()}


def find(lib: dict[str, Typology], term: str) -> list[Typology]:
    """Exact id first, then name/aka/keyword substring."""
    term = term.strip().lower()
    if term in lib:
        return [lib[term]]
    hits = []
    for t in lib.values():
        hay = " ".join([t.id, t.name, *t.aka, *t.keywords, t.family]).lower()
        if term in hay:
            hits.append(t)
    return hits


# ------------------------------------------------------------------ terminal

def _wrap(s: str, width: int = 78, indent: str = "  ") -> str:
    return "\n".join(textwrap.wrap(s, width=width, initial_indent=indent,
                                   subsequent_indent=indent))


def to_text(t: Typology) -> str:
    L: list[str] = []
    L.append("=" * 78)
    L.append(t.name.upper())
    if t.aka:
        L.append("also called: " + ", ".join(t.aka))
    L.append(f"family: {t.family}   id: {t.id}")
    L.append("=" * 78)
    L.append("")
    L.append("WHAT IT IS")
    L.append(_wrap(t.summary))
    L.append("")
    L.append("HOW IT WORKS")
    for i, m in enumerate(t.mechanics, 1):
        L.append(_wrap(f"{i}. {m}", indent="  ")[:0] + textwrap.fill(
            f"{i}. {m}", width=78, initial_indent="  ", subsequent_indent="     "))
    L.append("")
    L.append("IMPACT ON BANKS")
    L.append(_wrap(t.bank_impact))
    L.append("")
    L.append("RED FLAGS")
    for r in t.red_flags:
        L.append(textwrap.fill(f"- {r}", width=78, initial_indent="  ",
                               subsequent_indent="    "))
    L.append("")
    L.append("HOW TO SPOT IT")
    for h in t.how_to_spot:
        L.append(textwrap.fill(f"- {h}", width=78, initial_indent="  ",
                               subsequent_indent="    "))
    L.append("")
    L.append("WHAT TO DO AS THE ANALYST")
    for a in t.analyst_actions:
        L.append(textwrap.fill(f"- {a}", width=78, initial_indent="  ",
                               subsequent_indent="    "))
    L.append("")
    L.append("SOURCES")
    for s in t.sources:
        L.append(f"  - {s.get('title','')}")
        L.append(f"    {s.get('url','')}")
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------ markdown

def to_markdown(lib: dict[str, Typology]) -> str:
    fams: dict[str, list[Typology]] = {}
    for t in lib.values():
        fams.setdefault(t.family, []).append(t)

    L: list[str] = ["# FinCrime typology reference", ""]
    L.append(f"{len(lib)} typologies, grouped by family. Every entry cites primary "
             "sources; run `python argus.py verify --typologies` to confirm each "
             "cited link is still live.")
    L.append("")
    L.append("## Contents")
    L.append("")
    for fam in sorted(fams):
        L.append(f"**{fam}**")
        for t in sorted(fams[fam], key=lambda x: x.name):
            anchor = t.name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            anchor = anchor.replace(",", "").replace("'", "").replace("/", "").replace(".", "")
            L.append(f"- [{t.name}](#{anchor}) — `{t.id}`")
        L.append("")

    for fam in sorted(fams):
        L.append(f"---\n\n# {fam}\n")
        for t in sorted(fams[fam], key=lambda x: x.name):
            L.append(f"## {t.name}")
            L.append("")
            if t.aka:
                L.append(f"*Also called: {', '.join(t.aka)}*  ·  id `{t.id}`")
                L.append("")
            L.append(t.summary)
            L.append("")
            L.append("**How it works**")
            L.append("")
            for i, m in enumerate(t.mechanics, 1):
                L.append(f"{i}. {m}")
            L.append("")
            L.append("**Impact on banks**")
            L.append("")
            L.append(t.bank_impact)
            L.append("")
            L.append("**Red flags**")
            L.append("")
            for r in t.red_flags:
                L.append(f"- {r}")
            L.append("")
            L.append("**How to spot it**")
            L.append("")
            for h in t.how_to_spot:
                L.append(f"- {h}")
            L.append("")
            L.append("**What to do as the analyst**")
            L.append("")
            for a in t.analyst_actions:
                L.append(f"- {a}")
            L.append("")
            L.append("**Sources**")
            L.append("")
            for s in t.sources:
                L.append(f"- [{s.get('title','')}]({s.get('url','')})")
            L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------- html

def to_html(lib: dict[str, Typology], generated: str) -> str:
    from .digest import _CSS  # reuse the palette

    e = html.escape
    fams: dict[str, list[Typology]] = {}
    for t in lib.values():
        fams.setdefault(t.family, []).append(t)

    extra = """
.ty{background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:18px 20px;margin-bottom:14px;box-shadow:var(--shadow)}
.ty h3{margin:0 0 3px;font-size:1.05rem}
.aka{color:var(--muted);font-size:.78rem;margin-bottom:10px}
.ty h4{margin:14px 0 6px;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;color:var(--accent)}
.ty ol,.ty ul{margin:0;padding-left:20px}
.ty li{margin-bottom:4px;font-size:.88rem}
.flag li::marker{color:var(--hi)}
"""
    P: list[str] = []
    P.append("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    P.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    P.append("<title>Argus FinCrime - typology reference</title>")
    P.append(f"<style>{_CSS}{extra}</style></head><body><div class='wrap'>")
    P.append("<h1>FinCrime typology reference</h1>")
    P.append(f"<div class='sub'>{len(lib)} typologies · generated {e(generated)} · "
             "every entry cites primary sources</div>")
    P.append("<div class='controls'><input type='search' id='q' "
             "placeholder='Search typologies, red flags, keywords…'>"
             "<span class='chip' id='count'></span></div>")

    for fam in sorted(fams):
        P.append(f"<div class='sec'>{e(fam)}</div>")
        for t in sorted(fams[fam], key=lambda x: x.name):
            blob = " ".join([t.name, *t.aka, *t.keywords, t.summary, t.bank_impact,
                             *t.mechanics, *t.red_flags, *t.how_to_spot]).lower()
            P.append(f"<div class='ty item' data-j='all' data-p='all' data-search='{e(blob)}'>")
            P.append(f"<h3>{e(t.name)}</h3>")
            aka = f"Also called: {', '.join(t.aka)} · " if t.aka else ""
            P.append(f"<div class='aka'>{e(aka)}id <code>{e(t.id)}</code></div>")
            P.append(f"<div class='desc'>{e(t.summary)}</div>")
            P.append("<h4>How it works</h4><ol>")
            for m in t.mechanics:
                P.append(f"<li>{e(m)}</li>")
            P.append("</ol><h4>Impact on banks</h4>")
            P.append(f"<div class='desc'>{e(t.bank_impact)}</div>")
            P.append("<h4>Red flags</h4><ul class='flag'>")
            for r in t.red_flags:
                P.append(f"<li>{e(r)}</li>")
            P.append("</ul><h4>How to spot it</h4><ul>")
            for h in t.how_to_spot:
                P.append(f"<li>{e(h)}</li>")
            P.append("</ul><h4>What to do as the analyst</h4><ul>")
            for a in t.analyst_actions:
                P.append(f"<li>{e(a)}</li>")
            P.append("</ul><h4>Sources</h4><ul>")
            for s in t.sources:
                P.append(f"<li><a href='{e(s.get('url',''))}' target='_blank' "
                         f"rel='noopener'>{e(s.get('title',''))}</a></li>")
            P.append("</ul></div>")

    P.append("<div class='empty' id='none' style='display:none'>No typology matches.</div>")
    P.append("<footer>Compiled reference for KYC/AML analyst use. Each entry cites its "
             "primary sources — follow the links rather than relying on this summary alone."
             "</footer>")
    js = """
const items=[...document.querySelectorAll('.ty')];const q=document.getElementById('q');
function apply(){const s=(q.value||'').toLowerCase().trim();let n=0;
items.forEach(el=>{const show=!s||el.dataset.search.includes(s);
el.style.display=show?'':'none';if(show)n++;});
document.querySelectorAll('.sec').forEach(h=>{let sib=h.nextElementSibling,any=false;
while(sib&&!sib.classList.contains('sec')){if(sib.classList.contains('ty')&&sib.style.display!=='none')any=true;
sib=sib.nextElementSibling;}h.style.display=any?'':'none';});
document.getElementById('count').textContent=n+' shown';
document.getElementById('none').style.display=n?'none':'';}
q.addEventListener('input',apply);apply();
"""
    P.append(f"</div><script>{js}</script></body></html>")
    return "".join(P)
