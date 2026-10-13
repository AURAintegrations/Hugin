"""Server-side bridge to Dex's documented Streamable HTTP MCP service.
Contract reference: getdex/agent-skills@50c86c38 (2026-10-07 inspection).
No host connector credentials are assumed to exist in this process.
"""
from copy import deepcopy
import json
import time
import threading
import uuid
import requests
from .config import ConnectorError
from .sources import full_name


class DexMCP:
    def __init__(self, settings):
        self.key, self.url = settings.dex_key, settings.dex_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'dex-cli', 'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json'})
        if self.key:
            self.session.headers['Authorization'] = 'Bearer ' + self.key
        self.schemas = None
        self.connection_lock = threading.RLock()

    def _rpc(self, method, params, timeout=20, notification=False):
        if not self.key:
            raise ConnectorError('authentication_required', 'Set DEX_API_KEY securely in environment settings; Dex access requires an eligible plan.')
        deadline = time.monotonic() + timeout
        request_id = uuid.uuid4().hex
        payload = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if not notification:
            payload['id'] = request_id
        try:
            with self.session.post(self.url, json=payload, timeout=timeout, stream=True, allow_redirects=False) as response:
                if response.status_code in (401, 403):
                    raise ConnectorError('authentication_required', 'Dex rejected access. Check the configured key, plan and network policy.')
                if response.status_code == 429:
                    raise ConnectorError('quota_exhausted', 'Dex rate limit reached; retry later.')
                if response.status_code >= 500:
                    raise ConnectorError('unavailable', 'Dex service is unavailable.')
                if response.status_code not in (200, 202, 204):
                    raise ConnectorError('unsupported', 'Dex rejected this MCP request; check the supported tool contract.')
                session_id = response.headers.get('Mcp-Session-Id')
                if session_id:
                    self.session.headers['Mcp-Session-Id'] = session_id
                if notification:
                    return {}
                if 'text/event-stream' in response.headers.get('Content-Type', ''):
                    total = 0
                    for line in response.iter_lines():
                        if time.monotonic() >= deadline:
                            raise ConnectorError('timeout', 'Dex stream deadline reached.')
                        total += len(line)
                        if total > 1_000_000:
                            raise ConnectorError('unsupported', 'Dex response exceeded the bounded response size.')
                        if line.startswith(b'data:'):
                            try:
                                body = json.loads(line[5:].strip())
                            except ValueError:
                                continue
                            if body.get('id') == request_id:
                                break
                    else:
                        raise ConnectorError('unsupported', 'Dex stream ended without a complete result.')
                else:
                    content = bytearray()
                    for chunk in response.iter_content(8192):
                        if time.monotonic() >= deadline:
                            raise ConnectorError('timeout', 'Dex response deadline reached.')
                        content.extend(chunk)
                        if len(content) > 1_000_000:
                            raise ConnectorError('unsupported', 'Dex response exceeded the bounded response size.')
                    body = json.loads(content)
        except requests.Timeout:
            raise ConnectorError('timeout', 'Dex request timed out; a remote write may still have completed.') from None
        except (requests.RequestException, ValueError):
            raise ConnectorError('unavailable', 'Cannot reach or decode Dex MCP. Check network access.') from None
        if body.get('error'):
            raise ConnectorError('unsupported', 'Dex reported an MCP protocol error.')
        return body.get('result', {})

    def connect(self):
        with self.connection_lock:
            if self.schemas is not None:
                return
            initialized = self._rpc('initialize', {'protocolVersion': '2025-03-26', 'capabilities': {}, 'clientInfo': {'name': 'hugin', 'version': '1.0.0'}})
            version = initialized.get('protocolVersion', '2025-03-26')
            if version not in ('2024-11-05', '2025-03-26', '2025-06-18'):
                raise ConnectorError('unsupported', 'Dex negotiated an unsupported MCP protocol version.')
            self.session.headers['MCP-Protocol-Version'] = version
            self._rpc('notifications/initialized', {}, notification=True)
            schemas = {}
            cursor = None
            for _ in range(5):
                response = self._rpc('tools/list', {'cursor': cursor} if cursor else {})
                schemas.update({tool['name']: tool.get('inputSchema', {}) for tool in response.get('tools', [])})
                cursor = response.get('nextCursor')
                if not cursor:
                    self.schemas = schemas
                    return
            raise ConnectorError('unsupported', 'Dex tool discovery exceeded its pagination bound.')

    def call(self, name, arguments, timeout=20):
        self.connect()
        schema = self.schemas.get(name)
        if schema is None:
            raise ConnectorError('unsupported', f'Dex tool {name} is not available on this account.')
        properties = schema.get('properties', {})
        if any(key not in properties for key in arguments):
            raise ConnectorError('unsupported', f'Dex tool {name} does not support the required safe parameters.')
        read_only = name in ('dex_search_contacts', 'dex_get_contact', 'dex_get_contact_research', 'dex_list_notes', 'dex_get_note')
        deadline = time.monotonic() + timeout
        for attempt in range(2 if read_only else 1):
            try:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ConnectorError('timeout', 'Dex operation deadline reached.')
                result = self._rpc('tools/call', {'name': name, 'arguments': arguments}, timeout=remaining)
                break
            except ConnectorError as error:
                if not read_only or attempt == 1 or error.outcome not in ('unavailable', 'timeout'):
                    raise
                time.sleep(min(0.1, max(0, deadline - time.monotonic())))

        if result.get('isError'):
            # Never reflect an opaque upstream error body into logs/UI.
            raise ConnectorError('provider_error', f'Dex tool {name} failed. Check account access and supported parameters.')
        if 'structuredContent' in result:
            return result['structuredContent']
        for block in result.get('content', []):
            if block.get('type') == 'text':
                try:
                    return json.loads(block['text'])
                except ValueError:
                    continue
        raise ConnectorError('unsupported', 'Dex returned an unstructured result; no changes will be assumed successful.')

    def search(self, query):
        return self.call('dex_search_contacts', {'query': query, 'limit': 50}).get('items', [])

    def contact(self, contact_id):
        result = self.call('dex_get_contact', {'id': contact_id, 'fields': ['contact_emails', 'related_contacts']})
        contact = result.get('contact', result)
        if contact.get('id') != contact_id:
            raise ConnectorError('ambiguous_identity', 'Dex returned a different or missing contact ID.')
        return contact

    def cached(self, contact_id):
        result = self.call('dex_get_contact_research', {'contact_ids': [contact_id]})
        rows = result.get('items', [])
        for row in rows:
            if row.get('contact_id', row.get('id')) == contact_id:
                return row.get('research')
        if rows:
            raise ConnectorError('ambiguous_identity', 'Cached Dex research was not bound to the selected ID.')
        return None

    def fresh(self, contact_id, timeout):
        # Never force and never retry a paid request automatically.
        result = self.call('dex_research_contacts', {'contact_ids': [contact_id], 'force': False}, timeout=timeout)
        for row in result.get('items', []):
            if row.get('contact_id', row.get('id')) == contact_id:
                if row.get('outcome') != 'ok':
                    raise ConnectorError(row.get('outcome', 'provider_error'), 'Dex research did not return completed research. Read the cache later; do not blindly rerun.')
                return row.get('research')
        raise ConnectorError('no_result', 'Dex research returned no matching contact.')

    @staticmethod
    def normalize_note(result):
        # Dex timeline rows use `note` for the body and nested association rows.
        note = result.get('note', result)
        if not isinstance(note, dict):
            note = result
        note = deepcopy(note)
        if 'content' not in note and isinstance(note.get('note'), str):
            note['content'] = note['note']
        if 'contact_ids' not in note:
            associations = note.get('timeline_items_contacts') or []
            note['contact_ids'] = [row['contact_id'] for row in associations if isinstance(row, dict) and row.get('contact_id')]
        return note

    def find_note(self, contact_id, marker):
        cursor = None
        deadline = time.monotonic() + 60
        for _ in range(20):
            if time.monotonic() >= deadline:
                raise ConnectorError('timeout', 'Note verification deadline reached; refusing a possibly duplicate write.')
            arguments = {'contact_id': contact_id, 'limit': 50, 'include_contacts': True}
            if cursor:
                arguments['cursor'] = cursor
            response = self.call('dex_list_notes', arguments)
            for note in response.get('items', []):
                note = self.normalize_note(note)
                if marker in note.get('content', ''):
                    return note
            if not response.get('has_more'):
                return None
            cursor = response.get('next_cursor')
            if not cursor:
                break
        raise ConnectorError('unsupported', 'Note history exceeded the safe verification bound; refusing a possibly duplicate write.')

    def create_note(self, contact_id, content, event_time, key):
        result = self.call('dex_create_note', {'contact_ids': [contact_id], 'content': content, 'event_time': event_time, 'idempotency_key': key, 'include_contacts': True})
        return self.normalize_note(result)

    def get_note(self, note_id):
        result = self.call('dex_get_note', {'note_id': note_id, 'include_contacts': True})
        return self.normalize_note(result)

    def update_missing(self, contact_id, fields):
        if fields:
            self.call('dex_update_contact', {'id': contact_id, **fields})

    def add_related(self, contact_id, ids):
        if ids:
            self.call('dex_add_related_contacts', {'contact_id': contact_id, 'contact_ids': ids})


