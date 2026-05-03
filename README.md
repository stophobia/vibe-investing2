# vibe-investing

AI 기반 시장 분석 칼럼, 퀀트 트레이딩 전략, AI 투자 도구 큐레이션을 모아둔 레포입니다.

다루는 시장: 미국 NASDAQ / S&P500, 가상화폐, 유럽 명품 섹터, 크립토-주식 상관관계 그리고 인간의 욕망에 대해 다룹니다.

- 작성자: 김호광 (Dennis Kim)
- 라이선스: MIT
- 업데이트 주기: 주 1-2회
- English README: [README_EN.md](Readme%20en.MD)

---

## 투자 철학

1. **2017년부터 블록체인 시장에서 일하며 한국과 중국의 가교 역할을 해왔습니다.** 시장의 버블과 탐욕을 겸험하며 투자에 대한 인사이트과 진리를 찾고 있습니다. 현자의 돌이 있듯 인공지능을 통한 경제학 모델이 언젠가는 만들어질 것이라 믿습니다.

2. **AI는 도구입니다 — 엑셀처럼.** LLM은 만능이 아니며 오라클이 될 수 없습니다. 같은 데이터와 LLM을 이용하더라도 모델을 읽는 인간의 통찰력이 더 중요합니다.

3. **모델의 지능이 곧 트레이딩 지능은 아닙니다.** Alpha Arena Season 1에서 GPT-5는 -75%, DeepSeek V3.1은 +46%였습니다. 똑똑한 모델이 돈을 버는 것이 아닙니다.

4. **백테스트는 가설일 뿐입니다.** 실거래에서 살아남는 것이 검증입니다. 이 레포의 모든 백테스트 결과는 한계가 함께 명시되어 있습니다.

5. **데이터를 공개합니다.** 14개 이상의 CSV로 누구나 검증할 수 있게 합니다. 검증이 되지 않는 닫힌 알파는 알파가 아닙니다.

6. **돈키호테처럼 복잡한 레포입니다.** 하지만 뒤지는 재미와 살펴보는 재미가 있으며 다양한 저의 투자 관심사와 호기심이 가득한 공간입니다.
---

## 빠른 시작

