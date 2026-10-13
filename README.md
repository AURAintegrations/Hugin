# Hugin

Hugin researches one Dex contact, keeps the supporting evidence, and saves a dated, cited note to that same contact. A CLI command and a small local interface drive the same durable pipeline. Existing contact fields, descriptions, notes and relationships are preserved.

**Current verification:** the workspace has saved and verified a cited company-context note for the selected Dex contact. Personal biography, current role and relationships remain unconfirmed. API Anything now supplies three bounded public metadata searches; fixture tests verify their note writeback, and live source reads are verified separately. See [verification](docs/verification.md) and [API Anything integration](docs/api-anything.md) for results and limits.

## Install and start

Use Python 3.11+ (tested with 3.12), Node 20+ (tested with 24), Yarn Classic 1.22.22, and MongoDB 7/8. Keep the backend and frontend bound to loopback. The backend rejects remote client addresses, untrusted hosts, and unapproved browser origins. There is no fake login. Real authentication and authorization are required before remote deployment.

From the repository root:

```bash
python -m venv .venv
.venv/bin/pip install -e backend
bash scripts/install-collectors.sh
bash scripts/install-linkedin.sh
bash scripts/install-api-anything.sh
cp backend/.env.example backend/.env
# Edit backend/.env locally; never paste or commit keys.
cd frontend
yarn install --frozen-lockfile
cd ..
```

If Yarn is unavailable, install the pinned `yarn@1.22.22` in a local tools directory or use your approved package manager. The checked-in lockfile now includes the five dependencies that were previously missing. The archived prototype still uses React Beautiful DnD, which declares React 16–18 peers; the new workspace does not use that package.

For live mode, configure `DEX_API_KEY`, `MONGO_URL`, `DB_NAME`, and the exact public hosts you permit in `HUGIN_SOURCE_HOSTS`. Dex requires an eligible plan. Hugin's standalone backend authenticates independently of any connector installed in Codex. Its bridge uses **https://mcp.getdex.com/mcp**, Bearer authentication, and `User-Agent: dex-cli`. Proxy-backed keys must be bound to `mcp.getdex.com`; binding a key only to `api.getdex.com` will not authenticate this transport.

Use an existing authorized MongoDB service, or install the pinned local server on Debian 12/13 x86-64:

```bash
bash scripts/install-mongodb.sh
mkdir -p /workspace/.hugin-setup/data/mongodb /workspace/.hugin-setup/logs
/workspace/.hugin-setup/mongodb-linux-x86_64-debian12-8.0.16/bin/mongod \
  --bind_ip 127.0.0.1 --port 27017 \
  --dbpath /workspace/.hugin-setup/data/mongodb \
  --logpath /workspace/.hugin-setup/logs/mongodb.log --fork
```

The script retains TLS verification and checks the archive against MongoDB's official SHA-256 file before extraction. Other platforms should use MongoDB's supported installation path. The MongoDB server has its own SSPL license; review the actual deployment separately from application and source-data rights.

Start these in separate terminals:

```bash
cd backend
../.venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8001 --no-proxy-headers --no-access-log
```

```bash
cd frontend
BROWSER=none HOST=127.0.0.1 PORT=3000 WDS_SOCKET_PORT=3000 \
  REACT_APP_BACKEND_URL=http://127.0.0.1:8001 yarn start
```

The Contacts screen searches Dex and requires you to choose a record before running research. Runs, Evidence, Connections and Integrations show persisted data and actual connector outcomes. The old content-planning prototype remains at `/legacy`, with an archive warning; its demo login is not an access boundary.

### Explicit fixture mode

For a credentials-free demonstration, start the backend with:

```bash
cd backend
HUGIN_MODE=fixture HUGIN_FIXTURE_STORE=../.data/fixture-store.json \
  ../.venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8001 --no-proxy-headers --no-access-log
```

Fixture mode uses synthetic contacts, fixture HTML passed through the real extractor, and simulated Dex writes persisted in a separate locked JSON store. Every job, note, API health response and the interface identify this mode. It does not contact Dex, Brave or public websites. It is never a fallback for failed live authentication. Search `Alex River` to run the example, or `Jamie Vale` to see two candidates.

## One contact, one invocation

With the backend running:

