# caveman + rtk: AI 코딩 어시스턴트 토큰 최적화 완전 가이드

> "Why use many token when few token do trick?" — caveman 슬로건

---

## 1. 개요

AI 코딩 어시스턴트의 사용이 보편화되면서 API 비용과 컨텍스트 토큰 소모는 개발자에게 점점 더 큰 부담으로 자리 잡고 있습니다. 이러한 배경 속에서 두 가지 혁신적인 오픈소스 프로젝트가 등장했습니다.

**caveman**은 "왜 많은 토큰을 쓸 때 적은 토큰으로도 해결되는데?"라는 발상에서 출발했습니다. AI가 불필요한 문구 없이 핵심만 전달하도록 유도하여 기술적 정확성은 100% 유지하면서 출력 토큰을 약 65~75% 절감합니다. 2026년 4월 출시 이후 단기간에 GitHub 스타 71,000개 이상(2026년 6월 기준)을 획득하며 큰 주목을 받았습니다.

rtk (Rust Token Killer)는 CLI 명령어 출력을 실시간으로 필터링하고 압축하는 프록시 도구로, LLM 컨텍스트에 도달하기 전에 입력 토큰 사용량을 60~90% 줄여줍니다. 단일 Rust 바이너리로 제작되어 의존성이 없고 10ms 미만의 오버헤드만 발생시키며, GitHub 스타 42,000개 이상을 보유하고 있습니다.

두 도구는 서로 다른 레이어(입력/출력)를 담당하기 때문에 함께 사용할 때 시너지가 극대화됩니다.

---

## 2. caveman

### 2.1 배경

caveman은 AI의 과도한 화법과 불필요한 문구가 비용과 효율성에 미치는 영향을 비판적으로 바라보며 탄생했습니다. 2026년 3월 arXiv에 발표된 논문("Brevity Constraints Reverse Performance Hierarchies in Language Models", 번호 2604.00025)은 AI가 짧고 간결하게 답할수록 특정 벤치마크에서 정확도가 오히려 26퍼센트포인트 향상될 수 있음을 증명했습니다. caveman은 이 학문적 발견을 실용적인 도구로 구현한 것입니다.

Claude는 기본적으로 친절하고 장황하게 응답하도록 훈련되어 있습니다. 이는 일반 대화에서는 장점이지만, 자동화된 개발 파이프라인에서는 고비용의 비효율입니다. caveman은 이 기본값을 바꾸어 코드·URL·파일 경로 등 기술적 정보는 byte-perfect로 유지하면서 자연어 포장만 걷어냅니다.

### 2.2 효과

| 항목 | 효과 |
|------|------|
| 출력 토큰 절감 | 평균 65~75% (범위 22~87%) |
| 응답 속도 향상 | 약 3배 빨라짐 |
| 기술적 정확도 | 100% 유지 |
| 입력 토큰 절감 | CLAUDE.md 등 설정 파일 압축 시 약 46% 절감 |
| API 비용 절감 예시 | 일 10,000회 API 호출 기준 연간 약 $7,665 절약 (Claude Sonnet 기준) |

### 2.3 압축 강도 레벨

caveman은 상황에 맞게 조절할 수 있는 4단계 강도 레벨을 제공합니다.

| 레벨 | 설명 | 예시 |
|------|------|------|
| `lite` | 문법 유지, 불필요한 수식어 제거 | "Your component re-renders because you create a new object reference each render." |
| `full` | 관사·인사말 제거, 문장 간결화 | "New object ref each render. Inline object prop = new ref = re-render." |
| `ultra` | 최대 압축, 전문 용어 유지 | "Inline obj prop → new ref → re-render. useMemo." |
| `wenyan` | 고전 중국어 스타일 | "物出新參照，致重繪。useMemo Wrap之。" |

#### 실제 비교 예시

일반 응답:
```
I've successfully completed the refactoring of the authentication module.
The changes include updating the token validation logic to handle edge cases
more gracefully, adding appropriate error handling, and ensuring backwards
compatibility with the existing API contracts.
```

caveman `ultra` 적용 후:
```
Auth module refactored. Token validation, error handling, backward compat.
```

동일한 정보를 전달하면서 토큰이 약 75% 줄어듭니다.

### 2.4 추가 유틸리티 명령어

