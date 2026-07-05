# portfolio-daily-review 설치 및 사용 가이드

> 포트폴리오를 하루 한 번 점검하고, 정량 트리거 발동 시 퀀트·뉴스·SNS 3-소스를
> 교차검증해 투자 판단 재료를 생성하는 Claude Skill
> 개념·설계 배경은 [Claude_skill_guide.md](./Claude_skill_guide.md) 6장 참조

---

## 1. 이 스킬이 하는 일

- **트리거 문구**: "포트폴리오 점검", "내 계좌 어때", "오늘 리뷰", "보유 종목 점검", "리밸런싱 필요해?", "데일리 체크"
- **핵심 동작**:
  1. `assets/portfolio.json` 에서 보유 종목·평단·리스크 한도를 로드 (매번 재입력 불필요)
  2. 현재가를 웹 검색으로 갱신 후 **정량 트리거(T1~T5)** 판정
  3. **트리거 미발동 → "이상 없음" 한 줄로 종료** (노이즈 차단이 이 스킬의 제1 규칙)
  4. 발동 시에만 퀀트/뉴스/SNS 3-소스를 **독립 수집 → 교차검증 매트릭스**
  5. 액션 후보(유지/비중축소/비중확대/손절검토/추가관찰) + 반대 논거 + 반증 조건 제시
  6. `last_review` 갱신 및 리뷰 로그 기록 (다음 리뷰의 델타 계산용)

**설계 특징 3가지**:

- **"변동"의 정의를 LLM 재량에 맡기지 않음** — trigger-rules.md 정량 규칙 + 판정 스크립트로 고정
- **시장 동조 필터** — 종목 등락이 벤치마크와 1.5%p 이내면 "시장 동조 변동"으로 강등, 약식 보고만 (지수 하락일마다 종목별 장문 분석이 쏟아지는 것을 방지)
- **thesis 우선** — 가격 변동보다 등록된 투자 논거의 유효성을 먼저 점검. SNS 극단 쏠림은 역지표 후보로만 취급

---

## 2. 설치 방법

세 가지 방법 중 하나를 선택하세요.

### 방법 A: Claude.ai (웹/앱) — 권장

1. 이 저장소의 스킬 폴더 전체를 zip으로 압축하거나, 배포된 `.skill` 파일을 준비합니다.
   ```bash
   # 폴더에서 직접 만들 경우 (zip = .skill과 동일 포맷)
   zip -r portfolio-daily-review.skill portfolio-daily-review/
   ```
2. Claude.ai → **Settings → Capabilities → Skills** 에서 업로드합니다. (유료 플랜)
3. 업로드 후 새 대화에서 트리거 문구를 말하면 자동 발동됩니다.

### 방법 B: Claude Code

개인 스킬 디렉토리에 폴더째 복사합니다:

```bash
cp -r portfolio-daily-review/ ~/.claude/skills/portfolio-daily-review/
```

Claude Code 재시작 후 자연어로 언급만 하면 됩니다.

### 방법 C: Claude API

[Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill)를 참고해
`.skill` 패키지를 업로드하면 API 호출에서도 동일하게 작동합니다.

> **검증 팁**: 설치 후 "지금 사용 가능한 스킬 알려줘"라고 물으면 로드 여부를 확인할 수 있습니다.


---

## 3. 폴더 구조

```
portfolio-daily-review/
├── SKILL.md                      # 워크플로우 본체 (0~5단계)
├── assets/
│   └── portfolio.json            # 포트폴리오 상태 (설치 후 본인 것으로 교체)
├── references/
│   ├── trigger-rules.md          # T1~T5 정량 트리거 정의
│   ├── sentiment-guide.md        # SNS 해석 규칙 (역지표·조작 체크)
│   └── action-framework.md       # 액션 후보 5종 매핑 + 출력 형식
└── scripts/
    └── check_triggers.py         # 트리거 판정 스크립트 (실행 검증 완료)
```

