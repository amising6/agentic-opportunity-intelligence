import pytest
from opportunity_intelligence.core import Candidate, Opportunity, WorkflowStore, match

def test_scoring_and_constraints():
    candidate = Candidate(("Python", "SQL"), 150000, ("remote",))
    opportunity = Opportunity("one", "Demo", "Example", ("PYTHON", "AWS"), 160000)
    result = match(candidate, opportunity)
    assert result["match_score"] == 50.0
    assert result["missing"] == ["aws"]
    assert not result["qualified"]

def test_duplicate_and_checkpoint(tmp_path):
    store = WorkflowStore(tmp_path / "checkpoint.json")
    opportunity = Opportunity("one", "Demo", "Example", ("Python",))
    assert store.ingest(opportunity, {"qualified": True})
    assert not store.ingest(opportunity, {"qualified": True})
    assert len(WorkflowStore(tmp_path / "checkpoint.json").load()["records"]) == 1

def test_approval_and_submission_require_evidence(tmp_path):
    store = WorkflowStore(tmp_path / "state.json")
    store.ingest(Opportunity("one", "Demo", "Example", ()), {"qualified": True})
    store.transition("one", "qualified")
    store.transition("one", "prepared")
    with pytest.raises(ValueError, match="reviewer"):
        store.transition("one", "approved")
    store.transition("one", "approved", approved_by="demo-reviewer")
    with pytest.raises(ValueError, match="confirmation"):
        store.transition("one", "submitted")
    store.transition("one", "submitted", confirmation="DEMO-CONFIRMATION-001")
    assert store.load()["records"]["one"]["stage"] == "submitted"
    with pytest.raises(ValueError, match="Invalid"):
        store.transition("one", "qualified")
