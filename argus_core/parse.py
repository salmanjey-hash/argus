"""Feed and page parsing. Stdlib only.

Every Item keeps the publisher's own words verbatim in `summary_raw`. Nothing in
this pipeline paraphrases or invents text - see README "Evidence policy".
"""

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs, unquote


@dataclass
class Item:
    source_name: str
    title: str
    url: str
    external_id: str
    published: str | None = None      # ISO-8601 UTC
    summary_raw: str = ""             # publisher's own words, verbatim
    publisher: str = ""               # for aggregators, the original outlet
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------- helpers

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(s: str, limit: int = 600) -> str:
    if not s:
        return ""
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = _TAG_RE.sub(" ", s)
    s = html.unescape(s)
    s = _WS_RE.sub(" ", s).strip()
    if len(s) > limit:
        cut = s[:limit].rsplit(" ", 1)[0]
        s = cut + "…"
    return s


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    try:
        return _iso(parsedate_to_datetime(raw))
    except (TypeError, ValueError, IndexError):
        pass
    cleaned = raw.replace("Z", "+00:00")
    for candidate in (cleaned, cleaned[:19], cleaned[:10]):
        try:
            return _iso(datetime.fromisoformat(candidate))
        except ValueError:
            continue
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        try:
            return _iso(datetime(int(m[1]), int(m[2]), int(m[3])))
        except ValueError:
            return None
    return None


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _find(el: ET.Element, *names: str) -> ET.Element | None:
    wanted = {n.lower() for n in names}
    for child in el:
        if _localname(child.tag) in wanted:
            return child
    return None


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def unwrap_google_news(url: str) -> str:
    """Google News RSS wraps the publisher URL. Recover it where possible."""
    if "news.google.com" not in url:
        return url
    qs = parse_qs(urlparse(url).query)
    for key in ("url", "u"):
        if key in qs and qs[key]:
            return unquote(qs[key][0])
    return url  # newer opaque /articles/CBM... form; resolves on click


# --------------------------------------------------------------- RSS / Atom

def parse_feed(xml_text: str, source_name: str) -> list[Item]:
    """Parse RSS 2.0 or Atom. Namespace-agnostic."""
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError:
        # Some feeds ship a stray BOM or leading whitespace/doctype
        cleaned = xml_text.strip().lstrip("﻿")
        cleaned = re.sub(r"^<\?xml[^>]*\?>", "", cleaned).strip()
        cleaned = re.sub(r"^<!DOCTYPE[^>]*>", "", cleaned).strip()
        try:
            root = ET.fromstring(cleaned)
        except ET.ParseError:
            return []

    entries: list[ET.Element] = []
    for el in root.iter():
        if _localname(el.tag) in ("item", "entry"):
            entries.append(el)

    items: list[Item] = []
    for e in entries:
        title = strip_html(_text(_find(e, "title")), 300)
        if not title:
            continue

        # --- link
        link = ""
        link_el = _find(e, "link")
        if link_el is not None:
            link = (link_el.get("href") or _text(link_el) or "").strip()
        if not link:
            for child in e:
                if _localname(child.tag) == "link" and child.get("href"):
                    link = child.get("href", "").strip()
                    break
        if not link:
            link = _text(_find(e, "guid")).strip()
        if not link.startswith("http"):
            continue
        link = unwrap_google_news(link)

        # --- date
        published = None
        for key in ("pubdate", "published", "updated", "date", "modified"):
            node = _find(e, key)
            if node is not None:
                published = parse_date(_text(node))
                if published:
                    break

        # --- summary
        summary = ""
        for key in ("description", "summary", "content", "encoded", "subtitle"):
            node = _find(e, key)
            if node is not None:
                summary = strip_html(_text(node))
                if summary:
                    break

        # --- publisher (Google News <source>, Dublin Core creator)
        publisher = ""
        src = _find(e, "source")
        if src is not None:
            publisher = strip_html(_text(src), 80)
        if not publisher:
            creator = _find(e, "creator")
            if creator is not None:
                publisher = strip_html(_text(creator), 80)

        # Google News titles are "Headline - Publisher". Drop the suffix when
        # we already know the publisher from <source>, so it is not shown twice.
        if " - " in title:
            head, _, tail = title.rpartition(" - ")
            if publisher and tail.strip().lower() == publisher.strip().lower():
                title = head
            elif not publisher and "news.google" in link:
                title, publisher = head, tail

        guid = _text(_find(e, "guid")) or _text(_find(e, "id")) or link

        items.append(
            Item(
                source_name=source_name,
                title=title.strip(),
                url=link,
                external_id=guid.strip(),
                published=published,
                summary_raw=summary,
                publisher=publisher.strip(),
            )
        )
    return items


