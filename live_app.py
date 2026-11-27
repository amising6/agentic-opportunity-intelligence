import time
from pathlib import Path
from dataclasses import asdict

import pandas as pd
import streamlit as st

from opportunity_intelligence.discovery import (
    load_sources,
    discover,
)

st.set_page_config(
    page_title="Live Opportunity Intelligence",
    page_icon="🌐",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent

sources = [
    source
    for source in load_sources(
        str(ROOT / "config/job_sources.json")
    )
    if source.get("enabled", True)
]

st.title("🌐 Live Opportunity Intelligence")
st.caption("Data Engineering Copilot | Greenhouse Integration")

st.markdown(
    "[Main Platform]"
    "(https://de-copilot-opportunity-intelligence.streamlit.app)"
    " · [Website]"
    "(https://dataengineeringcopilot.com)"
    " · [GitHub]"
    "(https://github.com/amising6/agentic-opportunity-intelligence)"
)

st.info(
    "Discover publicly available career opportunities. "
    "No account access, résumé upload, AI inference "
    "or automatic application submission."
)

a, b, c = st.columns(3)

a.metric(
    "Greenhouse Sources",
    sum(s["provider"] == "greenhouse" for s in sources),
)

b.metric(
    "Lever Sources",
    sum(s["provider"] == "lever" for s in sources),
)

c.metric("Discovery Mode", "Live")

if "live_result" not in st.session_state:
    st.session_state.live_result = None


@st.cache_data(ttl=600, show_spinner=False, max_entries=64)
def search_jobs(selected_sources, keyword, location):
    started = time.monotonic()

    jobs, reports = discover(
        selected_sources,
        keyword=keyword,
        location=location,
    )

    return {
        "jobs": [asdict(job) for job in jobs],
        "reports": reports,
        "elapsed": round(time.monotonic() - started, 2),
    }


search_tab, source_tab, analytics_tab = st.tabs([
    "🔎 Live Discovery",
    "🌐 Source Registry",
    "📊 Execution Analytics",
])

with search_tab:

    st.subheader("Search Live Opportunities")

    providers = st.multiselect(
        "Job board providers",
        options=["greenhouse", "lever"],
        default=["greenhouse"],
        format_func=str.title,
    )

    available = [
        s for s in sources
        if s["provider"] in providers
    ]

    companies = sorted({
        s["organization"] for s in available
    })

    selected = st.multiselect(
        "Companies — leave empty to search all",
        options=companies,
    )

    selected_sources = [
        s for s in available
        if not selected or s["organization"] in selected
    ]

    a, b = st.columns(2)

    keyword = a.text_input(
        "Job title or keyword",
        value="data",
        max_chars=100,
    )

    location = b.text_input(
        "Location — optional",
        max_chars=100,
    )

    if st.button(
        "Search Live Opportunities",
        type="primary",
        disabled=not selected_sources,
    ):
        with st.spinner("Searching public career portals..."):
            try:
                st.session_state.live_result = search_jobs(
                    selected_sources,
                    keyword.strip(),
                    location.strip(),
                )
            except Exception as exc:
                st.session_state.live_result = None
                st.error(f"Discovery failed: {exc}")

    result = st.session_state.live_result

    if result is not None:

        jobs = result["jobs"]
        reports = result["reports"]

        failures = [
            report for report in reports
            if report.get("status") == "failed"
        ]

        a, b, c = st.columns(3)

        a.metric("Matching Opportunities", len(jobs))
        b.metric("Source Failures", len(failures))
        c.metric("Fetch Duration", f'{result["elapsed"]}s')

        if failures:
            st.warning(
                "Some sources failed. Results may be incomplete."
            )

        if jobs:

            frame = pd.DataFrame([
                {
                    "Company": job["organization"],
                    "Job Title": job["title"],
                    "Location": job["location"],
                    "Detected Skills": ", ".join(
                        job["required_skills"]
                    ),
                    "Job URL": job["source_url"],
                }
                for job in jobs
            ])

            st.dataframe(
                frame,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Job URL": st.column_config.LinkColumn(
                        "Career Portal",
                        display_text="View Job",
                    )
                },
            )

            st.download_button(
                "Download Opportunities CSV",
                frame.to_csv(index=False),
                file_name="live_opportunities.csv",
                mime="text/csv",
            )

            st.subheader("Job Description")

            lookup = {
                job["id"]: job for job in jobs
            }

            job_id = st.selectbox(
                "Select an opportunity",
                options=list(lookup),
                format_func=lambda key: (
                    lookup[key]["organization"]
                    + " | "
                    + lookup[key]["title"]
                ),
            )

            job = lookup[job_id]

            st.write(job["title"])
            st.caption(job["location"])
            st.text(job.get("description", ""))

        else:
            st.info(
                "No matching opportunities. "
                "Try a broader keyword or location."
            )

with source_tab:

    st.subheader("Configured Public Career Sources")

    st.dataframe(
        pd.DataFrame(sources),
        hide_index=True,
        use_container_width=True,
    )

with analytics_tab:

    st.subheader("Discovery Execution Analytics")

    result = st.session_state.live_result

    if result is None:
        st.info("Execute a search to view source analytics.")
    else:
        st.dataframe(
            pd.DataFrame(result["reports"]),
            hide_index=True,
            use_container_width=True,
        )

        if result["jobs"]:

            counts = pd.DataFrame(
                result["jobs"]
            )["organization"].value_counts()

            st.bar_chart(counts)

st.divider()

st.caption(
    "Public job board data may change. "
    "Search results are cached for up to 10 minutes. "
    "Detected skills are heuristic, not verified requirements. "
    "Always verify opportunities on the original career portal."
)
