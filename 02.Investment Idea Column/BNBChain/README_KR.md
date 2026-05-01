# 중앙화 거래소 에어드롭의 분배 비대칭과 BNB Chain 생태계

[![SSRN: 6688740](https://img.shields.io/badge/SSRN-6688740-orange.svg)](https://ssrn.com/abstract=6688740)
[![Companion: SSRN 6632838](https://img.shields.io/badge/Companion-SSRN%206632838-orange.svg)](https://ssrn.com/abstract=6632838)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **다국어 README**: [English](./readme.md) · [中文](./README_CN.md) · [日本語](./README_JP.md)

---

## 개요

본 저장소는 2024-2025년 바이낸스의 중앙화 거래소 (CEX) 에어드롭 프로그램 (Megadrop 및 HODLer Airdrop) 의 *분배 비대칭 메커니즘* 을 실증적·이론적으로 분석한 **사전 워킹 페이퍼, 소스 코드, 데이터, 다이어그램** 을 포함합니다.

**저자**: 김호광 (Dennis Kim), Betalabs Inc. CEO
**상태**: Preliminary Working Paper, 2026년 5월
**SSRN**: [Abstract ID 6688740](https://ssrn.com/abstract=6688740)
**동반 논문**: [Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838](https://ssrn.com/abstract=6632838)

---

## 연구 질문

> **바이낸스의 26억 달러 규모 에어드롭 프로그램에서 누가 실제로 이익을 얻고, 누구의 비용으로 이루어지는가?**

2024-2025년 바이낸스는 76개 이상의 보상 프로그램을 통해 BNB 보유자에게 약 26억 달러를 분배했으며, 이는 글로벌 CEX 분배의 약 94%를 차지합니다. 대표 프로그램은 *Megadrop* 과 *HODLer Airdrop* 이며, *"BNB를 락업하면 신규 프로젝트 토큰을 무료로 받는다"* 라고 광범위하게 홍보됩니다.

본 연구는 세 행위자에 미치는 차별적 영향을 형식화합니다:

1. **BNB 홀더** — 분배된 토큰의 수령자
2. **발행 재단** — 신규 토큰을 발행하는 프로젝트 주체
3. **BNB Chain 생태계** — 블록체인 플랫폼 자체

---

## 핵심 발견

### 1. 재단 재앙 (Foundation Disaster)

평균 분배 비율 α = 7.3% 의 Megadrop 토큰의 경우:
- **재단 비용 ≈ FDV의 30.5%** (Fully Diluted Valuation)
- **비대칭 비율 R = 4.18** (재단 손실 : 홀더 이익)
- **가치 파괴 D ≈ FDV의 23%** (시장 마찰을 통한)

### 2. 수학적 강건성

합리적 파라미터 범위에서 (α: 2-15%, θ: 30-60%, d: 10-90%):
- 재단 비용은 항상 ≥ 12.75%
- 비대칭 비율은 항상 R ≥ 1.70
- **임계 분배 비율 α* = 5.95% (R*=5)** — Megadrop의 일반적 5-8% 범위가 폭발 영역에 포함

### 3. 실증 검증

부트스트랩 95% 신뢰구간 분석 (N = 10,000회 반복, 표본 N = 21개 토큰):

| 카테고리 | N | 평균 수익률 | 95% CI |
|----------|---|-------------|--------|
| Megadrop | 5 | -76.0% | [-86.4%, -65.8%] |
| HODLer | 8 | -19.5% | [-67.8%, +39.6%] |
| Launchpool | 5 | -29.8% | [-50.4%, +0.0%] |
| Direct (Memecoin) | 2 | +81.5% | [+68.0%, +95.0%] |
| **Direct (HYPE 포함)** | 3 | **+384.3%** | **[+68.0%, +990.0%]** |

**Cohen's d (Megadrop vs. Direct, N=21) = -1.52** (매우 큰 효과 크기, Hyperliquid HYPE 반사실 통합을 통한 학술적 신뢰성 확보)

### 4. 디커플링 패턴 (Decoupling Pattern)

Megadrop 토큰이 하락하는 동안 BNB Chain 생태계는 *반대 방향* 으로 성장:

| 지표 | 2025년 Q1→Q3 변화 |
|------|-------------------|
| BNB Chain 거래량 | **+171.4%** |
| BNB Chain DeFi TVL | **+47.2%** |
| BNB Chain 활성 지갑 | **+91.6%** |
| BNB 가격 | $629 → $1,030 (Q4 ATH $1,369) |
| Megadrop 카테고리 시가총액 | **-75%** |

### 5. 3 행위자 절대 금액 영향 (2024-2025)

| 행위자 | 추정 영향 |
|--------|-----------|
| BNB 홀더 (이익) | **+$14억-20억** |
| 발행 재단 (손실) | **-$48억** |
| BNB Chain 시가총액 (성장) | **+$1,040억** |

**핵심 통찰**: 재단 손실은 명확하지만 (홀더 이익의 2.84배), BNB Chain 시가총액 성장의 4.6%에 불과 — *시스템 차원의 디커플링 패턴*.

### 6. 이론적 기여

7개 정리가 재단 비용 함수를 형식화하고 다음을 증명:

- **정리 6**: *손익분기 불가능성* — d* = -α/(1-α-θ) < 0 (재단은 가격 상승으로만 손익분기 가능)
- **정리 7**: *내쉬 균형* — 즉시 매도가 지배 전략

본 연구는 Allen, Berg, Lane (2023) 의 *직접 에어드롭* 분석을 *중앙화 거래소 주도 (CEX-led) 에어드롭* 의 새로운 카테고리로 확장하며, Schelling (1960) 의 협조 게임 이론과 Morris와 Shin (1998) 의 Global Games 프레임워크를 적용합니다.

---

## 저장소 구조

```
.
├── README.md                          # 영문판
├── README_KR.md                       # 한국어판 (이 파일)
├── README_CN.md                       # 중국어판
├── README_JP.md                       # 일본어판
├── paper/                             # 논문 산출물
│   ├── Distribution_Asymmetry_CEX_Airdrops.md
│   ├── Distribution_Asymmetry_CEX_Airdrops.pdf
│   ├── Distribution_Asymmetry_CEX_Airdrops_with_figures.docx
│   └── Distribution_Asymmetry_CEX_Airdrops_with_figures.pdf
├── figures/                           # 7개 출판 등급 시각 자료
├── scripts/                           # Python 소스 코드
├── data/                              # 입력 데이터 (CSV, 영문)
├── results/                           # 분석 결과 출력
└── docs/                              # 문서
```

---

## 재현성

### 빠른 시작

```bash
# 저장소 복제
git clone https://github.com/gameworkerkim/vibe-investing.git
cd vibe-investing/02.Investment\ Idea\ Column/BNBChain

# 의존성 설치
pip install pandas numpy scipy matplotlib

# 모든 분석 실행 (results/ 에 출력)
cd scripts/
python correlation_analysis.py
python robustness_analysis.py
python integrated_analysis_v10.py
python pair_trading_backtest.py

# 모든 다이어그램 재생성 (figures/ 에 출력)
for f in generate_figure*.py; do python "$f"; done
```

---

## 주의사항 및 한계

본 연구는 **사전 워킹 페이퍼** 입니다. 다음 한계를 명시적으로 인정합니다:

1. **표본 크기**: N=21 토큰 (카테고리당 N=2-8) 은 완전한 통계적 추론에 부족. 후속 버전에서 N≥100으로 확대 예정
2. **인과성**: 디커플링 패턴은 **관찰 증거에만 해당**. 완전한 Granger 인과성 검정은 일별 데이터가 필요하며 후속 버전에서 진행
3. **시간 해상도**: 분기별 데이터는 단기 인과 방향 추론을 제한
4. **선택 편향**: Direct 카테고리 밈코인 편향은 HYPE 포함 (N=2→N=3) 으로 부분 완화되었으나 선택 효과를 완전히 배제할 수는 없음
5. **트레이딩 전략**: 5.4절의 BTC 도미넌스 패턴은 **관찰 증거** 일 뿐 트레이딩 전략 사용 권장 안 함
6. **예측**: 본 연구는 과거 상장 사례의 **기술적 분석** 을 생산. CEX 정책 변화로 미래 토큰은 다른 패턴을 보일 수 있음

---

## 인용

본 코드, 데이터, 논문을 연구에 사용하실 경우 다음과 같이 인용 부탁드립니다:

```bibtex
@misc{kim2026distribution,
  author = {Kim, HoKwang},
  title = {Distribution Asymmetry of Centralized Exchange Airdrops and the BNB Chain Ecosystem},
  year = {2026},
  publisher = {SSRN},
  doi = {10.2139/ssrn.6688740},
  url = {https://ssrn.com/abstract=6688740},
  note = {Preliminary working paper}
}
```

---

## 라이선스

본 저장소는 **이중 라이선스** 를 사용합니다:

- **소스 코드** (`scripts/` 의 Python 스크립트): [MIT 라이선스](https://opensource.org/licenses/MIT)
- **논문, 데이터, 다이어그램** (`paper/`, `data/`, `figures/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## 저자

**김호광 (Dennis Kim)** · 독립 연구자
- Betalabs Inc. CEO (블록체인 컴퍼니 빌더)
- 전 Cyworld Z CEO
- 전 Microsoft Azure MVP (9년)
- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

---

## 로드맵

### v1.2 (현재 — 2026년 5월)
- ✅ HYPE 반사실 통합 (N=2→N=3)
- ✅ 부트스트랩 95% CI (N=10,000회 반복)
- ✅ 3 행위자 차별적 영향 정량화
- ✅ 7개 출판 등급 다이어그램 + 학술 캡션
- ✅ 5.2절 상관계수 값 수정
- ✅ 본문 등장 순서대로 그림 번호 재부여

### v2.0 (예정 — 2027)
- 표본 크기 N≥100 토큰
- CoinGecko/Binance API 를 통한 일별 OHLCV 데이터
- 완전한 Granger 인과성 검정
- 선택 편향에 대한 Propensity Score Matching (PSM)
- Heckman 2단계 추정
- 다중 거래소 비교 (Bybit, OKX, Coinbase)
- 동료 검토 학술지 LaTeX 제출

---

## 관련 문헌

- **동반 논문**: Kim, H. (2026). *The 72-Hour Shock: Token Unlock Price Impact*. SSRN 6632838.
- **토큰 언락 문헌**: Allen, F., Gu, X., & Li, J.Y. (2023). *Crypto Tokens and Token Offerings*. Annual Review of Financial Economics.
- **공적분 방법론**: Engle, R.F., & Granger, C.W.J. (1987). *Co-integration and Error Correction*. Econometrica.
- **협조 게임**: Schelling, T.C. (1960). *The Strategy of Conflict*. Harvard University Press.
- **Global Games**: Morris, S., & Shin, H.S. (1998). *Unique Equilibrium in a Model of Self-Fulfilling Currency Attacks*. American Economic Review.

---

*최종 업데이트: 2026년 5월 1일*
