"""Real case library: load, index, search.

Cases live in cases.toml, linked to typologies by id. Kept separate from
typologies.toml because one case usually illustrates several typologies, and
because new cases get appended far more often than typologies change.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Case:
    id: str
    name: str
    year: str
    jurisdiction: str
    headline: str
    typology_ids: list[str]
    backstory: str
    what_happened: str
    bank_impact: str
    analyst_lesson: str
    sources: list[dict] = field(default_factory=list)


def _clean(s: str) -> str:
    """Collapse the hard-wrapped TOML blocks into flowing paragraphs."""
    paras = [" ".join(p.split()) for p in s.strip().split("\n\n")]
    return "\n\n".join(p for p in paras if p)


def load(path: str | Path) -> dict[str, Case]:
    data = tomllib.load(open(path, "rb"))
    out: dict[str, Case] = {}
    for c in data.get("case", []):
        out[c["id"]] = Case(
            id=c["id"],
            name=c["name"],
            year=c.get("year", ""),
            jurisdiction=c.get("jurisdiction", ""),
            headline=c.get("headline", ""),
            typology_ids=c.get("typology_ids", []),
            backstory=_clean(c.get("backstory", "")),
            what_happened=_clean(c.get("what_happened", "")),
            bank_impact=_clean(c.get("bank_impact", "")),
            analyst_lesson=_clean(c.get("analyst_lesson", "")),
            sources=c.get("sources", []),
        )
    return out


def by_typology(lib: dict[str, Case]) -> dict[str, list[Case]]:
    """Index cases against the typologies they illustrate."""
    idx: dict[str, list[Case]] = {}
    for c in lib.values():
        for tid in c.typology_ids:
            idx.setdefault(tid, []).append(c)
    return idx


def find(lib: dict[str, Case], term: str) -> list[Case]:
    term = term.strip().lower()
    if not term:
        return list(lib.values())
    if term in lib:
        return [lib[term]]
    hits = []
    for c in lib.values():
        hay = " ".join([
            c.id, c.name, c.year, c.jurisdiction, c.headline,
            c.backstory, c.what_happened, c.bank_impact, c.analyst_lesson,
            *c.typology_ids,
        ]).lower()
        if all(w in hay for w in term.split()):
            hits.append(c)
    return hits


def to_text(c: Case, typology_names: dict[str, str] | None = None) -> str:
    import textwrap

    def para(s: str, indent: str = "  ") -> str:
        return "\n\n".join(
            textwrap.fill(p, width=78, initial_indent=indent, subsequent_indent=indent)
            for p in s.split("\n\n")
        )

    names = typology_names or {}
    L = ["=" * 78, c.name.upper(), f"{c.year}  ·  {c.jurisdiction}", "=" * 78, ""]
    L.append(para(c.headline))
    L.append("")
    L.append("BACKSTORY")
    L.append(para(c.backstory))
    L.append("")
    L.append("WHAT HAPPENED")
    L.append(para(c.what_happened))
    L.append("")
    L.append("IMPACT ON BANKS")
    L.append(para(c.bank_impact))
    L.append("")
    L.append("THE ANALYST LESSON")
    L.append(para(c.analyst_lesson))
    L.append("")
    L.append("TYPOLOGIES ILLUSTRATED")
    for tid in c.typology_ids:
        L.append(f"  · {names.get(tid, tid)}  (explain: python argus.py explain {tid})")
    L.append("")
    L.append("SOURCES")
    for s in c.sources:
        L.append(f"  - {s.get('title','')}")
        L.append(f"    {s.get('url','')}")
    L.append("")
    return "\n".join(L)
