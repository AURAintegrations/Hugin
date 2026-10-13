import React, { lazy, Suspense } from 'react';
import Workspace from './workspace/Workspace';
const LegacyApp = lazy(() => import('./LegacyApp'));

export default function App() {
  if (window.location.pathname === '/legacy') {
    return <><div style={{ padding: 16, background: '#fff3cd', color: '#533f03' }}>Archived prototype: sample data and demo login. This is not the contact research workspace. <a href="/">Open Hugin</a></div><Suspense fallback={<p>Loading archived prototype…</p>}><LegacyApp /></Suspense></>;
  }
  return <Workspace />;
}
