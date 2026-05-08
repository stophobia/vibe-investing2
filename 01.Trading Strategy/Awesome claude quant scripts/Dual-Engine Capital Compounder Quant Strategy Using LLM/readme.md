# Dual-Engine Capital Compounder Quant Strategy — Bundle

> **미국 금융 + 리테일 배당주 동시 발굴 퀀트 시스템**
> 한국어·영어·중국어 3개 언어 LLM 프롬프트 + 추천 포트폴리오 CSV 3종 + Python 스크리너 (TCRY 계산 + 사이클 방어력 점수 포함)

---

## Bundle 구성

| 파일 | 용도 | 언어 |
| --- | --- | --- |
| `Dual Engine Compounder Prompt kr.MD` | LLM 프롬프트 (한국어 결과) | 🇰🇷 한국어 |
| `Dual Engine Compounder Prompt EN.MD` | LLM 프롬프트 (영어 결과, 토큰 효율 최고) | 🇺🇸 English |
| `Dual Engine Compounder Prompt CN.MD` | LLM 프롬프트 (중문 결과) | 🇨🇳 简体中文 |
| `portfolio_kr.csv` | 추천 10종목 데이터 (한국어 컬럼) | 🇰🇷 |
| `portfolio_en.csv` | 추천 10종목 데이터 (영어 컬럼) | 🇺🇸 |
| `portfolio_cn.csv` | 추천 10종목 데이터 (중문 컬럼) | 🇨🇳 |
| `dual_engine_screener.py` | yfinance 기반 자동 스크리너 (TCRY + 사이클 방어력) | 🌐 다국어 호환 |

---

## 🚀 빠른 시작

### 1. LLM 프롬프트 사용 (가장 단순)

원하는 언어의 `.MD` 파일을 열고, 코드 블록 안의 프롬프트를 *전체 복사* → Claude/GPT-5/Gemini/DeepSeek에 붙여넣기.

### 2. CSV 파일 직접 활용

```bash
head -3 portfolio_en.csv
```

### 3. Python 스크리너 실행 (실시간 데이터)

```bash
pip install yfinance pandas numpy tabulate

# 전체 유니버스 스크리닝 (37개 티커)
python dual_engine_screener.py

# Financial Engine만 + 점수 80점 이상
python dual_engine_screener.py --engine financial --min-score 80

# Retail Engine만 + 결과 CSV 파일명 지정
python dual_engine_screener.py --engine retail --output retail_2026Q2.csv
```

---

## 추천 포트폴리오 요약

### 🏦 Financial Engine (5종)

| # | 티커 | 회사 | Sub-segment | 점수 | 배당 | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | V | Visa | Card Network | **90** | 0.65% | 4.7% |
| 2 | JPM | JPMorgan | Megabank | **88** | 2.05% | 6.5% |
| 3 | BLK | BlackRock | Asset Mgmt | **86** | 1.90% | 4.8% |
| 4 | AXP | American Express | Premium Card | **85** | 1.05% | 5.1% |
| 5 | CB | Chubb | Insurance | **82** | 1.25% | 4.0% |

### 🛒 Retail Engine (5종)

| # | 티커 | 회사 | Sub-segment | 점수 | 배당 | TCRY |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | HD | Home Depot | Home Improvement | **87** | 2.17% | 6.2% |
| 7 | TJX | TJX Companies | Off-Price | **86** | 1.15% | 4.7% |
| 8 | WMT | Walmart | Mass Retail | **84** | 0.87% | 2.9% |
| 9 | MCD | McDonald's | QSR | **83** | 2.28% | 5.4% |
| 10 | TGT | Target | Discount | **80** | 2.89% | 6.5% |

### 12개월 포트폴리오 기대수익

- **확률 가중 평균**: +12.6% (S&P 500 +9.5% 대비 +3.1%p 알파)
- **추정 베타**: 0.92 (시장 베타 1.0 대비 약간 방어적)
- **방어력 우위**: 침체 시나리오에서 S&P 500 (-22%) 대비 -15% (7%p 우위)

---

## 🔬 점수 체계 (이전 시리즈와의 차별화)

| 차원 | Dual-Engine | AI Super Cycle | Dividend Growth |
| --- | --- | --- | --- |
| 1차 가중치 | **수익품질·자본환원 (35%)** | AI 매출 노출 (35%) | 배당 지속성 (40%) |
| 2차 가중치 | **배당 성장 모멘텀 (30%)** | 자본 효율·모멘텀 (30%) | 배당 성장 (35%) |
| 3차 가중치 | **밸류에이션 (20%)** | GARP 밸류에이션 (20%) | 밸류에이션 (25%) |
| 4차 가중치 | **사이클 방어력 (15%)** | 모멘텀·수급 (15%) | — |
| 핵심 지표 | **TCRY (배당+자사주 합산)** | AI Revenue Exposure | Payout Ratio |

> **TCRY (Total Capital Return Yield)** 가 이 시스템의 핵심 신호입니다. 단순 배당수익률은 환원의 절반만 보여주고, 자사주 매입 비중까지 합산해야 *진정한 자본 환원의 복리 효과* 가 측정됩니다.

---

## 위험 고지

- 본 분석은 **교육·연구 목적의 가상 시뮬레이션**이며, 실제 투자 권유가 아닙니다
- **2008 GFC 당시 BAC 배당 -90%, C 배당 -97% 컷** — Dividend Aristocrat 자격 박탈 사례 존재
- **2020 팬데믹 당시 외식·여행·럭셔리 리테일 -30~50% 매출 충격** — sub-segment 차별화 필수
- **카드 네트워크 반독점 + 스테이블코인 침투** 장기 리스크 모니터링 필요
- 한국 거주자: 양도소득세 22% + 원천징수 15% 검토 필요

---

## 시리즈 정보

**시리즈명**: vibe-investing — Awesome Claude Quant Scripts

**시리즈 진화**:
1. [Dividend Growth Prompt](../Dividend%20growth%20prompt) — 6-섹터 배당 성장 (1세대)
2. [AI Super Cycle Prompt](../AI%20Super%20Cycle%20Prompt) — 4-Layer AI 가치사슬 (2세대)
3. **Dual-Engine Compounder** — 2-Engine 자본 환원 (3세대, 본 번들)

**저자**: 김호광 (Dennis Kim / HoKwang Kim)
- Independent Researcher, Betalabs Inc. CEO
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

**작성일**: 2026년 5월 2일 v1.0
**라이선스**: MIT (자유 사용, 출처 표기 권장)

---

> *"Compounding is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."* — Albert Einstein
