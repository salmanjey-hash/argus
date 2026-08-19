"""New & emerging — items describing a method the typology library does not cover."""

from __future__ import annotations

import streamlit as st

import app_shared as sh

st.title("New & emerging")
st.caption(
    "Relevant items that describe a *method* — a typology, red flag, modus operandi "
    "or emerging trend — but match nothing in the library. This is a review queue "
    "for you, not an auto-updater."
)

with st.container(border=True):
    st.markdown(
        "**Why this is a queue and not automatic.** Argus can reliably tell you "
        "*\"this item is describing a technique we hold nothing on\"* by matching "
        "language patterns. It cannot responsibly write a typology entry by itself — "
        "that would mean generating content, which is exactly what the rest of this "
        "tool avoids. You read the source, decide if it is genuinely new, and add it."
    )

row = st.container(horizontal=True, vertical_alignment="bottom")
with row:
    days = st.selectbox(
        "Window", [7, 14, 30, 60, 90], index=3,
        format_func=lambda d: f"Last {d} days", label_visibility="collapsed",
    )

rows = sh.candidates(days=days, limit=60)

if not rows:
    st.success(
        f"Nothing unmatched in the last {days} days — everything relevant mapped to "
        "a typology already in the library.",
        icon=":material/check_circle:",
    )
    st.stop()

st.caption(f"**{len(rows)}** item(s) to review")

for r in rows:
    with st.container(border=True):
        st.markdown(f"**{r['title']}**")
        st.caption(f"{r['source_name']} · {sh.fmt_date(r.get('published_at'))} · "
                   f"{r.get('jurisdiction','')} · {r.get('category','')}")
        if r.get("summary_raw"):
            st.write(r["summary_raw"])

        tags = st.container(horizontal=True, vertical_alignment="center")
        with tags:
            for s in r["signals"][:5]:
                st.badge(s, color="orange")
            st.link_button("Open source", r["url"], icon=":material/open_in_new:")

st.divider()
with st.expander("How to add a new typology"):
    st.markdown(
        "1. Read the source and confirm it is a genuinely distinct method, not a "
        "variant of something already in the library.\n"
        "2. Add a `[[typology]]` block to `typologies.toml` with: `id`, `name`, "
        "`aka`, `family`, `summary`, `mechanics`, `bank_impact`, `red_flags`, "
        "`how_to_spot`, `analyst_actions`, `keywords`, and `[[typology.sources]]`.\n"
        "3. If there is a documented case, add a `[[case]]` block to `cases.toml` "
        "with `typology_ids = [\"your-new-id\"]`.\n"
        "4. Run `python argus.py reclassify` so past items get tagged against it.\n\n"
        "The `keywords` list is what links live news to the typology, so make it "
        "specific — generic words will produce false matches."
    )
