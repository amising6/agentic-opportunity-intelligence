"""Streamlit dashboard for fictional opportunities."""
from pathlib import Path
import os
import pandas as pd
import streamlit as st
from opportunity_intelligence.core import ALLOWED
from opportunity_intelligence.demo import seed

ROOT = Path(__file__).resolve().parent
STATE_PATH = Path(os.environ.get("OPPORTUNITY_STATE", str(ROOT / "data" / "demo_state.json")))
store = seed(ROOT / "sample_data", STATE_PATH)
state = store.load()
records = list(state["records"].values())

st.set_page_config(page_title="Opportunity Intelligence", layout="wide")
st.title("Opportunity Intelligence")
st.caption("Workflow orchestration · Synthetic data · Human-reviewed transitions")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Discovered", len(records))
c2.metric("Qualified", sum(bool(r["evaluation"]["qualified"]) for r in records))
c3.metric("Awaiting approval", sum(r["stage"] == "prepared" for r in records))
c4.metric("Recorded submissions", sum(r["stage"] == "submitted" for r in records))

rows = [{
    "ID": r["id"],
    "Opportunity": r["title"],
    "Organization": r["organization"],
    "Fit (%)": r["evaluation"]["match_score"],
    "Salary fit": r["evaluation"]["salary_ok"],
    "Location fit": r["evaluation"]["location_ok"],
    "Stage": r["stage"],
} for r in records]

st.subheader("Opportunity pipeline")
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

st.subheader("Human-reviewed workflow")
selected = st.selectbox("Opportunity", [r["id"] for r in records])
current = state["records"][selected]
st.write(f"Current stage: **{current['stage']}**")
next_steps = sorted(ALLOWED[current["stage"]])
if next_steps:
    destination = st.selectbox("Next stage", next_steps)
    reviewer = st.text_input("Human reviewer (required for approval)") if destination == "approved" else None
    confirmation = st.text_input("External confirmation reference (required for submission)") if destination == "submitted" else None
    if st.button("Save transition"):
        try:
            store.transition(selected, destination, approved_by=reviewer, confirmation=confirmation)
            st.success("Transition saved to checkpoint")
            st.rerun()
        except (ValueError, KeyError) as exc:
            st.error(str(exc))
else:
    st.info("This record is in a terminal state.")

st.subheader("Recent workflow events")
if state["events"]:
    st.dataframe(pd.DataFrame(state["events"][-15:]), hide_index=True, use_container_width=True)
else:
    st.info("No transitions recorded yet.")
st.caption(f"Checkpoint: {STATE_PATH}. This demo never submits external applications.")
