"""Real isolated upstream parser on synthetic HTML; never a LinkedIn live test."""
from pathlib import Path
import json
import subprocess
import time
import pytest
from fastapi.testclient import TestClient
from hugin.app import create_app
from hugin.config import ConnectorError
from hugin.linkedin import inspect_html, profile_url, session_cookies
from hugin.models import EnrichRequest
from hugin.sources import Budget
from tests.conftest import run

DOCUMENT = (Path(__file__).parent / 'fixtures/linkedin-profile.html').read_text()
URL = 'https://www.linkedin.com/in/fixture-alex-river/'


@pytest.mark.parametrize('value', ['http://linkedin.com/in/person', 'https://evil.example/?next=linkedin.com/in/person', 'https://www.linkedin.com@evil.example/in/person', 'https://www.linkedin.com/in/person?x=1', 'https://www.linkedin.com:444/in/person', 'https://www.linkedin.com/in/person/details/experience', 'https://www.linkedin.com/in/person#x'])
def test_reject_invalid_url(value):
    with pytest.raises(ConnectorError):
        profile_url(value)


def test_canonical_and_dashes_and_no_executable_markup():
    assert profile_url('fixture-alex-river') == URL
    assert profile_url(URL.rstrip('/')) == URL
    clean = inspect_html(DOCUMENT, URL)
    assert '<script' not in clean and '<img' not in clean and 'onerror' not in clean
    assert 'Jan 2020 - Present' in clean and '2010 - 2014' in clean
    with pytest.raises(ConnectorError, match='canonical'):
        inspect_html(DOCUMENT.replace('in/fixture-alex-river/', 'in/wrong-person/'), URL)


@pytest.mark.parametrize('document,outcome', [('<iframe title="CAPTCHA"></iframe>', 'unsupported'), ('<div id="authwall">Sign in</div>', 'unsupported'), ('<body>Too many requests</body>', 'quota_exhausted'), ('<form action="/login">Sign in</form>', 'authentication_required'), ('', 'no_result')])
def test_challenges_and_empty(document, outcome):
    with pytest.raises(ConnectorError) as caught:
        inspect_html(document, URL)
    assert caught.value.outcome == outcome


def test_session_permissions_expiry_and_scoping(tmp_path):
    path = tmp_path / 'synthetic-session.json'
    # Dummy cookies only; not credentials and never used for network operations.
    data = {'cookies': [{'name': 'li_at', 'value': 'synthetic-invalid-cookie', 'domain': '.linkedin.com', 'secure': True, 'expires': time.time() + 300}, {'name': 'other', 'value': 'synthetic', 'domain': 'evil.example', 'secure': True, 'expires': -1}]}
    path.write_text(json.dumps(data)); path.chmod(0o644)
    with pytest.raises(ConnectorError, match='owner-only'):
        session_cookies(str(path))
    path.chmod(0o600)
    assert len(session_cookies(str(path))) == 1
    data['cookies'][0]['expires'] = 0
    path.write_text(json.dumps(data))
    with pytest.raises(ConnectorError) as caught:
        session_cookies(str(path))
    assert caught.value.outcome == 'authentication_required'
    link = tmp_path / 'symlink'; link.symlink_to(path)
    with pytest.raises(ConnectorError):
        session_cookies(str(link))


def test_actual_parser_evidence_writeback_cache_and_idempotency(workspace, monkeypatch):
    settings, store, dex, engine, fixture = workspace
    assert Path(settings.linkedin_python).is_file(), 'Run scripts/install-linkedin.sh for this integration test'
    before = dex.contact('fixture-alex')
    request = EnrichRequest(dex_contact_id='fixture-alex', sources=['linkedin'], linkedin_html=DOCUMENT, idempotency_key='linkedin-fixture-one')
    job = run(engine, store, request)
    assert job['state'] == 'completed' and job['sync']['note_verified']
    assert job['sync']['fixture'] and job['costs']['paid_attempts'] == 0
    assert job['costs']['requests'] == 0, 'Offline parser consumes no network units'
    kinds = {row['kind'] for row in job['findings']}
    assert {'biography', 'professional_headline', 'employment_history', 'education', 'company', 'job_title'} <= kinds
    assert {'email', 'phone', 'relationship'}.isdisjoint(kinds)
    assert all(row['provider_review_status'] == 'pending' for row in job['findings'])
    assert all(row['url'] == URL and row['evidence_origin'] == 'user_supplied_html' for row in job['evidence'])
    assert 'Jan 2020 | Present' in job['note'] and 'Example College' in job['note']
    assert job['outcomes'][-1]['coverage']['experiences'] == 'parsed'
    assert store.get('source_inputs', job['id']) is None
    assert 'linkedin_html' not in job['options'] and DOCUMENT not in json.dumps(job)
    assert dex.contact('fixture-alex') == before
    again, created = engine.submit(request)
    assert not created and again['id'] == job['id']
    assert len(store.rows('fixture_notes')) == 1
    monkeypatch.setattr('hugin.linkedin.run_worker', lambda *a, **k: pytest.fail('Cache should avoid another parser run'))
    rows, cached, coverage, stamp = engine.linkedin.page(job['contact'], Budget(1, 15, 0), inspect_html(DOCUMENT, URL))
    assert cached and rows and coverage['contacts'] == 'not_searched'


