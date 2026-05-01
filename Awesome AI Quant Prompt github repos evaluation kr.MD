# AI/LLM 기반 퀀트 프롬프트 GitHub 레포 — 사용자 평가 및 신뢰성 분석

## *2026년 4월 30일 기준 검증된 데이터 종합*

---

> *"가장 많이 별 받은 repo가 가장 신뢰할 만한 repo는 아니다. Stars는 *마케팅 성공*을 측정하고, Citations는 *학술 영향*을 측정하며, Forks는 *실제 사용*을 측정한다. 세 지표를 분리해서 봐야 진짜 평가가 가능하다."*

---

## 들어가며 — 이 문서의 한계 명시

본 문서는 *"AI/LLM 기반 퀀트 프롬프트 전략"* 영역의 GitHub repo를 정리한 것입니다. 그러나 미리 짚어야 할 한계가 있습니다.

**첫째, "퀀트 프롬프트 전략" 카테고리 자체가 명확히 확립되지 않았습니다.** 이 영역은 다음의 *3개 인접 영역*이 겹치는 곳입니다:

1. **LLM-based Trading Agents** — TradingAgents, FinAgent 같은 multi-agent 프레임워크
2. **Financial LLM Foundation Models** — FinGPT, BloombergGPT 같은 도메인 특화 모델
3. **Awesome List + Curated Resources** — 큐레이션 + 학습 자료

본 문서는 *프롬프트 엔지니어링이 핵심 가치*인 repo를 우선하지만, 위 카테고리들도 모두 다룹니다. 각각 *역할이 다르므로 단순 비교는 부적절*합니다.

**둘째, 일부 데이터는 추정치입니다.** GitHub stars 수치는 시점에 따라 변하며, 본 문서의 stars 데이터는 2026년 2-4월 기준입니다. 정확한 현재 수치는 각 repo 페이지에서 직접 확인하시기 바랍니다.

**셋째, "사용자 평가"는 GitHub stars/forks와 학술 인용으로 구성됩니다.** 더 정성적인 평가 (실제 트레이더 만족도 등) 는 본 문서 범위 밖입니다.

---

## 평가 프레임워크

본 문서는 다음 4개 차원으로 각 repo를 평가합니다.

### 차원 1: 인지도 (Visibility)
- GitHub Stars (절대 수치)
- 성장 속도 (출시 후 stars/month)

### 차원 2: 학술 신뢰성 (Academic Credibility)
- arXiv 또는 peer-reviewed paper 동반 여부
- Google Scholar 인용 수 (가능한 경우)
- 저자/소속의 학술적 배경

### 차원 3: 실제 사용도 (Practical Adoption)
- Forks (실제 derivative 작업)
- Issues / PRs 활성도
- 최근 commit 빈도

### 차원 4: 신뢰성 위험 신호 (Trust Risk Signals)
- *과장된 수익률 주장* 여부
- *재정 자문* 가장 여부
- 명확한 disclaimer 존재
- 라이선스 명확성

---

## Tier 1 — 학술 + 실용 통합 최상위 (검증된 영향력)

### 1. TradingAgents (TauricResearch/TradingAgents)

**한 줄 요약**: UCLA, MIT 연구진의 multi-agent LLM 트레이딩 프레임워크. arXiv 논문 (2412.20138) 동반.

| 차원 | 평가 |
|------|------|
| Stars | 매우 높음 (수만 단위, 2024년 12월 출시 후 급성장) |
| 학술 신뢰성 | **상위** — arXiv paper, 7번 버전 업데이트, ICLR 후속 논문 (Trade in Minutes 2026) |
| 저자 배경 | UCLA, MIT 연구진 (Yijia Xiao, Edward Sun, Di Luo, Wei Wang) |
| 실제 사용도 | 매우 활발 — v0.2.4 까지 정기 업데이트, Docker 지원, 11개 LLM provider |
| 신뢰성 위험 | **낮음** — *"research purposes"* 명시, 트레이딩 권유 아님 |

**강점**:
- 학술 + 오픈소스의 모범 사례
- Fundamentals/Sentiment/News/Technical Analyst 4개 분석가 + Researcher + Trader + Risk Manager 7개 역할
- LangGraph 기반 modular 설계
- Bull/Bear 디베이트 메커니즘
- Cumulative Returns, Sharpe Ratio, MDD 모두 baseline 대비 개선 실증

