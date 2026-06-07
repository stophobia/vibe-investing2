// alert-engine.ts — notification dispatch (Telegram + Dashboard SSE)

import type { Repository, Finding } from './types.js';
import { config } from './config.js';
import { logAudit } from './db.js';

export async function sendAlerts(repo: Repository, findings: Finding[]) {
  const criticalHigh = findings.filter(f => f.severity === 'critical' || f.severity === 'high');
  if (criticalHigh.length === 0) return;

  // Telegram
  if (config.alerts.telegram.botToken && config.alerts.telegram.chatId) {
    await sendTelegramAlert(repo, criticalHigh);
  }

  // Slack (future)
  // Email (future)
}

async function sendTelegramAlert(repo: Repository, findings: Finding[]) {
  const { botToken, chatId } = config.alerts.telegram;
  if (!botToken || !chatId) return;

  const lines = findings.map(f =>
    `🔴 [${f.severity.toUpperCase()}] ${f.provider} — ${f.secretType}\n` +
    `📁 ${repo.name}/${f.filePath}${f.line ? `:${f.line}` : ''}\n` +
    `🔑 ${f.maskedFingerprint}\n` +
    `💡 ${f.remediation.slice(0, 120)}`
  );

  const message =
    `🛡 *LAON VaultGuard* — Secret Alert\n\n` +
    `📦 Repo: *${repo.name}*\n` +
    `⚠️ Findings: ${findings.length} critical/high\n\n` +
    lines.join('\n\n');

  try {
    const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
    const body = {
      chat_id: chatId,
      text: message,
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Telegram API error: ${err}`);
    }

    logAudit('alert_sent', 'info', `Telegram alert sent: ${findings.length} findings`, {
      repo: repo.name, channel: 'telegram', findingsCount: findings.length,
    });
  } catch (err) {
    logAudit('alert_error', 'error',
      `Telegram alert failed: ${err instanceof Error ? err.message : String(err)}`,
      { repo: repo.name, channel: 'telegram' },
    );
  }
}
