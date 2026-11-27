# Agentic Opportunity Intelligence

An extensible Python prototype for **opportunity matching and human-reviewed workflow orchestration**. It demonstrates reusable discovery, screening, checkpointing and approval patterns with entirely fictional opportunities.

> **v0.1.0**: Local runnable prototype. Matching is deterministic, not LLM-powered. No scraping, account access, or automatic applications.

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

## Architecture

See [Architecture and trust boundaries](docs/architecture.md).

## Roadmap

Authorized discovery feed adapters; optional LLM reasoning; optional Gmail and Google Sheets integration; richer analytics and multi-user state.

## Privacy and licensing

All demo organizations and records are fictional. Do not commit credentials, personal applications, resumes, confidential employer data or screenshots of private dashboards. Licensed under the [MIT License](LICENSE).
