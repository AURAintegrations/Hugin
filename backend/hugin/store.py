"""MongoDB in live mode; locked, atomic JSON storage exclusively for labeled fixtures."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import fcntl
import json
import os
import time
import uuid
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


class MongoStore:
    def __init__(self, settings):
        self.client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=3000)
        self.db = self.client[settings.db_name]

    def ready(self):
        self.client.admin.command('ping')
        self.db.jobs.create_index('request_key', unique=True)
        self.db.jobs.create_index([('state', 1), ('lease_until', 1)])

    def get(self, kind, key):
        row = self.db[kind].find_one({'_id': key})
        if row:
            row.pop('_id', None)
        return row

    def put(self, kind, key, value):
        self.db[kind].replace_one({'_id': key}, {'_id': key, **deepcopy(value)}, upsert=True)

    def delete(self, kind, key):
        self.db[kind].delete_one({'_id': key})

    def rows(self, kind, limit=100):
        return [dict((k, v) for k, v in row.items() if k != '_id') for row in self.db[kind].find().sort('_id', -1).limit(limit)]

    def create_job(self, job):
        try:
            self.db.jobs.insert_one({'_id': job['id'], **deepcopy(job)})
            return job, True
        except DuplicateKeyError:
            row = self.db.jobs.find_one({'request_key': job['request_key']})
            row.pop('_id', None)
            return row, False

    def update_job(self, job, owner, previous_states=None):
        query = {'_id': job['id']}
        if previous_states is not None:
            query['state'] = {'$in': list(previous_states)}
        else:
            query['lease_owner'] = owner
        result = self.db.jobs.replace_one(query, {'_id': job['id'], **deepcopy(job)})
        if not result.matched_count:
            raise RuntimeError('Job ownership changed')

    def claim(self, owner):
        stamp = time.time()
        row = self.db.jobs.find_one_and_update(
            {'state': {'$in': ['queued', 'researching', 'syncing']}, 'lease_until': {'$lt': stamp}},
            {'$set': {'lease_owner': owner, 'lease_until': stamp + 240, 'state': 'researching'}},
            sort=[('created_at', 1)], return_document=ReturnDocument.AFTER)
        if row:
            row.pop('_id', None)
        return row

    def close(self):
        self.client.close()


class FixtureStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def transaction(self):
        with open(str(self.path) + '.lock', 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = json.loads(self.path.read_text()) if self.path.exists() else {}
            yield data
            temporary = self.path.with_suffix('.' + uuid.uuid4().hex + '.tmp')
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, 'w') as output:
                json.dump(data, output)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)

    def ready(self):
        with self.transaction():
            pass

    def get(self, kind, key):
        with self.transaction() as data:
            return deepcopy(data.get(kind, {}).get(key))

    def put(self, kind, key, value):
        with self.transaction() as data:
            data.setdefault(kind, {})[key] = deepcopy(value)

    def delete(self, kind, key):
        with self.transaction() as data:
            data.get(kind, {}).pop(key, None)

    def rows(self, kind, limit=100):
        with self.transaction() as data:
            return deepcopy(list(data.get(kind, {}).values())[-limit:][::-1])

    def create_job(self, job):
        with self.transaction() as data:
            jobs = data.setdefault('jobs', {})
            for row in jobs.values():
                if row['request_key'] == job['request_key']:
                    return deepcopy(row), False
            jobs[job['id']] = deepcopy(job)
            return job, True

    def update_job(self, job, owner, previous_states=None):
        with self.transaction() as data:
            current = data.get('jobs', {}).get(job['id'])
            if not current or (previous_states is not None and current['state'] not in previous_states) or (previous_states is None and current.get('lease_owner') != owner):
                raise RuntimeError('Job ownership changed')
            data['jobs'][job['id']] = deepcopy(job)

    def claim(self, owner):
        with self.transaction() as data:
            for row in data.get('jobs', {}).values():
                if row['state'] in ('queued', 'researching', 'syncing') and row['lease_until'] < time.time():
                    row.update(lease_owner=owner, lease_until=time.time() + 240, state='researching')
                    return deepcopy(row)

    def close(self):
        pass
