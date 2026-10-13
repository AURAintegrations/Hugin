# Verification record

Date: October 7, 2026. Base tree: `826240c7b9d0d309ad99084e7b6f35f1e1ff4c40`. `git fetch origin main` confirmed that this was also the latest remote main at implementation start. No pre-existing user changes were found.

## Executed checks

| Check | Actual outcome |
| --- | --- |
| `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q` | 33 passed, including the actual MongoDB integration test; one dependency deprecation warning |
| Yarn 1.22.22 `install --frozen-lockfile --non-interactive` | Passed after repairing the five missing dependency entries in the repository lockfile |
| `BUILD_PATH=/workspace/.hugin-setup/build npm run build` | Passed; CRA/Babel, Browserslist-age and Node deprecation notices remain |
| `bash scripts/install-cloud.sh` | Passed; installation is repeatable with the repaired frozen lockfile, editable backend and verified MongoDB archive |
| `bash scripts/install-mongodb.sh` | Passed; official SHA-256 check succeeded; MongoDB 8.0.16 starts on loopback |
| `.venv/bin/hugin enrich --dex-contact-id fixture-alex --job-key final-fixture-validation-v1` | Completed and verified a **simulated** Dex note; zero paid attempts; six findings and eight evidence records in this fixture |
| `HUGIN_PLAYWRIGHT_MODULE=/workspace/.hugin-setup/tools/node_modules/playwright-core node scripts/browser-smoke.cjs` | Passed; fixture banner, ambiguous selector, enrichment, cited note, simulated readback, evidence, connections, integration statuses and mobile layout; no page errors or external page requests |
| `pip check` | Passed: no broken requirements |
| Live-mode API with actual MongoDB, `GET /api/health` | Storage ready; reports `dex: authentication_required`; no fallback to fixtures |
| Public Dex MCP endpoint connectivity | HTTP 401 without authorization, rather than network-policy denial; reachability only, not authenticated readiness |
| Tracked `.env` inspection | Names/presence and credential-pattern check only; no credential-like values detected; values never printed. Removed tracked files and added examples/ignore rules |
| Protected `test_result.md` block | Original prefix preserved byte-for-byte; new verification appended below it |

The Mongo integration test uses actual database collections, unique indexes, concurrent submission, atomic claims, evidence persistence, expired-lease restart recovery and ownership checks. Its research and Dex providers remain fixtures. It creates and deletes only its own UUID-named test database.

The automated suite also checks wrong-person rejection, ambiguous names, name-only and company-homepage uncertainty, citation/evidence binding, uncited-claim rejection, pending contact methods, existing-field preservation, conflicting roles and relationships, dry-run writes, empty results, optional failures, request/paid limits, paid-request crash recovery, idempotency-key conflicts, bounded read retries, safe MCP parameter negotiation, SSE transport, source robots/cache rules, private-address rejection, credential-safe connector errors, browser-origin/host/local-only guards, note/contact readback mismatch, note timeout-after-write, field timeout-after-write and sync-only retries.

## Subsequent live validation

### Collector revision after the owner's workflow correction

The owner declined paid Dex Research and asked for Hugin's own collection system. Default runs now attempt public web discovery and Maigret account discovery in addition to cached research and page extraction. Empty results are a distinct terminal `no_results` state, retain their report in Hugin, exit the CLI with code 2, and never create a Dex note. The earlier empty-note run below remains historical; it did not meet the enrichment goal and was not silently deleted.

Actual single-contact invocation: `.venv/bin/hugin enrich --dex-contact-id <DEX_CONTACT_ID> --job-key selected-contact-public-collectors-2026-10-07`. Job `<PRIVATE_RUN_OR_NOTE_ID>` returned `no_results`, with no sync attempted and zero paid attempts. Public discovery returned an access challenge; LinkedIn robots disallowed extraction; cached Dex research was absent. Maigret's pinned detector classified one GitHub account candidate, but no independent identity signals linked it to the contact. It stayed pending and produced no factual findings. No further Dex note, field or relationship was written.

Maigret 0.6.6's MIT license and dependency requirements were inspected in its exact wheel. Its built-in network checker disables certificate verification, so Hugin does not call it: bounded verified HTTPS fetches feed the pinned database/detector offline in an isolated environment. `backend/collectors.lock.txt` pins the resolved collector dependencies; `bash scripts/install-collectors.sh` passed again using that lock, and its `pip check` passed. This integration currently supports GitHub only; it does not run the full site inventory or recursively expand handles.

