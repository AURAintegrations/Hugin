from copy import deepcopy
import json
import socket
from unittest.mock import Mock
import pytest
import requests
from hugin.config import Settings, ConnectorError
from hugin.dex import DexMCP
from hugin.sources import Budget, PublicSources, dex_observations


def test_dex_linkedin_handle_is_a_known_profile_without_field_changes():
    from hugin.sources import identity, linkedin_url
    contact = {'first_name': 'Alex', 'last_name': 'River', 'linkedin': 'fixture-alex-river'}
    url = linkedin_url(contact['linkedin'])
    assert url == 'https://www.linkedin.com/in/fixture-alex-river'
    assert identity(contact, {'name': 'Alex River'}, url)['confidence'] == 'high'
    assert identity(contact, {'name': 'Different Person'}, url)['confidence'] == 'rejected'
    assert contact['linkedin'] == 'fixture-alex-river'
    assert linkedin_url('https://www.linkedin.com/in/fixture-alex-river') == url
    assert linkedin_url(None) == ''
    assert linkedin_url('foo/bar') == 'foo/bar'


def test_live_timeline_shape_supports_readback_and_duplicate_detection(monkeypatch):
    from hugin.engine import note_contact_ids
    dex = DexMCP(Settings(dex_key='TEST-ONLY-NOT-A-CREDENTIAL'))
    row = {'id': 'n1', 'note': 'Hugin job: stable-marker', 'timeline_items_contacts': [{'timeline_item_id': 'n1', 'contact_id': 'c1', 'contacts': {'id': 'c1'}}]}
    monkeypatch.setattr(dex, 'call', lambda name, args: {'items': [deepcopy(row)], 'has_more': False} if name == 'dex_list_notes' else {'note': deepcopy(row)})
    note = dex.get_note('n1')
    assert note['content'] == row['note']
    assert note_contact_ids(note) == {'c1'}
    assert dex.find_note('c1', 'stable-marker')['id'] == 'n1'
    assert 'content' not in row
    assert dex.normalize_note({'id': 'n2', 'content': 'body', 'contact_ids': ['c2']})['contact_ids'] == ['c2']


class Response:
    def __init__(self, payload, status=200, sse=False, headers=None):
        self.status_code = status
        self.headers = headers or {'Content-Type': 'text/event-stream' if sse else 'application/json'}
        self.payload = payload
        self.encoding = 'utf-8'
        self.sse = sse
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def iter_content(self, *args): yield json.dumps(self.payload).encode()
    def iter_lines(self): yield b'data: ' + json.dumps(self.payload).encode()


def test_mcp_transport_contract_and_write_guard(monkeypatch):
    settings = Settings(mode='live', dex_key='TEST-ONLY-NOT-A-CREDENTIAL')
    dex = DexMCP(settings)
    seen = []
    def post(url, json, **kwargs):
        seen.append(deepcopy(json))
        if json['method'] == 'initialize':
            return Response({'jsonrpc': '2.0', 'id': json['id'], 'result': {'protocolVersion': '2025-03-26'}}, headers={'Content-Type': 'application/json', 'Mcp-Session-Id': 'fixture-session'})
        if json['method'] == 'notifications/initialized': return Response({}, status=202)
        if json['method'] == 'tools/list':
            tools = [{'name': 'dex_get_contact', 'inputSchema': {'properties': {'id': {}, 'fields': {}}}}, {'name': 'dex_create_note', 'inputSchema': {'properties': {p: {} for p in ['contact_ids', 'content', 'event_time', 'idempotency_key', 'include_contacts']}}}]
            return Response({'id': json['id'], 'result': {'tools': tools}})
        assert json['method'] == 'tools/call'
        value = {'id': 'c1'} if json['params']['name'] == 'dex_get_contact' else {'id': 'note1'}
        return Response({'id': json['id'], 'result': {'content': [{'type': 'text', 'text': __import__('json').dumps(value)}]}}, sse=True)
    monkeypatch.setattr(dex.session, 'post', post)
    assert dex.contact('c1')['id'] == 'c1'
    note = dex.create_note('c1', 'fixture cited content', '2026-10-07T00:00:00Z', 'hugin:fixed-key')
    assert note['id'] == 'note1'
    arguments = seen[-1]['params']['arguments']
    assert arguments['event_time'] == '2026-10-07T00:00:00Z'
    assert arguments['idempotency_key'] == 'hugin:fixed-key'
    assert dex.session.headers['Mcp-Session-Id'] == 'fixture-session'
    # A server without safe note parameters must not receive a mutation.
    dex.schemas['dex_create_note']['properties'].pop('idempotency_key')
    before = len(seen)
    with pytest.raises(ConnectorError, match='safe parameters'):
        dex.create_note('c1', 'same', '2026-10-07T00:00:00Z', 'key')
    assert len(seen) == before


