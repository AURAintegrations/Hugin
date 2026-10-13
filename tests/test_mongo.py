"""Opt-in real MongoDB storage tests with simulated providers, never live Dex."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from hugin.config import Settings
from hugin.dex import FixtureDex
from hugin.engine import Engine
from hugin.models import EnrichRequest
from hugin.sources import PublicSources
from hugin.store import MongoStore


@pytest.mark.skipif(not os.getenv('HUGIN_TEST_MONGO_URL'), reason='Opt-in actual MongoDB service required')
def test_real_mongo_job_claim_persistence_and_sync(workspace):
    _, _, _, _, fixture = workspace
    settings = Settings(mode='fixture', mongo_url=os.environ['HUGIN_TEST_MONGO_URL'], db_name='hugin_test_' + uuid.uuid4().hex)
    store = MongoStore(settings)
    try:
        store.ready()
        dex = FixtureDex(store, fixture)
        engine = Engine(settings, store, dex, PublicSources(settings, store), fixture)
        request = EnrichRequest(dex_contact_id='fixture-alex', idempotency_key='mongo-stable-operation')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: engine.submit(request), range(2)))
        assert sum(created for _, created in results) == 1
        assert len({job['id'] for job, _ in results}) == 1
        job = store.claim('mongo-worker')
        assert job and not store.claim('other-worker')
        engine.collect(job)
        engine.normalize(job)
        job['lease_until'] = 0
        store.update_job(job, 'mongo-worker')
        restored_store = MongoStore(settings)
        try:
            restored_store.ready()
            restored = Engine(settings, restored_store, FixtureDex(restored_store, fixture), PublicSources(settings, restored_store), fixture)
            recovered = restored_store.claim('restored-worker')
            assert recovered['research_complete']
            restored.process(recovered)
            saved = restored_store.get('jobs', job['id'])
            assert saved['state'] == 'completed' and saved['sync']['status'] == 'verified'
            assert len(restored_store.rows('fixture_notes')) == 1
            assert restored_store.rows('evidence')
            assert restored_store.rows('sync_receipts')
            assert restored.submit(request)[1] is False
            with pytest.raises(RuntimeError):
                store.update_job(job, 'mongo-worker')
        finally:
            restored_store.close()
    finally:
        store.client.drop_database(settings.db_name)
        store.close()
