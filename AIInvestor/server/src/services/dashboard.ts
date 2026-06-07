// services/dashboard.ts — Vibe Investing dashboard data (strategy signals + AI supercycle rankings)

export async function getDashboardData() {
  return {
    // Strategy signals summary
    strategies: [
      {
        id: 'ards',
        name: 'ARDS',
        full: 'Adaptive Recession-Defensive Strategy',
        signal: 'RISK_ON',
        label: 'Risk-On',
        description: 'Macro environment favorable. Equity risk premium positive, credit spreads tightening.',
        detail: {
          regime: 'RISK_ON',
          recession_composite: 32,
          price_stress: 18,
          recommend: 'Full equity allocation. AMQS momentum strategy active.',
        },
      },
      {
        id: 'amqs',
        name: 'AMQS',
        full: 'Adaptive Momentum Quant Strategy',
        signal: 'BUY',
        label: 'Buy Signal',
        description: '4-Factor composite momentum above +0.5 threshold. Top names selected.',
        detail: {
          top_sector: 'AI Semiconductor',
          momentum_score: 78,
          rotation: 'Weekly rebalance active',
        },
      },
    ],

    // AI Supercycle — 4-Layer Model rankings
    ai_supercycle_ranking: {
      title: 'AI Supercycle Stock Ranking (4-Layer Model)',
      updated: '2026-06-07T09:00:00Z',
      layers: [
        {
          name: 'Foundation',
          label: 'Foundation',
          description: 'GPU, AI accelerators, custom silicon',
          stocks: [
            { ticker: 'NVDA', name: 'NVIDIA', rank: 1, score: 98, signal: 'BUY', change_pct: 2.3 },
            { ticker: 'AVGO', name: 'Broadcom', rank: 2, score: 92, signal: 'BUY', change_pct: 0.8 },
            { ticker: 'AMD', name: 'AMD', rank: 3, score: 85, signal: 'HOLD', change_pct: -1.2 },
          ],
        },
        {
          name: 'Infrastructure',
          label: 'Infrastructure',
          description: 'Memory, networking, servers, data centers',
          stocks: [
            { ticker: 'MU', name: 'Micron', rank: 1, score: 90, signal: 'BUY', change_pct: 3.1 },
            { ticker: 'MRVL', name: 'Marvell', rank: 2, score: 87, signal: 'BUY', change_pct: 1.5 },
            { ticker: 'SMCI', name: 'Super Micro', rank: 3, score: 78, signal: 'HOLD', change_pct: -0.5 },
            { ticker: 'ANET', name: 'Arista', rank: 4, score: 75, signal: 'BUY', change_pct: 2.0 },
          ],
        },
        {
          name: 'Enablers',
          label: 'Enablers',
          description: 'Cloud platforms, AI services, model providers',
          stocks: [
            { ticker: 'MSFT', name: 'Microsoft', rank: 1, score: 95, signal: 'BUY', change_pct: 0.6 },
            { ticker: 'AMZN', name: 'Amazon', rank: 2, score: 91, signal: 'BUY', change_pct: -0.3 },
            { ticker: 'GOOGL', name: 'Alphabet', rank: 3, score: 88, signal: 'BUY', change_pct: 1.2 },
          ],
        },
        {
          name: 'Applications',
          label: 'Applications',
          description: 'AI-native software, autonomous, enterprise AI',
          stocks: [
            { ticker: 'META', name: 'Meta', rank: 1, score: 93, signal: 'BUY', change_pct: 1.8 },
            { ticker: 'TSLA', name: 'Tesla', rank: 2, score: 82, signal: 'HOLD', change_pct: -2.1 },
            { ticker: 'CRM', name: 'Salesforce', rank: 3, score: 76, signal: 'HOLD', change_pct: 0.4 },
          ],
        },
      ],
      methodology: 'Composite score based on: (1) 12-1 month momentum (50%), (2) 6-1 month momentum (30%), (3) revenue growth YoY (10%), (4) analyst revision momentum (10%). Rebalanced weekly.',
    },

    // Watchlist — key stocks with signals
    watchlist: [
      { ticker: 'NVDA', name: 'NVIDIA', sector: 'AI Semi', signal: 'BUY', price: 145.20, change_pct: 2.3 },
      { ticker: 'AVGO', name: 'Broadcom', sector: 'AI Semi', signal: 'BUY', price: 182.50, change_pct: 0.8 },
      { ticker: 'AMD', name: 'AMD', sector: 'AI Semi', signal: 'HOLD', price: 112.30, change_pct: -1.2 },
      { ticker: 'MU', name: 'Micron', sector: 'Memory', signal: 'BUY', price: 98.75, change_pct: 3.1 },
      { ticker: 'MSFT', name: 'Microsoft', sector: 'Cloud', signal: 'BUY', price: 468.90, change_pct: 0.6 },
      { ticker: 'GOOGL', name: 'Alphabet', sector: 'Cloud', signal: 'BUY', price: 195.40, change_pct: 1.2 },
      { ticker: 'AMZN', name: 'Amazon', sector: 'Cloud', signal: 'BUY', price: 215.60, change_pct: -0.3 },
      { ticker: 'META', name: 'Meta', sector: 'Social/AI', signal: 'BUY', price: 530.20, change_pct: 1.8 },
      { ticker: 'TSLA', name: 'Tesla', sector: 'EV/AI', signal: 'HOLD', price: 245.80, change_pct: -2.1 },
      { ticker: 'MRVL', name: 'Marvell', sector: 'Networking', signal: 'BUY', price: 88.40, change_pct: 1.5 },
      { ticker: 'AAPL', name: 'Apple', sector: 'Big Tech', signal: 'HOLD', price: 228.30, change_pct: 0.2 },
      { ticker: 'SMCI', name: 'Super Micro', sector: 'Server', signal: 'HOLD', price: 520.10, change_pct: -0.5 },
      { ticker: 'ANET', name: 'Arista', sector: 'Networking', signal: 'BUY', price: 365.00, change_pct: 2.0 },
      { ticker: 'CRM', name: 'Salesforce', sector: 'Enterprise', signal: 'HOLD', price: 305.20, change_pct: 0.4 },
      { ticker: 'QCOM', name: 'Qualcomm', sector: 'AI Semi', signal: 'HOLD', price: 188.60, change_pct: -0.8 },
    ],
  };
}