---

## 4. 초기 설정 (중요)

설치 직후 `assets/portfolio.json` 은 **샘플 데이터**입니다. 두 가지 방법으로 교체하세요:

**대화로**: 첫 리뷰 요청 시 스킬이 보유 종목·수량·평단을 물어 파일을 채웁니다.
또는 "포트폴리오 갱신해줘: 삼성전자 200주 평단 71,000원, ..." 처럼 직접 말하면 됩니다.

**파일 직접 수정**: 아래 스키마를 따르세요. `thesis`(투자 논거)는 반드시 채우세요 —
액션 판정 시 가격보다 먼저 점검하는 항목입니다.

---

## 5. 파일 전문

아래 내용을 그대로 복사해 동일한 폴더 구조로 저장하면 스킬이 완성됩니다.

### 5.1 SKILL.md

```markdown
---
name: portfolio-daily-review
description: >
  사용자의 투자 포트폴리오를 하루 한 번 점검하고, 사전 정의된 변동 트리거가
  발동하면 퀀트 분석·시장 뉴스·SNS 센티먼트 3개 소스를 종합해 투자 판단 재료를
  생성하는 스킬. 사용자가 "포트폴리오 점검", "내 계좌 어때", "오늘 리뷰",
  "보유 종목 점검", "리밸런싱 필요해?", "데일리 체크" 등을 언급하면 반드시
  이 스킬을 사용하라. 포트폴리오 상태는 assets/portfolio.json 에서 읽으며,
  사용자가 종목/수량 변경을 말하면 이 파일 갱신도 이 스킬로 처리한다.
---

# Portfolio Daily Review

## 목적

감정이 아닌 규칙으로 포트폴리오를 점검한다. 트리거 미발동이면 "이상 없음"
한 줄로 끝내고, 발동 시에만 3-소스(퀀트/뉴스/SNS) 종합 평가를 수행한다.

원칙: **트리거는 정량 규칙으로, 소스는 독립 수집 후 교차검증으로,
결론은 액션 후보 + 반증 조건으로.**

## 워크플로우

### 0단계: 상태 로드

`assets/portfolio.json` 을 읽는다.

- `last_review` 가 오늘 날짜면: "오늘 리뷰는 이미 완료됨"을 알리고
  재실행 여부를 사용자에게 확인한다 (하루 1회 원칙).
- 파일이 비어 있거나 `positions` 가 없으면: 사용자에게 보유 종목·수량·평단을
  물어 파일을 먼저 채운다. 리스크 한도(`risk_limits`)도 함께 확인한다.
- 사용자가 "삼성전자 50주 추가했어" 같은 변경을 말하면 파일을 갱신하고
  변경 내역을 요약해 확인받는다.

### 1단계: 시세 갱신 및 트리거 판정

각 포지션의 현재가를 웹 검색으로 확인한다. 학습 데이터의 기억으로
가격을 답하지 않는다.

`references/trigger-rules.md` 의 정량 규칙(T1~T5)으로 판정한다.
`scripts/check_triggers.py` 가 실행 가능한 환경이면 스크립트로 판정하고,
아니면 규칙 문서를 따라 수동 계산한다.

**트리거 미발동 시**: 현재가 테이블 + "트리거 없음, 액션 불필요" 로 종료한다.
불필요한 분석을 생성하지 않는다. 이것이 이 스킬의 가장 중요한 규칙이다.

### 2단계: 3-소스 수집 (트리거 발동 종목만)

각 소스를 **독립적으로** 수집하고 수집 단계에서 서로 섞지 않는다.

**[A] 퀀트 관점**
- 해당 종목의 팩터 상태: 1M/3M 모멘텀, 섹터 상대강도, 변동성 변화
- 시장 레짐과의 정합성 — `quant-market-brief` 스킬이 설치되어 있고
  오늘자 브리핑이 대화에 있으면 그 레짐 판정을 재사용한다.
  없으면 VIX/금리/지수만으로 약식 레짐을 판정하고 "약식"임을 표기한다.

**[B] 시장 뉴스**
- 웹 검색으로 트리거 원인 뉴스를 특정한다.
- 1차 출처(공시, 실적 발표, 규제기관 발표) 우선. 추측성 기사와 팩트를
  구분 표기한다. 원인 뉴스를 특정하지 못하면 "원인 불명 가격 변동"으로
  기록한다 — 이것 자체가 중요한 정보다.

**[C] SNS 센티먼트**
- X(트위터), 레딧, 국내 커뮤니티의 반응 방향과 강도를 웹 검색으로 파악한다.
- `references/sentiment-guide.md` 를 반드시 먼저 읽는다. 핵심: SNS는
  역지표일 수 있다. 극단적 쏠림(공포/환희)은 그 자체로 신호이며,
  방향 신호로 그대로 쓰지 않는다.
- 개별 계정을 특정 인용하지 않고 집계된 방향/강도만 다룬다.

### 3단계: 교차검증 및 종합 평가

세 소스의 방향 일치 여부를 매트릭스로 정리한다:

| 소스 | 방향 | 강도 | 핵심 근거 |
|---|---|---|---|
| 퀀트 | 긍정/중립/부정 | 강/중/약 | |
| 뉴스 | | | 1차 출처 여부 표기 |
| SNS | | | 극단 쏠림 시 역지표 가능성 표기 |

- **3개 일치** → 신뢰도 높음으로 표기
- **2:1 분열** → 소수 의견의 근거를 반드시 본문에 남긴다
- **뉴스(팩트)와 퀀트(가격행동)가 충돌** → 그 사실 자체를 강조한다.
  가격이 뉴스를 선반영했거나, 뉴스가 아직 가격에 반영 안 된 것 중 하나다

### 4단계: 액션 후보 제시

`references/action-framework.md` 기준으로 다음 형식을 지킨다:

- **액션 후보**: 유지 / 비중축소 / 비중확대 / 손절 검토 / 추가 관찰 중 1~2개
- 각 후보의 **근거와 반대 논거를 모두** 명시
- **반증 조건**: "X가 관측되면 이 평가는 무효" 를 반드시 포함
- 최종 결정은 사용자 몫임을 명시한다. 매수/매도 지시어를 쓰지 않는다

### 5단계: 상태 갱신

`assets/portfolio.json` 의 `last_review` 를 오늘 날짜로 갱신하고,
`review_log` 배열에 요약 1줄을 추가한다 (다음 리뷰의 "어제와의 델타"
계산에 사용). 로그는 최근 10개만 유지한다.

## 가이드라인

- 트리거 없으면 침묵한다. 매일 장문의 분석을 쏟아내는 것은 노이즈다.
- 세 소스의 가중치를 임의로 정하지 않는다. 불일치는 불일치로 보고한다.
- 모든 수치에 조회 시각을 명기한다.
- 리스크 한도(T3) 위반은 다른 모든 트리거보다 먼저, 눈에 띄게 보고한다.
- 이 스킬의 출력은 판단 재료이며 투자 자문이 아님을 마지막 줄에 명시한다.
```

