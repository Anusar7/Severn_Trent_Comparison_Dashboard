"""Run: python -m streamlit run app.py. Read this file from top to bottom."""
from pathlib import Path
import pandas as pd
import streamlit as st
import branding as brand
from analysis import (load_data, history_results, achievement, peer_rank,
                      format_value, change_description)
from charts import trend_chart, peer_chart

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Severn Trent | Performance review", layout="wide")
measures, history, peers, sources = load_data()

# This short CSS block changes appearance only. All app behaviour is Python.
st.markdown(f"""
<style>

.block-container {{
    max-width: 1280px;
    padding-top: 3rem;
}}

h1, h2, h3 {{
    color: {brand.NAVY};
    letter-spacing: -0.025em;
}}

[data-testid="stMetric"] {{
    background: #F1F6F6;
    padding: 18px;
    border-top: 3px solid {brand.TEAL};
    border-radius: 4px;
}}

[data-testid="stMetricValue"] {{
    color: {brand.NAVY};
}}

/* AMP7 subtitle */
.eyebrow {{
    color: {brand.NAVY};
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 8px;
    margin-bottom: 8px;
    opacity: 1;
}}

.intro {{
    border-left: 4px solid {brand.TEAL};
    padding: 4px 0 4px 18px;
    margin: 14px 0 24px;
    font-size: 18px;
    color: {brand.NAVY};
}}

</style>
""", unsafe_allow_html=True)

heading, logo = st.columns([6, 1])
with heading:
    st.markdown('<div class="eyebrow">AMP7 performance review · 2020/21–2024/25</div>', unsafe_allow_html=True)
    st.title(f"{brand.TITLE} | {brand.SUBTITLE}")
    st.caption(f"{brand.AUTHOR} · Independent analysis · Ofwat October 2025 report snapshot")
if brand.LOGO and (ROOT / brand.LOGO).is_file():
    with logo:
        st.image(str(ROOT / brand.LOGO), width=140)

page = st.radio("Navigation", ["Overview", "Measure explorer", "Recommendations"],
                horizontal=True, label_visibility="collapsed")
st.divider()


def source_link(source_id, page_number=None):
    source = sources.loc[source_id]
    suffix = f"#page={int(page_number)}" if page_number is not None else ""
    return f"[{source.title}]({source.url}{suffix})"


