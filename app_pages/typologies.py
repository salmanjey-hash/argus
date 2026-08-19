"""Typology library — what it is, how it works, what it costs banks,
red flags, how to spot it, and the real case behind it.

Performance note: this page used to render all 25 typologies as expanders.
Streamlit computes collapsed expander contents anyway, so that built every
typology body plus every nested case body on every rerun — fine on a laptop,
far too heavy for a Streamlit Cloud container. It now renders a compact list
and the full body for one selected typology only.
"""

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
mentions = sh.typology_mentions(days=60)

# ------------------------------------------------------------------- filters
with st.container(border=True):
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


shown = sorted([t for t in typ.values() if keep(t)],
               key=lambda t: (t["family"], t["name"]))

st.caption(f"**{len(shown)}** of {len(typ)} typologies · "
           f"{len(cases)} documented cases in the library")

if not shown:
    st.info("No typology matches that search.", icon=":material/search_off:")
    st.stop()


def label_for(tid: str) -> str:
    t = typ[tid]
    bits = [t["name"]]
    n_cases = len([c for c in cases.values() if tid in c["typology_ids"]])
    if n_cases:
        bits.append(f"{n_cases} case{'s' if n_cases > 1 else ''}")
    n_news = len(mentions.get(tid, []))
    if n_news:
        bits.append(f"{n_news} in the news")
    return "  ·  ".join(bits)


selected = st.selectbox(
    "Open a typology",
    [t["id"] for t in shown],
    format_func=label_for,
)

# ------------------------------------------------------------- selected entry
t = typ[selected]
linked = [c for c in cases.values() if t["id"] in c["typology_ids"]]
news = mentions.get(t["id"], [])

with st.container(border=True):
    st.subheader(t["name"])
    if t["aka"]:
        st.caption(f"Also called: {', '.join(t['aka'])}  ·  {t['family']}  ·  id `{t['id']}`")
    else:
        st.caption(f"{t['family']}  ·  id `{t['id']}`")

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
                st.markdown("**Backstory**")
                st.write(c["backstory"])
                st.markdown("**What happened**")
                st.write(c["what_happened"])
                st.markdown("**The analyst lesson**")
                st.write(c["analyst_lesson"])
                if c.get("verify_note"):
                    st.warning(c["verify_note"], icon=":material/link_off:")
                links = st.container(horizontal=True, vertical_alignment="center")
                with links:
                    for s in c["sources"]:
                        st.link_button(s.get("title", "Source"), s.get("url", ""),
                                       icon=":material/open_in_new:")
    else:
        st.info(
            "No documented case in the library for this typology yet. Add one as a "
            "`[[case]]` block in `cases.toml` — nothing is invented to fill the gap.",
            icon=":material/info:",
        )

    # ---- live news mentions
    if news:
        st.markdown("##### Recent items matching this typology")
        for i in news[:8]:
            st.markdown(
                f"- [{i['title']}]({i['url']}) — {i['source_name']}, "
                f"{sh.fmt_date(i.get('published_at'))}"
            )

    if t["sources"]:
        st.markdown("##### Sources")
        for s in t["sources"]:
            st.markdown(f"- [{s.get('title','')}]({s.get('url','')})")

# -------------------------------------------------------------- compact list
st.subheader("All typologies", divider="gray")
st.caption("Pick one above to read it in full.")

current_family = None
for t in shown:
    if t["family"] != current_family:
        current_family = t["family"]
        st.markdown(f"**{current_family}**")
    n_cases = len([c for c in cases.values() if t["id"] in c["typology_ids"]])
    n_news = len(mentions.get(t["id"], []))
    tail = []
    if n_cases:
        tail.append(f"{n_cases} case{'s' if n_cases > 1 else ''}")
    if n_news:
        tail.append(f":red[{n_news} in the news]")
    suffix = f" — {' · '.join(tail)}" if tail else ""
    st.markdown(f"- **{t['name']}**{suffix}  \n  {t['summary'][:150]}…")
