// scheduler.ts — cron-based scan + report scheduler

import cron from 'node-cron';
import { config } from './config.js';
import { listRepos, updateRepoLastScan, logAudit, listFindings, getAlertConfig } from './db.js';
import { scanRepository } from './scan-runner.js';
import { emitSse } from './sse.js';
import { sendSummaryReport } from './alert-engine.js';

let scanJob: cron.ScheduledTask | null = null;
let reportJob: cron.ScheduledTask | null = null;

export function startScheduler() {
  // ── Scan job ──
  if (scanJob) scanJob.stop();
  scanJob = cron.schedule(config.scan.cron, async () => {
    logAudit('scan_triggered', 'info', `Scheduled scan triggered (cron: ${config.scan.cron})`);
    await scanAllRepos('scheduled');
  });
  console.log(`[scheduler] Scan cron: ${config.scan.cron}`);

  // ── Report job ──
  const alertCfg = getAlertConfig();
  if (alertCfg.email && alertCfg.frequency !== 'off') {
    scheduleReport(alertCfg.frequency);
  }

  // initial scan
  setTimeout(() => scanAllRepos('scheduled'), 3000);
}

function scheduleReport(frequency: 'daily' | 'weekly') {
  if (reportJob) reportJob.stop();
  const expr = frequency === 'daily' ? '0 9 * * *' : '0 9 * * 1'; // 9am daily or Monday
  reportJob = cron.schedule(expr, async () => {
    await runSummaryReport(frequency);
  });
  console.log(`[scheduler] Report cron: ${expr} (${frequency})`);
}

export function rescheduleReport(frequency: 'daily' | 'weekly' | 'off') {
  if (frequency === 'off') {
    if (reportJob) { reportJob.stop(); reportJob = null; }
    return;
  }
  scheduleReport(frequency);
}

export function stopScheduler() {
  if (scanJob) { scanJob.stop(); scanJob = null; }
  if (reportJob) { reportJob.stop(); reportJob = null; }
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
      logAudit('scan_error', 'error', `Scan failed: ${repo.name}`,
        { repoId: repo.id, error: err instanceof Error ? err.message : String(err) });
    }
  }

  emitSse('scan:completed', { timestamp: new Date().toISOString() });
  logAudit('scan_completed', 'info', `Scan cycle completed (${repos.length} repos)`);
}

async function runSummaryReport(frequency: 'daily' | 'weekly') {
  const alertCfg = getAlertConfig();
  if (!alertCfg.email) return;

  const repos = listRepos();
  const reposMap = new Map(repos.map(r => [r.id, r.name]));
  const allFindings = listFindings({ acknowledged: false });

  if (allFindings.total === 0) {
    logAudit('report_skipped', 'info', `No open findings for ${frequency} report`);
    return;
  }

  const withRepoName = allFindings.findings.map(f => ({
    ...f,
    repoName: reposMap.get(f.repoId) || 'unknown',
  }));

  await sendSummaryReport(withRepoName, frequency);
}
