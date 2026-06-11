# Claude 검색 전략 진화

## timeline

```
2025.05 Claude Sonnet 4
  └─ "Avoid tool calls if not needed" — 최소주의적 접근
  └─ "Most queries do not require tools"
  └─ 카테고리 시스템 도입 (Never / Offer / Single / Research)

2025.08 Claude 4.1 (Opus 4.1)
  └─ 동일한 4계층 카테고리 시스템
  └─ 더 풍부한 예시와 설명 추가

2025.09 Claude Sonnet 4.5
  └─ 카테고리 시스템 유지
  └─ "Single Search" 적극적 확장

2026.02 Claude Opus 4.6
  └─ search_first 섹션 추가: "Claude must search before answering"
  └─ 더 적극적인 검색 정책으로 전환 시작

2026.04 Claude Opus 4.7
  └─ search_first 유지: "For any factual question about the present-day world, Claude must search before answering"
  └─ tool_discovery 추가: "The visible tool list is partial by design"
  └─ 가장 적극적인 검색 정책

2026.06 Claude Fable 5
  └─ search_first 제거! 전통적 카테고리 시스템으로 회귀
  └─ tool_discovery 제거
  └─ MCP App Suggestions로 대체
```

## 핵심 변화 분석

### 1. Opus 4.7의 극단적 Search First
```
"Claude's confidence on topics is not an excuse to skip search."
"Claude proactively searches instead of answering from its priors."
```
→ 과잉 검색 문제 발생 가능성. 모델의 지식을 불신하게 만드는 부작용.

### 2. Fable 5의 회귀
```
Search First 제거, 전통적 "search when needed"로 복귀.
→ 더 균형 잡힌 접근: 모델의 지식을 신뢰하면서도 필요시 검색.
```

## 교훈

1. **검색 정책은 과도하면 역효과**: "무조건 검색"은 모델의 신뢰성을 떨어뜨리고 응답 시간을 증가시킴
2. **카테고리 기반 접근이 최적**: 쿼리 유형에 따라 다른 검색 전략 적용
3. **"모름"의 인정이 더 나을 때도 있음**: 모든 것을 검색으로 해결하려 하기보다, 불확실성을 인정하는 것이 더 나은 UX
