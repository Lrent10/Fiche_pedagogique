import json
import pytest
from sqlalchemy import select
from app import models as m
from app.database import SessionLocal
from app.exporter import support_tex, teacher_tex


def payload(**changes):
    return dict(programme_id=1, scope="SEQUENCE", scope_id=1, title="Produits remarquables", instruction_ids=[3, 4, 6], **changes)


def compose(client, automatic=False):
    response = client.post('/api/authoring/compose', json=payload(automatic=automatic))
    assert response.status_code == 201, response.text
    return response.json()


def resource(client, **changes):
    data = dict(title="Formulation personnelle", level="4e", instruction_ids=[3], source_kind="TEACHER_COMMUNITY", source_ref="Fiche de l’auteur", source_version="1", validation_status="COMMUNITY", blocks=[dict(block_type="PROPERTY", title="Propriété", content_latex="$(a+b)^2=a^2+2ab+b^2$.")])
    data.update(changes)
    result = client.post('/api/authoring/resources', json=data)
    assert result.status_code == 201, result.text
    return result.json()


def test_CURR_001_002_003_class_sa_sequence_order(client):
    tree = client.get('/api/authoring/curriculum').json()
    assert tree[0]['level'] == '4e'
    assert tree[0]['situations'][0]['code'] == 'SA1'
    sequence = tree[0]['situations'][0]['sequences'][0]
    assert sequence['title'] == 'Calculs sur les expressions algébriques'
    assert [i['position'] for i in sequence['instructions']] == list(range(1, 8))


def test_CURR_004_005_inherited_attributes_have_real_scope_and_source(client):
    preview = client.post('/api/authoring/preview', json=payload()).json()
    attrs = preview['attributes']
    assert len([a for a in attrs if a['scope'] == 'SA']) == 3
    assert all(a['source_version'] and a['page_label'] for a in attrs)
    with SessionLocal() as db:
        assert len(list(db.scalars(select(m.CurriculumAttribute).where(m.CurriculumAttribute.scope == 'SA')))) == 3


def test_AUTO_001_002_003_and_TEACHER_002_003(client):
    sheet = compose(client)
    assert sheet['identification']['SA'] == 'SA1'
    assert 'Factorisation' in sheet['planning']['contenus de formation']
    assert sheet['authoring']['provenance']['identification.établissement']['origin'] == 'MANUAL_USER_ENTRY'
    assert sheet['authoring']['duration_conflict']
    assert 'durée curriculaire SA' not in sheet['identification']
    tex = teacher_tex(sheet)
    assert 'Configurations du plan' in tex
    assert 'Factorisation' in tex


def test_AUTO_override_requires_explicit_consent_and_loses_official_origin(client):
    sheet = compose(client)
    sheet['identification']['titre SA'] = 'Titre personnel'
    data = {'identification': sheet['identification'], 'planning': sheet['planning']}
    assert client.put(f"/api/sheets/{sheet['id']}/metadata", json=data).status_code == 422
    data['override_fields'] = ['identification.titre SA']
    updated = client.put(f"/api/sheets/{sheet['id']}/metadata", json=data).json()
    assert updated['authoring']['provenance']['identification.titre SA']['origin'] == 'USER_OVERRIDE'


def test_AUTO_deleting_curricular_value_requires_override(client):
    sheet = compose(client)
    del sheet['planning']['compétences disciplinaires']
    data = {'identification': sheet['identification'], 'planning': sheet['planning']}
    assert client.put(f"/api/sheets/{sheet['id']}/metadata", json=data).status_code == 422


def test_AUTO_reused_local_profile_keeps_its_origin(client):
    data = payload(local={'établissement': 'Établissement personnel'}, reused_local_fields=['établissement'])
    sheet = client.post('/api/authoring/compose', json=data).json()
    assert sheet['authoring']['provenance']['identification.établissement']['origin'] == 'REUSED_TEACHER_DATA'
    assert sheet['identification']['établissement'] == 'Établissement personnel'


