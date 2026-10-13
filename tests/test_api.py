import pytest
from fastapi.testclient import TestClient
from hugin.app import create_app


@pytest.fixture
def client(workspace):
    settings, store, dex, _, _ = workspace
    app = create_app(settings, store, dex, start_worker=False)
    with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 12345)) as client:
        yield client


def test_api_selection_and_job(client):
    assert client.get('/api/health').json()['mode'] == 'fixture'
    ambiguous = client.post('/api/enrichments', json={'query': 'Jamie Vale'})
    assert ambiguous.status_code == 409
    assert len(ambiguous.json()['detail']['candidates']) == 2
    response = client.post('/api/enrichments', json={'dex_contact_id': 'fixture-alex'})
    assert response.status_code == 202
    job_id = response.json()['job']['id']
    engine = client.app.state.engine
    engine.process(client.app.state.store.claim('api-worker'))
    job = client.get('/api/enrichments/' + job_id).json()
    assert job['state'] == 'completed'
    assert client.get('/api/evidence', params={'job_id': job_id}).json()['items']
    assert client.get('/api/connections', params={'job_id': job_id}).json()['items']
    integrations = client.get('/api/integrations').json()
    assert integrations['dex']['status'] == 'fixture'
    assert 'dex_key' not in integrations['dex'] and 'api_key' not in integrations['dex']


def test_origin_host_and_json_guards(client):
    assert client.post('/api/enrichments', json={'dex_contact_id': 'fixture-alex'}, headers={'Origin': 'https://evil.example'}).status_code == 403
    assert client.get('/api/health', headers={'Host': 'evil.example'}).status_code == 400
    assert client.post('/api/enrichments', content='{}', headers={'Content-Type': 'text/plain'}).status_code == 415


def test_remote_access_denied(workspace):
    settings, store, dex, _, _ = workspace
    app = create_app(settings, store, dex, start_worker=False)
    with TestClient(app, base_url='http://127.0.0.1', client=('203.0.113.10', 1000)) as remote:
        assert remote.get('/api/contacts').status_code == 403