```bash
.venv/bin/hugin enrich --dex-contact-id '<DEX_CONTACT_ID>'
```

This resolves the contact, creates a durable job, searches OpenAlex author records, Europe PMC publications and Hacker News company mentions through API Anything, attempts LinkedIn extraction, public web discovery and Maigret professional-account discovery, reads cached research, extracts permitted pages, checks identity signals, stores evidence and typed entity snapshots, saves supported findings, and verifies Dex writeback. Discovered URLs and matching accounts are candidates, not facts. Search availability is not guaranteed. It waits and emits JSON with source outcomes, pending changes, sync receipts and provider-unit counts. Exit 0 means completed or dry-run; exit 2 includes `no_results`, incomplete or failed runs, with the saved job ID. Empty runs are retained in Hugin and write nothing to Dex.

Use `--query 'name or email or profile'` instead of an ID when necessary. Multiple or zero matches return candidates and start nothing. Reinvoke with the chosen ID. Search is a bounded batch of up to 50 results, not a complete account export.

```bash
# Store a cited result in Hugin without any Dex writes.
.venv/bin/hugin enrich --dex-contact-id '<ID>' --dry-run

# Default: notes only. This optional policy fills only verified, empty website/LinkedIn fields.
.venv/bin/hugin enrich --dex-contact-id '<ID>' --fill-missing

# Explicitly authorize one optional Brave Search request unit.
.venv/bin/hugin enrich --dex-contact-id '<ID>' \
  --sources dex_cached,public_pages,brave --paid-budget-units 1

# Explicit fresh-Dex option. Never forces a rerun.
# Dex itself may fill empty high-confidence fields and replace its prior research/review state.
# This cannot run with dry-run or notes-only semantics.
.venv/bin/hugin enrich --dex-contact-id '<ID>' --fill-missing \
  --sources dex_fresh,public_pages --allow-fresh-dex --paid-budget-units 1

# Retry only the saved sync. No research or paid provider is rerun.
.venv/bin/hugin retry-sync '<HUGIN_JOB_ID>'
```

The default stable operation identity is contact + options + UTC day. Repeating the same invocation returns the same job, without another note. For project automation, use `--job-key '<stable-operation-key>'` and reuse it only with the same options. The UI generates and retains a key for submission retries. A deliberate new run needs a new key; cached public extraction is reused for up to 24 hours when the identity anchor is unchanged.

Equivalent API:

```http
POST /api/enrichments
Content-Type: application/json

{"dex_contact_id":"<ID>","idempotency_key":"<stable-key>","write_policy":"notes_only"}
```

Poll `GET /api/enrichments/{job_id}`. The same API supports `dry_run`, `sources`, `max_pages` (1–10), `max_requests` (1–25), `timeout_seconds` (10–180), and `paid_budget_units` (0–2). See the local FastAPI schema for precise types. `POST /api/enrichments/{job_id}/retry-sync` with `{}` queues only completed research for sync. The worker resumes queued jobs and expired leases after restart.

In a Codex project, ask: **“Enrich Dex contact `<ID>` and save the findings.”** [AGENTS.md](AGENTS.md) describes how to execute that request and report its result without treating simulated responses as live research.

## Sources, identity and costs

Research can continue without LinkedIn. The default `company_web` stage follows bounded public company pages and records cited business context separately from personal findings. A company-name domain guess stays a candidate; it does not confirm employment or personal relationships. See [research beyond LinkedIn](docs/company-research.md) for operation, limits and the verified live company-context result.

LinkedIn extraction is part of the default invocation. The isolated pinned scraper parses professional sections from permitted HTML or a session-backed retrieval when source access allows it. Attach profile HTML in the contact interface or pass `--linkedin-html-file /private/path/profile.html`. Imported claims stay pending and carry their source URL and evidence origin. No LinkedIn session is currently configured, and live retrieval remains unverified. See [LinkedIn adapter setup and operation](docs/linkedin-adapter.md) for install commands, private session handling, limits, rights and the upstream license conflict.

The source registry is in `backend/hugin/sources.py` and available through `/api/integrations`. No North Star service or candidate repository is required.

