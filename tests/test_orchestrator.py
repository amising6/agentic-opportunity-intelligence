from pathlib import Path
import pytest
from opportunity_intelligence.orchestrator import run_workflow
from opportunity_intelligence.core import WorkflowStore


def test_workflow_stops_at_review(tmp_path):
    path = tmp_path / 'state.json'
    data = Path(__file__).resolve().parents[1] / 'sample_data'
    assert run_workflow(data, path) == 23
    store = WorkflowStore(path)
    records = store.load()['records']
    assert sum(r['stage'] == 'prepared' for r in records.values()) == 23
    assert all(r.get('brief') for r in records.values() if r['stage'] == 'prepared')
    assert run_workflow(data, path) == 0
    key = next(k for k,r in records.items() if r['stage'] == 'prepared')
    store.transition(key, 'blocked')
    with pytest.raises(ValueError):
        store.transition(key, 'approved', approved_by='reviewer')
    store.transition(key, 'prepared')
    store.transition(key, 'approved', approved_by='reviewer')
    store.transition(key, 'submitted', confirmation='DEMO')
    assert store.load()['events'][-1]['confirmation'] == 'DEMO'
