from copy import deepcopy
import pytest
from hugin.config import ConnectorError
from hugin.engine import Engine, SelectionError
from hugin.models import EnrichRequest
from hugin.sources import PublicSources, identity, page_observations
from hugin.store import FixtureStore
from hugin.dex import FixtureDex
from tests.conftest import run


def request(**kwargs):
    return EnrichRequest(dex_contact_id='fixture-alex', **kwargs)


def test_one_invocation_cited_note_and_preservation(workspace):
    _, store, dex, engine, _ = workspace
    before = deepcopy(dex.contact('fixture-alex'))
    job = run(engine, store, request())
    assert job['state'] == 'completed'
    assert job['sync']['status'] == 'verified'
    assert job['sync']['fixture'] is True
    assert 'FIXTURE / SIMULATED RESEARCH' in job['note']
    assert job['editorial']['status'] == 'main_skill_reviewed'
    assert dex.contact('fixture-alex') == before
    assert len(store.rows('fixture_notes')) == 1
    assert job['findings'] and store.rows('evidence') and store.rows('source_outcomes')
    for finding in job['findings'] + job['relationships']:
        assert finding['evidence_ids']
        for key in finding['evidence_ids']:
            evidence = store.get('evidence', key)
            assert evidence['url'] in job['note']
            assert evidence['retrieved_at']
            assert evidence['excerpt']
    emails = [p for p in job['proposals'] if p['field'] == 'email']
    assert emails and all(p['status'] == 'pending' for p in emails)
    assert job['relationships'][0]['status'] == 'inferred'
    assert job['relationships'][0]['target_identity_confidence'] == 'unresolved'


def test_ambiguity_starts_nothing(workspace):
    _, store, _, engine, _ = workspace
    with pytest.raises(SelectionError) as error:
        engine.submit(EnrichRequest(query='Jamie Vale'))
    assert len(error.value.candidates) == 2
    assert not store.rows('jobs') and not store.rows('fixture_notes')


def test_wrong_person_and_name_only_rejected(workspace):
    _, store, dex, engine, fixture = workspace
    job = run(engine, store, request())
    assert any(e['review_status'] == 'rejected' for e in job['evidence'])
    assert 'Investor' not in job['note']
    assert identity(dex.contact('fixture-alex'), {'name': 'Alex River'}, 'https://example.net/alex')['confidence'] == 'low'
    wrong = page_observations(dex.contact('fixture-alex'), 'https://example.net/wrong-alex', fixture['pages']['https://example.net/wrong-alex'])
    assert all(o['identity']['confidence'] == 'rejected' for o in wrong)


def test_idempotency_and_parameter_conflict(workspace):
    _, store, _, engine, _ = workspace
    job = run(engine, store, request(idempotency_key='stable'))
    same, created = engine.submit(request(idempotency_key='stable'))
    assert same['id'] == job['id'] and not created
    assert not store.claim('next-worker')
    assert len(store.rows('fixture_notes')) == 1
    with pytest.raises(ConnectorError, match='different options'):
        engine.submit(request(idempotency_key='stable', dry_run=True))


def test_dry_run_never_writes(workspace):
    _, store, _, engine, _ = workspace
    job = run(engine, store, request(dry_run=True))
    assert job['state'] == 'dry_run' and not store.rows('fixture_notes')
    with pytest.raises(ConnectorError):
        engine.retry_sync(job['id'])


@pytest.mark.parametrize('after_write', [False, True])
def test_sync_retry_preserves_research_no_duplicate_or_paid_run(workspace, after_write):
    _, store, dex, engine, _ = workspace
    dex.fail_write = not after_write
    dex.fail_after_write = after_write
    job = run(engine, store, request(sources=['dex_fresh', 'public_pages'], write_policy='fill_missing', allow_fresh_dex=True, paid_budget_units=1))
    assert job['state'] == 'sync_failed'
    assert job['research_complete'] and dex.fresh_calls == 1
    evidence = deepcopy(job['evidence'])
    costs = deepcopy(job['costs'])
    dex.fail_write = dex.fail_after_write = False
    engine.retry_sync(job['id'])
    engine.process(store.claim('retry-worker'))
    result = store.get('jobs', job['id'])
    assert result['state'] == 'completed' and dex.fresh_calls == 1
    assert 'outcome' not in result['sync'] and 'message' not in result['sync']
    assert result['evidence'] == evidence and result['costs'] == costs
    assert len(store.rows('fixture_notes')) == 1
    engine.retry_sync(job['id'])
    assert not store.claim('again')