FollowTheMoney 4.11.0's selected schemas and MIT license were inspected and retained with artifact provenance in `backend/hugin/ftm_schema/`. An attempted full runtime install encountered missing native ICU build prerequisites. The dependency was removed; this implementation adapts the schema subset into the existing Pydantic/Mongo stack, as permitted by the handoff. Dated Person/Company/Employment/Associate snapshots retain evidence and review states, distinguish existing Dex context, avoid company-name-only merging and keep relationship targets unresolved. Full FtM normalization is not claimed.

Final collector checks: **42 backend tests passed** with actual MongoDB and the real pinned Maigret detector fed synthetic API responses; one dependency deprecation warning. Frontend production build passed. Chromium fixture validation on ports 3002/8003 passed, including paid-source controls, typed snapshots, empty-result/no-write UI, cited fixture notes, evidence, sync, mobile layout and no external requests or page errors. Fixture responses are simulations, not live research. Core and isolated collector `pip check` passed. Humanizer main-skill editorial scope is recorded separately.

The reusable installation script now includes the locked isolated collector installation. Broad live research for the selected contact is still blocked by search access and the lack of other accessible discovery coverage. Fresh paid Dex Research was not invoked, and no paid service was silently enabled. The milestone remains incomplete until a live run produces useful cited findings and verifies their Dex writeback.

After the owner corrected the secret destination and published the environment, runtime revision 7 included `mcp.getdex.com`. Actual Dex search succeeded with one matching contact. In live mode with actual MongoDB, the single-contact CLI created job `<PRIVATE_RUN_OR_NOTE_ID>` and saved note `<PRIVATE_RUN_OR_NOTE_ID>`. There were zero supported findings: cached Dex research was absent, and LinkedIn robots policy disallowed extraction. The note reports these limitations rather than simulated research. Paid request attempts: zero. Populated company, role and LinkedIn values remained unchanged; no fields or relationships were added.

Live responses exposed two fixture gaps, now fixed: LinkedIn handles are normalized to profile URLs without changing contact fields, and Dex timeline `note` bodies plus `timeline_items_contacts` associations are normalized for marker search and readback. Initial sync verification failed after the note had already been saved. `hugin retry-sync <PRIVATE_RUN_OR_NOTE_ID>` then verified the same note's exact content and selected-contact association, without rerunning research or creating another note. Repeating the original stable-key invocation returned the same completed job and note. Successful recovery clears stale error labels from the receipt.

Following these fixes, `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q` passed **35 tests**, with one dependency deprecation warning. `BUILD_PATH=/workspace/.hugin-setup/build npm run build` passed. Live run reports are retained only in ignored `.data` files and MongoDB. No credential values were printed.

Exact invocation: `.venv/bin/hugin enrich --dex-contact-id <DEX_CONTACT_ID> --job-key selected-contact-first-live-2026-10-07`. The live backend was started with `HUGIN_SOURCE_HOSTS=www.linkedin.com,linkedin.com`, default notes-only and zero paid budget. A live run producing cited facts still requires a permitted public professional page, usable cached research, or explicitly authorized paid discovery. The first milestone's cited-findings acceptance criterion is therefore still outstanding.

## Earlier access diagnosis (resolved)

