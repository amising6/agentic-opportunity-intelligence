"""Deterministic screening and human-reviewed opportunity workflow."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import tempfile

ALLOWED = {
    "discovered": {"qualified", "rejected", "blocked"},
    "qualified": {"prepared", "rejected", "blocked"},
    "prepared": {"approved", "rejected", "blocked"},
    "approved": {"submitted", "blocked"},
    "blocked": {"discovered", "qualified", "prepared", "approved", "rejected"},
    "submitted": set(),
    "rejected": set(),
}

@dataclass(frozen=True)
class Candidate:
    skills: tuple[str, ...]
    min_salary: int = 0
    locations: tuple[str, ...] = ()

@dataclass(frozen=True)
class Opportunity:
    id: str
    title: str
    organization: str
    required_skills: tuple[str, ...]
    salary_max: int | None = None
    location: str = "remote"
    source_url: str = ""

def normalized_skills(skills: tuple[str, ...]) -> set[str]:
    return {skill.strip().casefold() for skill in skills if skill.strip()}

def match(candidate: Candidate, opportunity: Opportunity) -> dict[str, Any]:
    """Explainable required-skill coverage, not predicted hiring probability."""
    required = normalized_skills(opportunity.required_skills)
    supplied = normalized_skills(candidate.skills)
    matched = sorted(required & supplied)
    missing = sorted(required - supplied)
    score = round(100 * len(matched) / len(required), 1) if required else 0.0
    salary_ok = opportunity.salary_max is None or opportunity.salary_max >= candidate.min_salary
    location_ok = not candidate.locations or opportunity.location.casefold() in {
        location.casefold() for location in candidate.locations
    }
    return {
        "id": opportunity.id,
        "match_score": score,
        "matched": matched,
        "missing": missing,
        "salary_ok": salary_ok,
        "location_ok": location_ok,
        "qualified": score >= 60 and salary_ok and location_ok,
    }

class WorkflowStore:
    """Atomic JSON checkpoint store for a single local process."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"records": {}, "events": []}
        with self.path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, state: dict[str, Any]) -> None:
        fd, temporary = tempfile.mkstemp(prefix=".checkpoint-", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def ingest(self, opportunity: Opportunity, evaluation: dict[str, Any]) -> bool:
        state = self.load()
        if opportunity.id in state["records"]:
            return False
        state["records"][opportunity.id] = {
            **asdict(opportunity),
            "evaluation": evaluation,
            "stage": "discovered",
            "confirmation": None,
        }
        self.save(state)
        return True

    @staticmethod
    def options(record):
        if record['stage'] == 'blocked':
            return {record.get('blocked_from', 'discovered'), 'rejected'}
        return ALLOWED[record['stage']]

    def transition(self, opportunity_id: str, new_stage: str, *,
                   approved_by: str | None = None,
                   confirmation: str | None = None, reason: str | None = None) -> None:
        state = self.load()
        record = state["records"].get(opportunity_id)
        if record is None:
            raise KeyError(f"Unknown opportunity: {opportunity_id}")
        prior = record["stage"]
        if new_stage not in self.options(record):
            raise ValueError(f"Invalid workflow transition: {prior} -> {new_stage}")
        if new_stage == "qualified" and not record["evaluation"].get("qualified", False):
            raise ValueError("Screening constraints not met")
        if new_stage == "approved" and not (approved_by or "").strip():
            raise ValueError("An identified human reviewer is required for approval")
        if new_stage == "submitted" and not (confirmation or "").strip():
            raise ValueError("An externally obtained confirmation reference is required")
        if new_stage == "blocked":
            record["blocked_from"] = prior
        record["stage"] = new_stage
        if confirmation:
            record["confirmation"] = confirmation
        state["events"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "opportunity_id": opportunity_id,
            "from": prior,
            "to": new_stage,
            "approved_by": approved_by,
            "confirmation": confirmation,
            "reason": reason,
        })
        self.save(state)
