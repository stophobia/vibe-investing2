# Claude 프롬프트 최적화 도구 Getting Started

> Claude의 출력 품질을 끌어올리는 프롬프트 최적화 오픈소스 5종 소개 자료이다. 우리는 Fable 사용이 제한되어 있기 때문에 Opus 4.8을 죽어라 최적화해야 한다.
> 각 프로젝트의 동작 방식, 사용 예, 장점·단점, 설치 가이드를 정리했고, 이 최적화 스킬과 훅을 쓰면 효율성이 높아진다.

---

## 0. 한눈에 비교

| 프로젝트 | 유형 | 동작 환경 | 핵심 메커니즘 | 규모(★) | 권장 사용자 |
|---|---|---|---|---|---|
| **CheswickDEV/claude-opus-4.8-prompt-optimizer** | 메타 옵티마이저 (system prompt) | 모든 Claude 인터페이스 (claude.ai / API / Code) | `prompt:` 트리거 → 11 rules + 10-component XML 구조화 | 신규 | 일관된 고품질 프롬프트를 반복 생성하려는 사용자 |
| **johnpsasser/claude-code-prompt-optimizer** | Hook | Claude Code | `<optimize>` 태그 가로채기 → extended thinking 확장 | 소규모 | Claude Code에서 즉석 확장이 필요한 개발자 |
| **severity1/claude-code-prompt-improver** | Hook + Skill (plugin) | Claude Code | 모호한 프롬프트만 선별 → 리서치·질문 주입 | ~1.4k | 교정 왕복을 줄이고 싶은 Claude Code 헤비유저 |
| **Hashaam101/prompt-optimizer** | Skill | Claude Code | auto(자동 정제) / manual(`/optimize` 텍스트 출력) 이중 모드 | 소규모 | 자동·수동을 골라 쓰고 싶은 사용자 |
| **nidhinjs/prompt-master** | Skill | 멀티 툴 (Claude·ChatGPT·Midjourney 등) | 타깃 툴별 프롬프트 생성, 메모리 유지 | 소규모 | 여러 AI 툴을 오가며 작업하는 사용자 |

**용어 정리**

- **Hook**: Claude Code가 프롬프트 제출 같은 특정 시점에 자동 실행하는 스크립트. 사용자가 입력한 내용을 가로채 변형할 수 있다.
- **Skill**: `~/.claude/skills/`에 두는 지침 파일. 조건이 맞으면 Claude가 스스로 로드해 동작에 반영한다.
- **메타 옵티마이저**: 도구 자체가 system prompt로 동작하며, 입력 프롬프트를 "실행 대상"이 아니라 "최적화 대상"으로 받아 구조화된 새 프롬프트를 돌려준다.

---

## 1. CheswickDEV/claude-opus-4.8-prompt-optimizer

원시(raw) 프롬프트를 Opus 4.8 아키텍처에 맞춘 production-ready XML 구조 프롬프트로 변환하는 메타 프롬프팅 시스템. 11개 최적화 규칙, 10-컴포넌트 프레임워크, 복잡도 기반 라우팅, 그리고 강제 `prompt:` 트리거를 갖췄으며 모두 Anthropic 공식 문서에서 도출됐다. 프롬프트 모음집이 아니라 "최적화 엔진"이라는 점이 핵심 차별점이다. (MIT License)

### 동작 방식 (5단계)

1. **Prompt analysis** — intent, complexity, domain, expected output, 누락 요소 탐지
2. **Complexity routing** — simple은 3–4 컴포넌트, moderate는 5–7, complex는 full 10-component
3. **Rule application** — 11개 규칙 중 해당하는 subset만 발화
4. **Quality check** — task 명확성, XML tag 유효성, example 일관성, 모순 지시 여부 점검
5. **Structured output** — 분석 + copy-ready 최적화 프롬프트 + 변경 사유 노트 반환

### 사용 예 (Before / After)

**입력 (raw)**

```
Write me a Python script that analyzes CSV files and finds anomalies
```

**출력 (optimized, 발췌)**

