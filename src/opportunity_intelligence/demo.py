"""Create fictional demo records without overwriting existing state."""
from pathlib import Path
import json
from .core import Candidate, Opportunity, WorkflowStore, match

def seed(data_dir: str | Path, state_file: str | Path) -> WorkflowStore:
    data_dir = Path(data_dir)
    candidate_data = json.loads((data_dir / "candidate.json").read_text(encoding="utf-8"))
    candidate = Candidate(
        skills=tuple(candidate_data["skills"]),
        min_salary=candidate_data["min_salary"],
        locations=tuple(candidate_data["locations"]),
    )
    opportunities = json.loads((data_dir / "opportunities.json").read_text(encoding="utf-8"))
    store = WorkflowStore(state_file)
    for item in opportunities:
        opportunity = Opportunity(**{**item, "required_skills": tuple(item["required_skills"])})
        store.ingest(opportunity, match(candidate, opportunity))
    return store
