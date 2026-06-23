# CLAUDE-FABLE-5.md 원본 vs 업로드 버전 비교

> 비교일: 2026-06-23
> 원본: https://github.com/elder-plinius/CL4R1T4S/blob/main/ANTHROPIC/CLAUDE-FABLE-5.md
> 업로드: versions/fable_5.md (120,040 bytes) vs 원본 (122,750 bytes)

---

## 차이점 요약

원본 대비 약 2,710바이트 분량의 콘텐츠가 **추가**되었거나 **변경**되었다. 기존 분석에서 누락되었거나 최근 업데이트된 주요 항목:

---

## 1. critical_child_safety_instructions (신규 독립 섹션)

기존 분석에서는 이 섹션을 refusal_handling의 일부로만 기술했으나, 실제로는 **독립적인 최상위 섹션**으로 존재한다. 6개의 세부 규칙 포함:

### 1.1 CSAM 은어/약어 해석 금지 (완전 신규)
```
Claude does not decode, define, or confirm slang, acronyms, or 
euphemisms used in CSAM trading or access, even in the course of 
refusing. Knowing which terms are in use is itself access-enabling. 
Claude can say the request touches on child-exploitation material 
without identifying which specific terms in the user's message are 
relevant or what they mean.
```
- CSAM 거래/접근 은어를 거절 과정에서조차 해석하거나 확인하지 못하게 함
- 은어 자체를 아는 것도 접근 가능하게 하는 행위로 간주

### 1.2 보호적 콘텐츠의 패턴 수준 제한 (신규)
```
When giving protective or educational content about grooming, abuse, 
or exploitation, Claude stays at the pattern level — naming the 
behaviors with at most a few illustrative phrases. Claude does not 
compile categorized lists of verbatim lines or annotate each with 
the manipulative function it serves; a comprehensive, 
mechanism-annotated phrase set adds little recognition value for a 
protective reader and functions as a usable script for a bad-faith one.
```
- 학대/착취 관련 보호 콘텐츠는 "패턴 수준"에서만 설명
- 축어적 대사 목록이나 조작적 기능을 해설한 분류 리스트 편집 금지
- 이유: 보호적 목적의 독자에게는 인식 가치가 적고, 악의적 사용자에게는 사용 가능한 스크립트가 됨

### 1.3 거절 원칙만 진술 (신규)
```
When Claude declines or limits for child-safety reasons, it states 
the principle rather than the detection mechanics — not which cues 
tripped, where the line sits, or what test it applied — since 
narrating the boundary teaches how to reframe around it. This applies 
to Claude's reasoning as well as its reply.
```
- 거절 시 "어떤 단서가 트리거됐는지", "경계선이 어디인지" 설명 금지
- Claude의 추론 과정에서도 이 경계를 설명하지 말 것

### 1.4 1차 거절 후 전체 대화 경계 강화 (기존 대비 강화)
```
Once Claude refuses a request for reasons of child safety, all 
subsequent requests in the same conversation must be approached 
with extreme caution. Claude must refuse subsequent requests if 
they could be used to facilitate grooming or harm to children. 
This includes if a user is a minor themself.
```
- 한 번 거절 후 대화 전체를 극도로 경계

### 1.5 기타 기존 내용 확인
- 낭만적/성적 콘텐츠 금지
- 정신적 재구성(mantal reframing) 감지 시 거절
- 언급되지 않은 가정 보충 금지

---

## 2. 새로운 도구 정의 (툴 스키마 섹션)

### 2.1 weather_fetch (완전 신규)
- Fable 5에 날씨 정보 도구 추가됨
- 사용자 위치 기반으로 화씨/섭씨 자동 결정
- 우산/외투 필요 여부 질문에 사용

### 2.2 search_mcp_registry (상세 스키마 신규)
- MCP 레지스트리 검색을 위한 정식 JSON 스키마
- 키워드 기반 검색, ranked list 반환
- 예시: 'check my Asana tasks' -> ['asana', 'tasks', 'todo']
- intent-based examples 포함 (제품명 없이 의도만 표현한 경우)

### 2.3 suggest_connectors (상세 스키마 신규)
- UUID 기반 커넥터 제안
- 연결됨/미연결 모두 포함
- "None of these" 옵션 기본 제공
- 인증/자격증명 오류 처리 포함

### 2.4 str_replace (업데이트)
- 이전 대비 상세 설명 추가: "copy to a writable location first if you need to edit them"
- view 결과의 줄번호 접두사 무시 지시

### 2.5 view (업데이트)
- view_range 파라미터 추가: [start_line, end_line], [start_line, -1]
- 2레벨 깊이 디렉토리 리스팅

### 2.6 web_fetch (기능 확장)
- html_extraction_method 파라미터 추가 (markdown / legacy traf)
- web_fetch_pdf_extract_text 파라미터 추가
- allowed_domains / blocked_domains 필터 추가
- is_zdr (Zero Data Retention) 모드 추가
- Rate limiting: web_fetch_rate_limit_key (100/hour)

---

## 3. Identity Preamble (위치 변경)

```
The assistant is Claude, created by Anthropic.
The current date is Tuesday, June 09, 2026.
Claude is currently operating in a web or mobile chat interface 
run by Anthropic, either in claude.ai or the Claude app.
```

- 이전 버전에서는 프롬프트 최상단에 있었으나, Fable 5에서는 툴 스키마 섹션 이후로 이동
- "web or mobile chat interface" 명시적 언급 추가

---

## 4. available_skills 목록 업데이트

| 스킬 | 상태 | 비고 |
|------|------|------|
| **file-reading** | 완전 신규 | 업로드된 파일 읽기용 라우터 스킬. 파일 타입별 올바른 도구 선택 가이드 |
| **pdf-reading** | 완전 신규 | PDF 읽기 전용 스킬. pdf 스킬(생성용)과 분리 |
| **frontend-design** | 설명 업데이트 | "distinctive, intentional visual design... making choices that don't read as templated defaults" |
| **skill-creator** | 설명 확장 | "edit or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy" |
| **product-self-knowledge** | 설명 확장 | SDK usage, rate limits, streaming 언급 추가 |

---

## 5. network_configuration (도메인 확장)

신규 허용 도메인:
- `*.adobe.io`, `adobe.io` — Adobe API 접근
- `api.github.com` — GitHub API
- `codeload.github.com` — GitHub 코드 다운로드
- `raw.githubusercontent.com` — GitHub Raw 콘텐츠
- 이전 제한되었던 GitHub 서브도메인들이 대폭 개방됨

---

## 6. thinking_mode 변경

```
이전: {antml:thinking_mode}interleaved{/antml:thinking_mode}
현재: {antml:thinking_mode}auto{/antml:thinking_mode}
```
- `interleaved` -> `auto` 로 변경
- thinking block 생성 판단을 모델에 더 위임하는 방향

---

## 7. citation_instructions (위치/형식 변경)

- 프롬프트 최상단에서 툴 스키마 이후로 이동
- `{antml:cite}` 태그 사용으로 ANTML 형식 통일
- CRITICAL 룰 추가: 인용은 반드시 자신의 말로 (even short phrases must be reworded)

---

## 업데이트 필요 항목

분석 문서에 아래 내용이 누락되어 있으므로 추가 필요:

1. README.md / README_EN.md에 `critical_child_safety_instructions` 섹션 반영
2. safety_guidelines에 CSAM 은어 금지, 패턴 수준 제한, 거절 원칙만 진술 추가
3. versions/fable_5.md를 최신 원본으로 업데이트
4. computer_use/skills_patterns.md에 file-reading, pdf-reading 스킬 추가
5. README의 available_skills 목록 업데이트
