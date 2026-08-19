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
        "**How the drafting works.** Press *Draft from source* on any item and Argus "
        "fetches the full article and pulls out the sentences that describe a "
        "mechanism, a red flag or an outcome — **verbatim, each with its source URL**. "
        "It writes those into a draft file for you.\n\n"
        "It quotes; it does not paraphrase. A model writing *\"criminals typically "
        "structure below £10,000\"* from memory can be wrong about the threshold, the "
        "country or the year. A sentence quoted out of an FCA notice cannot be wrong "
        "about what the FCA said. The analysis fields — what it is, impact on banks, "
        "how to spot it — stay empty for you to write, and `promote` refuses a draft "
        "until they are filled."
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
            drafted = st.button("Draft from source", key=f"draft{r['id']}",
                                icon=":material/edit_note:")

        if drafted:
            with st.spinner("Fetching the source and pulling quotes…"):
                d = sh.draft_from_item(r)
            if d.get("error"):
                st.error(f"Could not fetch the source: {d['error']}", icon=":material/error:")
            elif not d["total"]:
                st.warning(
                    "Fetched, but no sentence matched a mechanism, red-flag or "
                    "outcome pattern — usually that means it is a landing page "
                    "rather than an article. Open the source and read it.",
                    icon=":material/info:",
                )
            else:
                st.success(f"Draft saved to `drafts/{d['slug']}.toml` — "
                           f"{d['total']} quoted line(s).", icon=":material/check_circle:")
                for label, key in (("How it worked", "mechanics"),
                                   ("Red flags / failings", "red_flags"),
                                   ("Outcome", "outcomes")):
                    if d[key]:
                        st.markdown(f"**{label}** — quoted verbatim")
                        for qt in d[key]:
                            st.markdown(f"> {qt}")
                st.caption(
                    f"Every line above is verbatim from {r['url']}. Fill in the "
                    f"analysis fields in the draft file, then run "
                    f"`python argus.py promote {d['slug']}`."
                )

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