| Source | What it does | Default / cost |
| --- | --- | --- |
| Company website | Checks one company-domain candidate or supplied URL, follows published same-host links and retains attributed business context | Selected by default; no provider charge; organization match and personal affiliation stay unconfirmed |
| Public web discovery | Bounded DuckDuckGo HTML search returns candidate URLs; access challenges stop the stage | Selected by default; no provider charge; can be unavailable |
| Maigret 0.6.6 | Its pinned site database and detector check a known professional handle against GitHub's public API; candidates stay pending until identity signals support a match | Selected by default; isolated install, no provider charge |
| LinkedIn profile | Isolated pinned parser extracts professional sections from permitted HTML or authorized, allowed session retrieval; imported claims stay pending | Selected by default; no provider charge; access may be blocked |
| Cached Dex Research | Reads stored cited research without starting a run | Selected by default; no fresh-research charge |
| Public professional pages | Extracts Schema.org Person data and bounded professional context with Trafilatura | Selected by default; exact hosts required; no provider charge |
| Brave Search | Discovers up to five URLs; snippets are not treated as verified findings | Optional key and explicit budget; at most one search unit per run |
| Fresh Dex Research | Requests one contact with `force:false`; snapshots returned research in Hugin | Explicit opt-in and budget; Dex determines billing and may reuse recent research |

The default has **zero paid research requests**. Existing Dex subscription charges still apply. Paid counts are reserved/attempted request units, not billing receipts; an interrupted or cache-served request may cost nothing. The application does not invent dollar prices. A sync retry has no research charge.

Source budgets limit extraction requests and logical provider operations; MCP initialization, tool discovery, safe read retries and sync verification are separate bounded operations. Research is serial per worker, with one worker by default. Free reads retry transient failures at most once. Paid research and ambiguous writes are never blindly retried. Optional sources fail independently. Statuses distinguish not searched, unsupported, authentication required, quota exhausted, timeout, no result and ambiguous identity.

Hugin matches full names with known professional URLs or known email addresses, records company matches and conflicts, and rejects explicit name mismatches. Name/company overlap alone stays uncertain. Provider confidence is retained but cannot independently prove identity. Observations from differing roles, companies or profile URLs stay conflicting. Email and phone discoveries remain unresolved/pending. Shared usernames, IPs or event appearances do not create relationships.

Public extraction requires credential-free HTTPS, configured hosts or URLs returned by this run's discovery adapter, public DNS addresses, size and request bounds, and robots permission. Redirects are reported for canonical-URL review; logins, CAPTCHAs and denied pages are not bypassed. General prose extraction is conservative: it saves cited context rather than inventing structured job titles, publications or affiliations from arbitrary text. Structured `knows` assertions become documented-association records, not claims of friendship, investment or introduction. Target identity remains unresolved until checked independently.

Public discovery can authorize extraction of its returned HTTPS URLs within the same bounded run. Each destination still passes public-address checks, robots checks and the cloud network policy; redirects are refused. Known contact URLs outside discovery still require `HUGIN_SOURCE_HOSTS`. Search snippets are never accepted as evidence. Maigret is restricted to GitHub, without recursive username expansion, cookies, network scanning, TLS impersonation or challenge bypass. Hugin fetches through verified HTTPS and runs Maigret's detector offline; its default network checker is not invoked.

FollowTheMoney 4.11.0's Person, Company, Employment and Associate schemas are adapted into the existing Pydantic/Mongo stack, with the selected upstream schemas and MIT license retained. The full FtM runtime is not installed: its native ICU dependency was unavailable, and this workflow only needs the schema subset. `/api/entity-snapshots?contact_id=<ID>` returns dated snapshots with evidence references and review states. Existing Dex context is separate from researched claims. Company names do not automatically merge organizations across contacts, and related people remain unresolved until independently matched. This is schema adaptation, not a claim that FtM resolves identities.

Reuse rights remain source-specific. Hugin stores metadata, short excerpts and permitted structured evidence for private research. It does not imply a redistribution license for research briefs, webpages or provider results. Keys never go to the frontend. There is no analytics script on the workspace page.

## Writeback and recovery

