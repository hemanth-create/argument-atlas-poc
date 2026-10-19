"""Run with: streamlit run app.py"""
from pathlib import Path

import pandas as pd
import streamlit as st

import ui
from core import (compare_rows, download_public_pdf, load_records, search, source_link, validate_anchor,
                  word_comparison)

st.set_page_config(page_title="Argument Atlas | POC", page_icon=":material/balance:", layout="wide")
st.html(ui.CSS)

records = load_records()
by_id = {r["id"]: r for r in records}
COURTS = ["All"] + sorted({r["court"] for r in records})
OUTCOMES = ["All"] + [o for o in ui.OUTCOMES if any(r["outcome"] == o for r in records)]
CHIPS = ["differential diagnosis", "accident severity", "biomechanics", "qualifications", "damages methodology"]
MAX_COMPARE = 4
TABS = [":material/manage_search: Research", ":material/compare_arrows: Compare", ":material/account_balance: Sources & scope"]
label = lambda id_: f"{by_id[id_]['expert']} — {by_id[id_]['case_name']} ({by_id[id_]['outcome']})"

st.session_state.setdefault("compare", ["scott-sevin", "scott-norsworthy"])


def set_query(key):
    st.session_state.q = st.session_state[key] or ""


def clear_filters():
    st.session_state.update(q="", court="All", outcome="All")


def toggle_compare(id_):
    picked = st.session_state.compare
    if id_ in picked:
        picked.remove(id_)
    elif len(picked) >= MAX_COMPARE:
        st.toast(f"Comparison holds up to {MAX_COMPARE} rulings. Remove one in the Compare tab first.", icon=":material/info:")
    else:
        picked.append(id_)


def sync_compare():
    st.session_state.compare = list(st.session_state.compare_ms)


def open_compare():
    st.session_state.view = TABS[1]


def quick_searches(key):
    st.session_state[key] = st.session_state.get("q") if st.session_state.get("q") in CHIPS else None
    st.pills("Quick searches", CHIPS, key=key, on_change=set_query, args=(key,), label_visibility="collapsed")


st.html(ui.masthead())
st.html(ui.boundary())
with st.expander("Provenance & limits", icon=":material/policy:"):
    st.markdown(ui.PROVENANCE)

research, compare, sources = st.tabs(TABS, key="view", on_change="rerun")

with research:
    with st.container(key="searchpanel"):
        query = st.text_input("Search curated rulings", key="q", type="search", icon=":material/search:", live=True,
                              placeholder="Issue, expert, or doctrine, e.g. differential diagnosis",
                              bind="query-params") or ""
        quick_searches("chip")
        a, b, c = st.columns([5, 6, 2], vertical_alignment="bottom")
        court = a.segmented_control("Court", COURTS, key="court", default="All", required=True,
                                    format_func=lambda v: "All courts" if v == "All" else v, bind="query-params")
        outcome = b.segmented_control("Motion-to-exclude outcome", OUTCOMES, key="outcome", default="All", required=True,
                                      format_func=lambda v: "Any outcome" if v == "All" else v, bind="query-params")
        c.button("Reset", icon=":material/restart_alt:", on_click=clear_filters, type="tertiary",
                 disabled=not query and court == "All" and outcome == "All")

    hits = search(records, query=query, court=court or "All", outcome=outcome or "All")
    st.html(ui.overview(len(records), len({r["case_id"] for r in records}), hits))

    picked = st.session_state.compare
    with st.container(key="tray", horizontal=True, vertical_alignment="center"):
        names = ", ".join(by_id[i]["expert"] for i in picked) or "none yet"
        st.markdown(f":material/compare_arrows: **Comparison** · {len(picked)} of {MAX_COMPARE} · {names}", width="stretch")
        st.button("Open comparison", icon=":material/arrow_forward:", on_click=open_compare, disabled=not picked)

    st.html(ui.results_head(len(hits), query))
    if not hits:
        found = f" for “{query.strip()}”" if query.strip() else ""
        st.html(ui.empty_state(f"No curated rulings{found}", "The starter set has 10 rulings. Try a broader issue, "
                               "an expert's surname, or clear the filters. Search matches keywords, not meaning."))
        with st.container(key="emptyactions", horizontal=True, horizontal_alignment="center"):
            quick_searches("chip_empty")
            st.button("Clear search and filters", icon=":material/filter_alt_off:", on_click=clear_filters, type="primary")
    for r in hits:
        selected = r["id"] in picked
        with st.container(key=f"rec_{r['id']}" + ("--sel" if selected else "")):
            st.html(ui.card(r, query))
            with st.expander("Argument → Opposition → Court's reasoning", icon=":material/account_tree:"):
                st.html(ui.steps(r, query))
            with st.container(horizontal=True, vertical_alignment="center"):
                st.link_button(f"Open order, p. {int(r['source_page'])}", ui.safe_url(source_link(r)) or "#",
                               icon=":material/open_in_new:", disabled=not ui.safe_url(r["source_url"]))
                st.button("In comparison" if selected else "Add to compare", key=f"cmp_{r['id']}",
                          icon=":material/check_circle:" if selected else ":material/add:",
                          type="primary" if selected else "secondary", on_click=toggle_compare, args=(r["id"],))

