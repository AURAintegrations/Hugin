from contextlib import asynccontextmanager
from pathlib import Path
import ipaddress
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .config import Settings, ConnectorError
from .dex import DexMCP, FixtureDex
from .engine import Engine, SelectionError
from .models import EnrichRequest
from .sources import PublicSources, SOURCE_REGISTRY
from .store import FixtureStore, MongoStore


def create_app(settings=None, store=None, dex=None, start_worker=True):
    settings = settings or Settings()
    store = store or (FixtureStore(settings.fixture_store) if settings.mode == 'fixture' else MongoStore(settings))
    fixture = json.loads((Path(__file__).parent / 'fixtures/demo.json').read_text()) if settings.mode == 'fixture' else None
    dex = dex or (FixtureDex(store, fixture) if fixture is not None else DexMCP(settings))
    engine = Engine(settings, store, dex, PublicSources(settings, store), fixture)

    @asynccontextmanager
    async def lifespan(app):
        # Fail startup truthfully if required storage is unavailable.
        store.ready()
        if start_worker:
            engine.start()
        yield
        engine.stop()
        store.close()

    app = FastAPI(title='Hugin Contact Intelligence', lifespan=lifespan)
    app.state.engine = engine
    app.state.store = store
    app.state.settings = settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', '[::1]'])
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.origins), allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

    @app.middleware('http')
    async def local_only(request: Request, call_next):
        try:
            local = bool(request.client and ipaddress.ip_address(request.client.host).is_loopback)
        except ValueError:
            local = False
        if not local:
            return JSONResponse({'detail': 'Local-only workspace. Remote use requires authentication and authorization.'}, status_code=403)
        # Block browser cross-origin mutations, including localhost CSRF via simple POSTs.
        origin = request.headers.get('origin')
        if origin and origin not in settings.origins:
            return JSONResponse({'detail': 'Origin is not permitted.'}, status_code=403)
        if request.method == 'POST' and request.headers.get('content-type', '').split(';')[0] != 'application/json':
            return JSONResponse({'detail': 'JSON content type required.'}, status_code=415)
        return await call_next(request)

    @app.exception_handler(ConnectorError)
    async def connector_error(request, error):
        code = 409 if error.outcome in ('conflict', 'ambiguous_identity') else 503
        return JSONResponse({'detail': {'outcome': error.outcome, 'message': error.message}}, status_code=code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        # Pydantic's default response may echo the submitted profile/private input.
        return JSONResponse({'detail': 'Invalid request fields or enrichment options.'}, status_code=422)

    @app.get('/api/health')
    def health():
        try:
            store.ready()
        except Exception:
            raise HTTPException(503, 'Required storage unavailable.') from None
        return {'status': 'ok', 'mode': settings.mode, 'access': 'local_only', 'dex': 'fixture' if fixture is not None else 'configured_unverified' if settings.dex_key else 'authentication_required'}

    @app.get('/api/integrations')
    def integrations():
        return {'mode': settings.mode, 'access': 'local_only', 'sources': SOURCE_REGISTRY, 'api_anything': {**engine.api_anything.status(), **({'status': 'fixture'} if fixture is not None else {})}, 'linkedin': {**engine.linkedin.status(), 'status': 'fixture' if fixture is not None else engine.linkedin.status()['status']}, 'dex': {'transport': 'server-side MCP bridge', 'endpoint': settings.dex_url, 'status': 'fixture' if fixture is not None else 'configured_unverified' if settings.dex_key else 'authentication_required'}, 'brave': {'status': 'fixture' if fixture is not None else 'configured_unverified' if settings.brave_key else 'authentication_required'}, 'public_pages': {'allowed_hosts': list(settings.source_hosts), 'status': 'fixture' if fixture is not None else 'configured' if settings.source_hosts else 'not_configured'}}

    @app.get('/api/contacts')
    def contacts(q: str = ''):
        if len(q) > 200:
            raise HTTPException(422, 'Search query is too long.')
        from .engine import contact_anchor
        rows = [contact_anchor(c) for c in dex.search(q)]
        # Search is bounded; never claim a complete Dex database listing.
        return {'items': rows, 'mode': settings.mode, 'bounded': True, 'limit': 50}

    @app.get('/api/contacts/{contact_id}')
    def contact(contact_id: str):
        from .engine import contact_anchor
        return {'contact': contact_anchor(dex.contact(contact_id)), 'mode': settings.mode}

    @app.post('/api/enrichments', status_code=202)
    def submit(body: EnrichRequest):
        try:
            job, created = engine.submit(body)
        except SelectionError as error:
            raise HTTPException(409, {'outcome': 'selection_required', 'message': 'Choose one Dex contact ID; no research or writes have started.', 'candidates': error.candidates}) from None
        return {'job': job, 'created': created}

    @app.get('/api/enrichments')
    def jobs():
        return {'items': store.rows('jobs', 100), 'mode': settings.mode}

    @app.get('/api/enrichments/{job_id}')
    def job(job_id: str):
        row = store.get('jobs', job_id)
        if not row:
            raise HTTPException(404, 'Enrichment job not found.')
        return row

    @app.post('/api/enrichments/{job_id}/retry-sync', status_code=202)
    def retry(job_id: str):
        return {'job': engine.retry_sync(job_id)}

    @app.get('/api/evidence')
    def evidence(job_id: str | None = None):
        rows = store.rows('evidence', 500)
        return {'items': [row for row in rows if not job_id or row['job_id'] == job_id], 'mode': settings.mode}

    @app.get('/api/connections')
    def connections(job_id: str | None = None):
        rows = store.rows('relationships', 500)
        return {'items': [row for row in rows if not job_id or row['job_id'] == job_id], 'mode': settings.mode}

    @app.get('/api/account-candidates')
    def account_candidates(job_id: str | None = None):
        rows = store.rows('account_candidates', 500)
        return {'items': [row for row in rows if not job_id or row['job_id'] == job_id], 'mode': settings.mode}

    @app.get('/api/entity-snapshots')
    def entity_snapshots(contact_id: str | None = None):
        rows = store.rows('entity_snapshots', 500)
        return {'items': [row for row in rows if not contact_id or row['contact_id'] == contact_id], 'mode': settings.mode}

    return app
