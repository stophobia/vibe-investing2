# Awesome Vibe Invest — Crypto Edition (2026년 6월 18일 업데이트)

> **비트코인을 비롯한 암호화폐를 위한 LLM 트레이딩 GitHub 큐레이션 — 2026년 6월 갱신본.** 기존 2026년 4월 스냅샷 이후의 변화(Alpha Arena Season 1 최종 결과 정정, Season 1.5/2, 신규 프레임워크, MCP 생태계, 모델 지형 변화)를 반영합니다. 본 문서는 기존 본문에 병합(merge)하거나 별도 부록으로 추가할 수 있도록 구성했습니다.

---

## 이번 갱신의 핵심 (TL;DR)

1. **Alpha Arena Season 1 최종 결과 정정** — 기존 본문은 "DeepSeek V3.1 +46%로 우승"으로 기록했으나, 이는 대회 *중간 피크* 수치였다. 11월 3일 **최종 우승은 Qwen3 Max(+22.3%)**, DeepSeek는 2위로 마감했다. GPT-5는 -75%가 아니라 **약 -63%** 손실. 본문의 결정적 데이터 라인은 아래 정정 표를 따른다.
2. **Season 1.5 종료, Season 2 예고** — 1.5는 $320K 규모, 8개 모델(Kimi K2 + 스텔스 모델 추가), **미국 주식 토큰** 대상, 4종 경쟁 모드 도입. Season 2는 **인간 트레이더 동반 참가** 예고.
3. **Nof1 $15M 투자 유치** (SUI Group, Karatage 주도, 2026년 5월). Season 2 이후 *"마켓용 코딩 에이전트"* 소비자 제품 출시 계획.
4. **신규 프레임워크 다수** — TradingAgents(TauricResearch), ATLAS(자기개선 25-에이전트), oracle3(예측시장), OpenFinClaw, Vibe-Trading 등.
5. **MCP 생태계가 별도 카테고리로 성장** — Hyperliquid/Jupiter/sentiment/indicator MCP 서버군이 Claude·코딩 에이전트 직결 인프라로 자리잡음.
6. **모델 지형 변화** — 2026년 6월 기준 프론티어는 Claude Opus 4.5 계열, GPT-5.2/5.4/5.5 계열, Gemini 3.x, Kimi K2, DeepSeek/Qwen 최신판. 본문의 "GPT-5 / Claude Sonnet 4.5 / Gemini 2.5 Pro" 표기는 Season 1 시점 기준임을 명시.

---

## 평가 기준

기존 5+2 차원 체계는 유지하되, 이모티콘 표기를 텍스트로 전환합니다.

| 차원 | 의미 |
| --- | --- |
| 활성도 | 활발 (최근 3개월 내 커밋 다수) / 유지보수 / 정체 (6개월+ 무커밋) |
| 성숙도 | POC / Research (학술 검증) / Production-ish (실제 자본 운용) |
| 학습곡선 | Lv.1 쉬움 / Lv.2 중간 / Lv.3 가파름 |
| 벤치마크 | 공개 정량 결과 있음 / 백테스트 결과만 / 미공개 |
| 라이선스 | MIT / Apache / GPL / Custom |
| 체인 커버리지 | EVM / Solana / Hyperliquid / 멀티체인 / CEX 전용 |
| MEV 보호 | 있음 / 없음 — 온체인 봇에 필수 |

---

## A. 벤치마크 갱신 — Alpha Arena 그 이후

### A.1 Season 1 최종 결과 (정정)

기존 본문의 "DeepSeek +46% 우승"은 대회 중간(10월 말) 피크 기준이었다. DeepSeek는 한때 계좌가 약 +48%까지 올랐으나 변동성이 컸고, **11월 3일 종료 시점 최종 순위는 Qwen3 Max 우승**이다. 종료 시점 손익 요약:

