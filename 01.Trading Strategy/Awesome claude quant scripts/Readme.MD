# Awesome Claude Quant Scripts

Claude를 활용해 만든 트레이딩 전략 스크립트 모음입니다.

→ [상위 폴더 README](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/README.md)
→ [메인 레포 README](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)

---

## 개요

이 폴더는 5종의 트레이딩 전략과 1개의 Sample 템플릿, 그리고 전체 전략 맵 (`trading map.png`)을 담고 있습니다.

전체 개요는 [Awesome claude quant scripts.MD](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD)를 참조하세요.

---

## 수록 전략

| # | 전략 | 폴더 | 분류 | 형태 |
| --- | --- | --- | --- | --- |
| 1 | [AI supply chain bayesian analysis](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/AI%20supply%20chain%20bayesian%20analysis) | AI 공급망 베이지안 분석 | 연구 / 정량 분석 | Python 코드 |
| 2 | [DAT quant strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/DAT%20quant%20strategy) | DAT 기업 정량 전략 | 트레이딩 전략 | Python 코드 |
| 3 | [Declining Stock Quant Script Using LLM](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Declining%20Stock%20Quant%20Script%20Using%20LLM) | LLM 기반 하락주 스크립트 | 트레이딩 전략 | LLM 프롬프트 |
| 4 | [Long-Term Dividend Investing](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Long-Term%20Dividend%20Investing) | 장기 배당 투자 | 트레이딩 전략 | Python 코드 |
| 5 | [Dividend growth prompt](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Dividend%20growth%20prompt) | 배당 성장 LLM 프롬프트 (한/영 + 3사 LLM 비교) | 트레이딩 전략 | LLM 프롬프트 + 비교 분석 |
| - | [Sample](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Sample) | 새 전략 시작 시 사용할 템플릿 | Template | - |

---

## 전략별 설명

### 1. AI supply chain bayesian analysis

AI 산업의 공급망 위험을 베이지안 추론으로 분석한 연구 자료. 반도체, GPU, 클라우드, 데이터 등 AI 공급망 핵심 노드의 의존성과 단일 실패점(SPOF) 위험을 정량화합니다.

활용:

* 엔비디아·TSMC·ASML 같은 단일 노드 의존도가 높은 기업의 risk-adjusted 평가
* AI 섹터 포트폴리오의 공급망 집중도 측정
* 지정학적 충격 시 가장 먼저 영향받을 종목 식별

### 2. DAT quant strategy

DAT (Digital Asset Treasury) 기업, 즉 비트코인·이더리움·솔라나를 재무제표에 핵심 자산으로 보유하는 기업의 정량 트레이딩 전략입니다.

연관:

