# LinkedIn adapter

Hugin uses the evaluated `joeyism/linkedin_scraper` revision through an isolated, offline Chromium parser. It extracts biography, headline, employment history and education when the supported profile DOM is present. Current role/company are derived only from a single employment entry explicitly marked Present. A headline alone is not a current role. Missing and unparsed sections are reported separately. Skills, contact details and relationships are not collected by this adapter.

Install the worker from the repository root:

```sh
bash scripts/install-linkedin.sh
```

The lock file pins the upstream Git commit and runtime dependencies. The worker verifies its installed version and Git revision. System Chromium must exist at `/usr/bin/chromium`, or set `HUGIN_LINKEDIN_CHROMIUM` to a supported executable. `HUGIN_LINKEDIN_PYTHON` selects the isolated interpreter. Core FastAPI dependencies remain separate.

## One contact, one invocation

The default Enrich action includes LinkedIn. With an authorized session and permitted source access, use the existing command:

```sh
.venv/bin/hugin enrich --dex-contact-id '<DEX-ID>' --job-key '<stable-key>'
```

When automated retrieval is unavailable, supply profile HTML you have permission to use:

```sh
.venv/bin/hugin enrich --dex-contact-id '<DEX-ID>' \
  --linkedin-html-file '/private/path/profile.html' \
  --sources linkedin --job-key '<stable-key>'
```

Add `--dry-run` to store research without Dex writes. In the interface, select the Dex contact and attach the HTML under **LinkedIn profile HTML**, then use the same Enrich action. The file must be UTF-8 and at most one megabyte. The API accepts `linkedin_html` with the `linkedin` source in the existing `/api/enrichments` JSON request. It returns the durable job, not the raw HTML.

Imported claims remain pending even when the name/profile anchor matches, because supplied HTML does not prove current live content. Evidence records label `user_supplied_html`; timestamps record processing, not the original page capture time. Employment/education start dates retain their source precision in event_date as well as the claim text; year-only values are not expanded into invented full dates. Only the source URL, bounded excerpts and structured findings remain after the source checkpoint. A dated cited note can be saved while field changes stay pending. Existing Dex fields are preserved.

## Private sessions and source access

`HUGIN_LINKEDIN_SESSION_FILE` may point to Playwright storage-state JSON created through an authorized manual session. Keep it outside Git in an owner-only directory. The file must belong to the backend user, be a regular file with mode 0600, have no symlink and be under 100 KB. Expired or insecure cookies are ignored. Only LinkedIn-domain cookies are used. Never put a password, cookie or storage-state JSON into chat, a command argument, a test or a source file.

There is no automated login, warmup or CAPTCHA workaround. Session retrieval uses Requests with the inherited cloud proxy and CA trust. Before sending authenticated requests it checks the exact configured `www.linkedin.com` host and robots policy. Redirects are refused, TLS verification stays enabled, and HTTP 429/999, login pages, checkpoints and challenges stop collection with distinct outcomes. A session does not override a robots denial. LinkedIn previously denied automated profile extraction in this environment, and no session is configured here. Supplying a session alone may therefore still be insufficient for live retrieval.

The parser executes no source JavaScript and aborts all network requests. It does not use the upstream full-profile traversal, which automatically visits contact-info overlays and contains the defects found during evaluation. It parses only professional sections from the acquired HTML. Client-rendered content absent from that HTML is reported absent or unparsed. Total run deadlines, network budgets, one-megabyte responses, a bounded subprocess and the existing worker limit constrain collection. There are no paid LinkedIn provider calls or automatic paid Dex requests.

Results are cached for one day using contact anchor, input hash and parser revision. Source outcomes and observations are checkpointed before imported HTML is removed. Restart recovery and sync-only retries use those checkpoints. The stable job key prevents duplicate notes. An empty or wrong-person result writes nothing to Dex.

## License and verification

The pinned upstream root LICENSE is GPLv3; its README/package metadata disagree. This private development installation does not resolve that inconsistency. Do not describe the dependency as Apache-only or distribute a proprietary combined application without resolving applicable license obligations. Source access and content reuse rights remain separate from code licensing.

Run `HUGIN_TEST_MONGO_URL=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest tests -q` after installing the isolated worker. LinkedIn tests exercise the actual pinned parser and Chromium using synthetic profiles. They verify citations, pending imported claims, wrong-person rejection, canonical mismatch, challenge detection, session permissions/expiry/scoping, cache, restart recovery and sync retries. They do not authenticate to LinkedIn or represent live research. See `docs/verification.md` for executed results.