| 모델 | 최종 손익(대략) | 비고 |
| --- | --- | --- |
| Qwen3 Max | +22.3% (~$12,287) | 저빈도·고확신 거래, MACD/RSI + 엄격한 손절/익절 |
| DeepSeek V3.1 | +5% 부근 ($10,476 부근, 피크 약 +48%) | 장기 보유·일관된 청산, 우상향 곡선이나 변동 큼 |
| Claude Sonnet 4.5 | 약 -31% (-$3,081) | 거의 숏 미사용, 100% 롱 유지 → 중간 반전에 노출 |
| Grok 4 | 약 -45% (-$4,531) | 소셜 센티먼트 추종, FOMO 랠리에 매수·하락에 청산 |
| Gemini 2.5 Pro | 약 -57% (-$5,671) | 과매매(238회), 거의 전 구간 적자 |
| GPT-5 | 약 -63% (-$6,267) | 신호 충돌 시 결정 회피·헤지테이션, 본문 "-75%" 수치는 정정 필요 |

핵심 교훈은 그대로 유효하다 — **모델 IQ가 곧 트레이딩 IQ는 아니다.** 다만 우승자가 Qwen3 Max라는 점에서 "규율적 저빈도 실행 + 명시적 손절/익절"이 "잦은 매매"보다 우월했다는 해석을 본문에 추가하는 것이 정확하다.

### A.2 Season 1.5 (2025년 11월~12월 종료)

- **규모**: 총 $320K 배치 (Season 1의 $60K 대비 대폭 확대).
- **자산**: 크립토 무기한이 아닌 **미국 주식 토큰**을 Hyperliquid에서 거래.
- **모델**: 총 8개 — 기존 6개 + **Kimi K2**(중국)와 **상위 AI 랩의 스텔스(미스터리) 모델** 추가.
- **4종 경쟁 모드** (입력 조건을 달리해 모델의 적응력·견고성을 스트레스 테스트):
  - New Baseline: 뉴스·센티먼트·펀더멘털 등 풍부한 입력 제공.
  - Monk Mode: 자본 보존 강조 — *"아무것도 안 하는 것"*이 최선일 수 있는 환경.
  - Situational Awareness: 모델이 자신의 순위와 타 모델 손익을 인지.
  - Max Leverage: 매 거래 최대 레버리지 강제 (NDX 20x, 기타 10x).
- 각 모드 결과를 종합 집계, 통계적 엄밀성(statistical rigor) 보강이 목표.

### A.3 Season 2 (예고) 및 Nof1 펀딩

- **Season 2**: 인간 트레이더가 AI 모델과 **함께 경쟁**하는 형식을 예고. 추론 난이도 강화.
- **투자 유치**: 2026년 5월, **SUI Group·Karatage 주도 $15M 라운드**. Season 2 이후 *"마켓용 코딩 에이전트(coding agents for markets)"* 소비자 제품 출시 계획 — 인간·알고리즘 트레이더 모두 타깃.
- **주의**: nof1.ai 리더보드는 동적 렌더링이라 스냅샷 시점에 따라 순위가 다르다. 사용 전 직접 확인 필수.

### A.4 경쟁 아레나의 부상

Alpha Arena가 카테고리를 열자 유사 벤치마크/아레나가 다수 등장했다. 단순 관전·평가용으로 교차 확인 권장.

| 플랫폼 | 특징 | 비고 |
| --- | --- | --- |
| Rallies.ai AI Trading Arena | LLM 실시간/근실시간 주식 트레이딩 경쟁 | Alpha Arena와 자주 비교됨 |
| RockAlpha (RockFlow) | 아레나 + 카피트레이딩 브로커리지 연동 | 상위 AI 에이전트 미러링 상품화 |
| AI Trade Arena / Obside | 의사결정 체인 투명성·운영 연속성 강조 | 2026 비교 리뷰에서 다뤄짐 |

- **약점 공통**: 대부분 sample size·기간이 짧고, 일부는 카피트레이딩 영업과 결합되어 *상품 홍보 편향* 가능. 리더보드 수치를 trading skill의 결론으로 직결하지 말 것.

---

## B. 신규 / 갱신 프레임워크

### B.1 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)

> 실제 트레이딩 회사의 분업 구조를 모사한 멀티 에이전트 프레임워크. 펀더멘털 애널리스트·센티먼트·기술 분석·트레이더·리스크 매니지먼트 팀을 LLM 에이전트로 구성해 협업 의사결정. 본 큐레이션 추가 1순위.