# --------------------------------------------------------------- GOV.UK API

def parse_govuk(payload: dict, source_name: str) -> list[Item]:
    items: list[Item] = []
    for r in payload.get("results", []):
        title = strip_html(r.get("title", ""), 300)
        link = r.get("link", "")
        if not title or not link:
            continue
        if link.startswith("/"):
            link = "https://www.gov.uk" + link
        items.append(
            Item(
                source_name=source_name,
                title=title,
                url=link,
                external_id=link,
                published=parse_date(r.get("public_timestamp")),
                summary_raw=strip_html(r.get("description", "")),
                publisher="GOV.UK",
                extra={"doc_type": r.get("content_store_document_type", "")},
            )
        )
    return items


# --------------------------------------------------------------- HTML links

class _LinkHarvester(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._buf: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip_depth += 1
            return
        if tag == "a":
            d = dict(attrs)
            self._href = d.get("href")
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "a" and self._href:
            text = _WS_RE.sub(" ", "".join(self._buf)).strip()
            self.links.append((self._href, text))
            self._href = None
            self._buf = []

    def handle_data(self, data):
        if self._skip_depth == 0 and self._href is not None:
            self._buf.append(data)


# Nav/boilerplate anchor text we never want as an "item"
_NOISE = {
    "read more", "more", "next", "previous", "home", "back", "skip to main content",
    "cookies", "accessibility", "privacy", "sitemap", "contact", "search", "menu",
    "share", "print", "subscribe", "newsletter", "login", "sign in", "all news",
    "view all", "see all", "load more", "english", "français",
}


def parse_links(
    html_text: str,
    source_name: str,
    base_url: str,
    link_pattern: str | None = None,
    min_text: int = 25,
) -> list[Item]:
    """Turn a feedless index page into items, one per plausible content link.

    Preferred over whole-page hash diffing: raw HTML hashes churn on every
    nav/cookie-banner tweak, whereas a new anchor genuinely means new content.
    """
    p = _LinkHarvester()
    try:
        p.feed(html_text)
    except Exception:  # noqa: BLE001 - malformed markup must not kill the run
        pass

    pat = re.compile(link_pattern, re.I) if link_pattern else None
    seen: set[str] = set()
    items: list[Item] = []

    for href, text in p.links:
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        url = urljoin(base_url, href).split("#")[0].rstrip("/")
        if url in seen:
            continue
        if pat and not pat.search(url):
            continue
        text = text.strip()
        if len(text) < min_text or text.lower() in _NOISE:
            continue
        seen.add(url)
        title, summary, published = _split_card_text(text)
        items.append(
            Item(
                source_name=source_name,
                title=strip_html(title, 200),
                url=url,
                external_id=url,
                published=published,
                summary_raw=strip_html(summary) if summary else "",
                publisher=urlparse(url).netloc,
            )
        )
    return items


# Listing pages often wrap a whole card in one <a>: "Title 10 May 2024 Body…".
# Splitting on the embedded date recovers a real title, a real summary and a
# real date instead of one 400-character pseudo-title.
_CARD_DATE = re.compile(
    r"\s(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\s",
    re.I,
)


def _split_card_text(text: str) -> tuple[str, str, str | None]:
    text = _WS_RE.sub(" ", text).strip()
    m = _CARD_DATE.search(text)
    if m:
        head = text[: m.start()].strip(" -–—·|")
        tail = text[m.end():].strip()
        if len(head) >= 3:
            return head, tail, parse_date(m.group(1))
    if len(text) > 160:
        # No date to split on: keep a readable title, park the rest as summary.
        cut = text[:160].rsplit(" ", 1)[0]
        return cut, text[len(cut):].strip(), None
    return text, "", None
