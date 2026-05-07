# AI Super Cycle Quant Strategy — Bundle

> **인공지능 슈퍼 사이클에 올라타는 미국 주식 퀀트 전략**
> 한국어·영어·중국어 3개 언어 LLM 프롬프트 + 추천 포트폴리오 CSV 3종 + Python 스크리너

---

## Bundle 구성

| 파일 | 용도 | 언어 |
| --- | --- | --- |
| `AI Super Cycle Prompt kr.MD` | LLM 프롬프트 (한국어 결과) | 🇰🇷 한국어 |
| `AI Super Cycle Prompt EN.MD` | LLM 프롬프트 (영어 결과, 토큰 효율 최고) | 🇺🇸 English |
| `AI Super Cycle Prompt CN.MD` | LLM 프롬프트 (중문 결과) | 🇨🇳 简体中文 |
| `portfolio_kr.csv` | 추천 10종목 데이터 (한국어 컬럼) | 🇰🇷 |
| `portfolio_en.csv` | 추천 10종목 데이터 (영어 컬럼) | 🇺🇸 |
| `portfolio_cn.csv` | 추천 10종목 데이터 (중문 컬럼) | 🇨🇳 |
| `ai_super_cycle_screener.py` | yfinance 기반 자동 스크리너 | 🌐 다국어 호환 |

---

## 빠른 시작

### 1. LLM 프롬프트 사용 (가장 단순)

원하는 언어의 `.MD` 파일을 열고, 코드 블록 안의 프롬프트를 *전체 복사* → Claude/GPT-5/Gemini/DeepSeek에 붙여넣기. LLM이 즉시 Top 10 분석 리포트 생성.

### 2. CSV 파일 직접 활용

`portfolio_*.csv`는 LLM 프롬프트의 *예상 출력값을 사전 시뮬레이션* 한 자료. 엑셀/Google Sheets로 열어 즉시 확인 가능.

```bash
# CSV 미리보기
head -3 portfolio_en.csv
```

### 3. Python 스크리너 실행 (실시간 데이터 검증)

```bash
# 의존성 설치
pip install yfinance pandas numpy tabulate

# 전체 유니버스 스크리닝 (실시간 yfinance 데이터)
python ai_super_cycle_screener.py

# Layer 1 (반도체) 만 + 점수 80점 이상
python ai_super_cycle_screener.py --layer 1 --min-score 80

# 결과 CSV 파일명 지정
python ai_super_cycle_screener.py --output ai_screen_2026Q2.csv
```

---

## 추천 포트폴리오 요약

### 4-Layer 분산 (10종목 = Layer 1: 4 + Layer 2: 3 + Layer 3: 2 + Layer 4: 1)

| # | 티커 | 회사 | Layer | 점수 | AI 노출 |
| --- | --- | --- | --- | --- | --- |
| 1 | NVDA | NVIDIA | 1 (Foundation) | 95 | 90% |
| 2 | TSM | TSMC | 1 (Foundation) | 92 | 50% |
| 3 | MSFT | Microsoft | 2 (Infra) | 91 | 35% |
| 4 | AVGO | Broadcom | 1 (Foundation) | 90 | 60% |
| 5 | META | Meta Platforms | 2 (Infra) | 89 | 40% |
| 6 | GOOGL | Alphabet | 2 (Infra) | 88 | 30% |
| 7 | ASML | ASML | 1 (Foundation) | 87 | 45% |
| 8 | VRT | Vertiv | 3 (Enablers) | 86 | 70% |
| 9 | ANET | Arista Networks | 3 (Enablers) | 84 | 65% |
| 10 | PLTR | Palantir | 4 (Application) | 78 | 80% |

### 12개월 포트폴리오 기대수익

- **확률 가중 평균**: +18.4% (NASDAQ-100 +13.6% 대비 +4.8%p 알파)
- **추정 베타**: 1.30
- **목표 수익률 분포**: -22%(거품 붕괴 5%) ~ +32%(Capex 가속 30%)

---

## 🔬 점수 체계

| 차원 | 가중치 | 핵심 지표 |
| --- | --- | --- |
| AI 매출 노출도 | **35%** | AI 직접 매출 비중, 데이터센터 매출 성장, RPO 가시성 |
| 자본 효율성 & 모멘텀 | **30%** | ROIC vs WACC, FCF/Capex, EPS 성장률, 매출 가속 |
| 밸류에이션 (GARP) | **20%** | PEG, EV/Sales, Rule of 40, DCF 디스카운트 |
| 모멘텀 & 수급 | **15%** | 52주 신고가, 13F, EPS 추정 상향, 옵션 Skew |

---

## 위험 고지

- 본 분석은 **교육·연구 목적의 가상 시뮬레이션**이며, 실제 투자 권유가 아닙니다
- AI 슈퍼사이클은 닷컴버블(2000) 대비 펀더멘털이 강하지만 **-50% drawdown 가능성** 인지
- LLM 데이터는 **2025년 4월까지**의 정보 기반, **±5% 오차 범위** 명시
- 한국 거주자: 양도소득세 22% + 원천징수 15% 검토 필요
- 미국 외 투자자: 본국 세무 전문가 상담 필수

---

## 시리즈 정보

**시리즈명**: vibe-investing — Awesome Claude Quant Scripts

**연관 sub-strategy**:
- [Dividend Growth Prompt](../Dividend%20growth%20prompt) — 반대 팩터 (배당 성장 + 가치)
- [Long-Term Dividend Investing](../Long-Term%20Dividend%20Investing) — 장기 보유 코드 구현
- [DAT Quant Strategy](../DAT%20quant%20strategy) — 디지털 자산 보유 기업 전략

**저자**: 김호광 (Dennis Kim / HoKwang Kim)
- Independent Researcher, Betalabs Inc. CEO
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

**작성일**: 2026년 5월 2일 v1.0
**라이선스**: MIT (자유 사용, 출처 표기 권장)

---

> *"In the AI super cycle, the picks and shovels matter more than the gold."*