@pytest.mark.parametrize('status,outcome', [(401, 'authentication_required'), (403, 'authentication_required'), (429, 'quota_exhausted'), (500, 'unavailable')])
def test_provider_statuses_are_distinct_and_sanitized(monkeypatch, status, outcome):
    dex = DexMCP(Settings(dex_key='TEST-ONLY-SECRET'))
    monkeypatch.setattr(dex.session, 'post', lambda *a, **k: Response({'secret': 'PRIVATE-RESPONSE'}, status=status))
    with pytest.raises(ConnectorError) as error:
        dex.contact('c1')
    assert error.value.outcome == outcome
    assert 'SECRET' not in str(error.value) and 'PRIVATE-RESPONSE' not in str(error.value)


def test_citation_mapping_and_uncited_rejection(workspace):
    _, _, dex, _, _ = workspace
    contact = dex.contact('fixture-alex')
    research = {'identity_confidence': 'high', 'sources': [{'id': 1, 'url': contact['website']}], 'sections': {'current_focus': 'Alex River builds warehouse tools. [[1]]\nAn uncited claim about revenue.', 'background': 'Wrong citation. [[99]]'}, 'fields': {'email': {'value': 'new@example.org', 'confidence': 'high', 'evidence': 'No source reference', 'status': 'pending'}}}
    rows = dex_observations(contact, research)
    assert len(rows) == 1
    assert rows[0]['url'] == contact['website']
    assert 'uncited' not in rows[0]['value']
    research['identity_confidence'] = 'low'
    assert dex_observations(contact, research)[0]['identity']['confidence'] == 'low'


def test_private_source_and_unconfigured_host_blocked(workspace, monkeypatch):
    settings, store, _, _, _ = workspace
    settings.source_hosts = ('source.example',)
    source = PublicSources(settings, store)
    with pytest.raises(ConnectorError) as error:
        source.validate_url('https://other.example/person')
    assert error.value.outcome == 'not_searched'
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))])
    with pytest.raises(ConnectorError, match='non-public'):
        source.validate_url('https://source.example/person')
    with pytest.raises(ConnectorError):
        source.validate_url('https://user:password@source.example/person')


def test_public_page_extraction_caching_and_robots(workspace, monkeypatch):
    settings, store, dex, _, fixture = workspace
    settings.source_hosts = ('example.org',)
    source = PublicSources(settings, store)
    monkeypatch.setattr(source, 'validate_url', lambda url, allowed_hosts=(): requests.utils.urlparse(url))
    calls = []
    def get(url, budget, allowed_hosts=()):
        calls.append(url); budget.take()
        return url, 'User-agent: *\nAllow: /' if url.endswith('robots.txt') else fixture['pages'][url]
    monkeypatch.setattr(source, 'get', get)
    budget = Budget(10, 30, 0)
    first, cached, retrieved = source.page(dex.contact('fixture-alex'), 'https://example.org/team/alex', budget)
    assert first and not cached and len(calls) == 2
    second, cached, second_time = source.page(dex.contact('fixture-alex'), 'https://example.org/team/alex', budget)
    assert cached and first == second and retrieved == second_time and len(calls) == 2
    monkeypatch.setattr(source, 'get', lambda url, budget, allowed_hosts=(): (url, 'User-agent: *\nDisallow: /'))
    with pytest.raises(ConnectorError, match='robots'):
        source.page(dex.contact('fixture-alex'), 'https://example.org/another-person', budget)


def test_read_retry_is_bounded_mutation_never_blindly_retries(monkeypatch):
    dex = DexMCP(Settings(dex_key='TEST-ONLY-KEY'))
    dex.schemas = {'dex_get_contact': {'properties': {'id': {}, 'fields': {}}}, 'dex_create_note': {'properties': {p: {} for p in ['contact_ids', 'content', 'event_time', 'idempotency_key', 'include_contacts']}}}
    calls = []
    def failing(*args, **kwargs):
        calls.append(args)
        raise ConnectorError('unavailable', 'Synthetic service failure.')
    monkeypatch.setattr(dex, '_rpc', failing)
    with pytest.raises(ConnectorError): dex.contact('c1')
    assert len(calls) == 2
    calls.clear()
    with pytest.raises(ConnectorError): dex.create_note('c1', 'note', '2026-10-07T00:00:00Z', 'fixed')
    assert len(calls) == 1


def test_company_homepage_is_not_a_person_identifier():
    from hugin.sources import identity
    contact = {'first_name': 'Alex', 'last_name': 'River', 'company': 'Example Robotics', 'website': 'https://example.org/'}
    person = {'name': 'Alex River', 'worksFor': {'name': 'Example Robotics'}}
    result = identity(contact, person, 'https://example.org/')
    assert result['confidence'] == 'medium'
    assert 'known_profile' not in result['signals']


def test_profile_query_ids_and_case_sensitive_paths_do_not_merge():
    from hugin.sources import canonical, identity
    assert canonical('https://example.org/people?id=1') != canonical('https://example.org/people?id=2')
    assert canonical('https://example.org/Alex') != canonical('https://example.org/alex')
    contact = {'first_name': 'Alex', 'last_name': 'River', 'website': 'https://example.org/people?id=1'}
    assert identity(contact, {'name': 'Alex River'}, 'https://example.org/people?id=2')['confidence'] == 'low'
