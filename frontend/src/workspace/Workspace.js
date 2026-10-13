import React, { useCallback, useEffect, useState } from 'react';
import { Users, Layers3, FileSearch, Network, Plug, Feather, ArrowUpRight } from 'lucide-react';
import Contacts from './Contacts';
import RunDetail, { Status } from './RunDetail';
import Evidence from './Evidence';
import Integrations from './Integrations';
import { request, personName, terminal } from './api';
import './workspace.css';

const pages = [ ['Contacts', Users, 'Find a person. Build a cited professional brief.'], ['Enrichment Runs', Layers3, 'Follow research stages and verify what reached Dex.'], ['Evidence', FileSearch, 'Inspect the sources behind each finding.'], ['Connections', Network, 'Keep documented relationships and uncertainty together.'], ['Integrations', Plug, 'See configured sources, costs and access conditions.'] ];

export default function Workspace() {
  const [page, setPage] = useState('Contacts');
  const [integrations, setIntegrations] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');
  const [online, setOnline] = useState(false);
  const refresh = useCallback(async () => {
    try {
      const [health, config, runs] = await Promise.all([request('/health'), request('/integrations'), request('/enrichments')]);
      setOnline(health.status === 'ok'); setIntegrations(config); setJobs(runs.items); setError('');
    } catch (e) { setOnline(false); setError(e.message === 'Failed to fetch' ? 'Cannot reach Hugin. Start the local backend, then retry.' : e.message); }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => {
    if (!job || terminal.has(job.state)) return;
    let active = true;
    const timer = setInterval(async () => {
      try { const current = await request(`/enrichments/${job.id}`); if (active) { setJob(current); if (terminal.has(current.state)) refresh(); } }
      catch (e) { if (active) setError(e.message); }
    }, 1000);
    return () => { active = false; clearInterval(timer); };
  }, [job, refresh]);
  function submitted(current) { setJob(current); setPage('Enrichment Runs'); refresh(); }
  async function chooseRun(id) {
    try { setJob(await request(`/enrichments/${id}`)); }
    catch (e) { setError(e.message); }
  }
  const description = pages.find(item => item[0] === page)[2];
  return <div className="hg-app">
    <aside className="hg-sidebar"><a href="/" className="hg-brand"><span><Feather size={24} /></span>hugin<span className="hg-brand-dot">.</span></a><p className="hg-sidebar-label">CONTACT INTELLIGENCE</p><nav>{pages.map(([name, Icon]) => <button key={name} className={page === name ? 'active' : ''} onClick={() => setPage(name)}><Icon size={19} />{name}</button>)}</nav><div className="hg-sidebar-bottom"><p><span className={`hg-dot ${online ? 'online' : ''}`} />{online ? 'Local backend available' : 'Backend unavailable'}</p><small>Private workspace · one contact at a time</small><a href="/legacy">Archived prototype <ArrowUpRight size={13} /></a></div></aside>
    <main className="hg-main"><header className="hg-topbar"><span>Workspace / {page}</span><span className="hg-local">LOCAL ACCESS</span></header><div className="hg-content">
      {integrations?.mode === 'fixture' && <div className="hg-fixture" role="status"><strong>FIXTURE MODE</strong> Synthetic contacts and simulated source/Dex responses. No live research or external writes.</div>}
      {error && <div className="hg-error" role="alert">{error} <button onClick={refresh}>Retry connection</button></div>}
      <div className="hg-page-heading"><div><span className="hg-eyebrow">YOUR RESEARCH WORKSPACE</span><h1>{page}</h1><p>{description}</p></div><span className="hg-page-count">{jobs.length} saved run{jobs.length === 1 ? '' : 's'} loaded</span></div>
      {page === 'Contacts' ? <Contacts mode={integrations?.mode} onSubmitted={submitted} /> : page === 'Integrations' ? <Integrations data={integrations} /> : <>
        <div className="hg-run-selector"><label htmlFor="hg-run">Selected run</label><select id="hg-run" value={job?.id || ''} onChange={e => chooseRun(e.target.value)}><option value="">Choose a saved run</option>{jobs.map(run => <option key={run.id} value={run.id}>{personName(run.contact)} · {new Date(run.created_at).toLocaleString()} · {run.state}</option>)}</select><button onClick={refresh}>Refresh runs</button></div>
        {page === 'Enrichment Runs' ? <><RunDetail job={job} onUpdated={setJob} />{jobs.length > 0 && <section className="hg-card hg-recent"><h2>Recent runs</h2>{jobs.map(run => <button key={run.id} onClick={() => chooseRun(run.id)}><span>{personName(run.contact)}<small>{new Date(run.created_at).toLocaleString()}</small></span><Status value={run.state} /></button>)}</section>}</> : <Evidence job={job} connections={page === 'Connections'} />}
      </>}
    </div></main>
  </div>;
}