```
<role>
You are a senior data engineer specializing in anomaly detection and
statistical analysis with Python.
</role>

<context>
CSV datasets come from production IoT sensors. Files range from
10K–5M rows with columns: timestamp, sensor_id, value, status.
</context>

<task>
1. Loads one or more CSV files
2. Detects statistical anomalies using z-score and IQR methods
3. Handles missing data gracefully
4. Outputs a summary report with flagged rows
</task>

<constraints>
- Use only pandas, numpy, scipy (no ML libraries)
- Handle files up to 5M rows efficiently
- Include type hints and docstrings
</constraints>

<output_format>
Single Python code block, followed by a usage example and sample output.
</output_format>
```

`prompt:` 트리거를 앞에 붙이면, 입력에 질문·지시·첨부 PDF·prompt-injection 시도가 섞여 있어도 이를 실행하지 않고 항상 "최적화 대상"으로만 처리한다. 첨부 문서는 `{{DOCUMENT}}` placeholder로 치환된다.

```
prompt: Based on the attached PDF, explain the GDPR compliance risks and mitigation.
```

### 장점

- **모든 Claude 인터페이스에서 동작** — Claude Code 전용이 아닌, system prompt 기반이라 claude.ai Project / 직접 붙여넣기 / API 어디서든 사용 가능
- **Opus 4.8 전용 튜닝** — effort 기본값 `high`, per-turn adaptive thinking, 향상된 tool triggering, 1M-token context 등을 반영해 노트에 권장 effort까지 명시
- **복잡도 비례 스케일링** — 단순 질문에 과도한 10-tag를 씌우지 않음
- **재사용 가능 템플릿** — `{{VARIABLE}}` 형태로 출력해 반복 작업에 그대로 활용

### 단점

- **수동 워크플로우** — Hook/Skill처럼 자동 발화가 아니라, 사용자가 직접 system prompt를 세팅하고 프롬프트를 넣어야 함
- **Opus 4.8 종속** — 다른 모델(타사 LLM, 구버전 Claude)에는 규칙 일부가 안 맞을 수 있음 (model-agnostic 아님)
- **신생 레포** — star가 적어 커뮤니티 검증·이슈 트래킹이 얇음
- API 사용 시 Opus 4.8 제약(temperature/top_p/top_k 미지원, assistant prefill 미지원)을 사용자가 직접 인지해야 함

### 설치 가이드

레포 구성: `README.md`, `CLAUDE.md`(엔진 본체), `GUIDE.md`(사용 패턴), `QUICKSTART.md`, `LICENSE`

**Option A — Claude Project (권장)**

1. claude.ai에서 새 **Project** 생성
2. `CLAUDE.md` 내용을 **Project Instructions** 필드에 붙여넣기
3. `GUIDE.md`를 **knowledge file**로 업로드
4. 대화 시작 → raw 프롬프트 입력

**Option B — Direct Paste**

1. `CLAUDE.md` 전체 복사
2. 아무 Claude 인터페이스의 **system prompt**에 붙여넣기
3. raw 프롬프트를 user message로 전송

**Option C — API Integration**

```python
import anthropic

client = anthropic.Anthropic()

with open("CLAUDE.md", "r", encoding="utf-8") as f:
    system_prompt = f.read()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=8192,
    system=system_prompt,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},   # 기본값 high, 난도 높으면 xhigh/max
    messages=[
        {"role": "user", "content": "prompt: Your raw prompt here"}
    ],
)
print(response.content[0].text)
```

> API 주의: `temperature`/`top_p`/`top_k` 설정 금지(400 에러), assistant prefill 금지, adaptive thinking은 기본 off라 명시적 활성화 필요.

레포: `github.com/CheswickDEV/claude-opus-4.8-prompt-optimizer`

---

## 2. johnpsasser/claude-code-prompt-optimizer

Claude Code용 Hook. 간단한 프롬프트를 상세하고 구조화된 지시로 확장한다. 프롬프트에 `<optimize>` 태그를 붙이면 Hook이 가로채 Claude의 extended thinking 모드로 돌려, 원래 요청을 아키텍처·엔드포인트·에러 처리·인증·검증·테스트까지 포괄하는 사양으로 부풀린다. 사실상 prompt engineering을 대신 수행하는 셈이다.

### 사용 예

