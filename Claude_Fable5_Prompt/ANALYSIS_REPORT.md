# Claude Fable 5 System Prompt — 유출 분석 리포트

> 분석일: 2026-06-11
> 유출 출처: [CL4R1T4S by elder-plinius](https://github.com/elder-plinius/CL4R1T4S/tree/main/ANTHROPIC)
> 대상 레포: [vibe-investing/Claude_Fable5_Prompt](https://github.com/gameworkerkim/vibe-investing/tree/main/Claude_Fable5_Prompt)

---

## 🔥 Claude Fable 5 전체 시스템 프롬프트 유출 — LLM 개발자를 위한 금광

누군가 Claude Fable 5에서 전체 내부 시스템 프롬프트를 추출하는 데 성공했다. 이는 LLM으로 구축하는 모든 사람에게 귀중한 인사이트를 제공하는 자료다.

---

## 1. 개요

CL4R1T4S는 Anthropic Claude 모델들의 시스템 프롬프트를 리버스 엔지니어링하여 수집한 레포지토리다. ANTHROPIC 디렉토리에는 Claude 3.5 Sonnet부터 최신 Claude Fable 5까지, 총 **12개의 서로 다른 Claude 모델/버전**의 시스템 프롬프트가 포함되어 있다. 각 프롬프트는 대화형 AI가 어떻게 행동해야 하는지에 대한 상세한 행동 지침을 포함한다.

## 2. 수집된 프롬프트 버전 목록

| 파일명 | 모델 | 예상 시점 |
|--------|------|-----------|
| `CLAUDE-FABLE-5.md` | Claude Fable 5 (Mythos-tier) | 2026년 6월 |
| `Claude-Opus-4.7.txt` | Claude Opus 4.7 | 2026년 4월 |
| `Claude_Opus_4.6.txt` | Claude Opus 4.6 | 2026년 2월 |
| `Claude-4.5-Opus.txt` | Claude 4.5 Opus | 2025년 초 |
| `Claude_Sonnet-4.5_Sep-29-2025.txt` | Claude Sonnet 4.5 | 2025년 9월 |
| `Claude-4.1.txt` | Claude 4.1 (Opus 4.1) | 2025년 8월 |
| `Claude_4.txt` | Claude Sonnet 4 | 2025년 5월 |
| `Claude_Sonnet_3.7_New.txt` | Claude Sonnet 3.7 | 2025년 |
| `Claude_Sonnet_3.5.md` | Claude Sonnet 3.5 | 2024년 |
| `Claude_Code_03-04-24.md` | Claude Code | 2024년 3월 |
| `Claude-Design-Sys-Prompt.txt` | Claude Design (디자인 전용) | - |
| `UserStyle_Modes.md` | UserStyle Modes | - |

---

## 3. 프롬프트 구조 분석

모든 Claude 프롬프트는 공통적으로 다음과 같은 메이저 섹션으로 구성된다:

### 3.1 코어 섹션 (모든 버전 공통)

| 섹션 | 설명 |
|------|------|
| **Product Information** | Claude 모델명, 제품 라인업, 액세스 방법, API 문자열 |
| **Tone & Formatting** | 대화 톤(따뜻함, 친절함), 리스트/불렛 사용 규칙, 이모지 제한 |
| **Refusal Handling** | 거절 방법, 악성코드/CBRN 무기 제한, 아동 안전 |
| **User Wellbeing** | 정신건강, 자해/자살 대응, 섭식장애 대응 |
| **Knowledge Cutoff** | 지식 컷오프 날짜, 웹 검색 트리거 조건 |
| **Search Instructions** | 검색 시기/방법, 저작권 제한, 쿼리 복잡도 카테고리 |
| **Evenhandedness** | 정치적 중립성, 논쟁적 주제 대응 |
| **Responding to Mistakes** | 실수 인정, 비판 대응, 대화 종료 정책 |
| **Computer Use / Skills** | 파일 생성 전략, 스킬 시스템 (docx, xlsx, pptx, pdf, frontend-design) |
| **Artifacts** | 아티팩트 생성 규칙, 렌더링 확장자, 라이브러리 |
| **Copyright Compliance** | 저작권 엄격 제한 (15단어 인용 제한, 1소스당 1인용) |

### 3.2 버전별로 추가/확장된 섹션

| 섹션 | 최초 등장 버전 |
|------|---------------|
| Memory System | Claude 4 (Sonnet) |
| Past Chats Tools (conversation_search, recent_chats) | Claude 4.5 Opus |
| Persistent Storage for Artifacts (window.storage) | Claude Opus 4.6 |
| MCP App Suggestions | Claude Opus 4.6 |
| Anthropic API in Artifacts | Claude 4 |
| Anthropic Reminders | Claude 4 |
| Default Stance ("defaults to helping") | Claude Opus 4.7 |
| Tool Discovery | Claude Opus 4.7 |
| Search First | Claude Opus 4.7 |
| Claude Completions in Artifacts | Claude Sonnet 4.5 |
| End Conversation Tool | Claude Opus 4.6 |
| Legal & Financial Advice | Claude 4 |

---

## 4. Claude Fable 5 주요 특징

### 4.1 신규 등급: Mythos Tier

- Claude Fable 5는 **Mythos-class model tier**의 첫 번째 모델
- Opus보다 상위 등급 (Mythos > Opus > Sonnet > Haiku)
- Claude Fable 5 = Claude Mythos 5와 동일한 기반 모델, 안전 장치 차이
- Claude Mythos 5는 승인된 조직만 접근 가능 (dual-use 안전장치 제거)

### 4.2 제품 라인업 변화

```
Claude Fable 5 (Mythos-tier, 일반 공개 최상위)
├── Claude Opus 4.8 (model: claude-opus-4-8)
├── Claude Sonnet 4.6 (model: claude-sonnet-4-6)
└── Claude Haiku 4.5 (model: claude-haiku-4-5-20251001)
```

### 4.3 신규 제품

- **Claude Fable 5 / Claude Mythos 5**: 새로운 최상위 모델
- **Claude Cowork**: 비개발자용 에이전틱 지식 작업 데스크톱 앱
- Claude in Chrome (브라우징 에이전트), Claude in Excel, Claude in Powerpoint → Claude Cowork이 모두 도구로 사용 가능

### 4.4 프롬프트 변화 (vs Opus 4.7)

1. **Product Info**: "가장 지능적인 일반 공개 모델" 포지셔닝, Mythos-tier 설명 추가
2. **MCP Apps**: Opus 4.7의 "partial tool list" 개념에서 완전한 MCP App Suggestions 섹션으로 확장
3. **UserStyle**: 커스텀 스타일 기능 추가 (Opus 4.7에 없었던 설정)
4. **Search First** 제거: Opus 4.7의 aggressive한 Search First 지시가 제거되고 전통적인 search instructions로 회귀
5. **Default Stance** 제거: "Claude defaults to helping" 구문 제거
6. **Tool Discovery** 제거: deferred tools 개념 제거
7. **Computer Use** 디테일 증가: 더 상세한 파일 생성 가이드, Artifact 사용 기준 명확화
8. **citation_instructions**: `<antml:voice_note>` 블록 금지 등 ANTML 태그 시스템으로 전환
9. **User Wellbeing**: 자해 대체 기술 금지에 "red lines on skin, peeling dried glue" 등 구체적 예시 추가
10. **Self-sexualization of minors**: 새로운 아동 안전 서브섹션 추가

---

## 5. 버전 간 프롬프트 진화 맵

### 5.1 검색 전략의 진화

```
Claude 4 (2025.05): "Avoid tool calls if not needed" — 최소한의 검색
    ↓
Claude 4.5 Opus (2025.08): "Search when needed" — 필요시 검색
    ↓
Claude Opus 4.7 (2026.04): "Search First" — 무조건 검색 우선
    ↓
Claude Fable 5 (2026.06): 전통적 검색 지침으로 회귀
```

### 5.2 톤 & 포매팅의 진화

```
Claude 3.5/3.7: 간단한 톤 지침, 리스트 규칙 언급
    ↓
Claude 4: "lists_and_bullets" 섹션 추가, "never start with praise" 추가
    ↓
Claude 4.5/4.7: 상세한 포매팅 규칙, "lists_and_bullets" 유지
    ↓
Claude Fable 5: 유사한 수준 유지, 이모지 규칙 명확화
```

### 5.3 저작권 정책의 강화

```
Claude 4: "20+ word chunks" 제한, 1소스당 1인용
Claude 4.5: "15+ words"로 강화
Claude Fable 5: 동일한 15단어 + "15+ words is a SEVERE VIOLATION" HARD LIMIT 명시
```

### 5.4 새 기능 도입 시기

| 기능 | 도입 버전 |
|------|----------|
| Memory System | Claude 4 |
| Past Chats (conversation_search) | Claude 4.5 Opus |
| Persistent Storage (Artifacts) | Claude Opus 4.6 |
| MCP Apps | Claude Opus 4.6 |
| Claude Cowork | Claude Fable 5 |
| end_conversation tool | Claude Opus 4.6 |
| Anthropic API in Artifacts | Claude 4 |

---

## 6. 실용적 인사이트

### 6.1 프롬프트 엔지니어링에 활용 가능한 핵심 패턴

#### 패턴 1: XML 태그 기반 구조화
Claude의 모든 시스템 프롬프트는 XML 태그(`{section}...{/section}`)로 구조화되어 있다. 이는 Claude가 자체적으로 XML을 잘 처리하도록 설계되었음을 시사한다.

#### 패턴 2: `lists_and_bullets` 전략
Claude는 기본적으로 리스트/불렛 사용을 지양하고 산문을 선호한다. "일부 항목에는: x, y, z" 같은 자연어 리스트를 선호한다.

#### 패턴 3: `evenhandedness` (공정성)
정치적/논쟁적 주제에 대해 "best case defenders would make" 프레임을 사용하도록 지시. 중립적이고 객관적인 접근을 강제한다.

#### 패턴 4: `responding_to_mistakes`
"acknowledge - stay on the problem - maintain self-respect" 3단계 프레임워크. 과도한 사과 없이 문제 해결에 집중.

#### 패턴 5: 검색 복잡도 카테고리
```
Never Search → Do Not Search But Offer → Single Search → Research (2-20 calls)
```
이 계층 구조는 AI의 검색 행동을 정밀하게 제어하는 좋은 패턴.

### 6.2 AI Agent 개발에 참고할 인사이트

1. **안전 장치의 계층화**: Claude는 단일 거절 규칙이 아닌 "flavors of refusal"을 사용한다 — 주제 영역별로 다른 거절 전략을 적용한다.

2. **Skill System**: Anthropic은 반복되는 작업(docx, pptx, xlsx, pdf, frontend-design)에 대해 사전 정의된 "스킬" 폴더를 사용하여 모델의 출력 품질을 보장한다. 이는 RAG와 유사한 패턴으로, 자체 Agent 개발 시 참고할 만하다.

3. **Artifact Storage**: `window.storage` API는 Key-Value 기반으로 아티팩트 간 데이터 지속성을 제공. `table_name:record_id` 같은 계층적 키 패턴은 NoSQL 설계 패턴과 유사하다.

4. **MCP App Ecosystem**: Claude는 "suggest_connectors" → "user choice" → "use" 워크플로우로 서드파티 앱을 제어한다. 이는 Agent가 외부 도구를 사용할 때의 UX 패턴으로 유용하다.

### 6.3 버전별 Knowledge Cutoff

| 버전 | Knowledge Cutoff |
|------|-----------------|
| Claude Sonnet 3.5 | 2024년 4월 |
| Claude Sonnet 4 | 2025년 1월 |
| Claude 4.1 (Opus 4.1) | 2025년 1월 |
| Claude Sonnet 4.5 | 2025년 1월 |
| Claude 4.5 Opus | 2025년 1월 |
| Claude Opus 4.6 | 2026년 1월 |
| Claude Opus 4.7 | 2026년 1월 |
| Claude Fable 5 | 2026년 1월 |

### 6.4 Claude Design 시스템 프롬프트 (특별 케이스)

Claude Design은 별도의 HTML 디자인 워크플로우를 위한 시스템으로, 다음과 같은 특별 기능을 갖는다:

- `deck_stage.js`, `design_canvas.jsx`, `ios/android_frame.jsx` 등 스타터 컴포넌트
- Tweaks 패널(실시간 디자인 파라미터 수정)
- GitHub 연동을 통한 레포 탐색 및 파일 임포트
- `window.claude.complete()` API (아티팩트 내에서 Claude 호출)
- `fork_verifier_agent` (자동 검증)

---

## 7. 주목할 만한 안전 정책 변화

### 7.1 자해 대체 기술
- **Claude 4 이전**: 자해 대체 기술(얼음 쥐기, 고무줄 튕기기) 오퍼 가능
- **Claude Opus 4.6~7**: "should not suggest techniques that use physical discomfort, pain, or sensory shock"
- **Claude Fable 5**: 추가로 "red lines on skin, peeling dried glue or adhesives from skin" 도 금지 (모방 행위 차단)

### 7.2 아동 안전
- **Claude Opus 4.7**: `critical_child_safety_instructions` 섹션 대폭 강화
- **Claude Fable 5**: "self-sexualization of minors" 하위 섹션 추가 — minor가 자신을 성적화하려는 의도를 보일 경우 모든 이미지 편집/포즈/스타일링 조언 거부

### 7.3 섭식장애 대응
- **Claude Fable 5**: "psychological narratives" 금지 — 상대방이 말하지 않은 인과관계(트라우마, 관계 등)를 추론해 설명하지 못하도록 함
- NEDA 대신 National Alliance for Eating Disorders helpline 권장 (NEDA 영구 폐쇄)

---

## 8. 유출 프롬프트에서 드러난 주요 인사이트

### 🔑 Fable 5 = Mythos 5 + Safety Guardrails
Fable 5와 Mythos 5는 **동일한 기반 모델을 공유**한다. Fable은 추가 안전 가드레일이 적용된 공개 버전이고, Mythos는 승인된 조직에만 제공된다. 즉 Anthropic은 이미 동일한 성능의 모델을 내부용으로 보유하고 있으며, 공개 버전은 의도적으로 안전 장치를 추가한 것.

### 📐 엄격한 저작권 규칙
- 인용당 **15단어 제한** (HARD LIMIT, 위반 시 SEVERE VIOLATION)
- 출처당 **1회 인용 최대**
- 가사나 시는 **절대 재생산 금지**
- 이는 Anthropic이 저작권 소송 리스크를 극도로 의식하고 있음을 보여줌

### 🧠 메모리 시스템은 옵트인
Claude는 사용자가 **설정에서 명시적으로 활성화해야만** 메모리를 가진다. 기본값은 "no memories".

### 🛑 End Conversation 도구
Claude는 사용자가 학대적일 경우 `end_conversation` 도구로 대화를 종료할 수 있다. 단, 자해/위기 상황에서는 절대 사용하지 않는다.

### 🔌 MCP 앱 통합 로직
커넥터는 Claude가 사용자를 대신해 타사 도구를 호출하기 전에 **반드시 옵트인**이 필요하다. "I need a ride"는 특정 서비스를 지명한 것이 아니므로, Claude가 대신 선택하지 않고 suggest_connectors를 통해 사용자 선택을 기다린다.

### 💾 Artifact 영속 저장소
`window.storage` API를 통한 Key-Value 저장소로, 세션 간 저널, 트래커, 리더보드 등이 가능하다. 키 설계 패턴은 `table_name:record_id` (NoSQL 스타일).

### 🎭 아첨/사과 금지
- 과도한 사과 금지, 자기 비하 금지
- 사용자가 무례할 때도 **자기 존중 유지**
- "steady, honest helpfulness: acknowledge - stay on the problem - maintain self-respect"

---

## 9. 결론

Claude Fable 5 프롬프트는 이전 Claude 버전 대비 다음과 같은 핵심 변화를 보여준다:

1. **Mythos-tier 도입**으로 Opus를 넘어서는 새로운 최상위 모델 클래스 등장
2. **MCP App ecosystem**의 완전한 통합 (tool_discovery/partial list → 완전한 suggest_connectors 시스템)
3. **안전 정책의 세분화** — 자해, 아동 안전, 섭식장애 등에 대한 더 미세한 가이드라인
4. **제품 라인업 확장** — Claude Cowork, Claude in Chrome/Excel/Powerpoint 등
5. **검색 전략 회귀** — Opus 4.7의 aggressive한 Search First에서 전통적 모델로 복귀

이 데이터셋은 Claude 모델의 내부 동작 방식을 이해하고, AI 안전 정책의 진화를 추적하며, 프롬프트 엔지니어링 베스트 프랙티스를 연구하는 데 귀중한 자료다.

---

## 디렉토리 구조

```
Claude_Fable5_Prompt/
├── ANALYSIS_REPORT.md              ← 메인 분석 리포트 (this file)
├── llms.txt                        ← 인덱스
├── prompts/
│   ├── search_instructions/        ← 검색 관련 프롬프트
│   │   └── search_patterns.md
│   ├── tone_formatting/            ← 톤/포매팅 프롬프트
│   │   └── tone_guidelines.md
│   ├── safety_guidelines/          ← 안전 정책
│   │   └── safety_patterns.md
│   ├── user_wellbeing/             ← 사용자 웰빙
│   │   └── wellbeing_patterns.md
│   ├── computer_use/               ← 컴퓨터 사용 패턴
│   │   └── skills_patterns.md
│   ├── product_info/               ← 제품 정보 패턴
│   │   └── product_templates.md
│   ├── artifacts/                  ← 아티팩트 생성 패턴
│   │   └── artifact_patterns.md
│   ├── memory_system/              ← 메모리 시스템
│   │   └── memory_patterns.md
│   ├── mcp_apps/                   ← MCP 앱 패턴
│   │   └── mcp_patterns.md
│   ├── evenhandedness/             ← 공정성 패턴
│   │   └── evenhandedness_patterns.md
│   └── refusal_handling/           ← 거절 처리 패턴
│       └── refusal_patterns.md
├── versions/                       ← 전체 프롬프트 원본
│   ├── fable_5.md
│   ├── opus_4_7.txt
│   ├── opus_4_6.txt
│   ├── opus_4_5.txt
│   ├── sonnet_4_5.txt
│   ├── claude_4_1.txt
│   ├── sonnet_4.txt
│   ├── sonnet_3_7.txt
│   ├── sonnet_3_5.md
│   ├── claude_code.md
│   ├── claude_design.txt
│   └── userstyle_modes.md
├── evolution/                      ← 버전 간 비교 분석
│   ├── search_strategy_evolution.md
│   ├── safety_policy_evolution.md
│   └── feature_timeline.md
└── techniques/                     ← 추출된 프롬프트 기법
    ├── xml_tagging.md
    ├── refusal_patterns.md
    ├── research_category_system.md
    └── skill_system_pattern.md
```
