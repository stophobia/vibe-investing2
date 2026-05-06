"""Static HTML strings for the dashboard endpoint.

Two templates:
- _LANDING_HTML — public marketing page when no/wrong dashboard key
- _DASHBOARD_HTML — operator stats page when key matches; uses Chart.js CDN

Both intentionally have no external CSS — styled inline so the response
stays a single self-contained HTML blob.
"""

from __future__ import annotations

import json


def landing_page() -> str:
    return _LANDING_HTML


def dashboard_page(stats_24h: dict | None, stats_7d: dict | None, key_param: str) -> str:
    safe_24h = json.dumps(stats_24h or {}, ensure_ascii=False)
    safe_7d = json.dumps(stats_7d or {}, ensure_ascii=False)
    return _DASHBOARD_HTML.replace("__STATS_24H__", safe_24h)\
                           .replace("__STATS_7D__", safe_7d)\
                           .replace("__KEY__", key_param)


_LANDING_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Investor — 증권당 텔레그램 챗봇</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 720px; margin: 40px auto; padding: 0 24px; color: #222;
         line-height: 1.6; }
  h1 { font-size: 28px; margin-bottom: 8px; }
  .subtitle { color: #666; margin-bottom: 32px; }
  .persona-card { border: 1px solid #e2e2e2; border-radius: 8px; padding: 16px;
                   margin: 12px 0; background: #fafafa; }
  .persona-name { font-weight: 600; }
  .lang { font-size: 13px; color: #888; margin-top: 16px; }
  .disclaimer { background: #fff8e1; border-left: 4px solid #f9a825;
                 padding: 12px 16px; margin: 24px 0; font-size: 14px; }
  .cta { display: inline-block; background: #1976d2; color: white; padding: 12px 20px;
         border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 12px; }
  .cta:hover { background: #1565c0; }
  footer { margin-top: 48px; font-size: 12px; color: #999; }
</style>
</head>
<body>
  <h1>증권당 — 투자의 대가 페르소나 텔레그램 챗봇</h1>
  <p class="subtitle">당신만의 투자 멘토가 되어드릴 페르소나를 선택하고,
     매일의 미국 시황을 자연어로 만나 보세요.</p>

  <div class="persona-card">
    <div class="persona-name">📈 워렌 버핏 — 장기 가치 투자</div>
    <div>해자, owner earnings, 내재가치 기반 시각</div>
  </div>
  <div class="persona-card">
    <div class="persona-name">⚖️ 레이 달리오 — 매크로 / 올웨더</div>
    <div>크레딧 사이클·금리·인플레·지정학을 통합한 시각</div>
  </div>
  <div class="persona-card">
    <div class="persona-name">🚀 캐시 우드 — 혁신 성장</div>
    <div>AI / 로봇 / 유전학 / 블록체인 5년 잠재 성장</div>
  </div>

  <p class="lang">지원 언어: 한국어 / English / 日本語 / 中文</p>

  <div class="disclaimer">
    ⚠ 본 서비스는 투자 자문이 아닙니다. AI는 환각·오류가 있을 수 있으며,
    실제 투자는 전문가의 조언이 필요합니다. 모든 투자 판단의 책임은 본인에게 있습니다.
  </div>

  <a class="cta" href="https://t.me/AI_vibe_investor_bot">▶ 텔레그램에서 시작하기</a>

  <footer>
    AI Investor v1 — Korea Central · DeepSeek · Yahoo Finance
  </footer>
</body>
</html>
"""

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Investor — Operations Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 1100px; margin: 24px auto; padding: 0 24px; color: #222; }
  h1 { font-size: 22px; margin-bottom: 4px; }
  .gen { color: #888; font-size: 13px; margin-bottom: 24px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .card { border: 1px solid #e2e2e2; border-radius: 8px; padding: 16px;
          background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
  .card h3 { margin: 0 0 12px 0; font-size: 14px; color: #555; }
  .big-number { font-size: 28px; font-weight: 700; color: #1976d2; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid #f0f0f0; }
  th { background: #fafafa; color: #666; font-weight: 600; }
  .download { margin-top: 24px; }
  .download a { background: #1976d2; color: white; padding: 8px 14px; border-radius: 4px;
                text-decoration: none; margin-right: 8px; font-size: 13px; }
  .pill { display: inline-block; background: #e3f2fd; color: #1976d2; padding: 2px 8px;
          border-radius: 12px; font-size: 12px; margin: 2px; }
  canvas { max-height: 220px; }
</style>
</head>
<body>
  <h1>AI Investor — Operations Dashboard</h1>
  <div class="gen" id="gen-info">Loading…</div>

  <div class="grid">
    <div class="card">
      <h3>📊 응답 분류 (24h)</h3>
      <canvas id="tierChart"></canvas>
    </div>
    <div class="card">
      <h3>⏱ p50 응답시간 (ms, 24h)</h3>
      <canvas id="latencyChart"></canvas>
    </div>
    <div class="card">
      <h3>🌐 언어 분포 (24h)</h3>
      <canvas id="langChart"></canvas>
    </div>
    <div class="card">
      <h3>👤 페르소나 분포 (24h)</h3>
      <canvas id="personaChart"></canvas>
    </div>
    <div class="card" style="grid-column: span 2;">
      <h3>🔝 Top 20 ticker (24h)</h3>
      <table id="topTickers"><thead><tr><th>#</th><th>Ticker</th><th>Hits</th></tr></thead><tbody></tbody></table>
    </div>
    <div class="card" style="grid-column: span 2;">
      <h3>💸 LLM 토큰 사용량 (24h)</h3>
      <div>입력: <span class="big-number" id="llmIn">—</span> 토큰
           &nbsp;&nbsp;&nbsp; 출력: <span class="big-number" id="llmOut">—</span> 토큰</div>
    </div>
  </div>

  <div class="download">
    <a href="/api/dashboard_export?key=__KEY__&window=24h">📥 CSV (24h)</a>
    <a href="/api/dashboard_export?key=__KEY__&window=7d">📥 CSV (7d)</a>
  </div>

<script>
const stats24 = __STATS_24H__;
const stats7 = __STATS_7D__;

document.getElementById('gen-info').textContent =
  '24h total: ' + (stats24.total || 0) + ' · 7d total: ' + (stats7.total || 0) +
  ' · 갱신: ' + (stats24.generated_at || '—');

const palette = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c62828', '#0097a7', '#5d4037'];

function pieFromObj(canvasId, obj) {
  const labels = Object.keys(obj || {});
  const data = labels.map(k => obj[k]);
  new Chart(document.getElementById(canvasId), {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: palette }] },
    options: { plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } } }
  });
}

function barFromObj(canvasId, obj, label) {
  const labels = Object.keys(obj || {});
  const data = labels.map(k => obj[k]);
  new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: { labels, datasets: [{ data, label, backgroundColor: '#1976d2' }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
  });
}

pieFromObj('tierChart', stats24.tier_counts);
barFromObj('latencyChart', stats24.p50_by_tier, 'p50 ms');
pieFromObj('langChart', stats24.language_dist);
pieFromObj('personaChart', stats24.persona_dist);

const tbody = document.querySelector('#topTickers tbody');
(stats24.top_tickers || []).forEach(([t, n], i) => {
  const tr = document.createElement('tr');
  tr.innerHTML = `<td>${i+1}</td><td>${t}</td><td>${n}</td>`;
  tbody.appendChild(tr);
});

document.getElementById('llmIn').textContent  = (stats24.llm_total_in || 0).toLocaleString();
document.getElementById('llmOut').textContent = (stats24.llm_total_out || 0).toLocaleString();
</script>
</body>
</html>
"""