```
<optimize> build me a REST API for a todo app
```

→ Hook이 이를 가로채 architecture, endpoints, error handling, auth, validation, testing을 망라한 구조화된 스펙으로 확장. 성능 관련 요청이면 profiling 단계, bottleneck 식별, 우선순위화된 refactoring 타깃, 벤치마크 기준을 포함한 계획으로 확장된다.

### 장점

- **태그 기반 명시적 발화** — `<optimize>`를 붙인 프롬프트만 확장하므로 의도치 않은 개입이 없음
- **extended thinking 활용** — 단순 rewrite가 아니라 추론을 거친 사양 확장
- **튜닝 용이** — model, fallback model, timeout, system prompt가 `optimizer.config.json` / `system-prompt.md`에 분리돼 있어 TypeScript 수정 없이 조정 가능. 디버그 로그는 `/tmp/claude-code-hook-debug.log`

### 단점

- **Claude Code 전용** — claude.ai 웹/앱에서는 사용 불가
- **인증 설정 복잡** — OAuth 토큰 / API key 우선순위 해석 로직이 있어 초기 셋업 시 환경변수 이해 필요
- **Node 의존성** — npm 기반 설치, 별도 Agent SDK 인증 구성 요구

### 설치 가이드

```bash
git clone https://github.com/johnpsasser/claude-code-prompt-optimizer.git
cd claude-code-prompt-optimizer
npm run install-hook
```

installer가 의존성, 인증 셋업, hook 설정, 검증까지 처리한다. 인증 토큰은 다음과 같이 발급·등록:

```bash
claude auth token
export CLAUDE_CODE_OAUTH_TOKEN="your-oauth-token"   # shell profile에 추가
```

수동 hook 등록 시 `~/.claude/settings.json`(또는 프로젝트 설정)에 `UserPromptSubmit` hook으로 `src/hooks/optimize-prompt.sh` 경로를 지정한다.

레포: `github.com/johnpsasser/claude-code-prompt-optimizer`

---

## 3. severity1/claude-code-prompt-improver

"Type vibes, ship precision." Claude Code용 지능형 프롬프트 개선 plugin(Hook + Skill). 모든 프롬프트를 무조건 다듬지 않고, **명확한 프롬프트는 그대로 통과시키고 모호한 프롬프트만 골라** 리서치와 질문을 거치게 한다. 프롬프트 제출·도구 사용·서브에이전트 시작 시점에 적시 컨텍스트를 주입해 "첫 출력"의 품질을 높이는 것이 목표 — 교정 왕복 횟수를 줄여 토큰과 시간을 아낀다.

### 동작 방식

1. Hook이 프롬프트를 받아 ~189 토큰짜리 평가 프롬프트로 명확성 판정
2. **모호** → prompt-improver skill 발화 → 리서치 계획(TodoWrite) → Explore 서브에이전트로 Glob/Grep/Web/multi-file Read → 결과 종합 → 근거 기반 질문(1–6개)을 사용자에게 제시 → 답변 반영해 원 요청 실행
3. **명확** → skill 로드 없이 즉시 진행

설계 원칙: "fire wide, self-cancel cheap" — 놓친 nudge는 교정 한 바퀴를 낭비하지만 잘못 발화한 nudge는 무시되는 몇 토큰만 소모하므로, 고-recall 게이트를 쓰되 각 nudge가 안 맞으면 스스로 취소한다.

### 사용 예

```
fix the bug
```

→ 모호하다고 판정 → 코드베이스 리서치 후 "어떤 파일/증상/재현 조건인가" 등 근거 있는 질문 1–6개 제시 → 답변을 받아 실제 수정 수행. 반면 충분히 구체적인 프롬프트는 개입 없이 바로 실행된다.

### 장점

- **선별 개입** — 대부분의 프롬프트는 변형 없이 통과, 필요할 때만 발화해 오버헤드 최소
- **첫 출력 품질 최적화** — 단어 rewrite를 넘어 "프롬프트 → 출력" 경로 전체를 개선 (질문 + 컨텍스트 주입)
- **투명성** — 주입된 컨텍스트가 대화에 노출됨
- **검증된 규모** — ~1.4k stars로 커뮤니티 채택·유지보수 활발

