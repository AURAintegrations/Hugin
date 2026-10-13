import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'backend'))
from hugin.config import Settings
from hugin.dex import FixtureDex
from hugin.engine import Engine
from hugin.sources import PublicSources
from hugin.store import FixtureStore


@pytest.fixture
def workspace(tmp_path):
    fixture = json.loads((Path(__file__).parents[1] / 'backend/hugin/fixtures/demo.json').read_text())
    settings = Settings(mode='fixture', fixture_store=str(tmp_path / 'data.json'), dex_key='', brave_key='')
    store = FixtureStore(settings.fixture_store)
    dex = FixtureDex(store, fixture)
    engine = Engine(settings, store, dex, PublicSources(settings, store), fixture)
    return settings, store, dex, engine, fixture


def run(engine, store, request):
    job, _ = engine.submit(request)
    claimed = store.claim('test-worker')
    assert claimed and claimed['id'] == job['id']
    engine.process(claimed)
    return store.get('jobs', job['id'])
