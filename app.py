"""Local opportunity intelligence dashboard with fictional demo records."""
from pathlib import Path
import os
import pandas as pd
import streamlit as st
from opportunity_intelligence.orchestrator import run_workflow
from opportunity_intelligence.demo import seed

st.set_page_config(page_title='Opportunity Intelligence', layout='wide')
ROOT = Path(__file__).resolve().parent
# Isolate public demo workspaces by browser session.
if os.environ.get("PUBLIC_DEMO", "true").lower() == "true":
    import tempfile

    if "workspace_directory" not in st.session_state:
        st.session_state["workspace_directory"] = tempfile.TemporaryDirectory(
            prefix="opportunity-demo-"
        )

    checkpoint = Path(
        st.session_state["workspace_directory"].name
    ) / "demo_state.json"
else:
    checkpoint = Path(os.environ.get(
        "OPPORTUNITY_STATE",
        str(ROOT / "data" / "demo_state.json")
    ))

store = seed(ROOT / 'sample_data', checkpoint)
state = store.load()
records = list(state['records'].values())
rows = pd.DataFrame([{'ID':r['id'],'Opportunity':r['title'],'Organization':r['organization'],'Location':r['location'],'Salary ceiling':r['salary_max'],'Fit (%)':r['evaluation']['match_score'],'Screening':'Eligible' if r['evaluation']['qualified'] else 'Not eligible','Stage':r['stage']} for r in records])
rows = rows.sort_values(['Fit (%)','ID'],ascending=[False,True])
st.title('Opportunity Intelligence')
st.caption('DEMONSTRATION ENVIRONMENT  /  Synthetic records  /  Human-reviewed workflow')
with st.sidebar:
    st.header('Workspace')
    page = st.radio('Navigation',['Overview','Opportunity pipeline','Workflow review','Audit history'])
    st.divider()
    st.caption('Local checkpoint storage. No external submissions.')
if page == 'Overview':
    metrics = [('Tracked',len(rows)),('Screening eligible',int((rows.Screening=='Eligible').sum())),('Qualified stage',int((rows.Stage=='qualified').sum())),('Awaiting approval',int((rows.Stage=='prepared').sum())),('Approved',int((rows.Stage=='approved').sum())),('Recorded submissions',int((rows.Stage=='submitted').sum())),('Blocked',int((rows.Stage=='blocked').sum())),('Rejected',int((rows.Stage=='rejected').sum()))]
    for start in (0,4):
        for col,(label,value) in zip(st.columns(4),metrics[start:start+4]):
            col.metric(label,value,border=True)
    a,b=st.columns(2)
    with a:
        st.subheader('Workflow stages');st.bar_chart(rows.Stage.value_counts())
    with b:
        st.subheader('Screening outcomes');st.bar_chart(rows.Screening.value_counts())
    if st.button('Run Intelligence Workflow', type='primary'):
        count = run_workflow(ROOT / 'sample_data', store.path)
        st.session_state['run_result'] = f'{count} opportunities prepared for human review.'
        st.rerun()
    if 'run_result' in st.session_state: st.success(st.session_state['run_result'])
    st.subheader('Top ranked opportunities');st.dataframe(rows.head(10),hide_index=True,use_container_width=True)
    if st.button('Advance eligible discovered records to qualified'):
        for r in records:
            if r['stage']=='discovered' and r['evaluation']['qualified']:
                store.transition(r['id'],'qualified')
        st.rerun()
elif page == 'Opportunity pipeline':
    st.subheader('Search and filter')
    a,b,c=st.columns(3)
    query=a.text_input('Search title or organization')
    stages=b.multiselect('Stage',sorted(rows.Stage.unique()))
    screening=c.selectbox('Screening',['All','Eligible','Not eligible'])
    minimum=st.slider('Minimum skill coverage (%)',0,100,0)
    filtered=rows[rows['Fit (%)']>=minimum]
    if query: filtered=filtered[filtered.Opportunity.str.contains(query,case=False,regex=False)|filtered.Organization.str.contains(query,case=False,regex=False)]
    if stages: filtered=filtered[filtered.Stage.isin(stages)]
    if screening!='All': filtered=filtered[filtered.Screening==screening]
    st.caption(f'{len(filtered)} of {len(rows)} records')
    st.dataframe(filtered,hide_index=True,use_container_width=True)
    st.download_button('Export filtered CSV',filtered.to_csv(index=False),'opportunities.csv','text/csv')
elif page == 'Workflow review':
    selected=st.selectbox('Opportunity',list(rows.ID),format_func=lambda key:f"{key} — {state['records'][key]['title']}")
    record=state['records'][selected];evaluation=record['evaluation']
    st.write('Current stage:',record['stage']);st.write('Matched skills:',', '.join(evaluation['matched']) or 'None');st.write('Missing skills:',', '.join(evaluation['missing']) or 'None')
    st.write('Salary constraint:', evaluation['salary_ok']); st.write('Location constraint:', evaluation['location_ok'])
    if record.get('brief'):
        st.markdown(record['brief']); st.download_button('Download opportunity brief', record['brief'], selected + '.md')
    options=sorted(store.options(record), key=lambda x: (x in ('blocked','rejected'), x))
    if not evaluation['qualified']: options=[x for x in options if x not in ('qualified','prepared','approved')]
    if options:
        destination=st.selectbox('Next stage',options)
        reviewer=st.text_input('Reviewer identifier') if destination=='approved' else None
        confirmation=st.text_input('Demo external confirmation reference') if destination=='submitted' else None
        reason=st.text_input('Reason') if destination in ('blocked','rejected') else None
        if st.button('Save transition'):
            try:
                store.transition(selected,destination,approved_by=reviewer,confirmation=confirmation,reason=reason);st.rerun()
            except (ValueError,KeyError) as exc: st.error(str(exc))
    else: st.info('No available transitions.')
else:
    st.subheader('Workflow audit history')
    if state['events']:
        events=pd.DataFrame(state['events']);st.dataframe(events.iloc[::-1],hide_index=True,use_container_width=True);st.download_button('Export audit CSV',events.to_csv(index=False),'audit.csv','text/csv')
    else: st.info('No transitions recorded yet.')
