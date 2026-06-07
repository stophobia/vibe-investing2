// types.ts — LAON VaultGuard shared type definitions

export type RepoType = 'local' | 'github' | 'gitlab';
export type Severity = 'critical' | 'high' | 'medium' | 'info';
export type Confidence = 'high' | 'medium' | 'low';
export type Provider = 'AWS' | 'Azure' | 'GCP' | 'KTCloud' | 'NCP' | 'Generic';
export type ScanStatus = 'running' | 'completed' | 'failed';
export type TriggerMode = 'scheduled' | 'manual';
export type LlmMode = 'parallel' | 'sequential' | 'majority';
export type LlmProvider = 'openai' | 'deepseek' | 'minimax' | 'mimo';

// ── Repo ──

export interface Repository {
  id: string;
  name: string;
  type: RepoType;
  pathOrUrl: string;
  branch: string;
  enabled: boolean;
  cronOverride: string | null;
  lastScan: string | null;
  createdAt: string;
}

// ── Scan ──

export interface ScanRun {
  id: string;
  repoId: string;
  status: ScanStatus;
  trigger: TriggerMode;
  startedAt: string;
  completedAt: string | null;
  filesScanned: number;
  findingsCritical: number;
  findingsHigh: number;
  findingsMedium: number;
  findingsInfo: number;
  llmProvidersUsed: string[];
  errorMessage: string | null;
}

// ── Finding ──

export interface Finding {
  id: string;
  scanId: string;
  repoId: string;
  filePath: string;
  line: number | null;
  provider: Provider;
  secretType: string;
  maskedFingerprint: string;
  confidence: Confidence;
  severity: Severity;
  isPlaceholder: boolean;
  evidenceNote: string;
  remediation: string;
  acknowledged: boolean;
  acknowledgedAt: string | null;
  acknowledgedNote: string | null;
  detectedAt: string;
  llmSources: LlmProvider[];
}

// ── Candidate ──

export interface Candidate {
  filePath: string;
  lineNumber: number;
  snippet: string;
  matchedPattern: string;
}

// ── LLM Result ──

export interface LlmScanResult {
  scanSummary: {
    filesScanned: number;
    findingsCount: number;
    critical: number;
    high: number;
    medium: number;
    info: number;
    publishRecommendation: 'BLOCK' | 'REVIEW' | 'PASS';
  };
  findings: LlmFinding[];
  notes: string;
}

export interface LlmFinding {
  id: string;
  file: string;
  line: number | null;
  provider: Provider;
  secretType: string;
  maskedFingerprint: string;
  confidence: Confidence;
  severity: Severity;
  isPlaceholder: boolean;
  evidenceNote: string;
  remediation: string;
}

// ── Alert ──

export type AlertChannel = 'dashboard' | 'telegram' | 'slack' | 'email';

// ── SSE Events ──

export interface SseEvent {
  type: 'scan:started' | 'scan:completed' | 'finding:new' | 'finding:acknowledged';
  data: unknown;
}