**약점**:
- Sharpe Ratio 결과 *"too good to be true"* (저자 본인이 인정) — *"highest SR exceeds expected empirical range"*
- 3개월 backtest 한정 (2024 6-11월) — 시장 regime 일반화 어려움
- 일평균 11 LLM call + 20+ tool call — *비용 상당* (analysis당 ~$0.10 이상 추정)
- *"few pullbacks"* 시기에 backtest되어 *survivorship period* 위험

**실제 사용 권고**:
- 학습/연구 도구로 추천
- 실거래 적용은 *권장하지 않음* (저자 본인의 입장)
- LLM provider별 결과가 *상당히 다름* — Claude vs GPT-5 vs Gemini 비교 필요

---

### 2. FinGPT (AI4Finance-Foundation/FinGPT)

**한 줄 요약**: 콜럼비아 대학교 + NYU 상하이 연구진의 오픈소스 financial LLM 프로젝트.

| 차원 | 평가 |
|------|------|
| Stars | **18,500+** (검증됨) |
| Forks | **2,600+** |
| 학술 신뢰성 | **상위** — arXiv 2306.06031, 다수 후속 논문 |
| 저자 배경 | Hongyang Yang (AI4Finance Foundation), Xiao-Yang Liu (Columbia), Christina Dan Wang (NYU Shanghai) |
| 실제 사용도 | HuggingFace 모델 공개 (FinGPT v3.1, 3.2, 3.3) |
| 신뢰성 위험 | **낮음** — *"academic purposes"* 명시, 라이선스 MIT |

**강점**:
- 가장 인용 많이 받은 financial LLM open-source (BloombergGPT 의 오픈소스 대안)
- Llama2-13B 기반 LoRA fine-tuning — $4.10/GPU-hour 수준의 *재현 가능 비용*
- BloombergGPT (추정 비용 $260만) 대비 *수천 배 저렴*
- 다중 financial sentiment dataset에서 SOTA
- AI4Finance Foundation의 ecosystem (FinRL, FinRobot, FinNLP) 과 통합

**약점**:
- *프롬프트 엔지니어링*보다 *fine-tuning* 중심 — 이 문서 주제와 정확히 맞지 않음
- 2023-2024 모델 위주 — 최신 LLM (Claude 4.7, GPT-5.4, Gemini 2.5) 적용 부족
- Sentiment analysis 위주 — 실거래 의사결정까지 거리 있음

**실제 사용 권고**:
- *Financial sentiment analysis* 가 목적이면 최우선 선택지
- Trading agent 가 목적이면 TradingAgents 권장
- 두 repo 를 *조합*해서 사용 가능

---

## Tier 2 — Awesome List 큐레이션 (참고 자료)

### 3. wilsonfreitas/awesome-quant

**한 줄 요약**: GitHub 에서 가장 오래되고 종합적인 퀀트 큐레이션. *모든 영역* 다룸.

| 차원 | 평가 |
|------|------|
| Stars | 매우 높음 (수만 단위, 10년 이상 누적) |
| 학술 신뢰성 | 큐레이션이라 직접 평가 불가, 그러나 inclusion 자체가 신뢰 신호 |
| 실제 사용도 | 다수 정기 PR, 활발한 commit 이력 |
| 신뢰성 위험 | **낮음** — 큐레이션 표준 |

**강점**:
- Python, R, Julia, JavaScript, Rust, Java, C++, Haskell *언어별 분류*
- Trading & Backtesting, Market Data, Portfolio Optimization 등 *기능별 분류*
- 10년 이상 누적된 *생태계 사진*

**약점**:
- 너무 광범위 — *AI/LLM 프롬프트* 카테고리는 일부만 다룸
- 광고 형식의 *상업 서비스 inclusion* 증가 (KeepRule, ValueRay 등)
- 큐레이션 기준이 *명시적이지 않음*

---

### 4. leoncuhk/awesome-quant-ai

**한 줄 요약**: AI/ML 응용 퀀트에 *집중한* 큐레이션. *최근 LLM 트렌드* 잘 반영.

| 차원 | 평가 |
|------|------|
| Stars | 중간 (수백~수천) |
| 학술 신뢰성 | 큐레이션 — 학술 paper 인용 풍부 |
| 실제 사용도 | 활발한 업데이트 |
| 신뢰성 위험 | **낮음** |

**강점**:
- *AI-Agent Trading* 카테고리 명확히 분리
- HMM, Markov-Switching, Fuzzy Systems 등 *전통 ML* + *LLM 멀티에이전트* 통합
- Marcos López de Prado, Robert Carver 등 *고전 reference* 포함
- Efficient Market Hypothesis, Factor Validity 같은 *학술적 framework* 명시

