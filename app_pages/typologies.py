"""Typology library — what it is, how it works, what it costs banks,
red flags, how to spot it, and the real case behind it."""

from __future__ import annotations

import streamlit as st

import app_shared as sh

st.title("Typologies")
st.caption(
    "Every money laundering and financial crime method in the library, with the "
    "real case behind it, its impact on banks, the red flags, and how to spot it "
    "in your own data."
)

typ = sh.load_typologies()
cases = sh.load_cases()

# recent feed items mentioning each typology, so the reference links back to the news
recent = sh.load_items(days=60, relevant_only=True)
mentions: dict[str, list[dict]] = {}
for i in recent:
    for t in i["typologies"]:
        mentions.setdefault(t, []).append(i)

# ------------------------------------------------------------------- filters
with st.container(border=True):
    row = st.container(horizontal=True, vertical_alignment="bottom")
    with row:
        query = st.text_input(
            "Search typologies",
            placeholder="Search by name, red flag, keyword… e.g. 'invoice', 'cash', 'crypto'",
            label_visibility="collapsed",
        )
    families = sorted({t["family"] for t in typ.values()})
    chosen = st.pills("Family", families, selection_mode="multi", default=[],
                      help="No selection shows everything.")


def keep(t: dict) -> bool:
    if chosen and t["family"] not in chosen:
        return False
    if query:
        hay = " ".join([
            t["name"], t["family"], *t["aka"], *t["keywords"], t["summary"],
            t["bank_impact"], *t["mechanics"], *t["red_flags"], *t["how_to_spot"],
        ]).lower()
        if not all(w in hay for w in query.lower().split()):
            return False
    return True


shown = [t for t in typ.values() if keep(t)]
shown.sort(key=lambda t: (t["family"], t["name"]))

st.caption(f"**{len(shown)}** of {len(typ)} typologies · "
           f"{len(cases)} documented cases in the library")

if not shown:
    st.info("No typology matches that search.", icon=":material/search_off:")
    st.stop()

# -------------------------------------------------------------------- render
current_family = None
for t in shown:
    if t["family"] != current_family:
        current_family = t["family"]
        st.subheader(current_family, divider="gray")

    linked = [c for c in cases.values() if t["id"] in c["typology_ids"]]
    news = mentions.get(t["id"], [])

    label = f"**{t['name']}**"
    if linked:
        label += f"  ·  {len(linked)} case{'s' if len(linked) > 1 else ''}"
    if news:
        label += f"  ·  :red[{len(news)} in the news]"

    with st.expander(label):
        if t["aka"]:
            st.caption(f"Also called: {', '.join(t['aka'])}  ·  id `{t['id']}`")

        st.markdown("##### What it is")
        st.write(t["summary"])

        left, right = st.columns(2)
        with left:
            st.markdown("##### How it works")
            for n, m in enumerate(t["mechanics"], 1):
                st.markdown(f"{n}. {m}")
        with right:
            st.markdown("##### Impact on banks")
            st.write(t["bank_impact"])

        fl, sp = st.columns(2)
        with fl:
            st.markdown("##### :red[Red flags]")
            for r in t["red_flags"]:
                st.markdown(f"- {r}")
        with sp:
            st.markdown("##### :blue[How to spot it]")
            for h in t["how_to_spot"]:
                st.markdown(f"- {h}")

        st.markdown("##### What to do as the analyst")
        for a in t["analyst_actions"]:
            st.markdown(f"- {a}")

        # ---- the real case
        st.markdown("##### The real case")
        if linked:
            for c in linked:
                with st.container(border=True):
                    st.markdown(f"**{c['name']}**  ·  {c['year']}  ·  {c['jurisdiction']}")
                    st.caption(c["headline"])
                    with st.expander("Read the backstory"):
                        st.markdown("**Backstory**")
                        st.write(c["backstory"])
                        st.markdown("**What happened**")
                        st.write(c["what_happened"])
                        st.markdown("**Impact on banks**")
                        st.write(c["bank_impact"])
                        st.markdown("**The analyst lesson**")
                        st.write(c["analyst_lesson"])
                        for s in c["sources"]:
                            st.link_button(s.get("title", "Source"), s.get("url", ""),
                                           icon=":material/open_in_new:")
        else:
            st.info(
                "No documented case in the library for this typology yet. "
                "Add one as a `[[case]]` block in `cases.toml` — nothing is "
                "invented to fill the gap.",
                icon=":material/info:",
            )

        # ---- live news mentions
        if news:
            st.markdown("##### Recent items matching this typology")
            for i in news[:6]:
                st.markdown(
                    f"- [{i['title']}]({i['url']}) — {i['source_name']}, "
                    f"{sh.fmt_date(i.get('published_at'))}"
                )

        if t["sources"]:
            st.markdown("##### Sources")
            for s in t["sources"]:
                st.markdown(f"- [{s.get('title','')}]({s.get('url','')})")
