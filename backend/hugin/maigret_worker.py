"""Offline Maigret detector. Network access stays in Hugin's verified transport.

Run with the isolated collector Python; consume bounded pre-fetched responses.
Do not call Maigret's network checkers, which disable certificate verification.
"""
import json
import logging
import sys
from importlib.metadata import version
from importlib.resources import files
from maigret.checking import process_site_result
from maigret.sites import MaigretDatabase
from maigret.result import MaigretCheckStatus


def detect(payload):
    if version('maigret') != '0.6.6':
        raise ValueError('Unsupported collector version')
    database = MaigretDatabase().load_from_str(files('maigret').joinpath('resources/data.json').read_text())
    site = database.sites_dict['GitHub']
    username = payload['username']
    info = {'username': username, 'parsing_enabled': False, 'url_user': site.url.format(username=username), 'url_probe': site.url_probe.format(username=username)}
    logger = logging.getLogger('hugin.maigret'); logger.disabled = True
    result = process_site_result((payload['body'], 200, None), None, logger, info, site)
    return {'claimed': result['status'].status == MaigretCheckStatus.CLAIMED, 'profile_url': info['url_user'], 'collector': 'maigret', 'version': '0.6.6'}


if __name__ == '__main__':
    try:
        payload = json.loads(sys.stdin.read(1_010_000))
        print(json.dumps(detect(payload)))
    except Exception:
        # No upstream response, usernames or exception messages in stderr.
        print(json.dumps({'error': 'Collector could not classify this response'}))
        sys.exit(2)
