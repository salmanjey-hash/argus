"""HTTP layer. Stdlib only - no requests, no pip install.

Design notes:
  * Browser-like headers. Several regulator sites (FATF via Cloudflare, EBA)
    return 403 to a bare urllib User-Agent but 200 to a normal browser header
    set. This was verified empirically, not assumed.
  * Conditional GET via ETag / Last-Modified. Being polite costs nothing and
    means a daily run mostly transfers 304s.
  * Per-host rate limiting so we never hammer a regulator.
"""

from __future__ import annotations

import gzip
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from dataclasses import dataclass

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

BASE_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
}

_MIN_HOST_INTERVAL = 1.5  # seconds between hits on the same host
_last_hit: dict[str, float] = {}


@dataclass
class Response:
    url: str
    status: int
    body: str
    etag: str | None = None
    last_modified: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.body)

    @property
    def not_modified(self) -> bool:
        return self.status == 304


def _throttle(url: str) -> None:
    host = urllib.parse.urlparse(url).netloc
    now = time.time()
    prev = _last_hit.get(host)
    if prev is not None:
        wait = _MIN_HOST_INTERVAL - (now - prev)
        if wait > 0:
            time.sleep(wait)
    _last_hit[host] = time.time()


def _decode_body(raw: bytes, encoding_header: str, charset: str | None) -> str:
    if "gzip" in encoding_header:
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
    elif "deflate" in encoding_header:
        try:
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        except zlib.error:
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                pass
    for enc in filter(None, [charset, "utf-8", "cp1252", "latin-1"]):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def _curl_get(url: str, timeout: int = 30) -> Response:
    """Fallback fetcher for hosts that reject urllib.

    Some regulator sites (FATF) sit behind Cloudflare, which fingerprints the
    TLS/HTTP stack rather than just the headers - so no combination of headers
    makes urllib pass. curl presents a different fingerprint and is accepted.
    curl.exe ships with Windows 10 1803+ and with macOS/Linux, so this needs no
    install. Verified empirically: urllib 403 vs curl 200 on fatf-gafi.org.
    """
    import shutil
    import subprocess

    exe = shutil.which("curl")
    if not exe:
        return Response(url=url, status=0, body="", error="curl not available for fallback")

    cmd = [
        exe, "-sS", "-L", "--compressed",
        "--max-time", str(timeout),
        "-A", UA,
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-GB,en;q=0.9",
        "-w", "\n__FCR_STATUS__%{http_code}",
        url,
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout + 15, check=False)
    except (subprocess.TimeoutExpired, OSError) as e:
        return Response(url=url, status=0, body="", error=f"curl fallback: {e}")

    out = p.stdout.decode("utf-8", errors="replace")
    status = 0
    marker = "\n__FCR_STATUS__"
    if marker in out:
        out, _, tail = out.rpartition(marker)
        try:
            status = int(tail.strip())
        except ValueError:
            status = 0
    if status != 200:
        return Response(url=url, status=status, body="",
                        error=f"curl fallback got HTTP {status}")
    return Response(url=url, status=200, body=out)


def get(
    url: str,
    etag: str | None = None,
    last_modified: str | None = None,
    timeout: int = 30,
    retries: int = 2,
) -> Response:
    """Fetch a URL, returning a Response. Never raises."""
    headers = dict(BASE_HEADERS)
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    ctx = ssl.create_default_context()
    if os.environ.get("FCR_INSECURE_SSL") == "1":  # corporate MITM proxies
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    last_err = None
    for attempt in range(retries + 1):
        _throttle(url)
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                raw = r.read()
                body = _decode_body(
                    raw,
                    r.headers.get("Content-Encoding", "") or "",
                    r.headers.get_content_charset(),
                )
                return Response(
                    url=r.geturl(),
                    status=r.status,
                    body=body,
                    etag=r.headers.get("ETag"),
                    last_modified=r.headers.get("Last-Modified"),
                )
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return Response(url=url, status=304, body="")
            last_err = f"HTTP {e.code} {e.reason}"
            # 403 usually means bot-fingerprinting, not a real block - curl
            # presents a different TLS fingerprint and often succeeds.
            if e.code == 403:
                alt = _curl_get(url, timeout=timeout)
                if alt.ok:
                    return alt
                last_err = f"{last_err} (curl fallback: {alt.error or alt.status})"
            # 4xx other than 429 will not fix themselves on retry
            if e.code < 500 and e.code != 429:
                return Response(url=url, status=e.code, body="", error=last_err)
        except urllib.error.URLError as e:
            last_err = f"URL error: {e.reason}"
        except (TimeoutError, OSError) as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < retries:
            time.sleep(2 ** attempt)

    return Response(url=url, status=0, body="", error=last_err or "unknown error")


def get_json(url: str, **kw) -> tuple[dict | None, Response]:
    r = get(url, **kw)
    if not r.ok:
        return None, r
    try:
        return json.loads(r.body), r
    except json.JSONDecodeError as e:
        r.error = f"bad JSON: {e}"
        return None, r


def head_ok(url: str, timeout: int = 20) -> tuple[int, str]:
    """Used by `argus.py verify` to confirm a cited link is still live."""
    ctx = ssl.create_default_context()
    if os.environ.get("FCR_INSECURE_SSL") == "1":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    _throttle(url)
    req = urllib.request.Request(url, headers=BASE_HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except Exception as e:  # noqa: BLE001 - verification must never crash the run
        return 0, f"{type(e).__name__}: {e}"