### 단점

- **Claude Code 전용** — 웹/앱 미지원
- **개입 시 추가 턴 발생** — 모호 판정 시 질문 단계가 끼어 즉답을 원하는 흐름과 충돌할 수 있음
- **설정 학습 곡선** — plugin/hook/skill/nudge registry 구조 이해가 필요

### 설치 가이드

`.claude-plugin` 구조의 Claude Code plugin이므로 plugin marketplace 방식으로 설치한다. (정확한 명령은 레포 README 최신본 확인 권장)

```
# Claude Code 내에서
/plugin marketplace add severity1/claude-code-prompt-improver
/plugin install prompt-improver
```

또는 수동 설치 시 레포를 clone해 `hooks/` · `skills/prompt-improver/`를 `~/.claude/` 이하에 배치하고 settings에 hook을 등록한다.

레포: `github.com/severity1/claude-code-prompt-improver`

---

## 4. Hashaam101/prompt-optimizer

Claude Code skill. 두 가지 모드를 제공한다. **auto 모드**는 설치 후 모든 프롬프트를 조용히(silent) 정제해 더 나은 결과를 유도하고, **manual 모드**는 `/optimize {prompt}`로 정제된 프롬프트를 실행하는 대신 텍스트로 보여준다 — 프롬프트를 재사용하거나 더 나은 작성법을 학습하는 데 유용하다.

### 사용 예

```
# manual: 정제 결과를 텍스트로 확인
/optimize 분기 매출 데이터 분석해줘

# 또는 접두사 방식
optimize: 분기 매출 데이터 분석해줘
optimize prompt: 분기 매출 데이터 분석해줘
```

설치만 해두면 auto 모드(Mode 1)가 매 프롬프트마다 자동 활성화되어 별도 슬래시 명령 없이도 정제가 적용된다.

### 장점

- **이중 모드** — 평소엔 자동 정제, 필요 시 `/optimize`로 정제문만 추출해 재사용·학습
- **설치 간단** — SKILL.md 파일 하나 복사로 끝
- **silent 동작** — auto 모드는 워크플로우를 방해하지 않음

### 단점

- **Claude Code 전용**
- **auto 모드의 불투명성** — 자동 정제가 조용히 일어나 무엇이 바뀌었는지 추적이 어려울 수 있음 (manual 모드로 보완)
- **소규모 레포** — 커뮤니티 검증 얇음

### 설치 가이드

전역(모든 프로젝트) 또는 프로젝트 단위로 `SKILL.md`를 복사한다.

```bash
# 전역 설치 (Linux/macOS)
cp SKILL.md ~/.claude/skills/prompt-optimizer.md

# 프로젝트 단위 (Linux/macOS)
cp SKILL.md .claude/skills/prompt-optimizer.md
```

```powershell
# Windows (PowerShell) — 전역
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\prompt-optimizer.md"
```

설치 후 자동 활성화. `/optimize`로 manual 모드 호출.

레포: `github.com/Hashaam101/prompt-optimizer`

---

## 5. nidhinjs/prompt-master

"모든 AI 툴을 위한 정확한 프롬프트를 작성하는 Claude skill." 한 번에 정확한 프롬프트를 만들어 재-프롬프트로 인한 토큰·크레딧 낭비를 없애는 것을 목표로 한다. Claude·ChatGPT·Gemini·o1/o3·Cursor·Claude Code·GitHub Copilot·Windsurf·Bolt·v0·Lovable·Perplexity·Midjourney·DALL-E·Stable Diffusion·ComfyUI·Sora·Runway·ElevenLabs·Zapier·Make 등 타깃 툴별로 최적 프롬프트를 생성한다.

설계 철학: "최고의 프롬프트는 가장 긴 것이 아니라 모든 단어가 load-bearing인 것." 긴 세션에서 가장 큰 낭비는 "AI가 앞서 정한 내용을 잊는 것"이라 보고, 메모리 블록으로 결정 사항을 유지한다.

### 사용 예

```
Build a claude code prompt for a landing page for a business dashboard
that looks and feels exactly like notion - smooth animations, clean ui
```

