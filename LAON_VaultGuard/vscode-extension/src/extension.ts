// extension.ts — LAON VaultGuard VS Code Extension
//
// Features:
//   - Real-time secret pattern highlighting (regex decorations)
//   - Scan on save / manual scan commands
//   - Problems panel diagnostics (masked fingerprints only)
//   - Status bar indicator
//   - Deep LLM scan via CLI integration

import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

// ── Diagnostic collection ──

const diagnosticCollection = vscode.languages.createDiagnosticCollection('laon-vaultguard');

// ── Suspect patterns (from candidate-filter.ts, subset) ──

const SUSPECT_PATTERNS: { regex: RegExp; name: string; severity: vscode.DiagnosticSeverity }[] = [
  { regex: /\bAKIA[0-9A-Z]{16}\b/, name: 'AWS Access Key ID', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bASIA[0-9A-Z]{16}\b/, name: 'AWS Temporary Key', severity: vscode.DiagnosticSeverity.Warning },
  { regex: /\bAIza[0-9A-Za-z\-_]{35}\b/, name: 'GCP API Key', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bghp_[A-Za-z0-9]{36,}\b/, name: 'GitHub Personal Token', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bgho_[A-Za-z0-9]{36,}\b/, name: 'GitHub OAuth Token', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bgithub_pat_[A-Za-z0-9_]{22,}\b/, name: 'GitHub Fine-grained Token', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bsk-(?:ant-)?[A-Za-z0-9]{32,}\b/, name: 'OpenAI/LLM API Key', severity: vscode.DiagnosticSeverity.Error },
  { regex: /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/, name: 'Slack Token', severity: vscode.DiagnosticSeverity.Warning },
  { regex: /\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b/, name: 'JWT Token', severity: vscode.DiagnosticSeverity.Warning },
  { regex: /-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/, name: 'Private Key', severity: vscode.DiagnosticSeverity.Error },
  { regex: /(?:password|passwd|pwd|secret)\s*[:=]\s*['"][^'"]{8,}['"]/i, name: 'Hardcoded Password', severity: vscode.DiagnosticSeverity.Error },
  { regex: /(?:mongodb|mysql|postgres|redis):\/\/[^:]+:[^@]+@/, name: 'DB Connection String', severity: vscode.DiagnosticSeverity.Error },
  { regex: /NCP_(?:ACCESS|SECRET)_KEY\s*=\s*[A-Za-z0-9]{20,}/i, name: 'Naver Cloud Key', severity: vscode.DiagnosticSeverity.Warning },
];

// ── Status bar ──

let statusBarItem: vscode.StatusBarItem;

// ── Decoration type (dashed red underline) ──

const secretDecoration = vscode.window.createTextEditorDecorationType({
  borderWidth: '0 0 1px 0',
  borderStyle: 'dashed',
  borderColor: new vscode.ThemeColor('editorWarning.foreground'),
  overviewRulerColor: new vscode.ThemeColor('editorWarning.foreground'),
  overviewRulerLane: vscode.OverviewRulerLane.Right,
});

// ── Pattern scan (fast regex, no LLM) ──

interface QuickFinding {
  line: number;
  startCol: number;
  endCol: number;
  text: string;
  rule: string;
  severity: vscode.DiagnosticSeverity;
}

function maskSecret(text: string): string {
  if (text.length <= 8) return '[REDACTED]';
  return text.slice(0, 4) + '…' + text.slice(-2);
}

function scanText(text: string): QuickFinding[] {
  const results: QuickFinding[] = [];
  const lines = text.split('\n');

  for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
    const line = lines[lineIdx];
    for (const pattern of SUSPECT_PATTERNS) {
      pattern.regex.lastIndex = 0;
      let match: RegExpExecArray | null;
      while ((match = pattern.regex.exec(line)) !== null) {
        results.push({
          line: lineIdx,
          startCol: match.index,
          endCol: match.index + match[0].length,
          text: match[0],
          rule: pattern.name,
          severity: pattern.severity,
        });
      }
    }
  }

  return results;
}