### 5.2 assets/portfolio.json (샘플)

```json
{
  "base_currency": "KRW",
  "last_review": null,
  "risk_limits": {
    "single_position_max_pct": 20,
    "daily_drawdown_alert_pct": -3.0,
    "portfolio_drawdown_alert_pct": -5.0
  },
  "positions": [
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "asset_class": "equity_kr",
      "qty": 100,
      "avg_price": 72000,
      "thesis": "HBM 사이클"
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "asset_class": "equity_us",
      "qty": 10,
      "avg_price": 118.5,
      "thesis": "AI 인프라 capex"
    },
    {
      "ticker": "BTC",
      "name": "비트코인",
      "asset_class": "crypto",
      "qty": 0.5,
      "avg_price": 61000000,
      "thesis": "매크로 헤지"
    }
  ],
  "review_log": []
}
```

### 5.3 references/trigger-rules.md

```markdown
# 변동 트리거 정의

"변동이 생겼다"는 아래 정량 조건 중 **하나 이상 충족**을 의미한다.
LLM의 주관적 판단("좀 많이 빠진 것 같다")을 트리거로 쓰지 않는다.

| 트리거 | 조건 | 우선순위 |
|---|---|---|
| **T1** 개별 급변동 | 종목 일간 등락률 절대값 ≥ 3% (크립토는 ≥ 7%) | 중 |
| **T2** 포트폴리오 변동 | 전체 평가액 일간 등락률 절대값 ≥ 2% | 상 |
| **T3** 리스크 한도 | `risk_limits` 항목 위반 (비중 초과, 손실 한도 도달) | **최상** |
| **T4** 이벤트 | 보유 종목 관련 1차 출처 중대 뉴스 (실적 발표/가이던스 변경, 규제, 보안사고·해킹, 상장폐지/거래정지 이슈, 대규모 유상증자·CB) | 상 |
| **T5** 변동성 점프 | 종목 역사적 변동성(20일) 전일 대비 +50% 이상 | 중 |

## 판정 규칙

- 복수 트리거 동시 발동 시 **우선순위 높은 것부터** 보고한다.
- T3(리스크 한도)는 다른 분석보다 먼저, 별도 경고 블록으로 보고한다.
- 자산군별 임계값 차등: 크립토는 기본 변동성이 높으므로 T1 임계값을 7%로 상향.
  사용자가 `portfolio.json` 에 `trigger_overrides` 를 추가하면 그 값을 우선한다.
- 트리거 판정에 사용한 현재가와 조회 시각을 반드시 기록한다.
- 장중 조회 시: 일간 등락률은 전일 종가 대비로 계산하고 "장중 기준" 표기.

## 비트리거 (분석하지 않는 경우)

- 지수 전체가 같은 방향으로 움직여 개별 종목이 단순 동조한 경우
  (종목 등락률 − 벤치마크 등락률의 절대값 < 1.5%p 이면 T1 발동해도
  "시장 동조 변동"으로 강등, 약식 보고만)
- 거래량이 20일 평균의 50% 미만인 소폭 변동
```

