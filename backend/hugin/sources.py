"""Bounded public-source extraction. Source text is data, never executable instructions."""
from html.parser import HTMLParser
from urllib.parse import urlparse, urlencode, parse_qs, urljoin
from urllib.robotparser import RobotFileParser
import ipaddress
import json
import socket
import time
import requests
import trafilatura
from .config import ConnectorError
from .models import fingerprint, now

SOURCE_REGISTRY = [
    {'id': 'api_anything', 'name': 'API Anything professional metadata', 'access': 'Three reviewed GET operations: OpenAlex authors, Europe PMC publications, Hacker News company mentions. Offline pinned worker; Hugin public DNS/robots/TLS/budget controls; no browser, cookies or automatic repair.', 'reuse': 'OpenAlex CC0 metadata; Europe PMC bibliographic attribution and Hacker News short story metadata for private review. Article content and linked pages retain their own rights. Name matches and last listed affiliations remain pending.', 'cost': 'Anonymous public endpoints; no paid keys or paid research. OpenAlex may report a query-cost estimate, recorded separately from billing.', 'retention': 'Short cited metadata excerpts, reviewed operation digest, retrieval/event dates and identity signals'},
    {'id': 'company_web', 'name': 'Company public website', 'access': 'One bounded domain hypothesis or supplied candidates; published same-host links only; public DNS, robots and verified TLS required', 'reuse': 'Company statements are attributed excerpts. Candidate organization match and personal affiliation remain unconfirmed. Private research only.', 'cost': 'No provider charge', 'retention': 'Short cited excerpts, candidate origin and per-page outcomes'},
    {'id': 'linkedin', 'name': 'LinkedIn professional profile', 'access': 'Pinned isolated scraper; supplied permitted HTML or owner-only authorized session; robots and access controls respected; no contact overlay or login automation', 'reuse': 'Permitted private professional evidence only; session access and code licensing grant no rights to reuse LinkedIn content.', 'cost': 'No provider charge; authorized access and parser installation required', 'retention': 'Short excerpts and structured findings; submitted HTML removed after the source checkpoint'},
    {'id': 'public_discovery', 'name': 'Public web discovery', 'access': 'Bounded DuckDuckGo HTML search; robots respected, no challenge bypass', 'reuse': 'Search returns candidate URLs only; source-specific rights apply to extracted evidence.', 'cost': 'No provider charge; availability is not guaranteed', 'retention': 'Query fingerprint, discovered URLs and source outcomes'},
    {'id': 'maigret', 'name': 'Maigret professional account discovery', 'access': 'Pinned Maigret 0.6.6 database and detector; GitHub only; Hugin verified HTTPS transport; no recursion, cookies, scans or bypass', 'reuse': 'Public professional profile candidates for private review. A matching handle does not prove identity.', 'cost': 'No provider charge', 'retention': 'Candidate account URL, detector outcome, short professional excerpt and identity signals'},
    {'id': 'dex_cached', 'name': 'Dex cached research', 'access': 'Authorized Dex MCP; reads only', 'reuse': 'Private contact workspace. Upstream citations retain their own rights.', 'cost': 'No fresh research charge', 'retention': 'Cited structured observations and bounded excerpts'},
    {'id': 'public_pages', 'name': 'Public professional pages', 'access': 'Exact configured public hosts, robots respected; no login or CAPTCHA bypass', 'reuse': 'Source-specific rights; private research excerpts only. No redistribution license is inferred.', 'cost': 'No provider charge', 'retention': 'Metadata and short excerpts, not full HTML'},
    {'id': 'brave', 'name': 'Brave Search', 'access': 'Configured API key and explicit paid budget', 'reuse': 'Provider terms apply; search discovers URLs, snippets are not verified findings', 'cost': 'At most one search unit per run; billing depends on provider plan', 'retention': 'URLs and connector outcomes'},
    {'id': 'dex_fresh', 'name': 'Fresh Dex Research', 'access': 'Explicit opt-in; eligible Dex plan; never force; may fill Dex fields and replace stored research', 'reuse': 'Authorized private research; source-specific rights remain', 'cost': 'At most one fresh research unit; provider price not assumed', 'retention': 'Hugin preserves each run separately'},
]


