# Argus

**Financial crime intelligence, always watching.**

An AML/KYC regulatory and typology monitor for a working KYC analyst. It polls
UK, EU and global financial-crime sources, filters the noise, cross-references
what it finds against a typology reference with real case studies, and serves
the lot as a searchable app with a live refresh button.

**Cost: nothing.** No API keys, no subscriptions, no paid data. The only
dependency is Streamlit for the app — the monitoring engine itself is pure
Python standard library.

---

## Quick start

```bash
pip install -r requirements.txt
```

```bash
python argus.py app
```

That opens the app in your browser. Hit **Refresh now** on the news feed and it
pulls the latest from every source — about a minute the first time.

Requires Python 3.11+ (you have 3.14).

---

## What's in it

### 1. News feed — live
Regulatory changes, enforcement actions, sanctions updates and financial crime
news from 25 sources, newest first, filtered to what actually matters to a KYC
analyst. Every item links straight to the original source.

- **Refresh now** re-polls every source on demand and streams progress per source.
- **Auto** re-checks every 15 minutes while the tab is open.
- **Include weekly sources** adds the low-frequency ones (FATF, AMLA,
  OpenSanctions) — slower, use it once a week.
- Filter by jurisdiction, category and priority; search across headlines,
  summaries and typologies.

### 2. Typologies — 25 of them
Every method in the library gets:

| Section | What it gives you |
|---|---|
| **What it is** | The mechanism in plain English |
| **How it works** | Step by step |
| **Impact on banks** | Why it costs money and attracts regulators |
| **Red flags** | What you'd observe |
| **How to spot it** | Concrete detection — what to query, aggregate and alert on |
| **What to do** | The analyst's next move |
| **The real case** | A documented case with its backstory |
| **Sources** | Primary documents |

Typologies also show **how many recent news items matched them**, so the
reference links back to what's happening now.

### 3. Case library — 15 documented cases
Real matters with the story behind them: NatWest/Fowler Oldfield, Danske Bank
Estonia, Bitfinex, BNP Paribas, Deutsche Bank mirror trading, 1MDB, Operation
Fort, Wachovia, the Panama and Pandora Papers, Tornado Cash, and more. Each
gives you backstory, what happened, impact on banks, the analyst lesson, and
primary sources.

### 4. New & emerging — with quote-anchored drafting
Items that describe a *method* — a typology, modus operandi, red flag or
emerging trend — but match nothing in the library.

Press **Draft from source** on any of them (or `python argus.py draft <id>`) and
Argus fetches the full article and extracts the sentences describing a
mechanism, a red flag or an outcome — **verbatim, each tagged with its source
URL** — into `drafts/<slug>.toml`.

**It quotes; it does not paraphrase.** That distinction is the whole safety
argument. A model writing *"criminals typically structure below £10,000"* from
memory can be wrong about the threshold, the jurisdiction or the year. A
sentence quoted out of an FCA notice cannot be wrong about what the FCA said —
at worst it's quoted out of context, and the context is retrievable because the
URL travels with the quote.

The analysis fields — what it is, impact on banks, how to spot it, keywords —
are left **empty for you**. Those are judgement, not extraction, and the tool
will not fake them. `promote` refuses a draft until they're filled:

```bash
python argus.py draft 412
```

```bash
python argus.py promote sanctions-enforcement-action
```

`promote` appends the finished entry to `typologies.toml`, validates that the
file still parses, and tells you to run `reclassify` so past items get tagged
against the new typology.

### 5. Sources
Which sources are responding, which are failing, and why.

---

## Evidence policy

This matters most for your job, so it's worth being precise.

**There is no LLM anywhere in this pipeline.** Classification is a transparent
keyword rule engine in `argus_core/classify.py`. That's a deliberate design
choice, not a cost compromise: a rule engine cannot invent a fact that wasn't in
the source.

- **Every item links to its original source.** The link comes from the feed
  itself; it is never constructed.
- **Summaries are the publisher's own words**, verbatim and truncated. Where a
  source published no description, it says so rather than filling the gap.
- **Every scoring decision is inspectable** — `python argus.py why <id>` prints
  the exact terms that caused an item to be kept, categorised and prioritised.
- **Citations are machine-checkable** — `python argus.py verify` re-fetches
  every URL cited in the typology and case libraries and reports its status.
- **Case studies are compiled from public reporting**, with headline facts
  checked against primary sources when written. The linked source is the
  authority — read it before relying on any detail.
- **Where a citation could not be verified, it says so.** The AUSTRAC link on
  the Crown/Star case is flagged in the app because that host was unreachable
  from the build network. Nothing is quietly presented as verified when it isn't.

If you want an interpretation layer, `python argus.py brief` writes a
paste-ready prompt with the collected items and links, for you to hand to Claude
yourself. The tool never calls a paid API on its own.

---

## Commands

```bash
python argus.py app                 # launch the Streamlit app
python argus.py run                 # fetch + digest + dashboard (headless daily)
python argus.py fetch               # poll sources only
python argus.py fetch --source FCA  # poll one source
python argus.py digest              # today's Markdown digest (top 45)
python argus.py digest --weekly     # rolling 7-day rollup
python argus.py dashboard --days 30 # offline HTML dashboard
python argus.py typology            # list typologies
python argus.py explain tbml        # explain one, with red flags and detection
python argus.py cases               # list documented cases
python argus.py cases danske-estonia
python argus.py candidates          # possible new typologies to review
python argus.py draft 412           # quote-anchored draft from item 412
python argus.py promote <slug>      # append a finished draft to the library
python argus.py search "shell company"
python argus.py why 412             # why did item 412 score that way?
python argus.py health              # per-source fetch health
python argus.py verify              # check typology citations are live
python argus.py verify --cases      # check case citations
python argus.py reclassify          # re-score after editing the rules
python argus.py brief               # paste-ready prompt for Claude
```