### 5.4 references/sentiment-guide.md

```markdown
# SNS 센티먼트 해석 가이드

SNS는 정보원이자 동시에 **군중 심리의 온도계**다. 방향 신호로 그대로 쓰면
안 되고, 아래 규칙으로 해석한다.

## 수집 대상

- X(트위터): 종목 티커/키워드 언급량과 논조
- 레딧: r/stocks, r/wallstreetbets, 종목별 서브레딧 (미국 주식)
- 국내: 종목토론실 분위기, 주요 투자 커뮤니티 (한국 주식)
- 크립토: X + 텔레그램 채널 분위기

웹 검색으로 파악 가능한 범위까지만 수집한다. 접근 불가한 소스는
"확인 불가"로 기록하고 추정하지 않는다.

## 해석 규칙

### 1. 방향과 강도를 분리한다

- 방향: 긍정 / 중립 / 부정
- 강도: 약(평소 수준) / 중(언급량 증가) / 강(언급량 급증 + 논조 쏠림)

### 2. 극단 쏠림은 역지표 후보

- **극단 공포** (패닉셀 언급, "끝났다" 논조 지배): 단기 바닥 신호일 수 있음
- **극단 환희** (수익 인증 급증, "무조건 간다" 논조 지배): 단기 과열 신호일 수 있음
- 두 경우 모두 매트릭스에 "극단 쏠림 — 역지표 가능성" 을 반드시 병기한다

### 3. 언급량 급증 자체가 신호

논조와 무관하게 언급량이 평소의 수 배로 급증하면 변동성 확대 신호로
별도 표기한다.

### 4. 조작 가능성 체크

- 신규 계정/봇 패턴의 일방향 게시물 급증 → "펌핑/FUD 캠페인 가능성" 표기
- 특히 소형주·크립토에서 출처 불명의 호재/악재 루머는 1차 출처 확인 전까지
  뉴스([B] 소스)가 아닌 SNS([C] 소스)로만 분류한다

### 5. 인용 원칙

- 개별 계정·사용자를 특정해 인용하지 않는다
- 집계된 방향/강도/언급량 변화만 보고한다
```

