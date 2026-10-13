# LinkedIn extraction candidates

Inspected October 7, 2026. Joey's package was subsequently installed in an isolated evaluation environment and exercised against synthetic HTML in Chromium. No real LinkedIn session was accessed and no live extraction was verified.

Dex already supplies a LinkedIn handle for the selected contact. The immediate requirement is URL-to-profile extraction, rather than another name-to-URL finder.

| Repository | Exact inspected revision | Relevant capability | Acquisition requirement | License evidence |
| --- | --- | --- | --- | --- |
| [joeyism/linkedin_scraper](https://github.com/joeyism/linkedin_scraper) | `b1cdc1c0e85bee8764d62565d229c682e5eb81bb`, project version 3.1.2 | Python/Playwright `PersonScraper`; name, location, about, experience, education, interests, accomplishments and contacts. Actual Person model lacks the README's advertised headline and skills fields | README requires an authenticated LinkedIn session, created through manual login or supplied credentials; a Dex key does not supply that session | Root LICENSE is GPLv3, while README badge and pyproject metadata say Apache 2.0. Do not describe this revision as cleanly Apache licensed; account for the root license before distribution |
| [aadisriram/nodejs-linkedin-scraper](https://github.com/aadisriram/nodejs-linkedin-scraper) | `1292f4e10ea70178850e950e8b4f2d82e9232f18`, project version 2.0.0 | Node 20+/TypeScript parser for profile HTML; structured headline, summary, dated positions, education, skills, publications and websites when present; reports absent/empty/parsed sections | Primary interface parses accessible/saved HTML. Optional live client stops on login/challenge pages and HTTP 429/999; it cannot make a blocked page accessible | Root LICENSE and package metadata both MIT |

The Python project is an acquisition candidate requiring substantial adapter work, rather than a ready Hugin connector. The Node project is an MIT-licensed parsing candidate when profile HTML is available. Neither has been shown to retrieve the selected contact's profile in this environment. A parser alone does not resolve the current access blocker.

Also inspected [yatish27/linkedin-scraper](https://github.com/yatish27/linkedin-scraper) at `fb4297f57149507427188f73b89b36c466b6ef0a`: MIT-licensed Ruby gem for public profiles, last repository push April 2024. Its documented selectors and public-page access were not verified live; it is a weaker fit for the existing Python/Node stack.

Potential Hugin integration: normalize the existing Dex URL, retrieve an authorized profile through a bounded adapter, extract professional fields, retain the profile URL and retrieval time as evidence, check identity against the Dex anchor, and leave conflicts or contact methods pending. Existing job persistence and sync retry apply to the adapter's result. No login, CAPTCHA, network policy or source access restriction should be bypassed. Do not request passwords or session cookies in chat.

## Joey evaluation results

Isolated Python 3.12 install and `pip check` passed. Two explicitly selected upstream Person serialization unit tests passed. Hugin's `scripts/evaluate_linkedin_scraper.py` passed 11 characterization checks using real system Chromium, four intercepted browser requests and zero live requests. These checks confirm three extraction behaviors, two block-detection behaviors and six defects; they are not eleven successful production capabilities. All identities and page content were synthetic. The first test run exposed a missing fixture charset; UTF-8 fixture headers corrected that test harness issue before the reported run.

| Observed behavior | Implication |
| --- | --- |
| Name/location, biography and employment with hyphen-separated dates extracted correctly | Useful core parser, demonstrated only on the tested synthetic DOM |
| Text rate-limit and checkpoint pages raise RateLimitError | Some block detection works |
| CAPTCHA detection raises inside an `except Exception: pass` block | Its own CAPTCHA error is swallowed; require independent fail-closed challenge detection |
| Profile URL without trailing slash resolves details to `/in/details/experience` | Normalize trailing slash or repair URL construction; Hugin currently stores URLs without that slash |
| Model accepts off-host URL containing `linkedin.com/in/` in its query | Strict HTTPS host/path validation must happen before navigation, not only after extraction |
| Headline and skills absent from Person model | Advertised coverage cannot be assumed |
| En dash date range remains a single start-date string | Normalize dates conservatively and retain raw evidence |
| Empty synthetic session saved as mode 0644 under umask 022 | Protect real session files with mode 0600 and private directories |

Code inspection also found broad section exception handling that returns empty results, generic top-level error wrapping, automatic contact-info overlay navigation, and a credential-login warmup that visits unrelated websites. A Hugin adapter should preserve distinct failure outcomes, disable unnecessary contact collection and warmup, enforce total time/request limits, honor the cloud proxy/CA and source policy, and store citations/identity confidence itself. Upstream does not supply Hugin's evidence, identity matching or Dex writeback logic.

Reproduce the offline check after downloading and verifying the exact revision into an isolated virtual environment:

```sh
<evaluation-venv>/bin/python scripts/evaluate_linkedin_scraper.py
```

The script requires this pinned package and `/usr/bin/chromium`; it is not part of production dependencies. Current evaluation environment: `/tmp/hugin-linkedin-evaluation/venv`. No API charges were incurred. Live viability remains unresolved without an authorized LinkedIn session and permitted access. Verdict: retain as a conditional acquisition candidate; do not enable its unmodified scraper in the default enrichment pipeline. Resolve the license inconsistency and implement the bounded adapter before integration. This evaluation does not enrich the selected contact or change Dex.