function updateDiagnostics(document: vscode.TextDocument, findings: QuickFinding[]) {
  const config = vscode.workspace.getConfiguration('laon-vaultguard');
  const minSeverity = config.get<string>('severity', 'medium');
  const severityMap: Record<string, number> = { critical: 0, high: 1, medium: 2, all: 3 };
  const minLevel = severityMap[minSeverity] ?? 2;

  const diagnostics: vscode.Diagnostic[] = [];
  for (const f of findings) {
    const sevLevel = { 0: 0, 1: 1, 2: 2, 3: 1 }[f.severity] ?? 2;
    if (sevLevel > minLevel && minSeverity !== 'all') continue;

    const range = new vscode.Range(f.line, f.startCol, f.line, f.endCol);
    const diagnostic = new vscode.Diagnostic(
      range,
      `${f.rule}: ${maskSecret(f.text)}`,
      f.severity,
    );
    diagnostic.source = 'LAON VaultGuard';
    diagnostic.code = f.rule.replace(/[^a-zA-Z0-9]/g, '-');
    diagnostics.push(diagnostic);
  }

  diagnosticCollection.set(document.uri, diagnostics);
}

function updateDecorations(editor: vscode.TextEditor, findings: QuickFinding[]) {
  const decorations: vscode.DecorationOptions[] = findings.map(f => ({
    range: new vscode.Range(f.line, f.startCol, f.line, f.endCol),
    hoverMessage: `${f.rule}: ${maskSecret(f.text)}`,
  }));
  editor.setDecorations(secretDecoration, decorations);
}

// ── File scanning ──

let decorationTimeout: ReturnType<typeof setTimeout> | undefined;

function scanDocument(document: vscode.TextDocument) {
  const config = vscode.workspace.getConfiguration('laon-vaultguard');
  if (!config.get<boolean>('enabled', true)) return;

  const findings = scanText(document.getText());
  updateDiagnostics(document, findings);

  const editor = vscode.window.activeTextEditor;
  if (editor && editor.document === document) {
    updateDecorations(editor, findings);
  }

  updateStatus(findings.length);
}

function scheduleDecorationUpdate(editor: vscode.TextEditor) {
  if (decorationTimeout) clearTimeout(decorationTimeout);
  decorationTimeout = setTimeout(() => {
    if (vscode.window.activeTextEditor === editor) {
      const findings = scanText(editor.document.getText());
      updateDecorations(editor, findings);
    }
  }, 300);
}

// ── CLI integration (LLM deep scan) ──

function getWorkspaceRoot(): string | undefined {
  const folders = vscode.workspace.workspaceFolders;
  return folders?.[0]?.uri.fsPath;
}

function getLaonRoot(): string {
  const extPath = vscode.extensions.getExtension('gameworkerkim.laon-vaultguard')?.extensionPath;
  // extension is at LAON_VaultGuard/vscode-extension, CLI is at LAON_VaultGuard/src/cli.ts
  if (extPath) return path.resolve(extPath, '..');
  return getWorkspaceRoot() || '';
}

async function runCLIScan(target: string): Promise<QuickFinding[]> {
  return new Promise((resolve) => {
    const laonRoot = getLaonRoot();
    const cliPath = path.join(laonRoot, 'src', 'cli.ts');
    const cmd = `npx tsx "${cliPath}" scan "${target}"`;

    exec(cmd, { cwd: laonRoot, timeout: 120000, env: { ...process.env, FORCE_COLOR: '0' } }, (error, stdout, stderr) => {
      if (error && !stdout) {
        vscode.window.showErrorMessage(`LAON scan failed: ${error.message}`);
        resolve([]);
        return;
      }

      // Parse CLI output for findings (format: file:line: [PROVIDER] TYPE — fingerprint)
      const results: QuickFinding[] = [];
      const lines = stdout.split('\n');
      for (const line of lines) {
        const match = line.match(/^(.+?):(\d+):\s*\[(.+?)\]\s+(.+?)\s*[—–-]\s*(.+)$/);
        if (match) {
          const [, file, lineNum, provider, type, fingerprint] = match;
          results.push({
            line: parseInt(lineNum, 10) - 1,
            startCol: 0,
            endCol: 999,
            text: fingerprint.trim(),
            rule: `[${provider}] ${type}`,
            severity: vscode.DiagnosticSeverity.Error,
          });
        }
      }

      resolve(results);
    });
  });
}

