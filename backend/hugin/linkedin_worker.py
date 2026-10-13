"""Pinned parser; offline Chromium only. No login, session files or live URLs."""
import asyncio
import json
import logging
import sys
from importlib.metadata import version, distribution
from playwright.async_api import async_playwright
from linkedin_scraper import PersonScraper

logging.disable(logging.CRITICAL)


async def parse(payload):
    if version('linkedin_scraper') != '3.1.2':
        raise ValueError('Unsupported parser version')
    origin = json.loads(distribution('linkedin_scraper').read_text('direct_url.json') or '{}')
    if origin.get('vcs_info', {}).get('commit_id') != 'b1cdc1c0e85bee8764d62565d229c682e5eb81bb':
        raise ValueError('Unsupported parser revision')
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path=payload['chromium'], headless=True, args=['--no-sandbox'])
        try:
            context = await browser.new_context(java_script_enabled=False, service_workers='block')
            await context.route('**/*', lambda route: route.abort())
            page = await context.new_page()
            page.set_default_timeout(1500)
            await page.set_content(payload['html'], wait_until='domcontentloaded', timeout=3000)
            scraper = PersonScraper(page)
            name, _ = await scraper._get_name_and_location()
            about = await scraper._get_about()
            name = name[:200]
            about = about[:1200] if about else None
            result = {'name': name, 'about': about, 'experiences': [], 'educations': [], 'coverage': {'name': 'parsed' if name != 'Unknown' else 'absent', 'about': 'parsed' if about else 'absent', 'skills': 'unsupported', 'contacts': 'not_searched', 'relationships': 'not_searched'}}
            headline = page.locator('main .text-body-medium.break-words, [data-hugin-field="headline"]').first
            result['headline'] = (await headline.inner_text()).strip()[:1200] if await headline.count() else None
            result['coverage']['headline'] = 'parsed' if result['headline'] else 'absent'
            for label, key, method in [('Experience', 'experiences', scraper._parse_main_page_experience), ('Education', 'educations', scraper._parse_main_page_education)]:
                heading = page.locator('h2').filter(has_text=label).first
                section = heading.locator('xpath=ancestor::*[.//ul or .//ol][1]')
                rows = await section.locator('ul > li, ol > li').all() if await heading.count() and await section.count() else []
                for row in rows[:20]:
                    parsed = await method(row)
                    if parsed:
                        result[key].append(parsed.model_dump())
                result['coverage'][key] = 'parsed' if result[key] else 'unparsed' if rows else 'absent'
            return result
        finally:
            await browser.close()


if __name__ == '__main__':
    try:
        payload = json.loads(sys.stdin.read(1_100_000))
        print(json.dumps(asyncio.run(parse(payload))))
    except Exception:
        print(json.dumps({'error': 'parser_unavailable'}))
        sys.exit(1)