def test_RES_001_002_003_004_005_and_TRACE_001_002(client):
    r = resource(client, instruction_ids=[3, 4], validation_status='INSPECTOR_VALIDATED', validation_ref='PV inspection 2026-01', author='Enseignant pilote')
    for i in [3, 4]:
        rows = client.get(f'/api/authoring/instructions/{i}/candidates').json()
        assert len(rows) > 1
        row = next(x for x in rows if x['id'] == r['id'])
        assert row['provenance']['source_kind'] == 'TEACHER_COMMUNITY'
        assert row['provenance']['validation_status'] == 'INSPECTOR_VALIDATED'
        assert row['provenance']['source_version'] == '1'
        assert row['instruction_ids'] == [3, 4]


@pytest.mark.parametrize('kind', ['DEFINITION', 'PROPERTY', 'FORMULA', 'METHOD', 'FIGURE'])
def test_FORM_001_002_typed_formulations(client, kind):
    r = resource(client, blocks=[dict(block_type=kind, title=kind, content_latex='Contenu test')])
    rows = client.get('/api/authoring/instructions/3/candidates').json()
    assert next(x for x in rows if x['id'] == r['id'])['blocks'][0]['block_type'] == kind


def test_RAND_001_incompatible_and_demo_excluded(client):
    r = resource(client, source_kind='DEMO_UNSOURCED', validation_status='NON_REVU')
    assert r['id'] not in [x['id'] for x in client.get('/api/authoring/instructions/3/candidates').json()]
    assert r['id'] in [x['id'] for x in client.get('/api/authoring/instructions/3/candidates?allow_demo=true').json()]
    with SessionLocal() as db:
        version = db.get(m.PedagogicalResourceVersion, r['id'])
        db.get(m.PedagogicalResource, version.resource_id).level = '3e'
        db.commit()
    assert r['id'] not in [x['id'] for x in client.get('/api/authoring/instructions/3/candidates?allow_demo=true').json()]


def test_RAND_002_official_priority(client):
    resource(client)
    result = compose(client, automatic=True)
    assert all(s['provenance']['source_kind'] == 'OFFICIAL_GUIDE' for s in result['authoring']['selections'].values())


def test_RAND_003_inspector_priority_without_official(client):
    community = resource(client, instruction_ids=[1])
    inspector = resource(client, instruction_ids=[1], validation_status='INSPECTOR_VALIDATED', validation_ref='PV-1')
    data = payload(automatic=True)
    data['instruction_ids'] = [1]
    result = client.post('/api/authoring/compose', json=data).json()
    assert result['authoring']['selections']['1']['resource_version_id'] == inspector['id'] != community['id']


def test_RAND_004_COMP_001_002_003_seed_draft_and_trace(client):
    resource(client, instruction_ids=[1])
    resource(client, instruction_ids=[1])
    data = payload(automatic=True, seed=1234)
    data['instruction_ids'] = [1]
    a = client.post('/api/authoring/compose', json=data).json()
    b = client.post('/api/authoring/compose', json=data).json()
    assert a['status'] == b['status'] == 'DRAFT'
    assert a['authoring']['selections']['1']['resource_version_id'] == b['authoring']['selections']['1']['resource_version_id']
    assert a['authoring']['selections']['1']['origin'] == 'AUTO_SELECTED'
    assert all(not f['expected_result_latex'] for f in a['flow'])


def test_COMP_missing_candidate_rolls_back(client):
    before = len(client.get('/api/sheets').json())
    data = payload(automatic=True)
    data['instruction_ids'] = [1]
    assert client.post('/api/authoring/compose', json=data).status_code == 422
    assert len(client.get('/api/sheets').json()) == before


def test_COMP_class_is_navigation_not_giant_sheet(client):
    data = payload()
    data['scope'] = 'CLASS'
    assert client.post('/api/authoring/compose', json=data).status_code == 422
    assert client.post('/api/authoring/preview', json=data).status_code == 200


