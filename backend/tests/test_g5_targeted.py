import json

import pytest
from test_resource_library import package_bytes, rewrite_package


FILES = [('resources.jsonl', 'content'), ('resource_instruction_links.jsonl', 'instruction_code'), ('sources.jsonl', 'title')]


def post(client, raw, route):
    return client.post('/api/admin/resource-packages/' + route,
                       headers={'X-Package-Import-Key': 'test-package-key'},
                       files={'package': ('g5.zip', raw, 'application/zip')})


def rejected(client, raw, file, line, code=None, field=None):
    dry = post(client, raw, 'dry-run')
    assert dry.status_code == 200
    report = dry.json()
    assert report['can_import'] is False
    matches = [e for e in report['validation_errors'] if e['file'] == file and
               (code is None or e['code'] == code) and (field is None or e['field'] == field)]
    assert matches
    assert all(e['line'] == line for e in matches), matches
    assert all(set(e) == {'code', 'file', 'line', 'field', 'message'} for e in report['validation_errors'])
    imported = post(client, raw, 'import')
    assert imported.status_code == 422
    assert imported.json()['detail']['validation_errors'] == report['validation_errors']


@pytest.mark.parametrize('status', ['ABSENT', 'VERIFIED_SOURCE', 'CURATED', 'VALIDATED', 'USER_UNREVIEWED', 'REJECTED', 'ARCHIVED', 'UNKNOWN', 'validated', '', None, 123, True, [], {}])
def test_g5_link_status_routes(client, status):
    def change(files):
        row = json.loads(files['resource_instruction_links.jsonl'])
        if status == 'ABSENT':
            row.pop('validation_status')
        else:
            row['validation_status'] = status
        files['resource_instruction_links.jsonl'] = json.dumps(row).encode()
    raw = rewrite_package(package_bytes(), change)
    if isinstance(status, str) and status in {'ABSENT', 'VERIFIED_SOURCE', 'CURATED', 'VALIDATED', 'USER_UNREVIEWED', 'REJECTED', 'ARCHIVED'}:
        dry = post(client, raw, 'dry-run')
        assert dry.status_code == 200 and dry.json()['can_import'] is True
        assert post(client, raw, 'import').status_code == 200
        from app.database import SessionLocal
        from app import models as m
        from sqlalchemy import select
        with SessionLocal() as db:
            link = db.scalar(select(m.ResourceInstructionMapping).join(m.PedagogicalResourceVersion).join(m.PedagogicalResource).where(m.PedagogicalResource.code == 'PKG-P3-001'))
            assert link.validation_status == ('CURATED' if status == 'ABSENT' else status)
    else:
        rejected(client, raw, 'resource_instruction_links.jsonl', 1, 'INVALID_ENUM', 'validation_status')


@pytest.mark.parametrize('file,field', FILES)
@pytest.mark.parametrize('ending', ['\n', '\r\n', '\r'])
@pytest.mark.parametrize('prefix,expected,syntax', [(['valid'], 2, False), (['valid', ''], 3, False), (['', ''], 3, False), (['valid', ' \t ', 'valid'], 4, False), (['', 'valid', ' \t ', ''], 5, True)])
def test_g5_physical_lines_routes(client, tmp_path, file, field, ending, prefix, expected, syntax):
    def change(files):
        good = files[file].decode()
        bad = json.loads(good)
        bad[field] = {}
        lines = [good if item == 'valid' else item for item in prefix]
        lines.append('{' if syntax else json.dumps(bad))
        path = tmp_path / file
        path.write_bytes(ending.join(lines).encode())
        files[file] = path.read_bytes()
    raw = rewrite_package(package_bytes(), change)
    rejected(client, raw, file, expected, 'JSONL_INVALID' if syntax else 'INVALID_FIELD_TYPE')


@pytest.mark.parametrize('file,field', FILES)
@pytest.mark.parametrize('stage', ['unicode', 'utf8', 'semantic', 'multiple'])
def test_g5_line_survives_validation_stages(client, file, field, stage):
    semantic_fields = {'resources.jsonl': ('class_level', '5e', 'CLASS_LEVEL_UNSUPPORTED'),
                       'sources.jsonl': ('sha256', 'a' * 64, 'SOURCE_CONFLICT'),
                       'resource_instruction_links.jsonl': ('relation_type', 'UNKNOWN', 'LINK_INVALID')}
    if stage == 'semantic' and file == 'sources.jsonl':
        assert post(client, package_bytes(), 'import').status_code == 200
    def change(files):
        row = json.loads(files[file])
        if stage == 'unicode':
            row['provenance' if file == 'resource_instruction_links.jsonl' else 'title'] = {'text': '\ud800'} if file == 'resource_instruction_links.jsonl' else '\ud800'
        elif stage == 'semantic':
            key, value, _ = semantic_fields[file]
            row[key] = value
            if file == 'sources.jsonl': row['title'] = 'Different source'
        else:
            row[field] = {}
            row['extra_invalid'] = True
        files[file] = b'\n \t\n' + (b'\xff' if stage == 'utf8' else json.dumps(row).encode())
    raw = rewrite_package(package_bytes(), change)
    code = {'unicode': 'INVALID_UNICODE', 'utf8': 'UTF8_INVALID', 'semantic': semantic_fields[file][2], 'multiple': None}[stage]
    rejected(client, raw, file, 3, code)
