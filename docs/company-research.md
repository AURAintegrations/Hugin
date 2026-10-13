# Research beyond LinkedIn

Company-site collection is part of the default single-contact enrichment request. It starts from a supplied company URL, an existing root website, or one conventional `.com` hostname hypothesis built from the company name. That hypothesis is a candidate, never a verified organization match. It follows published same-host links to company, dealer, team, press and blog pages, with at most three pages per run and the shared network/time budgets. No domains are scanned and no hidden paths are probed.

The collector checks public DNS, credential-free HTTPS, robots policy and cloud access. It refuses redirects and does not bypass logins or challenges. It retains bounded, attributed company excerpts and blog publication titles with source URLs and retrieval timestamps. Company marketing statements are recorded as source claims, not independently audited facts. A page about another person cannot establish this contact's identity or a relationship.

`company_context` findings identify their subject as company and remain unresolved/pending. They never propose a personal role, profile, email or phone field. A run containing only these findings is labeled `company_context_only` in the job, note and interface. Its note says no new personal facts were confirmed and the existing Dex affiliation was not reverified. A research-and-save invocation may add that cited context note; populated fields and related links stay unchanged.

The existing invocation now includes this stage:

```sh
.venv/bin/hugin enrich --dex-contact-id '<ID>' --job-key '<stable-key>'
```

To select it alone or supply an optional company-site candidate:

```sh
.venv/bin/hugin enrich --dex-contact-id '<ID>' --sources company_web \
  --company-url 'https://www.example.org/' --job-key '<stable-key>'
```

The API accepts `company_urls` with the `company_web` source. Add `--dry-run` for Hugin-only storage. Candidates and per-page failures appear in source outcomes. Successful results are cached for a day, preserving their retrieval times. A failed optional page does not discard other evidence. Company-only notes reuse the existing durable job and idempotent, verified Dex sync.

Live on October 7, 2026: the selected contact's existing company name led to `www.ezup.com`, its dealer-program page and its blog index. Hugin collected five attributed company-context findings, saved one dated cited note to his selected Dex ID and verified the note's content and association through Dex readback. Zero paid research requests, field changes or relationship links were made. This demonstrates live business-context collection; the selected contact's current role, biography and personal relationships were not confirmed.

Broad person discovery remains limited. Public probes found Wikipedia denied access, GDELT robots unavailable, and Google News RSS and Brave's public search disallowed automated retrieval. The prior DuckDuckGo route returned a challenge. No configured search-provider key was available. These routes were not represented as completed person searches. Additional discovery coverage and person-specific corroboration remain expansion work, not a claim that every contact has a large public footprint.
