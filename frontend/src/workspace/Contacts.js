import React, { useState } from 'react';
import { Search, ArrowRight, UserRound } from 'lucide-react';
import { request, personName } from './api';

export default function Contacts({ onSubmitted, mode }) {
  const [query, setQuery] = useState('');
  const [contacts, setContacts] = useState(null);
  const [selected, setSelected] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [dryRun, setDryRun] = useState(false);
  const [fillMissing, setFillMissing] = useState(false);
  const [brave, setBrave] = useState(false);
  const [dexResearch, setDexResearch] = useState(false);
  const [key, setKey] = useState(null);
  const [linkedinHtml, setLinkedinHtml] = useState(null);
  const [profileFile, setProfileFile] = useState('');

  async function search(event) {
    event.preventDefault(); setBusy(true); setError('');
    try { const data = await request(`/contacts?q=${encodeURIComponent(query)}`); setContacts(data.items); setSelected(null); setKey(null); setLinkedinHtml(null); setProfileFile(''); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function choose(contact) {
    setBusy(true); setError('');
    try { const result = await request(`/contacts/${encodeURIComponent(contact.id)}`); setSelected(result.contact); setKey(null); setLinkedinHtml(null); setProfileFile(''); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function enrich() {
    const operationKey = key || window.crypto.randomUUID();
    setKey(operationKey); setBusy(true); setError('');
    try {
      const data = await request('/enrichments', { dex_contact_id: selected.id, idempotency_key: operationKey, dry_run: dryRun, write_policy: fillMissing || dexResearch ? 'fill_missing' : 'notes_only', sources: ['dex_cached', 'company_web', 'api_anything', 'linkedin', 'public_discovery', 'maigret', 'public_pages', ...(brave ? ['brave'] : []), ...(dexResearch ? ['dex_fresh'] : [])], ...(linkedinHtml !== null ? { linkedin_html: linkedinHtml } : {}), paid_budget_units: Number(brave) + Number(dexResearch), allow_fresh_dex: dexResearch, timeout_seconds: dexResearch ? 180 : 90 });
      onSubmitted(data.job);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  const changeOption = (setter) => (event) => { setter(event.target.checked); setKey(null); };
  async function attachProfile(event) {
    const file = event.target.files[0];
    setLinkedinHtml(null); setProfileFile(''); setKey(null); setError('');
    if (!file) return;
    if (file.size > 1000000) { setError('Profile HTML must be under one megabyte.'); return; }
    setBusy(true);
    try { setLinkedinHtml(await file.text()); setProfileFile(file.name); }
    catch (e) { setError('Could not read the profile HTML file.'); }
    finally { setBusy(false); }
  }
  return <div className="hg-columns">
    <section className="hg-card">
      <div className="hg-card-heading"><h2>Choose a contact</h2><span className="hg-muted">One person per run</span></div>
      <form onSubmit={search} className="hg-search"><Search size={18} /><input aria-label="Search Dex contacts" placeholder="Name, email or professional profile" value={query} onChange={e => setQuery(e.target.value)} /><button disabled={busy}>Search Dex</button></form>
      <p className="hg-muted hg-small">Search returns up to 50 contacts. Choose the exact record before research starts.</p>
      {error && <div role="alert" className="hg-error">{error}</div>}
      <div className="hg-contact-list">
        {contacts === null && <div className="hg-empty"><UserRound size={32} /><h3>Start with someone you know</h3><p>Find their Dex record, then research and save a cited note.</p></div>}
        {contacts?.length === 0 && <p className="hg-empty">No matching contacts. Try a different query.</p>}
        {contacts?.map(contact => <button key={contact.id} className={`hg-contact ${selected?.id === contact.id ? 'selected' : ''}`} onClick={() => choose(contact)} disabled={busy}><div className="hg-avatar">{personName(contact).slice(0, 1)}</div><div><strong>{personName(contact)}</strong><span>{contact.company || 'Company not recorded'}</span><small>{contact.id}</small></div><ArrowRight size={17} /></button>)}
      </div>
    </section>
    <section className="hg-card">
      <h2>Research & save</h2>
      {selected ? <>
        <div className="hg-selected"><span className="hg-eyebrow">SELECTED DEX CONTACT</span><h3>{personName(selected)}</h3><p>{[selected.job_title, selected.company].filter(Boolean).join(' · ') || 'No role or company recorded'}</p><code>{selected.id}</code></div>
        <div className="hg-policies">
          <label><input type="checkbox" checked={dryRun} disabled={dexResearch} onChange={changeOption(setDryRun)} /><div><strong>Dry run</strong><span>Store findings in Hugin without writing to Dex.</span></div></label>
          <label><input type="checkbox" checked={fillMissing || dexResearch} disabled={dexResearch} onChange={changeOption(setFillMissing)} /><div><strong>Fill verified missing profiles</strong><span>Website and LinkedIn only. Populated fields stay unchanged.</span></div></label>
          <label><input type="checkbox" checked={dexResearch} onChange={event => { setDexResearch(event.target.checked); if (event.target.checked) setDryRun(false); setKey(null); }} /><div><strong>Use Dex Research for web discovery</strong><span>Authorize one paid research request with the existing Dex key. Dex may fill empty verified profile fields and replace stored research. It never overwrites populated fields. No forced refresh.</span></div></label>
          <label><input type="checkbox" checked={brave} onChange={changeOption(setBrave)} /><div><strong>Use Brave Search</strong><span>Authorize up to one search unit. Provider charges may apply.</span></div></label>
        </div>
        <div className="hg-callout"><label htmlFor="linkedin-profile-html"><strong>LinkedIn profile HTML (optional)</strong></label><p className="hg-small">Upload profile HTML you have permission to use. Hugin parses professional sections without executing scripts. Without a file, it checks the backend's authorized session and source access.</p><input key={`${selected.id}:${profileFile}`} id="linkedin-profile-html" type="file" accept=".html,.htm,text/html" disabled={busy} onChange={attachProfile} />{profileFile && <p className="hg-small">Attached: {profileFile} <button onClick={() => { setLinkedinHtml(null); setProfileFile(''); setKey(null); }}>Remove</button></p>}</div>
        <p className="hg-small hg-muted">Each run attempts company-site research, LinkedIn extraction, public web discovery, Maigret professional-account discovery, cached research and permitted page extraction. Search may be unavailable or challenged. Matching usernames stay candidates until identity is checked. Empty runs stay in Hugin and write nothing to Dex. Paid providers are off unless selected.</p>
        <button className="hg-primary hg-wide" onClick={enrich} disabled={busy}>{busy ? 'Submitting…' : dryRun ? 'Research without Dex writes' : mode === 'fixture' ? 'Run simulated enrichment' : 'Enrich & save to Dex'}<ArrowRight size={18} /></button>
      </> : <div className="hg-empty"><p>Select a contact to see the write policy and begin.</p></div>}
    </section>
  </div>;
}
