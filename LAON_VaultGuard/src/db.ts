// db.ts — file-based JSON storage (macOS)
// Structure: data/repos.json, data/findings.json, data/logs/

import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import type { Repository, ScanRun, Finding } from './types.js';
import { config } from './config.js';

const DATA_DIR = path.resolve(config.db.path);

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function readJson<T>(filePath: string, fallback: T): T {
  try {
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf-8')) as T;
    }
  } catch { /* corrupt file, return fallback */ }
  return fallback;
}

function writeJson(filePath: string, data: unknown) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

// ── Repos ──

const REPOS_FILE = path.join(DATA_DIR, 'repos.json');

export function listRepos(): Repository[] {
  return readJson<Repository[]>(REPOS_FILE, []);
}

export function getRepo(id: string): Repository | undefined {
  return listRepos().find(r => r.id === id);
}

export function addRepo(input: Omit<Repository, 'id' | 'lastScan' | 'createdAt'>): Repository {
  const repos = listRepos();
  const repo: Repository = {
    ...input,
    id: randomUUID(),
    lastScan: null,
    createdAt: new Date().toISOString(),
  };
  repos.push(repo);
  writeJson(REPOS_FILE, repos);
  logAudit('repo_added', 'info', `Repo added: ${repo.name} (${repo.type})`, { repoId: repo.id });
  return repo;
}

export function removeRepo(id: string): boolean {
  const repos = listRepos();
  const idx = repos.findIndex(r => r.id === id);
  if (idx === -1) return false;
  const removed = repos.splice(idx, 1)[0];
  writeJson(REPOS_FILE, repos);
  logAudit('repo_removed', 'info', `Repo removed: ${removed.name}`, { repoId: id });
  return true;
}

export function updateRepoLastScan(id: string) {
  const repos = listRepos();
  const repo = repos.find(r => r.id === id);
  if (repo) {
    repo.lastScan = new Date().toISOString();
    writeJson(REPOS_FILE, repos);
  }
}

// ── Findings ──

const FINDINGS_FILE = path.join(DATA_DIR, 'findings.json');

export function listFindings(filter?: {
  severity?: string;
  acknowledged?: boolean;
  repoId?: string;
  limit?: number;
  offset?: number;
}): { total: number; findings: Finding[] } {
  const all = readJson<Finding[]>(FINDINGS_FILE, []);
  let filtered = all;

  if (filter?.severity) {
    filtered = filtered.filter(f => f.severity === filter.severity);
  }
  if (filter?.acknowledged !== undefined) {
    filtered = filtered.filter(f => f.acknowledged === filter.acknowledged);
  }
  if (filter?.repoId) {
    filtered = filtered.filter(f => f.repoId === filter.repoId);
  }

  filtered.sort((a, b) => new Date(b.detectedAt).getTime() - new Date(a.detectedAt).getTime());
  const total = filtered.length;
  const offset = filter?.offset || 0;
  const limit = filter?.limit || 50;

  return { total, findings: filtered.slice(offset, offset + limit) };
}

export function getFinding(id: string): Finding | undefined {
  return readJson<Finding[]>(FINDINGS_FILE, []).find(f => f.id === id);
}

export function saveFindings(findings: Finding[]) {
  const existing = readJson<Finding[]>(FINDINGS_FILE, []);
  existing.push(...findings);
  writeJson(FINDINGS_FILE, existing);
}

export function acknowledgeFinding(id: string, note?: string): Finding | undefined {
  const all = readJson<Finding[]>(FINDINGS_FILE, []);
  const f = all.find(f => f.id === id);
  if (!f) return undefined;
  f.acknowledged = true;
  f.acknowledgedAt = new Date().toISOString();
  f.acknowledgedNote = note || null;
  writeJson(FINDINGS_FILE, all);
  logAudit('finding_acknowledged', 'info', `Finding acknowledged: ${f.id}`, { findingId: id });
  return f;
}

export function countOpenFindings(): number {
  return readJson<Finding[]>(FINDINGS_FILE, []).filter(f => !f.acknowledged).length;
}

// ── Scan Runs ──

const SCANS_DIR = path.join(DATA_DIR, 'scans');

export function saveScanRun(run: ScanRun) {
  ensureDir(SCANS_DIR);
  const file = path.join(SCANS_DIR, `${run.id}.json`);
  writeJson(file, run);
}

export function getScanRun(id: string): ScanRun | undefined {
  const file = path.join(SCANS_DIR, `${id}.json`);
  return readJson<ScanRun | undefined>(file, undefined);
}

export function getLatestScan(): ScanRun | undefined {
  ensureDir(SCANS_DIR);
  const files = fs.readdirSync(SCANS_DIR)
    .filter(f => f.endsWith('.json'))
    .sort()
    .reverse();
  if (files.length === 0) return undefined;
  return readJson<ScanRun>(path.join(SCANS_DIR, files[0]), null as unknown as ScanRun);
}

export function getScanCount(): number {
  ensureDir(SCANS_DIR);
  try {
    return fs.readdirSync(SCANS_DIR).filter(f => f.endsWith('.json')).length;
  } catch { return 0; }
}

// ── Audit Log ──

const LOG_DIR = path.join(DATA_DIR, 'logs');

export function logAudit(
  event: string,
  severity: 'info' | 'warn' | 'error',
  message: string,
  metadata?: Record<string, unknown>,
) {
  ensureDir(LOG_DIR);
  const today = new Date().toISOString().slice(0, 10);
  const file = path.join(LOG_DIR, `${today}.log`);
  const entry = JSON.stringify({
    timestamp: new Date().toISOString(),
    event,
    severity,
    message,
    metadata: metadata || {},
  });
  fs.appendFileSync(file, entry + '\n', 'utf-8');
}
