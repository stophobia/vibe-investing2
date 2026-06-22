// hook-install.ts — pre-commit hook installer
// Usage: npx laon-vaultguard hook install [--force]

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const HOOK_NAME = 'pre-commit';

const HOOK_SCRIPT = `#!/bin/bash
# LAON VaultGuard + CIChecker pre-commit hook
# Checks staged files for: secrets, CI(Personal Info), DI(Data), Private Keys
# Bypass: git commit --no-verify

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

echo "🔍 LAON VaultGuard + CIChecker: scanning staged files..."

# ── CIChecker: CI/DI + Private Key patterns ──
TMPDIR=$(mktemp -d)
echo "$STAGED_FILES" > "$TMPDIR/staged.txt"
FOUND_CI=0

while IFS= read -r file; do
  [ -z "$file" ] && continue
  content=$(git show ":$file" 2>/dev/null)
  if [ -z "$content" ]; then continue; fi

  # CI: 주민등록번호 (Korean SSN)
  if echo "$content" | grep -qE '\b[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])-?[1-8][0-9]{6}\b'; then
    echo "  👤 [CI] 주민등록번호 detected in $file"
    FOUND_CI=1
  fi

  # CI: Phone numbers
  if echo "$content" | grep -qE '\b01[016789]-[0-9]{3,4}-[0-9]{4}\b'; then
    echo "  👤 [CI] 휴대전화번호 detected in $file"
    FOUND_CI=1
  fi

  # CI: Credit card
  if echo "$content" | grep -qE '\b(?:[0-9][ -]*?){13,19}\b'; then
    echo "  👤 [CI] 신용카드 번호 의심 패턴 in $file"
    FOUND_CI=1
  fi

  # DI: DB connection string
  if echo "$content" | grep -qiE '\b(?:mongodb|mysql|postgres|redis)://[^@]+@'; then
    echo "  📊 [DI] DB 연결 문자열 (인증정보 포함) in $file"
    FOUND_CI=1
  fi

  # DI: Bank account
  if echo "$content" | grep -qE '\b[0-9]{2,4}-[0-9]{2,4}-[0-9]{4,7}\b'; then
    echo "  📊 [DI] 계좌번호 의심 패턴 in $file"
    FOUND_CI=1
  fi

  # 🔑 Private Key
  if echo "$content" | grep -qE '(-----BEGIN.*PRIVATE KEY-----|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{36,}|AIza[0-9A-Za-z_-]{35}|AKIA[0-9A-Z]{16})'; then
    echo "  🔑 [SECRET] Private Key / API Key in $file"
    FOUND_CI=1
  fi
done < "$TMPDIR/staged.txt"

rm -rf "$TMPDIR"

if [ $FOUND_CI -eq 1 ]; then
  echo ""
  echo "🚫 Commit blocked by LAON VaultGuard + CIChecker."
  echo "   CI(Personal Info), DI(Data), or Private Keys detected."
  echo "   Review warnings above or use --no-verify to bypass."
  exit 1
fi

echo "✅ No secrets or CI/DI detected in staged files."
exit 0
`;

export function installHook(repoPath: string, force = false): { installed: boolean; message: string } {
  const hooksDir = path.join(repoPath, '.git', 'hooks');

  if (!fs.existsSync(hooksDir)) {
    return { installed: false, message: `Not a git repository: ${repoPath}` };
  }

  const hookPath = path.join(hooksDir, HOOK_NAME);

  if (fs.existsSync(hookPath) && !force) {
    return {
      installed: false,
      message: `Hook already exists: ${hookPath}\n  Use --force to overwrite.`,
    };
  }

  fs.writeFileSync(hookPath, HOOK_SCRIPT, { mode: 0o755 });
  return { installed: true, message: `✅ Installed: ${hookPath}` };
}

export function uninstallHook(repoPath: string): { removed: boolean; message: string } {
  const hookPath = path.join(repoPath, '.git', 'hooks', HOOK_NAME);

  if (!fs.existsSync(hookPath)) {
    return { removed: false, message: `No hook found: ${hookPath}` };
  }

  const content = fs.readFileSync(hookPath, 'utf-8');
  if (!content.includes('LAON VaultGuard')) {
    return { removed: false, message: `Hook exists but was not installed by LAON VaultGuard. Manual removal required: ${hookPath}` };
  }

  fs.unlinkSync(hookPath);
  return { removed: true, message: `✅ Removed: ${hookPath}` };
}

// ── CLI entry ──

export function hookCli(args: string[]) {
  const command = args[0];
  const repoPath = args.find(a => !a.startsWith('-') && a !== command) || process.cwd();

  if (command === 'install') {
    const force = args.includes('--force') || args.includes('-f');
    const result = installHook(repoPath, force);
    console.log(result.message);
    process.exit(result.installed ? 0 : 1);
  }

  if (command === 'uninstall') {
    const result = uninstallHook(repoPath);
    console.log(result.message);
    process.exit(result.removed ? 0 : 1);
  }

  console.log('Usage: npx laon-vaultguard hook <install|uninstall> [path] [--force]');
  process.exit(1);
}
