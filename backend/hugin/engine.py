"""Durable staged jobs; research checkpoints and sync receipts have separate retry paths."""
from copy import deepcopy
import threading
import time
import uuid
from urllib.parse import urlparse
from .config import ConnectorError
from .models import now, fingerprint, EnrichRequest
from .collectors import maigret_candidates
from .entities import snapshot
from .linkedin import LinkedInSource, inspect_html, profile_url
from .api_anything import ApiAnythingSource, OPERATIONS
from .company import collect as collect_company
from .sources import Budget, SOURCE_REGISTRY, canonical, dex_observations, full_name, linkedin_url, page_observations

TERMINAL = {'completed', 'dry_run', 'no_results', 'sync_failed', 'failed'}
ANCHOR_FIELDS = ('id', 'name', 'first_name', 'last_name', 'company', 'job_title', 'linkedin', 'website', 'contact_emails', 'emails', 'related_contacts')


class SelectionError(Exception):
    def __init__(self, candidates):
        self.candidates = candidates


def contact_anchor(contact):
    return {k: deepcopy(contact[k]) for k in ANCHOR_FIELDS if k in contact}


def linked_ids(value):
    result = set()
    for row in value or []:
        if isinstance(row, str):
            result.add(row)
        elif isinstance(row, dict):
            target = row.get('related_contact', row.get('contact', row))
            key = target.get('id') if isinstance(target, dict) else None
            if key:
                result.add(key)
    return result


def note_contact_ids(note):
    result = set(note.get('contact_ids') or [])
    if note.get('contact_id'):
        result.add(note['contact_id'])
    for row in note.get('contacts', []) or note.get('notes_contacts', []):
        if isinstance(row, dict):
            key = row.get('contact_id') or (row.get('contact') or {}).get('id') or row.get('id')
            if key:
                result.add(key)
    return result


