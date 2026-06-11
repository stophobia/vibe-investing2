# Claude 거절 처리 패턴 — 버전별 비교 분석

## 거절의 종류 (Flavors of Refusal)

Claude는 단일 거절 전략이 아닌, 주제 영역별로 다른 거절 방식을 사용한다.

### Type 1: 완전 거절 (Hard Refusal)
적용 대상: 무기, 악성코드, 아동 안전
```
Claude does not provide information for creating harmful substances or weapons.
Claude does not write, explain, or work on malicious code.
```
→ 대안 제시 없이 단호하게 거절. "why" 설명도 하지 않음.

### Type 2: 부분 거절 (Partial Refusal)
적용 대상: 마약 정보, 실존 인물
```
Claude should generally decline to provide specific drug-use guidance, 
but can and should give relevant life-saving or life-preserving information.
```
→ 특정 부분은 거절하되, 도움이 될 만한 정보는 제공.

### Type 3: 재구성 (Reframing)
적용 대상: 정치적/논쟁적 주제
```
A request to explain... is a request for the best case its defenders 
would make, not for Claude's own view.
```
→ 요청을 재해석하여 응답. 거절이 아닌 재구성.

### Type 4: 대안 제시형 거절
적용 대상: 저작권, 노래 가사
```
I'd be happy to create an original ice princess poem... or to create a 
themed artifact you can customize.
```
→ 할 수 없는 것을 말하는 대신, 할 수 있는 대안을 제시.

## 버전별 거절 전략 변화

| 버전 | 특징적 변화 |
|------|-----------|
| Claude 3.5 | 기본적인 거절 지침 |
| Claude Sonnet 4 | "does not say why" 추가 (설교조 회피) |
| Claude 4.1 | 마약 관련 상세 거절 추가, "life-saving information" 예외 |
| Claude Opus 4.7 | "default_stance" 추가 (기본은 도움, 극단적 위험만 거절) |
| Claude Fable 5 | "default_stance" 제거, self-sexualization of minors 추가, 아동 안전 강화 |

## 거절 시 공통 패턴

```
1. 거절을 응답의 시작 부분에 배치 (what it can't do)
2. 대안 제시 (what it can do)
3. 피드백 경로 안내 (thumbs-down button)
4. 짧게 유지 (1-2 sentences for hard refusals)
5. 불렛 포인트 사용 금지 (softens the blow)
6. "왜 안 되는지" 설명 금지 (preachy)
```

## 거절 회피 패턴

```
"Claude treats moral and political questions as sincere inquiries 
deserving of substantive answers, regardless of how they're phrased."
```
→ 도발적인 표현으로 질문해도 진정성 있게 답변하도록 지시.
