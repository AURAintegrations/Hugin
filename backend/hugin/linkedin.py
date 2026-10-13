"""Bounded acquisition; session credentials never reach the offline parser."""
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import json
import os
import re
import stat
import signal
import subprocess
import time
import requests
from lxml import html as lh
from .config import ConnectorError
from .models import fingerprint, now
from .sources import identity, linkedin_url

REVISION = 'b1cdc1c0e85bee8764d62565d229c682e5eb81bb'
MAX_HTML = 1_000_000


def run_worker(python, worker, payload, timeout):
    process = subprocess.Popen([python, str(worker)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(json.dumps(payload), timeout=timeout)
    except subprocess.TimeoutExpired:
        # Chromium/Playwright are children; kill the whole isolated process group.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()
        raise
    return subprocess.CompletedProcess([], process.returncode, stdout, stderr)


def profile_url(value):
    p = urlparse(linkedin_url(value))
    try:
        valid = p.scheme == 'https' and p.hostname in ('linkedin.com', 'www.linkedin.com') and p.port in (None, 443)
    except ValueError:
        valid = False
    if not valid or p.username or p.password or p.query or p.fragment or not re.fullmatch(r'/in/[A-Za-z0-9_-]{1,100}/?', p.path):
        raise ConnectorError('unsupported', 'A credential-free LinkedIn HTTPS /in/ profile URL or handle is required.')
    return 'https://www.linkedin.com' + p.path.rstrip('/') + '/'


def inspect_html(document, url):
    if not isinstance(document, str) or len(document.encode('utf-8')) > MAX_HTML:
        raise ConnectorError('unsupported', 'Profile HTML exceeded its one-megabyte bound.')
    try:
        tree = lh.fromstring(document)
    except (ValueError, lh.etree.ParserError):
        raise ConnectorError('no_result', 'No parseable profile HTML was supplied.') from None
    if tree.xpath('//iframe[contains(translate(@title,"CAPTCHA","captcha"),"captcha") or contains(@src,"captcha")]') or tree.xpath('//*[@id="captcha-internal" or @id="challenge" or @id="authwall"]'):
        raise ConnectorError('unsupported', 'LinkedIn returned an access challenge; it was not bypassed.')
    text = ' '.join(tree.xpath('//text()[not(ancestor::script) and not(ancestor::style)]')).casefold()
    if any(phrase in text for phrase in ('too many requests', 'rate limit exceeded', 'try again later')):
        raise ConnectorError('quota_exhausted', 'LinkedIn returned a rate-limit page.')
    if tree.xpath('//form[contains(@action,"login") or contains(@action,"checkpoint")]') or (not tree.xpath('//h1') and 'sign in' in text):
        raise ConnectorError('authentication_required', 'LinkedIn returned a login or checkpoint page.')
    canonical = tree.xpath('//link[contains(concat(" ",normalize-space(@rel)," ")," canonical ")]/@href')
    if canonical and profile_url(canonical[0]) != url:
        raise ConnectorError('ambiguous_identity', 'Profile HTML canonical URL differs from the selected Dex profile.')
    for node in tree.xpath('//script|//style|//iframe|//object|//embed|//form|//link|//meta|//img|//video|//audio|//source'):
        node.drop_tree()
    for node in tree.iter():
        for attribute in list(node.attrib):
            if attribute.lower().startswith('on') or attribute.lower() in ('src', 'srcdoc', 'style'):
                del node.attrib[attribute]
        if node.text:
            node.text = re.sub(r'\s[–—]\s', ' - ', node.text)
        if node.tail:
            node.tail = re.sub(r'\s[–—]\s', ' - ', node.tail)
    return lh.tostring(tree, encoding='unicode')


def session_cookies(path):
    if not path:
        raise ConnectorError('authentication_required', 'No private LinkedIn session file is configured. Supply permitted profile HTML or configure HUGIN_LINKEDIN_SESSION_FILE.')
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor) as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 100_000:
                raise ConnectorError('unsupported', 'LinkedIn session must be an owner-only regular file (mode 0600), bounded to 100 KB.')
            state = json.load(source)
    except (OSError, ValueError):
        raise ConnectorError('authentication_required', 'Cannot load the configured private LinkedIn session.') from None
    if not isinstance(state, dict) or not isinstance(state.get('cookies'), list):
        raise ConnectorError('unsupported', 'LinkedIn session is not Playwright storage-state JSON.')
    cookies = requests.cookies.RequestsCookieJar()
    for cookie in state['cookies']:
        if not isinstance(cookie, dict) or cookie.get('domain') not in ('.linkedin.com', 'linkedin.com', 'www.linkedin.com'):
            continue
        expiry = cookie.get('expires', -1)
        if not isinstance(expiry, (int, float)) or (expiry != -1 and expiry <= time.time()) or not cookie.get('secure'):
            continue
        if not isinstance(cookie.get('name'), str) or not isinstance(cookie.get('value'), str):
            continue
        cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie.get('path', '/'), secure=True)
    if not any(cookie.name == 'li_at' for cookie in cookies):
        raise ConnectorError('authentication_required', 'LinkedIn session has no unexpired secure authentication cookie.')
    return cookies


