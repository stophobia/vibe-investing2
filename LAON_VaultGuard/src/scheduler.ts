// scheduler.ts — cron-based scan scheduler

import cron from 'node-cron';
import { config } from './config.js';
import { listRepos, updateRepoLastScan, logAudit } from './db.js';
import { scanRepository } from './scan-runner.js';
import { emitSse } from './sse.js';

let cronJob: cron.ScheduledTask | null = null;

export function startScheduler() {
  const expression = config.scan.cron;

  if (cronJob) {
    cronJob.stop();
  }

  cronJob = cron.schedule(expression, async () => {
    logAudit('scan_triggered', 'info', `Scheduled scan triggered (cron: ${expression})`);
    await scanAllRepos('scheduled');
  });

  logAudit('scheduler_started', 'info', `Scheduler started (cron: ${expression})`);
  console.log(`[scheduler] Cron started: ${expression}`);

  // run initial scan immediately
  setTimeout(() => scanAllRepos('scheduled'), 3000);
}

export function stopScheduler() {
  if (cronJob) {
    cronJob.stop();
    cronJob = null;
  }
}

export async function scanAllRepos(trigger: 'scheduled' | 'manual') {
  const repos = listRepos().filter(r => r.enabled);
  if (repos.length === 0) {
    logAudit('scan_skipped', 'warn', 'No enabled repos to scan');
    return;
  }

  logAudit('scan_started', 'info', `Scanning ${repos.length} repos (trigger: ${trigger})`);
  emitSse('scan:started', { repoCount: repos.length, trigger });

  for (const repo of repos) {
    try {
      await scanRepository(repo);
      updateRepoLastScan(repo.id);
    } catch (err) {
      logAudit('scan_error', 'error',
        `Scan failed for repo: ${repo.name}`,
        { repoId: repo.id, error: err instanceof Error ? err.message : String(err) },
      );
    }
  }

  emitSse('scan:completed', { timestamp: new Date().toISOString() });
  logAudit('scan_completed', 'info', `Scan cycle completed (${repos.length} repos)`);
}
