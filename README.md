# FinCrime Radar

An AML/KYC regulatory and typology monitor for a working KYC analyst.

It polls UK, EU and global financial-crime sources every day, filters out the
noise, cross-references what it finds against a built-in typology reference,
and gives you a short Markdown digest plus a searchable offline dashboard.

**Cost: nothing.** No API keys, no subscriptions, no `pip install`. It uses only
the Python standard library and free public feeds.

---

## Quick start

```bash
cd C:\Users\salma\Projects\fincrime-radar
python radar.py run
```

That fetches, writes today's digest to `digests/`, builds `dashboard.html`, and
opens it. That single command is the whole daily routine.

Requires Python 3.11 or newer (you have 3.14). Nothing else.

---

## The daily loop

| When | Command | Takes |
|---|---|---|
| Every morning | `python radar.py run` | ~1 min to run, ~5 min to read |
| Friday | `python radar.py digest --weekly` | rolling 7-day rollup |
| When something looks unfamiliar | `python radar.py explain <typology>` | instant |
| Monthly | `python radar.py run --full` | includes weekly-cadence sources |
| Monthly | `python radar.py verify` | confirms citations are still live |

---

## Commands

```bash
python radar.py run                 # fetch + digest + dashboard (the daily one)
python radar.py fetch               # poll sources only
python radar.py fetch --daily-only  # skip weekly-cadence sources
python radar.py fetch --source FCA  # poll one source
python radar.py digest              # today's Markdown digest (top 45)
python radar.py digest --limit 0    # ...everything, no cap
python radar.py digest --weekly     # rolling 7-day rollup
python radar.py dashboard --days 30 # searchable offline HTML
python radar.py typology            # list the typology library
python radar.py typology --html     # render it as a browsable page
python radar.py explain tbml        # explain one typology
python radar.py explain "money mule"
python radar.py search "shell company"
python radar.py why 412             # why did item 412 score as it did?
python radar.py health              # per-source fetch health
python radar.py verify              # check cited links are live
python radar.py verify --links      # also check collected item links
python radar.py reclassify          # re-score after editing the rules
python radar.py brief               # paste-ready prompt for Claude
```

---

## Evidence policy

This is the part that matters most for your job, so it is worth being precise
about what the tool does and does not do.

**Nothing in this tool is AI-generated.** There is no LLM in the pipeline. The
classifier is a transparent keyword rule engine in `fcr/classify.py`. That is a
deliberate design choice, not a cost compromise: a rule engine cannot invent a
fact that was not in the source.

Concretely:

- **Every item links to its original source.** The link comes from the feed
  itself; it is never constructed.
- **Summaries are the publisher's own words**, taken verbatim from the feed and
  truncated. Where a source published no description, the digest says so
  explicitly rather than filling the gap.
- **Every scoring decision is inspectable.** `python radar.py why <id>` prints
  the exact terms that caused an item to be kept, categorised and prioritised.
- **Citations are machine-checkable.** `python radar.py verify` re-fetches every
  URL cited in the typology library and reports its HTTP status. As last run:
  22 checked, 0 broken.
- **The typology library is hand-written and sourced**, not generated. Each
  entry cites primary sources (legislation.gov.uk, NCA, FATF, OFSI, Europol,
  Wolfsberg). Treat it as an informed starting point that points you at the
  primary document — not as authority in itself.

If you want an interpretation layer, `python radar.py brief` writes a
paste-ready prompt containing the collected items and their links. You can feed
that to Claude yourself. The tool never calls a paid API on its own.

---

## Sources

26 active sources, every one HTTP-verified before it went into `feeds.toml`.
Tiers follow the standard practitioner hierarchy: tier 1 primary regulator,
tier 2 FIU/law-enforcement/typology, tier 3 commentary and press.

### UK
| Source | Type | What it gives you |
|---|---|---|
| FCA News | RSS | Enforcement, Dear CEO letters, Market Watch |
| FCA Publications | RSS | CPs, PSs, finalised guidance |
| OFSI blog | Atom | Sanctions list changes, licences, enforcement |
| legislation.gov.uk new SIs | Atom | Final text of MLR amendments (strict-filtered) |
| HM Treasury | GOV.UK API | SIs, sanctions policy, economic crime plan |
| OFSI publications | GOV.UK API | UK Sanctions List, general licences |
| HMRC AML supervision | GOV.UK API | Estate agents, ASPs, MSBs, high-value dealers |
| Home Office | GOV.UK API | ECCTA, failure to prevent fraud, NRA |
| Companies House | GOV.UK API | Identity verification rollout, PSC reform |
| NCA news | link scrape | SARs regime, DAML trends, red-flag alerts |

### EU
| Source | Type | What it gives you |
|---|---|---|
| EBA | RSS | AML/CFT guidelines, risk factor guidelines |
| ESMA | RSS | MiCA, market abuse, crypto supervision |
| AMLA | link scrape | The new single EU AML supervisor, Frankfurt |
| Europol newsroom | RSS | Operation write-ups — the best free "how the money moved" detail |