- Notes are additive timeline entries. Hugin does not replace the contact description or existing notes.
- The note has a stable job marker, a fixed `event_time` and a stable Dex idempotency key. Hugin searches existing notes before creation and reads the saved note back.
- Dex's replay window is 24 hours. After that, the job marker and bounded paginated note search prevent duplication. If the history cannot be fully checked within its bound, Hugin refuses another write.
- Default field proposals stay pending. `--fill-missing` applies only high-confidence, supported website/LinkedIn findings to fields still empty at sync time. Cached Dex findings explicitly marked pending remain pending. Emails, phones and conflicting values are never applied automatically.
- Dex has no documented conditional-update/CAS primitive. Hugin rereads before and after updates, but cannot promise atomic protection against another client filling a field between those requests. Use notes-only when concurrent field edits are possible.
- Existing Dex related links stay untouched. New discovered links remain pending; this milestone does not automate adding symmetric, unlabeled links before independently resolving both people. Typed explanations and citations remain in Hugin and the note.
- Sync failure keeps research, source outcomes and evidence. `retry-sync` reuses them and retries only writeback. Unexpected research failure also retains checkpoints; do not create repeated paid runs to diagnose it.

MongoDB stores contacts, jobs, findings, evidence, typed relationships, proposals, source outcomes, cached extraction, structured provider research and sync receipts in separate collections. Do not use the fixture store for live contact data. Back up MongoDB according to your retention needs. Submitted HTML is sanitized and stored privately while its source stage is queued, then removed after the source checkpoint; cached results retain only structured findings and short excerpts. Failed jobs also remove the submitted HTML. Private notes and unnecessary contact context are not sent to the public-page extractor or Brave; Brave receives only the selected person's professional name/company query.

## Verification and troubleshooting

```bash
.venv/bin/python -m pytest tests -q
cd frontend && yarn build
```

For actual MongoDB integration checks, set `HUGIN_TEST_MONGO_URL` and run `tests/test_mongo.py`; the tests create and remove only their own UUID-named test database. Browser smoke requires fixture mode and Chromium, with `playwright-core` installed separately:

```bash
HUGIN_PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/browser-smoke.cjs
```

- **Backend startup fails:** live mode requires MongoDB. Check `MONGO_URL` and database access; use explicit fixture mode for a simulated demonstration.
- **Dex authentication required:** configure the secure key for `mcp.getdex.com` and check the eligible plan. A connected Codex MCP tool does not authenticate the standalone backend.
- **No public findings:** configure exact source hosts in `HUGIN_SOURCE_HOSTS` and allow those domains in cloud settings. Add a known professional website/profile to the Dex contact when available. Empty results are reported truthfully.
- **Source redirects/robots/access denial:** select a permitted canonical URL or another authorized source. Do not disable TLS verification or bypass controls.
- **Sync failure:** inspect the saved job/receipt, restore the prerequisite, then use `retry-sync`. Do not rerun paid research.
- **CLI wait expires:** the job may still be running. Read its saved state or use the same operation key; do not assume no write occurred.
- **Frontend dependency warnings:** CRA 5 is unmaintained and the legacy drag-and-drop module has older React peer declarations. The new workspace build/browser flow is verified; a broader tooling migration is deferred.

Monitoring, broader username/OSINT coverage, graph visualization, relationship-link approval, research brief sales, multi-client access, and MiroShark exports are deferred. No private Dex notes are exported to simulations or other research services.

## Integration contract references

Implementation checked Dex's official [agent skill](https://github.com/getdex/agent-skills/blob/50c86c38ae13b54a1fc78123a02e53d5f4a2dfe3/dex-skill/SKILL.md) and [tool reference](https://github.com/getdex/agent-skills/blob/50c86c38ae13b54a1fc78123a02e53d5f4a2dfe3/dex-skill/references/tools-reference.md), inspected October 7, 2026. The backend checks live MCP tool schemas before using safe parameters and refuses unsupported contracts. The public `getdex/documentation` checkout was a starter template at inspection, so it was not used as an API specification. Live note creation, readback and sync recovery have now been verified; fresh paid research and field updates remain unverified live.

## API Anything sources

API Anything is included in the default enrichment action. It uses reviewed request templates and an offline extractor; Hugin makes the HTTPS requests under its DNS, robots, TLS, size and job-budget checks. Author records and publication matches stay pending, and company mentions do not prove personal affiliation. No browser session or paid API key is needed for these three operations. Source limits, setup paths and commands are in [docs/api-anything.md](docs/api-anything.md).
