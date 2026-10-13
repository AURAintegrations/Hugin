"""Actual pinned offline API Anything worker with synthetic provider responses."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import pytest
from hugin.api_anything import ApiAnythingSource, normalize
from hugin.config import ConnectorError
from hugin.models import EnrichRequest
from hugin.sources import Budget
from tests.conftest import run

AUTHOR = {'id': 'https://openalex.org/A123', 'display_name': 'Alex River', 'orcid': 'https://orcid.org/0000-0000-0000-0000', 'last_known_institutions': [{'display_name': 'Example Robotics'}]}
PAPER = {'id': '123', 'source': 'MED', 'title': 'Synthetic warehouse safety study', 'firstPublicationDate': '2026-09-02', 'doi': '10.1234/fixture-study', 'authorList': {'author': [{'firstName': 'Alex', 'lastName': 'River', 'authorAffiliationDetailsList': {'authorAffiliation': [{'affiliation': 'Example Robotics'}]}}]}}
NEWS = {'title': 'Example Robotics announces a synthetic distributor program', 'url': 'https://example.org/news', 'objectID': '1234', 'created_at': '2026-09-03T01:00:00Z', 'author': 'unrelated_poster'}


def responses():
    return {'openalex': {'results': [deepcopy(AUTHOR)], 'meta': {'cost_usd': 0.001}},
            'europepmc': {'resultList': {'result': [deepcopy(PAPER)]}}, 'industry_news': {'hits': [deepcopy(NEWS)]}}


def collector(workspace):
    settings, store, dex, engine, _ = workspace
    if not Path(settings.api_anything_dir, 'dist/http.js').is_file():
        pytest.skip('Run scripts/install-api-anything.sh for real pinned worker verification')
    return engine.api_anything, dex.contact('fixture-alex')


def test_actual_worker_query_encoding_extraction_and_cache(workspace):
    source, contact = collector(workspace)
    budget = Budget(3, 30, 0)
    query = 'Alex & River "test"'
    url = source.worker('build', 'openalex', budget, args={'query': query})['url']
    from urllib.parse import parse_qs, urlparse
    assert parse_qs(urlparse(url).query)['search'] == [query]
    rows, details = source.collect('openalex', contact, budget, responses())
    assert rows[0]['identity']['confidence'] == 'medium' and rows[0]['provider_review_status'] == 'pending'
    assert details['records_returned'] == 1 and details['operation_hash']
    assert details['provider_reported_query_cost_usd'] == 0.001
    requests = budget.requests
    assert source.collect('openalex', contact, budget, responses())[1]['cache_hit']
    assert budget.requests == requests
    _, publication = source.collect('europepmc', contact, Budget(1, 30, 0), responses())
    assert parse_qs(urlparse(publication['url']).query)['query'] == ['AUTH:"River A"']
    assert workspace[1].rows('api_metadata')[0]['records'][0]['excerpt']


def test_pipeline_note_citations_preservation_and_idempotency(workspace):
    collector(workspace)
    _, store, dex, engine, fixture = workspace
    fixture['api_anything'] = responses()
    before = dex.contact('fixture-alex')
    request = EnrichRequest(dex_contact_id='fixture-alex', sources=['api_anything'], idempotency_key='api-fixture-save')
    job = run(engine, store, request)
    assert job['state'] == 'completed' and job['sync']['note_verified']
    assert {f['kind'] for f in job['findings']} == {'professional_profile', 'publication', 'company_context'}
    assert all(f['status'] == 'unresolved' for f in job['findings'])
    assert not job['proposals'] and not job['relationships'] and dex.contact('fixture-alex') == before
    assert job['costs']['requests'] == 3 and job['costs']['paid_attempts'] == 0
    for finding in job['findings']:
        evidence = next(e for e in job['evidence'] if e['id'] == finding['evidence_ids'][0])
        assert evidence['operation'] and evidence['api_anything_revision'] and evidence['url'] in job['note']
    assert '2026-09-02' in job['note'] and 'FIXTURE / SIMULATED' in job['note']
    again, created = engine.submit(request)
    assert not created and again['id'] == job['id'] and len(store.rows('fixture_notes')) == 1
    assert engine.retry_sync(job['id'])['id'] == job['id']
    assert len(store.rows('fixture_notes')) == 1


def test_wrong_person_name_only_and_fuzzy_news_do_not_become_facts():
    contact = {'name': 'Alex River', 'company': 'Example Robotics'}
    author = {**AUTHOR, 'display_name': 'Alex Stone'}
    assert normalize('openalex', contact, [author], 'https://api.openalex.org/authors')[0]['identity']['confidence'] == 'rejected'
    rows = normalize('openalex', contact, [{**AUTHOR, 'last_known_institutions': []}], 'https://api.openalex.org/authors')
    assert rows[0]['identity']['confidence'] == 'low' and rows[0]['provider_review_status'] == 'pending'
    assert normalize('industry_news', contact, [{**NEWS, 'title': 'Example of robotics research'}], 'https://hn.algolia.com/api/v1/search') == []
    assert normalize('industry_news', {'company': 'EZUP'}, [{**NEWS, 'title': 'BigEZUPPER news'}], 'https://hn.algolia.com/api/v1/search') == []
    wrong_paper = {**PAPER, 'authorList': {'author': [{'firstName': 'Alex', 'lastName': 'Stone'}]}}
    assert normalize('europepmc', contact, [wrong_paper], 'https://www.ebi.ac.uk/europepmc/webservices/rest/search') == []
    initial_only = {**PAPER, 'authorList': {'author': [{'firstName': 'A', 'lastName': 'River'}]}}
    assert normalize('europepmc', contact, [initial_only], 'https://www.ebi.ac.uk/europepmc/webservices/rest/search') == []
    accent = normalize('openalex', {'name': 'Alex Rivera'}, [{**AUTHOR, 'display_name': 'Álex Rivera'}], 'https://api.openalex.org/authors')
    assert accent[0]['identity']['confidence'] == 'low' and accent[0]['provider_review_status'] == 'pending'


def test_source_failure_isolation_budget_empty_and_pending_fields(workspace):
    collector(workspace)
    _, store, _, engine, fixture = workspace
    fixture['api_anything'] = responses()
    fixture['api_anything']['openalex'] = {'error': 'quota_exhausted'}
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['api_anything']))
    assert job['state'] == 'completed' and len(job['findings']) == 2
    assert next(o for o in job['outcomes'] if o['source']=='api_anything:openalex')['outcome'] == 'quota_exhausted'
    # A second contact/run has no matching name and no company: zero notes added.
    fixture['api_anything'] = {'openalex': {'results': []}, 'europepmc': {'resultList': {'result': []}}, 'industry_news': {'hits': []}}
    empty = run(engine, store, EnrichRequest(dex_contact_id='fixture-jamie-one', sources=['api_anything']))
    assert empty['state'] == 'no_results' and len(store.rows('fixture_notes')) == 1
    limited = run(engine, store, EnrichRequest(dex_contact_id='fixture-jamie-two', sources=['api_anything'], max_requests=1))
    assert limited['costs']['requests'] == 1 and any(o['outcome']=='quota_exhausted' for o in limited['outcomes'])


def test_robots_and_redirect_access_do_not_run_extraction(workspace, monkeypatch):
    source, contact = collector(workspace)
    calls = []
    monkeypatch.setattr(source.public, 'validate_url', lambda *a: None)
    def get(url, budget, *a, **kw):
        budget.take(); calls.append(url)
        assert url.endswith('/robots.txt')
        return url, 'User-agent: *\nDisallow: /authors'
    monkeypatch.setattr(source.public, 'get', get)
    with pytest.raises(ConnectorError, match='robots'): source.collect('openalex', contact, Budget(4, 30, 0))
    assert len(calls) == 1 and not workspace[1].rows('api_metadata')


def test_missing_worker_and_schema_drift_are_explicit(workspace):
    source, contact = collector(workspace)
    with pytest.raises(ConnectorError): source.collect('openalex', contact, Budget(1, 30, 0), {'openalex': {'changed_schema': []}})
    assert not workspace[1].rows('source_cache')
    workspace[0].api_anything_dir = '/nonexistent/api-anything'
    assert source.status()['status'] == 'unsupported'
    with pytest.raises(ConnectorError, match='not installed'): source.collect('openalex', contact, Budget(1, 30, 0), responses())


def test_resume_source_checkpoint_does_not_repeat_completed_operation(workspace, monkeypatch):
    collector(workspace)
    _, store, _, engine, fixture = workspace
    fixture['api_anything'] = responses()
    initial, _ = engine.submit(EnrichRequest(dex_contact_id='fixture-alex', sources=['api_anything'], dry_run=True))
    job = store.claim('interrupted')
    original = engine.outcome
    def interrupt(job, source, *args, **kw):
        original(job, source, *args, **kw)
        if source == 'api_anything:openalex': raise RuntimeError('synthetic interruption after durable checkpoint')
    monkeypatch.setattr(engine, 'outcome', interrupt)
    with pytest.raises(RuntimeError): engine.collect(job)
    resumed = store.get('jobs', initial['id'])
    monkeypatch.setattr(engine, 'outcome', original)
    calls = []
    collect = engine.api_anything.collect
    def count(source, *args, **kw): calls.append(source); return collect(source, *args, **kw)
    monkeypatch.setattr(engine.api_anything, 'collect', count)
    engine.collect(resumed); engine.normalize(resumed)
    assert calls == ['europepmc','industry_news'] and resumed['costs']['requests'] == 3
    assert len(resumed['findings']) == 3


def test_worker_rejects_unreviewed_source_and_receives_no_secrets(workspace, monkeypatch):
    source, _ = collector(workspace)
    original = subprocess.run
    observed = []
    def guarded(*args, **kwargs):
        observed.append(kwargs['env']); return original(*args, **kwargs)
    monkeypatch.setattr(subprocess, 'run', guarded)
    monkeypatch.setenv('DEX_API_KEY', 'synthetic-secret-do-not-pass')
    with pytest.raises(ConnectorError): source.worker('build', 'unreviewed', Budget(1,30,0), args={'query':'Alex River'})
    assert observed == [{'PATH': observed[0]['PATH']}]


@pytest.mark.parametrize('after_write', [False, True])
def test_sync_retry_does_not_repeat_api_research(workspace, monkeypatch, after_write):
    collector(workspace)
    _, store, dex, engine, fixture = workspace
    fixture['api_anything'] = responses()
    dex.fail_write = not after_write
    dex.fail_after_write = after_write
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['api_anything']))
    assert job['state'] == 'sync_failed'
    costs = job['costs'].copy()
    dex.fail_write = dex.fail_after_write = False
    def forbidden(*args, **kwargs): raise AssertionError('Sync must never rerun API collection')
    monkeypatch.setattr(engine.api_anything, 'collect', forbidden)
    engine.retry_sync(job['id'])
    engine.process(store.claim('sync-recovery'))
    recovered = store.get('jobs', job['id'])
    assert recovered['state'] == 'completed' and recovered['sync']['note_verified']
    assert recovered['costs'] == costs and len(store.rows('fixture_notes')) == 1
