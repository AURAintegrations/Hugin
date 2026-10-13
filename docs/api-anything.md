# API Anything enrichment sources

The default CLI and Contacts action now include `api_anything`. One contact invocation runs three reviewed operations, stores cited evidence, and uses the existing Dex note sync and readback. Existing contact fields and relationships remain unchanged by these operations. Empty results write no note.

| Operation | What it searches | What Hugin accepts |
| --- | --- | --- |
| OpenAlex authors | Full professional name, first three records | Author profile candidates and last listed institutions. Historical institution metadata does not confirm current employment. |
| Europe PMC publications | Surname and first initial, first three records | Publication candidates only when the returned author metadata supplies the matching full given/surname. Initials alone are discarded. |
| Hacker News company mentions | Existing company name, first three stories | Titles containing the complete company phrase. Mentions remain company context, with organization identity unconfirmed; the poster is not treated as a contact relationship. |

This adds academic/publication and technical-news coverage. Many contacts will have no relevant records in these sources. Conference directories, trade associations and additional company newsrooms are not yet API Anything operations. The existing company-site collector remains available.

## Setup and invocation

```bash
bash scripts/install-api-anything.sh
.venv/bin/hugin enrich --dex-contact-id '<ID>' --job-key '<stable-key>'
# Limit a run to the new operations and save nothing to Dex:
.venv/bin/hugin enrich --dex-contact-id '<ID>' --sources api_anything --dry-run
```

The live backend uses port **8001**, with the live frontend on 3000. A separate explicit fixture backend uses 8003. Stop older Hugin workers before restarting updated code: workers from different revisions must not compete for the same MongoDB queue. During verification an older worker skipped a new-source job; it was stopped and the final checks were repeated with the current code.

`HUGIN_API_ANYTHING_DIR` selects the installed package directory, and `HUGIN_API_ANYTHING_NODE` selects Node. Defaults are in the sanitized backend environment example. Node 24 was verified; upstream requires at least 22.13. Source hosts are explicitly reviewed in `api_anything.py`, not arbitrary client-submitted operation names or URLs.

## Implementation and evidence

API Anything 0.1.0 is built from commit `0b556c36932b111ee8840c412008261abe717725` under its root MIT license. The isolated install uses the checked-in runtime dependency lock and MCP SDK 1.31.0 security fix. Hugin checks package version and hashes of the built JavaScript files before using it.

The request templates were learned by the real `learnOperation` implementation from two live public responses per endpoint. Recorded template examples were replaced with synthetic names before committing. The checked-in JSON operations are read-only, tier 1, and have no cookie/session references or volatile tokens. Europe PMC's author query uses its surname-and-initial syntax; Hugin checks full names in the returned metadata before retaining a publication candidate.

A short-lived Node worker uses API Anything's template builder and structured extractor. It receives only a search query or an already-fetched response, with no Dex key or private notes in its environment. It performs no network requests, imports no sessions and launches no browser. Hugin controls the actual fetch, public-IP checks, robots policy, TLS verification, redirects, size limit and durable request accounting. Source failures remain isolated. No automatic learning, healing, write operation or alternate access path is enabled during enrichment.

Evidence keeps the retrieval date, publication date where supplied, operation name, pinned revision, source-record index, URL and supporting excerpt. Source outcomes retain an operation digest and returned-record count. Selected excerpts are also retained separately in `api_metadata`. A 24-hour cache avoids repeating successful or empty queries; timeouts, quota errors and malformed responses are not cached. Each operation has its own durable checkpoint. Sync retries use saved research and do not repeat collection.

All new observations remain pending, including name-and-institution matches. Different full names are rejected. Matching names, author co-occurrence and news posters create no Dex relationship links. The existing field proposals, notes-only default and readback rules still apply.

## Costs and access

These operations use anonymous public endpoints, with no paid provider key or paid-research attempt. They are subject to provider availability and rate limits. OpenAlex returned a `cost_usd` query metric of 0.001 in live responses; Hugin records that metric in source outcomes and notes without treating it as a verified account charge. No currency billing was verified. Paid Dex Research remains disabled.

OpenAlex metadata is offered under CC0; see https://docs.openalex.org/additional-help/faq. Europe PMC API documentation is at https://europepmc.org/RestfulWebService. Hacker News search API documentation is at https://hn.algolia.com/api. Code licenses and API access do not grant rights to redistribute articles or linked pages. Hugin retains short bibliographic metadata for private review and retrieves no article full text through these operations.

OpenLibrary's tested search path was disallowed by robots. Crossref returned a rate limit during source evaluation. Neither was enabled. LinkedIn and Instagram access restrictions remain unchanged.
