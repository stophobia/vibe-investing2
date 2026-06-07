// sarif-export.ts — SARIF v2.1.0 export for GitHub Code Scanning / GitLab SAST
//
// Usage:
//   npx tsx src/sarif-export.ts [--repo <id>] [--output results.sarif]
//   npm run export-sarif -- --repo <id> --output results.sarif
//
// SARIF spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html

import fs from 'node:fs';
import path from 'node:path';
import { listFindings, listRepos } from './db.js';

interface SarifResult {
  ruleId: string;
  level: 'error' | 'warning' | 'note';
  message: { text: string };
  locations: {
    physicalLocation: {
      artifactLocation: { uri: string; uriBaseId?: string };
      region?: { startLine?: number; startColumn?: number };
    };
  }[];
  properties?: Record<string, string | number | boolean>;
}

interface SarifRun {
  tool: {
    driver: {
      name: string;
      version: string;
      informationUri: string;
      rules: { id: string; name: string; shortDescription: { text: string }; helpUri?: string }[];
    };
  };
  results: SarifResult[];
  invocations?: { executionSuccessful: boolean }[];
}

interface SarifLog {
  $schema: string;
  version: '2.1.0';
  runs: SarifRun[];
}

const SCHEMA_URI = 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json';
const TOOL_NAME = 'LAON VaultGuard';
const TOOL_VERSION = '0.5.0';
const TOOL_URI = 'https://github.com/gameworkerkim/vibe-investing/tree/main/LAON_VaultGuard';

function severityToSarifLevel(severity: string): 'error' | 'warning' | 'note' {
  switch (severity) {
    case 'critical':
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    default:
      return 'note';
  }
}

function confidenceToRank(confidence: string): number {
  switch (confidence) {
    case 'high': return 90;
    case 'medium': return 50;
    case 'low': return 10;
    default: return 50;
  }
}

export function buildSarifLog(
  findings: { id: string; filePath: string; line: number | null; provider: string; secretType: string; maskedFingerprint: string; confidence: string; severity: string; evidenceNote: string; remediation: string; detectedAt: string; repoId: string }[],
  repoLabel?: string,
): SarifLog {
  const uniqueRules = [...new Set(findings.map(f => f.secretType))];

  const run: SarifRun = {
    tool: {
      driver: {
        name: TOOL_NAME,
        version: TOOL_VERSION,
        informationUri: TOOL_URI,
        rules: uniqueRules.map(rule => ({
          id: `LAON/${rule.replace(/[^a-zA-Z0-9]/g, '-')}`,
          name: rule,
          shortDescription: { text: `Secret detected: ${rule}` },
        })),
      },
    },
    results: findings.map(f => ({
      ruleId: `LAON/${f.secretType.replace(/[^a-zA-Z0-9]/g, '-')}`,
      level: severityToSarifLevel(f.severity),
      message: {
        text: `${repoLabel ? `[${repoLabel}] ` : ''}${f.provider} ${f.secretType}: ${f.maskedFingerprint}${f.evidenceNote ? ` — ${f.evidenceNote.slice(0, 200)}` : ''}`,
      },
      locations: [{
        physicalLocation: {
          artifactLocation: { uri: f.filePath },
          ...(f.line ? { region: { startLine: f.line } } : {}),
        },
      }],
      properties: {
        provider: f.provider,
        secretType: f.secretType,
        maskedFingerprint: f.maskedFingerprint,
        confidence: f.confidence,
        severity: f.severity,
        detectedAt: f.detectedAt,
        rank: confidenceToRank(f.confidence),
      },
    })),
    invocations: [{ executionSuccessful: true }],
  };

  return {
    $schema: SCHEMA_URI,
    version: '2.1.0',
    runs: [run],
  };
}

export function writeSarifFile(outputPath: string, sarif: SarifLog) {
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(sarif, null, 2), 'utf-8');
}

// ── CLI ──

async function main() {
  const args = process.argv.slice(2);
  const repoId = args.includes('--repo') ? args[args.indexOf('--repo') + 1] : undefined;
  const outputPath = args.includes('--output') ? args[args.indexOf('--output') + 1] : './results.sarif';

  const { findings } = listFindings({
    acknowledged: false,
    ...(repoId ? { repoId } : {}),
    limit: 10000,
  });

  if (findings.length === 0) {
    console.log('  ✅ No open findings to export.');
    return;
  }

  let repoLabel: string | undefined;
  if (repoId) {
    const allRepos = listRepos();
    repoLabel = allRepos.find(r => r.id === repoId)?.name;
  }

  const sarif = buildSarifLog(findings, repoLabel);
  writeSarifFile(outputPath, sarif);

  console.log(`  ✅ Exported ${findings.length} finding(s) → ${outputPath}`);
  console.log(`  Import into GitHub: gh code scanning upload-sarif --file ${outputPath}`);
}

main().catch(console.error);
