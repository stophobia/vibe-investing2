# 01. Trading Strategy

vibe-investing 레포의 트레이딩 전략 인덱스입니다. 미국 주식(나스닥/S&P500), 가상화폐, 명품 섹터를 아우르는 정량 전략과 LLM 프롬프트, 그리고 학술 논문 기반 연구를 한곳에 모았습니다.

이 폴더 전체를 관통하는 방법론은 Multi-LLM 교차검증입니다. 동일한 프롬프트를 Claude, ChatGPT, Gemini, DeepSeek에 입력하고, 모델 간 합의는 robust한 신호로, 불일치는 사람이 더 깊이 검증해야 할 지점으로 다룹니다. 미래의 퀀트 시스템은 하나의 초지능이 아니라 서로 다른 철학을 가진 AI들의 위원회라는 가설 위에 서 있습니다.

→ [English version (영어 버전)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Readme%20EN.md)
→ [메인 README로 돌아가기](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md)
→ [Paper 논문 폴더 (이 전략들의 학술적 기반)](https://github.com/gameworkerkim/vibe-investing/blob/main/Paper%20%EB%85%BC%EB%AC%B8/readme.md)

---

## 처음 오셨다면: 읽는 순서

이 폴더에는 입문용부터 전문가용까지 난이도가 다양합니다. 본인 상황에 맞게 골라 읽으시길 권합니다.

기초부터 보고 싶다면, 먼저 [Awesome Claude Quant Scripts](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Readme.MD)의 프롬프트 모음으로 LLM에게 종목을 발굴시키는 방법을 익히고, 그다음 [명품 투자 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md)처럼 칼럼 형식으로 읽기 쉬운 섹터 분석을 보는 것을 추천합니다.

테마별로 묶어서 보고 싶다면, 아래 "테마별 정리" 섹션에서 관심 분야(AI/반도체, 배당, 가상화폐, 매크로/레짐, 공매도)를 선택하십시오.

데이터와 코드만 보고 싶다면, "데이터·코드 중심 항목" 섹션에 백테스트 CSV와 재현 가능한 Python 스크립트가 포함된 전략만 모아두었습니다.

최신 아이디어가 궁금하다면, 아래 "최신 아이디어" 섹션의 AI 헤지펀드와 ARDS를 먼저 보십시오.

---

## 최신 아이디어: AI를 헤지펀드 위원회처럼

이 레포의 가장 최근 방향성은, 단일 LLM에 의존하는 대신 여러 LLM의 서로 다른 개성을 하나의 헤지펀드 투자위원회처럼 운영하는 것입니다.

[AI 헤지펀드 (ai-hedge-fund) 분석 리포트](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/AI-hedge-fund/Readme.md) (한국어). GitHub 5만 스타 이상을 받은 오픈소스 프로젝트 virattt/ai-hedge-fund를 분석한 리포트입니다. 워런 버핏, 찰리 멍거, 캐시 우드 등 전설적 투자자 14인의 철학을 모방한 에이전트들과 가치평가·기술·펀더멘털·심리·리스크·포트폴리오 매니저 분석 에이전트가 LangGraph 위에서 협업하여 가상의 투자 결정을 내립니다. OpenAI/Groq/Anthropic/DeepSeek/Ollama를 지원합니다. 앞으로 이 구조 위에 LLM의 개성을 투자위원회처럼 운영하는 방향으로 발전시킬 예정입니다.

[ARDS — Adaptive Recession-Defensive Strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ARDS%3A%20Adaptive%20Recession-Defensive%20Strategy/readme.md) (2026-05-18, 한국어, 4-LLM 교차검증). 위 헤지펀드 위원회 개념 위에 세워진 가장 새로운 연구입니다. 

경기침체 진입기에 비대칭적 알파를 추구하는 동적 방어 포트폴리오로, AMQS-M7의 대칭적 헤지로 설계되었습니다. 핵심 발견은 거시 진단은 수렴하지만(4개 모델 모두 Phase 3 Recession-Warning, 표준편차 2.29pp) 실행은 발산한다는 것입니다 — 총 비중이 Claude 85%부터 DeepSeek 225%까지 14배 차이가 났고, 유일하게 만장일치한 종목은 GLD(금)뿐이었습니다. 모델별 캐릭터가 마치 멀티-PM 헤지펀드 투자위원회처럼 드러납니다.

(Claude는 절제된 PM, Gemini는 Cash-is-King 리스크 책임자, ChatGPT는 Quant 오버레이, DeepSeek는 공격적 알파 헌터).

앞으로 LLM의 개성과 해석의 다양성을 이용하여 LLM 헤지 펀드 위원회의 결정 구조를 chat bot으로 만들겠습니다.

[ARDS-X — Regime Classifier (조정·과매도·하락·침체 판별)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ARDS%20%E2%80%94%20Adaptive%20Recession-Defensive%20Strategy%20for%20AI_QQQ/README.md) (2026-06-06, 한국어 + KR/EN/CN 프롬프트, 재현 코드 + 대시보드 + 백테스트). 차별화 항목. ARDS의 실데이터 확장 모듈입니다. ARDS 원본이 5-Factor 침체 확률을 LLM으로 *추정*했다면, ARDS-X는 동일한 5-Factor를 **무료 실데이터(yfinance + FRED 무료 CSV)로 직접 계산**하고, 여기에 가격구조(드로다운·추세·과매도) 축을 더해 **2-축 레짐 맵**을 만듭니다. 핵심 질문은 *"미국 빅테크 + AI/인프라와 S&P500·Nasdaq100의 이 하락이 조정인가, 단기 과매도인가, 구조적 하락인가, 침체로 인한 리밸런싱인가"* 이며, 5개 상태 중 하나로 분류한 뒤 자매 전략(조정/과매도 → AMQS 모멘텀, 침체 → ARDS 방어)으로 핸드오프합니다. 즉 단독 매매 도구가 아니라 *"어떤 전략 책을 펴야 하나"를 판정하는 레짐 스위치*입니다. 2014–2026 백테스트에서 조정·과매도 구간의 60일 수익률은 +5%대(승률 77%)로 저점매수 가설이 검증된 반면, *시장 프록시만으로 만든 거시 축은 2022–24 곡선 역전 내내 침체를 과다 발화(BEAR_TRAP)* 하여 — 진짜 침체 판별에는 FRED의 Sahm Rule·LEI 같은 실데이터가 필수임을 역으로 입증했습니다.

---

## 테마별 정리

### AI / 반도체 / 모멘텀

[AMQS — Adaptive Momentum Quant Strategy (백테스트 리포트)](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/readme.md) (2026-05-02 v1.0, 한국어 + KR/EN 프롬프트). 차별화 항목. AI 슈퍼사이클 모멘텀 주간 리밸런싱 전략의 완전 공개 코드 + 백테스트입니다. 2024-01 ~ 2026-04 백테스트에서 AMQS +114.1% vs QQQ +46.2%, Sharpe 1.33, MDD -16.9%를 기록했습니다. 4-Factor Composite 모멘텀(12-1/6-1/3-1/변동성조정) + 거시 레짐 필터(QQQ 200일선/VIX) + 주간 리밸런싱이 핵심입니다. 시리즈 4세대.

[AMQS-M7 — Magnificent 7 특화 확장판](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/readme.md) (한국어 + KR/EN/CN 3개 언어 프롬프트). 위 AMQS를 M7(AAPL/MSFT/GOOGL/AMZN/META/NVDA/TSLA)에 특화한 확장판으로, 5번째 점수 차원으로 "단기 하락 매수 모멘텀(Pullback-in-Uptrend)"을 정식 편입했습니다. 4중 게이트로 falling knife를 차단합니다.

가상화폐가 아닌 미국 주식 단기 공매도 아이디어로는 [나스닥 공매도 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Nasdaq%20short%20selling%20strategy/IdeaNote.MD) (한국어, 미완성/아이디어 단계)과 [SaaS Short / HBM Long](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/SaaS%20short%20HBM%20Long) (준비중)도 참고하십시오.

### 가상화폐 — 시장 미시구조 및 포렌식

이 항목들은 모두 SSRN 논문 또는 5부작 칼럼 시리즈와 연결됩니다.

[Token Unlock 72h Shock Analysis](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Token%20unlock%2072h%20shock%20analysis%20/readme.MD) (2026-04-23 v3.0, 영어, 재현 코드 포함). 차별화 항목. 바이낸스 토큰 언락 52건 중 88.5%가 72시간 내 음의 수익률(평균 -16.97%, 이항검정 p=2.2×10⁻⁹)을 보임을 실증했습니다. SSRN 논문 #1(6632838)의 저장소로, 8개 Python 스크립트 + 10개 CSV로 모든 표를 재현할 수 있습니다.

[Binance Listing Day Crash](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Binance%20Listing%20Day%20Crash%20/Listing%20day%20crash%20analysis.md) (2026-04-20, 한국어). 차별화 항목. 2024-2025 바이낸스 상장 51개 토큰 전수 분석으로, 96.1%가 24시간 내 하락(72시간 평균 -45.24%)했음을 보였습니다. BTC가 +5% 상승하는 환경에서도 평균 -35.2% 하락하여 구조적 매도압을 증명합니다. LST-10 Ultimate Hybrid 숏 전략 포함. ([자기비판 로드맵](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Binance%20Listing%20Day%20Crash%20/Listing%20day%20crash%20selfcritique%20roadmap.md)도 동봉)

[Binance Alpha MM 봇을 잡아먹는 트레이딩 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Trading%20strategy%20that%20devours%20Binance%20Alpha%20MM%20bots/Binance%20alpha%20mm%20bot%20analysis.MD) (2026-04-20, 한국어). 바이낸스 Alpha 221개 상장 토큰 분석으로, MM 봇의 5단계 행동 모델(MBP-5: Accumulation → Pump Signal → Peak Formation → Distribution → Capitulation)을 제시합니다. Phase 3에서 숏 진입하는 STR-07 Hybrid 전략이 백테스트 승률 86%, Sharpe 3.25를 기록했습니다. 5부작 칼럼 시리즈 중 2부.

[BNB Trading Bot — BNB-ETH 정량 분석](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/BNB%20Trading%20Bot/Readme.md) (한국어 / 영어 / 중국어). BNB-ETH 4년치 통계 분석과 ETH 이동평균 교차 기반 BNB 트레이딩 신호입니다. HODLer 에어드롭 이후 상관계수는 유지되나 베타만 0.643→0.534로 감소(디커플링)하는 패턴을 발견했고, 백테스트 +123.21%를 기록했습니다. SSRN 논문 #4(6750298)와 연결됩니다.

[비트코인-나스닥 커플링 기반 투자 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Investment%20Strategy%20Based%20on%20Bitcoin%20and%20Nasdaq%20Coupling/IdeaNodte.MD) (2026-04, 한국어, 짧은 아이디어 노트). 2025년 평균 상관계수 0.52에서 2026년 4월 -0.20(10년 최저)으로 급변한 BTC-나스닥 관계를 다룹니다. 하락은 함께, 상승은 따로 움직이는 비대칭 커플링이 핵심 관찰입니다.

### 배당 / 자본 환원

배당 성장 및 자본 환원 전략은 대부분 [Awesome Claude Quant Scripts](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Awesome%20claude%20quant%20scripts/Readme.MD) 폴더 안에 프롬프트와 스크립트로 정리되어 있습니다(배당 성장 프롬프트, Dual-Engine Capital Compounder, 장기 배당 투자 등). 해당 폴더 README를 참조하십시오.

### 섹터 분석

[명품 투자 전략 — 럭셔리 기업 주식은 언제 사야 하는가](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md) (2026-04-19, 한국어). 입문용으로 읽기 좋은 칼럼형 섹터 분석입니다. 명품 13개 기업·ETF의 2020-2026 데이터와 225건 백테스트를 통해, 단일 종목 집중(LVMH DCA -10.87%)의 실패와 GLUX ETF를 통한 분산의 우위를 보입니다. 저/중/고 위험 3단계 포트폴리오를 제안합니다.

### 매크로 / 레짐 진단 (4-LLM 교차검증)

[MRDS — Market Regime Diagnostic Quant Strategy](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Market%20Regime%20Diagnostic%20Quant%20Strategy/readme.md) (2026-05-19 v2.0, 한국어, 4-LLM 교차검증). 차별화 항목. 동일한 시장 레짐 진단 프롬프트를 4개 LLM에 실행한 비교 리포트입니다. 3-of-4가 Cyclical Correction으로 수렴했으나, 동일 지표(NVDA 데이터센터 매출 YoY)에서 +44%/+73%/+115%의 LLM 환각(hallucination)을 발견하여, 모든 정량 수치의 원본 교차검증 필요성을 실증합니다. 시리즈 5세대 메타 레이어.

---

## 미완성 / 사전 연구 단계 항목

아래 항목들은 아이디어 또는 연구 설계 단계이며, 정량적 결론을 포함하지 않습니다. 사용 시 이 점에 유의하십시오.

[Disclosure Timing Around Token Unlocks](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/%20Disclosure%20Timing%20Around%20Token%20Unlocks/ideanote%20disclosuretiming%20kr.MD) (2026-04-23, 한국어 / [영어](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/%20Disclosure%20Timing%20Around%20Token%20Unlocks/ideanote%20disclosuretiming.MD)). 미완성 — Phase 3 연구 프로그램 설계 문서(목표 실행 2027 Q1-Q2). 토큰 언락 전후 재단 공시의 시간적 군집화와 실행-약속 간극을 LLM으로 탐지하는 연구 청사진입니다. 관련 보고서 PDF: [Report Token_Unlock_72h_Shock_Analysis.pdf](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Report%20Token_Unlock_72h_Shock_Analysis.pdf).

[ChainWar — 체인별 토큰 상장 후 성과 비교](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ChainWar/IdeaNote_ChainWar.MD) (2026-04-24, 한국어 v0.1). 미완성 — Phase 4 연구 프로그램 초안(목표 실행 2027 Q3-Q4). BNB Chain vs ERC-20 vs Solana 토큰의 BTC 조정 성과 차이를 검증하려는 사전 아이디어 노트로, 모든 패턴은 검증이 필요한 가설입니다.

[나스닥 공매도 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Nasdaq%20short%20selling%20strategy/IdeaNote.MD) (한국어). 미완성 — 짧은 아이디어 노트. 섹터/종목 커플링 기반 단기 공매도·곱버스 전략의 초기 구상입니다.

[SaaS Short / HBM Long](https://github.com/gameworkerkim/vibe-investing/tree/main/01.Trading%20Strategy/SaaS%20short%20HBM%20Long) (준비중). SaaS 숏 / HBM 롱 페어 전략 폴더입니다.

---

## 데이터·코드 중심 항목 (백테스트 CSV + 재현 Python)

코드와 데이터로 직접 검증하고 싶다면 아래 항목들이 적합합니다.

- [ARDS-X Regime Classifier](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/ARDS%20%E2%80%94%20Adaptive%20Recession-Defensive%20Strategy%20for%20AI_QQQ/README.md): yfinance + FRED 무료 CSV 기반 레짐 분류 엔진 + 2-축 대시보드 + 룩어헤드 없는 백테스트(상태별 향후수익률 CSV) + KR/EN/CN 프롬프트. API 키 불필요.
- [AMQS](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)/readme.md): yfinance 기반 백테스트 엔진 + 실시간 스크리너 + 일별 NAV CSV
- [AMQS-M7](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Adaptive%20Momentum%20Quant%20Strategy%20(AMQS)%20for%20M7/readme.md): CLI 트래커 + 백테스트 + KIS 증권사 API 자리표시
- [Token Unlock 72h](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Token%20unlock%2072h%20shock%20analysis%20/readme.MD): 8개 Python 스크립트로 논문 전체 표 재현 + 10개 CSV
- [BNB Trading Bot](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/BNB%20Trading%20Bot/Readme.md): 독립 실행형 신호 프로그램 + 13개 분석 CSV
- [Binance Listing Day Crash](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Binance%20Listing%20Day%20Crash%20/Listing%20day%20crash%20analysis.md): 분석 엔진 + 역전략 봇 + 5개 CSV
- [Binance Alpha MM 봇](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Trading%20strategy%20that%20devours%20Binance%20Alpha%20MM%20bots/Binance%20alpha%20mm%20bot%20analysis.MD): 리서치 엔진 + 역전략 봇 + 5개 CSV
- [명품 투자 전략](https://github.com/gameworkerkim/vibe-investing/blob/main/01.Trading%20Strategy/Luxury%20investment%20strategy/Luxury%20investment%20strategy.md): 4개 CSV 데이터셋 (성과, 백테스트, 위험별 포트폴리오)

---

## 언어 지원 현황

| 항목 | 한국어 | 영어 | 중국어 |
| --- | --- | --- | --- |
| Awesome Claude Quant Scripts | O | O | 일부 프롬프트 |
| AMQS (원본) | O | 프롬프트만 | - |
| AMQS-M7 | O | 프롬프트 | 프롬프트 |
| ARDS | O | 업데이트 예정 | - |
| ARDS-X Regime Classifier | O | O | 프롬프트 |
| AI 헤지펀드 | O | 업데이트 예정 | - |
| MRDS | O | 업데이트 예정 | - |
| Token Unlock 72h | 보고서 KR | O (본문) | - |
| BNB Trading Bot | O | O | O |
| Binance Listing Day Crash | O | 업데이트 예정 | - |
| Binance Alpha MM 봇 | O | 업데이트 예정 | - |
| 명품 투자 전략 | O | 업데이트 예정 | - |
| Disclosure Timing | O | O | - |
| ChainWar | O | 업데이트 예정 | - |
| 비트코인-나스닥 커플링 | O | 업데이트 예정 | - |
| 나스닥 공매도 | O | 업데이트 예정 | - |

참고: ARDS, MRDS, Binance Listing Day Crash, Binance Alpha MM 봇, 명품 투자 전략은 완성도가 높게 평가되는 한국어 전략이지만 아직 영어 버전이 없어 "업데이트 예정"으로 표기했습니다.

---

## 논문과의 연결 (학술적 기반)

이 폴더의 여러 가상화폐 전략은 SSRN에 게재된 4편의 작업 논문에서 도출되었습니다. 자세한 내용은 [Paper 논문 폴더](https://github.com/gameworkerkim/vibe-investing/blob/main/Paper%20%EB%85%BC%EB%AC%B8/readme.md)를 참조하십시오.

- 논문 #1 (SSRN 6632838): 72-Hour Shock, 바이낸스 토큰 언락 52건 → Token Unlock 72h 전략의 기반
- 논문 #2 (SSRN 6688740): 중앙화 거래소 에어드롭 분배 비대칭, BNB Chain 생태계
- 논문 #3 (SSRN 6705598): Less Volume More Variety, LLM 출력 길이와 컨트라리안 발굴 → Multi-LLM 방법론의 학술적 근거
- 논문 #4 (SSRN 6750298): Directional Decoupling, BNB-ETH 베타 변동성 비율 분해 → BNB Trading Bot의 기반

---

## 사용 시 권장 순서

1. 관심 시장 확인 (미국 주식 / 명품 / 가상화폐 / 매크로 레짐)
2. 해당 테마의 README와 칼럼을 먼저 정독
3. 스크립트나 봇 실행 전 각 문서의 "한계" 및 "위험 고지" 섹션 필수 확인
4. CSV 데이터로 재현·검증
5. 페이퍼 트레이딩으로 검증 후 실거래 고려
6. Multi-LLM 교차검증: 동일 프롬프트를 2개 이상 LLM에 입력하고, 합의 종목과 불일치 종목을 분리하여 불일치 종목은 1차 출처(SEC EDGAR, 10-Q, FRED 등)로 검증

---

## 위험 고지 (Disclaimer)

각 전략은 연구·교육 목적이며 투자 조언이 아닙니다. 백테스트 결과는 이상적 시나리오 기반이며 실거래 수익률과 다릅니다. LLM이 생성한 점수와 확률은 추정치이지 통계 모델의 출력이 아닙니다. 가상화폐 트레이딩 봇 코드는 모두 연구용 프로토타입으로, 실전 투입 전 testnet 검증과 법률 검토가 필수입니다. 한국 거주자는 해외주식 양도소득세 22%, 외환거래법, 가상자산이용자보호법 등 다중 규제 대상임을 유의하십시오. 자세한 내용은 [메인 README의 Disclaimer](https://github.com/gameworkerkim/vibe-investing/blob/main/README.md#disclaimer)를 참조하십시오.

---

## 저자

김호광 (Dennis Kim / HoKwang Kim) — Betalabs Inc. CEO, Microsoft Azure ex-MVP, CyworldZ 전 CEO

- ORCID: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
- GitHub: [@gameworkerkim](https://github.com/gameworkerkim)
- Email: gameworker@gmail.com

라이선스: MIT (출처 표기 권장: "Dennis Kim / vibe-investing")