**약점**:
- LLM-specific 깊이 부족 (TradingAgents 만 명시, 다른 framework 누락)
- 영어/중국어 혼재 — 가독성 일부 저하

---

### 5. georgezouq/awesome-ai-in-finance

**한 줄 요약**: AI 응용 finance 의 *광범위* 큐레이션. *Deep Learning* + *LLM* 통합.

| 차원 | 평가 |
|------|------|
| Stars | 높음 (수천 단위) |
| 학술 신뢰성 | 큐레이션 |
| 실제 사용도 | 활발 |
| 신뢰성 위험 | 중간 — *과장된 수익률 주장* repo도 일부 포함 |

**강점**:
- ChatGPT-powered 트레이딩 사례 다수
- FinGPT, BloombergGPT 등 financial LLM 카테고리 명확
- 도구/API 풍부

**약점**:
- *"500% returns"* 같은 sensational 헤드라인 inclusion
- 일부 repo 의 *재현 불가능 결과* 검증 안 됨
- *"AI Quant Agents"* 같은 모호한 분류

---

### 6. Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers

**한 줄 요약**: LLM 기반 퀀트 트레이딩 *논문* 만 모은 큐레이션.

| 차원 | 평가 |
|------|------|
| Stars | 중간 |
| 학술 신뢰성 | **최상** — 논문 only |
| 실제 사용도 | 학자/연구자에게 유용 |
| 신뢰성 위험 | **매우 낮음** |

**강점**:
- arXiv, EMNLP, ICLR, NeurIPS, KDD 등 *peer-reviewed* paper 위주
- *완전한 논문 inventory* — TradingAgents, AlphaAgents, QuantAgent, Alpha-GPT, FactorMAD, FinAgent 등
- *카테고리별 분류* (Multi-agent, Factor Mining, Reasoning, Benchmark)

**약점**:
- *코드/실용 도구* 가 아닌 *논문 only*
- 논문 검증 없이 *나열만*
- *최신 논문 수집 속도*가 빠르지만 *quality filter* 없음

---

## Tier 3 — 도메인 특화 / 실험적 (선별적 활용)

### 7. LLMQuant 그룹 (LLMQuant/quant-mind 등)

**한 줄 요약**: 중국 + 글로벌 퀀트 커뮤니티의 *AI4Quant 솔루션* 시리즈.

| 차원 | 평가 |
|------|------|
| Stars | 작음~중간 (151 stars for quant-mind) |
| 학술 신뢰성 | 중간 — *production-ready* 강조 |
| 실제 사용도 | MCP server 통합 등 *실용 지향* |
| 신뢰성 위험 | 중간 — *상업 서비스 연계* 가능성 |

**강점**:
- 중국 vs 해외 퀀트 *정보 격차 해소* 미션 명확
- MCP (Model Context Protocol) 활용한 *최신 통합*
- 한국어/일본어/중국어 등 *비영어 사용자* 친화

**약점**:
- 영어 문서 부족
- 실제 backtest 결과 검증 어려움
- *"production-ready"* 라는 주장의 *근거 불충분*

---

### 8. FinAgent / TradingAgents 후속 paper들

**관련 논문/repo**:
- AlphaAgents (25-08): Equity Portfolio Construction
- QuantAgent (SBU, 25-09): High-Frequency Trading
- R&D-Agent-Quant (CMU+MSRA, NeurIPS 2025)
- FactorMAD (THU, ICAIF 2025)
- QuantaAlpha (SUFE, 26-02)

**공통 평가**:
- 학술 신뢰성: 높음 (대학 연구 그룹)
- 실용성: *재현 어려움* — 대학 연구 환경 의존
- 권고: *학술 reference* 로 사용, *실거래 도구* 로는 부적합

---

## 위험 신호 — 피해야 할 패턴

본 문서의 가장 중요한 가치는 *피해야 할 repo* 의 *공통 패턴* 명시입니다.

### Red Flag 1: 과장된 수익률 주장

**패턴**: *"ChatGPT trading algorithm delivered 500% returns"* 같은 헤드라인

**진단**:
- *Backtest period* 가 매우 짧음 (보통 1-3개월)
- *Cherry-picked* 시기 (강세장 only)
- *슬리피지/수수료/세금* 미반영
- *Out-of-sample* 검증 없음