- **활성도**: 활발 (2026-05 v0.2.5) | **성숙도**: Research → Production-ish | **학습곡선**: Lv.2 | **벤치마크**: 백테스트 + non-US 알파 벤치 | **체인**: CEX/주식 중심(크립토 티커 적용 가능) | **라이선스**: 오픈소스
- **강점**:
  - **멀티 프로바이더 일급 지원** — GPT-5.x, Gemini 3.x, Claude 4.x, Grok 4.x, DeepSeek/Qwen/GLM/MiniMax, Ollama, OpenAI-compatible(vLLM·LM Studio·llama.cpp).
  - **지속 메모리 + 리플렉션** — 매 실행의 결정 로그를 저장, 다음 실행 시 실현 수익(raw 및 SPY 대비 알파)을 회수해 한 문단 회고를 생성·주입. CryptoTrade의 reflection 패턴을 프로덕션급으로 일반화.
  - deep_think_llm / quick_think_llm 분리 — 깊은 추론과 빠른 작업을 다른 모델에 배분(본문 9.7 latency 함정 대응 패턴의 정석).
  - LangGraph 체크포인트 resume, 구조화 출력, Docker, 다국어 지원.
  - Trading-R1 기술 리포트 + Terminal 제품 예고.
- **약점**: 주식 중심 설계 — 크립토 24/7·온체인 신호 통합은 사용자가 직접. LLM 비결정성으로 동일 입력에도 결과 분산(설계상 의도).
- **적합 사용자**: 멀티 에이전트 + 리플렉션 메모리 아키텍처의 현행 레퍼런스를 찾는 개발자. ARDS/AMQS류 자체 프레임워크의 cross-validation 베이스라인으로 적합.

### B.2 ATLAS (자기개선 멀티 에이전트)

> 25개 에이전트, Karpathy식 오토리서치, 다윈주의적 선택(Darwinian selection), 자율 에이전트 스포닝, 멀티-코호트 메타 가중치를 갖춘 자기개선 트레이딩 시스템.

- **활성도**: 활발 | **성숙도**: Research/실험 | **벤치마크**: 자체 메트릭
- **강점**: "에이전트 풀을 진화시킨다"는 접근 — 전략 생성→선택→재조합 루프가 본문의 Multi-LLM Cross-Validation 사상과 통한다.
- **약점**: 복잡도 높음, 자기개선 주장에 대한 외부 검증 부족. 과적합·서바이버십 바이어스 경계.
- **적합 사용자**: 전략 자동 탐색·진화에 관심 있는 연구자 (실거래 전 paper 검증 필수).

### B.3 그 외 주목 레포 (검증 권장)

| 프로젝트 | 한 줄 요약 | 카테고리 |
| --- | --- | --- |
| oracle3 | Kalshi·Polymarket·Solana DFlow 예측시장 에이전트, Wang Transform 가격결정 + 차익 전략 | 예측시장 |
| OpenFinClaw | 자연어 → 60초 퀀트 전략, 멀티마켓(US/HK/CN/Crypto), 자기진화 파이프라인 + 커뮤니티 리더보드 | 멀티마켓 |
| Vibe-Trading | 전략 생성·백테스트·포트폴리오 분석을 묶은 멀티 에이전트 리서치 워크스페이스 | 리서치 워크스페이스 |
| AgentFund | Base 체인 마일스톤 에스크로 기반 AI 에이전트 크라우드펀딩 | 에이전트 자본조달 |
| InvicTrade | 레전더리 투자가 전략 결합 + 멀티모델, 자체 주장 승률 74% | 시그널 (주장 검증 필요) |

- **공통 주의**: README의 승률·수익률 주장은 *작성자 자체 백테스트*인 경우가 대부분. 본문 9.2(슬리피지)·9.6(환각) 함정을 그대로 적용해 회의적으로 검증.

---

## C. (신규 카테고리) MCP 생태계 — Claude/코딩 에이전트 직결 인프라

> 2025~2026년 사이 MCP(Model Context Protocol) 서버가 크립토 트레이딩 데이터·실행 레이어로 빠르게 표준화됐다. Claude Desktop·코딩 에이전트에서 자연어로 시장 데이터 조회·주문이 가능해지면서, "봇을 짜기 전에 MCP로 먼저 붙인다"는 패턴이 자리잡았다.

