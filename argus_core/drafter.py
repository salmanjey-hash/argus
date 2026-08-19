"""Quote-anchored typology drafting.

The point of this module: build a draft typology entry automatically WITHOUT
inventing anything. Every line it produces is a verbatim sentence lifted from a
named source document, stored alongside the URL it came from.

That is the distinction that matters. A model writing "criminals typically
structure deposits below GBP 10,000" from memory can be wrong about the
threshold, the jurisdiction, or the year. A sentence quoted out of an FCA notice
cannot be wrong about what the FCA said - at worst it is quoted out of context,
and the surrounding context is stored too so that is checkable.

So drafts are extraction, not generation. The analyst turns quotes into prose;
the tool never puts words in a regulator's mouth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser

from . import fetch as F

# ---------------------------------------------------------------- extraction

_DROP_TAGS = {
    "script", "style", "noscript", "nav", "header", "footer", "aside",
    "form", "button", "svg", "iframe", "select", "template",
}


class _TextExtractor(HTMLParser):
    """Pull readable body text, skipping chrome. Stdlib only."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _DROP_TAGS:
            self._skip += 1
        elif tag in ("p", "li", "div", "br", "h1", "h2", "h3", "h4", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _DROP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag in ("p", "li", "h1", "h2", "h3", "h4", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self._skip == 0:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    p = _TextExtractor()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001 - malformed markup must not crash a draft
        pass
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(“\"'])")


def sentences(text: str) -> list[str]:
    out: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 40:
            continue
        for s in _SENT_SPLIT.split(line):
            s = s.strip()
            # Filter obvious boilerplate and navigation crumbs
            if not (40 <= len(s) <= 420):
                continue
            if s.count("|") > 2 or s.count("·") > 2:
                continue
            if re.match(r"(?i)^(cookie|accept|subscribe|sign up|share this|read more|skip to)", s):
                continue
            # Require terminal punctuation. Link lists and nav labels ("OFSI
            # enforcement actions: decisions and monetary penalties") match the
            # cue patterns but are not statements, and quoting them as evidence
            # would be padding. Precision matters more than recall here.
            if s[-1] not in '.!?"”':
                continue
            words = s.split()
            if len(words) < 7:
                continue
            # Skip ALL-CAPS nav text
            caps = sum(1 for w in words if w.isupper() and len(w) > 2)
            if caps > len(words) * 0.5:
                continue
            out.append(" ".join(words))
    # de-duplicate, keep order
    return list(dict.fromkeys(out))


# ------------------------------------------------------------------ patterns

# Sentences that describe how a scheme operated
MECHANIC_CUES = re.compile(
    r"(?i)\b("
    r"used to (?:move|transfer|launder|conceal|disguise|hide)|laundered (?:through|via|by)|"
    r"funds were (?:moved|transferred|routed|sent|converted|withdrawn)|"
    r"transferred (?:to|through|via)|routed (?:through|via)|"
    r"the scheme (?:involved|worked|operated)|operated by|carried out by|"
    r"in order to (?:conceal|disguise|avoid|evade)|"
    r"set up (?:a|an|companies|accounts)|opened (?:accounts|bank accounts)|"
    r"posing as|purporting to be|falsely (?:claimed|represented|stated)|"
    r"invoices? (?:were|was)|shell compan|front compan|"
    r"converted (?:into|to) (?:cash|crypto|cryptocurrency)|"
    r"deposited|withdrew|cash was|proceeds were"
    r")\b"
)

# Sentences that read as an indicator or warning
FLAG_CUES = re.compile(
    r"(?i)\b("
    r"red flags?|warning signs?|indicators?|should be alert|be alert to|"
    r"firms should|banks should|institutions should|look out for|watch for|"
    r"may indicate|can indicate|is indicative of|suggests? that|"
    r"suspicious|unusual|inconsistent with|out of (?:line|character) with|"
    r"failed to|did not (?:identify|question|escalate|monitor)|"
    r"without (?:adequate|sufficient|proper)|no (?:apparent|clear|obvious) "
    r"(?:economic|commercial|business) (?:purpose|rationale)"
    r")\b"
)

# Sentences carrying an outcome / penalty, useful for the case record
OUTCOME_CUES = re.compile(
    r"(?i)\b("
    r"fined|penalty|penalties|sentenced|jailed|convicted|pleaded guilty|"
    r"forfeit|confiscat|ordered to pay|settlement|agreed to pay|"
    r"prohibited|censure|prosecut"
    r")\b"
)


@dataclass
class Evidence:
    quote: str
    url: str
    kind: str  # mechanic | red_flag | outcome


@dataclass
class Draft:
    slug: str
    title: str
    url: str
    source_name: str
    published: str | None
    fetched_at: str
    mechanics: list[Evidence] = field(default_factory=list)
    red_flags: list[Evidence] = field(default_factory=list)
    outcomes: list[Evidence] = field(default_factory=list)
    fetch_error: str | None = None

    @property
    def total(self) -> int:
        return len(self.mechanics) + len(self.red_flags) + len(self.outcomes)


def slugify(s: str, maxlen: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:maxlen].rstrip("-") or "draft"


def build_draft(
    title: str,
    url: str,
    source_name: str,
    published: str | None = None,
    max_per_kind: int = 10,
) -> Draft:
    """Fetch the source and pull quote-anchored candidate material from it."""
    d = Draft(
        slug=slugify(title),
        title=title,
        url=url,
        source_name=source_name,
        published=published,
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )

    r = F.get(url)
    if not r.ok:
        d.fetch_error = r.error or f"HTTP {r.status}"
        return d

    # The <title> tag usually reappears in the body as an <h1>, and it matches
    # the outcome cues, so it would otherwise be quoted back as "evidence".
    title_key = re.sub(r"[^a-z0-9]+", "", title.lower())[:40]

    for s in sentences(html_to_text(r.body)):
        if title_key and re.sub(r"[^a-z0-9]+", "", s.lower()).startswith(title_key):
            continue
        if FLAG_CUES.search(s) and len(d.red_flags) < max_per_kind:
            d.red_flags.append(Evidence(s, url, "red_flag"))
        elif MECHANIC_CUES.search(s) and len(d.mechanics) < max_per_kind:
            d.mechanics.append(Evidence(s, url, "mechanic"))
        elif OUTCOME_CUES.search(s) and len(d.outcomes) < max_per_kind:
            d.outcomes.append(Evidence(s, url, "outcome"))
    return d


# --------------------------------------------------------------- TOML output

def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_toml(d: Draft) -> str:
    """Emit a draft typology block.

    Deliberately NOT valid for typologies.toml as-is: `summary`, `bank_impact`
    and `how_to_spot` are left empty for the analyst to write. Everything the
    tool filled in is a quote, and every quote carries its source URL.
    """
    L = [
        "# DRAFT - not part of the live library until you complete and promote it.",
        "#",
        "# Every line under [[draft.evidence]] is a VERBATIM sentence from the source",
        f"# below, fetched {d.fetched_at}. Nothing here was written by a model.",
        "#",
        "# Your job: turn these quotes into the library's own prose, fill in the",
        "# empty fields, then run:  python argus.py promote " + d.slug,
        "",
        "[draft]",
        f"slug = {_q(d.slug)}",
        f"title = {_q(d.title)}",
        f"source_name = {_q(d.source_name)}",
        f"url = {_q(d.url)}",
        f"published = {_q(d.published or '')}",
        f"fetched_at = {_q(d.fetched_at)}",
        "",
        "# ---- fields YOU write (the tool will not invent these) ----",
        "[draft.entry]",
        'id = ""              # kebab-case, e.g. "invoice-mirroring"',
        'name = ""            # e.g. "Invoice mirroring"',
        "aka = []",
        'family = ""          # e.g. "Trade & commerce"',
        'summary = """"""     # what it is, in your words',
        'bank_impact = """"""  # why it costs banks money / attracts regulators',
        "how_to_spot = []     # concrete detection steps for your own data",
        "analyst_actions = []",
        "keywords = []        # be specific - this is what links live news to it",
        "",
        "# ---- quoted evidence (verbatim, with source) ----",
    ]

    for kind, items in (
        ("mechanic", d.mechanics),
        ("red_flag", d.red_flags),
        ("outcome", d.outcomes),
    ):
        for e in items:
            L.append("[[draft.evidence]]")
            L.append(f"kind = {_q(kind)}")
            L.append(f"quote = {_q(e.quote)}")
            L.append(f"url = {_q(e.url)}")
            L.append("")

    if d.fetch_error:
        L.append(f"# FETCH FAILED: {d.fetch_error}")
        L.append("# The source could not be retrieved, so there is no evidence to")
        L.append("# quote. Open the URL manually.")
        L.append("")

    return "\n".join(L)


def to_text(d: Draft) -> str:
    """Terminal preview."""
    L = ["=" * 78, f"DRAFT: {d.title[:70]}", "=" * 78, ""]
    L.append(f"source   {d.source_name}")
    L.append(f"url      {d.url}")
    L.append(f"fetched  {d.fetched_at}")
    L.append("")
    if d.fetch_error:
        L.append(f"FETCH FAILED: {d.fetch_error}")
        L.append("Nothing could be quoted. Open the URL manually.")
        return "\n".join(L)
    if not d.total:
        L.append("The page was fetched but no sentence matched a mechanic,")
        L.append("red-flag or outcome pattern. That usually means it is a landing")
        L.append("page rather than an article. Open the URL and check.")
        return "\n".join(L)

    for label, items in (
        ("HOW IT WORKED (quoted)", d.mechanics),
        ("RED FLAGS / FAILINGS (quoted)", d.red_flags),
        ("OUTCOME (quoted)", d.outcomes),
    ):
        if not items:
            continue
        L.append(label)
        for e in items:
            L.append(f'  "{e.quote}"')
            L.append("")
    L.append("Every line above is verbatim from the source. Nothing was generated.")
    return "\n".join(L)
