// git-monitor.ts — git repository operations

import { simpleGit, type SimpleGit } from 'simple-git';
import fs from 'node:fs';
import { execSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Octokit } from '@octokit/rest';
import type { Repository, RepoType } from './types.js';
import { config } from './config.js';

let gitAvailable: boolean | null = null;

export function checkGitInstalled(): boolean {
  if (gitAvailable !== null) return gitAvailable;
  try {
    execSync('git --version', { stdio: 'pipe' });
    gitAvailable = true;
    return true;
  } catch {
    gitAvailable = false;
    return false;
  }
}

export interface GitChange {
  filePath: string;
  changeType: 'added' | 'modified' | 'deleted';
  additions: string[];
  lineNumbers: number[];
}

function getLocalGit(repoPath: string): SimpleGit {
  if (!fs.existsSync(repoPath)) {
    throw new Error(`Repository path does not exist: ${repoPath}`);
  }
  return simpleGit(repoPath);
}

export async function getLocalChanges(
  repo: Repository,
  since: string | null,
): Promise<GitChange[]> {
  const git = getLocalGit(repo.pathOrUrl);
  await git.fetch();

  const logOpts: Parameters<typeof git.log>[0] = { maxCount: 20 };
  if (since) {
    logOpts.from = since;
  }

  const log = await git.log(logOpts);
  if (log.all.length === 0) return [];

  // get diff from oldest new commit to newest
  const oldestHash = (log.all[log.all.length - 1] as { hash: string }).hash;
  const newestHash = (log.all[0] as { hash: string }).hash;

  // compare with previous commit or use initial commit diff
  let diff: string;
  try {
    diff = await git.diff([`${oldestHash}^..${newestHash}`]);
  } catch {
    diff = await git.diff([oldestHash]);
  }

  return parseDiff(diff);
}

export async function getWholeRepoChanges(repo: Repository): Promise<GitChange[]> {
  const git = getLocalGit(repo.pathOrUrl);

  // for initial scan, get all tracked files and their content
  const files = await git.raw(['ls-files']);
  const fileList = files.trim().split('\n').filter(Boolean);

  const changes: GitChange[] = [];
  for (const filePath of fileList) {
    try {
      const content = await git.show([`HEAD:${filePath}`]);
      const lines = content.split('\n');
      changes.push({
        filePath,
        changeType: 'added',
        additions: lines,
        lineNumbers: lines.map((_, i) => i + 1),
      });
    } catch {
      // binary or missing file, skip
    }
  }
  return changes;
}

export async function getGithubChanges(
  repo: Repository,
  since: string | null,
): Promise<GitChange[]> {
  if (!config.github.token) {
    throw new Error('GITHUB_TOKEN not configured');
  }

  const octokit = new Octokit({ auth: config.github.token });
  const [owner, name] = parseGithubUrl(repo.pathOrUrl);

  // get recent commits
  const commitsOpts: Parameters<typeof octokit.rest.repos.listCommits>[0] = {
    owner,
    repo: name,
    sha: repo.branch,
    per_page: 20,
  };
  if (since) {
    commitsOpts.since = since;
  }

  const { data: commits } = await octokit.rest.repos.listCommits(commitsOpts);
  if (commits.length === 0) return [];

  // get diff between the oldest and newest commits
  const { data: comparison } = await octokit.rest.repos.compareCommitsWithBasehead({
    owner,
    repo: name,
    basehead: `${commits[commits.length - 1].sha}...${commits[0].sha}`,
  });

  if (!comparison.files) return [];

  const changes: GitChange[] = [];
  for (const file of comparison.files) {
    if (!file.patch) continue;
    const additions = file.patch
      .split('\n')
      .filter(line => line.startsWith('+') && !line.startsWith('+++'))
      .map(line => line.slice(1));
    changes.push({
      filePath: file.filename,
      changeType: file.status as GitChange['changeType'] || 'modified',
      additions,
      lineNumbers: [], // GitHub API doesn't provide precise line numbers per addition
    });
  }

  return changes;
}

export function parseGithubUrl(url: string): [string, string] {
  // https://github.com/owner/repo(.git)?
  const match = url.match(/github\.com\/([^/]+)\/([^/\s.]+)/);
  if (!match) throw new Error(`Invalid GitHub URL: ${url}`);
  return [match[1], match[2].replace(/\.git$/, '')];
}

function parseDiff(diffText: string): GitChange[] {
  const changes: GitChange[] = [];
  const hunkPattern = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/;

  let currentFile: string | null = null;
  let currentAdditions: string[] = [];
  let currentLineNums: number[] = [];
  let currentLine = 0;

  const flush = () => {
    if (currentFile && currentAdditions.length > 0) {
      changes.push({
        filePath: currentFile,
        changeType: 'modified',
        additions: currentAdditions,
        lineNumbers: currentLineNums,
      });
    }
    currentFile = null;
    currentAdditions = [];
    currentLineNums = [];
    currentLine = 0;
  };

  for (const line of diffText.split('\n')) {
    if (line.startsWith('diff --git a/')) {
      flush();
      const m = line.match(/^diff --git a\/(.+) b\/(.+)$/);
      if (m) currentFile = m[1];
      continue;
    }

    if (!currentFile) continue;

    const hunkMatch = hunkPattern.exec(line);
    if (hunkMatch) {
      currentLine = parseInt(hunkMatch[1], 10);
      continue;
    }

    if (line.startsWith('+') && !line.startsWith('+++')) {
      currentAdditions.push(line.slice(1));
      currentLineNums.push(currentLine);
    }
    if (!line.startsWith('-')) {
      currentLine++;
    }
  }

  flush();
  return changes;
}

// ── GitHub clone helper ──

export async function cloneGithubRepo(repo: Repository): Promise<string> {
  const [owner, name] = parseGithubUrl(repo.pathOrUrl);
  const token = config.github.token || config.github.oauthToken;
  if (!token) throw new Error('GitHub token not configured (set GITHUB_TOKEN or connect via OAuth)');

  const tmpDir = mkdtempSync(join(tmpdir(), 'laon-'));
  const netrcPath = join(tmpDir, '.netrc');
  writeFileSync(netrcPath, `machine github.com\nlogin x-access-token\npassword ${token}\n`, { mode: 0o600 });
  const cloneUrl = `https://github.com/${owner}/${name}.git`;

  try {
    const git = simpleGit();
    await git.env('GIT_CONFIG_GLOBAL', netrcPath);
    await git.clone(cloneUrl, tmpDir, ['--depth', '50', '--single-branch', '--branch', repo.branch]);
    return tmpDir;
  } catch (err) {
    // cleanup on failure
    try { rmSync(tmpDir, { recursive: true, force: true }); } catch {}
    throw err;
  }
}

export function cleanupTempRepo(tmpDir: string) {
  try { rmSync(tmpDir, { recursive: true, force: true }); } catch {}
}