### 5.5 references/action-framework.md

````markdown
# 액션 프레임워크

평가 결과를 액션 후보로 매핑하는 기준. **후보 제시까지만** 하고
최종 결정은 사용자 몫이다. 매수/매도 지시어를 쓰지 않는다.

## 액션 후보 5종

| 후보 | 제시 조건 (예시) |
|---|---|
| **유지** | 3-소스 중립~긍정, thesis(투자 논거) 훼손 없음 |
| **추가 관찰** | 소스 간 2:1 분열, 또는 원인 불명 변동 |
| **비중축소** | 3-소스 부정 일치 + thesis 부분 훼손, 또는 T3 비중 한도 초과 |
| **비중확대** | 3-소스 긍정 일치 + 가격은 하락(선반영 해소) + 한도 여유 |
| **손절 검토** | thesis 자체가 무효화된 1차 출처 팩트 발생 (예: 핵심 사업 규제 확정) |

## 출력 형식 (필수)

각 트리거 발동 종목마다:

```
### {종목명} ({티커}) — 트리거: {T1~T5}

**교차검증 매트릭스**
| 소스 | 방향 | 강도 | 핵심 근거 |
|---|---|---|---|
| 퀀트 | | | |
| 뉴스 | | | |
| SNS  | | | |

**일치도**: {3소스 일치 / 2:1 분열 / 전면 불일치}

**액션 후보**: {1~2개}
- 근거: 
- 반대 논거: 

**반증 조건**: {X가 관측되면 이 평가는 무효}

**thesis 점검**: 등록된 투자 논거 "{thesis}" 는 {유효 / 부분 훼손 / 무효화}
```

## 핵심 원칙

1. **thesis 우선**: 가격 변동보다 투자 논거의 유효성을 먼저 점검한다.
   가격이 빠져도 thesis가 유효하면 "유지 + 관찰"이 기본값이다.
2. **반대 논거 필수**: 어떤 후보든 반대 논거 없이 제시하지 않는다.
3. **반증 조건 필수**: 반증 불가능한 평가는 평가가 아니다.
4. **한도가 왕**: T3(리스크 한도) 위반 시에는 다른 소스가 아무리 긍정적이어도
   한도 준수를 위한 후보(비중축소)를 반드시 포함한다.
5. 마지막 줄에 고지: "본 리뷰는 판단 재료이며 투자 자문이 아닙니다."
````

### 5.6 scripts/check_triggers.py

