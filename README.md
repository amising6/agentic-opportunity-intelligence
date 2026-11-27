# Agentic Opportunity Intelligence

An extensible Python framework for **opportunity discovery, intelligent matching and human-reviewed workflow orchestration**.

The platform demonstrates reusable patterns for live discovery, screening, ranking, checkpointing, approval and governed workflow execution.

![Version](https://img.shields.io/badge/version-v1.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Live Applications

| Application | Launch |
|---|---|
| Agentic Opportunity Intelligence | [Launch Demo](https://de-copilot-opportunity-intelligence.streamlit.app) |
| Live Greenhouse Discovery | [Launch Demo](https://de-copilot-live-discovery.streamlit.app) |
| STTM Factory | [Launch Demo](https://de-copilot-sttm-factory.streamlit.app) |

The Opportunity Intelligence demo uses synthetic data.
The Live Discovery application retrieves public job
postings through Greenhouse and Lever APIs.

The public interactive demonstration uses synthetic opportunities. Live discovery capabilities are available through the Python backend.

## Latest Release  v1.1.0

**Greenhouse Integration  Live Opportunity Discovery**

This release introduces live opportunity discovery through the Greenhouse public Job Board API, with additional Lever integration.

[View v1.1.0 Release](https://github.com/amising6/agentic-opportunity-intelligence/releases/tag/v1.1.0)

## Features

### Live Opportunity Discovery

- Greenhouse and Lever public API integration.
- Configurable registry of 13 company career sources.
- Parallel retrieval of publicly available opportunities.
- Job description and skill extraction.
- Keyword normalization and location-based filtering.
- Opportunity deduplication.
- Source-level execution reporting and error handling.

### Opportunity Intelligence

- Explainable skill-coverage scoring.
- Salary and location screening.
- Standardized opportunity data model.
- Automated opportunity ranking.
- Deduplicated ingestion keyed by opportunity identifier.

### Governed Workflow Orchestration

- Explicit human approval gates.
- Evidence requirements for workflow transitions.
- Persistent JSON checkpoints.
- Execution history and audit events.
- Automated opportunity brief preparation.

### Interactive Dashboard

- Opportunity overview and pipeline visualization.
- Workflow review and approval.
- Execution history.
- Downloadable opportunity data and generated briefs.
- Synthetic demonstration environment.

## Architecture

Public Job Board APIs → Source Adapters → Parallel Discovery Engine → Opportunity Filtering → Standardized Opportunity Model

The standardized opportunity model provides the foundation for screening, ranking and governed workflow orchestration.

See [Architecture and trust boundaries](docs/architecture.md).

## Ubuntu Quick Start

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

Open the local URL printed by Streamlit, usually http://localhost:8501.

## Live Discovery  Python Example

```python
from opportunity_intelligence.discovery import (
    load_sources,
    discover,
)

sources = load_sources("config/job_sources.json")

jobs, reports = discover(
    sources,
    keyword="data engineer",
    location="New York",
)

for job in jobs:
    print(job.organization)
    print(job.title)
    print(job.location)
    print(job.source_url)

print(reports)
```

The source registry can be configured through:

```text
config/job_sources.json
```

Public job availability depends on the respective career portals.

## Workflow

```text
Discovered
    ↓
Qualified
    ↓
Prepared
    ↓
Human Approval
    ↓
Externally Confirmed Submission
```

Records can also become blocked or rejected.

Approval requires a reviewer identifier. Submission requires an externally obtained confirmation reference.

The application records this reference; it does not independently validate it or submit applications automatically