class FixtureDex:
    """Local simulation with persisted writes, never a live Dex response."""
    def __init__(self, store, fixture):
        self.store = store
        self.fixture = fixture
        for contact in fixture['contacts']:
            if store.get('fixture_contacts', contact['id']) is None:
                store.put('fixture_contacts', contact['id'], contact)
        self.fail_write = False
        self.fail_after_write = False
        self.fresh_calls = 0

    def search(self, query):
        return [c for c in self.store.rows('fixture_contacts', 100) if query.lower() in (full_name(c) + ' ' + json.dumps(c)).lower()][:50]

    def contact(self, contact_id):
        result = self.store.get('fixture_contacts', contact_id)
        if not result:
            raise ConnectorError('no_result', 'Fixture contact not found.')
        return result

    def cached(self, contact_id):
        return deepcopy(self.fixture.get('research', {}).get(contact_id))

    def fresh(self, contact_id, timeout):
        self.fresh_calls += 1
        return self.cached(contact_id)

    def find_note(self, contact_id, marker):
        return next((n for n in self.store.rows('fixture_notes', 1000) if contact_id in n['contact_ids'] and marker in n['content']), None)

    def create_note(self, contact_id, content, event_time, key):
        if self.fail_write:
            raise ConnectorError('timeout', 'Fixture-only injected sync timeout.')
        existing = self.store.get('fixture_notes', key)
        if existing:
            return existing
        note = {'id': key, 'content': content, 'event_time': event_time, 'contact_ids': [contact_id]}
        self.store.put('fixture_notes', key, note)
        if self.fail_after_write:
            raise ConnectorError('timeout', 'Fixture-only injected timeout after persisted write.')
        return note

    def get_note(self, note_id):
        return self.store.get('fixture_notes', note_id)

    def update_missing(self, contact_id, fields):
        contact = self.contact(contact_id)
        contact.update(fields)
        self.store.put('fixture_contacts', contact_id, contact)

    def add_related(self, contact_id, ids):
        contact = self.contact(contact_id)
        contact['related_contacts'] = sorted(set(contact.get('related_contacts', []) + ids))
        self.store.put('fixture_contacts', contact_id, contact)
