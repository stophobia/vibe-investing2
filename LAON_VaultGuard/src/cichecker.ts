// cichecker.ts — CI/DI(Personal Info) + Private Key pre-commit / git audit checker
//
// CIChecker: detects PII(개인식별정보), CI(기밀정보), DI(데이터식별정보)
// in staged files (pre-commit) or full git history (audit)
//
// Usage:
//   npx laon-vaultguard hook install          # pre-commit (LAON + CIChecker)
//   npx laon-vaultguard audit-history [path]  # scan entire git history for CI/DI

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

// ── CI/DI Detection Patterns ──

interface CIPattern {
  name: string;
  category: 'CI' | 'DI' | 'PRIVATE_KEY';
  regex: RegExp;
  severity: 'critical' | 'high' | 'medium';
  message: string;
}

const CI_PATTERNS: CIPattern[] = [
  // ── Korean PII (개인식별정보) ──
  {
    name: '주민등록번호 (Korean SSN)',
    category: 'CI',
    regex: /\b\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])-?[1-8]\d{6}\b/g,
    severity: 'critical',
    message: '주민등록번호가 코드에 포함되어 있습니다. 즉시 삭제하고 .gitignore에 추가하세요.',
  },
  {
    name: '휴대전화번호 (Korean Phone)',
    category: 'CI',
    regex: /\b01[016789]-\d{3,4}-\d{4}\b/g,
    severity: 'high',
    message: '개인 휴대전화번호가 코드에 포함되어 있습니다.',
  },
  {
    name: '이메일 주소 (Email)',
    category: 'CI',
    regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
    severity: 'medium',
    message: '이메일 주소가 하드코딩되어 있습니다. 환경변수로 분리하세요.',
  },
  {
    name: '신용카드 번호 (Credit Card)',
    category: 'CI',
    regex: /\b(?:\d[ -]*?){13,19}\b/g,
    severity: 'critical',
    message: '신용카드 번호로 의심되는 숫자 패턴이 발견되었습니다.',
  },
  {
    name: '여권번호 (Passport)',
    category: 'CI',
    regex: /\b[MRS]\d{8}\b/g,
    severity: 'high',
    message: '여권번호로 의심되는 패턴이 발견되었습니다.',
  },
  {
    name: '운전면허번호 (Driver License)',
    category: 'CI',
    regex: /\b(?:서울|부산|대구|인천|광주|대전|울산|경기|강원|충북|충남|전북|전남|경북|경남|제주)\d{2}-\d{6}-\d{2}\b/g,
    severity: 'high',
    message: '운전면허번호가 코드에 포함되어 있습니다.',
  },
  {
    name: '외국인등록번호 (Alien Registration)',
    category: 'CI',
    regex: /\b\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])-[5-8]\d{6}\b/g,
    severity: 'critical',
    message: '외국인등록번호가 코드에 포함되어 있습니다.',
  },
  {
    name: '사업자등록번호 (Business Reg No)',
    category: 'DI',
    regex: /\b\d{3}-\d{2}-\d{5}\b/g,
    severity: 'medium',
    message: '사업자등록번호가 코드에 포함되어 있습니다.',
  },
  {
    name: '계좌번호 (Bank Account)',
    category: 'DI',
    regex: /\b\d{2,4}-\d{2,4}-\d{4,7}\b/g,
    severity: 'high',
    message: '은행 계좌번호로 의심되는 패턴이 발견되었습니다.',
  },
  {
    name: 'IP 주소 (Internal IP)',
    category: 'DI',
    regex: /\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b/g,
    severity: 'medium',
    message: '내부 IP 주소가 코드에 포함되어 있습니다.',
  },
  {
    name: 'DB 연결 문자열 (Connection String)',
    category: 'DI',
    regex: /\b(?:mongodb|mysql|postgres|postgresql|redis|sqlite)(?:\+srv)?:\/\/[^@\s]+@[^\s]+\b/gi,
    severity: 'critical',
    message: 'DB 연결 문자열에 인증정보가 포함되어 있습니다. 환경변수로 분리하세요.',
  },

  // ── Private Keys (중복 — LAON과 동일 패턴, CIChecker가 추가 검증) ──
  {
    name: 'Private Key (PEM)',
    category: 'PRIVATE_KEY',
    regex: /-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/g,
    severity: 'critical',
    message: 'Private Key가 코드에 포함되어 있습니다. 즉시 폐기하고 재발급하세요.',
  },
  {
    name: 'API Key (sk- / ghp_ / AIza)',
    category: 'PRIVATE_KEY',
    regex: /\b(?:sk-(?:ant-)?[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{36,}|AIza[0-9A-Za-z\-_]{35})\b/g,
    severity: 'critical',
    message: 'API 키가 코드에 포함되어 있습니다. 즉시 폐기하고 환경변수로 이동하세요.',
  },
];

// ── Check result ──

interface CIFinding {
  file: string;
  line: number;
  match: string;
  pattern: string;
  category: string;
  severity: string;
  message: string;
}

function maskValue(text: string): string {
  if (text.length <= 6) return '***';
  return text.slice(0, 3) + '***' + text.slice(-2);
}

// ── Scan staged files (pre-commit) ──

