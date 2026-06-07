// services/market.ts — Market data (indices, ETFs, risk gauge)

export async function getMarketData() {
  return {
    indices: [
      { name: 'NASDAQ', ticker: '^IXIC', price: 19650.42, change_pct: 0.85 },
      { name: 'S&P 500', ticker: '^GSPC', price: 5980.30, change_pct: 0.52 },
      { name: 'SOX (Semis)', ticker: '^SOX', price: 5640.18, change_pct: 1.24 },
      { name: 'KOSPI', ticker: '^KS11', price: 2785.60, change_pct: -0.35 },
    ],
    etfs: [
      { ticker: 'QQQ', name: 'Invesco QQQ', price: 520.45, change_pct: 0.78 },
      { ticker: 'SMH', name: 'VanEck Semi', price: 268.30, change_pct: 1.45 },
      { ticker: 'SOXX', name: 'iShares Semi', price: 248.90, change_pct: 1.32 },
      { ticker: 'XLK', name: 'Tech Sector', price: 228.15, change_pct: 0.61 },
      { ticker: 'TQQQ', name: 'ProShares 3x QQQ', price: 82.40, change_pct: 2.34 },
    ],
    risk_gauge: {
      score: 35,
      label: 'Moderate Risk',
      vix: 18.5,
      vix_change: -1.2,
      put_call_ratio: 0.72,
      credit_spread: 1.15,
    },
    sector_heatmap: [
      { sector: 'AI Semiconductor', change_pct: 2.8 },
      { sector: 'Cloud/Platform', change_pct: 1.2 },
      { sector: 'Memory', change_pct: 3.1 },
      { sector: 'Networking', change_pct: 1.8 },
      { sector: 'EV/Autonomous', change_pct: -0.9 },
      { sector: 'Enterprise SW', change_pct: 0.4 },
    ],
    ai_summary: 'AI/반도체 섹터 강세 지속. NVDA +2.3%, MU +3.1%로 메모리·GPU 수요 견조. ARDS RISK_ON 시그널로 위험자산 비중 확대 가능. VIX 18.5로 안정적. 주간 리밸런스 기준 Foundation·Infrastructure 레이어 비중 확대 유지.',
  };
}
