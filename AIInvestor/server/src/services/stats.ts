// services/stats.ts — Rankings and visit tracking

let visitCount = 0;

export async function getRankings() {
  return {
    top: [
      { ticker: 'NVDA', name: 'NVIDIA', rank: 1, search_count: 340 },
      { ticker: 'TSLA', name: 'Tesla', rank: 2, search_count: 285 },
      { ticker: 'AAPL', name: 'Apple', rank: 3, search_count: 210 },
      { ticker: 'MU', name: 'Micron', rank: 4, search_count: 178 },
      { ticker: 'AMD', name: 'AMD', rank: 5, search_count: 152 },
    ],
  };
}

export async function trackVisit() {
  visitCount++;
  return { dau: visitCount, total_au: visitCount + 1200 };
}