* [DAT mNAV 아비트리지 칼럼](https://github.com/gameworkerkim/vibe-investing/blob/main/mNAV(Market-to-Net-Asset-Value)%20arbitrage)에서 이론 배경 확인
* MSTR, BMNR, SBET 등 15개 기업 대상

### 3. Declining Stock Quant Script Using LLM

급락 중인 종목 가운데 반등 가능성이 있는 종목을 LLM이 선별하는 스크립트. 단순 모멘텀 역발상이 아니라 펀더멘털과 기술적 지표를 함께 검토합니다.

연관:

* [Earnings Momentum Agent](https://github.com/gameworkerkim/vibe-investing/blob/main/Harness%20quantv2)와 보완적 — Earnings Momentum이 "저점 + 실적 반등"을 잡는 반면, 본 스크립트는 "급락 + 회복 가능성"을 분석

### 4. Long-Term Dividend Investing

장기 배당 투자를 위한 종목 선별 스크립트. 단순 배당수익률이 아니라 배당 성장성, 지속 가능성, 페이아웃 비율, 재무 건전성을 종합 평가합니다.

활용:

* 은퇴 자금 운용
* 인컴 포트폴리오 구성
* 배당 귀족주 (Dividend Aristocrats) 후보 발굴

### 5. Dividend growth prompt — 배당 성장 LLM 프롬프트 (2026년 5월 신규)

S&P 500 + NASDAQ-100 종목에서 *배당 성장 + 가치* 를 동시에 충족하는 Top 10 종목 발굴 + 배당 ETF 3종 추천 + 동일가중 포트폴리오 시뮬레이션을 *LLM 한 번 호출* 로 자동 생성하는 프롬프트.

**핵심 차별점**:

* **한국어판 + 영문판 양쪽 제공** — 영문 프롬프트가 한국어 대비 *약 30% 토큰 절감* 효과
* **3사 LLM 결과 비교 분석 포함** — Claude, Gemini, DeepSeek 의 실제 출력 결과를 *비교 표 + 상이점 정리* 로 제공
* **듀레이션-프리미엄 모델** — 배당 지속가능성 (40%) + 배당 성장 모멘텀 (35%) + 밸류에이션 (25%) 의 3차원 통합 평가
* **6대 섹터 분산** — 필수소비재, 헬스케어, 금융, 테크, 에너지, 산업재
* **3개 출력 파트** — Part 1 (Top 10 종목) + Part 2 (배당 ETF 3종) + Part 3 (동일가중 포트폴리오 + Sharpe + MDD)

**사용 방법**: LLM (Claude, GPT-5, Gemini, DeepSeek 등) 에 프롬프트 *복사 후 붙여넣기* — 즉시 결과 생성

연관:

* **Long-Term Dividend Investing (4번)** 의 *LLM 프롬프트 보완판* — 4번이 *Python 코드 구현* 이라면, 5번은 *프롬프트 엔지니어링 형태* 로 *코드 없이* 동일 분석 가능
* **Declining Stock Quant Script Using LLM (3번)** 의 *반대 전략* — 3번은 *하락 종목 + 인버스 ETF*, 5번은 *상승 + 배당 성장*

### Sample

새 전략을 만들 때 사용할 템플릿 폴더입니다. 표준 구조 (README, 스크립트, 데이터, 백테스트, 한계)를 따릅니다.

→ [Sample Readme.MD](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Sample%20Readme.MD) 참조

---

## 코드 vs 프롬프트 형태 분류

본 폴더의 5종 전략은 *Python 코드* 와 *LLM 프롬프트* 두 가지 형태로 나뉩니다:

| 형태 | 전략 | 장점 | 단점 |
| --- | --- | --- | --- |
| **Python 코드** | 1, 2, 4 | 결정적 출력, 백테스트 가능, 재현성 높음 | 데이터 수집 필요, 코드 환경 구축 필요 |
| **LLM 프롬프트** | 3, 5 | 즉시 사용 가능, 데이터 수집 자동화, 정성적 분석 통합 | 비결정적 출력, 토큰 비용, hallucination 위험 |

*권장 워크플로*:

1. **LLM 프롬프트로 시작** (3번 또는 5번) — 시장 큰 그림 파악 + Top 후보 종목 발굴
2. **Python 코드로 검증** (1, 2, 4번) — 정량 백테스트 + 재현성 확보
3. **두 결과를 교차 검증** — LLM 의 정성 분석 + Python 의 정량 검증 결합

---

## 전체 맵

`trading map.png` — 본 폴더의 5종 전략 + Sample이 어떤 시장 상황에 적합한지 시각화한 맵.

---

## 사용 권장 순서

1. [Awesome claude quant scripts.MD](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Awesome%20claude%20quant%20scripts.MD)에서 전체 개요 읽기
2. 본인 관심 영역에 맞는 전략 폴더로 이동
3. 해당 전략의 README와 한계 섹션 읽기
4. **LLM 프롬프트 형태 (3, 5번)**: 즉시 LLM 에 복사 + 결과 검토
5. **Python 코드 형태 (1, 2, 4번)**: 백테스트 데이터 재현 + 페이퍼 트레이딩 검증
6. 실거래 고려 전 *독립 데이터 소스* (Bloomberg, FactSet, SeekingAlpha) 로 *교차 검증*

---

## Disclaimer

모든 스크립트는 연구·교육 목적입니다. 자세한 내용은 [메인 README의 Disclaimer](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md#disclaimer) 참조.

**LLM 프롬프트 형태 (3, 5번) 사용 시 추가 위험 고지**:

* LLM 의 데이터는 *학습 cutoff 시점까지의 정보* 기반이며, *실시간 가격/배당 데이터가 아닙니다*
* 동일 프롬프트라도 *LLM 모델별로 다른 결과* 출력 가능 (5번 README 의 *3사 비교 분석* 참조)
* *Hallucination 위험* — LLM 이 *존재하지 않는 종목* 또는 *잘못된 재무 데이터* 보고 가능
* *비결정적 출력* — temperature/seed 제어가 어려워 *동일 입력에 다른 출력* 가능
* 반드시 *독립 데이터 소스 교차 검증* 후 실거래 고려