### Global
| Source | Type | What it gives you |
|---|---|---|
| FATF publications | link scrape | Standards, grey/black list, typology reports |
| OFAC recent actions | RSS | US designations (matters via correspondent banking) |
| OpenSanctions changelog | link scrape | Consolidated OFSI+OFAC+EU+UN sanctions data |
| ComplyAdvantage insights | RSS | Plain-English typology explainers |

### News (Google News RSS — free, no key, links resolve to original publishers)
Global financial crime · UK AML regulation · EU AML/AMLA · Enforcement and
fines · Crypto and sanctions evasion · FATF and standards · Fraud and mule
typologies.

### Deliberately disabled, and why

Three sources in `feeds.toml` are set `enabled = false`. This is honest
reporting, not an oversight — each was tested and found unusable from a script:

- **JMLSG** — returns HTTP 403 to any non-browser client (Akamai). Check
  <https://www.jmlsg.org.uk/latest-news/> manually; it publishes rarely.
- **Wolfsberg Group** — the site is a Nuxt single-page app, so the served HTML
  contains only JavaScript bundles and no content links. Check
  <https://wolfsberg-group.org/resources> quarterly.
- **Europol main reports** — client-side rendered, same problem. The Europol
  newsroom RSS announces each flagship report anyway, so this loses nothing.

**FATF is flaky by design.** It sits behind Cloudflare, which fingerprints the
TLS stack rather than the headers — so no header combination makes `urllib`
pass. The fetcher automatically retries through `curl`, which usually succeeds,
but expect this source to fail on some runs. That is not a bug. The "News —
FATF and standards" feed is the reliable complement and catches grey-list
changes via press coverage.

---

## The typology library

25 typologies covering placement, layering, integration, sanctions, fraud,
corporate structures, virtual assets and exploitation — plus a process
explainer on SARs, DAML and tipping off.

Each entry gives you: what it is, how it works step by step, the red flags, what
to do as the analyst, and primary sources.

```bash
python radar.py typology           # list them
python radar.py explain tbml       # trade-based money laundering
python radar.py explain "cuckoo"   # partial match works
python radar.py typology --html    # browsable, searchable page
```

The digest cross-links automatically: when a collected item matches a typology's
keywords, the digest tells you which one and how to explain it. That is the
bridge between "here's some news" and "here's what it means for my job".

To add your own, append a `[[typology]]` block to `typologies.toml` and run
`python radar.py reclassify`.

---

## Scheduling it

Run `setup-schedule.cmd` once (double-click it). It registers a Windows
Scheduled Task that runs `run-daily.cmd` every weekday at 08:00.

To check or remove it:

```bash
schtasks /query /tn FinCrimeRadar
```

```bash
schtasks /delete /tn FinCrimeRadar /f
```

Nothing breaks if you skip scheduling — the tool is stateful, so a manual run
after a week away still catches everything you missed.

---

## Tuning it

If the digest is too noisy or too quiet, edit `fcr/classify.py`:

- `CORE_TERMS` — strong AML/sanctions/typology signals, high weight
- `SUPPORTING_TERMS` — supporting signals, lower weight
- `NOISE_TERMS` — subtract from the score (never hard-exclude)
- `threshold` in `classify()` — the relevance bar

Then `python radar.py reclassify` re-scores everything already collected without
re-fetching. Use `python radar.py why <id>` on a specific item to see exactly
what fired.

To add a source, append a `[[source]]` block to `feeds.toml`. Verify it returns
200 first — that is the standing rule for this project.

---

## Layout

```
feeds.toml           source config (26 active, 3 disabled with reasons)
typologies.toml      the typology library — single source of truth
radar.py             CLI
fcr/fetch.py         HTTP: conditional GET, throttling, curl fallback
fcr/parse.py         RSS/Atom/JSON/HTML parsing
fcr/classify.py      the rule engine — edit this to tune
fcr/store.py         SQLite state and dedup
fcr/digest.py        Markdown digest + HTML dashboard
fcr/typology.py      typology loading, matching, rendering
data/radar.db        SQLite: items, sources, runs, digests
digests/             dated Markdown digests
dashboard.html       searchable offline dashboard
typologies.html      browsable typology reference
```

---

## Known limits

- Google News items link through Google's redirector rather than straight to the
  publisher. The current token format is opaque and cannot be decoded offline
  (verified — it carries no embedded URL), so the link resolves only when you
  click it. The parser does unwrap the older `?url=` form, and the **publisher
  name is always shown** in the digest and dashboard, so you can see the outlet
  before you click. Tier-1 and tier-2 sources all link directly.
- Link-scraped sources (FATF, NCA, AMLA, OpenSanctions) have no reliable
  publication date, so the digest shows "date not stated by source" rather than
  guessing one.
- The classifier reads titles and feed summaries, not full article text. A badly
  titled item with a thin summary can score low. That is why nothing is deleted
  — everything stays searchable via `radar.py search`.
- Relevance is a heuristic. It is tuned to over-include rather than miss things,
  which is the right direction for compliance work, but it is not a substitute
  for reading the primary source.
