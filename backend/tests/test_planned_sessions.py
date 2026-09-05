import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func, select
from app import models as m
from app.database import SessionLocal
from app.exporter import teacher_tex, support_tex
from app.sessions import Durations

B = '/api/session-planning'


def ok(response, status=201):
    assert response.status_code == status, response.text
    return response.json()


def context(client, label='4e A', year='2026-2027'):
    return ok(client.post(B + '/contexts', json={'class_label': label, 'school_year': year}))


def plan(client, c=None):
    c = c or context(client)
    return ok(client.post(B + '/plans', json={'class_context_id': c['id'], 'sequence_id': 1, 'planned_sequence_minutes': 330}))


def data(number=1, **changes):
    return dict(title='Séance test', expected_session_number=number, instruction_ids=[3, 4, 6], durations={'slot_minutes': 120, 'break_minutes': 10}, **changes)


def create(client, p, number=1, **changes):
    return ok(client.post(f"{B}/plans/{p['id']}/sessions", json=data(number, **changes)))


def finalize(client, sheet):
    return ok(client.post(f"/api/sheets/{sheet['id']}/finalize"), 200)


def execute(client, sheet, statuses):
    return ok(client.post(f"{B}/sessions/{sheet['planned_session']['id']}/executions", json={
        'teacher_revision_id': sheet['id'], 'taught_on': '2026-09-04',
        'results': [{'segment_id': s['id'], 'status': status, 'actual_minutes': minutes} for s, (status, minutes) in zip(sheet['segments'], statuses)]}))


def coverage(client, p):
    return {r['instruction_id']: r for r in client.get(f"{B}/contexts/{p['class_context_id']}/coverage?sequence_id=1").json()['instructions']}


def test_T01_two_sessions_and_revision(client):
    p = plan(client); first = create(client, p); second = create(client, p, 2)
    revised = ok(client.post(f"/api/sheets/{first['id']}/new-revision"))
    assert first['sheet_id'] != second['sheet_id']
    assert revised['planned_session'] == first['planned_session']
    assert client.get(f"{B}/plans/{p['id']}").json()['next_session_number'] == 3


def test_T02_concurrent_creation_is_atomic(client):
    p = plan(client)
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(m.TeacherSessionSheet))
    with ThreadPoolExecutor(2) as pool:
        responses = list(pool.map(lambda _: client.post(f"{B}/plans/{p['id']}/sessions", json=data()), range(2)))
    assert sorted(r.status_code for r in responses) == [201, 409]
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(m.PlannedSession)) == 1
        assert db.scalar(select(func.count()).select_from(m.TeacherSessionSheet)) == before + 1


def test_T03_isolate_class_and_year(client):
    p = plan(client); s = finalize(client, create(client, p)); execute(client, s, [('COVERED', 17)])
    for c in [context(client, '4e B'), context(client, '4e A', '2027-2028')]:
        assert coverage(client, plan(client, c))[3]['status'] == 'NOT_STARTED'
    assert coverage(client, p)[3]['status'] == 'COVERED'


def test_T04_skipped_only(client):
    p = plan(client); s = finalize(client, create(client, p))
    assert coverage(client, p)[3]['status'] == 'NOT_STARTED'
    execute(client, s, [('SKIPPED', 0)])
    assert coverage(client, p)[3]['status'] == 'SKIPPED'


def test_T05_explicit_covered_only(client):
    p = plan(client); s = finalize(client, create(client, p))
    for status in ['PARTIAL', 'PARTIAL', 'COVERED']:
        execute(client, s, [(status, 40)])
        assert coverage(client, p)[3]['status'] == status


def test_T06_preserve_progress_after_skipped_and_reactivation(client):
    p = plan(client); s = finalize(client, create(client, p))
    execute(client, s, [('PARTIAL', 11)]); execute(client, s, [('SKIPPED', 0)])
    row = coverage(client, p)[3]
    assert (row['status'], row['last_result'], row['previously_skipped']) == ('PARTIAL', 'SKIPPED', True)
    execute(client, s, [('COVERED', 5)])
    create(client, p, 2, reactivate_instruction_ids=[3])
    execute(client, s, [('PARTIAL', 2)])
    assert coverage(client, p)[3]['status'] == 'COVERED'


def test_T07_recommendation_priority_and_covered_opt_in(client):
    p = plan(client); s = finalize(client, create(client, p)); execute(client, s, [('COVERED', 10), ('PARTIAL', 20), ('SKIPPED', 0)])
    rows = client.get(f"{B}/plans/{p['id']}/recommendation").json()
    assert rows[0]['instruction_id'] == 4
    assert not next(r for r in rows if r['instruction_id'] == 3)['eligible']
    assert next(r for r in rows if r['instruction_id'] == 6)['previously_skipped']
    rows = client.get(f"{B}/plans/{p['id']}/recommendation?include_covered=true").json()
    assert all(r['eligible'] for r in rows)