---

## Sources

25 active sources, every one HTTP-verified before it went into `feeds.toml`.
Tiers follow the practitioner hierarchy: tier 1 primary regulator, tier 2
FIU/law enforcement, tier 3 commentary and press.

**UK** — FCA news, FCA publications, OFSI blog, legislation.gov.uk new SIs,
HM Treasury, OFSI publications, HMRC AML supervision, Home Office, Companies
House, NCA news.

**EU** — EBA, ESMA, AMLA, Europol newsroom.

**Global** — FATF publications, OFAC recent actions, OpenSanctions changelog,
ComplyAdvantage insights.

**News** (Google News RSS — free, no key, links resolve to original publishers)
— global financial crime, UK AML regulation, EU AML/AMLA, enforcement and
fines, crypto and sanctions evasion, FATF and standards, fraud and mule
typologies.

### Deliberately disabled, and why

Three sources are `enabled = false` in `feeds.toml`. Each was tested and found
unusable from a script — recorded rather than silently ignored:

- **JMLSG** — HTTP 403 to any non-browser client (Akamai). Check
  <https://www.jmlsg.org.uk/latest-news/> manually; it publishes rarely.
- **Wolfsberg Group** — a single-page app, so the served HTML has only
  JavaScript bundles and no content links. Check
  <https://wolfsberg-group.org/resources> quarterly.
- **Europol main reports** — client-side rendered, same problem. The Europol
  newsroom RSS announces each flagship report anyway.

**FATF is flaky by design.** It sits behind Cloudflare, which fingerprints the
TLS stack rather than the headers — so no header combination gets `urllib`
through. The fetcher retries via `curl`, which usually succeeds, but expect it
to fail on some runs. That is not a bug.

---

## Adding to the library

**A new typology** — append a `[[typology]]` block to `typologies.toml` with
`id`, `name`, `aka`, `family`, `summary`, `mechanics`, `bank_impact`,
`red_flags`, `how_to_spot`, `analyst_actions`, `keywords`, and
`[[typology.sources]]`. Then:

```bash
python argus.py reclassify
```

The `keywords` list is what links live news to the typology, so make it
specific — generic words produce false matches.

**A new case** — append a `[[case]]` block to `cases.toml` with
`typology_ids = ["..."]` linking it to the typologies it illustrates. One case
can illustrate several.

---

## Scheduling

Run `setup-schedule.cmd` once to register a Windows Scheduled Task that runs the
headless daily fetch every weekday at 08:00.

```bash
schtasks /query /tn Argus
```

```bash
schtasks /delete /tn Argus /f
```

Nothing breaks if you skip it — the tool is stateful, so a manual run after a
week away still catches everything.

---

## Deploying it online (optional, free)

Streamlit Community Cloud hosts this for free from the GitHub repo:

1. Go to <https://share.streamlit.io> and sign in with GitHub.
2. Point it at `salmanjey-hash/argus`, main branch, `streamlit_app.py`.
3. Deploy.

One caveat: the cloud filesystem is ephemeral, so the SQLite database resets
when the app restarts. Press **Refresh now** and it repopulates in about a
minute. For a personal monitoring tool that's fine; if you want persistent
history online, point `DB` at a hosted database instead.

---

## Layout

```
argus.py              CLI
streamlit_app.py      app entry point and navigation
app_shared.py         cached data access for the app
app_pages/            feed, typologies, cases, emerging, sources
argus_core/
  fetch.py            HTTP: conditional GET, throttling, curl fallback
  parse.py            RSS/Atom/JSON/HTML parsing
  classify.py         the rule engine - edit this to tune
  store.py            SQLite state, dedup
  pipeline.py         shared fetch used by both CLI and app
  digest.py           Markdown digest + HTML dashboard
  typology.py         typology loading and rendering
  cases.py            case library
  drafter.py          quote-anchored draft extraction
feeds.toml            25 active sources, 3 disabled with reasons
typologies.toml       25 typologies
cases.toml            15 documented cases
drafts/               work-in-progress typology drafts (gitignored)
data/argus.db         SQLite (gitignored)
digests/              dated Markdown digests (gitignored)
```

---

## Known limits

- Google News items link through Google's redirector. The current token format
  is opaque and cannot be decoded offline (verified — it carries no embedded
  URL), so it resolves only on click. The **publisher name is always shown** so
  you know the outlet first. All tier-1 and tier-2 sources link directly.
- Link-scraped sources (FATF, NCA, AMLA, OpenSanctions) often have no reliable
  publication date, so the app shows "date not stated" rather than guessing.
- The classifier reads titles and feed summaries, not full article text. A badly
  titled item with a thin summary can score low — which is why nothing is
  deleted and everything stays searchable.
- Relevance is a heuristic tuned to over-include rather than miss things. That's
  the right direction for compliance work, but it is not a substitute for
  reading the primary source.
- 20 of the 25 typologies have a documented case attached. The other five say so
  plainly rather than inventing one.
