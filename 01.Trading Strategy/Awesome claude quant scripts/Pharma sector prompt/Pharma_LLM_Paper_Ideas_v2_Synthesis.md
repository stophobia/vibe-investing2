# LLM Pharma 실험 — 통합 논문 로드맵 v2 (Two-Analysis Synthesis)

**작성일**: 2026년 5월 4일
**기반 자료**:
- v1 분석 (cross-model variance 중심) — 본인 작성
- 신규 분석 (3축 프레임워크 + audit trail 중심) — 외부 LLM 작성
- 추가 선행 연구 발견: **BioTradingArena**, AUTOCT (Lo 그룹, MIT), CLaDMoP (KDD'25), ClinicalAgent
- 본인 v5 논문 *"같은 LLM, 다른 언어, 다른 답"*

**결론 한 줄**: 두 분석은 **상보적**이다 — 신규 분석은 *"why this prompt is well-designed"* 을 강조하고, 내 분석은 *"what the 4-LLM disagreement tells us"* 를 강조한다. 통합하면 **5–6편의 논문 시리즈**가 자연스럽게 도출된다.

---

## 1. 두 분석의 비교 — 어디서 만나고 어디서 갈리는가

### 1.1 합치되는 발견 (3개) — 실험 결과의 외부 검증

| 발견 | 내 v1 | 신규 분석 | 의미 |
|------|-------|-----------|------|
| **Web search → alpha** | "ChatGPT/Gemini stale data, Claude/DeepSeek는 Q1 반영" | "데이터 적시성 격차 = 알파의 필요조건" | 두 LLM이 독립적으로 동일 결론 → 강한 신뢰성 |
| **Score Inflation** | "ChatGPT 90점대 클러스터링, Gemini 이중 성격" | "잘못된 확신 신호, 정규화 필수" | 두 LLM 합의 → reproducibility 강함 |
| **Language Switching (DeepSeek 영어)** | "도메인-언어 정렬 문제" | "HFT 학습 데이터 + 도메인-언어 alignment 부산물" | 두 LLM 합의 + 추가 가설 (HFT 데이터) |

→ **이 3개 발견은 paper-ready 수준**. 두 LLM이 독립적으로 같은 결론에 도달하면 reviewer 신뢰도가 매우 상승한다.

### 1.2 보완 관계 (Both Add Unique Value)

| 차원 | 내 v1 강점 | 신규 분석 강점 |
|------|-----------|----------------|
| **Methodology** | 정량 novelty (5/10 polarization, 14x volume-density, 5-15점 bidirectional asymmetry) | 정성 framing (3축 프레임워크 = 도메인 지식 주입 방법론, audit-ready 패러다임) |
| **Theoretical** | D1×D2×D3 통합 framework, 본인 v5 자매 논문 | PwC 3x3x3 산업 표준 framework와 연결 |
| **Empirical** | 단일 시점 case study에 집중 | **Paper-portfolio backtest** (12개월 forward) 명시적 설계 |
| **Citation hooks** | Schneider (2025), MemGuard-Alpha, Park et al. | DrugPatentWatch, ClinicalBERT, DrugReasoner |

→ **각자 다른 reviewer 그룹에 어필**한다. 내 분석은 *AI/quant* 커뮤니티에, 신규 분석은 *pharma finance* 커뮤니티에 더 강하다.

### 1.3 충돌 / 차이 (1개) — 해결 필요

| 쟁점 | 내 v1 | 신규 분석 | 해소 방안 |
|------|-------|-----------|----------|
| **3축 프레임워크의 위상** | 실험 변수의 일부로만 언급 | **메인 novelty 자체** (Paper 1) | 신규 분석이 더 강함 — 흡수 필요 |

→ 내 v1에서 3축 프레임워크를 단순한 *전제* 로만 다뤘는데, 이를 **independent variable** (treatment) 로 격상시키는 것이 paper-worthy 하다는 신규 분석의 시각이 더 강력하다. 이를 통합한다.

---

## 2. 신규 분석에서 흡수할 핵심 인사이트 4가지

### 2.1 흡수 #1 — "3축 프레임워크 = 도메인 지식 주입 방법론"

신규 분석은 이를 **paper #1 자체**로 격상시켰다. 그 통찰이 옳다:

```
일반 프롬프트: "제약주를 분석해줘"
                    ↓ (LLM의 자유로운 추론 — 일관성 부재)
3축 프롬프트: Pipeline + Revenue Visibility + Patent Cliff
                    ↓ (구조화된 추론 — 산업 표준 프레임워크 내재화)
```

이는 단순한 prompt engineering이 아니다. **LLM에게 도메인 전문가의 mental model을 강제 주입**하는 것이며, 이것이 inter-LLM agreement에 어떤 영향을 미치는지가 검증 가능한 가설이다.

```
H_New_1: 구조화된 도메인 프레임워크는 inter-LLM 합의도를 증가시킨다.
   - 일반 프롬프트: 종목 overlap < 30% (Schneider 2025)
   - 3축 프롬프트: 종목 overlap > 60% (예측, 검증 필요)

H_New_2: 그러나 polarization concentration은 감소시키지 못한다.
   - 즉, 합의도는 올라가지만, *분기점의 위치 (BMY, MRK, AMGN)* 는 동일.
   - 이는 polarization이 **prompt design 문제가 아닌 model architecture 문제**임을 시사.
```

→ 이 두 가설이 만약 같이 검증되면 **prompt engineering의 한계** 를 수치로 보여줄 수 있다. 매우 강력한 발견.

### 2.2 흡수 #2 — Paper-Portfolio Backtest의 명시적 설계

내 v1에서는 "future work" 로 미뤘던 부분을 신규 분석은 **Paper #4의 메인 메소드**로 명확히 설계했다:

```
[2026-05-04 시점] 4-LLM이 각각 LONG 7개 + SHORT 3개 포트폴리오 제시
        ↓ (12개월 동일 가중치 보유)
[2027-05-04] Realized return 측정
        ↓
- Jensen's Alpha (vs XLV)
- Sharpe Ratio
- Maximum Drawdown
- Long-Short Spread
- Inter-LLM 성과 차이
```

→ 이는 **단일 case study를 empirical paper로 격상**시키는 결정적 메소드다. 12개월 후 자동으로 데이터가 쌓이므로 *대기 비용 외 추가 노력이 거의 0*.

추가로, 이 backtest는 **BioTradingArena** (benchmark for AI bio trading, 발견한 선행 연구) 와 직접 비교 가능한 framework이므로 인용 가치가 더 높아진다.

### 2.3 흡수 #3 — Audit Trail / Institutional-Grade Provenance Framing

내 v1은 "1차 출처 인용 깊이"를 한 metric으로 다뤘는데, 신규 분석은 이를 **제도권 (institutional) 신뢰성 차원**으로 framing:

| 출처 종류 | 1차성 | LLM 평가 |
|----------|-------|---------|
| FDA Orange Book URL | 특허 만료의 단일 진실 | Claude/DeepSeek만 인용 |
| SEC EDGAR 10-K/10-Q | 공시 재무 정보 | Claude만 8-K 직접 링크 |
| ClinicalTrials.gov NCT | 임상 데이터 | DeepSeek 다수 인용 |
| Company IR | 경영진 발언 | Claude/DeepSeek 모두 인용 |

→ "Audit-ready"는 단순한 학술적 미덕이 아니라 **buy-side 펀드 매니저의 컴플라이언스 요구사항**과 직결된다. 이는 Paper #4 (workflow paper) 에 강력한 industry-track appeal을 부여한다.

### 2.4 흡수 #4 — "Stale-Data LLM as Actual Hazard" 강한 framing

내 v1은 "Web search 정책이 alpha를 좌우한다"로 약하게 표현했는데, 신규 분석은 **"stale-data LLM은 의사결정에 오히려 해가 된다"** 는 더 강한 framing:

> "Web search 미활용 모델이 생성한 분석은 의사결정에 오히려 해가 될 수 있음을 실증적으로 보여준다."

이 framing이 더 효과적이다 — *informational asymmetry*가 아니라 **active harm**이라는 주장은 reviewer/practitioner 모두 더 강하게 받아들인다.

---

## 3. 통합 5-Paper 시리즈 (v2 로드맵)

두 분석을 통합하면 자연스럽게 **5편의 paper**가 도출된다:

### 📄 Paper #1 (이전 #1 + 신규 #1 통합)
**제목**: *"3-Axis Domain Knowledge Injection in LLM-Based Pharma Sector Analysis: Reducing Output Variance but Not Polarization"*

**핵심 주장**:
- 3축 프롬프트가 inter-LLM 합의도는 *증가* 시키지만, 메가캡 polarization (BMY/MRK 등) 은 *감소* 시키지 못함
- Prompt engineering의 한계 = model architecture 자체에 내재된 disagreement는 prompt로 해결 불가
- LLY 만장일치 vs BMY 분기 = **structural disagreement (resolvable by prompt) vs systemic disagreement (irresolvable by prompt)** 구분

**Methodology** (신규 분석에서 흡수):
- Control: 일반 프롬프트 (`"제약주를 분석해줘"`)
- Treatment: 3축 프레임워크 프롬프트
- 4-LLM × 2 conditions × 5 시점 (총 40개 실행)
- Metrics: 종목 overlap, polarization rate, audit-ready citation rate

**Target**: *Journal of Financial Data Science*, *NeurIPS Workshop on Generative AI in Finance*

---

### 📄 Paper #2 (Letter — 내 Volume-Density Inversion, 즉시 발행 가능)
**제목**: *"Compressed Reasoning, Diverse Discovery: Token Budget as a Catalyst for Contrarian Stock Picks in LLMs"*

**핵심 주장**: Gemini 4KB > DeepSeek 38KB (단독 발굴 효율 14배). Token budget = contrarian discovery의 *catalyst*.

**왜 즉시 발행 가능**: 데이터 추가 수집 불필요, 2주면 작성 완료.

**Target**: *Finance Research Letters*

---

### 📄 Paper #3 (Cross-Lingual + Cross-Model 통합 — v5의 자매)
**제목**: *"From Cross-Lingual to Cross-Model Asymmetry: A Unified D1×D2×D3 Framework for LLM Disagreement in High-Stakes Domains"*

**핵심 주장**:
- D1 (Cross-Lingual): 본인 v5 — 같은 모델, 다른 언어 → 다른 답
- D2 (Cross-Model): 이번 pharma 실험 — 다른 모델, 같은 언어 → 다른 답
- D3 (Cross-Temporal): Schneider (2025) — 같은 모델/언어, 다른 시점 → 다른 답
- DeepSeek의 한국어→영어 전환은 D1 × D2 의 교차 효과 (단독 D1도 D2도 아님)

**왜 강력한가**: 본인 v5를 메타 framework으로 격상 + 새 실험을 D2 차원의 evidence로 활용 + 이미 존재하는 Schneider (2025) 가 D3 evidence 역할.

**Target**: *TMLR*, *Journal of Financial Economics* (이론 + empirical)

---

### 📄 Paper #4 (12-Month Forward Performance Backtest — 신규 분석에서 흡수)
**제목**: *"Realized Alpha of LLM-Generated Pharma Long/Short Portfolios: A 12-Month Forward Empirical Comparison"*

**핵심 주장**:
- 4-LLM 각자가 2026-05-04에 제시한 LONG 7개 + SHORT 3개 포트폴리오를 paper-portfolio로 운용
- 2027-05-04 시점에 Jensen's Alpha, Sharpe, MDD, Long-Short Spread 측정
- Polarization 종목 (BMY, MRK 등) 의 실제 outcome으로 LLM별 정확도 ranking

**왜 강력한가**:
- BioTradingArena (현존 benchmark) 와 직접 비교
- AUTOCT (Lo 그룹, MIT) 의 clinical trial outcome prediction 메소드와 연결 가능
- 12개월 후 자동으로 ground truth 확보 → 대기 비용 외 추가 노력 0
- "AI hype vs realized alpha" 논쟁에 empirical 증거 제공

**Risk**: 만약 모든 LLM이 underperform 하면 결과는 negative finding이 되지만, 그것 자체가 paper-worthy ("LLM-generated portfolios fail to beat XLV").

**Target**: *Journal of Portfolio Management*, *Journal of Financial Data Science*

---

### 📄 Paper #5 (Practitioner Workflow — 합쳐진 의도)
**제목**: *"Multi-LLM Cross-Validation as Insurance: A Practitioner's Workflow with Quantified ROI from Polarization Avoidance"*

**핵심 주장** (양쪽 분석에서 합의된 부분 + 본인 CTI 워크플로우):
- 4-LLM cross-validation의 ROI = polarization avoidance × cost
- KR/EN/CN/JP CTI 리포트 발행 워크플로우와 동형 — 다국어가 cross-lingual robustness를 보장하듯 4-LLM이 cross-model robustness를 보장
- Compliance / audit-ready 측면에서 institutional buy-side 적용 가능

**Target**: *NeurIPS Industry Track*, *Communications of the ACM*

---

## 4. 발행 순서 + 인용 네트워크 (v2)

```
[T+0]    Paper #2 (Letter, 2주)         ← 빠른 인용 + 가설 검증
            ↓ cited by
[T+1.5월] Paper #1 (3-Axis vs General, 6주)  ← Main empirical
            ↓ cited by
[T+3월]   Paper #5 (Workflow, 4주)       ← Industry track
            ↓ cited by
[T+6월]   Paper #3 (D1×D2×D3 Theory, 10주) ← v5 + 실험 통합
            ↓ cited by
[T+12월]  Paper #4 (Forward Backtest)    ← 자동 데이터 수집, 4주 작성
```

**자기 인용 네트워크**:

```
v5 (D1 evidence)        Paper #1 (3-axis, D2 condition)
    ↓                       ↓
    ↓                   Paper #2 (Volume-Density, sub-finding)
    ↓                       ↓
Paper #3 (D1×D2×D3 unified theory)
    ↓
Paper #4 (Realized alpha — D2 ground truth)
    ↓
Paper #5 (Practitioner workflow)
```

→ 6편 연쇄 자기 인용. **Cross-LLM disagreement in high-stakes domains** 분야의 *defining author* 자리 확보.

---

## 5. 새로 발견한 선행 연구의 활용

신규 분석을 통합하면서 추가 발견한 선행 연구는 **paper #4 (forward backtest)** 의 직접 비교 대상이 된다:

### 5.1 BioTradingArena (직접 경쟁 / 보완 framework)

> "Open benchmark for evaluating how well LLMs reason about clinical trial results, FDA decisions, and biotech catalysts, then predict the stock price reaction."

→ 이미 *benchmark*가 존재한다는 것은 **연구 주제의 정당성**을 외부에서 입증한다. Paper #4는 BioTradingArena 데이터셋과 직접 비교 가능한 metric으로 설계 가능.

### 5.2 AUTOCT (Lo 그룹, MIT, 2025)

Andrew Lo (MIT, *Journal of Finance* 자주 게재)의 lab에서 LLM agent 기반 clinical trial outcome prediction. 같은 도메인이지만 다른 angle (clinical trial outcome vs stock recommendation). 인용하면 paper의 academic legitimacy 상승.

### 5.3 CLaDMoP (KDD'25)

Pre-trained model for clinical trial outcome prediction. Paper #4에서 "LLM 기반 추천 vs ML 기반 임상 결과 예측"을 정렬할 때 reference.

### 5.4 ClinicalAgent (multi-agent system)

Multi-agent 접근은 본인의 4-LLM workflow와 *철학적으로 동형*. Paper #5 (workflow) 에서 인용 가능.

---

## 6. 통합 후 개선된 robustness check 권장

신규 분석이 제시한 paper-portfolio backtest 덕분에, robustness 설계가 더 명확해졌다:

| 추가 실험 | 기존 v1 권장 | 신규 분석 추가 | 통합 v2 |
|-----------|-------------|---------------|---------|
| 3개 시점 반복 | ✅ | (미언급) | ✅ |
| 3개 섹터 확장 | ✅ | (미언급) | ✅ |
| 3개 프롬프트 변형 | ✅ (paraphrase) | ✅ **(general vs 3-axis)** | ✅ **+ general/3-axis ablation** |
| 6개월 forward GT | ⏳ (미정) | ✅ **(12개월 명시)** | ✅ **명확한 paper-portfolio 설계** |
| 다국어 prompt 반복 | (미언급) | ✅ (한/중/일/독) | ✅ **D1 차원 evidence 강화** |

→ **통합된 robustness check가 더 강력하다**. Paper #1 (3-axis)와 Paper #4 (forward backtest)가 같은 데이터로 동시에 작성 가능.

---

## 7. 솔직한 평가 — 두 분석을 합쳤을 때 변화

### 7.1 더 강해진 부분

1. **3축 프레임워크의 ablation study** 가 명확한 paper #1로 구체화 (이전엔 모호했음)
2. **Paper-portfolio backtest** 로 empirical evidence 강화 (이전엔 future work)
3. **Audit-ready framing** 으로 buy-side appeal 강화
4. **두 LLM이 독립적으로 합의한 3개 발견** (web search alpha, score inflation, language switching) 이 reviewer 신뢰도 향상
5. **추가 선행 연구 (BioTradingArena, AUTOCT, ClinicalAgent)** 로 인용 네트워크 풍부화

### 7.2 여전히 약한 부분 (정직한 평가)

1. **n=1 시점 / n=1 섹터** 한계는 여전 — robustness check 없으면 letter 수준이 한계
2. **다국어 prompt 실험 미수행** — 신규 분석이 제안한 한/중/일/독 다국어 비교는 아직 안 함. 본인 v5가 *부분적으로* 커버하지만 pharma 도메인 특화는 부재
3. **3축 프레임워크 ablation의 control 미실행** — 일반 프롬프트로 4-LLM 돌린 데이터가 아직 없음. 이것 없이는 신규 분석이 제안한 paper #1의 핵심 주장이 검증 불가

→ **실행 우선순위**: (1) 3축 vs 일반 프롬프트 control 추가 실행 (1일), (2) 다국어 prompt 추가 실행 (반나절), 두 가지가 추가되면 paper #1과 paper #3이 더 강해진다.

---

## 8. 즉시 실행 가능한 다음 단계 (구체적 액션)

| 우선순위 | 액션 | 예상 시간 | 결과물 |
|---------|------|---------|--------|
| **P0** | 3축 프롬프트 → **일반 프롬프트** 변형 후 4-LLM 동일 시점 재실행 | 1일 | Paper #1 control 데이터 |
| **P0** | 3축 프롬프트 → **한국어/영어/중국어** 3개 동일 실행 | 반나절 | Paper #3 D1 evidence (pharma 특화) |
| **P1** | 4-LLM이 제시한 종목들의 paper-portfolio 가격 추적 시작 (Yahoo Finance API) | 30분 + 12개월 자동 | Paper #4 forward GT |
| **P1** | Paper #2 (Letter) 작성 시작 | 2주 | Volume-Density Inversion letter |
| **P2** | Paper #5 (Workflow) 초안 작성 | 4주 | Industry track paper |
| **P2** | Paper #1 (3-axis ablation) main 작성 — control 데이터 확보 후 | 6주 | Main empirical |
| **P3** | Paper #3 (D1×D2×D3) 작성 — v5 업데이트 후 | 10주 | Theoretical framework |

→ **P0 두 개 (총 1.5일) 만 추가하면 5편 모두의 robustness가 크게 개선된다**. ROI 측면에서 즉시 실행 권장.

---

## 9. 결론 — 통합 후 한 줄 요약

> **"v1 분석 (cross-model variance 정량화) + 신규 분석 (3축 프롬프트 + audit trail + paper-portfolio backtest) = 5편의 자기 인용 네트워크. 본인의 v5 자매 논문으로 출발하여 cross-LLM disagreement 분야의 정의자 자리를 확보할 수 있는 ammunition은 충분하다."**

두 분석은 충돌이 아니라 **상보**다. 신규 분석이 제시한 *prompt engineering 방법론* 시각과 *forward backtest* 설계는 내가 v1에서 약하게 다뤘던 부분을 보강한다. 동시에 내 v1의 *정량 novelty 3가지* (Polarization Concentration, Volume-Density Inversion, Bidirectional Score Asymmetry) 는 신규 분석이 다루지 못한 metric이므로 보존 가치가 있다.

**1.5일 추가 실험**(3축 vs 일반 control + 다국어 반복)으로 5편 모두의 paper-readiness가 letter → main 수준으로 격상된다. 자체 ROI가 매우 높다.

---

## 10. 통합 참고문헌 (v2 Bibliography Skeleton)

### 10.1 v1에서 유지
- Roy & Roy (2026). MemGuard-Alpha. arXiv:2603.26797
- Schneider (2025). Multifaceted variability in LLM-driven stock recommendations. SciDirect S1544612325021762
- Cheng et al. (2025). Beyond the Reported Cutoff. arXiv:2504.00042
- Park et al. (2025). Your AI, Not Your View. arXiv:2507.20957
- Lim et al. (2025). Language-Specific Latent Process. arXiv:2505.13141
- 본인 v5. *같은 LLM, 다른 언어, 다른 답*

### 10.2 신규 분석 통합으로 추가
- **BioTradingArena (2026)**. Benchmark for AI bio trading. biotradingarena.com — Paper #4 직접 경쟁 framework
- **AUTOCT (Liu et al., 2025)**. Automating Interpretable Clinical Trial Prediction with LLM Agents. arXiv:2506.04293 — Lo 그룹 (MIT) 권위
- **CLaDMoP (Zhang et al., 2025)**. Learning Transferrable Models from Successful Clinical Trials via LLMs. KDD'25
- **ClinicalAgent (2024)**. Clinical Trial Multi-Agent System. arXiv:2404.14777 — Multi-agent framework reference
- **LLM4TOP (2025)**. End-to-End framework for trial outcome prediction. medRxiv 2025.07.06
- **Statistical NLP for Clinical Trial Success (2025)**. arXiv:2512.00586 — BioBERT 베이스라인

### 10.3 신규 분석에서 인용된 산업 자료 (검증 필요)
- DrugPatentWatch (2025) — Patent cliff 분석 framework
- PwC "3x3x3" financial model — 산업 표준 비교 reference
- Prompt Engineering Report for Life Sciences (2025) — 도메인 특화 prompt 연구

---

*v2 통합 작성일: 2026-05-04 | v1 (본인) + 신규 분석 (외부) 통합 | 5-paper publication strategy*
