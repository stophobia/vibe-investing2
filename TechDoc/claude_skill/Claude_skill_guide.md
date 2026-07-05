# Claude Skill 가이드

> Anthropic Agent Skills를 활용해 나만의 반복 가능한 워크플로우를 만드는 방법
> 참고: [anthropics/skills 저장소](https://github.com/anthropics/skills) · [Agent Skills 표준](http://agentskills.io)

---

## 1. Skill이란 무엇인가?

Skill은 Claude가 특정 작업을 **반복 가능한 방식**으로 더 잘 수행하도록 가르치는 **지침·스크립트·리소스가 담긴 폴더**입니다. Claude는 작업 상황에 맞춰 Skill을 동적으로 로드합니다.

한 줄 요약하면 잘 쓰는 기능을 모음집으로 만든 것이다.

핵심 아이디어는 단순합니다.

- **프롬프트를 매번 다시 쓰지 않는다.** 잘 다듬은 워크플로우를 폴더 하나에 담아두면, Claude가 관련 작업을 만날 때마다 그 지침을 따른다.
- **점진적 로딩(Progressive Disclosure).** Skill의 이름과 설명(description)만 항상 컨텍스트에 상주하고, 본문과 번들 리소스는 필요할 때만 로드된다. 컨텍스트를 아끼면서도 깊은 전문성을 담을 수 있다.
- **LLM은 엑셀이지 오라클이 아니다.** Skill은 이 원칙의 실무적 구현이다 — 모델에게 "알아서 잘"을 기대하는 대신, 검증된 절차와 체크리스트를 명시적으로 주입한다.

---

## 2. 저장소 구조

[anthropics/skills](https://github.com/anthropics/skills) 저장소 구성

| 디렉토리 | 설명 |
|---|---|
| `./skills` | 실제 Skill 예제 (Creative & Design, Development & Technical, Enterprise & Communication, Document Skills) |
| `./spec` | Agent Skills 표준 명세 |
| `./template` | 새 Skill을 만들 때 사용하는 템플릿 |

특히 `skills/docx`, `skills/pdf`, `skills/pptx`, `skills/xlsx`는 Claude의 실제 문서 생성 기능을 구동하는 프로덕션 Skill로, 복잡한 Skill을 설계할 때 좋은 참고 자료입니다(소스 공개, 오픈소스 아님).

---

## 3. Skill의 해부학

```
skill-name/
├── SKILL.md            (필수)
│   ├── YAML 프론트매터  (name, description 필수)
│   └── Markdown 지침
└── 번들 리소스          (선택)
    ├── scripts/        - 결정적/반복 작업용 실행 코드
    ├── references/     - 필요할 때만 컨텍스트에 로드되는 문서
    └── assets/         - 출력에 사용되는 파일 (템플릿, 아이콘, 폰트)
```

### 프론트매터 필수 항목

| 항목 | 설명 |
|---|---|
| `name` | 고유 식별자 (소문자, 띄어쓰기는 하이픈) |
| `description` | **트리거 메커니즘의 핵심.** 무엇을 하는지 + 언제 사용해야 하는지 모두 여기에 |

### 설계 원칙

1. **description은 약간 "적극적으로"** — Claude는 Skill을 덜 쓰는(undertrigger) 경향이 있으므로, "사용자가 X, Y, Z를 언급하면 명시적으로 요청하지 않아도 이 Skill을 사용하라"처럼 트리거 조건을 구체적으로 나열한다.
2. **SKILL.md 본문은 500줄 이하** — 넘어가면 `references/`로 계층을 분리하고 언제 읽을지 명확히 안내한다.
3. **결정적 작업은 스크립트로** — 계산, 파싱, API 호출처럼 매번 같아야 하는 작업은 LLM의 자유 생성에 맡기지 말고 `scripts/`에 코드로 고정한다.
4. **도메인이 여러 개면 variant별로 분리** — 예: `references/krx.md`, `references/us-market.md`처럼 시장별 참조 파일을 나누면 Claude가 필요한 것만 읽는다.

---

## 4. 사용 방법

### Claude Code

```bash
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

설치 후 자연어로 언급만 하면 됩니다:
> "퀀트 시황 스킬로 오늘 장 요약해줘"

개인 Skill은 `~/.claude/skills/` 에 폴더째 넣으면 됩니다.

### Claude.ai (웹/앱)

유료 플랜에서 Settings → Capabilities에서 Skill 업로드가 가능합니다. `.skill` 패키지 또는 SKILL.md가 담긴 zip을 올리면 됩니다. ([공식 가이드](https://support.claude.com/en/articles/12512180-using-skills-in-claude))

### Claude API

사전 구축 Skill 사용 또는 커스텀 Skill 업로드가 가능합니다. ([Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill))

---

## 5. 예제 ①: 퀀트 관점 데일리 시황 요약 스킬

매일 아침 "오늘 시황 요약해줘" 한 마디로, 뉴스 나열이 아닌 **팩터·수급·변동성 관점의 구조화된 브리핑**을 받는 스킬입니다.

### 폴더 구조

```
quant-market-brief/
├── SKILL.md
└── references/
    ├── factor-checklist.md    # 점검할 팩터 목록과 해석 기준
    └── output-template.md     # 브리핑 출력 템플릿
```

### SKILL.md

```markdown
---
name: quant-market-brief
description: >
  오늘의 주식 시황을 퀀트 관점에서 요약하는 스킬. 사용자가 "시황", "오늘 장",
  "마켓 브리핑", "장 요약", "오늘 코스피/나스닥 어때" 등을 언급하면
  명시적으로 "퀀트"라는 단어가 없어도 반드시 이 스킬을 사용하라.
  단순 뉴스 나열이 아니라 팩터·변동성·수급 프레임으로 구조화된 브리핑을 생성한다.
---

# Quant Market Brief

## 목적
개별 뉴스가 아닌 시장 구조(레짐)를 읽는다. "무슨 일이 있었나"가 아니라
"팩터·변동성·수급 관점에서 시장이 어느 레짐에 있고, 무엇이 바뀌었나"에 답한다.

## 워크플로우

### 1단계: 데이터 수집 (웹 검색 필수)
다음을 반드시 검색으로 확인한다. 학습 데이터의 기억으로 답하지 않는다:
- 주요 지수 종가/등락률: KOSPI, KOSDAQ, S&P 500, NASDAQ, 필라델피아 반도체
- 변동성: VIX 레벨과 전일 대비 변화, VKOSPI
- 금리/환율: 미국 10년물, 원/달러, 달러인덱스(DXY)
- 수급: 외국인/기관 순매수 (KRX), 주요 섹터 ETF 자금 흐름
- 크립토(선택): BTC, 김치프리미엄 — 위험선호 프록시로만 사용

### 2단계: 팩터 렌즈 적용
references/factor-checklist.md 를 읽고 다음을 판정한다:
- 모멘텀 vs 리버설: 최근 주도주가 계속 가는가, 꺾이는가
- 성장 vs 가치: 금리 방향과 스타일 로테이션 정합성
- 대형 vs 소형: 위험선호 확산 여부
- 퀄리티/로우볼: 방어 팩터로의 자금 이동 여부

### 3단계: 레짐 판정
아래 중 하나로 명시적으로 분류하고 근거를 한 줄로 단다:
Risk-On / Risk-Off / Rotation(로테이션) / Chop(방향성 부재)

### 4단계: 출력
references/output-template.md 템플릿을 따른다. 반드시 포함:
1. 한 줄 레짐 판정 (맨 위)
2. 숫자 테이블 (지수/변동성/금리/환율/수급)
3. 팩터 스코어카드 (각 팩터: 강세/중립/약세 + 근거 1줄)
4. "어제와 달라진 것" 섹션 — 델타에 집중
5. 반증 조건 — 오늘 판정이 틀렸다면 무엇이 관측될 것인가

## 가이드라인
- 예측하지 않는다. 관측된 사실 → 팩터 해석 → 조건부 시나리오 순서를 지킨다.
- 모든 수치에 출처와 기준 시각을 명기한다.
- 확신도를 상/중/하로 표기한다. 데이터가 엇갈리면 "엇갈림"이라고 쓴다.
- 투자 권유 표현("사라/팔아라")을 쓰지 않는다. 판단 재료만 제공한다.
```

### references/factor-checklist.md (발췌)

```markdown
# 팩터 점검 체크리스트

## 모멘텀
- 신호: 최근 1개월 상위 수익률 섹터가 당일에도 상대강세인가
- 강세 판정: 주도 섹터 상대수익률 > 시장 && 거래대금 유지
- 붕괴 신호: 주도주 급락 + 거래량 급증 (분산 매도)

## 변동성 레짐
- VIX < 15: 저변동성 (캐리/모멘텀 유리)
- VIX 15–25: 중립
- VIX > 25: 고변동성 (로우볼/퀄리티, 포지션 축소 검토 구간)
- 주의: VIX '레벨'보다 '변화율'이 단기 신호로 유효
```

---

## 6. 예제 ②: 포트폴리오 데일리 모니터링 & 평가 스킬

내 포트폴리오를 등록해두고, **하루 한 번** 변동이 발생하면 퀀트 관점 + 시장 뉴스 + SNS 센티먼트를 종합해 "투자에 반영할 수 있는 형태"로 평가하는 스킬입니다.

핵심 설계 포인트:

- **포트폴리오는 `assets/portfolio.json`에 상태로 저장** — 매번 다시 입력하지 않는다
- **변동 트리거 규칙을 코드/명세로 고정** — "변동이 생겼다"의 정의를 LLM 재량에 맡기지 않는다
- **3개 정보원(퀀트/뉴스/SNS)을 분리 수집 후 교차검증** — 하나의 소스가 결론을 지배하지 못하게 한다 (멀티소스 위원회 방식)

### 폴더 구조

```
portfolio-daily-review/
├── SKILL.md
├── assets/
│   └── portfolio.json         # 보유 종목·수량·평단·리스크 한도
├── references/
│   ├── trigger-rules.md       # "변동"의 정량적 정의
│   ├── sentiment-guide.md     # SNS 센티먼트 해석 시 주의사항
│   └── action-framework.md    # 평가 → 액션 후보 매핑 기준
└── scripts/
    └── check_triggers.py      # 가격 변동/한도 위반 판정 스크립트 (선택)
```

### assets/portfolio.json

```json
{
  "base_currency": "KRW",
  "last_review": "2026-07-04",
  "risk_limits": {
    "single_position_max_pct": 20,
    "daily_drawdown_alert_pct": -3.0,
    "portfolio_drawdown_alert_pct": -5.0
  },
  "positions": [
    { "ticker": "005930.KS", "name": "삼성전자", "qty": 100, "avg_price": 72000, "thesis": "HBM 사이클" },
    { "ticker": "NVDA",      "name": "엔비디아", "qty": 10,  "avg_price": 118.5, "thesis": "AI 인프라 capex" },
    { "ticker": "BTC",       "name": "비트코인", "qty": 0.5, "avg_price": 61000000, "thesis": "매크로 헤지" }
  ]
}
```

### SKILL.md

```markdown
---
name: portfolio-daily-review
description: >
  사용자의 투자 포트폴리오를 하루 한 번 점검하고, 사전 정의된 변동 트리거가
  발동하면 퀀트 분석·시장 뉴스·SNS 센티먼트를 종합해 투자 판단 재료를 생성하는
  스킬. 사용자가 "포트폴리오 점검", "내 계좌", "오늘 리뷰", "보유 종목 어때",
  "리밸런싱" 등을 언급하거나 데일리 체크를 요청하면 반드시 이 스킬을 사용하라.
  포트폴리오 상태는 assets/portfolio.json 에서 읽는다.
---

# Portfolio Daily Review

## 목적
감정이 아닌 규칙으로 포트폴리오를 점검한다. 트리거 미발동이면 "이상 없음"
한 줄로 끝내고, 발동 시에만 3-소스 종합 평가를 수행한다.

## 워크플로우

### 0단계: 상태 로드
assets/portfolio.json 을 읽는다. last_review가 오늘이면
"오늘 리뷰는 이미 완료됨"을 알리고 재실행 여부를 확인한다 (하루 1회 원칙).

### 1단계: 시세 갱신 및 트리거 판정
각 포지션의 현재가를 웹 검색으로 확인하고, references/trigger-rules.md 의
규칙으로 판정한다. 요약:
- 개별 종목 일간 등락 ±3% 이상
- 포트폴리오 전체 평가액 일간 ±2% 이상
- risk_limits 위반 (단일 종목 비중 초과, 손실 한도 도달)
- 보유 종목 관련 중대 뉴스 (실적, 규제, 해킹/보안사고, 상장폐지 이슈)

**트리거 미발동 시**: 현재가 테이블 + "트리거 없음, 액션 불필요" 로 종료.
불필요한 분석을 생성하지 않는다.

### 2단계: 3-소스 수집 (트리거 발동 종목만)
각 소스를 독립적으로 수집하고 서로 섞지 않는다:

[A] 퀀트 관점
- 해당 종목의 팩터 상태: 모멘텀(1M/3M), 섹터 상대강도, 변동성 변화
- 시장 레짐과의 정합성 (quant-market-brief 스킬이 있으면 그 결과 재사용)

[B] 시장 뉴스
- 웹 검색으로 트리거 원인 뉴스를 특정한다. 1차 출처(공시, 실적 발표,
  규제기관 발표) 우선. 추측성 기사와 팩트를 구분 표기한다.

[C] SNS 센티먼트
- X(트위터), 레딧, 국내 커뮤니티의 반응 방향과 강도를 웹 검색으로 파악.
- references/sentiment-guide.md 를 반드시 먼저 읽는다. 핵심:
  SNS는 역지표일 수 있다. 극단적 쏠림(공포/환희)은 그 자체로 신호이며,
  방향 신호로 그대로 쓰지 않는다.

### 3단계: 교차검증 및 종합 평가
세 소스의 방향이 일치하는지 매트릭스로 정리한다:

| 소스 | 방향 | 강도 | 핵심 근거 |
|---|---|---|---|
| 퀀트 | 부정 | 중 | 모멘텀 꺾임 + 섹터 상대약세 |
| 뉴스 | 부정 | 강 | 실적 가이던스 하향 (1차 출처) |
| SNS  | 극단 공포 | 강 | 역지표 가능성 표기 |

- 3개 일치 → 신뢰도 높음
- 2:1 분열 → 소수 의견의 근거를 반드시 본문에 남긴다
- 뉴스(팩트)와 퀀트(가격행동)가 충돌하면 그 사실 자체를 강조한다

### 4단계: 액션 후보 제시
references/action-framework.md 기준으로 다음 형식을 지킨다:
- 액션 후보: 유지 / 비중축소 / 비중확대 / 손절 검토 / 추가 관찰 중 택1~2
- 각 후보의 근거와 반대 논거를 모두 명시
- 반증 조건: "X가 관측되면 이 평가는 무효" 를 반드시 포함
- 최종 결정은 사용자 몫임을 명시. 매수/매도 지시어를 쓰지 않는다.

### 5단계: 상태 갱신
portfolio.json 의 last_review 를 오늘 날짜로 갱신하고,
리뷰 요약을 로그로 남긴다 (다음 리뷰 때 "어제와의 델타" 계산에 사용).

## 가이드라인
- 트리거 없으면 침묵한다. 매일 장문의 분석을 쏟아내는 것은 노이즈다.
- 세 소스의 가중치를 임의로 정하지 않는다. 불일치는 불일치로 보고한다.
- SNS 인용 시 개별 계정을 특정하지 않고 집계된 방향/강도만 다룬다.
- 모든 수치에 조회 시각을 명기한다.
```

### references/trigger-rules.md (발췌)

```markdown
# 변동 트리거 정의

"변동이 생겼다"는 다음 정량 조건 중 하나 이상 충족을 의미한다.
LLM의 주관적 판단("좀 많이 빠진 것 같다")을 트리거로 쓰지 않는다.

| 트리거 | 조건 | 우선순위 |
|---|---|---|
| T1 개별 급변동 | 종목 일간 등락 |±3%| 이상 | 중 |
| T2 포트폴리오 변동 | 전체 평가액 일간 |±2%| 이상 | 상 |
| T3 리스크 한도 | risk_limits 항목 위반 | 최상 |
| T4 이벤트 | 실적/규제/보안사고/상폐 관련 1차 출처 뉴스 | 상 |
| T5 변동성 점프 | 종목 내재/역사 변동성 전일 대비 +50% | 중 |

복수 트리거 동시 발동 시 우선순위 높은 것부터 보고한다.
```

### 실행 예시 (Claude Code)

```
> 오늘 포트폴리오 리뷰해줘

[portfolio-daily-review 스킬 발동]
1. portfolio.json 로드 → 3개 포지션
2. 시세 검색 → NVDA -4.2% (T1 발동), 나머지 트리거 없음
3. NVDA에 대해 퀀트/뉴스/SNS 3-소스 수집
4. 교차검증 매트릭스 + 액션 후보 + 반증 조건 출력
5. last_review 갱신
```

---

## 7. 두 스킬을 연결하기

두 스킬은 독립적으로도 작동하지만, 함께 설치하면 시너지가 생깁니다:

```
아침 루틴:
1. quant-market-brief  → 시장 레짐 판정 (Risk-On / Off / Rotation / Chop)
2. portfolio-daily-review → 그 레짐을 컨텍스트로 개별 포지션 평가
   (SKILL.md 2단계 [A]에서 "quant-market-brief 결과 재사용" 명시)
```

이런 스킬 간 참조가 Skills 시스템의 실전 활용 패턴입니다 — 각 스킬은 작고 단일 책임을 갖되, 워크플로우 수준에서 조합됩니다.

---

## 8. 만들 때 흔한 실수

| 실수 | 교정 |
|---|---|
| description에 기능만 쓰고 트리거 조건을 안 씀 | "사용자가 X, Y를 언급하면 사용하라"를 명시 (undertrigger 방지) |
| 판단 기준을 LLM 재량에 맡김 | 정량 규칙을 references/에 고정 (예: 트리거 정의) |
| 매번 포트폴리오를 대화로 입력 | assets/에 상태 파일로 저장 |
| SKILL.md 하나에 전부 몰아넣음 | 500줄 넘으면 references/로 분리, 읽을 시점 안내 |
| 예측/매매지시 출력 | 관측 → 해석 → 조건부 시나리오 + 반증 조건 구조 강제 |
| 테스트 없이 배포 | 실제 프롬프트 3~5개로 발동 여부와 출력 품질 검증 |

---

## 9. 관련 링크

- [anthropics/skills 저장소](https://github.com/anthropics/skills)
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Creating custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills (엔지니어링 블로그)](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill)
- [Agent Skills 표준](http://agentskills.io)

> **주의**: 저장소의 Skills는 데모/교육 목적입니다. 실제 Claude 동작과 다를 수 있으므로 중요한 작업 전 반드시 자신의 환경에서 테스트하세요. 본 가이드의 투자 관련 스킬은 판단 재료를 구조화하는 도구이며, 투자 자문이 아닙니다.