// ── Commands ──

async function commandScanWorkspace() {
  const root = getWorkspaceRoot();
  if (!root) {
    vscode.window.showErrorMessage('No workspace folder open.');
    return;
  }

  statusBarItem.text = '$(sync~spin) LAON: scanning...';
  statusBarItem.show();

  try {
    const findings = await runCLIScan(root);
    if (findings.length === 0) {
      vscode.window.showInformationMessage('LAON VaultGuard: No secrets found ✅');
    } else {
      vscode.window.showWarningMessage(`LAON VaultGuard: ${findings.length} secret(s) detected ⚠`);
    }
    updateStatus(findings.length);
  } finally {
    statusBarItem.text = '$(shield) LAON';
  }
}

async function commandScanFile() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor.');
    return;
  }

  const findings = scanText(editor.document.getText());
  updateDiagnostics(editor.document, findings);
  updateDecorations(editor, findings);

  if (findings.length === 0) {
    vscode.window.showInformationMessage('No secrets detected in this file.');
  } else {
    vscode.window.showWarningMessage(`${findings.length} potential secret(s) found in this file.`);
  }
  updateStatus(findings.length);
}

function commandClearDiagnostics() {
  diagnosticCollection.clear();
  if (vscode.window.activeTextEditor) {
    vscode.window.activeTextEditor.setDecorations(secretDecoration, []);
  }
  updateStatus(0);
}

function updateStatus(count: number) {
  if (count === 0) {
    statusBarItem.text = '$(shield) LAON: clean';
    statusBarItem.backgroundColor = undefined;
  } else {
    statusBarItem.text = `$(warning) LAON: ${count}`;
    statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
  }
  statusBarItem.show();
}

// ── Activation ──

export function activate(context: vscode.ExtensionContext) {
  // status bar
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = '$(shield) LAON';
  statusBarItem.tooltip = 'LAON VaultGuard — Secret Scanner';
  statusBarItem.command = 'laon-vaultguard.scan';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // commands
  context.subscriptions.push(
    vscode.commands.registerCommand('laon-vaultguard.scan', commandScanWorkspace),
    vscode.commands.registerCommand('laon-vaultguard.scanFile', commandScanFile),
    vscode.commands.registerCommand('laon-vaultguard.clearDiagnostics', commandClearDiagnostics),
  );

  // scan active editor on activation
  if (vscode.window.activeTextEditor) {
    scanDocument(vscode.window.activeTextEditor.document);
  }

  // watch for document changes
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => {
      const config = vscode.workspace.getConfiguration('laon-vaultguard');
      if (config.get<boolean>('scanOnOpen', false)) scanDocument(doc);
    }),
    vscode.workspace.onDidSaveTextDocument(doc => {
      const config = vscode.workspace.getConfiguration('laon-vaultguard');
      if (config.get<boolean>('scanOnSave', true)) scanDocument(doc);
    }),
    vscode.window.onDidChangeActiveTextEditor(editor => {
      if (editor) scanDocument(editor.document);
    }),
    vscode.workspace.onDidChangeTextDocument(event => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        scheduleDecorationUpdate(editor);
      }
    }),
    vscode.workspace.onDidCloseTextDocument(doc => {
      diagnosticCollection.delete(doc.uri);
    }),
  );

  vscode.window.showInformationMessage('LAON VaultGuard activated — watching for secrets.');
}

export function deactivate() {
  diagnosticCollection.clear();
  diagnosticCollection.dispose();
  secretDecoration.dispose();
}
