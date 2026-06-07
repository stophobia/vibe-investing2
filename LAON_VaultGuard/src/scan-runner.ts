// scan-runner.ts — single repository scan pipeline

import { randomUUID } from 'node:crypto';
import type { Repository, ScanRun, Finding, LlmProvider, Candidate } from './types.js';
import { saveScanRun, saveFindings, logAudit } from './db.js';
import { getLocalChanges, getWholeRepoChanges, getGithubChanges } from './git-monitor.js';
import { extractCandidates } from './candidate-filter.js';
import { analyzeCandidates } from './llm-harness.js';
import { emitSse } from './sse.js';
import { sendAlerts } from './alert-engine.js';

export async function scanRepository(repo: Repository) {
  const scanId = randomUUID();
  const startedAt = new Date().toISOString();

  const scanRun: ScanRun = {
    id: scanId,
    repoId: repo.id,
    status: 'running',
    trigger: 'scheduled',
    startedAt,
    completedAt: null,
    filesScanned: 0,
    findingsCritical: 0,
    findingsHigh: 0,
    findingsMedium: 0,
    findingsInfo: 0,
    llmProvidersUsed: [],
    errorMessage: null,
  };

  saveScanRun(scanRun);
  logAudit('scan_repo_started', 'info', `Scan started: ${repo.name}`, { scanId, repoId: repo.id });

  try {
    // Phase 1: Get changes
    const isFirstScan = !repo.lastScan;
    let candidates: Candidate[] = [];

    if (repo.type === 'local') {
      if (isFirstScan) {
        // For first scan, we still use candidate filter (git grep) only — no full file send
        candidates = await extractCandidates(repo.pathOrUrl);
        scanRun.filesScanned = 0; // counted via grep
      } else {
        // delta scan via diff
        candidates = await extractCandidates(repo.pathOrUrl);
        scanRun.filesScanned = candidates.length > 0 ? 0 : 0; // approximate
      }
    } else if (repo.type === 'github') {
      // GitHub remote: extract candidates from compareCommits diff
      candidates = await extractCandidates(repo.pathOrUrl); // uses local git if cloned
    } else {
      // GitLab (future)
      candidates = await extractCandidates(repo.pathOrUrl);
    }

    // Phase 2: LLM analysis
    let findings: Finding[] = [];
    let providersUsed: LlmProvider[] = [];
    let totalTokens = 0;

    if (candidates.length > 0) {
      const result = await analyzeCandidates(candidates);
      findings = result.findings.map((f, idx) => ({
        id: `F-${scanId.slice(0, 8)}-${String(idx + 1).padStart(3, '0')}`,
        scanId,
        repoId: repo.id,
        filePath: f.file,
        line: f.line,
        provider: f.provider,
        secretType: f.secretType,
        maskedFingerprint: f.maskedFingerprint,
        confidence: f.confidence,
        severity: f.severity,
        isPlaceholder: f.isPlaceholder,
        evidenceNote: f.evidenceNote,
        remediation: f.remediation,
        acknowledged: false,
        acknowledgedAt: null,
        acknowledgedNote: null,
        detectedAt: new Date().toISOString(),
        llmSources: result.providersUsed,
      }));
      providersUsed = result.providersUsed;
      totalTokens = result.totalTokens;
    }

    // Phase 3: Save
    if (findings.length > 0) {
      saveFindings(findings);
      logAudit('finding_detected', findings.some(f => f.severity === 'critical') ? 'warn' : 'info',
        `${findings.length} findings (${findings.filter(f => f.severity === 'critical').length} critical)`,
        { scanId, repoId: repo.id },
      );

      for (const f of findings) {
        if (f.severity === 'critical' || f.severity === 'high') {
          emitSse('finding:new', f);
        }
      }
    }

    // Phase 4: Alerts
    await sendAlerts(repo, findings);

    // Update scan run
    scanRun.status = 'completed';
    scanRun.completedAt = new Date().toISOString();
    scanRun.findingsCritical = findings.filter(f => f.severity === 'critical').length;
    scanRun.findingsHigh = findings.filter(f => f.severity === 'high').length;
    scanRun.findingsMedium = findings.filter(f => f.severity === 'medium').length;
    scanRun.findingsInfo = findings.filter(f => f.severity === 'info').length;
    scanRun.llmProvidersUsed = providersUsed;
    saveScanRun(scanRun);

  } catch (err) {
    scanRun.status = 'failed';
    scanRun.errorMessage = err instanceof Error ? err.message : String(err);
    scanRun.completedAt = new Date().toISOString();
    saveScanRun(scanRun);
    logAudit('scan_error', 'error', `Scan failed: ${repo.name}`, {
      scanId, repoId: repo.id, error: scanRun.errorMessage,
    });
  }
}
