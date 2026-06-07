// alert-engine.ts — notification dispatch (Slack + Telegram + Email + Dashboard SSE)

import type { Repository, Finding } from './types.js';
import { config } from './config.js';
import { logAudit } from './db.js';
import { getAlertConfig } from './db.js';

export async function sendAlerts(repo: Repository, findings: Finding[]) {
  const criticalHigh = findings.filter(f => f.severity === 'critical' || f.severity === 'high');
  if (criticalHigh.length === 0) return;

  const alertCfg = getAlertConfig();

  // per-channel dispatch based on alert config
  if (alertCfg.slack && config.alerts.slack.webhookUrl) {
    await sendSlackAlert(repo, criticalHigh);
  }
  if (alertCfg.telegram && config.alerts.telegram.botToken && config.alerts.telegram.chatId) {
    await sendTelegramAlert(repo, criticalHigh);
  }
  if (alertCfg.email && config.alerts.email.host && config.alerts.email.user) {
    await sendEmailAlert(repo, criticalHigh, 'realtime');
  }
  if (alertCfg.teams && config.alerts.teams.webhookUrl) {
    await sendWebhookAlert(repo, criticalHigh, config.alerts.teams.webhookUrl, 'teams');
  }
  if (alertCfg.discord && config.alerts.discord.webhookUrl) {
    await sendWebhookAlert(repo, criticalHigh, config.alerts.discord.webhookUrl, 'discord');
  }
}

// ── Slack ──

async function sendSlackAlert(repo: Repository, findings: Finding[]) {
  const { webhookUrl } = config.alerts.slack;
  if (!webhookUrl) return;

  const blocks: Record<string, unknown>[] = [];

  blocks.push({
    type: 'header',
    text: { type: 'plain_text', text: `🛡 LAON VaultGuard — Secret Alert` },
  });

  const critical = findings.filter(f => f.severity === 'critical').length;
  const high = findings.filter(f => f.severity === 'high').length;
  blocks.push({
    type: 'section',
    text: {
      type: 'mrkdwn',
      text: `*Device:* ${config.deviceName}\n*Repo:* ${repo.name}\n*Findings:* ${findings.length} total (🔴 ${critical} critical, 🟠 ${high} high)`,
    },
  });

  blocks.push({ type: 'divider' });

  for (const f of findings.slice(0, 5)) {
    const emoji = f.severity === 'critical' ? '🔴' : '🟠';
    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `${emoji} *[${f.severity.toUpperCase()}] ${f.provider} — ${f.secretType}*\n📁 \`${f.filePath}${f.line ? `:${f.line}` : ''}\`\n🔑 \`${f.maskedFingerprint}\``,
      },
    });
  }

  if (findings.length > 5) {
    blocks.push({
      type: 'section',
      text: { type: 'mrkdwn', text: `_... and ${findings.length - 5} more findings_` },
    });
  }

  try {
    const res = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: `🛡 LAON VaultGuard — ${findings.length} secrets in ${repo.name}`, blocks }),
    });

    if (!res.ok) throw new Error(`Slack API error: ${await res.text()}`);
    logAudit('alert_sent', 'info', `Slack alert: ${findings.length} findings`, { repo: repo.name, channel: 'slack', findingsCount: findings.length });
  } catch (err) {
    logAudit('alert_error', 'error', `Slack alert failed: ${err instanceof Error ? err.message : String(err)}`, { repo: repo.name, channel: 'slack' });
  }
}

// ── Telegram ──

async function sendTelegramAlert(repo: Repository, findings: Finding[]) {
  const { botToken, chatId } = config.alerts.telegram;
  if (!botToken || !chatId) return;

  const lines = findings.map(f =>
    `🔴 [${f.severity.toUpperCase()}] ${f.provider} — ${f.secretType}\n` +
    `📁 ${repo.name}/${f.filePath}${f.line ? `:${f.line}` : ''}\n` +
    `🔑 ${f.maskedFingerprint}`
  );

  const message =
    `🛡 *LAON VaultGuard* — Secret Alert\n` +
    `🖥 Device: *${config.deviceName}*\n` +
    `📦 Repo: *${repo.name}*\n` +
    `⚠️ Findings: ${findings.length} critical/high\n\n` +
    lines.join('\n\n');

  try {
    const res = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text: message, parse_mode: 'Markdown', disable_web_page_preview: true }),
    });

    if (!res.ok) throw new Error(`Telegram API error: ${await res.text()}`);
    logAudit('alert_sent', 'info', `Telegram alert: ${findings.length} findings`, { repo: repo.name, channel: 'telegram', findingsCount: findings.length });
  } catch (err) {
    logAudit('alert_error', 'error', `Telegram alert failed: ${err instanceof Error ? err.message : String(err)}`, { repo: repo.name, channel: 'telegram' });
  }
}

