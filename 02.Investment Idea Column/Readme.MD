# 02. Investment Idea Column

vibe-investing 레포의 칼럼 인덱스입니다. 시장의 거시 흐름과 산업 변화를 분석한 칼럼을 한 자리에 모아둡니다.

→ [메인 README로 돌아가기](../README.md)

---

## 칼럼 목록

레포 곳곳에 흩어져 있는 칼럼들의 통합 인덱스입니다. 각 칼럼은 실제 위치에 따라 링크되어 있습니다.

| # | 제목 | 위치 | 주제 | 데이터 |
|---|---|---|---|---|
| 1 | LTCM의 사례로 배우는 모델을 읽는 힘 | [`/Vibe Investing Risk Management.MD`](../Vibe%20Investing%20Risk%20Management.MD) | 1998년 LTCM 사태 + AI 바이브 투자 리스크 | - |
| 2 | Microsoft의 Fintool 인수 | [`/Microsoft fintool acquisition column.MD`](../Microsoft%20fintool%20acquisition%20column.MD) | 370억 달러 금융 데이터 시장 진입 분석 | - |
| 3 | 보이지 않는 손인가, 계획된 사기인가 | [`/Crypto perp manipulation column.MD`](../Crypto%20perp%20manipulation%20column.MD) | 가상화폐 선물 pump-dump 패턴 수학적 검토 | - |
| 4 | 시장은 닫혔을 때 열리는가 | [`/AfterMarketClose/`](../AfterMarketClose/) | 미국 상장사 91.2% AMC 공시 집중 현상 | 34건 |
| 5 | DAT 기업의 mNAV 아비트리지 전략 | [`/mNAV(...)/`](../mNAV(Market-to-Net-Asset-Value)%20arbitrage/) | MSTR, BMNR 등 디지털 자산 보유 기업 분석 | CSV 3종 |
| 6 | 명품은 언제 사야 하는가 | [`/01.Trading Strategy/Luxury investment strategy/`](../01.Trading%20Strategy/Luxury%20investment%20strategy/) | LVMH, Hermès, Kering 3단계 포트폴리오 | CSV 4종 |
| 7 | 가상화폐와 나스닥은 얼마나 동기화되고 있을까 | [`/01.Trading Strategy/Investment Strategy ... Coupling/`](../01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) | BTC-QQQ 6년 상관관계 + 6 regime 분류 | CSV 4종 |

---

## 주제별 분류

### 위험 관리 / 시장 구조

| # | 제목 | 다루는 것 |
|---|---|---|
| 1 | LTCM 사례 | 모델 동질화로 인한 시스템 리스크, AI 바이브 투자의 함정 |
| 4 | After Market Close | 정보 비대칭, 시장 외 시간 공시 집중 현상 |

### 산업 / 섹터 분석

| # | 제목 | 다루는 것 |
|---|---|---|
| 2 | Microsoft Fintool 인수 | 금융 데이터 터미널 시장의 구조적 변화 |
| 6 | 명품 투자 전략 | 중국 경기 침체 시대의 명품 섹터 양극화 |

### 정량 / 데이터 기반 분석

| # | 제목 | 다루는 것 |
|---|---|---|
| 3 | Crypto perp manipulation | 벤포드 법칙 + 베이지안 분석으로 본 무기한 선물 시장 |
| 5 | DAT mNAV 아비트리지 | 12 사이클 + 15개 기업의 mNAV 정량 검증 |
| 7 | BTC-Nasdaq 커플링 | 26 분기 상관계수 + 31 이벤트 + 6 regime 분류 |

---

## 권장 읽기 순서

처음 오신 분에게 권장하는 순서:

1. **위험 관리부터** → 1번 (LTCM)
2. **시장 구조 이해** → 4번 (AMC)
3. **섹터 분석** → 6번 (명품)
4. **정량 분석** → 7번 (BTC-Nasdaq)

각 칼럼은 약 5,000-15,000자 분량이며, 핵심 발견 / 다루는 내용 / 데이터 출처 / 알려진 한계 순으로 구성되어 있습니다.

---

## 데이터셋

각 칼럼이 사용한 CSV는 해당 폴더 안에 함께 위치합니다. 모든 분석은 공개 데이터로 재현 가능합니다.

| 칼럼 | CSV 위치 |
|---|---|
| 4. AMC | [`/AfterMarketClose/`](../AfterMarketClose/) |
| 5. DAT mNAV | [`/mNAV(...)/`](../mNAV(Market-to-Net-Asset-Value)%20arbitrage/) |
| 6. 명품 | [`/01.Trading Strategy/Luxury investment strategy/`](../01.Trading%20Strategy/Luxury%20investment%20strategy/) |
| 7. BTC-Nasdaq | [`/01.Trading Strategy/Investment Strategy ... Coupling/`](../01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/) |

전체 데이터셋 인덱스는 [메인 README의 데이터셋 섹션](../README.md#데이터셋) 참조.

---

## 칼럼 작성 원칙

이 레포의 칼럼들은 다음 원칙을 따릅니다.

- **실증 데이터 기반** — 인상이나 주관이 아닌 공개 데이터에 근거
- **재현 가능** — 사용한 CSV를 함께 공개
- **법적 안전성** — 시장 구조 분석 시 특정 주체를 지목하지 않고 통계적 귀납만 사용
- **알려진 한계 명시** — 모든 결론에 적용 범위와 한계를 함께 제시
- **다국어 친화** — 영문 readers를 위한 번역 가능성 고려

---

## Disclaimer

모든 칼럼은 연구·교육 목적입니다. 시장 구조 분석은 통계적·학술적 논평이며 특정 주체를 지목하지 않습니다. 자세한 내용은 [메인 README의 Disclaimer](../README.md#disclaimer) 참조.