| MCP 서버 | 기능 | 체인/거래소 |
| --- | --- | --- |
| hyperliquid-mcp (Impa-Ventures / TradingBalthazar v6) | Hyperliquid 거래·전략 관리 온체인 툴 | Hyperliquid |
| jupiter-mcp (kukapay) | Jupiter Ultra API로 Solana 토큰 스왑 | Solana |
| crypto-indicators-mcp (kukapay) | 기술적 지표·전략을 에이전트에 노출 | 범용 |
| crypto-sentiment-mcp (kukapay) | 소셜·뉴스 실시간 센티먼트 | 범용 |
| SignalFuse MCP | 센티먼트·매크로 레짐·Hyperliquid 시장구조 융합 신호 | Hyperliquid 중심 |
| armor-crypto-mcp | 지갑 관리·스왑·멀티체인 전략 거래 | 멀티체인 |
| solscan-mcp / etherscan-mcp / evm-mcp-server | 온체인 데이터 자연어 조회 | Solana / EVM |
| anchor-x402-mcp | Base+Solana 페이-퍼-콜(USDC) 툴군, OFAC 스크리닝·서명 결정 증명 등 | Base/Solana |

- **강점**: 코드 작성 없이 Claude 등에 즉시 연결, x402 류 에이전트 결제와 결합 시 agent-commerce 실험 가능.
- **약점**: 서버별 보안·키 관리 편차 큼. **개인키/거래소 키를 MCP 서버에 넘기는 구성은 신중히** — 비수탁(non-custodial)·읽기 전용 우선, 주문 권한은 출금 불가 API 지갑으로 제한.
- **메타 자료**: TensorBlock/awesome-mcp-servers의 finance--crypto 문서가 최신 목록 추적에 유용.

---

## D. Hyperliquid 봇 플랫폼 (CloddsBot 외 보강)

본문 3장의 CloddsBot 외에, 2026년 Hyperliquid 전용·연동 플랫폼이 다양해졌다.

| 플랫폼 | 특징 | 수탁 구조 |
| --- | --- | --- |
| Katoshi AI | 노코드 AI 에이전트 생성, 자연어/Chat·API 호출, TradingView 웹훅, Trading Groups(타 유저 봇 팔로우) | 비수탁(API 지갑) |
| goodcryptoX | 30+ CEX + Hyperliquid + 멀티 스팟 DEX 통합 앱, 누적 $5B+ 거래량 | 비수탁(출금 불가 API) |
| Hummingbot (Hyperliquid 커넥터) | 오픈소스, 마켓메이킹·차익·DCA·그리드, 자체 호스팅 + 키 사용자 보유 | 비수탁(자기 호스팅) |

- **공통 강점**: 비수탁 구조 — 본문 9.4(CEX 의존성 리스크) 완화.
- **약점**: AI 라벨이지만 상당수는 rule-based 자동화에 가깝다. "AI" 마케팅과 실제 LLM 활용 깊이를 구분할 것.

---

## E. 학술 신작 (2025~2026)

| 자료 | 핵심 발견 | 출처/시점 |
| --- | --- | --- |
| Multi-Agent Crypto Portfolio (3-에이전트: Crypto/News/Trading) | 모달리티별 전문 에이전트 분업 + 3종 통신 구조로 BTC/ETH/SOL 포트폴리오 운용 | arXiv 2501.00826 (갱신 지속) |
| Resisting Manipulative Bots in Meme Coin Copy Trading | CoT 추론 멀티 에이전트로 밈코인 카피트레이딩의 조작 봇 저항 | WWW '26 (Dubai) |
| Bitcoin Explainable Zero-Shot Multi-Agent | Reddit 센티먼트 +23.30% total return, 뉴스 센티먼트는 노이즈 / slippage·fee 명시 백테스트 + G-EVAL | (본문 기수록, 재확인) |

- 흐름 요약: ① 단일 LLM·파인튜닝의 예측력 한계가 재확인되며 ② 멀티 에이전트·역할 분업으로 무게중심 이동, ③ 밈코인 카피트레이딩 같은 *적대적 환경*에서의 조작 저항이 새 연구 축으로 부상.

