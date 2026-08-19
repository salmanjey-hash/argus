"""Sources — what Argus watches, and whether each source is actually responding."""

from __future__ import annotations

import streamlit as st

import app_shared as sh

st.title("Sources")
st.caption(
    "Every source was HTTP-verified before it went into the config. This page "
    "shows whether each one is still responding."
)

rows = sh.source_health()

if not rows:
    st.info("No sources polled yet. Refresh from the news feed first.",
            icon=":material/rss_feed:")
    st.stop()

ok = [r for r in rows if r["last_status"] in (200, 304)]
bad = [r for r in rows if r["last_status"] not in (200, 304)]

cols = st.columns(4)
cols[0].metric("Sources", len(rows))
cols[1].metric("Responding", len(ok))
cols[2].metric("Failing", len(bad), delta=None if not bad else f"-{len(bad)}",
               delta_color="inverse")
cols[3].metric("Items collected", f"{sum(r['n_items'] for r in rows):,}")

if bad:
    st.warning(
        "Some sources are not responding. FATF is expected to fail intermittently — "
        "it sits behind Cloudflare, which fingerprints the TLS stack rather than the "
        "headers, so no header combination gets a script through. Argus retries it "
        "via curl, which usually works.",
        icon=":material/warning:",
    )

table = [
    {
        "Source": r["name"],
        "Tier": r["tier"],
        "Where": r["jurisdiction"],
        "Type": r["type"],
        "Status": r["last_status"],
        "Items": r["n_items"],
        "Last checked": sh.ago(r["last_fetch_at"]),
        "Error": (r["last_error"] or "")[:60],
    }
    for r in rows
]

st.dataframe(
    table,
    width="stretch",
    hide_index=True,
    column_config={
        "Tier": st.column_config.NumberColumn(
            "Tier", help="1 = primary regulator · 2 = FIU/law enforcement · 3 = press",
            width="small",
        ),
        "Status": st.column_config.NumberColumn("HTTP", width="small"),
        "Items": st.column_config.NumberColumn("Items", width="small"),
    },
)

st.divider()

with st.expander("Deliberately disabled sources, and why"):
    st.markdown(
        "Three sources are switched off in `feeds.toml`. Each was tested and found "
        "unusable from a script — this is recorded rather than silently ignored.\n\n"
        "- **JMLSG** — returns HTTP 403 to any non-browser client (Akamai). Check "
        "[jmlsg.org.uk](https://www.jmlsg.org.uk/latest-news/) manually; it publishes rarely.\n"
        "- **Wolfsberg Group** — a single-page app, so the served HTML holds only "
        "JavaScript bundles and no content links. Check "
        "[wolfsberg-group.org/resources](https://wolfsberg-group.org/resources) quarterly.\n"
        "- **Europol main reports** — client-side rendered, same problem. The Europol "
        "newsroom RSS announces each flagship report anyway, so nothing is lost."
    )

with st.expander("How relevance is decided"):
    st.markdown(
        "There is no LLM in this pipeline. Classification is a keyword rule engine "
        "in `argus_core/classify.py`, which means it cannot invent a fact that was "
        "not in the source, and every decision is inspectable:\n\n"
        "```bash\n"
        "python argus.py why <item id>\n"
        "```\n\n"
        "That prints the exact terms that caused an item to be kept, categorised and "
        "prioritised. To tune it, edit the term weights in `classify.py` and run "
        "`python argus.py reclassify` — that re-scores everything already collected "
        "without re-hitting the regulators."
    )
