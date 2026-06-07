// routes/vibe.ts — Vibe Investing API endpoints

import { Router } from 'express';
import { getDashboardData } from '../services/dashboard.js';
import { getMarketData } from '../services/market.js';
import { getRankings, trackVisit } from '../services/stats.js';

export const vibeRouter = Router();

// GET /api/vibe/dashboard — strategy signals, watchlist, AI supercycle ranking
vibeRouter.get('/dashboard', async (_req, res) => {
  try {
    const data = await getDashboardData();
    res.json({ data, updated_at: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: 'Failed to load dashboard data' });
  }
});

// GET /api/vibe/market — market indices, ETFs, risk gauge, AI summary
vibeRouter.get('/market', async (_req, res) => {
  try {
    const data = await getMarketData();
    res.json({ data, updated_at: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: 'Failed to load market data' });
  }
});

// GET /api/vibe/news — AI news summary
vibeRouter.get('/news', async (_req, res) => {
  res.json({ data: { market_summary: 'Market summary from LLM analysis will appear here.', items: [] } });
});

// GET /api/vibe/rankings — popular search rankings
vibeRouter.get('/rankings', async (_req, res) => {
  const data = await getRankings();
  res.json({ data });
});

// POST /api/vibe/track — site visit tracking
vibeRouter.post('/track', async (_req, res) => {
  const stats = await trackVisit();
  res.json({ data: stats });
});

// GET /api/vibe/search — ticker search
vibeRouter.get('/search', async (req, res) => {
  const q = (req.query.q as string || '').toUpperCase();
  const tickers: Record<string, { name: string; sector: string; signals: Array<{ strategy: string; signal: string; date: string }> }> = {
    'NVDA': { name: 'NVIDIA', sector: 'AI Semiconductor', signals: [{ strategy: 'AMQS', signal: 'BUY', date: '2026-06-07' }, { strategy: 'ARDS', signal: 'RISK_ON', date: '2026-06-07' }] },
    'AAPL': { name: 'Apple', sector: 'Big Tech', signals: [{ strategy: 'AMQS', signal: 'HOLD', date: '2026-06-07' }] },
    'MSFT': { name: 'Microsoft', sector: 'Big Tech', signals: [{ strategy: 'AMQS', signal: 'BUY', date: '2026-06-07' }] },
    'TSLA': { name: 'Tesla', sector: 'EV/AI', signals: [{ strategy: 'AMQS', signal: 'SELL', date: '2026-06-07' }] },
  };
  const result = tickers[q] || { name: q, sector: 'Unknown', signals: [] };
  res.json({ data: { ticker: q, signals: result.signals, name: result.name, sector: result.sector } });
});