| 명령어 | 기능 |
|--------|------|
| `/caveman-commit` | 50자 이내의 간결한 커밋 메시지 생성 |
| `/caveman-review` | 한 줄 PR 코멘트 작성 |
| `/caveman-stats` | 실시간 토큰 통계 및 비용 표시 |
| `/caveman-compress` | CLAUDE.md 등 설정 파일 압축 |

### 2.5 설치 및 사용법

**macOS / Linux / WSL**

```bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex
```

**Claude Code에서 활성화**

```bash
# 스킬 등록
claude skills add JuliusBrussee/caveman

# 기본 활성화
/caveman

# 강도 지정 활성화
/caveman ultra

# 비활성화
stop caveman
```

**CLAUDE.md / AGENTS.md에 직접 삽입 (시스템 프롬프트 방식)**

```text
You are a code assistant. Respond in caveman speak only. No pleasantries.
No greetings, no sign-offs, no narration. Just the answer.
```

> 지원 플랫폼: Claude Code, Codex, Gemini CLI, Cursor, Windsurf, Cline, GitHub Copilot 등 34개 이상의 AI 코딩 도구

### 2.6 주의사항

caveman은 **출력 토큰**에만 효과가 있습니다. 사고·추론(thinking/reasoning) 토큰은 영향을 받지 않습니다. "Caveman no make brain smaller. Caveman make mouth smaller." 따라서 코드 생성이 주된 작업인 경우보다는 대화·브레인스토밍·Q&A처럼 대화 왕래가 많은 세션에서 효과가 두드러집니다.

---

## 3. rtk (Rust Token Killer)

### 3.1 배경

AI 코딩 에이전트가 테스트 실행, 린팅, git 명령어 등을 수행할 때 생성되는 대량의 로그와 콘솔 출력은 엄청난 입력 토큰을 소비합니다. 예를 들어 `git status` 하나만으로도 2,000 토큰이 발생하고, `cargo test`를 실행하면 200줄 이상의 출력이 그대로 컨텍스트 윈도우에 주입됩니다. 에이전트는 그 모든 줄을 읽습니다.

rtk는 명령어 출력이 LLM 컨텍스트에 도달하기 전 단계에서 필터링과 압축을 적용하여 이 문제를 해결합니다. 워크플로우 변경 없이 투명하게 동작합니다.

### 3.2 효과

| 항목 | 수치 |
|------|------|
| 토큰 절감률 | 60~90% |
| 지원 명령어 | 100개 이상 |
| 오버헤드 | 10ms 미만 |
| 의존성 | 없음 (단일 Rust 바이너리) |
| GitHub 스타 | 42,000+ (2026년 6월) |
| 라이선스 | Apache-2.0 |

### 3.3 핵심 압축 전략

rtk는 네 가지 전략으로 출력을 압축합니다:

1. **Smart Filtering**: ANSI 코드, 진행 바, 주석, 과도한 공백, 보일러플레이트 제거
2. **Group Aggregation**: 비슷한 항목 묶기 (디렉터리별 파일, 유형별 오류 등)
3. **Intelligent Truncation**: 관련 컨텍스트 유지, 중복 제거
4. **Deduplication**: 반복되는 줄을 카운트로 축약

#### 압축 전후 비교: `git status`

일반 출력 (약 2,000 토큰):
```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be staged)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   src/auth/token.ts

no changes added to commit (use "git add" and/or "git commit -a")
```

rtk 적용 후 (약 400 토큰):
```
main...origin/main ~ Modified: 1 files src/auth/token.ts
```

LLM이 필요로 하는 정보(브랜치, 변경 파일)만 남기고 나머지를 제거합니다.

### 3.4 명령어별 절감 효과 (30분 세션 기준)

| 명령어 | 실행 횟수 | 일반 토큰 | rtk 적용 | 절감률 |
|--------|-----------|-----------|-----------|--------|
| `ls` / `tree` | 10회 | 2,000 | 400 | 80% |
| `cat` / `read` | 20회 | 40,000 | 12,000 | 70% |
| `grep` / `rg` | 8회 | 16,000 | 3,200 | 80% |
| `git status` | 10회 | 3,000 | 600 | 80% |
| `git diff` | 5회 | 10,000 | 2,500 | 75% |
| `git add/commit/push` | 8회 | 1,600 | 120 | 92% |
| `npm test` / `cargo test` | 5회 | 25,000 | 2,500 | 90% |
| `pytest` | 4회 | 8,000 | 800 | 90% |
| `go test` | 3회 | 6,000 | 600 | 90% |
| `docker ps` | 3회 | 900 | 180 | 80% |
| **합계** | — | **~118,000** | **~23,900** | **80%** |