class Budget:
    def __init__(self, max_requests, seconds, paid_units, checkpoint=None):
        self.checkpoint = checkpoint
        self.remaining = max_requests
        self.deadline = time.monotonic() + seconds
        self.paid_remaining = paid_units
        self.requests = 0
        self.paid_attempts = 0

    def timeout(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ConnectorError('timeout', 'Research deadline reached.')
        return min(remaining, 15)

    def take(self, paid=False):
        self.timeout()
        if self.remaining <= 0 or (paid and self.paid_remaining <= 0):
            raise ConnectorError('quota_exhausted', 'Configured run budget exhausted.')
        self.remaining -= 1
        self.requests += 1
        if paid:
            self.paid_remaining -= 1
            self.paid_attempts += 1
        if self.checkpoint:
            self.checkpoint(paid)


class StructuredHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.collect = False
        self.text = ''
        self.documents = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type', '').lower() == 'application/ld+json':
            self.collect, self.text = True, ''

    def handle_data(self, data):
        if self.collect:
            self.text += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.collect:
            try:
                document = json.loads(self.text)
                self.documents.extend(document if isinstance(document, list) else [document])
            except ValueError:
                pass
            self.collect = False


def linkedin_url(value):
    """Dex can return a LinkedIn handle. Preserve the contact field itself."""
    if not isinstance(value, str):
        return ''
    value = value.strip()
    import re
    if re.fullmatch(r'[A-Za-z0-9_-]+', value):
        return 'https://www.linkedin.com/in/' + value
    return value


def canonical(url):
    if not isinstance(url, str):
        return ''
    p = urlparse(url.strip())
    # Keep case-sensitive paths and query identifiers: two profile IDs are not interchangeable.
    return (p.hostname or '').lower().removeprefix('www.') + p.path.rstrip('/') + ('?' + p.query if p.query else '')


def emails(contact):
    values = contact.get('contact_emails', contact.get('emails', []))
    return [row.get('email', '').lower() if isinstance(row, dict) else row.lower() for row in values]


def full_name(contact):
    return contact.get('name') or ' '.join(str(contact.get(k) or '') for k in ('first_name', 'last_name')).strip()


def identity(contact, person, source_url, text=''):
    name = full_name(contact).casefold()
    candidate_name = str(person.get('name') or '').casefold()
    org = person.get('worksFor') or {}
    if isinstance(org, list):
        org = org[0] if org else {}
    company = org.get('name', '') if isinstance(org, dict) else str(org)
    if not isinstance(company, str):
        company = ''
    expected = str(contact.get('company') or '').casefold()
    same_as = person.get('sameAs') or []
    if isinstance(same_as, str):
        same_as = [same_as]
    if not isinstance(same_as, list):
        same_as = []
    candidate_urls = [source_url, person.get('url', '')] + [u for u in same_as if isinstance(u, str)]
    # A company homepage is not a person-specific professional identifier.
    known_urls = [linkedin_url(contact.get('linkedin', ''))]
    website = contact.get('website', '')
    if website and urlparse(website).path.rstrip('/'):
        known_urls.append(website)
    signals = []
    if name and (candidate_name == name or (not candidate_name and name in text.casefold())):
        signals.append('full_name')
    if expected and company.casefold() == expected:
        signals.append('company')
    if any(canonical(u) and canonical(u) == canonical(k) for u in candidate_urls for k in known_urls):
        signals.append('known_profile')
    candidate_email = str(person.get('email') or '').lower().removeprefix('mailto:')
    if candidate_email and candidate_email in emails(contact):
        signals.append('known_email')
    conflicts = []
    if candidate_name and name and candidate_name != name:
        conflicts.append('different_name')
    if expected and company and company.casefold() != expected:
        conflicts.append('different_company')
    if candidate_email and emails(contact) and candidate_email not in emails(contact):
        # A different professional email may be a new address, not proof of a different person.
        conflicts.append('unconfirmed_email')
    if 'different_name' in conflicts:
        return {'confidence': 'rejected', 'signals': signals, 'conflicts': conflicts}
    strong = 'known_profile' in signals or 'known_email' in signals
    if strong and 'full_name' in signals and 'different_company' not in conflicts:
        confidence = 'high'
    elif len(signals) >= 2:
        confidence = 'medium'
    else:
        confidence = 'low'
    return {'confidence': confidence, 'signals': signals, 'conflicts': conflicts}


def page_observations(contact, url, html):
    parser = StructuredHTML()
    parser.feed(html)
    text = trafilatura.extract(html, include_comments=False, include_tables=False) or ''
    documents = []
    for document in parser.documents:
        if isinstance(document, dict):
            documents.extend(document.get('@graph', [document]))
    people = [d for d in documents if isinstance(d, dict) and 'Person' in (d.get('@type') if isinstance(d.get('@type'), list) else [d.get('@type')])]
    observations = []
    for person in people[:10]:
        match = identity(contact, person, url, text)
        if match['confidence'] == 'rejected':
            observations.append({'kind': 'rejected_identity', 'value': 'Page describes a different person', 'identity': match, 'excerpt': str(person.get('name', ''))[:200]})
            continue
        company = person.get('worksFor') or {}
        if isinstance(company, list):
            company = company[0] if company else {}
        values = {'job_title': person.get('jobTitle'), 'company': company.get('name') if isinstance(company, dict) else company, 'biography': person.get('description'), 'website': person.get('url'), 'email': person.get('email'), 'phone': person.get('telephone')}
        same_as = person.get('sameAs', [])
        if isinstance(same_as, str):
            same_as = [same_as]
        if not isinstance(same_as, list):
            same_as = []
        for profile in same_as:
            if isinstance(profile, str) and urlparse(profile).hostname in ('www.linkedin.com', 'linkedin.com'):
                values['linkedin'] = profile
        for kind, value in values.items():
            if isinstance(value, str) and value.strip():
                observations.append({'kind': kind, 'value': value[:1200], 'identity': match, 'excerpt': json.dumps({kind: value}, ensure_ascii=False)[:500], 'event_date': person.get('dateModified')})
        # knows does not establish friendship, investment, or introductions.
        knows = person.get('knows', [])
        if isinstance(knows, dict):
            knows = [knows]
        if isinstance(knows, list):
            for other in knows[:10]:
                if isinstance(other, dict) and other.get('name'):
                    observations.append({'kind': 'relationship', 'value': other['name'][:200], 'relationship_type': 'documented_association', 'target_url': other.get('url'), 'identity': match, 'excerpt': json.dumps({'knows': other}, ensure_ascii=False)[:500]})
    if not people and text:
        match = identity(contact, {}, url, text)
        name = full_name(contact)
        position = text.casefold().find(name.casefold()) if name else -1
        if position >= 0:
            excerpt = text[max(0, position - 60):position + 440]
            observations.append({'kind': 'professional_context', 'value': excerpt, 'identity': match, 'excerpt': excerpt})
    return observations[:50]


def dex_observations(contact, research):
    if not research or research.get('status') == 'no_data_found':
        return []
    sources = research.get('sources') or []
    source_map = {str(s.get('id', i + 1)): s for i, s in enumerate(sources) if isinstance(s, dict)}
    observations = []
    import re
    sections = research.get('sections') or {}
    if not isinstance(sections, dict):
        sections = {}
    for kind, content in sections.items():
        texts = content if isinstance(content, list) else [content]
        for entry in texts:
            if isinstance(entry, dict):
                entry = entry.get('text', '')
            if not isinstance(entry, str):
                continue
            # Each statement must carry its own citation; don't attach unrelated sources.
            for statement in re.split(r'(?<=\]\])\s+|\n', entry):
                refs = re.findall(r'\[\[(\d+)\]\]', statement)
                for ref in refs:
                    source = source_map.get(ref, {})
                    url = source.get('url', '')
                    if urlparse(url).scheme not in ('http', 'https'):
                        continue
                    match = identity(contact, {}, url, statement)
                    # Provider confidence is recorded, but is not independent identity proof.
                    match['provider_confidence'] = research.get('identity_confidence', 'unknown')
                    if research.get('identity_confidence') != 'high':
                        match['confidence'] = 'low'
                    observations.append({'kind': kind, 'value': re.sub(r'\[\[\d+\]\]', '', statement).strip()[:1200], 'url': url, 'identity': match, 'excerpt': statement[:500], 'event_date': research.get('researched_at', research.get('created_at'))})
    fields = research.get('fields') or {}
    if isinstance(fields, list):
        fields = {f.get('field', ''): f for f in fields if isinstance(f, dict)}
    if isinstance(fields, dict):
        for kind, finding in fields.items():
            if not isinstance(finding, dict) or not finding.get('value'):
                continue
            evidence = finding.get('evidence') or ''
            url = finding.get('source_url')
            refs = re.findall(r'\[\[(\d+)\]\]', str(evidence))
            if not url and refs:
                url = source_map.get(refs[0], {}).get('url')
            if not url or urlparse(url).scheme not in ('http', 'https'):
                continue
            match = identity(contact, {}, url, str(evidence))
            if finding.get('confidence') != 'high' or research.get('identity_confidence') != 'high':
                match['confidence'] = 'low'
            observations.append({'kind': kind, 'value': str(finding['value'])[:1200], 'url': url, 'identity': match, 'excerpt': str(evidence)[:500], 'provider_review_status': finding.get('status', 'pending')})
    return observations[:50]


class PublicSources:
    def __init__(self, settings, store):
        self.settings, self.store = settings, store
        self.http = requests.Session()
        self.http.headers['User-Agent'] = 'HuginResearch/1.0 (private professional research; respects robots.txt)'

    def validate_url(self, url, allowed_hosts=()):
        p = urlparse(url)
        try:
            port = p.port
        except ValueError:
            raise ConnectorError('unsupported', 'Invalid public source port.') from None
        if p.scheme != 'https' or p.username or p.password or port not in (None, 443) or not p.hostname:
            raise ConnectorError('unsupported', 'Only credential-free public HTTPS source URLs are supported.')
        if p.hostname.lower() not in (*self.settings.source_hosts, *allowed_hosts):
            raise ConnectorError('not_searched', 'Source hostname is not in HUGIN_SOURCE_HOSTS.')
        try:
            addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
        except socket.gaierror:
            raise ConnectorError('unavailable', 'Cannot resolve the public source host.') from None
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise ConnectorError('unsupported', 'Private, loopback and non-public source addresses are blocked.')
        return p

    def get(self, url, budget, allowed_hosts=(), json_allowed=False):
        for _ in range(3):
            self.validate_url(url, allowed_hosts)
            budget.take()
            try:
                with self.http.get(url, timeout=budget.timeout(), stream=True, allow_redirects=False) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        # Refuse page redirects: permission for one path is not permission for another.
                        # The caller can explicitly select the canonical URL after review.
                        raise ConnectorError('unsupported', 'Source redirected; configure its canonical URL and robots policy before extraction.')
                    if response.status_code in (401, 403):
                        raise ConnectorError('unsupported', 'Source access was denied; no access controls will be bypassed.')
                    if response.status_code == 429:
                        raise ConnectorError('quota_exhausted', 'Source rate limit reached.')
                    if response.status_code == 404:
                        raise ConnectorError('no_result', 'Source page was not found.')
                    if response.status_code >= 400:
                        raise ConnectorError('unavailable', 'Source request failed.')
                    content_type = response.headers.get('Content-Type', '')
                    if not any(t in content_type for t in ('text/', 'application/xhtml', *(['application/json'] if json_allowed else []))):
                        raise ConnectorError('unsupported', 'Only HTML and text sources are supported.')
                    content = bytearray()
                    for chunk in response.iter_content(8192):
                        budget.timeout()
                        content.extend(chunk)
                        if len(content) > 1_000_000:
                            raise ConnectorError('unsupported', 'Source exceeded the one-megabyte limit.')
                    return url, content.decode(response.encoding or 'utf-8', errors='replace')
            except requests.Timeout:
                raise ConnectorError('timeout', 'Source request timed out.') from None
            except requests.RequestException:
                raise ConnectorError('unavailable', 'Cannot reach source through the configured network.') from None
        raise ConnectorError('unsupported', 'Source redirect bound reached.')

    def page(self, contact, url, budget, discovered=False):
        allowed_hosts = (urlparse(url).hostname,) if discovered else ()
        self.validate_url(url, allowed_hosts)
        key = fingerprint({'url': url, 'contact': contact, 'version': 1})
        cached = self.store.get('source_cache', key)
        if cached and time.time() - cached['cached_at'] < 86400:
            return cached['observations'], True, cached['retrieved_at']
        p = urlparse(url)
        robots_url = f'{p.scheme}://{p.netloc}/robots.txt'
        try:
            _, robots_text = self.get(robots_url, budget, allowed_hosts)
        except ConnectorError as error:
            if error.outcome == 'no_result':
                robots_text = ''
            else:
                raise
        robots = RobotFileParser()
        robots.parse(robots_text.splitlines())
        if not robots.can_fetch('HuginResearch', url):
            raise ConnectorError('unsupported', 'Source robots policy disallows extraction.')
        for attempt in range(2):
            try:
                final_url, html = self.get(url, budget, allowed_hosts)
                break
            except ConnectorError as error:
                if attempt == 1 or error.outcome not in ('timeout', 'unavailable'):
                    raise
        observations = page_observations(contact, final_url, html)
        for observation in observations:
            observation['url'] = final_url
        retrieved_at = now()
        self.store.put('source_cache', key, {'observations': observations, 'cached_at': time.time(), 'retrieved_at': retrieved_at})
        return observations, False, retrieved_at

    def discover(self, contact, budget):
        query = ' '.join('"' + str(v).replace('"', '') + '"' for v in (full_name(contact), contact.get('company')) if v)
        key = fingerprint({'public_discovery': query, 'version': 1})
        cached = self.store.get('source_cache', key)
        if cached and time.time() - cached['cached_at'] < 86400:
            return cached['urls'], True
        root = 'https://html.duckduckgo.com'
        url = root + '/html/?' + urlencode({'q': query})
        hosts = ('html.duckduckgo.com',)
        _, rules = self.get(root + '/robots.txt', budget, hosts)
        robots = RobotFileParser(); robots.parse(rules.splitlines())
        if not robots.can_fetch('HuginResearch', url):
            raise ConnectorError('unsupported', 'Discovery service robots policy disallows search.')
        _, document = self.get(url, budget, hosts)
        if 'challenge-form' in document or 'anomaly.js' in document:
            raise ConnectorError('unsupported', 'Discovery service returned an access challenge; it was not bypassed.')
        parser = SearchLinks(); parser.feed(document)
        urls = parser.urls[:5]
        self.store.put('source_cache', key, {'urls': urls, 'cached_at': time.time()})
        return urls, False


    def search(self, contact, budget):
        if not self.settings.brave_key:
            raise ConnectorError('authentication_required', 'BRAVE_SEARCH_API_KEY is not configured.')
        query = f'"{full_name(contact)}" "{contact.get("company") or ""}" professional biography'
        key = fingerprint({'brave': query})
        cached = self.store.get('source_cache', key)
        if cached and time.time() - cached['cached_at'] < 86400:
            return cached['urls'], True
        budget.take(paid=True)
        try:
            response = self.http.get('https://api.search.brave.com/res/v1/web/search', params={'q': query, 'count': 5}, headers={'X-Subscription-Token': self.settings.brave_key}, timeout=budget.timeout(), allow_redirects=False)
            if response.status_code in (401, 403):
                raise ConnectorError('authentication_required', 'Brave denied access; check the API key and network policy.')
            if response.status_code == 429:
                raise ConnectorError('quota_exhausted', 'Brave quota exhausted.')
            if response.status_code != 200:
                raise ConnectorError('unavailable', 'Brave search request failed.')
            if len(response.content) > 1_000_000:
                raise ConnectorError('unsupported', 'Brave response exceeded its size bound.')
            urls = [row['url'] for row in response.json().get('web', {}).get('results', []) if row.get('url')][:5]
        except requests.Timeout:
            raise ConnectorError('timeout', 'Brave search timed out.') from None
        except (requests.RequestException, ValueError):
            raise ConnectorError('unavailable', 'Cannot reach or decode Brave search.') from None
        self.store.put('source_cache', key, {'urls': urls, 'cached_at': time.time()})
        return urls, False


class SearchLinks(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag != 'a' or 'result__a' not in attrs.get('class', '').split():
            return
        p = urlparse(urljoin('https://html.duckduckgo.com', attrs.get('href', '')))
        href = parse_qs(p.query).get('uddg', [''])[0] if p.hostname in ('duckduckgo.com', 'html.duckduckgo.com') else p.geturl()
        target = urlparse(href)
        if target.scheme == 'https' and target.hostname and not target.username and not target.password and href not in self.urls:
            self.urls.append(href)
