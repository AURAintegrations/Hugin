"""Professional collector adapters; candidates remain distinct from findings."""
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import subprocess
import time
from .config import ConnectorError
from .models import fingerprint, now
from .sources import identity, linkedin_url


def profile_username(contact):
    # Use the known professional profile, not guessed names or email local parts.
    p = urlparse(linkedin_url(contact.get('linkedin')))
    value = p.path.strip('/').split('/')[-1]
    return value if p.hostname in ('linkedin.com', 'www.linkedin.com') and re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}', value) else None


def maigret_candidates(settings, public, store, contact, budget):
    username = profile_username(contact)
    if not username:
        raise ConnectorError('not_searched', 'No supported professional username anchor is available; usernames were not guessed.')
    if not Path(settings.maigret_python).is_file():
        raise ConnectorError('unsupported', 'Pinned Maigret collector is not installed. Run scripts/install-collectors.sh.')
    key = fingerprint({'maigret': '0.6.6', 'username': username, 'contact': contact})
    cached = store.get('source_cache', key)
    if cached and time.time() - cached['cached_at'] < 86400:
        return cached['candidates'], cached['observations'], True
    # GitHub's documented public user API is the exact probe in Maigret's database.
    # No SDK network checker, TLS impersonation, cookies or recursive expansion.
    url = 'https://api.github.com/users/' + username
    _, body = public.get(url, budget, ('api.github.com',), json_allowed=True)
    budget.timeout()
    worker = Path(__file__).with_name('maigret_worker.py')
    try:
        result = subprocess.run([settings.maigret_python, str(worker)], input=json.dumps({'username': username, 'body': body}), capture_output=True, text=True, timeout=budget.timeout(), check=False)
        data = json.loads(result.stdout)
        if result.returncode or data.get('error'):
            raise ConnectorError('unsupported', 'Maigret response classification failed; no identity conclusion was accepted.')
    except subprocess.TimeoutExpired:
        raise ConnectorError('timeout', 'Bounded Maigret detector did not finish.') from None
    except (OSError, ValueError):
        raise ConnectorError('unsupported', 'Maigret detector was unavailable or returned an unsupported response.') from None
    if not data.get('claimed'):
        return [], [], False
    try:
        profile = json.loads(body)
        if not isinstance(profile, dict):
            raise ValueError
    except ValueError:
        raise ConnectorError('unsupported', 'Public profile response was not a supported object.') from None
    expected_url = 'https://github.com/' + username
    if str(profile.get('login', '')).casefold() != username.casefold() or str(profile.get('html_url', '')).casefold() != expected_url.casefold():
        raise ConnectorError('ambiguous_identity', 'Public profile did not match the requested account identifier.')
    person = {'name': profile.get('name') or '', 'worksFor': {'name': profile.get('company') or ''}, 'url': expected_url}
    match = identity(contact, person, expected_url)
    candidate = {'url': expected_url, 'provider_url': url, 'username': username, 'provider': 'maigret', 'collector_version': '0.6.6', 'retrieved_at': now(), 'identity': match, 'review_status': 'rejected' if match['confidence'] == 'rejected' else 'pending', 'reason': 'Matching username is a candidate only; independent identity signals are required.'}
    observations = []
    if match['confidence'] != 'rejected' and 'full_name' in match['signals']:
        for kind, field in (('biography', 'bio'), ('company', 'company')):
            value = profile.get(field)
            if isinstance(value, str) and value.strip():
                observations.append({'kind': kind, 'value': value[:1200], 'url': url, 'provider': 'maigret', 'retrieved_at': candidate['retrieved_at'], 'identity': match, 'excerpt': json.dumps({'name': profile.get('name'), field: value})[:500]})
    store.put('source_cache', key, {'candidates': [candidate], 'observations': observations, 'cached_at': time.time()})
    return [candidate], observations, False