class Engine:
    def __init__(self, settings, store, dex, public, fixture=None):
        self.settings, self.store, self.dex, self.public = settings, store, dex, public
        self.fixture = fixture
        self.linkedin = LinkedInSource(settings, store, public)
        self.api_anything = ApiAnythingSource(settings, public, store)
        self.stop_event = threading.Event()
        self.threads = []

    def submit(self, request: EnrichRequest):
        if request.dex_contact_id:
            contact = self.dex.contact(request.dex_contact_id)
        else:
            candidates = self.dex.search(request.query)
            if len(candidates) != 1:
                raise SelectionError([contact_anchor(c) for c in candidates])
            contact = self.dex.contact(candidates[0]['id'])
        anchor = contact_anchor(contact)
        options = request.model_dump(exclude={'query', 'idempotency_key', 'linkedin_html'})
        if request.linkedin_html is not None:
            clean_html = inspect_html(request.linkedin_html, profile_url(anchor.get('linkedin', '')))
            options['linkedin_input_hash'] = fingerprint(clean_html)
        options['dex_contact_id'] = contact['id']
        spec = fingerprint({'options': options, 'mode': self.settings.mode})
        # The default is one operation per contact/options/day. Explicit keys support durable project retries.
        key = request.idempotency_key or f'{contact["id"]}:{now()[:10]}:{spec[:16]}'
        job = {'id': str(uuid.uuid4()), 'request_key': key, 'spec_hash': spec, 'mode': self.settings.mode, 'contact': anchor, 'options': options, 'state': 'queued', 'stage': 'queued', 'created_at': now(), 'updated_at': now(), 'lease_until': 0, 'lease_owner': None, 'research_complete': False, 'outcomes': [], 'observations': [], 'findings': [], 'evidence': [], 'relationships': [], 'proposals': [], 'sync': {'status': 'not_attempted'}, 'costs': {'paid_attempts': 0, 'requests': 0, 'currency_amount': None}, 'editorial': {'type': 'precision copy', 'venue': 'private contact research', 'status': 'pending'}}
        if request.linkedin_html is not None:
            self.store.put('source_inputs', job['id'], {'html': clean_html})
        existing, created = self.store.create_job(job)
        if not created:
            self.store.delete('source_inputs', job['id'])
        if existing['spec_hash'] != spec:
            raise ConnectorError('conflict', 'This idempotency key belongs to different options. Use the original options or a new key.')
        self.store.put('contacts', contact['id'], anchor)
        return existing, created

    def save(self, job):
        job['updated_at'] = now()
        job['lease_until'] = time.time() + 240
        self.store.update_job(job, job.get('lease_owner'))

    def outcome(self, job, source, status, message, **extra):
        row = {'id': fingerprint({'job': job['id'], 'source': source}), 'job_id': job['id'], 'source': source, 'outcome': status, 'message': message, 'retrieved_at': now(), **extra}
        job['outcomes'].append(row)
        self.store.put('source_outcomes', row['id'], row)
        self.save(job)

    def collect(self, job):
        options = job['options']
        def checkpoint(paid):
            job['costs']['requests'] += 1
            if paid:
                job['costs']['paid_attempts'] += 1
            self.save(job)
        budget = Budget(max(0, options['max_requests'] - job['costs']['requests']), options['timeout_seconds'], max(0, options['paid_budget_units'] - job['costs']['paid_attempts']), checkpoint)

        done = {r['source'] for r in job['outcomes']}
        requested = set(options['sources'])
        contact = job['contact']
        # Outcomes are explicit even for sources omitted from the selection.
        for source in ('dex_cached', 'dex_fresh', 'company_web', 'api_anything', 'linkedin', 'public_discovery', 'maigret', 'brave', 'public_pages'):
            if source not in requested and source not in done:
                self.outcome(job, source, 'not_searched', 'Not selected for this run.')
        for source in ('dex_cached', 'dex_fresh'):
            if source not in requested or source in done:
                continue
            job['stage'] = source
            self.save(job)
            try:
                if source == 'dex_fresh':
                    if job.get('fresh_requested'):
                        budget.take()
                        research = self.dex.cached(contact['id'])
                        if not research:
                            raise ConnectorError('in_progress', 'Previous paid request may still be running. Use cached research later; a fresh request will not be repeated for this job.')
                    else:
                        budget.take(paid=True)
                        job['fresh_requested'] = True
                        self.save(job)  # Persist before the external paid call.
                        research = self.dex.fresh(contact['id'], min(budget.deadline - time.monotonic(), options['timeout_seconds']))
                else:
                    budget.take()
                    research = self.dex.cached(contact['id'])
                observations = dex_observations(contact, research)
                for observation in observations:
                    observation['provider'] = source
                    observation['retrieved_at'] = now()
                job['observations'].extend(observations)
                if research:
                    # Preserve permitted structured research separately; never overwrite older runs.
                    self.store.put('provider_research', job['id'] + ':' + source, {'job_id': job['id'], 'provider': source, 'research': research, 'retrieved_at': now()})
                self.outcome(job, source, 'ok' if observations else 'no_result', 'Cited research read.' if observations else 'No usable cited research was returned.', count=len(observations))
            except ConnectorError as error:
                self.outcome(job, source, error.outcome, error.message)
            except (TypeError, ValueError, KeyError):
                self.outcome(job, source, 'unsupported', 'Provider research had an unsupported structured shape; no claims were accepted.')
        if 'company_web' in requested and 'company_web' not in done:
            job['stage'] = 'company_web'; self.save(job)
            try:
                rows, pages, cached = collect_company(self.public, self.store, contact, budget, options.get('company_urls', []), min(3, options['max_pages']), self.fixture.get('company_pages', {}) if self.fixture is not None else None)
                job['observations'].extend(rows)
                self.outcome(job, 'company_web', 'ok' if rows else 'no_result', 'Company context is separate from personal findings; affiliation and organization match remain unconfirmed.', count=len(rows), cache_hit=cached, pages=pages)
            except ConnectorError as error:
                self.outcome(job, 'company_web', error.outcome, error.message)
        if 'api_anything' in requested and 'api_anything' not in done:
            job['stage'] = 'api_anything'; self.save(job)
            for operation in OPERATIONS:
                source_id = 'api_anything:' + operation
                if source_id in done:
                    continue
                try:
                    rows, details = self.api_anything.collect(operation, contact, budget, self.fixture.get('api_anything', {}) if self.fixture is not None else None)
                    job['observations'].extend(rows)
                    status = 'ambiguous_identity' if rows and all(r['identity']['confidence'] == 'rejected' for r in rows) else 'ok' if rows else 'no_result'
                    self.outcome(job, source_id, status, 'Public metadata collected; author identity, organization matches and historical affiliations remain pending.' if rows else 'No matching professional metadata; search candidates were not promoted to facts.', count=len(rows), **details)
                except ConnectorError as error:
                    self.outcome(job, source_id, error.outcome, error.message)
                except (KeyError, TypeError, ValueError):
                    self.outcome(job, source_id, 'unsupported', 'API metadata had an unsupported shape; this operation was isolated.')
            count = sum(r.get('count', 0) for r in job['outcomes'] if r['source'].startswith('api_anything:'))
            self.outcome(job, 'api_anything', 'ok' if count else 'no_result', 'Reviewed public API operations completed; individual failures and skipped searches are listed separately.', count=count)
        if 'linkedin' in requested and 'linkedin' not in done:
            job['stage'] = 'linkedin'
            self.save(job)
            supplied = self.store.get('source_inputs', job['id'])
            try:
                document = supplied['html'] if supplied else None
                if options.get('linkedin_input_hash') and not supplied:
                    raise ConnectorError('unavailable', 'Submitted profile HTML is unavailable; no live fallback was attempted.')
                if self.fixture is not None and document is None:
                    document = self.fixture.get('linkedin_html')
                    if document is None:
                        raise ConnectorError('not_searched', 'No synthetic LinkedIn HTML is configured for this fixture.')
                rows, cached, coverage, stamp = self.linkedin.page(contact, budget, document)
                job['observations'].extend(rows)
                self.outcome(job, 'linkedin', 'ambiguous_identity' if rows and all(r['identity']['confidence'] == 'rejected' for r in rows) else 'ok' if rows else 'no_result', 'Professional profile parsed; identity and missing sections retained for review.', count=len(rows), cache_hit=cached, coverage=coverage, acquisition='supplied_html' if supplied else 'fixture' if self.fixture is not None else 'session', evidence_retrieved_at=stamp)
            except ConnectorError as error:
                self.outcome(job, 'linkedin', error.outcome, error.message)
            self.store.delete('source_inputs', job['id'])
        elif 'linkedin' in done:
            self.store.delete('source_inputs', job['id'])
        urls = [contact.get('website'), linkedin_url(contact.get('linkedin'))]
        # API search responses are evidence endpoints, not discovered person pages.
        urls += [o.get('url') for o in job['observations'] if o.get('provider') not in ('maigret', 'api_anything')]
        discovered_urls = []
        if 'public_discovery' in requested and 'public_discovery' not in done:
            try:
                if self.fixture is not None:
                    budget.take()
                    found, cached = self.fixture.get('discovery_urls', []), False
                else:
                    found, cached = self.public.discover(contact, budget)
                self.store.put('job_discovery_urls', job['id'], {'urls': found})
                self.outcome(job, 'public_discovery', 'ok' if found else 'no_result', 'Candidate URL discovery only; snippets are not findings.', cache_hit=cached, count=len(found))
            except ConnectorError as error:
                self.outcome(job, 'public_discovery', error.outcome, error.message)
        discovered = self.store.get('job_discovery_urls', job['id'])
        if discovered:
            discovered_urls = discovered['urls']
            urls.extend(discovered_urls)
        if 'maigret' in requested and 'maigret' not in done:
            try:
                if self.fixture is not None:
                    budget.take()
                    candidates, observations, cached = self.fixture.get('account_candidates', []), [], False
                else:
                    candidates, observations, cached = maigret_candidates(self.settings, self.public, self.store, contact, budget)
                job['account_candidates'] = candidates
                job['observations'].extend(observations)
                for candidate in candidates:
                    record = {**candidate, 'id': fingerprint({'job': job['id'], 'url': candidate['url']})[:24], 'job_id': job['id'], 'contact_id': contact['id']}
                    self.store.put('account_candidates', record['id'], record)
                self.outcome(job, 'maigret', 'ok' if candidates else 'no_result', 'Professional account candidates retained for identity review; a matching handle is not proof.', count=len(candidates), cache_hit=cached)
            except ConnectorError as error:
                self.outcome(job, 'maigret', error.outcome, error.message)
        if 'brave' in requested and 'brave' not in done:
            try:
                if self.fixture is not None:
                    budget.take(paid=True)
                    found, cached = self.fixture.get('search_urls', []), False
                else:
                    found, cached = self.public.search(contact, budget)
                urls.extend(found)
                self.store.put('job_search_urls', job['id'], {'urls': found})
                self.outcome(job, 'brave', 'ok' if found else 'no_result', 'URL discovery only; findings require page evidence.', cache_hit=cached, count=len(found))
            except ConnectorError as error:
                self.outcome(job, 'brave', error.outcome, error.message)
        else:
            prior = self.store.get('job_search_urls', job['id'])
            if prior:
                urls.extend(prior['urls'])
        if 'public_pages' in requested and 'public_pages' not in done:
            if self.fixture is not None:
                urls.extend(self.fixture.get('pages', {}).keys())
            urls = list(dict.fromkeys(u for u in urls if isinstance(u, str) and urlparse(u).scheme in ('http', 'https')))[:options['max_pages']]
            count = sum(int(r.get('count', 0)) for r in job['outcomes'] if r['source'].startswith('public_pages:'))
            for url in urls:
                outcome_id = 'public_pages:' + fingerprint(url)[:16]
                if outcome_id in done:
                    continue
                try:
                    if self.fixture is not None:
                        budget.take()
                        document = self.fixture.get('pages', {}).get(url)
                        if document is None:
                            raise ConnectorError('no_result', 'No fixture page exists for this URL.')
                        if isinstance(document, dict) and document.get('error'):
                            raise ConnectorError(document['error'], 'Fixture-only configured source outcome.')
                        observations, cached, retrieved_at = page_observations(contact, url, document), False, now()
                        for observation in observations:
                            observation['url'] = url
                    else:
                        observations, cached, retrieved_at = self.public.page(contact, url, budget, discovered=url in discovered_urls)
                    for observation in observations:
                        observation.update(provider='public_pages', retrieved_at=retrieved_at)
                    job['observations'].extend(observations)
                    count += len(observations)
                    self.outcome(job, outcome_id, 'ok' if observations else 'no_result', 'Extracted bounded professional evidence.' if observations else 'No matching professional evidence.', url=url, cache_hit=cached, count=len(observations))
                except ConnectorError as error:
                    self.outcome(job, outcome_id, error.outcome, error.message, url=url)
                except (TypeError, ValueError, KeyError):
                    self.outcome(job, outcome_id, 'unsupported', 'Source returned malformed structured evidence; this page was isolated.', url=url)
            self.outcome(job, 'public_pages', 'ok' if count else 'no_result', 'Public page stage completed.', page_count=len(urls), count=count)
        self.save(job)

    def normalize(self, job):
        evidence, findings, relationships = [], [], []
        for index, observation in enumerate(job['observations']):
            match = observation['identity']
            evidence_id = fingerprint({'job': job['id'], 'observation': observation})[:24]
            source_url = observation.get('url', '')
            if urlparse(source_url).scheme not in ('http', 'https'):
                continue
            record = {'id': evidence_id, 'job_id': job['id'], 'contact_id': job['contact']['id'], 'url': source_url, 'provider': observation['provider'], 'retrieved_at': observation['retrieved_at'], 'event_date': observation.get('event_date'), 'excerpt': observation.get('excerpt', '')[:500], 'identity': match, 'evidence_origin': observation.get('evidence_origin', 'provider'), 'access_conditions': next(s['reuse'] for s in SOURCE_REGISTRY if s['id'] == observation['provider']), 'review_status': 'rejected' if match['confidence'] == 'rejected' else 'unreviewed'}
            evidence.append(record)
            if observation.get('operation'):
                record.update(operation=observation['operation'], api_anything_revision=observation['api_anything_revision'], record_index=observation['record_index'])
            record['subject_type'] = observation.get('subject_type', 'person')
            if match['confidence'] == 'rejected':
                continue
            status = 'verified' if match['confidence'] == 'high' else 'inferred' if match['confidence'] == 'medium' else 'unresolved'
            if observation['kind'] in ('email', 'phone') or observation.get('provider_review_status') == 'pending':
                status = 'unresolved'
            finding = {'id': fingerprint({'evidence': evidence_id, 'kind': observation['kind'], 'value': observation['value']})[:24], 'job_id': job['id'], 'contact_id': job['contact']['id'], 'kind': observation['kind'], 'value': observation['value'], 'evidence_ids': [evidence_id], 'identity_confidence': match['confidence'], 'status': status, 'review_status': 'pending', 'provider_review_status': observation.get('provider_review_status'), 'event_date': observation.get('event_date')}
            finding['subject_type'] = observation.get('subject_type', 'person')
            if finding['kind'] == 'relationship':
                finding['subject_identity_confidence'] = match['confidence']
                finding['target_identity_confidence'] = 'unresolved'
                finding['status'] = 'inferred' if status == 'verified' else status
                finding.update(relationship_type=observation.get('relationship_type', 'documented_association'), target_name=observation['value'], target_url=observation.get('target_url'), target_dex_id=None)
                relationships.append(finding)
            else:
                findings.append(finding)
        # Different scalar observations or a mismatch with existing CRM data remain conflicts.
        for kind in ('company', 'job_title', 'website', 'linkedin', 'email', 'phone'):
            group = [f for f in findings if f['kind'] == kind]
            existing = job['contact'].get(kind)
            values = {canonical(f['value']) if kind in ('website', 'linkedin') else f['value'].casefold().strip() for f in group}
            if existing:
                values.add(canonical(linkedin_url(existing) if kind == 'linkedin' else existing) if kind in ('website', 'linkedin') else str(existing).casefold().strip())
            if len(values) > 1:
                for finding in group:
                    finding['status'] = 'conflicting'
        # Relationship claims sharing a target but incompatible types are retained as conflicts.
        for relationship in relationships:
            if any(other['target_name'].casefold() == relationship['target_name'].casefold() and other['relationship_type'] != relationship['relationship_type'] for other in relationships):
                relationship['status'] = 'conflicting'
        proposals = []
        for finding in findings:
            if finding['kind'] not in ('website', 'linkedin', 'email', 'phone', 'company', 'job_title'):
                continue
            field = finding['kind']
            existing = job['contact'].get(field)
            eligible = field in ('website', 'linkedin') and not existing and finding['status'] == 'verified' and finding.get('provider_review_status') != 'pending' and urlparse(finding['value']).scheme == 'https'
            proposals.append({'id': finding['id'], 'finding_id': finding['id'], 'field': field, 'value': finding['value'], 'status': 'eligible' if eligible else 'pending', 'reason': 'Verified missing profile field.' if eligible else 'Existing, conflicting, unconfirmed or contact-method finding; preserved for review.'})
        job.update(evidence=evidence, findings=findings, relationships=relationships, proposals=proposals)
        job['research_scope'] = 'company_context_only' if findings and all(f['kind'] == 'company_context' for f in findings) and not relationships else 'personal_and_business' if findings or relationships else 'no_findings'
        for kind, rows in [('evidence', evidence), ('findings', findings), ('relationships', relationships), ('proposed_changes', proposals)]:
            for row in rows:
                self.store.put(kind, row['id'], {**row, 'job_id': job['id']})
        job['entity_snapshot'] = snapshot(job)
        self.store.put('entity_snapshots', job['id'], job['entity_snapshot'])
        job['note'] = self.render_note(job)
        job['editorial'] = {'type': 'precision copy', 'venue': 'private contact research', 'conservative_mode': True, 'status': 'main_skill_reviewed', 'scope': 'reviewed template; source excerpts unchanged', 'limitations': ['Humanizer supplemental references were unavailable.'], 'checks': ['Template prose reviewed against Humanizer main skill; claims and citation targets preserved.', 'Source excerpts kept verbatim; uncertainty retained.'], 'reviewed_at': now()}
        job['research_complete'] = True
        job['stage'] = 'research_complete'
        self.save(job)

    def render_note(self, job):
        label = 'FIXTURE / SIMULATED RESEARCH — no live sources or Dex writes' if self.settings.mode == 'fixture' else 'Hugin contact research'
        lines = [f'{label} | {job["created_at"][:10]}', f'Contact: {full_name(job["contact"])}', f'Hugin job: {job["id"]}', '', 'Findings (verified means matched to known professional identifiers, not independently audited):']
        refs = {}
        if job.get('research_scope') == 'company_context_only':
            lines.append('No new personal facts were confirmed. Company context follows; existing Dex affiliation is not reverified.')
        all_findings = job['findings'] + job['relationships']
        for finding in [f for f in all_findings if f['kind'] != 'company_context'] + [f for f in all_findings if f['kind'] == 'company_context']:
            if finding['kind'] == 'company_context' and not any(line.startswith('Company context:') for line in lines):
                lines.extend(['', 'Company context: cited source records only; these do not verify this contact’s affiliation.'])
            citations = []
            for evidence_id in finding['evidence_ids']:
                record = next(e for e in job['evidence'] if e['id'] == evidence_id)
                if evidence_id not in refs:
                    refs[evidence_id] = (len(refs) + 1, record)
                citations.append(f'[{refs[evidence_id][0]}]')
            lines.append(f'- [{finding["status"]}; identity {finding["identity_confidence"]}] {finding["kind"]}: {finding["value"]} {" ".join(citations)}')
        if not job['findings'] and not job['relationships']:
            lines.append('- No supported findings. No identity or relationship conclusions were drawn.')
        if job['proposals']:
            lines.extend(['', 'Field review:'])
            for proposal in job['proposals']:
                lines.append(f'- {proposal["field"]}: {proposal["status"]}. {proposal["reason"]}')
        lines.extend(['', 'Source outcomes:'])
        for outcome in job['outcomes']:
            lines.append(f'- {outcome["source"]}: {outcome["outcome"]}. {outcome["message"]}')
            if 'provider_reported_query_cost_usd' in outcome:
                lines.append(f'  Provider reported query-cost metric: USD {outcome["provider_reported_query_cost_usd"]}; this does not verify a billing charge.')
        lines.extend(['', 'Sources:'])
        for number, record in refs.values():
            event = f'; event date {record["event_date"]}' if record.get('event_date') else ''
            lines.append(f'[{number}] {record["url"]} (retrieved {record["retrieved_at"]}{event})')
        lines.extend(['', 'Follow-up suggestion (not a factual finding): review pending identity, relationship and field changes before acting.', f'Provider cost: {job["costs"]["paid_attempts"]} paid request attempt(s); actual currency charge is determined by the provider.'])
        return '\n'.join(lines)

    def sync(self, job):
        if not job['findings'] and not job['relationships']:
            job.update(state='no_results', stage='finished', sync={'status': 'not_attempted', 'message': 'No supported findings were collected. Nothing was written to Dex. Review source failures and configure another accessible source.'})
            self.store.put('sync_receipts', job['id'], {'job_id': job['id'], **job['sync']})
            self.save(job)
            return
        if job['options']['dry_run']:
            job.update(state='dry_run', stage='finished', sync={'status': 'dry_run', 'message': 'No Dex writes were attempted.'})
            self.save(job)
            return
        job.update(state='syncing', stage='dex_sync')
        self.save(job)
        receipt = job['sync']
        contact_id = job['contact']['id']
        marker = f'Hugin job: {job["id"]}'
        try:
            current = self.dex.contact(contact_id)
            before = contact_anchor(current)
            receipt['provider_or_external_changes'] = {k: current.get(k) for k in ('website', 'linkedin', 'company', 'job_title') if current.get(k) != job['contact'].get(k)}
            note = self.dex.find_note(contact_id, marker)
            if note is None:
                # Stable content/event_time/key persisted before the first write.
                receipt.setdefault('event_time', job['created_at'])
                receipt.setdefault('idempotency_key', 'hugin:' + job['id'])
                receipt['status'] = 'writing'
                self.save(job)
                note = self.dex.create_note(contact_id, job['note'], receipt['event_time'], receipt['idempotency_key'])
            note_id = note.get('id')
            if not note_id:
                raise ConnectorError('unsupported', 'Dex returned no note ID. The write remains unverified.')
            receipt['note_id'] = note_id
            self.save(job)
            verified_note = self.dex.get_note(note_id)
            if not verified_note or verified_note.get('content') != job['note'] or contact_id not in note_contact_ids(verified_note):
                raise ConnectorError('verification_failed', 'Dex note readback did not match the content and selected contact.')
            receipt['note_verified'] = True
            fields = {}
            for proposal in job['proposals']:
                if job['options']['write_policy'] == 'fill_missing' and proposal['status'] == 'eligible':
                    if current.get(proposal['field']):
                        proposal['sync_status'] = 'unchanged_existing'
                    else:
                        fields[proposal['field']] = proposal['value']
            if fields:
                receipt.setdefault('field_intent', {}).update(fields)
                self.save(job)
                self.dex.update_missing(contact_id, fields)
            after = self.dex.contact(contact_id)
            for field, value in fields.items():
                if after.get(field) != value:
                    raise ConnectorError('verification_failed', 'A proposed missing-field update did not match Dex readback.')
            # Detect populated-field drift. Dex has no conditional-update/CAS semantics; never claim atomicity.
            changed_existing = [k for k in ('company', 'job_title', 'linkedin', 'website') if before.get(k) and after.get(k) != before.get(k)]
            if changed_existing:
                raise ConnectorError('conflict', 'Populated fields changed during sync. Review Dex; Hugin will not restore or overwrite them.')
            verified_fields = {k: v for k, v in receipt.get('field_intent', {}).items() if after.get(k) == v}
            for proposal in job['proposals']:
                if verified_fields.get(proposal['field']) == proposal['value']:
                    proposal['sync_status'] = 'applied_verified'
                    self.store.put('proposed_changes', proposal['id'], {**proposal, 'job_id': job['id']})
            receipt.update(status='verified', verified_at=now(), additions={'note_id': note_id, 'fields': verified_fields, 'related_contact_ids': []}, pending_changes=[p for p in job['proposals'] if p.get('sync_status') != 'applied_verified'], unchanged_populated_fields=[k for k in ('company', 'job_title', 'linkedin', 'website') if before.get(k)], fixture=self.settings.mode == 'fixture')
            receipt.pop('outcome', None)
            receipt.pop('message', None)
            job.update(state='completed', stage='finished')
        except ConnectorError as error:
            receipt.update(status='failed', outcome=error.outcome, message=error.message)
            job.update(state='sync_failed', stage='dex_sync')
        self.store.put('sync_receipts', job['id'], {'job_id': job['id'], **receipt})
        self.save(job)

    def process(self, job):
        try:
            if not job['research_complete']:
                self.collect(job)
                self.normalize(job)
            self.sync(job)
        except ConnectorError as error:
            job.update(state='failed', stage='failed', error={'outcome': error.outcome, 'message': error.message})
            self.save(job)
        except Exception:
            # No exception strings: upstream bodies, URLs or credentials may appear there.
            job.update(state='failed', stage='failed', error={'outcome': 'internal_error', 'message': 'Unexpected pipeline error; research checkpoints are retained. Inspect sanitized diagnostics.'})
            self.save(job)
        finally:
            if job['state'] in TERMINAL:
                self.store.delete('source_inputs', job['id'])

    def retry_sync(self, job_id):
        job = self.store.get('jobs', job_id)
        if not job or not job['research_complete']:
            raise ConnectorError('conflict', 'No completed research is available to sync.')
        if job['state'] == 'no_results':
            raise ConnectorError('conflict', 'This run has no findings to sync. Select an accessible research source and start a new run.')
        if job['options']['dry_run']:
            raise ConnectorError('conflict', 'Dry-run jobs cannot be converted into writes; submit a research-and-save action.')
        if job['state'] == 'completed':
            return job
        if job['state'] not in ('sync_failed', 'failed'):
            raise ConnectorError('conflict', 'This job is already queued or running.')
        job.update(state='queued', stage='sync_retry', lease_until=0, lease_owner=None)
        self.store.update_job(job, job.get('lease_owner'), previous_states=('sync_failed', 'failed'))
        return job

    def worker(self):
        owner = uuid.uuid4().hex
        while not self.stop_event.is_set():
            try:
                job = self.store.claim(owner)
                if job:
                    self.process(job)
                    continue
            except Exception:
                # Database disconnection: jobs remain durable and become claimable after lease expiry.
                pass
            self.stop_event.wait(0.3)

    def start(self):
        for _ in range(self.settings.workers):
            thread = threading.Thread(target=self.worker, daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join(timeout=2)
