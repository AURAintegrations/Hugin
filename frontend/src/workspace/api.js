const base = (process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8001').replace(/\/$/, '');

export async function request(path, body) {
  const response = await fetch(`${base}/api${path}`, { method: body === undefined ? 'GET' : 'POST', headers: { 'Content-Type': 'application/json' }, ...(body === undefined ? {} : { body: JSON.stringify(body) }) });
  let result;
  try { result = await response.json(); } catch { throw new Error('Hugin returned an unreadable response. Check the backend.'); }
  if (!response.ok) {
    const detail = result.detail;
    const error = new Error(typeof detail === 'string' ? detail : detail?.message || 'The request failed.');
    error.outcome = detail?.outcome;
    error.candidates = detail?.candidates;
    throw error;
  }
  return result;
}

export function personName(person) { return person?.name || [person?.first_name, person?.last_name].filter(Boolean).join(' ') || person?.id || 'Unnamed contact'; }
export const terminal = new Set(['completed', 'dry_run', 'no_results', 'sync_failed', 'failed']);