**조치**: 해당 repo 의 *GitHub Issues* 에서 *"can't reproduce"* 또는 *"different results"* 언급 검색. 다수면 신뢰 안 함.

### Red Flag 2: 라이선스 모호성

**패턴**: 라이선스 미지정 또는 *commercial use 제한* 모호

**진단**: *"All rights reserved"* + *오픈소스 표방* = 사용자에게 법적 리스크

**조치**: MIT, Apache 2.0, BSD 같은 명확한 OSI-approved 라이선스만 사용

### Red Flag 3: Disclaimer 부재

**패턴**: *"financial advice"* 명시적 부정 없음

**진단**: 미국, EU, 한국 모두 *unlicensed financial advice* 는 법적 위험

**조치**: 신뢰할 만한 repo 는 항상 다음 명시:
> *"This software is for research/educational purposes only. Not financial advice."*

### Red Flag 4: 활성도 부족

**패턴**: 마지막 commit *6개월 이상 전*

**진단**: 
- Crypto 시장: 6개월이면 *영원*
- Stock 시장: 1년 이상 미업데이트도 가능
- LLM 의존 repo: *3개월* 이상 미업데이트면 *모델 deprecation* 위험

### Red Flag 5: 익명 저자

**패턴**: README 에 저자 정보 없음, 단일 GitHub 계정 + 다른 활동 없음

**진단**: 학술 신뢰성 검증 불가, *책임 추적 불가*

**조치**: 익명 저자 repo 는 *코드만* 참고, *결론은 신뢰 안 함*

---

## 실용적 의사결정 가이드

### "내가 어떤 목적으로 사용하는가" 에 따른 권고

#### 목적 1: LLM trading agent 학습
**1순위**: TradingAgents (TauricResearch)
**2순위**: AI4Finance Foundation 의 FinRL + FinGPT 조합
**비고**: 두 repo 를 *조합*해서 fine-tuned LLM + RL 통합 가능

#### 목적 2: Financial sentiment analysis
**1순위**: FinGPT (AI4Finance Foundation)
**2순위**: HuggingFace 의 FinBERT 변종들
**비고**: FinGPT v3.3 (Llama2-13B) 가 가장 강력

#### 목적 3: 학술 paper 발표용 reference
**1순위**: Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers
**2순위**: 각 paper 의 official GitHub repo 직접 확인
**비고**: 인용 시 *arXiv version* + *commit hash* 명시

#### 목적 4: 큐레이션 + 학습 자료
**1순위**: wilsonfreitas/awesome-quant (광범위)
**2순위**: leoncuhk/awesome-quant-ai (AI 특화)
**비고**: *광고/상업 서비스* inclusion 주의

#### 목적 5: 한국어 자료
**현실**: 한국어 *AI/LLM 퀀트 프롬프트* repo 는 매우 드뭅니다. 대부분 영어 학습 후 번역 필요.

---

## 한국 시장 관점의 추가 평가

### 한국 거주자가 사용 시 고려사항

**기술적 측면**:
- 대부분 repo 가 *미국 주식 (S&P 500, NASDAQ)* 중심
- 한국 주식 (KOSPI, KOSDAQ) 데이터는 *별도 통합 필요*
- yfinance, Alpha Vantage 같은 미국 데이터 API 위주

**법적 측면**:
- 한국 자본시장법상 *unlicensed financial advice* 위험
- *backtested 수익률* 을 마케팅으로 사용 시 위반 가능
- *AI 추천* 으로 운용업 영위 시 *투자자문업 등록* 필요

**문화적 측면**:
- 한국 학자가 만든 LLM finance repo 는 매우 드묾
- 한국 trading firm (NHN, 카카오, 토스, 각 증권사) 의 *오픈소스 기여 거의 없음*
- 한국어 documentation 자료 매우 제한적

### 한국에서 *카테고리가 비어 있는* 영역

다음 영역은 한국에서 *경쟁 repo 가 거의 없습니다*:

1. *한국어 financial LLM prompt 큐레이션*
2. *한국 주식 LLM 분석 framework*
3. *한국 거래소 (Upbit, Bithumb) crypto LLM 통합*
4. *KOSPI/KOSDAQ multi-agent trading*
5. *한국 거주자 대상 외환거래법 준수 LLM 도구*

이 영역은 향후 *한국인 개발자/연구자가 진입하기 좋은 niche* 입니다.

---

## 종합 평가 요약

### 신뢰성 + 영향력 매트릭스 (개인적 평가)