with compare:
    st.html('<p class="aa-sec">Compare rulings side by side</p><p class="aa-sub">Choose 2&ndash;4 expert challenges. '
            'Rows align across rulings so you can read each challenge, response, and rationale in parallel. '
            'Compared rulings are not necessarily factually or legally equivalent.</p>')
    st.session_state.compare_ms = list(st.session_state.compare)
    st.multiselect("Rulings in comparison", list(by_id), key="compare_ms", format_func=label,
                   max_selections=MAX_COMPARE, on_change=sync_compare, placeholder="Add a ruling to compare")
    selected = compare_rows(records, st.session_state.compare)
    if len(selected) == 1:
        st.info("Add at least one more ruling to compare.", icon=":material/info:")
    if selected:
        st.html(ui.compare_grid(selected))
        with st.container(key="exportpanel"):
            st.html('<p class="aa-label">Export</p>')
            with st.container(horizontal=True):
                st.download_button("Word comparison (DRAFT)", lambda: word_comparison(selected), type="primary",
                                   file_name="Argument_Atlas_Comparison_DRAFT.docx", icon=":material/description:",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   on_click="ignore")
                st.download_button("CSV", pd.DataFrame(selected).to_csv(index=False).encode("utf-8"),
                                   file_name="Argument_Atlas_Comparison.csv", mime="text/csv",
                                   icon=":material/table_view:", on_click="ignore")
            st.caption("The Word file is a marked DRAFT built from public court orders. It requires attorney review "
                       "and is not legal advice.")
    else:
        st.html(ui.empty_state("Nothing selected yet", "Pick rulings above, or use “Add to compare” on any "
                               "result card in Research."))

with sources:
    st.html('<p class="aa-sec">Public sources</p><p class="aa-sub">Each record comes from one of four real public '
            'court orders. No motion briefs have been packaged.</p>')
    st.html(ui.case_cards(records))
    st.html('<p class="aa-sec">Proof-of-concept scope</p>')
    st.html(ui.SCOPE)
    with st.container(key="spotpanel"):
        st.html('<p class="aa-sec" style="margin-top:0">Optional PDF spot-check</p><p class="aa-sub">With internet '
                'access, download a public order and confirm that a short reference phrase appears on the cited PDF '
                'page. <b>This does not verify the legal interpretation.</b></p>')
        chosen = st.selectbox("Record to spot-check", list(by_id), format_func=label)
        if st.button("Download public order and check page anchor", icon=":material/fact_check:"):
            r = by_id[chosen]
            try:
                with st.spinner("Retrieving the public source PDF..."):
                    path = download_public_pdf(r["source_url"], Path(__file__).parent / "downloads")
                    ok, message = validate_anchor(r, path)
                (st.success if ok else st.warning)(message, icon=":material/check_circle:" if ok else ":material/warning:")
                st.caption(f"Downloaded to {path.name}; you must still check accuracy of the summarized arguments "
                           "and reasoning.")
            except Exception as exc:
                st.error(f"Source check unavailable: {exc}", icon=":material/error:")
    st.warning("Prototype only. No legal citator, case-history verification, automated LLM extraction, OCR, or SHB "
               "integrations. Do not use this output as filing-ready legal research.", icon=":material/gavel:")

st.html(ui.footer())