def test_restart_and_lease_recovery(workspace):
    settings, store, _, engine, fixture = workspace
    job, _ = engine.submit(request())
    running = store.claim('crashed-worker')
    engine.collect(running)
    engine.normalize(running)
    running['lease_until'] = 0
    store.update_job(running, 'crashed-worker')
    restored_store = FixtureStore(settings.fixture_store)
    restored_dex = FixtureDex(restored_store, fixture)
    restored = Engine(settings, restored_store, restored_dex, PublicSources(settings, restored_store), fixture)
    claimed = restored_store.claim('restored-worker')
    assert claimed['research_complete']
    restored.process(claimed)
    assert restored_store.get('jobs', job['id'])['state'] == 'completed'
    with pytest.raises(RuntimeError, match='ownership'):
        engine.save(running)


def test_empty_results_and_optional_failures(workspace):
    _, store, _, engine, fixture = workspace
    fixture['api_anything'] = {'openalex': {'results': []}, 'europepmc': {'resultList': {'result': []}}, 'industry_news': {'hits': []}}
    fixture['pages'] = {'https://example.org/team/alex': {'error': 'timeout'}}
    job = run(engine, store, request())
    assert job['state'] == 'no_results'
    assert job['sync']['status'] == 'not_attempted'
    assert not store.rows('fixture_notes')
    with pytest.raises(ConnectorError, match='no findings'):
        engine.retry_sync(job['id'])
    assert not job['findings']
    assert any(o['outcome'] == 'timeout' for o in job['outcomes'])
    assert any(o['source'] == 'brave' and o['outcome'] == 'not_searched' for o in job['outcomes'])
    assert 'No supported findings' in job['note']


def test_budget_and_paid_opt_in(workspace):
    _, store, _, engine, _ = workspace
    job = run(engine, store, request(max_requests=1, sources=['dex_cached', 'public_pages', 'brave']))
    assert job['costs']['requests'] == 1
    assert job['costs']['paid_attempts'] == 0
    assert any(o['outcome'] == 'quota_exhausted' for o in job['outcomes'])
    with pytest.raises(ValueError):
        request(sources=['dex_fresh'])
    with pytest.raises(ValueError):
        request(sources=['dex_fresh'], paid_budget_units=1, allow_fresh_dex=True, write_policy='notes_only')


def test_conflicts_retained_missing_fields_only(workspace):
    _, store, dex, engine, fixture = workspace
    contact = dex.contact('fixture-alex')
    contact['website'] = ''
    dex.store.put('fixture_contacts', contact['id'], contact)
    fixture['pages']['https://example.org/team/alex'] = fixture['pages']['https://example.org/team/alex'].replace('"jobTitle":"Founder"', '"jobTitle":"CEO"')
    job = run(engine, store, request(write_policy='fill_missing'))
    assert job['state'] == 'completed'
    assert dex.contact('fixture-alex')['website'] == 'https://example.org/team/alex'
    assert dex.contact('fixture-alex')['job_title'] == 'Founder'
    assert any(f['kind'] == 'job_title' and f['status'] == 'conflicting' for f in job['findings'])
    assert not job['sync']['additions']['related_contact_ids']


def test_conflicting_relationships_remain_in_store(workspace):
    _, store, _, engine, _ = workspace
    job, _ = engine.submit(request(dry_run=True))
    job = store.claim('test')
    engine.collect(job)
    relationship = next(o for o in job['observations'] if o['kind'] == 'relationship')
    contradictory = deepcopy(relationship)
    contradictory['relationship_type'] = 'unconfirmed_introduction'
    job['observations'].append(contradictory)
    engine.normalize(job)
    assert all(r['status'] == 'conflicting' for r in job['relationships'])
    assert len(store.rows('relationships')) == 2


def test_paid_request_restart_does_not_repeat(workspace):
    _, store, dex, engine, _ = workspace
    job, _ = engine.submit(request(sources=['dex_fresh'], write_policy='fill_missing', allow_fresh_dex=True, paid_budget_units=1))
    running = store.claim('crashed')
    running['fresh_requested'] = True
    running['costs']['paid_attempts'] = 1
    running['lease_until'] = 0
    store.update_job(running, 'crashed')
    engine.process(store.claim('restored'))
    result = store.get('jobs', job['id'])
    assert dex.fresh_calls == 0
    assert any(o['outcome'] == 'in_progress' for o in result['outcomes'])