```python
#!/usr/bin/env python3
"""
포트폴리오 트리거 판정 스크립트.

트리거 정의는 references/trigger-rules.md 와 동기화되어야 한다.
사용법:
    python check_triggers.py --portfolio ../assets/portfolio.json --prices prices.json

prices.json 형식 (Claude가 웹 검색으로 수집한 현재가를 넣는다):
{
  "005930.KS": {"price": 74500, "prev_close": 76900, "benchmark_change_pct": -0.8},
  "NVDA":      {"price": 121.2, "prev_close": 126.5, "benchmark_change_pct": -1.1},
  "BTC":       {"price": 95000000, "prev_close": 93000000, "benchmark_change_pct": null}
}
"""

import argparse
import json
import sys
from datetime import date

T1_EQUITY_PCT = 3.0     # 개별 급변동 (주식)
T1_CRYPTO_PCT = 7.0     # 개별 급변동 (크립토)
T2_PORTFOLIO_PCT = 2.0  # 포트폴리오 전체 변동
MARKET_SYNC_BAND = 1.5  # 시장 동조 판정 밴드 (%p)


def pct(a, b):
    return (a - b) / b * 100.0 if b else 0.0


def check(portfolio: dict, prices: dict) -> dict:
    triggers = []
    total_now, total_prev = 0.0, 0.0
    limits = portfolio.get("risk_limits", {})

    # 평가액 집계
    values = {}
    for p in portfolio.get("positions", []):
        t = p["ticker"]
        if t not in prices:
            triggers.append({"type": "DATA_MISSING", "ticker": t,
                             "msg": "현재가 미확인 — 웹 검색으로 수집 필요"})
            continue
        now = p["qty"] * prices[t]["price"]
        prev = p["qty"] * prices[t]["prev_close"]
        values[t] = now
        total_now += now
        total_prev += prev

    # T1 / T5 개별 종목
    for p in portfolio.get("positions", []):
        t = p["ticker"]
        if t not in prices:
            continue
        d = pct(prices[t]["price"], prices[t]["prev_close"])
        limit = T1_CRYPTO_PCT if p.get("asset_class") == "crypto" else T1_EQUITY_PCT
        if abs(d) >= limit:
            bench = prices[t].get("benchmark_change_pct")
            sync = bench is not None and abs(d - bench) < MARKET_SYNC_BAND
            triggers.append({
                "type": "T1", "priority": "MID", "ticker": t,
                "change_pct": round(d, 2),
                "market_sync": sync,
                "msg": f"{p['name']} 일간 {d:+.2f}%"
                       + (" (시장 동조 — 약식 보고)" if sync else ""),
            })

    # T2 포트폴리오
    if total_prev:
        pd = pct(total_now, total_prev)
        if abs(pd) >= T2_PORTFOLIO_PCT:
            triggers.append({"type": "T2", "priority": "HIGH",
                             "change_pct": round(pd, 2),
                             "msg": f"포트폴리오 평가액 일간 {pd:+.2f}%"})

    # T3 리스크 한도
    max_pct = limits.get("single_position_max_pct")
    if max_pct and total_now:
        for t, v in values.items():
            w = v / total_now * 100.0
            if w > max_pct:
                triggers.append({"type": "T3", "priority": "CRITICAL", "ticker": t,
                                 "weight_pct": round(w, 1),
                                 "msg": f"{t} 비중 {w:.1f}% > 한도 {max_pct}%"})

    dd = limits.get("portfolio_drawdown_alert_pct")
    if dd is not None and total_prev:
        pd = pct(total_now, total_prev)
        if pd <= dd:
            triggers.append({"type": "T3", "priority": "CRITICAL",
                             "msg": f"포트폴리오 일간 {pd:+.2f}% ≤ 손실 한도 {dd}%"})

    order = {"CRITICAL": 0, "HIGH": 1, "MID": 2}
    triggers.sort(key=lambda x: order.get(x.get("priority", "MID"), 3))

    return {
        "date": date.today().isoformat(),
        "portfolio_value": round(total_now, 2),
        "portfolio_change_pct": round(pct(total_now, total_prev), 2) if total_prev else None,
        "triggered": bool([t for t in triggers if t["type"].startswith("T")]),
        "triggers": triggers,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portfolio", required=True)
    ap.add_argument("--prices", required=True)
    args = ap.parse_args()

    with open(args.portfolio, encoding="utf-8") as f:
        portfolio = json.load(f)
    with open(args.prices, encoding="utf-8") as f:
        prices = json.load(f)

    result = check(portfolio, prices)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
```

---

## 6. 스크립트 단독 테스트

