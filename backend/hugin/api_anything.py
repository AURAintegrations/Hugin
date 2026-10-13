"""Reviewed API Anything operations with Hugin-owned, bounded HTTPS transport."""
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import json
import os
import re
import subprocess
import time
import unicodedata
from .config import ConnectorError
from .models import fingerprint, now
from .sources import full_name, identity

OPERATIONS = {
    'openalex': {'host': 'api.openalex.org', 'path': '/authors', 'name': 'OpenAlex author directory', 'reuse': 'CC0 metadata; identity attribution and upstream work rights remain separate.'},
    'europepmc': {'host': 'www.ebi.ac.uk', 'path': '/europepmc/webservices/rest/search', 'name': 'Europe PMC publications', 'reuse': 'Bibliographic metadata and short attribution only; no article/abstract redistribution rights inferred.'},
    'industry_news': {'host': 'hn.algolia.com', 'path': '/api/v1/search', 'name': 'Hacker News company mentions', 'reuse': 'Short story metadata for private review; third-party linked content retains its own rights.'},
}
REVISION = '0b556c36932b111ee8840c412008261abe717725'


def compact(value):
    value = unicodedata.normalize('NFKD', str(value).casefold())
    return re.sub(r'[^a-z0-9]', '', value)


class ApiAnythingSource:
    def __init__(self, settings, public, store):
        self.settings, self.public, self.store = settings, public, store

    def status(self):
        installed = Path(self.settings.api_anything_dir, 'dist/http.js').is_file()
        return {'status': 'configured_unverified' if installed else 'unsupported', 'version': '0.1.0', 'revision': REVISION,
                'transport': 'Hugin verified HTTPS; API Anything offline request/extraction worker',
                'operations': [{'id': k, **v} for k, v in OPERATIONS.items()]}

    def worker(self, action, source, budget, **payload):
        if not Path(self.settings.api_anything_dir, 'dist/http.js').is_file():
            raise ConnectorError('unsupported', 'API Anything is not installed. Run scripts/install-api-anything.sh.')
        try:
            result = subprocess.run([self.settings.api_anything_node, str(Path(__file__).with_name('api_anything_worker.mjs'))],
                                    input=json.dumps({'action': action, 'source': source, 'module_dir': self.settings.api_anything_dir, **payload}),
                                    text=True, capture_output=True, timeout=min(5, budget.timeout()),
                                    env={'PATH': os.environ.get('PATH', '/usr/bin:/bin')}, check=False)
            if len(result.stdout) > 200_000:
                raise ValueError
            data = json.loads(result.stdout)
            if result.returncode or data.get('error'):
                raise ValueError
            return data
        except subprocess.TimeoutExpired:
            raise ConnectorError('timeout', 'Offline API Anything worker exceeded its deadline.') from None
        except (OSError, ValueError, TypeError):
            raise ConnectorError('unsupported', 'API Anything version, operation or response could not be validated.') from None

    def collect(self, source, contact, budget, fixture=None):
        spec = OPERATIONS[source]
        name = full_name(contact)
        company = str(contact.get('company') or '').strip()
        if source == 'industry_news':
            if len(compact(company)) < 4:
                raise ConnectorError('not_searched', 'No specific company name is available for bounded news discovery.')
            query = company
        elif len(name.split()) < 2:
            raise ConnectorError('not_searched', 'A full professional name is required for author discovery.')
        else:
            # Europe PMC indexes authors as surname + initials. Retrieve a small
            # candidate set, then require full given/surname metadata below.
            query = 'AUTH:' + json.dumps(name.split()[-1] + ' ' + name[0]) if source == 'europepmc' else name
        # Requests contain only this query; the worker never receives private notes or keys.
        url = self.worker('build', source, budget, args={'query': query})['url']
        p = urlparse(url)
        if p.hostname != spec['host'] or p.path != spec['path'] or p.scheme != 'https' or p.username or p.password or p.port not in (None, 443) or p.fragment:
            raise ConnectorError('unsupported', 'Learned operation escaped its reviewed source endpoint.')
        operation_hash = fingerprint(json.loads((Path(__file__).parent / 'api_operations' / (source + '.json')).read_text()))
        key = fingerprint({'api_anything': source, 'normalizer': 1, 'operation': operation_hash, 'contact': contact, 'fixture': fixture is not None})
        cached = self.store.get('source_cache', key)
        if cached and time.time() - cached['cached_at'] < 86400:
            return cached['observations'], {**cached['details'], 'cache_hit': True}
        if fixture is not None:
            configured = fixture.get(source)
            if isinstance(configured, dict) and configured.get('error'):
                raise ConnectorError(configured['error'], 'Explicit synthetic API Anything source outcome.')
            if configured is None:
                raise ConnectorError('not_searched', 'No synthetic response was configured for this API Anything operation.')
            budget.take()
            body = json.dumps(configured)
        else:
            self.public.validate_url(url, (spec['host'],))
            try:
                _, rules = self.public.get('https://' + spec['host'] + '/robots.txt', budget, (spec['host'],))
            except ConnectorError as error:
                if error.outcome != 'no_result':
                    raise
                rules = ''
            robots = RobotFileParser(); robots.parse(rules.splitlines())
            if not robots.can_fetch('HuginResearch', url):
                raise ConnectorError('unsupported', 'API operation is disallowed by source robots policy.')
            _, body = self.public.get(url, budget, (spec['host'],), json_allowed=True)
        records = self.worker('extract', source, budget, body=body)['records']
        observations = normalize(source, contact, records, url)
        details = {'url': url, 'operation': source + ':search', 'operation_hash': operation_hash,
                   'api_anything_revision': REVISION, 'records_returned': len(records), 'cache_hit': False,
                   'acquisition': 'fixture' if fixture is not None else 'public_api'}
        # Provider-reported query cost is an estimate, not evidence of an owner charge.
        if source == 'openalex':
            estimate = json.loads(body).get('meta', {}).get('cost_usd')
            if isinstance(estimate, (float, int)) and not isinstance(estimate, bool) and estimate >= 0:
                details['provider_reported_query_cost_usd'] = estimate
        # Retain only the selected metadata that supports the readable evidence,
        # separately from notes; never keep response HTML, abstracts or full texts.
        self.store.put('api_metadata', key, {'source': source, 'url': url, 'operation_hash': operation_hash,
                       'retrieved_at': now(), 'records': [{'index': o['record_index'], 'excerpt': o['excerpt']} for o in observations]})
        self.store.put('source_cache', key, {'observations': observations, 'details': details, 'cached_at': time.time()})
        return observations, details


