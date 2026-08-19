"""Case library — real, documented financial crime cases with their backstory."""

from __future__ import annotations

import streamlit as st

import app_shared as sh

st.title("Case library")
st.caption(
    "Real cases, publicly documented. Headline facts were checked against primary "
    "sources when written — the linked source is the authority, so read it before "
    "relying on any detail here."
)

cases = sh.load_cases()
typ_names = sh.typology_names()

with st.container(border=True):
    query = st.text_input(
        "Search cases",
        placeholder="Search by name, country, year, typology… e.g. 'sanctions', 'Danske', 'UK'",
        label_visibility="collapsed",
    )
    all_t = sorted({t for c in cases.values() for t in c["typology_ids"]})
    chosen = st.pills(
        "Typology", all_t, selection_mode="multi", default=[],
        format_func=lambda t: typ_names.get(t, t),
        help="No selection shows everything.",
    )


def keep(c: dict) -> bool:
    if chosen and not set(chosen) & set(c["typology_ids"]):
        return False
    if query:
        hay = " ".join([
            c["name"], c["year"], c["jurisdiction"], c["headline"], c["backstory"],
            c["what_happened"], c["bank_impact"], c["analyst_lesson"],
            *[typ_names.get(t, t) for t in c["typology_ids"]],
        ]).lower()
        if not all(w in hay for w in query.lower().split()):
            return False
    return True


shown = [c for c in cases.values() if keep(c)]
shown.sort(key=lambda c: c["year"])

st.caption(f"**{len(shown)}** of {len(cases)} cases")

if not shown:
    st.info("No case matches that search.", icon=":material/search_off:")
    st.stop()

for c in shown:
    with st.container(border=True):
        st.markdown(f"### {c['name']}")
        st.caption(f"{c['year']}  ·  {c['jurisdiction']}")
        st.markdown(f"**{c['headline']}**")

        tags = st.container(horizontal=True, vertical_alignment="center")
        with tags:
            for t in c["typology_ids"]:
                st.badge(typ_names.get(t, t), color="violet")

        with st.expander("Read the full case"):
            st.markdown("#### Backstory")
            st.write(c["backstory"])

            st.markdown("#### What happened")
            st.write(c["what_happened"])

            left, right = st.columns(2)
            with left:
                st.markdown("#### Impact on banks")
                st.write(c["bank_impact"])
            with right:
                st.markdown("#### The analyst lesson")
                st.write(c["analyst_lesson"])

            st.markdown("#### Sources")
            links = st.container(horizontal=True, vertical_alignment="center")
            with links:
                for s in c["sources"]:
                    st.link_button(s.get("title", "Source"), s.get("url", ""),
                                   icon=":material/open_in_new:")