```
              학술 신뢰성 ↑
                 |
   FinGPT *      |    * TradingAgents
                 |
                 |
   awesome-      |    * Tom-roujiang
   quant-ai *    |       (papers only)
                 |
   ----------------------------------- 인지도 →
                 |
                 |
   LLMQuant *    |    * awesome-quant
                 |       (general)
                 |
                 |    * georgezouq/awesome-ai
   학술 신뢰성 ↓
```

### 한 줄 평가

| Repo | 한 줄 평가 |
|------|-----------|
| TradingAgents | "학술 + 실용 통합의 모범. 단, 실거래 적용은 신중" |
| FinGPT | "Sentiment analysis 의 사실상 표준" |
| awesome-quant | "퀀트 생태계의 *전화번호부*" |
| awesome-quant-ai | "AI 특화 큐레이션 중 가장 정제됨" |
| awesome-ai-in-finance | "광범위하지만 quality filter 부족" |
| Awesome-LLM-Quant-Papers | "학자에게 필수, 실무자에게는 부족" |
| LLMQuant 그룹 | "중국 시장 진입에 유용, 검증 필요" |

---

## 본 문서의 한계와 면책

1. **완전성 한계**: 위에 언급되지 않은 우수한 repo 가 다수 존재. 본 문서는 *대표적 사례*만 다룹니다.
2. **시점 한계**: 2026년 4월 30일 기준. *6개월 후 panorama 가 크게 변할 가능성* 있음.
3. **검증 한계**: 일부 stars 수치는 검색 결과 기반으로 *±20% 오차* 있을 수 있음. 정확한 수치는 GitHub 직접 확인.
4. **편향**: 영어권 repo 위주. 일본어/중국어/한국어 repo 는 부분적 다룸.
5. **개인 평가**: *"신뢰성 위험"*, *"실제 사용 권고"* 는 일반적 기준에 따른 평가이며 *절대적 판단* 아님.

---

## References

### 검증된 GitHub Repos

- TradingAgents: github.com/TauricResearch/TradingAgents
- FinGPT: github.com/AI4Finance-Foundation/FinGPT
- awesome-quant (Wilson Freitas): github.com/wilsonfreitas/awesome-quant
- awesome-quant-ai (leoncuhk): github.com/leoncuhk/awesome-quant-ai
- awesome-ai-in-finance (georgezouq): github.com/georgezouq/awesome-ai-in-finance
- Awesome-LLM-Quantitative-Trading-Papers: github.com/Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers
- AI4Finance Foundation: github.com/ai4finance-foundation
- LLMQuant: github.com/LLMQuant
- Awesome-Quant-Machine-Learning-Trading: github.com/grananqvist/Awesome-Quant-Machine-Learning-Trading

### 학술 paper

- TradingAgents (Xiao et al., 2024): arXiv 2412.20138
- FinGPT (Yang et al., 2023): arXiv 2306.06031
- Trade in Minutes (TJU+MSRA, ICLR 2026)
- AlphaAgents (2025): arXiv 25-08
- QuantAgent (SBU, 2025)
- R&D-Agent-Quant (CMU+MSRA, NeurIPS 2025)
- FactorMAD (THU, ICAIF 2025)

### 시리즈 연계

- vibe-investing 시리즈: github.com/gameworkerkim/vibe-investing
- SSRN 6632838 — The 72-Hour Shock
- Awesome Claude Quant Scripts (vibe-investing 의 자매 프로젝트)

---

## Disclaimer

본 문서는 **연구·교육 목적의 큐레이션**입니다.

- 본 문서는 *투자 권유가 아닙니다*
- 각 repo 의 stars/forks 수치는 *시점에 따라 변동*
- *"신뢰성"* 평가는 일반적 기준이며, 본인 use case 에 따라 다를 수 있음
- 모든 LLM/AI 도구는 *backtest 결과가 실거래 수익을 보장하지 않음*
- 한국 거주자: *unlicensed financial advice* 위반 가능성 별도 확인 필요
- 본 문서를 기반으로 한 투자 결정의 책임은 본인에게 있음

> *Past performance does not guarantee future results.*

---

## 작성 정보

**작성일**: 2026년 4월 30일
**저자**: 김호광 (Dennis Kim / HoKwang Kim) — Independent Researcher · Betalabs Inc. CEO
**시리즈**: vibe-investing — Investment Idea Column
**ORCID**: [0009-0002-0962-2175](https://orcid.org/0009-0002-0962-2175)
**GitHub**: [vibe-investing](https://github.com/gameworkerkim/vibe-investing)