After the environment restart, `DEX_API_KEY` was present (value never inspected or printed). The runtime configuration still scoped it to `api.getdex.com`. A read-only search for the owner's selected name, the selected contact, failed during MCP authentication with `authentication_required`; no contact results were retrieved and no writes occurred. A non-redirecting read-only `GET https://api.getdex.com/v1` returned HTTP 502. Dex's current [authentication documentation](https://getdex.com/docs/api-reference/authentication) specifies `api.prod.getdex.com` for REST, so the existing destination cannot be assumed to support the documented REST API either. The existing MCP implementation requires editing the secret's allowed destination to `mcp.getdex.com`; a network allowlist entry alone does not change a secret binding.

The following prerequisites were identified before the successful live empty-result run above:

1. Securely configure `DEX_API_KEY` for an eligible Dex account. The saved requirement was initially bound to `api.getdex.com`; **edit its allowed destination in environment settings to include `mcp.getdex.com`**, the transport this implementation uses. The configuration API cannot revise an existing secret binding; its attempted update returned a conflict, and no duplicate was created.
2. Select one contact ID. Configure exact approved public source hosts and cloud network destinations if public-page extraction is wanted. Cached Dex research alone needs no paid research opt-in; absent cached data may yield an honest empty result.
3. Start live mode with real MongoDB and run `hugin enrich --dex-contact-id '<ID>' --job-key '<stable-key>'`. Inspect source outcomes, citations, identity confidence and the verified Dex receipt. Do not mass-enrich contacts as a test.

Brave Search and fresh Dex Research are implemented but not live-tested. No prices or billing charges have been verified. Default paid request budget is zero. Fresh Dex's replacement and auto-fill behavior is disclosed and disallowed in dry-run/notes-only mode.

New Dex related-contact links remain pending; only typed, cited associations are stored in this milestone. Monitoring, broader username/OSINT tools, graph visualization, link approval, multi-client authentication, billing and scenario exports are deferred.

The Humanizer review scope and unavailable supplements are recorded in [editorial-review.md](editorial-review.md). The current filesystem and saved environment draft have been validated; publication and restoration in a new task have not been verified.

## Changed files

- `backend/server.py`, `backend/hugin/{app,cli,config,dex,engine,models,sources,store}.py`: local API, CLI, bounded connectors, identity/evidence pipeline, durable Mongo jobs and receipts.
- `backend/hugin/fixtures/demo.json`: explicitly synthetic contacts/pages; package data only.
- `backend/requirements.txt`, `backend/pyproject.toml`: pinned runtime/test dependencies and installed `hugin` command.
- `frontend/src/App.js`, `frontend/src/workspace/*`: focused contacts/research interface. `frontend/src/LegacyApp.js` preserves the earlier application; `components.js` remains available only to the archive.
- `frontend/public/index.html`: truthful metadata, removed third-party analytics/badge; `frontend/yarn.lock`: missing dependency entries repaired.
- `.gitignore`, `backend/.env.example`, `frontend/.env.example`: private configuration and generated-data exclusions. Removed tracked `backend/.env` and `frontend/.env`; no history rewrite.
- `tests/{conftest,test_api,test_connectors,test_mongo,test_pipeline}.py`, `scripts/browser-smoke.cjs`: fixture/API/transport/real-storage and browser verification.
- `scripts/{install-cloud,install-mongodb}.sh`: repeatable local/cloud setup with frozen frontend install and official artifact verification.
- `README.md`, `AGENTS.md`, `docs/{verification,editorial-review}.md`, `test_result.md`: setup, operation, project instruction, results and editorial scope.

Pinned-package license metadata was also rechecked: Trafilatura 2.0.0 and Requests 2.32.5 use Apache-2.0; PyMongo 4.14.1 includes the Apache-2.0 license; FastAPI 0.116.1, Pydantic 2.11.7 and Typer 0.16.1 use MIT; HTTPX 0.28.1 and Uvicorn 0.35.0 use BSD-3-Clause. This does not grant reuse rights to source records or settle the separate MongoDB server deployment license.

LinkedIn scraper evaluation: see `docs/linkedin-connectors.md` and `scripts/evaluate_linkedin_scraper.py`. Isolated joeyism 3.1.2 installation passed pip check and two upstream serialization tests. The offline Chromium characterization passed 11 checks, including six reproduced defects, with four intercepted requests and no live traffic. No production dependency or connector was enabled. Regression commands `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q` and `BUILD_PATH=/workspace/.hugin-setup/build npm run build` passed: 42 tests (one existing dependency warning) and a successful production build (existing Node/Browserslist notices). Live LinkedIn acquisition remains unverified.

## LinkedIn adapter implementation, October 7, 2026

The subsequent authorized implementation adds an isolated worker pinned to `b1cdc1c0e85bee8764d62565d229c682e5eb81bb`, private session-backed HTTP acquisition under source policy, permitted HTML import, source outcomes, evidence origins and integration/UI status. It avoids upstream full-profile traversal, normalizes dash separators, validates profile URLs before acquisition, independently rejects challenges and protects session files. Imported findings remain pending. HTML is private while queued and deleted after a source checkpoint or terminal failure. The parser is offline with scripts disabled and network requests aborted. Session retrieval retains the cloud proxy and TLS trust. Root GPLv3 license/metadata inconsistency remains documented.

Executed checks:

- `bash scripts/install-linkedin.sh`: pinned VCS install, repeat install and pip check passed; no source login or paid calls.
- `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q`: **64 passed**, no skipped tests, one existing dependency deprecation warning. Includes the actual pinned upstream parser and system Chromium on synthetic HTML, canonical mismatch, wrong-person rejection, citations, imported pending claims, session permissions/expiry/scoping, cache/idempotency, durable input recovery, isolated missing-session failure, robots denial, sync-only retry and termination of timed-out child processes.
- `BUILD_PATH=/workspace/.hugin-setup/build npm run build`: passed; existing CRA/Babel, Node and Browserslist notices remain.
- `HUGIN_PLAYWRIGHT_MODULE=/workspace/.hugin-setup/tools/node_modules/playwright-core HUGIN_WEB_URL=http://127.0.0.1:3002 HUGIN_API_URL=http://127.0.0.1:8003 node scripts/browser-smoke.cjs`: passed after starting the absent fixture frontend. Includes actual file upload, upstream parsing, source/evidence origins, pending education, simulated sync, source outcomes, mobile layout and no external requests or page errors. All contacts and Dex writes in this check were simulated.
- Fixture CLI: `.venv/bin/hugin enrich --api http://127.0.0.1:8003 --dex-contact-id fixture-alex --sources linkedin --linkedin-html-file tests/fixtures/linkedin-profile.html --job-key linkedin-cli-fixture-2026-10-07 --dry-run`: exit 0, seven findings, zero network requests and paid attempts; no Dex write.
- Live, owner-selected contact check: `.venv/bin/hugin enrich --dex-contact-id <DEX_CONTACT_ID> --sources linkedin --job-key selected-contact-linkedin-adapter-check-2026-10-07 --dry-run`: exit 2, job `<PRIVATE_RUN_OR_NOTE_ID>`, live `no_results`, `authentication_required`, zero research network requests/paid attempts, no note or field write. Dex contact resolution succeeded. No LinkedIn session is configured; earlier robots denial also remains a potential blocker. This is not live enrichment.

API 8001 was restarted with the adapter and verified live/local-only; API 8003 is explicitly fixture mode. Core and isolated pip checks passed; `git diff --check` passed. Main-skill Humanizer scope and limitations are recorded in editorial-review.md. Live profile acquisition, original HTML capture dates, skills, new relationships and current professional findings for the selected contact remain unverified or unsupported as documented.

## Company-first research, October 7, 2026

Added `backend/hugin/company.py` and the default `company_web` source. It checks one company-domain hypothesis or supplied candidates, follows published same-host links, enforces source access/budgets and saves attributed excerpts/publication titles. Company subjects and unresolved affiliation are explicit in evidence, jobs, notes and UI. Company context never proposes personal fields or relationship links. Transient budget/network failures are not cached for a day.

- Backend command `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q`: **72 passed**, no skips, one dependency deprecation warning. New checks cover candidate hypotheses, wrong-company exclusion, off-host links, robots, caching, provider budgets, pending company-only notes, person preservation and optional-source isolation.
- `BUILD_PATH=/workspace/.hugin-setup/build npm run build`: passed with existing CRA/Babel, Node and Browserslist notices.
- Fixture browser command on 3002/8003: passed after starting the absent frontend. The interface now includes company-source page outcomes and evidence subject labels; existing upload, cited notes, simulated sync and mobile checks remain passing. No external requests/page errors.
- Live review invocation with `--sources company_web --dry-run`, selected Dex ID `<DEX_CONTACT_ID>`, key `selected-contact-public-company-review-2026-10-07`: job `<PRIVATE_RUN_OR_NOTE_ID>`, company context only, four public requests, zero paid attempts, no write.
- Live research-and-save invocation: `.venv/bin/hugin enrich --dex-contact-id <DEX_CONTACT_ID> --sources company_web --job-key selected-contact-public-company-save-2026-10-07`. Job `<PRIVATE_RUN_OR_NOTE_ID>` completed with five cited company-context findings from the homepage, dealer-program page and blog index. Note `<PRIVATE_RUN_OR_NOTE_ID>` content/contact association matched Dex readback. Existing fields/links unchanged; zero paid attempts. Repeating the exact invocation returned the same job, note and request counters, with no new research or write. Reports remain private under `/workspace/.hugin-setup/logs/`.

This is a real business-context result, not a verified the selected contact biography or role. Company statements, including marketing/dealer counts, remain attributed and pending. No installed Dex skill was available in the cloud skills catalog; the existing server-side Dex bridge performed authorized operations. Read-only route probes checked access, not successful person research: E-Z UP allowed pages were reachable; Wikipedia returned 403, GDELT robots 503, Google News RSS/Brave public search robots denied automation. No other search API keys were present. Broad person discovery still needs more coverage; no comprehensive contact footprint is claimed.

## API Anything pipeline integration (October 13, 2026)

Installed API Anything 0.1.0 at pinned commit `0b556c36932b111ee8840c412008261abe717725`, with exact built-file checks and a committed runtime lock including patched MCP SDK 1.31.0. `bash scripts/install-api-anything.sh` passed frozen source install/build/check, local package installation, frozen runtime install, zero-vulnerability runtime audit and actual offline worker verification.

Commands and final results:

- `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q`: **82 passed**, no skips, one existing AnyIO/Starlette deprecation warning. Real Mongo, pinned Maigret, pinned LinkedIn parser and the actual API Anything worker were installed. Tests exercise cited fixture note writeback, preserved fields, rejected identities, pending author findings, event dates, encoding, empty results, source isolation, quotas, robots, schema drift, worker secret isolation, request caching, operation checkpoints and sync-only recovery before/after note creation.
- `.venv/bin/python -m pytest tests/test_api_anything.py -q`: **10 passed** after adding surname/initial query and strict full-name/diacritic checks.
- `BUILD_PATH=/workspace/.hugin-setup/build npm run build` in frontend: passed. A separate build with `REACT_APP_BACKEND_URL=http://127.0.0.1:8003` and a separate fixture build directory also passed. Existing CRA/Browserslist warnings remain.
- Fixture Chromium smoke uses API8003, the fixture build served on3002, and an explicit fixture CORS origin on3002. It verifies real UI selection, all three simulated API source outcomes through the actual worker, pending publication evidence, cited note, simulated sync receipt, imported HTML, empty/no-write behavior, evidence, connections, integrations, mobile layout and no external asset requests/page errors. These are synthetic provider/Dex data, not live contact research.

Live public checks used Hugin transport with DNS, robots, proxy, verified TLS, redirect refusal and budget controls. OpenAlex returned three author records for a public historical figure; Europe PMC returned three full-name publication candidates for a public scientist; Hacker News returned three title-matched technical-news records. These smoke checks did not create Dex records or notes. Author metadata remains pending, and news remains company context. The Europe PMC query was corrected to its indexed surname-plus-initial syntax; a full given/surname match in returned metadata is required before retaining a publication candidate.

The selected contact was read from live Dex and tested using `--sources api_anything --dry-run`. Final job `<PRIVATE_RUN_OR_NOTE_ID>` used six public requests and zero paid attempts: OpenAlex returned zero records, Europe PMC returned three candidates with no matching full author name, and Hacker News returned three titles with no accepted complete company phrase. State **no_results**, zero findings, zero Dex writes. An OpenAlex cost metric of USD0.001 is recorded as provider-reported query cost, not verified billing. Stable-key repetition returned the same job and counters. Earlier source probes and a job skipped by an older worker are historical checks, not successful final pipeline runs.

During restart, old servers competed for the live Mongo queue and one older worker skipped the new source. The task-owned old workers were stopped by verified PID, then the current code was restarted and live checks repeated. An initial browser check also exposed a missing fixture CORS origin; the fixture server was restarted with only its local3002 origin allowed. Current live API8001/frontend3000 and fixture API8003 are separate. Do not operate multiple backend revisions against the same queue.

The default API, CLI and Contacts action now include the three reviewed operations. LinkedIn/Instagram restrictions, missing broad web-search coverage, additional conference/trade-directory operations, remote authentication, monitoring and external simulation exports remain outside this increment. No claim of comprehensive enrichment or universal identity accuracy is made.
