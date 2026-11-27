from pathlib import Path
from opportunity_intelligence.demo import seed


def test_demo_is_idempotent(tmp_path):
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / 'state.json'
    store = seed(root / 'sample_data', path)
    assert len(store.load()['records']) == 50
    store.transition('demo-001', 'qualified')
    assert seed(root / 'sample_data', path).load()['records']['demo-001']['stage'] == 'qualified'