### 3.5 설치 및 사용법

**Homebrew (macOS, 권장)**

```bash
brew install rtk
```

**Linux / macOS 직접 설치**

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# PATH에 추가 (zsh 기준)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Cargo로 설치**

```bash
cargo install --git https://github.com/rtk-ai/rtk
```

**Windows**: 릴리스 페이지에서 `rtk-x86_64-pc-windows-msvc.zip` 다운로드 후 `rtk.exe`를 PATH에 등록.

**Claude Code 연동 (자동 후킹)**

```bash
# Claude Code의 PreToolUse 훅 자동 설치
rtk init -g --claude-md

# 설치 확인
rtk --version

# 동작 테스트
rtk git status
```

`rtk init -g` 실행 시 `~/.claude/settings.json`에 `PreToolUse` 훅이 자동 추가되어 모든 Bash 명령이 rtk를 통해 라우팅됩니다. 수동으로 명령어 앞에 `rtk`를 붙일 필요가 없습니다.

**절감 통계 확인**

```bash
# 누적 절감 통계 및 ASCII 그래프 확인
rtk gain

# 일자별 JSON 내보내기
rtk gain --json

# 누락된 절감 기회 탐색
rtk discover
```

**설정 커스터마이징 (`~/.config/rtk/config.toml`)**

```toml
[filters]
exclude_commands = ["echo", "pwd"]
tee_mode = true   # 실패 시 원본 출력 복구

[project.myapp]
extra_filters = ["*.lock"]
```

### 3.6 주의사항

짧은 명령어는 rtk를 거쳐도 토큰이 오히려 약간 증가할 수 있습니다 (rtk 헤더 오버헤드). 이미 구조화된 짧은 출력은 그대로 통과시킵니다. `rtk gain`으로 실제 절감량을 확인하고, 한 주 후에도 10% 이상 절감이 없다면 `rtk init -g --uninstall`로 제거를 고려하세요.

---

## 4. caveman + rtk 통합 최적화 가이드

### 4.1 통합 개념: 입력 + 출력 양방향 최적화

두 도구는 서로 다른 레이어에서 동작하기 때문에 함께 사용할 때 효과가 극대화됩니다.

```
[개발자 명령어]
     |
     v
[rtk CLI Proxy]  <-- 명령어 출력 필터링/압축 (60~90% 절감) [입력 최적화]
     |
     v
[LLM으로 전송]   (입력 토큰 최적화 완료)
     |
     v
[LLM 처리]
     |
     v
[LLM 응답]
     |
     v
[caveman 변환]   <-- 응답을 간결하게 변환 (65~75% 절감) [출력 최적화]
     |
     v
[최종 압축 응답]

전체 절감률: 80~95%
```

| 도구 | 역할 | 절감 대상 |
|------|------|-----------|
| rtk | CLI 출력을 LLM에 넣기 전 압축 | 입력 토큰 |
| caveman | LLM 응답을 간결하게 변환 | 출력 토큰 |

### 4.2 통합 설정 방법

**Step 1: caveman 설치 및 스킬 등록**

```bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
claude skills add JuliusBrussee/caveman
```

**Step 2: rtk 설치 및 Claude Code 연동**

```bash
brew install rtk          # macOS
rtk init -g --claude-md   # Claude Code PreToolUse 훅 자동 설치
```

**Step 3: `~/.claude/settings.json`에 세션 시작 훅 추가**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "echo 'RTK proxy active. Caveman mode ready.'"
      }
    ]
  }
}
```

**Step 4: 셸 별칭 등록 (선택사항, `~/.zshrc` 또는 `~/.bashrc`)**

```bash
# rtk 프록시 자동 적용
for cmd in git ls cat grep rg cargo npm pytest go docker kubectl; do
  alias $cmd="rtk $cmd"