---

## F. 모델 지형 변화 (2026년 6월 기준)

본문의 모델 표기는 **Alpha Arena Season 1(2025-10) 시점**(GPT-5, Claude Sonnet 4.5, Gemini 2.5 Pro, Grok 4, DeepSeek V3.1, Qwen3 Max)임을 명시한다. 2026년 6월 현재 프레임워크들이 실제로 붙이는 프론티어는 아래로 이동했다.

| 진영 | Season 1 시점 | 2026-06 시점(프레임워크 채택 기준) |
| --- | --- | --- |
| Anthropic | Claude Sonnet 4.5 | Claude Opus 4.5 계열, Claude 4.6 |
| OpenAI | GPT-5 | GPT-5.2 / 5.4 / 5.5 계열 (mini 포함) |
| Google | Gemini 2.5 Pro | Gemini 3.x |
| 중국권 | DeepSeek V3.1, Qwen3 Max | DeepSeek/Qwen 최신, Kimi K2, GLM, MiniMax |

- **함의**: 모델 세대가 빨라도 본문 핵심 명제는 불변 — *모델 업그레이드가 곧 트레이딩 성과 개선은 아니다.* (Season 1에서 강한 GPT-5가 약한 모델보다 못한 결과를 낸 것이 대표 사례.) 신규 모델 도입 시 반드시 **자체 dry-run 재검증** 후 운용.
- **운용 팁**: deep/quick 모델 분리(TradingAgents 패턴)로 비용·latency 최적화 — 빠른 결정은 mini급, 깊은 분석은 플래그십.

---

## 본문 반영용 정정 표 (요약)

| 위치 | 기존 표기 | 정정/갱신 |
| --- | --- | --- |
| Executive Summary / 한글 요약 / 마지막 결론 | DeepSeek V3.1 +46% 우승, GPT-5 -75% | **Qwen3 Max 우승(+22.3%)**, DeepSeek 2위(피크 약 +48%, 종료 시 +5% 부근), GPT-5 약 **-63%** |
| 1장 Alpha Arena "결정적 데이터" | DeepSeek 1위, Qwen 2위, Claude 3위 | Qwen 1위, DeepSeek 2위, Claude는 약 -31%로 손실권 |
| 1장 Alpha Arena 활성도 | "Season 2 진행 중" | Season 1.5 종료, **Season 2 예고(인간 동반)**, Nof1 $15M 유치 |
| 모델 표기 전반 | GPT-5 / Sonnet 4.5 / Gemini 2.5 Pro | "Season 1 시점 기준" 주석 추가 + 2026-06 모델 지형 표 참조 |

---

## Disclaimer (갱신 유지)

- 본 갱신본의 모든 평가는 **2026년 6월 시점 공개 정보 기반 주관적 평가**다. 크립토+AI 분야는 주 단위로 변하므로 사용 전 각 레포의 마지막 커밋·이슈 활성도를 직접 확인할 것.
- 어떤 도구도 수익을 보장하지 않는다 — Alpha Arena의 GPT-5 약 -63%가 실제 데이터다.
- 아레나/프레임워크의 승률·수익률 주장은 상당수가 자체 백테스트이며, 카피트레이딩 영업과 결합된 경우 홍보 편향 가능.
- MCP 서버·봇 플랫폼에 **개인키/거래소 출금 권한**을 넘기는 구성은 신중히. 비수탁·읽기 전용·출금 불가 API 지갑을 우선.
- 미국 SEC/CFTC, 한국 금감원, EU MiCA 모두 AI 자동 트레이딩에 규제 적용 가능 — 타인 자금 운용은 라이선스 검토 필수.
- MEV의 sandwich attack 등 일부 전략은 윤리적 회색지대이며 일부 관할권에서 시장 조작으로 해석될 수 있다.
- 투자 결과 및 법적 리스크 책임은 사용자에게 있다.

---

*"Model intelligence is not trading intelligence."*
*"모델의 지능이 곧 트레이딩 지능은 아니다."*
— Alpha Arena Season 1 lesson (최종 우승: Qwen3 Max, +22.3%)
