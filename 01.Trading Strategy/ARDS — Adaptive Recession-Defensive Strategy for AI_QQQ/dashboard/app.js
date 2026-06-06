/* ARDS-X Regime Classifier — Dashboard */
"use strict";

const STATE_LABEL = {
  UPTREND_HEALTHY: "정상 상승추세",
  CORRECTION: "조정",
  OVERSOLD_BOUNCE: "단기 과매도",
  DOWNTREND_DISTRIBUTION: "하락 / 분배",
  RECESSION_REBALANCE: "자산 리밸런싱 (침체)",
};

const fmt = (n, d = 1) => (n === null || n === undefined || Number.isNaN(n) ? "–" : Number(n).toFixed(d));
const sign = (n) => (n > 0 ? "pos" : n < 0 ? "neg" : "");
const el = (id) => document.getElementById(id);

async function load() {
  let data;
  try {
    const res = await fetch("data/latest.json?_=" + Date.now());
    data = await res.json();
  } catch (e) {
    document.body.insertAdjacentHTML("beforeend",
      `<p style="color:#ff5a5f;padding:22px">latest.json 로드 실패: ${e}. quant/run.py 를 먼저 실행하세요.</p>`);
    return;
  }
  render(data);
}

function render(d) {
  const v = d.verdict;
  el("asof").textContent = "기준: " + (d.asof || "").replace("T", " ").slice(0, 16);

  // ---- 판정 배지 ----
  const badge = el("verdictBadge");
  badge.className = "verdict-badge state-" + v.state;
  badge.innerHTML = `<div>${v.state_kr}</div><div style="font-size:11px;font-weight:600;opacity:.8;margin-top:8px">${v.action}</div>`;
  el("verdictKr").innerHTML = `${v.state_kr} <span style="font-size:13px;color:var(--muted);font-weight:600">${v.state}</span>`;
  el("verdictHeadline").innerHTML = mdBold(v.headline);
  el("verdictHandoff").innerHTML = mdBold(v.handoff);
  el("confFill").style.width = v.confidence + "%";
  el("confVal").textContent = v.confidence + "%";

  // ---- 2축 맵 ----
  const macroX = clamp(v.axes.macro);
  const stressY = clamp(v.axes.price_stress);
  const dot = el("mapDot");
  dot.style.left = macroX + "%";
  dot.style.bottom = stressY + "%";
  dot.title = `거시 ${fmt(v.axes.macro, 0)} · 가격스트레스 ${fmt(v.axes.price_stress, 0)}`;
  el("mapAxes").innerHTML = `
    <div><b>거시 침체축(X):</b> ${fmt(v.axes.macro, 0)}/100 · Phase ${v.axes.macro_phase_kr}</div>
    <div><b>가격 스트레스(Y):</b> ${fmt(v.axes.price_stress, 0)}/100</div>
    <div><b>하락 점수:</b> ${fmt(v.axes.decline_score, 0)} · <b>과매도 점수:</b> ${fmt(v.axes.oversold_score, 0)}</div>
    <div style="margin-top:8px"><b>테이프 고점대비:</b> <span class="${sign(v.evidence.tape_drawdown)}">${fmt(v.evidence.tape_drawdown)}%</span></div>
    <div><b>복합체 200일선 위:</b> ${fmt(v.evidence.breadth_above_200dma, 0)}%</div>
    <div><b>지수 최저 RSI:</b> ${fmt(v.evidence.index_min_rsi14, 0)}</div>
    <div><b>추세 붕괴:</b> ${v.evidence.trend_broken ? "예 ⚠️" : "아니오"}</div>`;

  // ---- 거시 5-Factor ----
  el("macroComposite").textContent = fmt(d.macro.composite, 1);
  el("macroPhase").textContent = `Phase: ${d.macro.phase} (${d.macro.phase_kr})`;
  const order = ["A_yield_curve", "B_sahm", "C_ism_proxy", "D_lei_proxy", "E_credit"];
  el("factorList").innerHTML = order.map((k) => {
    const f = d.macro.components[k];
    const sc = f.score;
    const w = sc === null ? 0 : sc;
    const tag = f.status === "live" ? "tag-live" : f.status === "proxy" ? "tag-proxy" : "tag-missing";
    const tagTxt = f.status === "live" ? "실데이터" : f.status === "proxy" ? "프록시" : "결측";
    const col = sc === null ? "var(--muted)" : sc >= 60 ? "var(--red)" : sc >= 40 ? "var(--orange)" : "var(--green)";
    return `<div class="factor">
      <span class="fname">${f.label} <span style="color:var(--muted)">${Math.round(f.weight * 100)}%</span></span>
      <span class="fbar"><span class="ffill" style="width:${w}%;background:${col}"></span></span>
      <span class="fscore">${sc === null ? "–" : fmt(sc, 0)}</span>
      <span class="ftag ${tag}">${tagTxt}</span>
    </div>`;
  }).join("");
  const dq = d.data_quality;
  el("dataQuality").textContent =
    `데이터: 거시 실데이터 ${dq.macro_live} · 프록시 ${dq.macro_proxy} · 결측 ${dq.macro_missing} | 가격 ${dq.n_prices}/${dq.n_expected}종목` +
    (dq.macro_missing >= 2 ? "  ⚠️ 거시 결측多 — Composite 신뢰도 하향" : "");

  // ---- 지수 표 ----
  el("indexTable").querySelector("tbody").innerHTML = d.indices.map(rowIndex).join("");

  // 그룹 카드
  el("groupCards").innerHTML = Object.values(d.groups || {}).map((g) => `
    <div class="gcard">
      <div class="gh">${g.label} (${g.n})</div>
      <div class="gv ${sign(g.avg_dd_from_high)}">${fmt(g.avg_dd_from_high)}%</div>
      <div class="gs">200일선 위 ${fmt(g.breadth_above_200dma, 0)}% · RSI ${fmt(g.avg_rsi14, 0)}</div>
    </div>`).join("");

  // ---- 복합체 ----
  const ca = d.complex_aggregate;
  el("breadthHint").textContent =
    `평균 고점대비 ${fmt(ca.avg_dd_from_high)}% · 200일선 위 ${fmt(ca.breadth_above_200dma, 0)}% · 과매도 ${ca.n_oversold}/${ca.n}종목`;
  el("complexTable").querySelector("tbody").innerHTML = d.complex.map(rowComplex).join("");

  el("footer").textContent = "⚠️ " + d.disclaimer;
}

