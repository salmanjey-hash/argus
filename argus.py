#!/usr/bin/env python3
"""Argus - AML/KYC regulatory and typology monitor.

Zero dependencies (Python 3.11+ stdlib only). Zero API keys. Zero cost.

    python argus.py fetch          poll sources, classify, store
    python argus.py digest         write today's Markdown digest
    python argus.py dashboard      write a searchable offline HTML dashboard
    python argus.py run            fetch + digest + dashboard  (the daily command)
    python argus.py explain <x>    explain a typology
    python argus.py typology       list / render the typology library
    python argus.py search <term>  search everything collected so far
    python argus.py why <id>       show why an item scored the way it did
    python argus.py verify         check that cited links are still live
    python argus.py health         per-source fetch health
    python argus.py brief          write a paste-ready prompt for Claude Code
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Windows consoles default to cp1252 and choke on the box-drawing and tick
# glyphs used below. Force UTF-8 on the streams before anything prints.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

from argus_core import classify as C          # noqa: E402
from argus_core import digest as D            # noqa: E402
from argus_core import fetch as F             # noqa: E402
from argus_core import parse as P             # noqa: E402
from argus_core import typology as T          # noqa: E402
from argus_core import cases as CS            # noqa: E402
from argus_core.store import Store, dedupe_by_url, fingerprint, now_iso  # noqa: E402

FEEDS = ROOT / "feeds.toml"
TYPOLOGIES = ROOT / "typologies.toml"
CASES = ROOT / "cases.toml"
DB = ROOT / "data" / "argus.db"
DIGEST_DIR = ROOT / "digests"


# --------------------------------------------------------------------- utils

def load_sources(only_daily: bool = False, only: str | None = None) -> list[dict]:
    cfg = tomllib.load(open(FEEDS, "rb"))
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


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _c(text: str, code: str) -> str:
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


# --------------------------------------------------------------------- fetch

def cmd_fetch(args) -> int:
    from argus_core import pipeline as PL

    sources = PL.load_sources(FEEDS, only_daily=args.daily_only, only=args.source)
    if not sources:
        print("No sources matched.")
        return 1

    print(f"Argus - polling {len(sources)} source(s) - {stamp()}\n")

    def report(r) -> None:
        if r.unchanged:
            print(f"  {_c('. unchanged', '90')}  {r.name}")
        elif not r.ok:
            print(f"  {_c('x FAILED  ', '31')}  {r.name}  {_c(r.error or '', '31')}")
        else:
            mark = _c("+", "32;1" if r.new else "32")
            kept = _c(f"{r.kept:3d} relevant", "36") if r.kept else "  0 relevant"
            print(f"  {mark} {r.seen:3d} seen  {r.new:3d} new  {kept}   {r.name}")

    out = PL.run_fetch(
        FEEDS, TYPOLOGIES, DB,
        daily_only=args.daily_only, only=args.source, force=args.force,
        on_source=report,
    )

    print(f"\n{out.ok_count} ok - {out.fail_count} failed - {out.new_total} new items - "
          f"{_c(f'{out.kept_total} relevant', '36;1')}")
    if out.fail_count:
        print(f"{_c('Some sources failed.', '33')} Run `python argus.py health` for detail.")
    return 0


def cmd_reclassify(args) -> int:
    """Re-score everything already stored, without re-fetching.

    Use after editing classify.py or typologies.toml - tuning the rules should
    never mean hammering the regulators again.
    """
    lib = T.load(TYPOLOGIES)
    tindex = T.keyword_index(lib)
    src_cfg = {s["name"]: s for s in load_sources()}
    store = Store(DB)

    rows = store.db.execute(
        "SELECT id, source_name, title, summary_raw, relevant FROM items"
    ).fetchall()
    changed = gained = lost = 0

    for r in rows:
        s = src_cfg.get(r["source_name"])
        if not s:
            continue  # source removed or disabled since collection
        v = C.classify(
            r["title"], r["summary_raw"] or "", s["tier"], s["jurisdiction"],
            s["category"], strict=s.get("strict_filter", False),
            typology_index=tindex,
        )
        was = bool(r["relevant"])
        if was != v.relevant:
            changed += 1
            gained += int(v.relevant and not was)
            lost += int(was and not v.relevant)
        store.db.execute(
            """UPDATE items SET relevant=?, score=?, jurisdiction=?, category=?,
               priority=?, matched_terms=?, typologies=?, has_deadline=? WHERE id=?""",
            (int(v.relevant), v.score, v.jurisdiction, v.category, v.priority,
             json.dumps(v.matched), json.dumps(v.typologies), int(v.has_deadline),
             r["id"]),
        )
    store.commit()
    s = store.stats()
    print(f"Re-scored {len(rows)} item(s): {changed} changed "
          f"({gained} newly relevant, {lost} dropped).")
    print(f"Now {s['items_relevant']} relevant of {s['items_total']}.")
    store.close()
    return 0


# -------------------------------------------------------------------- digest

def cmd_digest(args) -> int:
    lib = T.load(TYPOLOGIES)
    tnames = T.names(lib)
    store = Store(DB)

    if args.weekly:
        since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")
        rows = dedupe_by_url(store.items_since(since))
        kind, note = "Weekly", "rolling 7-day window"
    else:
        rows = dedupe_by_url(store.pending_digest_items(min_priority=args.min_priority))
        kind, note = "Daily", "new since last digest"

    # Rows arrive priority-sorted, so a cap keeps the most important items and
    # drops the tail. `--limit 0` means "everything".
    all_rows = rows
    limit = args.limit if args.limit is not None else 45
    held_back = 0
    if limit and len(rows) > limit:
        held_back = len(rows) - limit
        rows = rows[:limit]

    DIGEST_DIR.mkdir(exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    suffix = "weekly" if args.weekly else "daily"
    path = DIGEST_DIR / f"{date}-{suffix}.md"

    md = D.render_markdown(rows, kind, stamp(), tnames, note, held_back=held_back)
    path.write_text(md, encoding="utf-8")

    # Mark everything reviewed, including held-back items - they remain in the
    # dashboard and the database, and we do not want them re-queued tomorrow.
    if not args.weekly and all_rows:
        store.mark_digested([r["id"] for r in all_rows])
    store.record_digest(date, suffix, str(path), len(rows))

    print(f"{kind} digest · {len(rows)} item(s) → {path}")
    if args.open:
        webbrowser.open(path.resolve().as_uri())
    store.close()
    return 0


def cmd_dashboard(args) -> int:
    lib = T.load(TYPOLOGIES)
    store = Store(DB)
    days = args.days
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    rows = store.items_since(since)

    out = ROOT / "dashboard.html"
    out.write_text(
        D.render_dashboard(rows, stamp(), T.names(lib),
                           title=f"Argus · last {days} days"),
        encoding="utf-8",
    )
    print(f"Dashboard · {len(rows)} item(s) → {out}")
    if not args.no_open:
        webbrowser.open(out.resolve().as_uri())
    store.close()
    return 0


def cmd_run(args) -> int:
    rc = cmd_fetch(argparse.Namespace(daily_only=not args.full, source=None, force=False))
    if rc:
        return rc
    print()
    cmd_digest(argparse.Namespace(weekly=False, limit=None, open=False, min_priority=None))
    cmd_dashboard(argparse.Namespace(days=args.days, no_open=args.no_open))
    return 0


# ----------------------------------------------------------------- typology

def cmd_explain(args) -> int:
    lib = T.load(TYPOLOGIES)
    hits = T.find(lib, args.term)
    if not hits:
        print(f"No typology matches '{args.term}'.\n")
        print("Available:")
        for t in sorted(lib.values(), key=lambda x: x.name):
            print(f"  {t.id:22s} {t.name}")
        return 1
    if len(hits) > 1 and args.term.lower() not in lib:
        print(f"{len(hits)} matches for '{args.term}':\n")
        for t in hits:
            print(f"  {t.id:22s} {t.name}")
        print("\nRun `python argus.py explain <id>` for the full entry.")
        return 0
    for t in hits:
        print(T.to_text(t))
    return 0


def cmd_typology(args) -> int:
    lib = T.load(TYPOLOGIES)
    if args.html:
        out = ROOT / "typologies.html"
        out.write_text(T.to_html(lib, stamp()), encoding="utf-8")
        print(f"{len(lib)} typologies → {out}")
        if not args.no_open:
            webbrowser.open(out.resolve().as_uri())
        return 0
    if args.markdown:
        out = ROOT / "TYPOLOGIES.md"
        out.write_text(T.to_markdown(lib), encoding="utf-8")
        print(f"{len(lib)} typologies → {out}")
        return 0
    fams: dict[str, list] = {}
    for t in lib.values():
        fams.setdefault(t.family, []).append(t)
    print(f"\n{len(lib)} typologies in the library:\n")
    for fam in sorted(fams):
        print(_c(fam, "1"))
        for t in sorted(fams[fam], key=lambda x: x.name):
            print(f"  {t.id:22s} {t.name}")
        print()
    print("Explain one:  python argus.py explain <id>")
    return 0


# ------------------------------------------------------------------- lookup

def cmd_search(args) -> int:
    store = Store(DB)
    rows = store.search(args.term, limit=args.limit)
    if not rows:
        print(f"Nothing collected yet matching '{args.term}'.")
        return 1
    print(f"\n{len(rows)} match(es) for '{args.term}':\n")
    for r in rows:
        pr = {"High": "31;1", "Medium": "33", "Low": "90"}.get(r["priority"], "0")
        print(f"  [{r['id']}] {_c(r['priority'][:4].ljust(4), pr)} "
              f"{(r['published_at'] or r['first_seen_at'])[:10]}  {r['title'][:78]}")
        print(f"        {_c(r['url'], '4;36')}")
        print(f"        {r['source_name']}")
        print()
    store.close()
    return 0


def cmd_why(args) -> int:
    store = Store(DB)
    r = store.get_item(args.id)
    if not r:
        print(f"No item with id {args.id}.")
        return 1
    lib = T.load(TYPOLOGIES)
    print(f"\n{r['title']}\n{r['url']}\n")
    print(f"  source        {r['source_name']}")
    print(f"  published     {r['published_at'] or '(not stated by source)'}")
    print(f"  first seen    {r['first_seen_at']}")
    print(f"  relevant      {bool(r['relevant'])}   score {r['score']}")
    print(f"  jurisdiction  {r['jurisdiction']}")
    print(f"  category      {r['category']}")
    print(f"  priority      {r['priority']}")
    print(f"  deadline cue  {bool(r['has_deadline'])}")
    terms = json.loads(r["matched_terms"] or "[]")
    print(f"\n  matched terms ({len(terms)}):")
    for t in terms:
        print(f"    · {t}")
    tids = json.loads(r["typologies"] or "[]")
    if tids:
        print("\n  related typologies:")
        for t in tids:
            print(f"    · {t}  —  {lib[t].name if t in lib else t}")
            print(f"      explain: python argus.py explain {t}")
    print()
    store.close()
    return 0


# -------------------------------------------------------------------- cases

def cmd_cases(args) -> int:
    lib = CS.load(CASES)
    tnames = T.names(T.load(TYPOLOGIES))

    if not args.term:
        by_t = CS.by_typology(lib)
        print(f"\n{len(lib)} documented cases in the library:\n")
        for c in sorted(lib.values(), key=lambda x: x.year):
            print(f"  {_c(c.id.ljust(26), '1')} {c.year:<22} {c.name}")
            print(f"  {'':26} {_c(c.headline[:74], '90')}")
        print(f"\nCovering {len(by_t)} of {len(tnames)} typologies.")
        print("Read one:  python argus.py cases <id>")
        return 0

    hits = CS.find(lib, args.term)
    if not hits:
        print(f"No case matches '{args.term}'. Run `python argus.py cases` to list them.")
        return 1
    if len(hits) > 1 and args.term.lower() not in lib:
        print(f"\n{len(hits)} matches for '{args.term}':\n")
        for c in hits:
            print(f"  {c.id:26} {c.name}")
        print("\nRead one:  python argus.py cases <id>")
        return 0
    for c in hits:
        print(CS.to_text(c, tnames))
    return 0


def cmd_candidates(args) -> int:
    """Items that describe a *method* but match no typology we hold."""
    from argus_core import pipeline as PL

    rows = PL.find_candidates(DB, days=args.days, limit=args.limit)
    if not rows:
        print(f"No new-typology candidates in the last {args.days} days.")
        return 0

    print(f"\n{len(rows)} possible new/undocumented typolog(ies) in the last "
          f"{args.days} days.\nThese are relevant items describing a technique that "
          f"matches nothing in typologies.toml:\n")
    for r in rows:
        print(f"  [{r['id']}] {_c(r['title'][:74], '1')}")
        print(f"        {_c(r['url'], '4;36')}")
        print(f"        {r['source_name']} - signals: {', '.join(r['signals'][:4])}")
        if r["summary_raw"]:
            print(f"        {r['summary_raw'][:150]}")
        print()
    print(_c("These are a review queue, not auto-added.", "33"))
    print("If one is a genuine new typology, add a [[typology]] block to "
          "typologies.toml,\nthen run `python argus.py reclassify`.")
    return 0


def cmd_app(args) -> int:
    """Launch the Streamlit app."""
    import shutil
    import subprocess

    app = ROOT / "streamlit_app.py"
    if not app.exists():
        print(f"Missing {app}")
        return 1
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("Streamlit is not installed. Install it with:\n\n"
              "    pip install streamlit\n")
        return 1
    exe = shutil.which("streamlit")
    cmd = ([exe] if exe else [sys.executable, "-m", "streamlit"]) + ["run", str(app)]
    print("Starting Argus... (Ctrl+C to stop)\n")
    return subprocess.call(cmd)


# ------------------------------------------------------------------- verify

def _verdict(code: int) -> tuple[str, str, bool]:
    """Map an HTTP code to (label, colour, is_real_problem).

    403/429 means the host blocks scripted clients - the page is still there
    and opens fine in a browser. Only 404/410/connection failures mean a
    citation is actually broken, so only those are counted as problems.
    """
    if code == 200:
        return "200", "32", False
    if code in (401, 403, 429):
        return f"{code}*", "33", False
    if code in (404, 410):
        return str(code), "31", True
    if code == 0:
        return "ERR", "31", True
    return str(code), "33", False


def cmd_verify(args) -> int:
    """Confirm cited links are live. This is the anti-fabrication check."""
    bad = 0
    checked = 0
    blocked = 0

    if args.cases or not (args.links or args.typologies):
        clib = CS.load(CASES)
        seen_c: set[str] = set()
        print("\nVerifying case library citations...\n")
        for c in sorted(clib.values(), key=lambda x: x.name):
            for s in c.sources:
                url = s.get("url", "")
                if not url or url in seen_c:
                    continue
                seen_c.add(url)
                code, err = F.head_ok(url)
                checked += 1
                label, col, problem = _verdict(code)
                bad += int(problem)
                blocked += int(not problem and code != 200)
                suffix = f"  {_c(err[:50], col)}  ({c.id})" if code != 200 else ""
                print(f"  {_c(label.rjust(4), col)}  {url}{suffix}")

    if args.typologies or not (args.links or args.cases):
        lib = T.load(TYPOLOGIES)
        seen: set[str] = set()
        print("\nVerifying typology library citations…\n")
        for t in sorted(lib.values(), key=lambda x: x.name):
            for s in t.sources:
                url = s.get("url", "")
                if not url or url in seen:
                    continue
                seen.add(url)
                code, err = F.head_ok(url)
                checked += 1
                label, col, problem = _verdict(code)
                bad += int(problem)
                blocked += int(not problem and code != 200)
                suffix = f"  {_c(err[:50], col)}  ({t.id})" if code != 200 else ""
                print(f"  {_c(label.rjust(4), col)}  {url}{suffix}")

    if args.links:
        store = Store(DB)
        rows = store.items_since(
            (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat(timespec="seconds")
        )[: args.limit]
        print(f"\nVerifying {len(rows)} collected item link(s)…\n")
        for r in rows:
            code, err = F.head_ok(r["url"])
            checked += 1
            store.record_link_check(r["id"], code)
            label, col, problem = _verdict(code)
            bad += int(problem)
            blocked += int(not problem and code != 200)
            print(f"  {_c(label.rjust(4), col)}  {r['title'][:62]}")
            if code != 200:
                print(f"        {r['url']}")
        store.commit()
        store.close()

    print()
    summary = f"{checked} checked · "
    summary += _c(f"{bad} broken", "31;1") if bad else _c("0 broken", "32;1")
    if blocked:
        summary += f" · {_c(f'{blocked} bot-blocked', '33')}"
    print(summary)
    if blocked:
        print(_c("  * = host refuses scripted clients (403/429). The page is still "
                 "there;\n    open it in a browser to confirm. Not a broken citation.",
                 "90"))
    return 1 if bad else 0


def cmd_health(args) -> int:
    store = Store(DB)
    rows = store.source_health()
    if not rows:
        print("No sources polled yet. Run `python argus.py fetch` first.")
        return 1
    print(f"\n{'STATUS':>6}  {'FAILS':>5}  {'ITEMS':>5}  {'LAST FETCH':<17} SOURCE")
    print("-" * 88)
    for r in rows:
        st = r["last_status"]
        col = "32" if st in (200, 304) else "31"
        last = (r["last_fetch_at"] or "")[:16].replace("T", " ")
        print(f"{_c(str(st or '-').rjust(6), col)}  "
              f"{str(r['consecutive_failures'] or 0).rjust(5)}  "
              f"{str(r['n_items']).rjust(5)}  {last:<17} {r['name']}")
        if r["last_error"] and (r["consecutive_failures"] or 0) > 0:
            print(f"{'':>6}  {_c(r['last_error'][:70], '31')}")
    s = store.stats()
    print(f"\n{s['items_total']} items collected · {s['items_relevant']} relevant · "
          f"{s['runs']} runs · {s['digests']} digests")
    store.close()
    return 0


# -------------------------------------------------------------------- brief

BRIEF_HEADER = """\
You are helping a KYC/financial-crime analyst understand this week's
developments. Below are items collected automatically from primary regulator
and law-enforcement feeds. Each has a working source link.