// ── Email (nodemailer) ──

import nodemailer from 'nodemailer';

export async function sendEmailAlert(
  repo: Repository,
  findings: Finding[],
  type: 'realtime' | 'daily' | 'weekly',
) {
  const { host, port, user, pass, to } = config.alerts.email;
  if (!host || !user || !pass || !to) return;

  const transporter = nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });

  const subjectType = type === 'realtime' ? '🚨 CRITICAL Secret Alert' :
    type === 'daily' ? '📋 Daily Summary' : '📊 Weekly Summary';

  const subject = `[LAON VaultGuard] ${subjectType} — ${config.deviceName}`;

  const html = buildEmailHtml(repo, findings, type);

  try {
    await transporter.sendMail({
      from: `"LAON VaultGuard" <${user}>`,
      to,
      subject,
      html,
    });
    logAudit('alert_sent', 'info', `Email ${type} alert: ${findings.length} findings`, { repo: repo.name, channel: 'email', type, findingsCount: findings.length });
  } catch (err) {
    logAudit('alert_error', 'error', `Email alert failed: ${err instanceof Error ? err.message : String(err)}`, { repo: repo.name, channel: 'email', type });
  }
}

export async function sendSummaryReport(
  allFindings: Array<Finding & { repoName: string }>,
  type: 'daily' | 'weekly',
) {
  const { host, port, user, pass, to } = config.alerts.email;
  if (!host || !user || !pass || !to) return;

  const transporter = nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });

  const subject = `[LAON VaultGuard] ${type === 'daily' ? 'Daily' : 'Weekly'} Report — ${config.deviceName}`;
  const html = buildSummaryHtml(allFindings, type);

  try {
    await transporter.sendMail({
      from: `"LAON VaultGuard" <${user}>`,
      to,
      subject,
      html,
    });
    logAudit('report_sent', 'info', `${type} summary report sent (${allFindings.length} findings)`, { channel: 'email', type, findingsCount: allFindings.length });
  } catch (err) {
    logAudit('report_error', 'error', `Summary report failed: ${err instanceof Error ? err.message : String(err)}`, { channel: 'email', type });
  }
}

function buildEmailHtml(repo: Repository, findings: Finding[], type: string): string {
  const rows = findings.slice(0, 20).map(f => `
    <tr>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><span style="color:${f.severity === 'critical' ? '#f85149' : '#d29922'};font-weight:bold">${f.severity.toUpperCase()}</span></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${f.provider}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${f.secretType}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><code>${f.filePath}${f.line ? `:${f.line}` : ''}</code></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><code>${f.maskedFingerprint}</code></td>
    </tr>`).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:monospace;padding:20px">
<h1 style="color:#3fb950">🛡 LAON VaultGuard</h1>
<p><strong>Device:</strong> ${config.deviceName} · <strong>Type:</strong> ${type} · <strong>Time:</strong> ${new Date().toISOString()}</p>
<hr style="border-color:#30363d">
<h2 style="color:#f85149">🚨 Secret Alert — ${repo.name}</h2>
<p>Findings: ${findings.length} total (🔴 ${findings.filter(f=>f.severity==='critical').length} critical, 🟠 ${findings.filter(f=>f.severity==='high').length} high)</p>
<table style="width:100%;border-collapse:collapse;background:#161b22;border:1px solid #30363d;border-radius:8px">
<thead><tr style="text-align:left;color:#8b949e;font-size:13px">
<th style="padding:10px">Severity</th><th>Provider</th><th>Type</th><th>File</th><th>Fingerprint</th>
</tr></thead><tbody>${rows}</tbody></table>
<p style="color:#8b949e;margin-top:16px;font-size:12px">Sent by LAON VaultGuard · <a href="http://localhost:3101/dashboard" style="color:#58a6ff">Open Dashboard</a></p>
</body></html>`;
}

function buildSummaryHtml(findings: Array<Finding & { repoName: string }>, type: string): string {
  const openFindings = findings.filter(f => !f.acknowledged);
  const rows = openFindings.slice(0, 30).map(f => `
    <tr>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><span style="color:${f.severity === 'critical' ? '#f85149' : f.severity === 'high' ? '#d29922' : '#58a6ff'}">${f.severity.toUpperCase()}</span></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${f.repoName}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d">${f.provider} — ${f.secretType}</td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d"><code>${f.maskedFingerprint}</code></td>
      <td style="padding:6px 10px;border-bottom:1px solid #30363d;font-size:12px">${f.detectedAt.slice(0, 10)}</td>
    </tr>`).join('');

  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="background:#0d1117;color:#c9d1d9;font-family:monospace;padding:20px">
<h1 style="color:#3fb950">🛡 LAON VaultGuard — ${type === 'daily' ? 'Daily' : 'Weekly'} Report</h1>
<p><strong>Device:</strong> ${config.deviceName} · <strong>Period:</strong> ${type} · <strong>Generated:</strong> ${new Date().toISOString()}</p>
<hr style="border-color:#30363d">
<div style="display:flex;gap:16px;margin:16px 0">
  <div style="background:#161b22;padding:12px;border-radius:8px;border:1px solid #30363d;flex:1">
    <span style="color:#8b949e;font-size:12px">OPEN FINDINGS</span><br>
    <span style="font-size:24px;color:#f85149">${openFindings.length}</span>
  </div>
  <div style="background:#161b22;padding:12px;border-radius:8px;border:1px solid #30363d;flex:1">
    <span style="color:#8b949e;font-size:12px">CRITICAL</span><br>
    <span style="font-size:24px;color:#f85149">${openFindings.filter(f => f.severity === 'critical').length}</span>
  </div>
  <div style="background:#161b22;padding:12px;border-radius:8px;border:1px solid #30363d;flex:1">
    <span style="color:#8b949e;font-size:12px">HIGH</span><br>
    <span style="font-size:24px;color:#d29922">${openFindings.filter(f => f.severity === 'high').length}</span>
  </div>
</div>
<table style="width:100%;border-collapse:collapse;background:#161b22;border:1px solid #30363d;border-radius:8px">
<thead><tr style="text-align:left;color:#8b949e;font-size:13px">
<th style="padding:10px">Severity</th><th>Repo</th><th>Type</th><th>Fingerprint</th><th>Date</th>
</tr></thead><tbody>${rows || '<tr><td colspan="5" style="padding:20px;text-align:center;color:#3fb950">✅ No open findings</td></tr>'}</tbody></table>
<p style="color:#8b949e;margin-top:16px;font-size:12px">Sent by LAON VaultGuard · <a href="http://localhost:3101/dashboard" style="color:#58a6ff">Open Dashboard</a></p>
</body></html>`;
}