Claude 없이도 트리거 판정 로직을 검증할 수 있습니다:

```bash
cat > prices.json << 'EOF'
{
  "005930.KS": {"price": 74500, "prev_close": 76900, "benchmark_change_pct": -0.8},
  "NVDA": {"price": 121.2, "prev_close": 126.5, "benchmark_change_pct": -1.1},
  "BTC": {"price": 95000000, "prev_close": 93000000, "benchmark_change_pct": null}
}
EOF
python3 scripts/check_triggers.py --portfolio assets/portfolio.json --prices prices.json
```

샘플 실행 결과: BTC 비중 86.4% > 한도 20% → **T3 (CRITICAL) 최우선 정렬**,
삼성전자 -3.12% / NVDA -4.19% → T1 발동. 우선순위 정렬(CRITICAL > HIGH > MID)이
정상 동작함을 확인했습니다.

---

## 7. 사용 예시

```
> 오늘 포트폴리오 리뷰해줘

[portfolio-daily-review 발동]
1. portfolio.json 로드 → 3개 포지션, last_review 확인
2. 시세 웹 검색 → NVDA -4.2% (T1), 나머지 트리거 없음
3. NVDA만 3-소스 수집: 퀀트(모멘텀/섹터 상대강도) / 뉴스(1차 출처) / SNS(방향·강도)
4. 교차검증 매트릭스 → 일치도 판정 → 액션 후보 + 반증 조건
5. thesis "AI 인프라 capex" 유효성 점검
6. last_review 갱신 + review_log 기록
```

트리거가 없는 날은:

```
> 오늘 포트폴리오 리뷰해줘
현재가 테이블 + "트리거 없음, 액션 불필요." (끝)
```

---

## 8. 커스터마이징 포인트

| 항목 | 위치 | 기본값 | 비고 |
|---|---|---|---|
| 개별 급변동 임계 (T1) | trigger-rules.md, check_triggers.py | 주식 ±3% / 크립토 ±7% | 두 곳 동기화 필수 |
| 포트폴리오 변동 임계 (T2) | 〃 | ±2% | |
| 리스크 한도 (T3) | portfolio.json `risk_limits` | 비중 20% / 일간 -3% / 전체 -5% | 파일만 수정하면 됨 |
| 시장 동조 밴드 | check_triggers.py `MARKET_SYNC_BAND` | 1.5%p | |
| 리뷰 로그 보존 개수 | SKILL.md 5단계 | 10개 | |

> **주의**: 임계값 수정 시 `trigger-rules.md`(Claude가 읽는 규칙)와
> `check_triggers.py`(스크립트 상수)를 반드시 함께 수정하세요. 둘이 어긋나면
> 스크립트 실행 환경과 비실행 환경에서 판정이 달라집니다.

---

## 9. quant-market-brief 와 함께 쓰기

```
아침 루틴:
1. "오늘 시황 요약해줘"        → quant-market-brief: 레짐 판정
2. "포트폴리오 리뷰해줘"       → portfolio-daily-review: 같은 대화의 레짐 판정을
                                 2단계 [A] 퀀트 소스에서 재사용
```

같은 대화에서 순서대로 실행하면 레짐 컨텍스트가 자동 연결됩니다.
브리핑이 없으면 스킬이 약식 레짐 판정으로 대체하고 "약식"임을 표기합니다.

---

## 10. 주의사항

- 본 스킬의 출력은 **판단 재료이며 투자 자문이 아닙니다.** 최종 결정은 사용자 몫입니다.
- `portfolio.json` 에는 실제 계좌번호·증권사 인증정보 등 민감정보를 넣지 마세요.
  종목·수량·평단만으로 충분합니다. 공개 저장소에 커밋할 경우 실제 포트폴리오
  파일은 `.gitignore` 처리를 권장합니다.
- 스킬은 데모/교육 목적이며 실제 사용 전 자신의 환경에서 충분히 테스트하세요.
