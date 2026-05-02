# Awesome Claude Quant Scripts

Claude를 활용해 만든 트레이딩 전략 스크립트 모음입니다.

→ [상위 폴더 README](../README.md)
→ [메인 레포 README](../../README.md)

---

## 개요

이 폴더는 4종의 트레이딩 전략과 1개의 Sample 템플릿, 그리고 전체 전략 맵 (`trading map.png`)을 담고 있습니다.

전체 개요는 [Awesome claude quant scripts.MD](Awesome%20claude%20quant%20scripts.MD)를 참조하세요.

---

## 수록 전략

| # | 전략 | 폴더 | 분류 |
|---|---|---|---|
| 1 | [AI supply chain bayesian analysis](AI%20supply%20chain%20bayesian%20analysis/) | AI 공급망 베이지안 분석 | 연구 / 정량 분석 |
| 2 | [DAT quant strategy](DAT%20quant%20strategy/) | DAT 기업 정량 전략 | 트레이딩 전략 |
| 3 | [Declining Stock Quant Script Using LLM](Declining%20Stock%20Quant%20Script%20Using%20LLM/) | LLM 기반 하락주 스크립트 | 트레이딩 전략 |
| 4 | [Long-Term Dividend Investing](Long-Term%20Dividend%20Investing/) | 장기 배당 투자 | 트레이딩 전략 |
| - | [Sample](Sample/) | 새 전략 시작 시 사용할 템플릿 | Template |

---

## 전략별 설명

### 1. AI supply chain bayesian analysis

AI 산업의 공급망 위험을 베이지안 추론으로 분석한 연구 자료. 반도체, GPU, 클라우드, 데이터 등 AI 공급망 핵심 노드의 의존성과 단일 실패점(SPOF) 위험을 정량화합니다.

활용:
- 엔비디아·TSMC·ASML 같은 단일 노드 의존도가 높은 기업의 risk-adjusted 평가
- AI 섹터 포트폴리오의 공급망 집중도 측정
- 지정학적 충격 시 가장 먼저 영향받을 종목 식별

### 2. DAT quant strategy

DAT (Digital Asset Treasury) 기업, 즉 비트코인·이더리움·솔라나를 재무제표에 핵심 자산으로 보유하는 기업의 정량 트레이딩 전략입니다.

연관:
- [DAT mNAV 아비트리지 칼럼](../../mNAV(Market-to-Net-Asset-Value)%20arbitrage/)에서 이론 배경 확인
- MSTR, BMNR, SBET 등 15개 기업 대상

### 3. Declining Stock Quant Script Using LLM

급락 중인 종목 가운데 반등 가능성이 있는 종목을 LLM이 선별하는 스크립트. 단순 모멘텀 역발상이 아니라 펀더멘털과 기술적 지표를 함께 검토합니다.

연관:
- [Earnings Momentum Agent](../../Harness%20quantv2/)와 보완적 — Earnings Momentum이 "저점 + 실적 반등"을 잡는 반면, 본 스크립트는 "급락 + 회복 가능성"을 분석

### 4. Long-Term Dividend Investing

장기 배당 투자를 위한 종목 선별 스크립트. 단순 배당수익률이 아니라 배당 성장성, 지속 가능성, 페이아웃 비율, 재무 건전성을 종합 평가합니다.

활용:
- 은퇴 자금 운용
- 인컴 포트폴리오 구성
- 배당 귀족주 (Dividend Aristocrats) 후보 발굴

### Sample

새 전략을 만들 때 사용할 템플릿 폴더입니다. 표준 구조 (README, 스크립트, 데이터, 백테스트, 한계)를 따릅니다.

→ [Sample Readme.MD](Sample%20Readme.MD) 참조

---

## 전체 맵

`trading map.png` — 본 폴더의 4종 전략 + Sample이 어떤 시장 상황에 적합한지 시각화한 맵.

---

## 사용 권장 순서

1. [Awesome claude quant scripts.MD](Awesome%20claude%20quant%20scripts.MD)에서 전체 개요 읽기
2. 본인 관심 영역에 맞는 전략 폴더로 이동
3. 해당 전략의 README와 한계 섹션 읽기
4. 백테스트 데이터 재현
5. 페이퍼 트레이딩 검증 후 실거래 고려

---

## Disclaimer

모든 스크립트는 연구·교육 목적입니다. 자세한 내용은 [메인 README의 Disclaimer](../../README.md#disclaimer) 참조.
