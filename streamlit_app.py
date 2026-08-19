"""Argus FinCrime — AML/KYC regulatory and financial crime intelligence.

Entry point. Run with:  python argus.py app     (or: streamlit run streamlit_app.py)
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Argus FinCrime — financial crime intelligence",
    page_icon=":material/visibility:",
    layout="wide",
    initial_sidebar_state="expanded",
)

import app_shared as sh  # noqa: E402

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

pages = {
    "Live": [
        st.Page("app_pages/feed.py", title="News feed",
                icon=":material/newspaper:", default=True),
        st.Page("app_pages/emerging.py", title="New & emerging",
                icon=":material/new_releases:"),
    ],
    "Reference": [
        st.Page("app_pages/typologies.py", title="Typologies",
                icon=":material/account_tree:"),
        st.Page("app_pages/cases.py", title="Case library",
                icon=":material/gavel:"),
    ],
    "System": [
        st.Page("app_pages/sources.py", title="Sources",
                icon=":material/rss_feed:"),
    ],
}

page = st.navigation(pages, position="sidebar")

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title(":material/visibility: Argus FinCrime")
    st.caption("Financial crime intelligence, always watching")

    s = sh.stats()
    if s:
        st.metric("Last checked", sh.ago(s.get("last_fetch")))
        st.caption(
            f"{s.get('items_relevant', 0):,} relevant items · "
            f"{s.get('sources', 0)} sources"
        )
    else:
        st.warning("No data yet — hit **Refresh now** on the news feed.", icon=":material/info:")

    st.divider()
    st.caption(
        "Sources are polled live from UK, EU and global regulators, "
        "FIUs and press. Nothing is AI-generated."
    )

page.run()