function rowIndex(r) {
  return `<tr>
    <td class="left"><b>${r.name}</b> <span class="grp">${r.ticker}</span></td>
    <td>${fmt(r.last, 0)}</td>
    <td class="${sign(r.dd_from_high)}">${fmt(r.dd_from_high)}%</td>
    <td class="${sign(r.pct_vs_50dma)}">${fmt(r.pct_vs_50dma)}%</td>
    <td class="${sign(r.pct_vs_200dma)}">${fmt(r.pct_vs_200dma)}%</td>
    <td>${fmt(r.rsi14, 0)}</td>
    <td>${trendPill(r)}</td>
  </tr>`;
}

function rowComplex(r) {
  return `<tr>
    <td class="left"><b>${r.name}</b> <span class="grp">${r.ticker}</span></td>
    <td class="grp">${groupKr(r.group)}</td>
    <td>${fmt(r.last, 0)}</td>
    <td class="${sign(r.dd_from_high)}">${fmt(r.dd_from_high)}%</td>
    <td class="${r.above_200dma ? "" : "neg"}">${fmt(r.pct_vs_200dma)}%</td>
    <td>${fmt(r.rsi14, 0)}</td>
    <td class="${sign(r.mom6m)}">${fmt(r.mom6m)}%</td>
    <td class="score-cell" style="color:${scoreCol(r.decline_score, true)}">${fmt(r.decline_score, 0)}</td>
    <td class="score-cell" style="color:${scoreCol(r.oversold_score, false)}">${fmt(r.oversold_score, 0)}</td>
  </tr>`;
}

function trendPill(r) {
  if (r.above_200dma && r.golden_cross) return `<span class="pill pill-ok">상승</span>`;
  if (!r.above_200dma && !r.golden_cross) return `<span class="pill pill-bad">붕괴</span>`;
  return `<span class="pill pill-warn">혼조</span>`;
}

function groupKr(g) {
  return { bigtech: "빅테크", ai_semi: "AI 반도체", ai_infra: "AI 인프라" }[g] || g || "–";
}
function scoreCol(s, isDecline) {
  if (isDecline) return s >= 60 ? "var(--red)" : s >= 35 ? "var(--orange)" : "var(--muted)";
  return s >= 60 ? "var(--blue)" : s >= 40 ? "var(--accent)" : "var(--muted)";
}
function clamp(x) { return Math.max(2, Math.min(98, Number(x) || 0)); }
function mdBold(s) { return (s || "").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>"); }

el("reloadBtn").addEventListener("click", load);
load();