def overview():
    st.subheader("Where is attention needed?")
    st.markdown('<div class="intro">Pollution and drinking-water quality warrant investigation. '
                'Strong leakage and supply-interruption results show that performance is mixed.</div>',
                unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Full numeric targets missed", f"{int((measures.target_met == False).sum())} / {int(measures.target.notna().sum())}")
    b.metric("Behind the published sector benchmark", f"{int(measures.behind_sector.sum())} / {len(measures)}")
    c.metric("Period reviewed", "5 years")
    st.caption("Numeric target results are our calculation, not Ofwat’s overall categorisation. "
               "C-MeX uses the sector median; treatment compliance is below its full target but within its payment deadband.")
    left, right = st.columns([2, 1])
    scope = left.selectbox("Show", ["Target missed or behind sector", "All 12 measures", "Full target missed", "Behind sector"])
    domain = right.selectbox("Service", ["All services", "Wastewater", "Water", "Customer"])
    rows = measures.copy()
    if scope == "Target missed or behind sector":
        rows = rows[rows.attention]
    elif scope == "Full target missed":
        rows = rows[rows.target_met == False]
    elif scope == "Behind sector":
        rows = rows[rows.behind_sector]
    if domain != "All services":
        rows = rows[rows.domain == domain]
    table = []
    for _, m in rows.iterrows():
        table.append({"Measure": m["name"], "Actual": format_value(m.actual, m),
            "Full target": format_value(m.target, m),
            "Target result": "Median-based" if pd.isna(m.target) else "Met" if m.target_met else "Missed",
            "Sector benchmark": format_value(m.benchmark, m),
            "Peer result": "Behind" if m.behind_sector else "At / ahead",
            "Unit": m.unit})
    if table:
        st.dataframe(pd.DataFrame(table), hide_index=True, width="stretch")
    else:
        st.info("No measures match these filters.")
    st.caption("Peer benchmarks are the published average, median or sector reduction for each measure. "
               "They are not a simple average of the displayed companies. Different metrics have different units.")
    st.caption("Supply interruptions are displayed as minutes and seconds. CRI, pollution and treatment results refer to calendar 2024; other results to 2024/25.")
    with st.expander("Five-year target record"):
        summary = []
        for _, m in measures.iterrows():
            h = history_results(m, history)
            score = achievement(m, h)
            record = {"Measure": m["name"]}
            for _, row in h.iterrows():
                if m.id == "internal":
                    record[row.year] = "APR met" if row.met else "APR missed"
                elif m.id == "cmex":
                    record[row.year] = "—"
                else:
                    record[row.year] = "Met" if row.met else "Missed"
            record["Achievement"] = f"{score[0]}/{score[1]} ({score[0]/score[1]:.0%})" if score else "Not scored"
            summary.append(record)
        st.dataframe(pd.DataFrame(summary), hide_index=True, width="stretch")
        st.caption("Internal flooding uses original APR values only; its combined score is withheld. "
                   "C-MeX has no fixed numeric target. PSR scores refer to reach only, not the whole PSR commitment. "
                   "CRI and treatment scores use full targets, not payment deadbands. PCC is unadjusted.")


def explorer():
    names = dict(zip(measures.id, measures["name"]))
    selected = st.selectbox("Choose a measure", list(names),
                            index=list(names).index("pollution"), format_func=names.get)
    m = measures[measures.id == selected].iloc[0]
    h = history_results(m, history)
    p = peer_rank(m, peers)
    st.subheader(m["name"])
    st.write(m.definition)
    st.caption(f"{m.unit} · {m.direction.capitalize()} is better · Latest period: {m.period}")
    a, b, c, d = st.columns(4)
    a.metric("Ofwat actual", format_value(m.actual, m))
    b.metric("Full target", format_value(m.target, m))
    c.metric("Sector " + m.benchmark_type, format_value(m.benchmark, m))
    rank = int(p[p.company == "Severn Trent Water"]["rank"].iloc[0])
    d.metric("Peer rank · 1 is best", f"{rank} / {len(p)}")
    if pd.notna(m.gap):
        gap_unit = "percentage points" if m.unit.startswith("%") else m.unit
        relative = f" ({m.gap_pct:+.2f}% of target)" if pd.notna(m.gap_pct) else ""
        st.caption(f"Adverse target gap: {m.gap:+.2f} {gap_unit}{relative}. Positive means a shortfall; negative means better than target.")
    st.caption("Ranks include separately reported operating regions where applicable; ties share a rank.")
    if m.id == "internal":
        st.warning("Source difference: Ofwat reports 1.52 (target missed); the original APR reports 1.33 "
                   "(target met). The history below is the original APR series. Its combined achievement score "
                   "and change rates are withheld until the full series is reconciled.")
    elif m.id in {"cri", "treatment"}:
        st.info(f"The full target is {format_value(m.target, m)}. The payment deadband is "
                f"{format_value(m.deadband, m)}. These are different assessment thresholds.")
    elif m.id == "pcc":
        st.info("Peer comparison: unadjusted litres/person/day. Historical trend: percentage reduction "
                "from baseline. These are different units. Ofwat’s payment-adjusted 130.4 also exceeds the 129.0 target.")
    trend, comparison = st.tabs(["Five-year trend", "Peer comparison"])
    with trend:
        a, b = st.columns(2)
        score = achievement(m, h)
        label = "Reach targets met" if m.id == "psr" else "Full targets met"
        a.metric(label, f"{score[0]}/{score[1]} · {score[0]/score[1]:.0%}" if score else "Not scored")
        change, explanation = change_description(m, h)
        b.metric("Change across the period", change)
        st.caption(explanation)
        st.plotly_chart(trend_chart(m, h), width="stretch", config={"displayModeBar": False})
        if m.id == "cmex":
            st.caption("Historical scores use the APR, except 2024/25: Ofwat 74.43 replaces APR 74.42. "
                       "Only the verified final-year median is shown; this is not a five-year fixed-target score.")
        if m.id in {"cri", "pollution", "treatment"}:
            st.caption("Chart labels are calendar years 2020–2024, reported in financial years 2020/21–2024/25.")
        with st.expander("Exact values and source notes"):
            values = pd.DataFrame({"Reporting year": h.year, "Measurement period": h.period,
                "Actual": h.actual, "Full target": h.target})
            st.dataframe(values, hide_index=True, width="stretch")
            st.caption("Unit: " + m.history_unit)
            st.write(m.note.replace("; see the CRI baseline note in Guide & sources", ""))
            st.markdown("Historical actuals: " + source_link("apr25", 25) + " · printed p24.")
            if m.id != "cmex":
                source = "apr23" if m.id in {"pcc", "leakage"} else "apr21"
                st.markdown("Historical targets: " + source_link(source, 32 if source == "apr23" else 51))
    with comparison:
        st.caption(f"Purple dashed line: published sector {m.benchmark_type} · "
                   f"{format_value(m.benchmark, m)}. Navy bar: Severn Trent.")
        st.plotly_chart(peer_chart(m, p), width="stretch", config={"displayModeBar": False})
        if m.id == "collapses":
            st.caption("The difference from the sector average is only 0.02 per 1,000 km. Treat it proportionately.")
        if m.id == "leakage":
            st.caption("This compares reduction from each company’s own baseline, not absolute leakage efficiency.")
        if m.id == "psr":
            st.caption("Register reach alone does not establish whether vulnerable customers receive adequate support.")
    st.caption(f"Source: Ofwat October 2025 report, p{int(m.page)}.")
    st.markdown(source_link("ofwat25", m.page))


def recommendations():
    st.subheader("From performance gaps to investigation priorities")
    st.write("These are proposed next steps based on published results. The company-level data identify "
             "questions to investigate; they do not identify incident causes or infiltration hotspots.")
    items = [
        ("01 · Investigate wastewater deterioration", "Pollution increased from 20.60 to 29.30 incidents per 10,000 km "
         "between 2020 and 2024; the 2024 target was 19.50. Internal flooding misses its target in Ofwat’s edition.",
         "Reconcile flooding records first. Then join verified incident locations, dates, rainfall, sewer levels "
         "and asset records to identify repeat locations and wet-weather patterns for operational review.",
         "Track source reconciliation, repeat incidents and completeness of location/time fields. Rainfall association alone would not prove infiltration."),
        ("02 · Investigate the increase in drinking-water risk", "CRI rose from 1.53 in 2020 to 10.32 in 2024, "
         "above the 2.00 payment deadband and 2.11 sector median.",
         "Review the failures contributing most to CRI, their sites, severity and recurrence. "
         "Check whether corrective actions were completed and whether subsequent results improved.",
         "Track repeat failures and overdue corrective actions. CRI is a risk score, not the percentage of unsafe water."),
        ("03 · Follow up customer and consumption gaps", "C-MeX is 74.43 versus the 74.74 median. "
         "Unadjusted consumption is 133.1 litres/person/day against a 129.0 target.",
         "Break customer feedback down by journey and repeat contact. For consumption, examine metering, "
         "customer-side leaks and water-efficiency activity using a consistent reporting basis.",
         "Track repeat contacts, resolution times and consumption trends. Keep adjusted and unadjusted consumption separate.")]
    for title, evidence, action, check in items:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write(evidence)
            left, right = st.columns([3, 2])
            left.markdown("**Next analysis**")
            left.write(action)
            right.markdown("**How to assess progress**")
            right.write(check)
    st.success("Retain the strengths: leakage reduction reached 16.8% against 14.3%; supply interruptions fell "
               "to 4m 34s against a 5m target. Review which practices are transferable before proposing wider adoption.")


if page == "Overview":
    overview()
elif page == "Measure explorer":
    explorer()
else:
    recommendations()

with st.expander("Sources and assessment basis"):
    st.write("This is a fixed review of 2020/21–2024/25, not a live performance feed. Official figures were "
             "transcribed from published reports and checked against the retained PDFs. The October 2025 "
             "Ofwat PDF is not updated for final ODI determinations. Calculations use rounded published figures.")
    st.write("Full-target results are separate from payment deadbands. Ofwat’s published assessment identifies "
             "C-MeX, PCC, CRI, internal flooding and pollution as below its assessment level. Our numeric screen "
             "excludes C-MeX and includes treatment compliance, so the identical count of five has different membership.")
    for source_id, source in sources.iterrows():
        st.markdown("- " + source_link(source_id) + " — " + source.edition)
st.divider()
st.caption(f"{brand.AUTHOR} · Independent interview project · Not affiliated with Severn Trent or Ofwat. "
           "Severn Trent logo reproduced from its 2024/25 Annual Performance Report.")
