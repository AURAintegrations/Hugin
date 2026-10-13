"""Real pinned Maigret detector with explicitly synthetic provider responses."""
import json
from pathlib import Path
import pytest
from hugin.config import ConnectorError
from hugin.collectors import maigret_candidates, profile_username
from hugin.sources import PublicSources, Budget, SearchLinks


def test_search_results_are_urls_not_claims_and_challenges_stop(workspace, monkeypatch):
    settings, store, dex, _, _ = workspace
    source = PublicSources(settings, store)
    document = '<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fsource.example%2Fperson">Unverified snippet</a><a class="result__a" href="http://127.0.0.1/a">Ignore</a>'
    parser = SearchLinks(); parser.feed(document)
    assert parser.urls == ['https://source.example/person']
    calls = []
    def get(url, budget, hosts=()):
        calls.append(url); budget.take()
        return url, 'User-agent: *\nAllow: /' if url.endswith('/robots.txt') else document
    monkeypatch.setattr(source, 'get', get)
    urls, cached = source.discover(dex.contact('fixture-alex'), Budget(4, 20, 0))
    assert urls == parser.urls and not cached and len(calls) == 2
    assert source.discover(dex.contact('fixture-alex'), Budget(1, 20, 0))[1]
    changed = {**dex.contact('fixture-alex'), 'company': 'Different Example'}
    monkeypatch.setattr(source, 'get', lambda url, budget, hosts=(): (url, 'User-agent: *\nAllow: /' if url.endswith('/robots.txt') else '<form id="challenge-form"></form>'))
    with pytest.raises(ConnectorError, match='challenge'):
        source.discover(changed, Budget(4, 20, 0))


def test_search_discovered_host_still_rejects_private_addresses(workspace, monkeypatch):
    import socket
    settings, store, _, _, _ = workspace
    source = PublicSources(settings, store)
    monkeypatch.setattr(socket, 'getaddrinfo', lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))])
    with pytest.raises(ConnectorError, match='non-public'):
        source.page({}, 'https://discovered.example/a', Budget(5, 20, 0), discovered=True)


@pytest.mark.parametrize('name,review,has_findings', [('Different Person', 'rejected', False), ('', 'pending', False), ('Alex River', 'pending', True)])
def test_maigret_handle_is_only_a_candidate(workspace, monkeypatch, name, review, has_findings):
    settings, store, dex, _, _ = workspace
    if not Path(settings.maigret_python).is_file():
        pytest.skip('Install the pinned isolated Maigret collector for this integration test')
    contact = dex.contact('fixture-alex')
    username = profile_username(contact)
    assert username == 'fixture-alex-river'
    body = json.dumps({'login': username, 'html_url': 'https://github.com/' + username, 'name': name, 'company': 'Example Robotics', 'bio': 'Synthetic professional biography'})
    source = PublicSources(settings, store)
    monkeypatch.setattr(source, 'get', lambda *a, **k: (a[0], body))
    candidates, observations, cached = maigret_candidates(settings, source, store, contact, Budget(3, 30, 0))
    assert candidates[0]['review_status'] == review
    assert candidates[0]['identity']['confidence'] != 'high'
    assert bool(observations) == has_findings and not cached
    assert maigret_candidates(settings, source, store, contact, Budget(1, 30, 0))[2]