def test_manual_replacement_keeps_history_and_edits(client):
    sheet = compose(client, True)
    r = resource(client)
    first = sheet['authoring']['selections']['3']
    replaced = client.put(f"/api/authoring/sheets/{sheet['id']}/selection", json={'instruction_id': 3, 'resource_version_id': r['id']}).json()
    assert replaced['authoring']['selection_history'][0] == first
    assert replaced['authoring']['selections']['3']['resource_version_id'] == r['id']
    assert any(x['id'] == first['instance_id'] for x in replaced['resources'])


@pytest.mark.parametrize('target', ['LEARNER_INITIAL', 'LEARNER_COMPLETED'])
def test_LEARNER_001_002_003_004_005(target):
    types = ['INSTRUCTION', 'DEFINITION', 'PROPERTY', 'FIGURE', 'EXPECTED_RESPONSE', 'RESPONSE_SPACE']
    blocks = [dict(id=i, block_type=k, title=k, content_latex='SECRETANSWER' if k == 'EXPECTED_RESPONSE' else ('MASSIVEGAP' if k == 'RESPONSE_SPACE' else 'VISIBLE'+k), visible=True) for i, k in enumerate(types)]
    tex = support_tex(dict(title='Support', sequence=None, situation=None, resources=[dict(title='Activité', blocks=blocks)]), target)
    assert 'SECRETANSWER' not in tex and 'MASSIVEGAP' not in tex
    for kind in ['INSTRUCTION', 'DEFINITION', 'PROPERTY', 'FIGURE']:
        assert 'VISIBLE'+kind in tex


def test_TEACHER_001_learner_copy_excludes_expected_and_preserves_figure(client):
    sheet = compose(client, True)
    flow = sheet['flow'][0]
    sheet = client.put(f"/api/sheets/{sheet['id']}/flow/{flow['id']}", json={'expected_result_latex': 'REPONSEPROF'}).json()
    assert 'REPONSEPROF' in teacher_tex(sheet)
    result = client.post(f"/api/authoring/sheets/{sheet['id']}/learner-support")
    assert result.status_code == 201
    assert 'REPONSEPROF' not in support_tex(result.json())


def test_IMMUT_001_finalized_authoring_and_new_revision(client):
    sheet = compose(client, True)
    assert client.post(f"/api/sheets/{sheet['id']}/finalize").status_code == 200
    r = resource(client)
    assert client.put(f"/api/authoring/sheets/{sheet['id']}/selection", json={'instruction_id': 3, 'resource_version_id': r['id']}).status_code == 409
    with SessionLocal() as db:
        revision = db.get(m.TeacherSheetRevision, sheet['id'])
        revision.authoring_json = '{}'
        with pytest.raises(ValueError):
            db.commit()
        db.rollback()
    revised = client.post(f"/api/sheets/{sheet['id']}/new-revision").json()
    assert revised['status'] == 'DRAFT'
    ids = {x['id'] for x in revised['resources']}
    assert all(x['instance_id'] in ids for x in revised['authoring']['selections'].values())


def test_TRACE_community_cannot_be_official(client):
    response = client.post('/api/authoring/resources', json=dict(title='Test', level='4e', instruction_ids=[3], source_kind='TEACHER_COMMUNITY', source_ref='Auteur', source_version='1', validation_status='OFFICIAL', blocks=[dict(block_type='PROPERTY', title='P', content_latex='x')]))
    assert response.status_code == 422


def test_scope_rejects_outside_instruction(client):
    data = payload()
    data['instruction_ids'] = [999]
    assert client.post('/api/authoring/compose', json=data).status_code == 422


def test_LEARNER_legacy_response_suffix_removed_without_mutating_source():
    content = r"Calculer $2+2$.\par\medskip\textbf{Réponse :}\par\vspace{16cm}"
    detail = dict(title='Support', sequence=None, situation=None, resources=[dict(title='Consigne', blocks=[dict(title='Consigne', block_type='INSTRUCTION', content_latex=content, visible=True)])])
    rendered = support_tex(detail)
    assert '16cm' not in rendered and 'Réponse :' not in rendered
    assert detail['resources'][0]['blocks'][0]['content_latex'] == content