def test_field_filled_between_research_and_sync_is_preserved(workspace):
    _, store, dex, engine, _ = workspace
    contact = dex.contact('fixture-alex')
    contact['website'] = ''
    store.put('fixture_contacts', contact['id'], contact)
    job, _ = engine.submit(request(write_policy='fill_missing'))
    running = store.claim('worker')
    engine.collect(running); engine.normalize(running)
    contact['website'] = 'https://example.org/user-selected-profile'
    store.put('fixture_contacts', contact['id'], contact)
    engine.sync(running)
    final = store.get('jobs', job['id'])
    assert dex.contact(contact['id'])['website'] == contact['website']
    assert final['sync']['additions']['fields'] == {}
    assert final['sync']['provider_or_external_changes']['website'] == contact['website']


def test_field_timeout_after_write_recovers_intent(workspace, monkeypatch):
    _, store, dex, engine, _ = workspace
    contact = dex.contact('fixture-alex'); contact['website'] = ''
    store.put('fixture_contacts', contact['id'], contact)
    original = dex.update_missing
    def write_then_timeout(contact_id, fields):
        original(contact_id, fields)
        raise ConnectorError('timeout', 'Synthetic timeout after missing-field write.')
    monkeypatch.setattr(dex, 'update_missing', write_then_timeout)
    job = run(engine, store, request(write_policy='fill_missing'))
    assert job['state'] == 'sync_failed' and job['sync']['field_intent']
    monkeypatch.setattr(dex, 'update_missing', original)
    engine.retry_sync(job['id']); engine.process(store.claim('recovery'))
    final = store.get('jobs', job['id'])
    assert final['state'] == 'completed'
    assert final['sync']['additions']['fields']['website'] == 'https://example.org/team/alex'
    assert any(p.get('sync_status') == 'applied_verified' for p in final['proposals'])
    assert len(store.rows('fixture_notes')) == 1


def test_wrong_contact_note_readback_never_marked_successful(workspace, monkeypatch):
    _, store, dex, engine, _ = workspace
    original = dex.get_note
    def wrong_contact(key):
        result = deepcopy(original(key)); result['contact_ids'] = ['other-contact']; return result
    monkeypatch.setattr(dex, 'get_note', wrong_contact)
    job = run(engine, store, request())
    assert job['state'] == 'sync_failed' and job['sync']['outcome'] == 'verification_failed'
    assert len(store.rows('fixture_notes')) == 1


def test_partial_research_restart_preserves_source_counts(workspace, monkeypatch):
    settings, store, dex, engine, fixture = workspace
    job, _ = engine.submit(request())
    running = store.claim('interrupted')
    original = engine.outcome
    class Crash(BaseException): pass
    def checkpoint_then_crash(job, source, status, message, **extra):
        original(job, source, status, message, **extra)
        if source.startswith('public_pages:') and status == 'ok':
            raise Crash()
    monkeypatch.setattr(engine, 'outcome', checkpoint_then_crash)
    with pytest.raises(Crash): engine.collect(running)
    saved = store.get('jobs', job['id']); saved['lease_until'] = 0
    store.update_job(saved, 'interrupted')
    restored = Engine(settings, store, dex, PublicSources(settings, store), fixture)
    restored.process(store.claim('restart'))
    final = store.get('jobs', job['id'])
    assert final['state'] == 'completed'
    summary = next(o for o in final['outcomes'] if o['source'] == 'public_pages')
    page_outcomes = [o for o in final['outcomes'] if o['source'].startswith('public_pages:')]
    assert summary['count'] == sum(o.get('count', 0) for o in page_outcomes)
    assert len([o for o in page_outcomes if o.get('url') == 'https://example.org/team/alex']) == 1


def test_malformed_optional_evidence_does_not_fail_other_sources(workspace):
    _, store, _, engine, fixture = workspace
    fixture['api_anything'] = {'openalex': {'results': []}, 'europepmc': {'resultList': {'result': []}}, 'industry_news': {'hits': []}}
    fixture['pages']['https://example.org/team/alex'] = '<script type="application/ld+json">{"@type":"Person","name":"Alex River","knows":[{"name":{"bad":"shape"}}]}</script>'
    job = run(engine, store, request())
    assert job['state'] == 'no_results'
    assert not store.rows('fixture_notes')
    assert any(o['outcome'] == 'unsupported' and o['source'].startswith('public_pages:') for o in job['outcomes'])
    assert any(e['review_status'] == 'rejected' for e in job['evidence'])
