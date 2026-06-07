// routes/api.ts — REST API endpoints

import { Router } from 'express';
import { randomUUID } from 'node:crypto';
import {
  listRepos, addRepo, removeRepo,
  listFindings, getFinding, acknowledgeFinding,
  countOpenFindings, getLatestScan, getScanCount, getScanHistory,
} from '../db.js';
import { getAlertConfig, updateAlertConfig } from '../db.js';
import { rescheduleReport } from '../scheduler.js';
import { scanAllRepos } from '../scheduler.js';
import { sseClientCount, emitSse } from '../sse.js';
import { config } from '../config.js';
import {
  exchangeCodeForToken, fetchGithubUser, saveOAuthToken,
  getOAuthState, clearOAuthToken, listGithubRepos, getAuthToken,
} from '../oauth.js';

export const apiRouter = Router();

// ── Status ──

apiRouter.get('/api/status', (_req, res) => {
  const latest = getLatestScan();
  res.json({
    open_findings: countOpenFindings(),
    last_scan: latest?.completedAt || null,
    total_scans: getScanCount(),
    registered_repos: listRepos().length,
    sse_clients: sseClientCount(),
    uptime: process.uptime(),
  });
});

apiRouter.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Math.floor(process.uptime()),
    version: '0.1.0',
    platform: process.platform,
  });
});

// ── Repos ──

apiRouter.get('/api/repos', (_req, res) => {
  const repos = listRepos();
  const result = repos.map(r => {
    const findings = listFindings({ repoId: r.id });
    return {
      ...r,
      findings_total: findings.total,
      findings_open: findings.findings.filter(f => !f.acknowledged).length,
    };
  });
  res.json({ repos: result });
});

apiRouter.post('/api/repos', (req, res) => {
  const { name, type, pathOrUrl, branch } = req.body;
  if (!name || !type || !pathOrUrl) {
    return res.status(400).json({ error: 'name, type, and pathOrUrl are required' });
  }
  const repo = addRepo({
    name,
    type,
    pathOrUrl,
    branch: branch || 'main',
    enabled: true,
    cronOverride: null,
  });
  res.status(201).json(repo);
});

apiRouter.delete('/api/repos/:id', (req, res) => {
  const ok = removeRepo(req.params.id);
  if (!ok) return res.status(404).json({ error: 'Repo not found' });
  res.json({ deleted: true });
});

// ── Scan ──

apiRouter.post('/api/scan/trigger', async (_req, res) => {
  res.json({ scan_id: randomUUID(), status: 'started' });
  // fire and forget
  scanAllRepos('manual').catch(err => {
    console.error('[api] Manual scan failed:', err);
  });
});

// ── Findings ──

apiRouter.get('/api/findings', (req, res) => {
  const { severity, acknowledged, repo_id, limit, offset, from, to } = req.query;
  const result = listFindings({
    severity: severity as string | undefined,
    acknowledged: acknowledged !== undefined ? acknowledged === 'true' : undefined,
    repoId: repo_id as string | undefined,
    limit: limit ? parseInt(limit as string, 10) : undefined,
    offset: offset ? parseInt(offset as string, 10) : undefined,
  });
  // date range filter
  let filtered = result.findings;
  if (from) {
    const fromDate = new Date(from as string).toISOString();
    filtered = filtered.filter(f => f.detectedAt >= fromDate);
  }
  if (to) {
    const toDate = new Date(to as string).toISOString();
    filtered = filtered.filter(f => f.detectedAt <= toDate);
  }
  // attach repo name
  const repos = listRepos();
  const withRepoName = filtered.map(f => ({
    ...f,
    repo_name: repos.find(r => r.id === f.repoId)?.name || 'unknown',
  }));
  res.json({ total: withRepoName.length, findings: withRepoName });
});

apiRouter.get('/api/findings/:id', (req, res) => {
  const f = getFinding(req.params.id);
  if (!f) return res.status(404).json({ error: 'Finding not found' });
  const repo = listRepos().find(r => r.id === f.repoId);
  res.json({ ...f, repo_name: repo?.name || 'unknown' });
});