def test_T08_temporary_deferral_visible_and_reproposed(client):
    p = plan(client); payload = data(); payload.update(instruction_ids=[3, 4], deferred_instruction_ids=[6])
    s = ok(client.post(f"{B}/plans/{p['id']}/sessions", json=payload))
    assert s['authoring']['session_preparation']['deferred_instruction_ids'] == [6]
    assert next(r for r in client.get(f"{B}/plans/{p['id']}/recommendation").json() if r['instruction_id'] == 6)['eligible']
    assert any(i['instruction_id'] == 6 for i in create(client, p, 2)['segments'])


def test_T09_distinct_results_and_minutes(client):
    p = plan(client); s = finalize(client, create(client, p)); execute(client, s, [('PARTIAL', 13), ('COVERED', 22), ('SKIPPED', 0)])
    rows = coverage(client, p)
    assert [(rows[i]['status'], rows[i]['actual_minutes']) for i in [3, 4, 6]] == [('PARTIAL', 13), ('COVERED', 22), ('SKIPPED', 0)]


@pytest.mark.parametrize('slot,pause,pedagogy', [(119, 0, 119), (120, 10, 110), (130, 10, 120)])
def test_T10_duration_snapshot(slot, pause, pedagogy):
    assert Durations(slot_minutes=slot, break_minutes=pause).snapshot()['pedagogical_minutes'] == pedagogy


@pytest.mark.parametrize('slot,pause', [(0, 0), (120, -1), (120, 120), (120, 121), (120.5, 10), (120, 1.5), ('1 h 30', 0), (True, 0)])
def test_T11_invalid_durations(slot, pause):
    with pytest.raises(ValueError):
        Durations(slot_minutes=slot, break_minutes=pause)


def test_T12_snapshot_frozen_after_profile_and_plan_change(client):
    p = plan(client); s = finalize(client, create(client, p)); before = teacher_tex(s)
    ok(client.put(f"{B}/plans/{p['id']}/duration", json={'class_context_id': p['class_context_id'], 'sequence_id': 1, 'planned_sequence_minutes': 600}), 200)
    payload = data(2); payload['durations'] = {'slot_minutes': 120, 'break_minutes': 15, 'default_break_minutes': 15}
    newer = ok(client.post(f"{B}/plans/{p['id']}/sessions", json=payload))
    assert newer['authoring']['session_preparation']['durations']['pedagogical_minutes'] == 105
    assert teacher_tex(client.get(f"/api/sheets/{s['id']}").json()) == before
    updated_context = ok(client.put(f"{B}/contexts/{p['class_context_id']}/timetable", json={'class_label': '4e A', 'school_year': '2026-2027', 'teacher_actual_weekly_minutes': 280}), 200)
    assert updated_context['teacher_actual_weekly_minutes'] == 280
    assert client.get(f"/api/sheets/{s['id']}").json()['authoring']['session_preparation']['teacher_actual_weekly_minutes'] is None


def test_T14_historical_raw_results_not_coverage(client):
    s = ok(client.post('/api/authoring/compose', json={'programme_id': 1, 'scope': 'SEQUENCE', 'scope_id': 1, 'title': 'Historique', 'instruction_ids': [3]}))
    s = finalize(client, s)
    for status in ['DONE', 'PARTIAL', 'SKIPPED']:
        ok(client.post('/api/teaching-sessions', json={'teacher_revision_id': s['id'], 'class_label': '4e A', 'taught_on': '2026-09-04', 'actual_minutes': 12, 'status': status}))
    row = next(r for r in client.get('/api/progress').json()['instructions'] if r['instruction_id'] == 3)
    assert row['status'] == 'UNCONTEXTUALIZED'
    assert [r['status'] for r in row['raw_results']] == ['DONE', 'PARTIAL', 'SKIPPED']
    assert coverage(client, plan(client))[3]['status'] == 'NOT_STARTED'


def test_T15_export_correct_duration_and_fixed_metadata(client):
    p = plan(client); s = create(client, p); tex = teacher_tex(s)
    assert '110 min' in tex and '330 min' in tex and '120 min' in tex and '10 min' in tex
    assert 'Durée curriculaire SA' in tex
    assert '56 h / 60 h (conflit de sources conservé)' in tex
    metadata = {'identification': {**s['identification'], 'durée de la séance': '130'}, 'planning': s['planning']}
    assert client.put(f"/api/sheets/{s['id']}/metadata", json=metadata).status_code == 422


