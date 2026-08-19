"""Live news feed — regulatory changes, enforcement, sanctions and fincrime news."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

import app_shared as sh

st.title("News feed")
st.caption(sh.EVIDENCE_NOTE)

typ_names = sh.typology_names()


# ---------------------------------------------------------------- refresh bar

@st.fragment(run_every="5m")
def refresh_bar() -> None:
    """Own fragment so the 'last checked' clock ticks without redrawing the feed.

    run_every only re-renders this strip. It never fetches on its own — polling
    regulators on a timer from a browser session would be rude and pointless.
    Auto-refresh below is opt-in and rate-limited.
    """
    s = sh.stats()
    last = s.get("last_fetch") if s else None

    bar = st.container(horizontal=True, vertical_alignment="center")
    with bar:
        go = st.button("Refresh now", icon=":material/refresh:", type="primary")
        deep = st.toggle(
            "Include weekly sources", value=False,
            help="Also polls FATF, AMLA, OpenSanctions and other low-frequency "
                 "sources. Slower — use once a week.",
        )
        auto = st.toggle(
            "Auto", value=st.session_state.auto_refresh,
            help="Re-check every 15 minutes while this tab is open.",
        )
        st.session_state.auto_refresh = auto
        st.markdown(f"Last checked **{sh.ago(last)}**")

    due = False
    if auto and last:
        try:
            dt = datetime.fromisoformat(last)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            due = (datetime.now(timezone.utc) - dt).total_seconds() > 900
        except ValueError:
            due = False

    if go or due:
        with st.status("Checking sources…", expanded=True) as status:
            log = st.empty()
            seen: list[str] = []

            def on_source(r) -> None:
                if r.unchanged:
                    line = f"· {r.name} — unchanged"
                elif not r.ok:
                    line = f"✗ {r.name} — {r.error}"
                else:
                    line = f"✓ {r.name} — {r.new} new, {r.kept} relevant"
                seen.append(line)
                log.code("\n".join(seen[-14:]), language=None)

            out = sh.refresh(daily_only=not deep, progress=on_source)
            msg = (f"{out.new_total} new · {out.kept_total} relevant · "
                   f"{out.ok_count} sources ok")
            if out.fail_count:
                msg += f" · {out.fail_count} failed"
            status.update(label=msg, state="complete", expanded=False)

        if out.failures:
            st.warning(
                "Some sources did not respond: "
                + ", ".join(f.name for f in out.failures)
                + ". FATF blocks scripted clients intermittently — that one is "
                  "expected to fail sometimes. See the Sources page.",
                icon=":material/warning:",
            )
        st.rerun()


refresh_bar()
st.divider()

# ------------------------------------------------------------------- filters
items = sh.load_items(days=60, relevant_only=True)

if not items:
    st.info(
        "Nothing collected yet. Press **Refresh now** above to pull the latest "
        "from every source — it takes about a minute the first time.",
        icon=":material/rss_feed:",
    )
    st.stop()

with st.container(border=True):
    row = st.container(horizontal=True, vertical_alignment="bottom")
    with row:
        query = st.text_input(
            "Search", placeholder="Search headlines, summaries, typologies…",
            label_visibility="collapsed",
        )
        window = st.selectbox(
            "Window", [1, 3, 7, 14, 30, 60], index=3,
            format_func=lambda d: "Last 24 hours" if d == 1 else f"Last {d} days",
            label_visibility="collapsed",
        )
    juris = st.segmented_control(
        "Jurisdiction", ["UK", "EU", "Global"], selection_mode="multi",
        default=["UK", "EU", "Global"],
    )
    cats = sorted({i["category"] for i in items})
    chosen_cats = st.pills(
        "Category", cats, selection_mode="multi", default=[],
        help="No selection shows everything.",
    )
    only_high = st.toggle("High priority only", value=False)

# -------------------------------------------------------------------- filter
cutoff = datetime.now(timezone.utc).timestamp() - window * 86400


def keep(i: dict) -> bool:
    if juris and i["jurisdiction"] not in juris:
        return False
    if chosen_cats and i["category"] not in chosen_cats:
        return False
    if only_high and i["priority"] != "High":
        return False
    when = i.get("when")
    if when:
        try:
            dt = datetime.fromisoformat(when)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt.timestamp() < cutoff:
                return False
        except ValueError:
            pass
    if query:
        hay = " ".join([
            i["title"], i.get("summary_raw") or "", i["source_name"],
            i.get("publisher") or "",
            " ".join(typ_names.get(t, t) for t in i["typologies"]),
        ]).lower()
        if not all(w in hay for w in query.lower().split()):
            return False
    return True


shown = [i for i in items if keep(i)]
shown.sort(key=lambda i: (sh.PRIORITY_ORDER.get(i["priority"], 3), i.get("when") or ""),
           reverse=False)

n_high = sum(1 for i in shown if i["priority"] == "High")

if not shown:
    st.caption("**0** items")
    st.info("Nothing matches those filters.", icon=":material/filter_alt_off:")
    st.stop()

# ---------------------------------------------------------------- pagination
# Each card is several elements, so rendering the whole result set put the
# Streamlit Cloud container into a very long rerun. 25 a page keeps it snappy.
PER_PAGE = 25
pages = (len(shown) + PER_PAGE - 1) // PER_PAGE

bar = st.container(horizontal=True, vertical_alignment="center")
with bar:
    st.markdown(f"**{len(shown)}** item(s) · {n_high} high priority · "
                "highest priority first, then newest")
    page = st.number_input(
        "Page", min_value=1, max_value=max(pages, 1), value=1, step=1,
        label_visibility="collapsed", width=110,
    ) if pages > 1 else 1

start = (int(page) - 1) * PER_PAGE
batch = shown[start:start + PER_PAGE]
if pages > 1:
    st.caption(f"Showing {start + 1}–{start + len(batch)} of {len(shown)} "
               f"(page {int(page)} of {pages})")

# --------------------------------------------------------------------- feed
for i in batch:
    with st.container(border=True):
        # Markdown link rather than a link_button: one element instead of two,
        # and it keeps the headline itself clickable.
        st.markdown(f"#### [{i['title']}]({i['url']})")

        meta = [i["source_name"], sh.fmt_date(i.get("published_at"))]
        if i.get("publisher") and i["publisher"] not in i["source_name"]:
            meta.append(i["publisher"])
        if i.get("also_from"):
            meta.append(f"also via {', '.join(i['also_from'])}")
        st.caption(" · ".join(meta))

        if i.get("summary_raw"):
            st.write(i["summary_raw"])
        else:
            st.caption("_Source published no summary — open the link._")

        # One markdown line of tags rather than several badge elements.
        colour = {"High": "red", "Medium": "orange"}.get(i["priority"], "gray")
        tags = [f":{colour}-badge[{i['priority']}]",
                f":blue-badge[{i['jurisdiction']}]",
                f":violet-badge[{i['category']}]"]
        if i.get("has_deadline"):
            tags.append(":orange-badge[:material/schedule: date/deadline]")
        for t in i["typologies"]:
            tags.append(f":gray-badge[:material/account_tree: {typ_names.get(t, t)}]")
        st.markdown(" ".join(tags))
