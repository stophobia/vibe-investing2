# Data Dictionary

This document describes all CSV files in the `data/` directory.

---

## 1. `listed_tokens.csv`

Sample of N=21 tokens used in Section 6 empirical analysis (Megadrop, HODLer, Launchpool, Direct categories, including Hyperliquid HYPE).

| Column | Type | Description |
|--------|------|-------------|
| `token_symbol` | string | Token ticker symbol (e.g., BB, LISTA, SPK, HYPE) |
| `token_name` | string | Full project name (e.g., BounceBit, Lista DAO) |
| `listing_date` | date (YYYY-MM-DD) | Date of Binance spot listing |
| `airdrop_program` | string | Distribution program: Megadrop, HODLer, Launchpool, or Direct |
| `distribution_ratio` | float (0–1) | Proportion of total token supply distributed via airdrop |
| `total_supply` | integer | Total token supply at listing |
| `airdrop_amount` | integer | Number of tokens distributed in airdrop |
| `listing_price_usd` | float | Token price at listing in USD |
| `fdv_at_listing_usd` | float | Fully Diluted Valuation at listing (= listing_price × total_supply) |
| `circulating_at_listing_pct` | float | Percentage of supply circulating at listing |
| `token_category` | string | DeFi / GameFi / Memecoin / Infrastructure / RWA / etc. |
| `price_24h_pct` | float | 24-hour price change after listing (%) |
| `price_7d_pct` | float | 7-day price change after listing (%) |
| `price_30d_pct` | float | 30-day price change after listing (%) |
| `price_90d_pct` | float | 90-day price change after listing (%) |
| `price_180d_pct` | float | 180-day price change after listing (%) |
| `btc_relative_30d` | float | T+30 BTC-relative abnormal return (%) |
| `verified_source` | string | Primary source for verification (e.g., Binance_official, CoinGecko, tokenomist.ai) |

**Notes**:
- `verified_source` distinguishes [primary verified] vs [estimated] data classification described in Section 6.2.1
- `btc_relative_30d` will be expanded to full daily BTC-relative AR series in subsequent versions
- Initial sample errors (LISTA distribution_ratio 5%->10%, SPK listing_price $0.177->$0.0745) corrected as of v1.0

---

## 2. `btc_eth_bnb_quarterly.csv`

Quarterly closing prices and on-chain metrics for BTC, ETH, BNB used in Section 5 (Market Cycle Control).

| Column | Type | Description |
|--------|------|-------------|
| `period` | string | Quarter identifier (e.g., 2024Q1, 2024Q2) |
| `date` | date | Quarter-end date |
| `btc_close_usd` | float | BTC closing price (USD) at quarter end |
| `eth_close_usd` | float | ETH closing price (USD) at quarter end |
| `bnb_close_usd` | float | BNB closing price (USD) at quarter end |
| `btc_qoq_pct` | float | BTC Quarter-over-Quarter return (%) |
| `eth_qoq_pct` | float | ETH QoQ return (%) |
| `bnb_qoq_pct` | float | BNB QoQ return (%) |
| `bnb_chain_tvl_usd` | float | BNB Chain Total Value Locked (USD) |
| `bnb_chain_tx_daily` | integer | BNB Chain daily average transactions |
| `bnb_chain_active_wallets` | integer | BNB Chain daily average active wallets |
| `btc_dominance_pct` | float | BTC market dominance (% of total crypto market cap) |
| `verified_source` | string | Source: CoinGecko, Messari, CoinLaw, Industry_Report |

**Sample size**: N=9 quarters (2024 Q1 through 2026 Q1)
**Limitations**: Quarterly resolution is too coarse for full Granger causality testing (Limitation 6). Subsequent versions will expand to daily resolution.

---

## 3. `bnb_chain_metrics.csv`

BNB Chain macro-activity metrics for 2025 Q1–Q3 used in Section 7 (Decoupling Pattern).

| Column | Type | Description |
|--------|------|-------------|
| `quarter` | string | Quarter identifier |
| `fees_usd` | float | Total fees collected in USD |
| `fees_qoq_pct` | float | Fees QoQ change (%) |
| `daily_tx_avg` | integer | Daily average transactions |
| `daily_tx_qoq_pct` | float | Daily transactions QoQ change (%) |
| `daily_active_wallets` | integer | Daily average active wallets |
| `daily_active_qoq_pct` | float | Active wallets QoQ change (%) |
| `defi_tvl_usd` | float | DeFi Total Value Locked in USD |
| `defi_tvl_qoq_pct` | float | TVL QoQ change (%) |
| `gas_price_gwei` | float | Average gas price in Gwei |
| `interpretation` | string | Period-specific qualitative interpretation |
| `source` | string | Primary source (Messari "State of BNB" reports) |

**Key observation**: BNB Chain trading volume +171.4%, TVL +47.2%, active wallets +91.6% (Q1->Q3 2025) while Megadrop category market cap declined ~75% — the decoupling pattern.

---

## 4. `correlation_matrix.csv`

Pre-computed correlation matrices and statistical significance tests for Section 5.

| Column | Type | Description |
|--------|------|-------------|
| `analysis_type` | string | pearson_price / spearman_price / pearson_returns / spearman_returns |
| `pair` | string | Asset pair (e.g., BTC-ETH, BTC-BNB, ETH-BNB) |
| `correlation` | float | Correlation coefficient |
| `p_value` | float or NULL | Two-tailed test p-value (NULL = not pre-computed) |
| `significance` | string | Significance level: ***/**/*/n.s. or descriptive |
| `sample_size` | integer | N (= 9 for quarterly data) |
| `interpretation` | string | Qualitative interpretation of the result |

---

## Data Source Verification Notes

All data is collected from publicly available sources as of 2026-04-30:

- **Token data**: Binance official announcements (binance.com/en/support/announcement), CoinGecko, CoinMarketCap, tokenomist.ai
- **Quarterly prices**: CoinGecko Q3 2025 Industry Report, Messari quarterly reports
- **BNB Chain metrics**: Messari "State of BNB Q1/Q2/Q3 2025" reports
- **Distribution program details**: Binance Square, Binance Academy

**Data freshness**: All data verified as of 2026-04-30. Subsequent versions will rebuild from CoinGecko/Binance API for daily-level analysis.

---

## Reproducibility Note

To reproduce all analysis from these data files:

```bash
# Install dependencies
pip install pandas numpy scipy matplotlib

# Run analyses (from scripts/ directory)
python correlation_analysis.py
python robustness_analysis.py
python integrated_analysis_v10.py
python pair_trading_backtest.py

# Generate all figures
for f in generate_figure*.py; do python "$f"; done
```

All scripts use `../data/` and `../figures/` relative paths from the `scripts/` directory.