def normalize(source, contact, records, url):
    observations = []
    stamp = now()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ConnectorError('unsupported', 'API source record schema changed; no findings were accepted.')
        value, person, kind, event = None, {}, 'professional_profile', None
        supporting = {}
        if source == 'openalex':
            name, identifier = record.get('display_name'), record.get('id')
            institutions = record.get('last_known_institutions') or []
            if not isinstance(name, str) or not isinstance(identifier, str) or not re.fullmatch(r'https://openalex.org/A[0-9]+', identifier) or not isinstance(institutions, list):
                raise ConnectorError('unsupported', 'Author directory schema changed; results remain unsupported.')
            orgs = [v['display_name'] for v in institutions if isinstance(v, dict) and isinstance(v.get('display_name'), str)]
            company = next((v for v in orgs if compact(v) == compact(contact.get('company'))), orgs[0] if orgs else '')
            person = {'name': name, 'worksFor': {'name': company}, 'url': identifier, 'sameAs': [record.get('orcid') or '']}
            value = f'OpenAlex author candidate: {name[:150]}. Profile: {identifier}.'
            if orgs:
                value += ' Last listed institution(s): ' + '; '.join(orgs[:3])[:220] + '. Current role is unconfirmed.'
            supporting = {'display_name': name[:150], 'id': identifier, 'last_known_institutions': '; '.join(orgs[:3])[:220]}
        elif source == 'europepmc':
            title, authors = record.get('title'), (record.get('authorList') or {}).get('author', []) if isinstance(record.get('authorList'), dict) else []
            if not isinstance(title, str) or not isinstance(authors, list) or not record.get('id'):
                raise ConnectorError('unsupported', 'Publication metadata schema changed; results remain unsupported.')
            candidates = []
            for author in authors:
                if not isinstance(author, dict): continue
                candidate_name = ' '.join(v for v in [author.get('firstName'), author.get('lastName')] if isinstance(v, str))
                affiliations = (author.get('authorAffiliationDetailsList') or {}).get('authorAffiliation', []) if isinstance(author.get('authorAffiliationDetailsList'), dict) else []
                affiliation = next((v.get('affiliation', '') for v in affiliations if isinstance(v, dict) and str(contact.get('company') or '').casefold() in str(v.get('affiliation') or '').casefold()), '') if contact.get('company') else ''
                # An affiliation string is retained as text, not a current-role claim.
                candidates.append({'name': candidate_name, 'worksFor': {'name': str(contact.get('company') or '') if affiliation else ''}})
            person = next((a for a in candidates if compact(a['name']) == compact(full_name(contact))), {})
            if not person:
                continue  # Search response alone does not establish authorship.
            kind, event = 'publication', record.get('firstPublicationDate')
            event = event if isinstance(event, str) and re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?', event) else None
            value = f'Possible publication by {person["name"][:150]}: {title[:250]}'
            doi = record.get('doi')
            if isinstance(doi, str) and re.fullmatch(r'10\.\d{4,9}/[^\s<>"\\]+', doi):
                value += ' (https://doi.org/' + doi[:200] + ')'
            supporting = {'author_name': person['name'][:150], 'title': title[:250], 'id': str(record['id'])[:40], 'firstPublicationDate': event}
        else:
            title = record.get('title')
            if not isinstance(title, str) or not record.get('objectID'):
                raise ConnectorError('unsupported', 'News metadata schema changed; results remain unsupported.')
            company = compact(contact.get('company'))
            # Require the whole company phrase, not fuzzy search tokens or URL coincidence.
            phrase = r'(?<![a-z0-9])' + r'[^a-z0-9]*'.join(re.findall(r'[a-z0-9]+', str(contact.get('company') or '').casefold())) + r'(?![a-z0-9])'
            if len(company) < 4 or not re.search(phrase, title.casefold()) or not re.fullmatch(r'[0-9]+', str(record['objectID'])):
                continue
            kind = 'company_context'
            person = {'name': ''}
            value = f'Hacker News lists a company-name mention: {title[:250]} (https://news.ycombinator.com/item?id={str(record["objectID"])[:30]}). Organization match is unconfirmed.'
            event = record.get('created_at')
            event = event[:10] if isinstance(event, str) and re.match(r'^\d{4}-\d{2}-\d{2}T', event) else None
            supporting = {'title': title[:350], 'objectID': str(record['objectID']), 'created_at': event}
        # Accent variants support candidate matching, never automatic verification.
        name_anchor = {**contact, 'name': compact(full_name(contact))}
        match = identity(name_anchor, {**person, 'name': compact(person.get('name', ''))}, url)
        if source == 'industry_news':
            match = {'confidence': 'low', 'signals': ['company_name_in_news_title'], 'conflicts': []}
        observations.append({'kind': kind, 'value': value, 'url': url, 'provider': 'api_anything', 'retrieved_at': stamp,
                             'identity': match, 'provider_review_status': 'pending', 'event_date': event,
                             'subject_type': 'company' if kind == 'company_context' else 'person',
                             'excerpt': json.dumps(supporting, ensure_ascii=False)[:500],
                             'evidence_origin': 'api_anything_public_metadata', 'operation': source + ':search', 'record_index': index,
                             'api_anything_revision': REVISION})
    return observations
