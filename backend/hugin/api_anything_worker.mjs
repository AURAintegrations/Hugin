/** Offline API Anything bridge. Hugin owns transport, source policy and budgets. */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
const here = dirname(new URL(import.meta.url).pathname);
const allowed = ['openalex', 'europepmc', 'industry_news'];
try {
  const payload = JSON.parse(readFileSync(0, 'utf8'));
  const lock = JSON.parse(readFileSync(join(here, 'api_anything.lock.json'), 'utf8'));
  const base = payload.module_dir;
  const pkg = JSON.parse(readFileSync(join(base, 'package.json'), 'utf8'));
  if (pkg.version !== lock.version) throw Error('version');
  for (const [file, digest] of Object.entries(lock.files)) {
    if (createHash('sha256').update(readFileSync(join(base, file))).digest('hex') !== digest) throw Error('revision');
  }
  // Components used below are pure. Never use call(), healing, browser or session import.
  globalThis.fetch = () => { throw Error('worker network disabled'); };
  const { parseSite } = await import(pathToFileURL(join(base, 'dist/spec.js')));
  const { buildRequest } = await import(pathToFileURL(join(base, 'dist/http.js')));
  const { extract } = await import(pathToFileURL(join(base, 'dist/extract.js')));
  if (payload.action === 'learn') {
    const { learnOperation } = await import(pathToFileURL(join(base, 'dist/learn.js')));
    const result = learnOperation(payload.input);
    console.log(JSON.stringify({ operation: result.operation, warnings: result.warnings }));
  } else {
    if (!allowed.includes(payload.source)) throw Error('source');
    const site = parseSite(JSON.parse(readFileSync(join(here, 'api_operations', payload.source + '.json'), 'utf8')));
    const op = site.operations[0];
    if (!op.readOnly || op.minTier !== 1 || op.request.method !== 'GET' || op.slots.some(s => s.ref) || op.volatile.length) throw Error('policy');
    if (payload.action === 'build') {
      const req = buildRequest(op, payload.args, { cookies: [], values: {} });
      if (req.method !== 'GET' || req.body || Object.keys(req.headers).some(k => /cookie|authorization/i.test(k))) throw Error('policy');
      console.log(JSON.stringify({ url: req.url }));
    } else if (payload.action === 'extract') {
      const result = extract(op.response, payload.body);
      if (!Array.isArray(result)) throw Error('schema');
      console.log(JSON.stringify({ records: result.slice(0, 5) }));
    } else throw Error('action');
  }
} catch {
  console.log(JSON.stringify({ error: 'API Anything operation, version or response is unsupported.' }));
  process.exitCode = 1;
}