→ 타깃(Claude Code), framework, 토큰 추정, 전략을 라우팅한 뒤 production-quality 사양으로 출력. Midjourney를 타깃하면 comma-separated descriptor, lighting/mood 앵커링, aspect ratio·version 고정, negative prompt 같은 이미지-툴 특화 형식으로 생성된다.

### 장점

- **멀티 툴 라우팅** — Claude 외 ChatGPT·Midjourney·코딩 에이전트 등 툴별 최적 형식 자동 적용
- **메모리 유지** — 세션 내 결정 사항을 기억해 재-프롬프트 낭비 감소
- **활발한 업데이트** — Opus 4.8 호환(v1.7.0), 버전-aware routing(4.6/4.7/4.8), Prompt Decompiler 모드 등 지속 갱신

### 단점

- **Claude를 "프롬프트 생성기"로 사용** — Claude 자체 출력을 직접 개선한다기보다, 다른 툴에 넣을 프롬프트를 만들어주는 성격이 강함
- **Claude Code skill 설치 기반** — skill 환경 필요
- **소규모 레포** — 커뮤니티 검증 얇음

### 설치 가이드

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/nidhinjs/prompt-master.git ~/.claude/skills/prompt-master
```

설치 후 trigger 조건에 맞을 때 skill이 자동 발화. references 폴더의 템플릿이 타깃 툴별 출력을 보조한다.

레포: `github.com/nidhinjs/prompt-master`

---

## 6. 선택 가이드

| 상황 | 추천 |
|---|---|
| claude.ai 웹/앱 또는 API에서 구조화된 프롬프트를 반복 생성 | **CheswickDEV 4.8** (Project로 등록) |
| Claude Code에서 즉석으로 특정 프롬프트만 골라 확장 | **johnpsasser** (`<optimize>` 태그) |
| Claude Code 헤비유저, 교정 왕복을 줄이고 첫 출력 품질을 높이고 싶음 | **severity1** (선별 개입) |
| Claude Code에서 자동 정제 + 수동 정제문 추출을 함께 쓰고 싶음 | **Hashaam101** (이중 모드) |
| Claude 외 ChatGPT·Midjourney·코딩 에이전트용 프롬프트를 한 곳에서 생성 | **nidhinjs** (멀티 툴) |
| 잘 만들어진 프롬프트 "예시"를 참고하고 싶음 (도구 X) | `langgptai/awesome-claude-prompts` 등 큐레이션 모음 |

**조합 팁**: 환경이 Claude Code라면 selective 개입형(severity1)을 상시 깔아두고, 별도로 정식 프롬프트 자산을 만들 때 CheswickDEV 4.8을 claude.ai Project로 운용하는 식의 병행이 효과적이다. 반복 출력의 일관성이 중요한 워크플로우(예: 정형 리포트, 정량 분석 프롬프트)라면 모음집보다 옵티마이저의 컴포넌트 프레임워크나 직접 만든 템플릿을 reference로 등록하는 쪽이 안정적이다.

---

## 7. 공통 주의사항

- **모델 종속성 확인** — Opus 4.8 전용으로 튜닝된 도구(CheswickDEV 등)는 다른 모델에서 규칙 일부가 안 맞을 수 있다.
- **자동 발화형의 불투명성** — auto 모드/silent hook은 무엇이 바뀌었는지 추적이 어려울 수 있으므로, 가능하면 변경 내용을 노출하는 manual 모드나 투명성 옵션을 병행한다.
- **인증·토큰 관리** — Hook 계열은 OAuth 토큰/API key를 다루므로 환경변수와 shell profile 노출에 유의한다.
- **레포 신뢰도** — star·commit·이슈 활동을 확인하고, 설치 명령은 항상 각 레포의 최신 README와 대조한다. 본 문서의 명령은 작성 시점 기준이다.
- **공식 가이드 병행** — 도구에만 의존하지 말고 Anthropic 공식 prompt engineering 문서(`docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview`)를 함께 참고하면 도구의 산출물을 더 잘 검증할 수 있다.

---

*작성 기준일: 2026-06-21. 각 프로젝트의 기능·설치 방법은 업데이트될 수 있으므로 레포 README 최신본을 확인할 것.*