// Teams / Discord (generic webhook)

async function sendWebhookAlert(
  repo: Repository,
  findings: Finding[],
  webhookUrl: string,
  channel: 'teams' | 'discord',
) {
  const critical = findings.filter(f => f.severity === 'critical').length;
  const high = findings.filter(f => f.severity === 'high').length;

  const message = channel === 'discord'
    ? {
        embeds: [{
          title: 'LAON VaultGuard — Secret Alert',
          description: `**Device:** ${config.deviceName}\n**Repo:** ${repo.name}\n**Findings:** ${findings.length} (critical: ${critical}, high: ${high})`,
          color: critical > 0 ? 0xf85149 : 0xd29922,
          fields: findings.slice(0, 10).map(f => ({
            name: `[${f.severity.toUpperCase()}] ${f.provider} — ${f.secretType}`,
            value: `File: \`${f.filePath}${f.line ? `:${f.line}` : ''}\`\nFingerprint: \`${f.maskedFingerprint}\``,
          })),
        }],
      }
    : {
        type: 'message',
        attachments: [{
          contentType: 'application/vnd.microsoft.card.adaptive',
          content: {
            type: 'AdaptiveCard',
            version: '1.4',
            body: [
              { type: 'TextBlock', text: 'LAON VaultGuard — Secret Alert', weight: 'bolder', size: 'large' },
              { type: 'FactSet', facts: [
                { title: 'Device', value: config.deviceName },
                { title: 'Repo', value: repo.name },
                { title: 'Critical', value: String(critical) },
                { title: 'High', value: String(high) },
              ]},
              ...findings.slice(0, 5).map(f => ({
                type: 'TextBlock' as const,
                text: `[${f.severity.toUpperCase()}] ${f.provider} — ${f.secretType}\n${f.filePath}${f.line ? `:${f.line}` : ''} | ${f.maskedFingerprint}`,
                wrap: true,
              })),
            ],
          },
        }],
      };

  try {
    const res = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message),
    });
    if (!res.ok) throw new Error(`${channel} API error: ${await res.text()}`);
    logAudit('alert_sent', 'info', `${channel} alert: ${findings.length} findings`, { repo: repo.name, channel, findingsCount: findings.length });
  } catch (err) {
    logAudit('alert_error', 'error', `${channel} alert failed: ${err instanceof Error ? err.message : String(err)}`, { repo: repo.name, channel });
  }
}