done
```

**Step 5: caveman 설정 파일 (프로젝트 루트에 `.caveman.config` 생성)**

```text
mode=ultra
exclude_files=Dockerfile,*.log
always_compress_tokens=true
```

### 4.3 심화: OmniRoute Stacked 모드

OmniRoute는 여러 LLM 최적화 엔진을 통합 파이프라인으로 묶어주는 도구입니다. caveman + rtk를 Stacked 모드로 연결하면 설정 하나로 두 도구가 자동으로 순서대로 동작합니다.

```json
{
  "compression": {
    "mode": "stacked",
    "pipeline": ["rtk", "caveman"],
    "caveman_intensity": "ultra",
    "rtk_filters_path": ".rtk/filters.json"
  }
}
```

### 4.4 절감 효과 요약

| 구성 | 절감률 | 절감 대상 |
|------|--------|-----------|
| rtk 단독 | 60~90% | 명령어 출력 (입력 토큰) |
| caveman 단독 | 65~75% | LLM 응답 (출력 토큰) |
| rtk + caveman 조합 | **80~95%** | 입력 + 출력 전체 |

### 4.5 실제 사용 시나리오별 명령어 예시

**시나리오 1: 테스트 실패 디버깅**

```bash
# rtk가 실패한 테스트만 추출하고, caveman이 분석을 간결하게 반환
rtk cargo test
# caveman 응답 예시: "3 tests fail: auth::token_expired, db::conn_timeout, api::rate_limit. See logs."
```

**시나리오 2: 코드 리뷰 요청**

```bash
# rtk가 diff를 압축하고, caveman이 리뷰를 한 줄로 반환
rtk git diff HEAD~1
/caveman-review
# 응답 예시: "Missing null check in token.ts:42. Add early return."
```

**시나리오 3: 커밋 메시지 생성**

```bash
rtk git status
/caveman-commit
# 응답 예시: "fix: null check in token validation"
```

**시나리오 4: 긴 로그 요약**

```bash
rtk grep "ERROR" app.log
# caveman ultra 응답 예시: "14 errors: 11x DB timeout, 3x auth fail. Peak 14:30-15:00."
```

**시나리오 5: 의존성 점검**

```bash
rtk npm list --depth=0
# rtk가 중복·불필요한 정보를 제거하고 핵심 패키지 목록만 전달
```

### 4.6 실사용자 경험

두 도구를 결합한 사용자들은 일관된 효과를 보고하고 있습니다. 30분 세션에서 소진되던 Claude Code 컨텍스트가 3시간 이상으로 연장되었으며, 반복적인 CLI 작업이 많은 환경 (테스트 주도 개발, 대규모 git 히스토리 탐색 등)에서 효과가 특히 두드러집니다.

---

## 5. 비용 절감 계산기 (빠른 추산)

Claude Sonnet 기준 (2026년 초 기준, 입력 $3/백만 토큰, 출력 $15/백만 토큰):

| 조건 | 월 비용 (최적화 전) | caveman 적용 후 | rtk 적용 후 | 두 도구 조합 |
|------|---------------------|-----------------|-------------|--------------|
| 개인 개발자 (소규모) | $50 | ~$17 | ~$15 | ~$5~10 |
| 팀 10명 (중간 규모) | $2,500 | ~$800 | ~$500 | ~$125~250 |
| 엔터프라이즈 파이프라인 | $10,000+ | ~$3,000 | ~$2,000 | ~$500~1,000 |

> 실제 절감액은 작업 유형, LLM 모델, 사용 패턴에 따라 달라집니다. `rtk gain`과 `/caveman-stats`로 실측값을 확인하세요.

---

## 6. 마치며

caveman과 rtk는 각각 독특한 방식으로 LLM 비용 최적화에 접근합니다. caveman은 **출력 최적화**, rtk는 **입력 최적화**에 특화되어 있어 두 도구가 완벽하게 상호 보완적입니다.

핵심 원칙은 단순합니다. LLM의 기본값은 비용 효율이 아닌 **인간 친화적 응답**에 최적화되어 있습니다. caveman은 응답 스타일을 바꾸고, rtk는 컨텍스트 노이즈를 제거합니다. 두 도구를 통해 AI 코딩 어시스턴트를 더 저렴하고, 더 빠르고, 더 집중된 방식으로 활용할 수 있습니다.

---

## 7. 참고 자료

| 항목 | 링크 |
|------|------|
| caveman GitHub | https://github.com/JuliusBrussee/caveman |
| rtk GitHub | https://github.com/rtk-ai/rtk |
| rtk 공식 사이트 | https://www.rtk-ai.app |
| arXiv 논문 (2604.00025) | https://arxiv.org/abs/2604.00025 |
| Claude Plugin Hub - caveman | https://www.claudepluginhub.com/plugins/juliusbrussee-caveman |

> GitHub 스타 수 및 수치 데이터는 2026년 6월 기준이며, 프로젝트는 지속적으로 발전하고 있습니다. 최신 정보는 각 저장소의 공식 문서를 참조하시기 바랍니다.