def test_wrong_person_rejected_and_empty_no_write(workspace):
    _, store, _, engine, _ = workspace
    wrong = DOCUMENT.replace('Alex River', 'Different Person')
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['linkedin'], linkedin_html=wrong))
    assert job['state'] == 'no_results' and not job['findings']
    assert job['evidence'][0]['review_status'] == 'rejected'
    assert next(o for o in job['outcomes'] if o['source'] == 'linkedin')['outcome'] == 'ambiguous_identity'
    assert not store.rows('fixture_notes')


def test_restart_input_and_sync_only_retry(workspace, monkeypatch):
    settings, store, dex, engine, fixture = workspace
    from hugin.engine import Engine
    from hugin.sources import PublicSources
    request = EnrichRequest(dex_contact_id='fixture-alex', sources=['linkedin'], linkedin_html=DOCUMENT)
    job, _ = engine.submit(request)
    assert store.get('source_inputs', job['id'])
    restarted = Engine(settings, store, dex, PublicSources(settings, store), fixture)
    original = dex.create_note
    monkeypatch.setattr(dex, 'create_note', lambda *a: (_ for _ in ()).throw(ConnectorError('unavailable', 'Synthetic write failure')))
    restarted.process(store.claim('restart-worker'))
    failed = store.get('jobs', job['id'])
    assert failed['state'] == 'sync_failed' and failed['research_complete']
    assert not store.get('source_inputs', job['id'])
    monkeypatch.setattr(dex, 'create_note', original)
    monkeypatch.setattr(restarted.linkedin, 'page', lambda *a: pytest.fail('Sync retry must not collect'))
    restarted.retry_sync(job['id']); restarted.process(store.claim('sync-worker'))
    completed = store.get('jobs', job['id'])
    assert completed['state'] == 'completed' and completed['sync']['note_verified']


def test_no_session_isolated_optional_failure(workspace):
    _, store, _, engine, _ = workspace
    engine.fixture = None  # Other sources omitted; no live network without a session.
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['linkedin']))
    assert job['state'] == 'no_results' and job['costs']['requests'] == 0
    assert next(o for o in job['outcomes'] if o['source'] == 'linkedin')['outcome'] == 'authentication_required'


def test_robots_block_before_authenticated_get(workspace, monkeypatch):
    _, _, _, engine, _ = workspace
    monkeypatch.setattr('hugin.linkedin.session_cookies', lambda p: [])
    monkeypatch.setattr(engine.public, 'validate_url', lambda *a: None)
    monkeypatch.setattr(engine.public, 'get', lambda *a: (URL, 'User-agent: *\nDisallow: /in/'))
    monkeypatch.setattr('requests.Session', lambda: pytest.fail('Denied profiles must not be fetched'))
    with pytest.raises(ConnectorError, match='robots'):
        engine.linkedin.acquire(URL, Budget(3, 15, 0))


def test_budget_and_parser_failure(workspace, monkeypatch):
    _, _, _, engine, _ = workspace
    budget = Budget(1, 15, 0); budget.deadline = 0
    with pytest.raises(ConnectorError) as caught:
        engine.linkedin.page({'name': 'Alex River', 'linkedin': URL}, budget, DOCUMENT)
    assert caught.value.outcome == 'timeout'
    monkeypatch.setattr('hugin.linkedin.run_worker', lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired('private', 1)))
    with pytest.raises(ConnectorError) as caught:
        engine.linkedin.page({'name': 'Alex River', 'linkedin': URL}, Budget(1, 15, 0), DOCUMENT)
    assert caught.value.outcome == 'timeout' and 'private' not in caught.value.message


def test_worker_timeout_kills_browser_process_group(tmp_path):
    import os
    import sys
    from hugin.linkedin import run_worker
    script = tmp_path / 'synthetic-hanging-worker.py'
    child_file = tmp_path / 'child.pid'
    script.write_text('import subprocess,sys,time\nfrom pathlib import Path\n'
                      'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"])\n'
                      f'Path({str(child_file)!r}).write_text(str(child.pid))\n'
                      'time.sleep(60)\n')
    with pytest.raises(subprocess.TimeoutExpired):
        run_worker(sys.executable, script, {}, 0.5)
    child = int(child_file.read_text())
    status = Path(f'/proc/{child}/stat')
    if status.exists():
        assert status.read_text().split()[2] == 'Z', 'Timed-out child must be exited, never left running'


def test_api_import_never_echoes_html(workspace):
    settings, store, dex, _, _ = workspace
    app = create_app(settings, store, dex, start_worker=False)
    with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 1)) as client:
        invalid = client.post('/api/enrichments', json={'dex_contact_id': 'fixture-alex', 'sources': ['maigret'], 'linkedin_html': 'private-input-sentinel'})
        assert invalid.status_code == 422 and 'private-input-sentinel' not in invalid.text
        result = client.post('/api/enrichments', json={'dex_contact_id': 'fixture-alex', 'sources': ['linkedin'], 'linkedin_html': DOCUMENT})
        assert result.status_code == 202 and DOCUMENT not in result.text
        config = client.get('/api/integrations').json()['linkedin']
        assert config['status'] == 'fixture' and not config['live_verified']
