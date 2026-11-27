# Agentic Opportunity Intelligence

An extensible Python prototype for **opportunity matching and human-reviewed workflow orchestration**. It demonstrates reusable discovery, screening, checkpointing and approval patterns with entirely fictional opportunities.

> **v1.0.0**: Local runnable prototype with automated screening, ranking and brief preparation. Matching is deterministic, not LLM-powered. No scraping, account access, or automatic applications.

## Features

- Explainable skill-coverage scoring and salary/location screening
- Deduplicated ingestion keyed by opportunity identifier
- Explicit approval and evidence gates for workflow transitions
- Persistent JSON checkpoints and event history
- Interactive Streamlit dashboard
- Synthetic demo inputs, tests and GitHub Actions continuous integration

## Ubuntu quick start

```bash
git clone https://github.com/amising6/agentic-opportunity-intelligence.git
cd agentic-opportunity-intelligence
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest -q
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501). The first run creates `data/demo_state.json`. Stop the app and delete that file to reset the demo.

## Workflow

`discovered → qualified → prepared → approved → submitted`

Records can also become `blocked` or `rejected`. Approval requires a reviewer identifier. Submission requires an externally obtained confirmation reference. The application **records** that reference; it does not independently validate it or send an application.
## Live Opportunity Discovery  v1.1.0

Agentic Opportunity Intelligence now supports live job discovery through the Greenhouse public Job Board API, with additional Lever integration.

### Capabilities

- Configurable registry of 13 company career sources.
- Parallel retrieval of publicly available opportunities.
- Job description and skill extraction.
- Keyword normalization and location-based filtering.
- Opportunity deduplication.
- Source-level execution reporting and error handling.
- Standardized opportunity data model.

### Architecture

Public Job Board APIs → Source Adapters → Parallel Discovery Engine → Opportunity Filtering → Standardized Opportunity Model

### Privacy and Governance

The integration retrieves publicly available job postings without requiring personal credentials or automated access to restricted platforms.

The public Streamlit demonstration continues to use synthetic data. Live discovery is currently available through the Python backend.

### Release

[View v1.1.0 — Greenhouse Integration](https://github.com/amising6/agentic-opportunity-intelligence/releases/tag/v1.1.0)
## Architecture

See [Architecture and trust boundaries](docs/architecture.md).

## Roadmap

Authorized discovery feed adapters; optional LLM reasoning; optional Gmail and Google Sheets integration; richer analytics and multi-user state.

## Privacy and licensing

All demo organizations and records are fictional. Do not commit credentials, personal applications, resumes, confidential employer data or screenshots of private dashboards. Licensed under the [MIT License](LICENSE).

## Automated demonstration

Select **Run Intelligence Workflow** on Overview. Eligible discovered records advance through qualification and preparation in skill-coverage order. Download the generated Markdown brief in Workflow review. The workflow stops before human approval; submission is a manually recorded simulation. Re-running skips completed stages. JSON storage is single-process, and reviewer identifiers are not authenticated. No LLM or live discovery is included in this release.
