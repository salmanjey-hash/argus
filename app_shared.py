"""Shared data access for the Argus Streamlit app.

Pages stay thin; everything that touches disk or the network lives here so it
can be cached in one place. The fetch itself goes through argus_core.pipeline,
the exact same code path as `python argus.py fetch`.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

from argus_core import cases as CS
from argus_core import pipeline as PL
from argus_core import typology as T
from argus_core.store import dedupe_by_url as Store_dedupe

ROOT = Path(__file__).resolve().parent
FEEDS = ROOT / "feeds.toml"
TYPOLOGIES = ROOT / "typologies.toml"
CASES = ROOT / "cases.toml"
DB = ROOT / "data" / "argus.db"

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_ICON = {
    "High": ":material/priority_high:",
    "Medium": ":material/remove:",
    "Low": ":material/low_priority:",
}


# --------------------------------------------------------------- reference data

@st.cache_data(show_spinner=False)
def load_typologies() -> dict:
    lib = T.load(TYPOLOGIES)
    return {
        tid: {
            "id": t.id, "name": t.name, "aka": t.aka, "family": t.family,
            "summary": t.summary, "mechanics": t.mechanics,
            "bank_impact": " ".join(t.bank_impact.split()) if t.bank_impact else "",
            "red_flags": t.red_flags, "how_to_spot": t.how_to_spot,
            "analyst_actions": t.analyst_actions, "keywords": t.keywords,
            "sources": t.sources,
        }
        for tid, t in lib.items()
    }


@st.cache_data(show_spinner=False)
def load_cases() -> dict:
    lib = CS.load(CASES)
    return {
        cid: {
            "id": c.id, "name": c.name, "year": c.year,
            "jurisdiction": c.jurisdiction, "headline": c.headline,
            "typology_ids": c.typology_ids, "backstory": c.backstory,
            "what_happened": c.what_happened, "bank_impact": c.bank_impact,
            "analyst_lesson": c.analyst_lesson, "verify_note": c.verify_note,
            "sources": c.sources,
        }
        for cid, c in lib.items()
    }


def typology_names() -> dict[str, str]:
    return {tid: t["name"] for tid, t in load_typologies().items()}


def cases_for_typology(tid: str) -> list[dict]:
    return [c for c in load_cases().values() if tid in c["typology_ids"]]


# ------------------------------------------------------------------- database

def _connect() -> sqlite3.Connection | None:
    if not DB.exists():
        return None
    db = sqlite3.connect(DB, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


@st.cache_data(ttl=30, show_spinner=False)
def load_items(days: int = 30, relevant_only: bool = True) -> list[dict]:
    db = _connect()
    if db is None:
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    where = "COALESCE(published_at, first_seen_at) >= ?"
    if relevant_only:
        where += " AND relevant=1"
    rows = db.execute(
        f"SELECT * FROM items WHERE {where} ORDER BY "
        "COALESCE(published_at, first_seen_at) DESC",
        (since,),
    ).fetchall()
    db.close()

    out = []
    for r in Store_dedupe(rows):
        d = dict(r)
        d["typologies"] = json.loads(d.get("typologies") or "[]")
        d["matched_terms"] = json.loads(d.get("matched_terms") or "[]")
        d["when"] = d.get("published_at") or d.get("first_seen_at")
        out.append(d)
    return out


@st.cache_data(ttl=30, show_spinner=False)
def source_health() -> list[dict]:
    db = _connect()
    if db is None:
        return []
    rows = db.execute(
        """SELECT name, tier, type, jurisdiction, category, last_status,
                  last_fetch_at, last_error, consecutive_failures,
                  (SELECT COUNT(*) FROM items i WHERE i.source_name=s.name) AS n_items
           FROM sources s ORDER BY tier, name"""
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


@st.cache_data(ttl=30, show_spinner=False)
def stats() -> dict:
    db = _connect()
    if db is None:
        return {}
    g = lambda q: db.execute(q).fetchone()[0]  # noqa: E731
    out = {
        "items_total": g("SELECT COUNT(*) FROM items"),
        "items_relevant": g("SELECT COUNT(*) FROM items WHERE relevant=1"),
        "sources": g("SELECT COUNT(*) FROM sources"),
        "last_fetch": g("SELECT MAX(last_fetch_at) FROM sources") or "",
    }
    db.close()
    return out


@st.cache_data(ttl=30, show_spinner=False)
def candidates(days: int = 60, limit: int = 40) -> list[dict]:
    if not DB.exists():
        return []
    return PL.find_candidates(DB, days=days, limit=limit)


# --------------------------------------------------------------------- fetch

def refresh(daily_only: bool = True, progress=None) -> PL.RunResult:
    """Run the real pipeline, then drop caches so the UI shows new data."""
    out = PL.run_fetch(
        FEEDS, TYPOLOGIES, DB, daily_only=daily_only, on_source=progress
    )
    st.cache_data.clear()
    st.session_state["last_refresh"] = datetime.now(timezone.utc)
    return out


# --------------------------------------------------------------------- format

def ago(iso: str | None) -> str:
    """Human 'x ago' for an ISO timestamp."""
    if not iso:
        return "never"
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return iso[:16]
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    secs = (datetime.now(timezone.utc) - dt).total_seconds()
    if secs < 0:
        return "just now"
    if secs < 90:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)} min ago"
    if secs < 86400:
        return f"{int(secs // 3600)} hr ago"
    days = int(secs // 86400)
    return "yesterday" if days == 1 else f"{days} days ago"


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "date not stated"
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except ValueError:
        return iso[:10]


EVIDENCE_NOTE = (
    "Every item links to its original source. Summary text is quoted verbatim "
    "from the publisher's own feed — nothing here is AI-generated or paraphrased."
)
