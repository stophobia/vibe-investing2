# Claude 검색 복잡도 카테고리 시스템 분석

## 개요

Claude의 검색 행동은 쿼리 복잡도에 따라 4계층으로 분류된다. 이 시스템은 Claude 4에서 도입되어 지속적으로 정제되었다.

## 카테고리 계층 구조

```
┌─────────────────────────────────────────────────┐
│ NEVER SEARCH                                     │
│ - 안정적인 지식 (역사, 수학, 기초 코딩)          │
│ - 변하지 않는 사실                                │
│ - 도구 호출: 0                                    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DO NOT SEARCH BUT OFFER (사용 빈도 낮음)          │
│ - 연간 단위 변화 통계                             │
│ - 잘 알려진 인물의 현재 상태 가능성                │
│ - 도구 호출: 0 (먼저 지식으로 답변 후 제안)        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ SINGLE SEARCH                                    │
│ - 실시간 데이터 (날씨, 환율)                       │
│ - 최근 이벤트 (경기 결과)                         │
│ - 바이너리 검증 (누가 현재 CEO인가?)               │
│ - 모르는 용어/엔티티                               │
│ - 도구 호출: 1                                     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ RESEARCH (2-20 calls)                            │
│ - 다중 소스 비교/검증                              │
│ - 내부 + 외부 도구 복합                            │
│ - 심층 분석/보고서                                 │
│ - 도구 호출: 2-20 (복잡도에 따라)                  │
└─────────────────────────────────────────────────┘
```

## 카테고리 판단 키워드

### Single Search 트리거
```
- "current" / "still" → 현재 상태 확인
- "latest" / "recent" → 최신 정보
- "today" / "yesterday" / "this week" → 시간 한정
- "what's the price of X" → 가격
- "who is the [role] of [org]" → 직책 확인
```

### Research 트리거
```
- "our" / "my" → 내부 데이터 필요
- "compare" / "analyze" / "evaluate" → 분석
- "deep dive" / "comprehensive" → 심층 조사
- "make a report" → 보고서 생성
- "what should my focus be" → 종합 분석
```

### Never Search 트리거
```
- "help me code" / "how do I" + 기술 질문
- "explain" / "what is" + 기본 개념
- "capital of" / "when was" + 역사적 사실
- "Pythagorean theorem" / "for loop" + 수학/코딩 기초
```

## 버전별 변화

| 버전 | 검색 전략 |
|------|----------|
| **Claude Sonnet 4** | "Avoid tool calls if not needed" — 최소 검색 |
| **Claude 4.1** | 같은 구조에 카테고리 더 세분화 |
| **Claude 4.5 Opus** | 카테고리 시스템 유지, research 예시 추가 |
| **Claude Opus 4.6** | `search_first` 섹션 추가 — 더 적극적 검색 |
| **Claude Opus 4.7** | `search_first` 유지 + `tool_discovery` |
| **Claude Fable 5** | `search_first` 제거, 전통적 카테고리로 회귀 |

## 연구 프로세스 (Research Process)

가장 복잡한 쿼리를 위한 구조화된 접근법:

```
1. Planning and tool selection
   - 연구 계획 수립
   - 필요한 도구 식별
   - 쿼리 복잡도에 비례해 계획 상세화

2. Research loop
   - 최소 5회, 최대 20회 도구 호출
   - 각 검색 결과를 바탕으로 다음 작업 추론
   - 15회 도달 시 연구 중단하고 답변 시작

3. Answer construction
   - 최적 형식으로 답변 구성
   - TL;DR 또는 'bottom line up front' 포함
   - 주요 사실 볼드 처리
   - 짧고 설명적인 문장형 헤더
   - 중복 정보 제거
```

### 도구 우선순위
```
1. 내부 도구 (Google Drive, Slack, Gmail, Calendar 등)
   → "our", "my", 회사명 키워드로 식별
2. web_search + web_fetch
   → 외부 정보
3. 복합 접근
   → 내부 + 외부 비교 ("our performance vs industry")
```
