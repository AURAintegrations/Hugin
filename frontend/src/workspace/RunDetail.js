import React, { useState } from 'react';
import { request, personName } from './api';

export function Status({ value }) { return <span className={`hg-status hg-${value}`}>{String(value || 'unknown').replaceAll('_', ' ')}</span>; }

export default function RunDetail({ job, onUpdated }) {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (!job) return <div className="hg-card hg-empty"><h2>No run selected</h2><p>Choose a contact to begin, or select a saved run.</p></div>;
  async function retry() {
    setBusy(true); setError('');
    try { const result = await request(`/enrichments/${job.id}/retry-sync`, {}); onUpdated(result.job); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <div className="hg-run-detail">
    <section className="hg-card">
      <div className="hg-card-heading"><div><span className="hg-eyebrow">ENRICHMENT RUN</span><h2>{personName(job.contact)}</h2><p className="hg-muted hg-small">{new Date(job.created_at).toLocaleString()} · <code>{job.id}</code></p></div><Status value={job.state} /></div>
      <div className="hg-facts"><div><span>Current stage</span><strong>{job.stage.replaceAll('_', ' ')}</strong></div><div><span>Paid request attempts</span><strong>{job.costs.paid_attempts}</strong></div><div><span>Write policy</span><strong>{job.options.dry_run ? 'Dry run' : job.options.write_policy.replaceAll('_', ' ')}</strong></div></div>
      {job.error && <p role="alert" className="hg-error">{job.error.message}</p>}
      {job.research_scope === 'company_context_only' && <p className="hg-callout">Company context only. No new personal facts were confirmed; the contact's affiliation remains unverified.</p>}{job.state === 'no_results' && <p role="status" className="hg-error">No supported findings. Nothing was saved to Dex. Review the source failures and configure another accessible source for a new run.</p>}
      <h3>Source outcomes</h3>
      {job.outcomes.length === 0 ? <p className="hg-muted">Waiting for the worker to begin.</p> : <div className="hg-outcomes">{job.outcomes.map((outcome, index) => <div key={`${outcome.id}-${index}`}><div><strong>{outcome.source.startsWith('public_pages:') ? 'Public page' : outcome.source.replaceAll('_', ' ')}</strong><p>{outcome.message}</p>{outcome.acquisition && <p className="hg-small">Input: {outcome.acquisition.replaceAll("_", " ")}. {outcome.cache_hit ? "Cached evidence." : ""}</p>}{outcome.coverage && <p className="hg-small">Sections: {Object.entries(outcome.coverage).map(([section, state]) => `${section}: ${state}`).join(" · ")}</p>}{outcome.pages && <div className="hg-small">{outcome.pages.map(item => <p key={item.url}><a href={item.url} target="_blank" rel="noreferrer">{item.url}</a> · {item.outcome.replaceAll("_", " ")}: {item.message}</p>)}</div>}{outcome.url && <a href={outcome.url} target="_blank" rel="noreferrer">{outcome.url}</a>}</div><Status value={outcome.outcome} /></div>)}</div>}
    </section>
    {job.account_candidates?.length > 0 && <section className="hg-card"><h2>Account candidates</h2><p className="hg-muted">These accounts were discovered by a collector. Matching handles alone do not link them to this contact.</p>{job.account_candidates.map(candidate => <article key={candidate.url}><a href={candidate.url} target="_blank" rel="noreferrer">{candidate.url}</a> <Status value={candidate.review_status} /><p className="hg-small">Identity: {candidate.identity.confidence}. Signals: {candidate.identity.signals.join(', ') || 'None'}. {candidate.reason}</p></article>)}</section>}
    {job.entity_snapshot && <section className="hg-card"><h2>Entity snapshot</h2><p className="hg-muted">Dated person, company and relationship records using FollowTheMoney schemas. Existing contact context is separate from collected claims; unresolved entities are not automatically merged.</p>{job.entity_snapshot.edges.map(row => <article key={row.entity.id}><strong>{row.entity.schema}</strong> <Status value={row.review_status} /><p className="hg-small">{row.entity.properties.role?.join(', ') || row.entity.properties.relationship?.join(', ') || 'Affiliation assertion'} · {row.evidence_ids.length} evidence reference(s)</p></article>)}</section>}
    {job.note && <section className="hg-card"><div className="hg-card-heading"><h2>{job.state === 'no_results' ? 'Run report · kept in Hugin' : 'Cited research note'}</h2><Status value={job.editorial.status} /></div><p className="hg-small hg-muted">Source claims and identity confidence stay visible. Suggested follow-ups are separate from factual findings.</p><pre className="hg-note">{job.note}</pre></section>}
    <section className="hg-card"><h2>Dex sync</h2><Status value={job.sync.status} />{job.sync.message && <p>{job.sync.message}</p>}{job.sync.note_id && <p className="hg-small">Note ID: <code>{job.sync.note_id}</code></p>}{job.sync.note_verified && <p>Note content and contact association matched the Dex readback.{job.mode === 'fixture' ? ' This was a simulated response.' : ''}</p>}{job.sync.additions && <p className="hg-small">Fields added: {Object.keys(job.sync.additions.fields).join(', ') || 'None'}. Related links added: {job.sync.additions.related_contact_ids.length}.</p>}{job.state === 'sync_failed' && <button disabled={busy} onClick={retry}>Retry sync only</button>}{error && <p className="hg-error" role="alert">{error}</p>}
      <h3>Proposed field changes</h3>{job.proposals.length === 0 ? <p className="hg-muted">No field changes proposed.</p> : <div className="hg-table-wrap"><table><thead><tr><th>Field</th><th>Finding</th><th>Review</th></tr></thead><tbody>{job.proposals.map(proposal => <tr key={proposal.id}><td>{proposal.field}</td><td>{proposal.value}<small>{proposal.reason}</small></td><td><Status value={proposal.sync_status || proposal.status} /></td></tr>)}</tbody></table></div>}
    </section>
  </div>;
}
