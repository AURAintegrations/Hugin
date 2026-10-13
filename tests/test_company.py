"""Company evidence stays distinct from person identity; fixtures are synthetic."""
import pytest
from hugin.company import collect, page_context, roots
from hugin.config import ConnectorError
from hugin.models import EnrichRequest
from hugin.sources import Budget
from tests.conftest import run

HOME = '<html><title>Example Robotics</title><main><style>noise</style><h1>Example Robotics</h1><p>Example Robotics supplies warehouse automation systems and offers a dealer partner program for professional distributors.</p><a href="/dealers">Dealer program</a><a href="https://other.example/team">Ignore off-host</a></main></html>'
DEALER = '<html><title>Dealer Program</title><main><p>Example Robotics offers training and technical support to distributors who participate in its professional partner program.</p></main></html>'
ROOT = 'https://www.examplerobotics.com/'


def test_company_domain_is_only_a_hypothesis():
    assert roots({'company': 'E-Z UP'}) == (['https://www.ezup.com/'], 'company_name_hypothesis')
    assert roots({'company': ''})[0] == []
    rows, links = page_context({'name': 'Alex River', 'company': 'Example Robotics'}, ROOT, HOME)
    assert rows[0]['kind'] == 'company_context' and rows[0]['subject_type'] == 'company'
    assert rows[0]['identity']['confidence'] == 'low' and rows[0]['provider_review_status'] == 'pending'
    assert links == [ROOT + 'dealers']
    assert page_context({'company': 'Different Company'}, ROOT, HOME)[0] == []


def test_actual_page_bounds_cache_and_robots_isolation(workspace, monkeypatch):
    _, store, dex, engine, _ = workspace
    contact = dex.contact('fixture-alex')
    calls = []
    def get(url, budget, hosts=()):
        budget.take(); calls.append(url)
        if url.endswith('robots.txt'):
            return url, 'User-agent: *\nDisallow: /dealers'
        return url, HOME
    monkeypatch.setattr(engine.public, 'validate_url', lambda *a: None)
    monkeypatch.setattr(engine.public, 'get', get)
    rows, outcomes, cached = collect(engine.public, store, contact, Budget(5, 20, 0))
    assert rows and not cached and len(calls) == 2
    assert outcomes[-1]['outcome'] == 'unsupported' and ROOT + 'dealers' not in calls
    assert collect(engine.public, store, contact, Budget(1, 20, 0))[2]
    previous = len(store.rows('source_cache'))
    _, limited, _ = collect(engine.public, store, {**contact, 'company': 'Different Example'}, Budget(1, 20, 0))
    assert any(row['outcome'] == 'quota_exhausted' for row in limited)
    assert len(store.rows('source_cache')) == previous, 'Temporary budget failure must not poison the next run'


def test_company_only_notes_are_labeled_and_preserve_person(workspace):
    _, store, dex, engine, fixture = workspace
    fixture['company_pages'] = {ROOT: HOME, ROOT + 'dealers': DEALER}
    before = dex.contact('fixture-alex')
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['company_web']))
    assert job['state'] == 'completed' and job['sync']['note_verified']
    assert job['research_scope'] == 'company_context_only'
    assert all(f['kind'] == 'company_context' and f['subject_type'] == 'company' and f['status'] == 'unresolved' for f in job['findings'])
    assert 'do not verify this contact’s affiliation' in job['note']
    assert not job['proposals'] and not job['relationships']
    assert dex.contact('fixture-alex') == before and job['costs']['paid_attempts'] == 0


@pytest.mark.parametrize('url', ['http://example.org', 'https://user:password@example.org', 'https://example.org/?key=secret', 'https://example.org/#fragment'])
def test_bad_company_hints_rejected(url):
    with pytest.raises(ValueError):
        EnrichRequest(dex_contact_id='fixture-alex', sources=['company_web'], company_urls=[url])


def test_company_fails_without_disabling_other_evidence(workspace):
    _, store, _, engine, fixture = workspace
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex', sources=['company_web', 'public_pages']))
    assert job['state'] == 'completed' and job['findings']
    assert next(o for o in job['outcomes'] if o['source']=='company_web')['outcome'] == 'no_result'
