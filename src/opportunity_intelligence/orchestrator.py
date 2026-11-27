"""Deterministic, resumable orchestration; never performs external actions."""
from pathlib import Path
import json
from .demo import seed


def run_workflow(data_dir, state_file):
    store = seed(data_dir, state_file)
    records = store.load()['records']
    ranked = sorted(records.values(), key=lambda r: (-r['evaluation']['match_score'], r['id']))
    prepared = 0
    for r in ranked:
        if not r['evaluation']['qualified'] or r['stage'] not in ('discovered', 'qualified'):
            continue
        if r['stage'] == 'discovered':
            store.transition(r['id'], 'qualified')
        e = r['evaluation']
        brief = f"# {r['title']} — {r['organization']}\n\nSynthetic opportunity brief\n\nSkill coverage: {e['match_score']}%\n\nMatched skills: {', '.join(e['matched'])}\n\nSkill gaps: {', '.join(e['missing']) or 'None'}\n\nHuman review required. No external action taken."
        state = store.load()
        state['records'][r['id']]['brief'] = brief
        store.save(state)
        store.transition(r['id'], 'prepared')
        prepared += 1
    return prepared
