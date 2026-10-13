"""Offline characterization of joeyism/linkedin_scraper 3.1.2.

Run in an isolated environment with that pinned package and system Chromium.
All browser requests are fulfilled with synthetic HTML; no live research.
Known-defect checks assert observed behavior, not production suitability.
"""
import asyncio
import json
import os
import stat
import tempfile
from pathlib import Path
from urllib.parse import urljoin

from linkedin_scraper import BrowserManager, PersonScraper
from linkedin_scraper.models import Person
from linkedin_scraper.core.exceptions import RateLimitError
from linkedin_scraper.core.utils import detect_rate_limit

PROFILE = """<html><head><meta charset='utf-8'></head><body><nav><a href='/feed'>Home</a></nav><main>
<h1>Alex Fixture</h1>
<div class='text-body-small inline t-black--light break-words'>Fixture City</div>
<section data-view-name='profile-card'><span aria-hidden='true'>About</span>
<span aria-hidden='true'>Synthetic professional biography.</span></section>
<section><h2>Experience</h2><ul><li>
<a href='https://www.linkedin.com/company/example-gear/'>Logo</a><a>
<span aria-hidden='true'>Sales Director</span>
<span aria-hidden='true'>Example Gear</span>
<span aria-hidden='true'>Jan 2020 - Present · 6 yrs</span>
</a></li></ul></section></main></body></html>"""


async def main():
    checks = []
    requests = []
    html = PROFILE

    def check(name, condition):
        assert condition, name
        checks.append(name)

    async with BrowserManager(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        async def route(request_route):
            requests.append(request_route.request.url)
            await request_route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)

        await browser.page.context.route("**/*", route)
        await browser.page.goto("https://www.linkedin.com/in/alex-fixture/")
        scraper = PersonScraper(browser.page)
        name, location = await scraper._get_name_and_location()
        check("name and location extraction", (name, location) == ("Alex Fixture", "Fixture City"))
        check("about extraction", await scraper._get_about() == "Synthetic professional biography.")
        experiences = await scraper._get_experiences("https://www.linkedin.com/in/alex-fixture/")
        check("employment extraction with dates", len(experiences) == 1 and
              experiences[0].institution_name == "Example Gear" and
              experiences[0].position_title == "Sales Director" and
              experiences[0].from_date == "Jan 2020" and experiences[0].to_date == "Present")
        check("DEFECT: headline and skills absent from output model",
              not {"headline", "skills"}.intersection(Person.model_fields))
        check("DEFECT: off-host URL accepted by model", Person(
            linkedin_url="https://example.invalid/?next=linkedin.com/in/fake").linkedin_url.startswith("https://example.invalid"))
        check("DEFECT: no-trailing-slash detail URL loses contact handle",
              urljoin("https://www.linkedin.com/in/alex-fixture", "details/experience") ==
              "https://www.linkedin.com/in/details/experience")
        check("DEFECT: en dash date range not separated",
              scraper._parse_work_times("Jan 2020 – Present · 6 yrs") ==
              ("Jan 2020 – Present", "", "6 yrs"))

        html = "<html><body><iframe title='captcha' src='about:blank'></iframe></body></html>"
        await browser.page.goto("https://www.linkedin.com/in/alex-fixture/")
        await detect_rate_limit(browser.page)
        check("DEFECT: CAPTCHA exception swallowed", await browser.page.locator("iframe[title='captcha']").count() == 1)
        html = "<html><body>Too many requests</body></html>"
        await browser.page.goto("https://www.linkedin.com/in/alex-fixture/")
        try:
            await detect_rate_limit(browser.page)
        except RateLimitError:
            check("text rate-limit detected", True)
        else:
            raise AssertionError("text rate limit not detected")
        html = "<html><body>Checkpoint</body></html>"
        await browser.page.goto("https://www.linkedin.com/checkpoint/")
        try:
            await detect_rate_limit(browser.page)
        except RateLimitError:
            check("checkpoint detected", True)
        else:
            raise AssertionError("checkpoint not detected")
        # Empty synthetic storage only; never load or save real credentials.
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder) / "empty-session.json"
            previous_umask = os.umask(0o022)
            try:
                await browser.save_session(str(session))
            finally:
                os.umask(previous_umask)
            check("DEFECT: session file gets mode 0644 under umask 022",
                  stat.S_IMODE(session.stat().st_mode) == 0o644)
    print(json.dumps({"mode": "synthetic offline characterization", "checks": checks,
                      "browser_requests_intercepted": len(requests), "live_requests": 0}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
