"""The fetch pipeline, callable from both the CLI and the Streamlit app.

Kept free of printing so the Streamlit refresh button and `argus.py fetch` run
exactly the same code path - one place for the logic, two front ends.
"""

import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import classify as C
from . import fetch as F
from . import parse as P
from . import typology as T
from .store import Store, fingerprint, now_iso


@dataclass
class SourceResult:
    name: str
    status: int
    seen: int = 0
    new: int = 0
    kept: int = 0
    error: str | None = None
    unchanged: bool = False

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class RunResult:
    results: list[SourceResult] = field(default_factory=list)
    new_total: int = 0
    kept_total: int = 0

    @property
    def ok_count(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.ok)

    @property
    def failures(self) -> list[SourceResult]:
        return [r for r in self.results if not r.ok]


def load_sources(
    feeds_path: str | Path,
    only_daily: bool = False,
    only: str | None = None,
) -> list[dict]:
    cfg = tomllib.load(open(feeds_path, "rb"))
    out = []
    for s in cfg.get("source", []):
        if not s.get("enabled", True):
            continue
        if only and only.lower() not in s["name"].lower():
            continue
        if only_daily and s.get("cadence", "daily") != "daily":
            continue
        out.append(s)
    return out


def run_fetch(
    feeds_path: str | Path,
    typologies_path: str | Path,
    db_path: str | Path,
    daily_only: bool = False,
    only: str | None = None,
    force: bool = False,
    on_source: Callable[[SourceResult], None] | None = None,
    on_start: Callable[[str, int, int], None] | None = None,
) -> RunResult:
    """Poll sources, classify, store. Returns a RunResult; never prints."""
    lib = T.load(typologies_path)
    tindex = T.keyword_index(lib)
    store = Store(db_path)

    sources = load_sources(feeds_path, only_daily=daily_only, only=only)
    mode = "daily" if daily_only else "full"
    run_id = store.start_run(mode)
    out = RunResult()

    for i, s in enumerate(sources):
        name = s["name"]
        if on_start:
            on_start(name, i, len(sources))
        store.upsert_source(s)
        etag, lastmod = store.get_cache_headers(name)
        if force:
            etag = lastmod = None

        r = F.get(s["url"], etag=etag, last_modified=lastmod)
        store.record_fetch(name, r.status, r.etag, r.last_modified, r.error)

        if r.not_modified:
            res = SourceResult(name, r.status, unchanged=True)
            out.results.append(res)
            if on_source:
                on_source(res)
            continue
        if not r.ok:
            res = SourceResult(name, r.status, error=r.error or f"HTTP {r.status}")
            out.results.append(res)
            if on_source:
                on_source(res)
            continue

        try:
            stype = s["type"]
            if stype in ("rss", "atom"):
                items = P.parse_feed(r.body, name)
            elif stype == "api_govuk":
                items = P.parse_govuk(json.loads(r.body), name)
            elif stype == "links":
                items = P.parse_links(r.body, name, s["url"], s.get("link_pattern"))
            else:
                raise ValueError(f"unknown feed type: {stype}")
        except Exception as e:  # noqa: BLE001 - one bad feed must not kill the run
            res = SourceResult(name, r.status, error=f"{type(e).__name__}: {e}")
            out.results.append(res)
            if on_source:
                on_source(res)
            continue

        res = SourceResult(name, r.status, seen=len(items))
        for it in items:
            fp = fingerprint(name, it.external_id, it.url, it.title)
            if store.item_exists(fp):
                continue
            res.new += 1
            v = C.classify(
                it.title, it.summary_raw, s["tier"], s["jurisdiction"],
                s["category"], strict=s.get("strict_filter", False),
                typology_index=tindex,
            )
            if v.relevant:
                res.kept += 1
            store.insert_item({
                "fingerprint": fp, "source_name": name, "title": it.title,
                "url": it.url, "publisher": it.publisher, "published_at": it.published,
                "first_seen_at": now_iso(), "summary_raw": it.summary_raw,
                "relevant": int(v.relevant), "score": v.score,
                "jurisdiction": v.jurisdiction, "category": v.category,
                "priority": v.priority, "matched_terms": json.dumps(v.matched),
                "typologies": json.dumps(v.typologies),
                "has_deadline": int(v.has_deadline),
            })
        store.commit()
        out.new_total += res.new
        out.kept_total += res.kept
        out.results.append(res)
        if on_source:
            on_source(res)

    store.finish_run(run_id, out.ok_count, out.fail_count, out.new_total, out.kept_total)
    store.close()
    return out


# --------------------------------------------------------------- candidates

# Language that suggests an item is describing a *method* rather than an event.
# Used to surface possible new typologies the library does not cover yet.
_SIGNAL = re.compile(
    r"(?<![a-z])("
    r"typolog\w*|modus operandi|new (?:scheme|method|tactic|technique)s?|"
    r"novel (?:scheme|method|approach)|emerging (?:threat|risk|trend|typolog\w*)|"
    r"red flags?|warning signs?|indicators? of|how (?:criminals|fraudsters|launderers)|"
    r"new(?:ly)? (?:identified|observed|detected) (?:trend|pattern|method)|"
    r"increasingly (?:using|exploiting|abusing)|shift(?:ing|ed)? to|"
    r"threat assessment|trend report|case stud(?:y|ies)"
    r")(?![a-z])",
    re.I,
)


def find_candidates(db_path: str | Path, days: int = 60, limit: int = 40) -> list[dict]:
    """Relevant items that describe a method but match no known typology.

    This is deliberately a *review queue*, not an auto-updater. The tool cannot
    responsibly invent a typology entry on its own - but it can reliably tell
    you "this looks like it's describing a technique we have nothing on yet".
    """
    from datetime import datetime, timedelta, timezone

    store = Store(db_path)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    rows = store.db.execute(
        """SELECT id, title, url, summary_raw, source_name, publisher,
                  published_at, first_seen_at, category, jurisdiction, score
           FROM items
           WHERE relevant=1 AND (typologies='[]' OR typologies IS NULL)
             AND COALESCE(published_at, first_seen_at) >= ?
           ORDER BY score DESC""",
        (since,),
    ).fetchall()

    out = []
    for r in rows:
        text = f"{r['title']} {r['summary_raw'] or ''}"
        hits = sorted({m.group(0).lower() for m in _SIGNAL.finditer(text)})
        if not hits:
            continue
        d = dict(r)
        d["signals"] = hits
        out.append(d)
        if len(out) >= limit:
            break
    store.close()
    return out
