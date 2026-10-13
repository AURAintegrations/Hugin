from copy import deepcopy
from hugin.entities import snapshot
from hugin.models import EnrichRequest
from tests.conftest import run


def test_typed_snapshot_preserves_uncertain_relationships_and_citations(workspace):
    _, store, _, engine, _ = workspace
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex'))
    graph = job['entity_snapshot']
    assert store.get('entity_snapshots', job['id']) == graph
    assert any(e['entity']['schema'] == 'Employment' and e['review_status'] == 'existing_contact_context' for e in graph['edges'])
    relation = next(e for e in graph['edges'] if e['entity']['schema'] == 'Associate')
    assert relation['review_status'] != 'verified'
    assert relation['evidence_ids'] and set(relation['evidence_ids']) <= set(graph['evidence_ids'])
    target_id = relation['entity']['properties']['associate'][0]
    assert next(n for n in graph['nodes'] if n['entity']['id'] == target_id)['review_status'] == 'unresolved'
    assert 'contact_emails' not in str(graph)


def test_company_name_does_not_merge_contacts_or_rewrite_older_snapshot(workspace):
    _, store, _, engine, _ = workspace
    job = run(engine, store, EnrichRequest(dex_contact_id='fixture-alex'))
    previous = deepcopy(job['entity_snapshot'])
    second = deepcopy(job); second['id'] = 'second-job'; second['contact']['id'] = 'other-contact'
    newer = snapshot(second)
    company = lambda graph: next(n['entity']['id'] for n in graph['nodes'] if n['entity']['schema'] == 'Company' and n['review_status'] == 'existing_contact_context')
    assert company(previous) != company(newer)
    assert store.get('entity_snapshots', job['id']) == previous
