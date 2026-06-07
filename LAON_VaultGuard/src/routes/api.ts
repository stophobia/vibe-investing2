// routes/api.ts — REST API endpoints

import { Router } from 'express';
import { randomUUID } from 'node:crypto';
import {
  listRepos, addRepo, removeRepo, getRepo,
  listFindings, getFinding, acknowledgeFinding, unacknowledgeFinding, addFindingComment,
  countOpenFindings, getLatestScan, getScanCount, getScanHistory,
} from '../db.js';
import { getAlertConfig, updateAlertConfig } from '../db.js';
import { rescheduleReport } from '../scheduler.js';
import { scanAllRepos } from '../scheduler.js';
import { scanRepository } from '../scan-runner.js';
import { checkGitInstalled } from '../git-monitor.js';
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
    version: '0.3.0',
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
  if (!clientId) {
    return res.status(200).json({
      error: 'GITHUB_CLIENT_ID not configured',
      message: 'Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env to enable GitHub OAuth.',
      docs: 'docs/GitHub_OAuth.md',
    });
  }
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

// ── Scan specific repo ──

apiRouter.post('/api/scan/repo/:id', async (req, res) => {
  const repo = getRepo(req.params.id);
  if (!repo) return res.status(404).json({ error: 'Repo not found' });
  res.json({ scan_id: randomUUID(), status: 'started', repo: repo.name });
  scanRepository(repo, 'manual').catch(err => {
    console.error('[api] Repo scan failed:', err);
  });
});

// ── Un-acknowledge ──

apiRouter.put('/api/findings/:id/unacknowledge', (req, res) => {
  const result = unacknowledgeFinding(req.params.id);
  if (!result) return res.status(404).json({ error: 'Finding not found' });
  emitSse('finding:acknowledged', { id: result.id, acknowledged: false });
  res.json(result);
});

// ── Add comment ──

apiRouter.put('/api/findings/:id/comment', (req, res) => {
  const { comment } = req.body;
  if (!comment) return res.status(400).json({ error: 'comment required' });
  const result = addFindingComment(req.params.id, comment);
  if (!result) return res.status(404).json({ error: 'Finding not found' });
  res.json(result);
});

// ── HTML Report ──

apiRouter.get('/api/report', (_req, res) => {
  const repos = listRepos();
  const repoMap = new Map(repos.map(r => [r.id, r.name]));
  const { findings } = listFindings({ acknowledged: false, limit: 500 });
  const bySeverity = (s: string) => findings.filter(f => f.severity === s).length;
  const rows = findings.map(f => `
    <tr>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><span style="color:${f.severity === 'critical' ? '#f85149' : f.severity === 'high' ? '#d29922' : '#58a6ff'}">${f.severity.toUpperCase()}</span></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${repoMap.get(f.repoId) || '-'}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${f.provider} — ${f.secretType}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><code>${f.filePath}${f.line ? `:${f.line}` : ''}</code></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><code>${f.maskedFingerprint}</code></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d;font-size:12px">${f.detectedAt.slice(0, 10)}</td>
    </tr>`).join('');

  const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>LAON VaultGuard Report</title></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:monospace;padding:20px">
<h1 style="color:#3fb950">LAON VaultGuard — Security Report</h1>
<p>Device: ${config.deviceName} · Generated: ${new Date().toISOString()} · Repos: ${repos.length}</p>
<hr style="border-color:#30363d">
<div style="display:flex;gap:16px;margin:16px 0">
  <div style="background:#161b22;padding:12px;border-radius:8px;flex:1"><span style="color:#8b949e">OPEN</span><br><span style="font-size:24px;color:#f85149">${findings.length}</span></div>
  <div style="background:#161b22;padding:12px;border-radius:8px;flex:1"><span style="color:#8b949e">CRITICAL</span><br><span style="font-size:24px;color:#f85149">${bySeverity('critical')}</span></div>
  <div style="background:#161b22;padding:12px;border-radius:8px;flex:1"><span style="color:#8b949e">HIGH</span><br><span style="font-size:24px;color:#d29922">${bySeverity('high')}</span></div>
</div>
<table style="width:100%;border-collapse:collapse;background:#161b22;border:1px solid #30363d">
<thead><tr style="text-align:left;color:#8b949e"><th style="padding:10px">Severity</th><th>Repo</th><th>Type</th><th>File</th><th>Fingerprint</th><th>Date</th></tr></thead>
<tbody>${rows || '<tr><td colspan="6" style="padding:20px;text-align:center;color:#3fb950">No open findings</td></tr>'}</tbody></table>
<p style="color:#8b949e;margin-top:16px;font-size:12px">LAON VaultGuard v0.3.0 · ${config.deviceName}</p>
</body></html>`;
  res.set('Content-Type', 'text/html; charset=utf-8');
  res.send(html);
});

// ── Dashboard ──

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(__dirname, '../../public');

apiRouter.get('/dashboard', (_req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});
