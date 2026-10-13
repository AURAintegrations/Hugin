"""One CLI invocation starts, waits for and reports a single-contact enrichment job."""
import json
from pathlib import Path
import time
from urllib.parse import urlparse
import requests
import typer
from .models import EnrichRequest
from .engine import TERMINAL
from .sources import full_name

app = typer.Typer(no_args_is_help=True)


def api_request(base, method, path, body=None):
    if urlparse(base).hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise typer.BadParameter('This prototype supports a local-only API.')
    try:
        response = requests.request(method, base.rstrip('/') + '/api' + path, json=body, timeout=30)
    except requests.RequestException:
        typer.echo('Cannot reach Hugin. Start the local backend; no operation is assumed successful.', err=True)
        raise typer.Exit(1) from None
    if response.status_code >= 400:
        typer.echo(json.dumps(response.json(), indent=2), err=True)
        raise typer.Exit(1)
    return response.json()


def wait_job(base, job, wait_seconds):
    deadline = time.monotonic() + wait_seconds
    while job['state'] not in TERMINAL and time.monotonic() < deadline:
        time.sleep(0.5)
        job = api_request(base, 'GET', '/enrichments/' + job['id'])
    report = {k: job[k] for k in ('id', 'mode', 'state', 'stage', 'created_at', 'costs', 'findings', 'evidence', 'relationships', 'proposals', 'sync', 'editorial')}
    report['contact'] = {'id': job['contact']['id'], 'name': full_name(job['contact'])}
    if job.get('note'):
        report['note'] = job['note']
    if job.get('error'):
        report['error'] = job['error']
    report['outcomes'] = job['outcomes']
    report['research_scope'] = job.get('research_scope')
    report['account_candidates'] = job.get('account_candidates', [])
    typer.echo(json.dumps(report, indent=2))
    if job['state'] not in ('completed', 'dry_run'):
        raise typer.Exit(2)


@app.command()
def enrich(
    dex_contact_id: str = typer.Option(None, '--dex-contact-id'),
    query: str = typer.Option(None),
    dry_run: bool = typer.Option(False),
    fill_missing: bool = typer.Option(False),
    sources: str = typer.Option('dex_cached,company_web,api_anything,linkedin,public_discovery,maigret,public_pages'),
    company_url: list[str] = typer.Option(None, '--company-url', help='Optional company website candidate; does not prove personal affiliation.'),
    linkedin_html_file: Path = typer.Option(None, '--linkedin-html-file', help='Permitted saved profile HTML; parsed offline, never executed.'),
    job_key: str = typer.Option(None),
    paid_budget_units: int = typer.Option(0),
    allow_fresh_dex: bool = typer.Option(False),
    timeout_seconds: int = typer.Option(90),
    wait_seconds: int = typer.Option(240),
    api: str = typer.Option('http://127.0.0.1:8001'),
):
    """Research and save a cited note. Ambiguous queries return choices without writing."""
    try:
        document = None
        if linkedin_html_file is not None:
            with linkedin_html_file.open('rb') as source:
                data = source.read(1_000_001)
            if len(data) > 1_000_000:
                raise ValueError
            document = data.decode('utf-8')
        body = EnrichRequest(dex_contact_id=dex_contact_id, query=query, dry_run=dry_run, write_policy='fill_missing' if fill_missing else 'notes_only', sources=[s.strip() for s in sources.split(',')], company_urls=company_url or [], linkedin_html=document, idempotency_key=job_key, paid_budget_units=paid_budget_units, allow_fresh_dex=allow_fresh_dex, timeout_seconds=timeout_seconds)
    except (ValueError, OSError):
        typer.echo('Invalid enrichment options or profile HTML file. Use a UTF-8 file under one megabyte and include the linkedin source.', err=True)
        raise typer.Exit(1) from None
    result = api_request(api, 'POST', '/enrichments', body.model_dump())
    wait_job(api, result['job'], wait_seconds)


@app.command('retry-sync')
def retry_sync(job_id: str, api: str = 'http://127.0.0.1:8001', wait_seconds: int = 120):
    """Retry only saved writeback. Does not rerun research or paid providers."""
    result = api_request(api, 'POST', '/enrichments/' + job_id + '/retry-sync', {})
    wait_job(api, result['job'], wait_seconds)


@app.command()
def contacts(query: str = '', api: str = 'http://127.0.0.1:8001'):
    typer.echo(json.dumps(api_request(api, 'GET', '/contacts?' + requests.compat.urlencode({'q': query})), indent=2))


if __name__ == '__main__':
    app()