apiRouter.put('/api/findings/:id/acknowledge', (req, res) => {
  const { note } = req.body;
  const f = acknowledgeFinding(req.params.id, note);
  if (!f) return res.status(404).json({ error: 'Finding not found' });
  emitSse('finding:acknowledged', { id: f.id });
  res.json(f);
});

// ── Bulk acknowledge ──
apiRouter.put('/api/findings/acknowledge/bulk', (req, res) => {
  const { ids, note } = req.body;
  if (!ids || !Array.isArray(ids)) {
    return res.status(400).json({ error: 'ids array required' });
  }
  let count = 0;
  for (const id of ids) {
    const f = acknowledgeFinding(id, note || 'Bulk acknowledged');
    if (f) {
      count++;
      emitSse('finding:acknowledged', { id: f.id });
    }
  }
  res.json({ acknowledged: count });
});

// ── OAuth ──

apiRouter.get('/api/oauth/github', (_req, res) => {
  const { clientId, redirectUri } = config.github;
  if (!clientId) return res.status(500).json({ error: 'GITHUB_CLIENT_ID not configured' });
  const scope = 'repo,read:user';
  const url = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${scope}`;
  res.redirect(url);
});

apiRouter.get('/api/oauth/github/callback', async (req, res) => {
  const { code } = req.query;
  if (!code || typeof code !== 'string') {
    return res.status(400).send('<h3>Authorization failed: no code</h3>');
  }
  try {
    const { access_token } = await exchangeCodeForToken(code);
    const user = await fetchGithubUser(access_token);
    saveOAuthToken(access_token, user.login);
    res.send(`
      <html><body style="font-family:monospace;background:#0d1117;color:#3fb950;text-align:center;padding-top:80px">
        <h1>✅ GitHub Connected</h1><p>Logged in as <strong>${user.login}</strong></p>
        <p>You can close this window and return to the dashboard.</p>
        <script>setTimeout(()=>window.close(),2000)</script>
      </body></html>
    `);
  } catch (err) {
    res.status(500).send(`<h3>OAuth Error: ${err instanceof Error ? err.message : String(err)}</h3>`);
  }
});

apiRouter.get('/api/oauth/status', (_req, res) => {
  const state = getOAuthState();
  res.json({
    connected: !!state.githubToken,
    user: state.githubUser,
    connectedAt: state.connectedAt,
    clientIdConfigured: !!config.github.clientId,
  });
});

apiRouter.post('/api/oauth/disconnect', (_req, res) => {
  clearOAuthToken();
  res.json({ connected: false });
});

apiRouter.get('/api/github/repos', async (_req, res) => {
  const token = getAuthToken();
  if (!token) return res.status(401).json({ error: 'Not connected to GitHub' });
  try {
    const repos = await listGithubRepos(token);
    res.json({ repos });
  } catch (err) {
    res.status(500).json({ error: err instanceof Error ? err.message : String(err) });
  }
});

// ── Alert Config ──

apiRouter.get('/api/alerts/config', (_req, res) => {
  res.json(getAlertConfig());
});

apiRouter.put('/api/alerts/config', (req, res) => {
  const cfg = updateAlertConfig(req.body);
  if (req.body.frequency) rescheduleReport(req.body.frequency);
  res.json(cfg);
});

// ── Scan History ──

apiRouter.get('/api/scans', (_req, res) => {
  const scans = getScanHistory(30);
  const repos = listRepos();
  const repoMap = new Map(repos.map(r => [r.id, r]));
  const enriched = scans.map(s => ({
    ...s,
    repoName: repoMap.get(s.repoId)?.name || 'unknown',
    repoType: repoMap.get(s.repoId)?.type || 'unknown',
    repoUrl: repoMap.get(s.repoId)?.pathOrUrl || '',
  }));
  res.json({ scans: enriched });
});

// ── Dashboard ──

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(__dirname, '../../public');

apiRouter.get('/dashboard', (_req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});