def test_T16_link_and_business_guards(client):
    assert client.post(B + '/contexts', json={'class_level': '6e', 'class_label': '6e A', 'school_year': '2026-2027'}).status_code == 422
    p = plan(client); a = create(client, p); b = finalize(client, create(client, p, 2))
    payload = {'teacher_revision_id': a['id'], 'taught_on': '2026-09-04', 'results': [{'segment_id': b['segments'][0]['id'], 'status': 'COVERED', 'actual_minutes': 2}]}
    assert client.post(f"{B}/sessions/{a['planned_session']['id']}/executions", json=payload).status_code == 409
    a = finalize(client, a)
    assert client.post(f"{B}/sessions/{a['planned_session']['id']}/executions", json=payload).status_code == 422
    payload['teacher_revision_id'] = b['id']
    assert client.post(f"{B}/sessions/{a['planned_session']['id']}/executions", json=payload).status_code == 409
    assert client.post('/api/teaching-sessions', json={'teacher_revision_id': a['id'], 'class_label': '4e A', 'taught_on': '2026-09-04'}).status_code == 422
    assert client.get(f"{B}/contexts/{p['class_context_id']}/coverage").json()['curriculum_weekly_mass']['minutes'] == 360


def test_T17_preserve_authoring_and_learner_content(client):
    p = plan(client); s = create(client, p, automatic=True)
    assert s['status'] == 'DRAFT' and s['authoring']['provenance'] and s['authoring']['selections']
    support = ok(client.post(f"/api/authoring/sheets/{s['id']}/learner-support"))
    assert all(b['block_type'] not in ['EXPECTED_RESPONSE', 'RESPONSE_SPACE'] for r in support['resources'] for b in r['blocks'])
    assert 'vspace{3cm}' not in support_tex(support)
    duplicate = ok(client.post(f"/api/sheets/{s['id']}/duplicate"))
    assert duplicate['planned_session'] is None and 'session_preparation' not in duplicate['authoring']


def test_T18_prepared_export_not_executed(client):
    p = plan(client); s = create(client, p); teacher_tex(s)
    ok(client.post('/api/exports', json={'document_family': 'TEACHER', 'revision_id': s['id']}))
    assert all(r['status'] == 'NOT_STARTED' for r in coverage(client, p).values())
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(m.TeachingSession).where(m.TeachingSession.planned_session_id.is_not(None))) == 0


def test_T19_finalized_without_execution(client):
    p = plan(client); finalize(client, create(client, p))
    assert all(r['status'] == 'NOT_STARTED' for r in coverage(client, p).values())


def test_T20_three_prepared_in_advance(client):
    p = plan(client)
    assert [create(client, p, n)['planned_session']['number'] for n in [1, 2, 3]] == [1, 2, 3]
    assert all(r['status'] == 'NOT_STARTED' for r in coverage(client, p).values())


def test_T21_divergence_preserves_future_and_finalized(client):
    p = plan(client); first = finalize(client, create(client, p)); future = create(client, p, 2)
    execute(client, first, [('COVERED', 15), ('PARTIAL', 10), ('SKIPPED', 0)])
    assert [coverage(client, p)[i]['status'] for i in [3, 4, 6]] == ['COVERED', 'PARTIAL', 'SKIPPED']
    assert client.get(f"/api/sheets/{first['id']}").json() == first
    assert client.get(f"/api/sheets/{future['id']}").json() == future


def test_T22_recommendation_readonly_explicit_draft_adaptation(client):
    p = plan(client); first = finalize(client, create(client, p)); future = finalize(client, create(client, p, 2, automatic=True))
    execute(client, first, [('COVERED', 15), ('PARTIAL', 10), ('SKIPPED', 0)])
    rows = client.get(f"{B}/plans/{p['id']}/recommendation").json()
    assert next(r for r in rows if r['instruction_id'] == 4)['planned_in_sessions'] == [2]
    assert client.get(f"/api/sheets/{future['id']}").json() == future
    payload = {'instruction_ids': [4, 6], 'deferred_instruction_ids': [3], 'durations': {'slot_minutes': 130, 'break_minutes': 10}}
    assert client.put(f"{B}/revisions/{future['id']}/preparation", json=payload).status_code == 409
    revised = ok(client.post(f"/api/sheets/{future['id']}/new-revision"))
    updated = ok(client.put(f"{B}/revisions/{revised['id']}/preparation", json=payload), 200)
    assert [s['instruction_id'] for s in updated['segments']] == [4, 6]
    assert updated['planned_session']['number'] == 2
    assert client.get(f"/api/sheets/{future['id']}").json() == future


def test_context_normalization_and_uniqueness(client):
    context(client, ' 4ème   a ', '2026/2027')
    assert client.post(B + '/contexts', json={'class_label': '4e A', 'school_year': '2026-2027'}).status_code == 409