export function scanStagedFiles(repoPath: string): CIFinding[] {
  const findings: CIFinding[] = [];

  try {
    const staged = execSync('git diff --cached --name-only --diff-filter=ACM', {
      cwd: repoPath, encoding: 'utf-8', stdio: 'pipe',
    }).trim();

    if (!staged) return findings;

    for (const file of staged.split('\n')) {
      const f = file.trim();
      if (!f) continue;

      try {
        const content = execSync(`git show ":${f}"`, {
          cwd: repoPath, encoding: 'utf-8', stdio: 'pipe',
        });

        const lines = content.split('\n');
        for (const pattern of CI_PATTERNS) {
          pattern.regex.lastIndex = 0;
          for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
            const line = lines[lineIdx];
            pattern.regex.lastIndex = 0;
            let match: RegExpExecArray | null;
            while ((match = pattern.regex.exec(line)) !== null) {
              // Skip .env.example, README, test files
              if (/\.env\.example$|README|\.test\.|\.spec\.|mock|fixture/i.test(f)) continue;
              // Skip common false positives
              if (match[0] === '192.168.0.1' && pattern.name.includes('IP')) continue;

              findings.push({
                file: f,
                line: lineIdx + 1,
                match: match[0],
                pattern: pattern.name,
                category: pattern.category,
                severity: pattern.severity,
                message: pattern.message,
              });
            }
          }
        }
      } catch { /* binary file or deleted */ }
    }
  } catch { /* not a git repo */ }

  return findings;
}

// ── Audit git history ──

export function auditGitHistory(repoPath: string): CIFinding[] {
  const findings: CIFinding[] = [];

  try {
    const log = execSync(
      'git log --all --pretty=format:"%H" --diff-filter=ACM -p',
      { cwd: repoPath, encoding: 'utf-8', stdio: 'pipe', maxBuffer: 50 * 1024 * 1024 },
    );

    const commits = log.split('commit ');
    for (const block of commits) {
      if (!block.trim()) continue;
      const hash = block.split('\n')[0]?.slice(0, 8) || 'unknown';

      // extract --- a/file and +++ b/file lines
      const fileMatch = block.match(/^\+\+\+ b\/(.+)$/m);
      const filename = fileMatch?.[1] || 'unknown';

      // check additions (+ lines)
      const lines = block.split('\n');
      let lineNum = 0;
      for (const line of lines) {
        if (line.startsWith('@@')) {
          const m = line.match(/\+(\d+)/);
          if (m) lineNum = parseInt(m[1], 10);
          continue;
        }
        if (line.startsWith('+') && !line.startsWith('+++')) {
          lineNum++;
          for (const pattern of CI_PATTERNS) {
            const content = line.slice(1);
            pattern.regex.lastIndex = 0;
            let match: RegExpExecArray | null;
            while ((match = pattern.regex.exec(content)) !== null) {
              findings.push({
                file: filename,
                line: lineNum,
                match: match[0],
                pattern: pattern.name,
                category: pattern.category,
                severity: pattern.severity,
                message: pattern.message,
              });
            }
          }
        } else if (!line.startsWith('-')) {
          lineNum++;
        }
      }
    }
  } catch { /* not a git repo or too large */ }

  return findings;
}

// ── Format output ──

export function formatFindings(findings: CIFinding[]): string {
  if (findings.length === 0) return '✅ No CI/DI or private keys detected.';

  // group by file
  const byFile = new Map<string, CIFinding[]>();
  for (const f of findings) {
    const arr = byFile.get(f.file) || [];
    arr.push(f);
    byFile.set(f.file, arr);
  }

  const ci = findings.filter(f => f.category === 'CI').length;
  const di = findings.filter(f => f.category === 'DI').length;
  const pk = findings.filter(f => f.category === 'PRIVATE_KEY').length;

  let output = `\n🚨 CIChecker: ${findings.length} issue(s) found\n`;
  output += `   CI(Personal): ${ci}  DI(Data): ${di}  Private Key: ${pk}\n\n`;

  for (const [file, items] of byFile) {
    output += `📄 ${file}\n`;
    for (const f of items) {
      const badge = f.category === 'PRIVATE_KEY' ? '🔑' : f.category === 'CI' ? '👤' : '📊';
      output += `   ${badge} [${f.severity.toUpperCase()}] L${f.line}: ${f.pattern} → ${maskValue(f.match)}\n`;
      output += `      ${f.message}\n`;
    }
    output += '\n';
  }

  if (pk > 0 || ci > 0) {
    output += '🚫 Commit blocked. Fix the issues above or use --no-verify to bypass.\n';
  }

  return output;
}

// ── CLI for audit-history ──

export function auditHistoryCli(args: string[]) {
  const repoPath = args.find(a => !a.startsWith('-')) || process.cwd();
  console.log('🔍 CIChecker: Scanning git history for CI/DI + private keys...\n');
  console.log(`   Repository: ${repoPath}`);
  console.log('   This may take a while for large repos...\n');

  const findings = auditGitHistory(repoPath);
  console.log(formatFindings(findings));

  if (findings.length > 0) {
    process.exit(1);
  }
}

// ── LLM Prompt for git history audit ──

export const AUDIT_HISTORY_PROMPT = `You are CIChecker, a git history auditor. Scan the following git diff for:

1. **CI (Personal Identifiable Information)**:
   - Korean resident registration numbers (주민등록번호)
   - Phone numbers, email addresses
   - Passport numbers, driver license numbers
   - Credit card numbers

2. **DI (Data Identifiers)**:
   - Bank account numbers
   - Business registration numbers
   - Internal IP addresses (10.x, 172.16-31.x, 192.168.x)
   - Database connection strings with credentials

3. **Private Keys**:
   - PEM private key blocks (BEGIN/END PRIVATE KEY)
   - API keys (sk-, ghp_, AIza patterns)
   - Cloud access keys (AKIA, ASIA)

For each finding, report:
- File path and line number
- What was found (mask the value: show first 3 + last 2 chars only)
- Severity (critical/high/medium)
- Recommended remediation

Output as JSON array of findings. If nothing found, return empty array.`;
