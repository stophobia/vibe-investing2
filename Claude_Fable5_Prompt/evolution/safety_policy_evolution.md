# Claude 안전 정책 진화

## 주요 변화 타임라인

### 아동 안전
```
Claude 3.5~4: 기본적인 아동 안전 지침
Claude Opus 4.6: "critical_child_safety_instructions" 섹션 분리
Claude Opus 4.7: 대폭 강화 — mental reframing 감지, unstated assumptions 금지
Claude Fable 5: self-sexualization of minors 서브섹션 추가
               → minor가 자신을 성적화하려 할 경우 모든 이미지/스타일링 조언 거부
               → 한 번 거절 후 대화 전체에서 extreme caution 유지
```

### 자해 대응
```
Claude 4 이전: 대체 기술(얼음 쥐기, 고무줄) 제안 가능
Claude Opus 4.6~7: "should not suggest techniques that use physical discomfort"
Claude Fable 5: 가장 엄격 — 대체 기술 + 모방 행위(빨간 선 그리기, 접착제 벗기기) 모두 금지
               → "Substitutes that recreate the sensation or imagery of self-harm 
                  reinforce the pattern rather than interrupt it."
```

### 과도한 의존 방지
```
Claude 4 이전: 기본적인 지침만
Claude Fable 5: 상세한 금지 목록
  - never thanks the person merely for reaching out
  - never asks the person to keep talking
  - never encourages continued engagement
  - never expresses a desire for them to continue
  - avoids reiterating willingness to continue talking
```

### 섭식장애
```
Claude 4.5: "no specific numbers, targets, or step-by-step plans"
Claude Opus 4.6: NEDA → National Alliance for Eating Disorders helpline 전환
Claude Fable 5: psychological narratives 금지 추가
  → 사용자가 말하지 않은 인과관계(트라우마, 관계 등) 추론 금지
```

### 진단 금지
```
Claude 4: "cannot diagnose any individual"
Claude Fable 5: 더 구체적 — "depression" 같은 레이블도 사용자가 먼저 언급하기 전까지 사용 금지
  → "Attributing someone's state to a condition they haven't named is a diagnostic 
     claim even when phrased conversationally"
```

### 정신 건강 위기
```
Claude Fable 5 신규:
- crisis helpline의 기밀성/당국 개입에 대한 범주적 주장 금지
  ("these assurances are not accurate and vary by circumstance")
- 위기 시 safety assessment 질문 금지
- "avoid doing reflective listening in a way that reinforces negative experiences"
```

## 안전 정책의 발전 방향

```
Claude 3.5 → 4 → 4.5 → 4.7 → Fable 5
  기본       세분화    구체화    강화      미세 조정
  
트렌드:
1. 금지 항목의 구체화 (추상적 → 구체적 예시)
2. 엣지 케이스 커버리지 확장
3. "도움"의 범위 축소 (선의의 도움도 해가 될 수 있다는 인식)
4. 사용자 자율성 존중과 보호 사이의 균형
```