Please:
1. Group them by what actually matters to a KYC analyst's day job.
2. For anything with a deadline or an in-force date, state the date plainly.
3. Where an item reflects a typology, explain the mechanism in two or three
   sentences and give the red flags an analyst would look for.
4. Flag anything where the headline alone is misleading and the source should
   be read in full.
5. Do not add facts that are not in these items. If something needs checking,
   say so and point at the link.

ITEMS
-----
"""


def cmd_brief(args) -> int:
    """Write a paste-ready prompt so Claude Code can add the interpretation
    layer, without this tool ever calling a paid API itself."""
    store = Store(DB)
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat(timespec="seconds")
    rows = store.items_since(since)
    if args.min_priority == "High":
        rows = [r for r in rows if r["priority"] == "High"]
    elif args.min_priority == "Medium":
        rows = [r for r in rows if r["priority"] in ("High", "Medium")]
    rows = rows[: args.limit]

    lib = T.load(TYPOLOGIES)
    L = [BRIEF_HEADER]
    for r in rows:
        L.append(f"### {r['title']}")
        L.append(f"- link: {r['url']}")
        L.append(f"- source: {r['source_name']} ({r['jurisdiction']}, {r['category']}, "
                 f"priority {r['priority']})")
        L.append(f"- published: {r['published_at'] or 'not stated'}")
        if r["summary_raw"]:
            L.append(f"- publisher's own summary: {r['summary_raw']}")
        tids = json.loads(r["typologies"] or "[]")
        if tids:
            L.append("- matched typologies: "
                     + ", ".join(lib[t].name if t in lib else t for t in tids))
        L.append("")

    out = ROOT / "brief-prompt.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"{len(rows)} item(s) → {out}")
    print("\nNow run, in this folder:")
    print("  claude \"read brief-prompt.md and write me the weekly briefing\"")
    print("…or just open the file and paste it into any Claude session.")
    store.close()
    return 0


# ---------------------------------------------------------------------- main

def main() -> int:
    p = argparse.ArgumentParser(
        prog="argus.py",
        description="Argus - AML/KYC regulatory & typology monitor.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="poll sources, classify, store")
    f.add_argument("--daily-only", action="store_true",
                   help="skip sources marked cadence=weekly")
    f.add_argument("--source", help="only poll sources whose name contains this")
    f.add_argument("--force", action="store_true",
                   help="ignore ETag/Last-Modified caching")
    f.set_defaults(func=cmd_fetch)

    rc = sub.add_parser("reclassify",
                        help="re-score stored items after editing the rules")
    rc.set_defaults(func=cmd_reclassify)

    d = sub.add_parser("digest", help="write a Markdown digest")
    d.add_argument("--weekly", action="store_true", help="rolling 7-day rollup")
    d.add_argument("--limit", type=int)
    d.add_argument("--min-priority", choices=["High", "Medium"])
    d.add_argument("--open", action="store_true")
    d.set_defaults(func=cmd_digest)

    b = sub.add_parser("dashboard", help="write searchable offline HTML dashboard")
    b.add_argument("--days", type=int, default=14)
    b.add_argument("--no-open", action="store_true")
    b.set_defaults(func=cmd_dashboard)

    r = sub.add_parser("run", help="fetch + digest + dashboard (the daily command)")
    r.add_argument("--full", action="store_true", help="include weekly-cadence sources")
    r.add_argument("--days", type=int, default=14)
    r.add_argument("--no-open", action="store_true")
    r.set_defaults(func=cmd_run)

    e = sub.add_parser("explain", help="explain a typology")
    e.add_argument("term")
    e.set_defaults(func=cmd_explain)

    t = sub.add_parser("typology", help="list or render the typology library")
    t.add_argument("--html", action="store_true")
    t.add_argument("--markdown", action="store_true")
    t.add_argument("--no-open", action="store_true")
    t.set_defaults(func=cmd_typology)

    cs = sub.add_parser("cases", help="real case library (story, impact, lessons)")
    cs.add_argument("term", nargs="?", help="case id or search term")
    cs.set_defaults(func=cmd_cases)

    cd = sub.add_parser("candidates",
                        help="possible new typologies not yet in the library")
    cd.add_argument("--days", type=int, default=60)
    cd.add_argument("--limit", type=int, default=40)
    cd.set_defaults(func=cmd_candidates)

    ap = sub.add_parser("app", help="launch the Streamlit app")
    ap.set_defaults(func=cmd_app)

    s = sub.add_parser("search", help="search collected items")
    s.add_argument("term")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_search)

    w = sub.add_parser("why", help="show why an item scored the way it did")
    w.add_argument("id", type=int)
    w.set_defaults(func=cmd_why)

    v = sub.add_parser("verify", help="check cited links are still live")
    v.add_argument("--typologies", action="store_true",
                   help="check typology library citations (default)")
    v.add_argument("--cases", action="store_true",
                   help="check case library citations")
    v.add_argument("--links", action="store_true",
                   help="also check collected item links")
    v.add_argument("--days", type=int, default=7)
    v.add_argument("--limit", type=int, default=40)
    v.set_defaults(func=cmd_verify)

    h = sub.add_parser("health", help="per-source fetch health")
    h.set_defaults(func=cmd_health)

    br = sub.add_parser("brief", help="write a paste-ready prompt for Claude")
    br.add_argument("--days", type=int, default=7)
    br.add_argument("--limit", type=int, default=60)
    br.add_argument("--min-priority", choices=["High", "Medium"])
    br.set_defaults(func=cmd_brief)

    args = p.parse_args()
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
