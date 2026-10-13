"""Company-first public collection; a candidate site never proves personal affiliation."""
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import re
import time
from lxml import html as lh
from .config import ConnectorError
from .models import fingerprint, now
from .sources import page_observations


def compact(value):
    return re.sub(r'[^a-z0-9]', '', str(value).casefold())


def roots(contact, supplied=()):
    if supplied:
        return list(dict.fromkeys(supplied))[:3], 'supplied_candidate'
    website = contact.get('website', '')
    if website and not urlparse(website).path.rstrip('/'):
        return [website], 'existing_website_candidate'
    company = re.sub(r'\b(incorporated|inc|llc|ltd|limited|corp|corporation)\.?$', '', str(contact.get('company') or ''), flags=re.I).strip()
    label = compact(company)
    if not re.fullmatch(r'[a-z][a-z0-9]{2,39}', label):
        return [], 'no_domain_candidate'
    # One conventional hostname hypothesis, not a domain scan or an identity assertion.
    return [f'https://www.{label}.com/'], 'company_name_hypothesis'


def page_context(contact, url, document):
    tree = lh.fromstring(document)
    title = ' '.join(tree.xpath('//title/text()'))
    published_links = [(node.get('href'), node.text_content()) for node in tree.xpath('//a[@href]')]
    for node in tree.xpath('//script|//style|//nav|//header|//footer|//aside|//form'):
        node.drop_tree()
    company = str(contact.get('company') or '')
    brand = compact(company)
    # Preserve observations describing the contact only when identity signals match.
    personal = [row for row in page_observations(contact, url, document) if 'full_name' in row['identity']['signals']]
    for row in personal:
        row['subject_type'] = 'person'
    body = tree.xpath('//main')
    main = body[0] if body else tree
    main_text = ' '.join(main.text_content().split())
    if not brand or brand not in compact(title + ' ' + main_text[:2000]):
        return personal, []
    # Source excerpts, not generated assertions. Keep promotional rankings attributed.
    paragraphs = []
    for node in main.xpath('.//p|.//li'):
        if node.xpath('ancestor::nav|ancestor::footer|ancestor::header|ancestor::aside|ancestor::form'):
            continue
        text = ' '.join(node.text_content().split())
        if not 60 <= len(text) <= 1200 or '?' in text or any(word in text.casefold() for word in ('cookie', 'newsletter', 'shopping cart', 'promo code', 'offer expires', 'ground shipping', 'quiz', 'marketing messages')):
            continue
        if text not in paragraphs:
            paragraphs.append(text)
    context = []
    paragraphs.sort(key=lambda text: (brand not in compact(text), 'dealer' not in text.casefold()))
    for excerpt in paragraphs[:2]:
        excerpt = excerpt[:500]
        context.append({'kind': 'company_context', 'value': f'Candidate company site reports: {excerpt}', 'excerpt': excerpt, 'url': url,
                        'identity': {'confidence': 'low', 'signals': ['company_name_on_candidate_site'], 'conflicts': []},
                        'subject_type': 'company', 'provider_review_status': 'pending',
                        'evidence_origin': 'public_company_candidate', 'company_name': company})
    # A blog index supports publication titles, not proof of authorship by this contact.
    if 'blog' in urlparse(url).path.casefold():
        publications = []
        for href, label in published_links:
            target = urljoin(url, href)
            label = ' '.join(label.split())
            if urlparse(target).hostname == urlparse(url).hostname and '/blog/' in urlparse(target).path and len(label) >= 30 and (target, label) not in publications:
                publications.append((target, label))
        publications.sort(key=lambda item: not any(word in item[1].casefold() for word in ('outdoor', 'event', 'brand', 'trade show', 'dealer')))
        if publications:
            context = []
            for target, label in publications[:2]:
                excerpt = f'Company publication listed: {label[:300]} ({target})'
                context.append({'kind': 'company_context', 'value': excerpt, 'excerpt': excerpt[:500], 'url': url, 'identity': {'confidence': 'low', 'signals': ['company_name_on_candidate_site'], 'conflicts': []}, 'subject_type': 'company', 'provider_review_status': 'pending', 'evidence_origin': 'public_company_candidate', 'company_name': company})
    # Follow only links actually published on the same host; no invented deep paths.
    links = []
    priorities = ('about', 'team', 'leadership', 'dealer', 'dealers', 'press', 'news', 'newsroom', 'blog', 'partner', 'partners')
    for href, link_text in published_links:
        target = urljoin(url, href)
        p = urlparse(target)
        label = (link_text + ' ' + p.path).casefold()
        if p.scheme == 'https' and p.hostname == urlparse(url).hostname and not p.query and not p.fragment and any(re.search(r'(?<![a-z])' + word + r'(?![a-z])', label) for word in priorities):
            links.append(target)
    links = sorted(set(links), key=lambda target: min((i for i, word in enumerate(priorities) if word in target.casefold()), default=99))
    return personal + context, links[:5]


def collect(public, store, contact, budget, supplied=(), max_pages=3, fixture_pages=None):
    candidates, origin = roots(contact, supplied)
    if not candidates:
        raise ConnectorError('not_searched', 'No company domain candidate is available.')
    key = fingerprint({'company_web': 2, 'contact': contact, 'candidates': candidates, 'max_pages': max_pages, 'fixture': fixture_pages is not None})
    cached = store.get('source_cache', key)
    if cached and time.time() - cached['cached_at'] < 86400:
        return cached['observations'], cached['outcomes'], True
    queue = list(candidates)
    visited, observations, outcomes, robots_cache = set(), [], [], {}
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            if fixture_pages is not None:
                budget.take()
                document = fixture_pages.get(url)
                if document is None:
                    raise ConnectorError('no_result', 'No synthetic company page exists for this candidate.')
            else:
                host = urlparse(url).hostname
                public.validate_url(url, (host,))
                if host not in robots_cache:
                    try:
                        _, rules = public.get(f'https://{host}/robots.txt', budget, (host,))
                    except ConnectorError as error:
                        if error.outcome != 'no_result':
                            raise
                        rules = ''
                    robots = RobotFileParser(); robots.parse(rules.splitlines())
                    robots_cache[host] = robots
                if not robots_cache[host].can_fetch('HuginResearch', url):
                    raise ConnectorError('unsupported', 'Company source robots policy disallows this page.')
                _, document = public.get(url, budget, (host,))
            rows, links = page_context(contact, url, document)
            stamp = now()
            for row in rows:
                row.update(provider='company_web', retrieved_at=stamp)
            observations.extend(rows)
            queue.extend(link for link in links if link not in visited and link not in queue)
            outcomes.append({'url': url, 'outcome': 'ok' if rows else 'no_result', 'count': len(rows), 'candidate_origin': origin, 'message': 'Candidate company context; personal affiliation is not confirmed.'})
        except ConnectorError as error:
            outcomes.append({'url': url, 'outcome': error.outcome, 'count': 0, 'candidate_origin': origin, 'message': error.message})
        except (ValueError, lh.etree.ParserError):
            outcomes.append({'url': url, 'outcome': 'unsupported', 'count': 0, 'candidate_origin': origin, 'message': 'Company page could not be parsed.'})
    if not any(row['outcome'] in ('timeout', 'quota_exhausted', 'unavailable') for row in outcomes):
        store.put('source_cache', key, {'observations': observations, 'outcomes': outcomes, 'cached_at': time.time()})
    return observations, outcomes, False
