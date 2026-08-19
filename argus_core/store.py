"""SQLite state. Stdlib sqlite3, single file at data/argus.db."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    name            TEXT PRIMARY KEY,
    url             TEXT NOT NULL,
    homepage        TEXT,
    type            TEXT,
    jurisdiction    TEXT,
    category        TEXT,
    tier            INTEGER,
    cadence         TEXT,
    etag            TEXT,
    last_modified   TEXT,
    last_fetch_at   TEXT,
    last_status     INTEGER,
    last_error      TEXT,
    consecutive_failures INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint     TEXT UNIQUE NOT NULL,
    source_name     TEXT NOT NULL,
    title           TEXT NOT NULL,
    url             TEXT NOT NULL,
    publisher       TEXT,
    published_at    TEXT,
    first_seen_at   TEXT NOT NULL,
    summary_raw     TEXT,
    relevant        INTEGER DEFAULT 0,
    score           INTEGER DEFAULT 0,
    jurisdiction    TEXT,
    category        TEXT,
    priority        TEXT,
    matched_terms   TEXT,
    typologies      TEXT,
    has_deadline    INTEGER DEFAULT 0,
    in_digest       INTEGER DEFAULT 0,
    link_status     INTEGER,
    link_checked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_items_seen     ON items(first_seen_at);
CREATE INDEX IF NOT EXISTS idx_items_relevant ON items(relevant, first_seen_at);
CREATE INDEX IF NOT EXISTS idx_items_digest   ON items(in_digest, relevant);
CREATE INDEX IF NOT EXISTS idx_items_source   ON items(source_name);

CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at   TEXT,
    finished_at  TEXT,
    sources_ok   INTEGER,
    sources_fail INTEGER,
    items_new    INTEGER,
    items_kept   INTEGER,
    mode         TEXT
);

CREATE TABLE IF NOT EXISTS digests (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    date     TEXT,
    kind     TEXT,
    path     TEXT,
    n_items  INTEGER,
    created_at TEXT
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fingerprint(source_name: str, external_id: str, url: str, title: str) -> str:
    """Stable identity for an item.

    Uses the feed's own id where present, else the URL, else the title. Titles
    alone are a poor key (they get edited), so they are the last resort.
    """
    basis = external_id.strip() or url.strip() or title.strip()
    return hashlib.sha256(f"{source_name}|{basis}".encode("utf-8")).hexdigest()[:32]


def dedupe_by_url(rows: list) -> list[dict]:
    """Collapse the same document arriving from more than one source.

    Several feeds legitimately carry the same item - an OFSI general licence
    appears under both the HM Treasury and the OFSI GOV.UK searches. Items are
    stored per-source so provenance is preserved, but a reader should see the
    document once, with the other sources noted.
    """
    out: dict[str, dict] = {}
    order: list[str] = []
    for r in rows:
        d = dict(r)
        key = (d.get("url") or "").rstrip("/").lower() or f"__id{d.get('id')}"
        prev = out.get(key)
        if prev is None:
            d.setdefault("also_from", [])
            out[key] = d
            order.append(key)
            continue
        keep, drop = (prev, d) if prev.get("score", 0) >= d.get("score", 0) else (d, prev)
        also = list(dict.fromkeys(
            list(prev.get("also_from", [])) + list(drop.get("also_from", []))
            + [drop.get("source_name", "")]
        ))
        keep["also_from"] = [s for s in also if s and s != keep.get("source_name")]
        out[key] = keep
    return [out[k] for k in order]


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.db.commit()

    # ---------------------------------------------------------- sources
    def upsert_source(self, s: dict) -> None:
        self.db.execute(
            """INSERT INTO sources (name,url,homepage,type,jurisdiction,category,tier,cadence)
               VALUES (:name,:url,:homepage,:type,:jurisdiction,:category,:tier,:cadence)
               ON CONFLICT(name) DO UPDATE SET
                 url=excluded.url, homepage=excluded.homepage, type=excluded.type,
                 jurisdiction=excluded.jurisdiction, category=excluded.category,
                 tier=excluded.tier, cadence=excluded.cadence""",
            {
                "name": s["name"], "url": s["url"], "homepage": s.get("homepage", ""),
                "type": s["type"], "jurisdiction": s["jurisdiction"],
                "category": s["category"], "tier": s["tier"],
                "cadence": s.get("cadence", "daily"),
            },
        )
        self.db.commit()

    def get_cache_headers(self, name: str) -> tuple[str | None, str | None]:
        row = self.db.execute(
            "SELECT etag, last_modified FROM sources WHERE name=?", (name,)
        ).fetchone()
        return (row["etag"], row["last_modified"]) if row else (None, None)

    def record_fetch(
        self, name: str, status: int, etag: str | None,
        last_modified: str | None, error: str | None,
    ) -> None:
        failures = 0 if status in (200, 304) else None
        if failures is None:
            row = self.db.execute(
                "SELECT consecutive_failures FROM sources WHERE name=?", (name,)
            ).fetchone()
            failures = (row["consecutive_failures"] or 0) + 1 if row else 1
        self.db.execute(
            """UPDATE sources SET last_fetch_at=?, last_status=?, last_error=?,
               etag=COALESCE(?,etag), last_modified=COALESCE(?,last_modified),
               consecutive_failures=? WHERE name=?""",
            (now_iso(), status, error, etag, last_modified, failures, name),
        )
        self.db.commit()

    def source_health(self) -> list[sqlite3.Row]:
        return self.db.execute(
            """SELECT name, tier, type, jurisdiction, last_status, last_fetch_at,
                      last_error, consecutive_failures,
                      (SELECT COUNT(*) FROM items i WHERE i.source_name=s.name) AS n_items
               FROM sources s ORDER BY consecutive_failures DESC, tier, name"""
        ).fetchall()

    # ---------------------------------------------------------- items
    def item_exists(self, fp: str) -> bool:
        return self.db.execute(
            "SELECT 1 FROM items WHERE fingerprint=?", (fp,)
        ).fetchone() is not None

    def insert_item(self, rec: dict) -> bool:
        """Returns True if the item was new."""
        try:
            self.db.execute(
                """INSERT INTO items
                   (fingerprint, source_name, title, url, publisher, published_at,
                    first_seen_at, summary_raw, relevant, score, jurisdiction,
                    category, priority, matched_terms, typologies, has_deadline)
                   VALUES (:fingerprint,:source_name,:title,:url,:publisher,:published_at,
                           :first_seen_at,:summary_raw,:relevant,:score,:jurisdiction,
                           :category,:priority,:matched_terms,:typologies,:has_deadline)""",
                rec,
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def commit(self) -> None:
        self.db.commit()

    def pending_digest_items(self, min_priority: str | None = None) -> list[sqlite3.Row]:
        q = """SELECT * FROM items
               WHERE relevant=1 AND in_digest=0
               ORDER BY CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                        score DESC, COALESCE(published_at, first_seen_at) DESC"""
        rows = self.db.execute(q).fetchall()
        if min_priority == "High":
            rows = [r for r in rows if r["priority"] == "High"]
        elif min_priority == "Medium":
            rows = [r for r in rows if r["priority"] in ("High", "Medium")]
        return rows

    def items_since(self, iso_ts: str) -> list[sqlite3.Row]:
        return self.db.execute(
            """SELECT * FROM items WHERE relevant=1
               AND COALESCE(published_at, first_seen_at) >= ?
               ORDER BY CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                        score DESC""",
            (iso_ts,),
        ).fetchall()

    def mark_digested(self, ids: list[int]) -> None:
        self.db.executemany(
            "UPDATE items SET in_digest=1 WHERE id=?", [(i,) for i in ids]
        )
        self.db.commit()

    def search(self, term: str, limit: int = 50) -> list[sqlite3.Row]:
        """Word-wise AND across title, summary and typology tags.

        Phrase matching alone is too brittle: "shell company" should find an
        item titled "shell companies used to..." and one tagged
        `shell-companies`, neither of which contains the literal phrase.
        """
        words = [w for w in term.lower().split() if w]
        if not words:
            return []
        clauses, params = [], []
        for w in words:
            like = f"%{w}%"
            clauses.append(
                "(LOWER(title) LIKE ? OR LOWER(summary_raw) LIKE ? "
                "OR LOWER(typologies) LIKE ? OR LOWER(source_name) LIKE ?)"
            )
            params.extend([like, like, like, like])
        params.append(limit)
        return self.db.execute(
            f"""SELECT * FROM items WHERE {' AND '.join(clauses)}
                ORDER BY relevant DESC,
                         CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                         COALESCE(published_at, first_seen_at) DESC LIMIT ?""",
            params,
        ).fetchall()

    def get_item(self, item_id: int) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()

    def record_link_check(self, item_id: int, status: int) -> None:
        self.db.execute(
            "UPDATE items SET link_status=?, link_checked_at=? WHERE id=?",
            (status, now_iso(), item_id),
        )

    # ---------------------------------------------------------- runs
    def start_run(self, mode: str) -> int:
        cur = self.db.execute(
            "INSERT INTO runs (started_at, mode) VALUES (?,?)", (now_iso(), mode)
        )
        self.db.commit()
        return int(cur.lastrowid or 0)

    def finish_run(self, run_id: int, ok: int, fail: int, new: int, kept: int) -> None:
        self.db.execute(
            """UPDATE runs SET finished_at=?, sources_ok=?, sources_fail=?,
               items_new=?, items_kept=? WHERE id=?""",
            (now_iso(), ok, fail, new, kept, run_id),
        )
        self.db.commit()

    def record_digest(self, date: str, kind: str, path: str, n: int) -> None:
        self.db.execute(
            "INSERT INTO digests (date,kind,path,n_items,created_at) VALUES (?,?,?,?,?)",
            (date, kind, path, n, now_iso()),
        )
        self.db.commit()

    def stats(self) -> dict:
        g = lambda q: self.db.execute(q).fetchone()[0]  # noqa: E731
        return {
            "items_total": g("SELECT COUNT(*) FROM items"),
            "items_relevant": g("SELECT COUNT(*) FROM items WHERE relevant=1"),
            "sources": g("SELECT COUNT(*) FROM sources"),
            "runs": g("SELECT COUNT(*) FROM runs"),
            "digests": g("SELECT COUNT(*) FROM digests"),
        }

    def close(self) -> None:
        self.db.close()