| 목적 | 추천 경로 |
|---|---|
| 시장 통찰을 얻고 싶음 | [칼럼](#칼럼) — LTCM 또는 After Market Close부터 |
| 트레이딩 전략을 둘러보고 싶음 | [트레이딩 전략](#트레이딩-전략) |
| AI 투자 도구를 둘러보고 싶음 | [큐레이션](AWESOME.md) |
| 코드를 바로 실행하고 싶음 | [도구](#도구) — Nasdaq-BTC Coupling Bot |
| 데이터셋만 받아가고 싶음 | [데이터셋](#데이터셋) |
| 연구·논문을 보고 싶음 | [연구 / 논문](#연구--논문) |

---

## 최근 업데이트

| 일자 | 항목 | 종류 |
|---|---|---|
| 2026-05 | Awesome claude quant scripts (4종 전략) | 트레이딩 전략 |
| 2026-05-01 | Awesome AI Quant Prompt 평가 | 큐레이션 |
| 2026-05-01 | Awesome Vibe Trading Bot | 큐레이션 |
| 2026-04-17 | Nasdaq-BTC Coupling Bot v1 | 도구 |
| 2026-04 | 가상화폐와 나스닥은 얼마나 동기화되고 있을까 | 칼럼 |
| 2026-04 | 명품은 언제 사야 하는가 | 칼럼 |
| 2026-04 | DAT 기업의 mNAV 아비트리지 전략 | 칼럼 |
| 2026-04 | 시장은 닫혔을 때 열리는가 | 칼럼 |

---

## 칼럼

시장의 거시 흐름과 산업 변화를 분석한 7편의 칼럼입니다. 칼럼 전체 인덱스는 [02.Investment Idea Column/README.md](02.Investment%20Idea%20Column/README.md) 참조.

| # | 제목 | 주제 | 데이터 |
|---|---|---|---|
| 1 | [LTCM의 사례로 배우는 모델을 읽는 힘](Vibe%20Investing%20Risk%20Management.MD) | 1998년 LTCM 사태 + AI 바이브 투자 리스크 | - |
| 2 | [Microsoft의 Fintool 인수](Microsoft%20fintool%20acquisition%20column.MD) | 370억 달러 금융 데이터 시장 진입 분석 | - |
| 3 | [보이지 않는 손인가, 계획된 사기인가](Crypto%20perp%20manipulation%20column.MD) | 가상화폐 선물 pump-dump 패턴 수학적 검토 | - |
| 4 | [시장은 닫혔을 때 열리는가](AfterMarketClose/After_Market_Close_Column.md) | 미국 상장사 91.2% AMC 공시 집중 현상 | 34건 |
| 5 | [DAT 기업의 mNAV 아비트리지 전략](mNAV(Market-to-Net-Asset-Value)%20arbitrage/Dat%20mnav%20arbitrage%20strategy.MD) | MSTR, BMNR 등 디지털 자산 보유 기업 분석 | CSV 3종 |
| 6 | [명품은 언제 사야 하는가](01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md) | LVMH, Hermès, Kering 3단계 포트폴리오 | CSV 4종 |
| 7 | [가상화폐와 나스닥은 얼마나 동기화되고 있을까](01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/Nasdaq%20crypto%20coupling%20strategy.MD) | BTC-QQQ 6년 상관관계 + 6 regime 분류 | CSV 4종 |

권장 읽기 순서: 1 → 4 → 6 → 7 (위험 관리 → 시장 구조 → 섹터 분석 → 정량 분석)

---

## 트레이딩 전략

전체 인덱스는 [01.Trading Strategy/README.md](01.Trading%20Strategy/README.md) 참조.

| 카테고리 | 설명 |
|---|---|
| [Awesome claude quant scripts](01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/) | Claude를 활용한 4종 트레이딩 전략 (AI 공급망 베이지안 / DAT / 하락주 / 장기 배당) |
| [Luxury investment strategy](01.Trading%20Strategy/Luxury%20investment%20strategy/) | LVMH, Hermès, Kering 명품 섹터 3단계 포트폴리오 |
| [Investment Strategy Based on Bitcoin and Nasdaq Coupling](01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) | BTC-QQQ 상관관계 기반 6 regime 트레이딩 |

---

## 도구

직접 개발한 3개의 AI 트레이딩 도구입니다.

| # | 이름 | 설명 | 검증 |
|---|---|---|---|
| 1 | [Harness Quant v2](Harness%20quant%20v2%20readme%20.MD) | LLM 기반 NASDAQ/S&P500 분석. 6개 시나리오 + 백테스트 + MCP + 멀티 에이전트 토론 | - |
| 2 | [Earnings Momentum Agent](Harness%20quantv2/Earnings%20momentum%20agent%20readme%20.MD) | 어닝 서프라이즈 Top 30 추천 파이프라인 | 24개월 백테스트 hit rate 83.3% (백테스트 기준) |
| 3 | [Nasdaq-BTC Coupling Bot](01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) | BTC-QQQ 30일 rolling correlation 실시간 추적 + regime 분류 + 신호 생성 | Python 547 lines |

각 도구의 README에 사용법, 환경 변수, 알려진 한계를 정리해두었습니다. 실거래 적용 전 반드시 한계 섹션을 먼저 읽으세요.

---

## 연구 / 논문

데이터·통계 기반의 정량 분석 자료입니다. 모든 분석은 공개 CSV로 재현 가능합니다.

| 주제 | 위치 | 데이터 규모 |
|---|---|---|
| AI 공급망 베이지안 분석 | [Awesome claude quant scripts/AI supply chain bayesian analysis/](01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/) | 베이지안 추론 모델 |
| AMC 공시 타이밍 실증 분석 | [AfterMarketClose/](AfterMarketClose/) | 34건 8-K 공시 + 다음날 수익률 |
| DAT mNAV 사이클 분석 | [mNAV(...) arbitrage/](mNAV(Market-to-Net-Asset-Value)%20arbitrage/) | 12 사이클 + 15개 기업 |
| 명품 섹터 백테스트 | [Luxury investment strategy/](01.Trading%20Strategy/Luxury%20investment%20strategy/) | 225건 백테스트 + 3가지 전략 비교 |
| BTC-나스닥 커플링 분석 | [Investment Strategy ... Coupling/](01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) | 26 분기 + 31 이벤트 + 6 regime |
| 어닝 모멘텀 백테스트 | [Harness quantv2/](Harness%20quantv2/) | 24개월 768 의사결정 |

---

## 데이터셋

연구·검증 목적으로 공개한 CSV 데이터셋입니다. Python pandas로 즉시 분석 가능합니다.

| 카테고리 | 파일 | 설명 |
|---|---|---|
| 공시 타이밍 | `disclosure_timing_cases.csv` | 34건 AMC 공시 + 다음날 수익률 |
| DAT 기업 | `dat_companies_2026.csv` | 15개 DAT 기업 현황 |
| DAT 기업 | `dat_vs_benchmark_performance.csv` | 반기별 수익률 비교 |
| DAT 기업 | `mnav_cycles_arbitrage_signals.csv` | mNAV 사이클 + 매매 신호 |
| 명품 섹터 | `luxury_companies_etfs_2026.csv` | 13개 명품 기업/ETF |
| 명품 섹터 | `luxury_performance_2020_2026.csv` | 반기별 수익률 |
| 명품 섹터 | `luxury_backtest_3strategies.csv` | 225건 백테스트 로그 |
| 명품 섹터 | `luxury_portfolio_by_risk.csv` | 위험단계별 포트폴리오 |
| 커플링 | `btc_qqq_correlation_2020_2026.csv` | 26 분기 상관계수 |
| 커플링 | `btc_nasdaq_event_log.csv` | 31개 이벤트 영향 |
| 커플링 | `intraday_coupling_samples.csv` | 4개 세션 인트라데이 |
| 커플링 | `correlation_regimes_signals.csv` | 6 regime 분류 |
| 어닝 모멘텀 | `backtest_log_24months.csv` | 768건 의사결정 |

각 CSV는 해당 칼럼·전략 폴더 안에 위치합니다.

---

## 큐레이션

AI 투자 도구를 카테고리별로 평가한 어썸 시리즈는 별도 파일로 정리했습니다.

→ [AWESOME.md](AWESOME.md)

다루는 카테고리:
- Stocks & Equities (NASDAQ/S&P500 AI 도구 30+)
- Crypto & DeFi (LLM 트레이딩 봇 + 벤치마크)
- AI Quant Prompt
- Vibe Trading Bot

---

## 디렉토리 구조

```
vibe-investing/
├── README.md                              한국어 메인 (이 파일)
├── README_EN.md                           English README
├── AWESOME.md                             큐레이션 인덱스
│
├── 01.Trading Strategy/                   트레이딩 전략 모음
│   ├── README.md
│   ├── Awesome claude quant scripts/      Claude 기반 4종 전략 + Sample
│   ├── Luxury investment strategy/        명품 섹터 전략 + CSV 4종
│   └── Investment Strategy Based on Bitcoin and Nasdaq Coupling/
│
├── 02.Investment Idea Column/             칼럼 인덱스
│   └── README.md
│
├── AfterMarketClose/                      AMC 공시 칼럼 + CSV
├── mNAV(...)/                             DAT mNAV 칼럼 + CSV 3종
├── Harness quantv2/                       Earnings Momentum Agent
│
├── Vibe Investing Risk Management.MD      LTCM 칼럼
├── Microsoft fintool acquisition column.MD Fintool 칼럼
├── Crypto perp manipulation column.MD     Crypto perp 칼럼
├── Harness quant v2 readme .MD            Harness Quant v2 도구
│
├── Awesome vibe invest.MD                 큐레이션 1
├── Awesome vibe invest crypto.MD          큐레이션 2
├── Awesome AI Quant Prompt ...kr.MD       큐레이션 3
└── Awesome Vibe Trading Bot.MD            큐레이션 4
```

---

## About

**김호광 (Dennis Kim)**

Cyworld CEO, BetaLabs 대표, Web3 Investor

2017년부터 블록체인 시장에 참여해왔으며, 한국과 중국 블록체인 생태계의 가교 역할을 해왔습니다. 한 시장에서 본 패턴을 다른 시장에서 검증하는 작업이 본 레포의 분석 기조에 녹아 있습니다.

- 이메일: gameworker@gmail.com
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)

---

## Disclaimer

이 레포의 모든 콘텐츠는 연구·교육 목적입니다.

- 어떤 도구도 수익을 보장하지 않습니다
- 백테스트 결과는 이상적 시나리오 기반이며 실거래 수익률과 다릅니다 (slippage, 수수료, 세금, 지연)
- 본인 자산 운용은 가능하나 타인 자금 운용은 라이선스가 필요합니다
- 시장 구조 분석 칼럼은 통계적·학술적 논평이며 특정 주체를 지목하지 않습니다
- 공매도, 곱버스 ETF, 레버리지 투자는 개인에게 치명적일 수 있습니다
- 투자 결과와 법적 리스크에 대한 책임은 사용자에게 있습니다

자세한 위험 고지는 각 칼럼·도구의 "알려진 리스크" 섹션을 참조하세요.

---

## License

MIT License. 자유롭게 사용·수정·배포 가능합니다.

칼럼 인용 시 "김호광 (Dennis Kim) / vibe-investing" 출처 명기를 부탁드립니다.

---

## 기여하기

- 이슈 또는 PR 환영합니다
- 평가 반박, 누락 레포 제보, 백테스트 결과 공유 모두 환영
- 영문 번역 contribution 환영