def observations(contact, url, parsed, retrieved_at):
    name = parsed.get('name', '')
    if not name or name == 'Unknown':
        return []
    current = [row for row in parsed.get('experiences', []) if str(row.get('to_date', '')).casefold() == 'present']
    company = current[0].get('institution_name') if len(current) == 1 else None
    match = identity(contact, {'name': name, 'worksFor': {'name': company or ''}}, url)
    if match['confidence'] == 'rejected':
        return [{'kind': 'rejected_identity', 'value': 'Profile describes a different person', 'url': url, 'excerpt': name[:200], 'identity': match, 'provider': 'linkedin', 'retrieved_at': retrieved_at}]
    values = [('biography', parsed.get('about'), None), ('professional_headline', parsed.get('headline'), None)]
    if len(current) == 1:
        values.extend([('company', company, None), ('job_title', current[0].get('position_title'), None)])
    for row in parsed.get('experiences', [])[:20]:
        values.append(('employment_history', ' | '.join(str(row.get(k) or '') for k in ('position_title', 'institution_name', 'from_date', 'to_date')).strip(' |'), row.get('from_date')))
    for row in parsed.get('educations', [])[:10]:
        values.append(('education', ' | '.join(str(row.get(k) or '') for k in ('institution_name', 'degree', 'from_date', 'to_date')).strip(' |'), row.get('from_date')))
    return [{'kind': kind, 'value': value[:1200], 'url': url, 'excerpt': f'{name}: {value}'[:500], 'identity': match, 'provider': 'linkedin', 'retrieved_at': retrieved_at, 'event_date': date}
            for kind, value, date in values if isinstance(value, str) and value.strip()]


class LinkedInSource:
    def __init__(self, settings, store, public):
        self.settings, self.store, self.public = settings, store, public

    def status(self):
        return {'status': 'configured_unverified' if self.settings.linkedin_session_file else 'authentication_required', 'parser': 'installed_unverified' if Path(self.settings.linkedin_python).is_file() else 'not_installed', 'html_import': 'available', 'live_verified': False, 'revision': REVISION}

    def acquire(self, url, budget):
        cookies = session_cookies(self.settings.linkedin_session_file)
        self.public.validate_url(url)
        _, rules = self.public.get('https://www.linkedin.com/robots.txt', budget)
        robots = RobotFileParser(); robots.parse(rules.splitlines())
        if not robots.can_fetch('HuginResearch', url):
            raise ConnectorError('unsupported', 'LinkedIn robots policy disallows automated retrieval. An authorized session does not override it; permitted profile HTML can be imported.')
        self.public.validate_url(url)
        budget.take()
        try:
            # Inherited HTTPS proxy and CA trust are honored. No browser egress.
            with requests.Session() as transport:
                transport.cookies = cookies
                transport.headers['User-Agent'] = 'HuginResearch/1.0 (private professional research)'
                with transport.get(url, timeout=budget.timeout(), stream=True, allow_redirects=False) as response:
                    if response.status_code in (301, 302, 303, 307, 308, 401, 403):
                        raise ConnectorError('authentication_required', 'LinkedIn denied or redirected access; no login or challenge was bypassed.')
                    if response.status_code in (429, 999):
                        raise ConnectorError('quota_exhausted', 'LinkedIn blocked or limited retrieval.')
                    if response.status_code == 404:
                        raise ConnectorError('no_result', 'LinkedIn profile was not found.')
                    if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                        raise ConnectorError('unsupported', 'LinkedIn did not return supported profile HTML.')
                    content = bytearray()
                    for chunk in response.iter_content(8192):
                        budget.timeout(); content.extend(chunk)
                        if len(content) > MAX_HTML:
                            raise ConnectorError('unsupported', 'Profile HTML exceeded its one-megabyte bound.')
                    return content.decode(response.encoding or 'utf-8', errors='replace')
        except requests.Timeout:
            raise ConnectorError('timeout', 'LinkedIn retrieval timed out.') from None
        except requests.RequestException:
            raise ConnectorError('unavailable', 'Cannot reach LinkedIn through the configured network.') from None

    def page(self, contact, budget, supplied_html=None):
        url = profile_url(contact.get('linkedin', ''))
        python = self.settings.linkedin_python
        if not Path(python).is_file():
            raise ConnectorError('unsupported', 'Install the pinned LinkedIn worker with scripts/install-linkedin.sh.')
        key = fingerprint({'revision': REVISION, 'parser': 1, 'contact': contact, 'url': url, 'input': fingerprint(supplied_html) if supplied_html is not None else 'session'})
        cached = self.store.get('source_cache', key)
        if cached and time.time() - cached['cached_at'] < 86400:
            return cached['observations'], True, cached['coverage'], cached['retrieved_at']
        document = supplied_html if supplied_html is not None else self.acquire(url, budget)
        clean = inspect_html(document, url)
        budget.timeout()
        worker = Path(__file__).with_name('linkedin_worker.py')
        try:
            process = run_worker(python, worker, {'html': clean, 'chromium': self.settings.linkedin_chromium}, budget.timeout())
            parsed = json.loads(process.stdout)
            if process.returncode or parsed.get('error'):
                raise ConnectorError('unsupported', 'LinkedIn parser could not extract a supported profile. No upstream diagnostics were logged.')
        except subprocess.TimeoutExpired:
            raise ConnectorError('timeout', 'LinkedIn parser exceeded its time bound.') from None
        except (OSError, ValueError):
            raise ConnectorError('unsupported', 'LinkedIn parser is unavailable or returned an unsupported response.') from None
        retrieved_at = now()
        rows = observations(contact, url, parsed, retrieved_at)
        if supplied_html is not None:
            for row in rows:
                row['provider_review_status'] = 'pending'
                row['evidence_origin'] = 'user_supplied_html'
        else:
            for row in rows:
                row['evidence_origin'] = 'session_retrieval'
        coverage = parsed.get('coverage', {})
        self.store.put('source_cache', key, {'observations': rows, 'coverage': coverage, 'retrieved_at': retrieved_at, 'cached_at': time.time()})
        return rows, False, coverage, retrieved_at
