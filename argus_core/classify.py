"""Deterministic relevance scoring and tagging.

No LLM is involved in the default pipeline. That is a deliberate choice:
  * it costs nothing to run, and
  * a rule engine cannot invent a fact that was not in the source text.

Everything here is transparent - `argus.py why <id>` prints the exact terms that
caused an item to score the way it did.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- vocabularies
# Weight reflects how strongly a term implies "a KYC analyst must see this".

CORE_TERMS: dict[str, int] = {
    # the subject itself
    "money laundering": 10, "anti-money laundering": 10, "aml/cft": 10,
    "counter-terrorist financing": 9, "terrorist financing": 9,
    "terrorism financing": 9, "proliferation financing": 9,
    "financial crime": 8, "economic crime": 8, "illicit finance": 8,
    "proceeds of crime": 8, "fincrime": 8,
    # the process
    "customer due diligence": 9, "enhanced due diligence": 9,
    "simplified due diligence": 8, "know your customer": 9,
    "beneficial owner": 8, "beneficial ownership": 8,
    "source of funds": 8, "source of wealth": 8,
    "suspicious activity report": 9, "suspicious transaction report": 9,
    "transaction monitoring": 8, "adverse media": 7, "onboarding": 4,
    "politically exposed person": 8, "risk assessment": 4,
    "defence against money laundering": 9, "tipping off": 8,
    "money laundering reporting officer": 8,
    # instruments and bodies
    "money laundering regulations": 10, "fatf": 8, "amla": 9,
    "amld": 8, "amlr": 8, "wolfsberg": 7, "egmont": 7,
    "travel rule": 8, "sixth money laundering directive": 9,
    "financial action task force": 9, "ukfiu": 8,
    "national crime agency": 6, "financial intelligence unit": 8,
    "joint money laundering steering group": 9,
    "economic crime and corporate transparency": 9,
    # sanctions
    "sanctions": 8, "sanctioned": 7, "designation": 5, "designated person": 8,
    "asset freeze": 8, "ofsi": 9, "ofac": 8, "sanctions evasion": 9,
    "consolidated list": 7, "general licence": 7, "specific licence": 6,
    "circumvention": 6, "export control": 5, "dual-use": 5,
    # typologies
    "typology": 9, "red flag": 8, "indicator": 3, "case study": 4,
    "trade-based money laundering": 10, "money mule": 9, "smurfing": 9,
    "structuring": 6, "layering": 6, "shell company": 9, "shelf company": 8,
    "hawala": 9, "underground banking": 9, "cuckoo smurfing": 10,
    "correspondent banking": 8, "nested account": 9, "de-risking": 7,
    "trust or company service provider": 9, "professional enabler": 9,
    "unexplained wealth order": 9, "account freezing order": 8,
    "confiscation": 6, "civil recovery": 7, "asset recovery": 7,
    "bust-out": 8, "invoice fraud": 8, "authorised push payment": 9,
    "app fraud": 8, "romance fraud": 8, "boiler room": 8,
    "free trade zone": 7, "bearer share": 8, "nominee director": 9,
    "shadow fleet": 8, "dark fleet": 8, "ship-to-ship": 6,
    # crypto
    "virtual asset service provider": 9, "cryptoasset": 7, "crypto-asset": 7,
    "mixer": 8, "tumbler": 8, "privacy coin": 8, "unhosted wallet": 8,
    "self-hosted wallet": 8, "stablecoin": 5, "darknet": 7,
    "ransomware": 6, "chain-hopping": 8, "mica": 6,
}

SUPPORTING_TERMS: dict[str, int] = {
    "fraud": 4, "bribery": 5, "corruption": 5, "tax evasion": 5,
    "embezzlement": 5, "kleptocracy": 6, "organised crime": 5,
    "human trafficking": 5, "modern slavery": 5, "drug trafficking": 4,
    "wildlife trafficking": 5, "arms trafficking": 5,
    "fine": 3, "fined": 5, "penalty": 3, "enforcement": 4,
    "final notice": 6, "censure": 4, "prosecution": 4, "convicted": 4,
    "compliance failure": 6, "systems and controls": 6, "whistleblower": 3,
    "due diligence": 5, "screening": 3, "kyc": 8, "cdd": 5, "edd": 5,
    "ubo": 6, "pep": 5, "sar": 5, "sars": 5, "mlro": 7, "mlr": 6,
    "poca": 7, "eccta": 8, "nra": 3, "vasp": 8, "tbml": 9, "ivts": 8,
}

# Terms that mark an item as off-topic for a KYC analyst. These subtract; they
# never hard-exclude, because "consumer credit firm fined for AML failings" is
# a real and relevant headline.
NOISE_TERMS: dict[str, int] = {
    "motor finance": 5, "mortgage rule": 4, "pension transfer": 4,
    "consumer duty": 3, "climate": 3, "net zero": 3, "greenwashing": 2,
    "diversity and inclusion": 4, "appointed representative": 2,
    "football": 3, "sport": 2, "vacancy": 6, "job opportunity": 6,
    "webinar registration": 3, "annual report and accounts": 3,
    "speech by": 1, "podcast": 2, "recruitment": 5, "procurement": 4,
    "call for applications": 5, "staff regulations": 5, "tender": 4,
    "webinars and events": 6, "frequently asked questions": 4,
    "privacy notice": 6, "cookie": 5, "accessibility statement": 6,
    "subscribe to": 4, "newsletter": 3,
}

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Sanctions", [
        "sanction", "asset freeze", "designat", "ofsi", "ofac", "consolidated list",
        "general licence", "restrictive measure", "embargo", "sdn list",
    ]),
    ("Enforcement", [
        "fined", "final notice", "penalty", "enforcement action", "censure",
        "prosecut", "convict", "sentenc", "charged with", "guilty",
        "monetary penalty", "settlement", "disgorge", "arrest",
    ]),
    ("Legislation", [
        "statutory instrument", "regulations 20", "act 20", "directive",
        "comes into force", "in force", "transpos", "bill", "amendment regulations",
        "delegated regulation", "implementing regulation", "commencement",
    ]),
    ("Consultation", [
        "consultation", "call for evidence", "call for input", "discussion paper",
        "have your say", "cp2", "dp2", "feedback statement", "public hearing",
    ]),
    ("Guidance", [
        "guidance", "guideline", "technical standard", "rts", "its", "q&a",
        "frequently asked", "dear ceo", "good practice", "policy statement",
        "opinion", "handbook", "supervisory expectation",
    ]),
    ("Typology", [
        "typology", "red flag", "threat assessment", "case study", "indicator",
        "laundered", "network dismantled", "operation ", "modus operandi",
        "how criminals", "trend report", "risk alert", "socta", "iocta",
    ]),
]

# Terms that mean "this has a deadline you can miss"
DEADLINE_HINTS = [
    "comes into force", "effective from", "applies from", "deadline",
    "closes on", "by 1 ", "must be implemented", "transitional period",
    "implementation date", "responses by",
]


@dataclass
class Verdict:
    relevant: bool
    score: int
    jurisdiction: str
    category: str
    priority: str                       # High | Medium | Low
    matched: list[str] = field(default_factory=list)
    typologies: list[str] = field(default_factory=list)
    has_deadline: bool = False


def _hits(text: str, vocab: dict[str, int]) -> tuple[int, list[str]]:
    total, found = 0, []
    for term, weight in vocab.items():
        # Word-boundary match so "sar" does not fire inside "Sarah"
        if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text):
            total += weight
            found.append(term)
    return total, found


def classify(
    title: str,
    summary: str,
    source_tier: int,
    source_jurisdiction: str,
    source_category: str,
    strict: bool = False,
    typology_index: dict[str, list[str]] | None = None,
) -> Verdict:
    """Score one item. `strict` is for firehose feeds (all new UK SIs)."""
    text = f"{title} {summary}".lower()

    core_score, core_hits = _hits(text, CORE_TERMS)
    sup_score, sup_hits = _hits(text, SUPPORTING_TERMS)
    noise_score, _ = _hits(text, NOISE_TERMS)

    # Keyword score is what the item's own text earned. Source bonuses are
    # added separately and deliberately kept out of the presumed-relevance
    # test - otherwise a category bonus alone would admit every item from a
    # feed, e.g. NCA drug-seizure stories with no financial-crime content.
    kw_score = core_score + sup_score - noise_score
    score = kw_score

    # Tier 1 regulators earn a small floor: a bare "Policy Statement PS26/4"
    # title may carry no keywords yet still matter.
    if source_tier == 1:
        score += 2
    if source_category in ("Sanctions", "Typology"):
        score += 3

    threshold = 12 if strict else 6
    # A source that exists only to publish AML material (e.g. OFSI, the
    # targeted news queries) does not need to clear the full bar - but it must
    # still show some financial-crime signal of its own.
    presumed = source_category in ("Sanctions", "Typology", "News") and source_tier >= 2
    relevant = score >= threshold or (presumed and kw_score >= 5)

    # -------- jurisdiction
    juris = source_jurisdiction
    if re.search(r"\b(uk|british|britain|england|wales|scotland|fca|hmrc|ofsi|nca|hm treasury|companies house)\b", text):
        juris = "UK" if source_jurisdiction in ("Global", "UK") else source_jurisdiction
    if re.search(r"\b(european union|eu-wide|amla|amld|eba|esma|european commission|brussels|eur-lex)\b", text):
        if source_jurisdiction == "Global":
            juris = "EU"

    # -------- category
    category = source_category
    for name, cues in CATEGORY_RULES:
        if any(c in text for c in cues):
            category = name
            break

    # -------- typology cross-reference
    typologies: list[str] = []
    if typology_index:
        for tid, kws in typology_index.items():
            if any(re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text) for k in kws):
                typologies.append(tid)

    has_deadline = any(h in text for h in DEADLINE_HINTS)

    # -------- priority
    if (source_tier == 1 and category in ("Legislation", "Enforcement", "Sanctions")) or score >= 30:
        priority = "High"
    elif source_tier <= 2 and score >= 14:
        priority = "High" if has_deadline else "Medium"
    elif score >= 10:
        priority = "Medium"
    else:
        priority = "Low"

    return Verdict(
        relevant=relevant,
        score=score,
        jurisdiction=juris,
        category=category,
        priority=priority,
        matched=sorted(set(core_hits + sup_hits))[:14],
        typologies=typologies,
        has_deadline=has_deadline,
    )
