# Headroom (헤드룸) 완전 가이드
> 설명 · 설치 · 설정 · DeepSeek V4 Pro / Open Code 연동까지

---

## 목차

1. [헤드룸이란?](#1-헤드룸이란)
2. [설치하기 (Proxy 모드 권장)](#2-설치하기-proxy-모드-권장)
3. [AI 도구 연동하기](#3-ai-도구-연동하기-proxy-모드)
4. [DeepSeek V4 Pro + Open Code 환경에서 사용하기](#4-deepseek-v4-pro--open-code-환경에서-사용하기)
5. [다른 사용 방법](#5-헤드룸의-다른-사용-방법)
6. [유용한 명령어 및 팁](#6-유용한-명령어-및-팁)
7. [문제 해결 (Troubleshooting)](#7-문제-해결-troubleshooting)
8. [레퍼런스 및 주요 링크](#8-레퍼런스-및-주요-링크)

---

## 1. 헤드룸이란?

**Headroom**은 AI 에이전트(특히 코딩용 AI 모델)와의 통신에서 발생하는 방대한 컨텍스트(코드, 로그, 검색 결과 등)를 지능적으로 압축하여 **비용은 최대 95%까지 줄이면서도 응답 품질은 유지**하는 오픈소스 프로젝트입니다.

> Netflix 시니어 엔지니어 Tejas Chopra가 개발, 2026년 1월 오픈소스로 공개. Apache 2.0 라이선스.

### 왜 필요한가?

AI가 작업을 수행할 때는 매 요청마다 다음과 같은 대량의 컨텍스트가 전송됩니다.

- 코드 검색 결과
- 로그 파일
- API 응답
- 이전 대화 기록

이는 **비용 증가**와 **정보 과부하**로 이어져 AI가 중요한 부분을 놓치게 만듭니다.

### 작동 방식

```
[AI 에이전트] ──요청──▶ [Headroom Proxy] ──압축된 요청──▶ [LLM API]
                              │
                         스마트 압축
                    (반복·불필요 정보 제거)
                    CacheAligner 적용
```

| 단계 | 설명 |
|------|------|
| **요청 가로채기** | AI 에이전트와 API 사이에 위치하여 모든 요청을 중간에서 가로챕니다 |
| **스마트 압축** | 반복적이거나 덜 중요한 정보를 참조 링크로 대체하거나 압축합니다 |
| **캐시 정렬** | CacheAligner 기술로 프롬프트 캐시 파괴 문제를 해결, 비용 절감 극대화 |

### 주요 압축 엔진

| 엔진 | 역할 |
|------|------|
| `SmartCrusher` | 범용 JSON 배열·중첩 객체 압축 |
| `CodeCompressor` | Python, JS, Go, Rust, Java, C++ AST-aware 압축 |
| `Kompress-base` | HuggingFace 훈련 모델 기반 에이전트 트레이스 압축 |
| `CacheAligner` | Anthropic/OpenAI KV 캐시 prefix 안정화 |
| `IntelligentContext` | 중요도 점수 기반 컨텍스트 피팅 |
| `CCR` | 가역 압축 (LLM이 필요 시 원본 검색 가능) |

### 주요 효과

| 구분 | 절감 효과 |
|------|-----------|
| 토큰 절감 | **60% ~ 95%** |
| 비용 절감 | **최대 ~50%** (동일 예산으로 약 2배 사용 가능) |
| 품질 | 동등 또는 소폭 향상 |

---

## 2. 설치하기 (Proxy 모드 권장)

Proxy 모드는 기존 코드 변경 없이 가장 간단하게 헤드룸을 사용할 수 있는 방법입니다.  
DeepSeek V4 Pro, Open Code 등 모든 LLM과 도구에서 동작합니다.

### 2.1 헤드룸 설치

```bash
pip install "headroom-ai[proxy]"
```

> 전체 기능 설치: `pip install "headroom-ai[all]"`

### 2.2 프록시 서버 실행

```bash
headroom proxy --port 8787
```

- `--port 8787` : 프록시 서버가 사용할 포트 지정 (다른 포트도 가능)
- 정상 실행 시 `Listening on http://localhost:8787` 메시지 출력

### 2.3 정상 작동 확인

```bash
curl http://localhost:8787/health
```

성공 응답:

```json
{"status": "healthy", "version": "x.x.x"}
```

---

## 3. AI 도구 연동하기 (Proxy 모드)

프록시 서버가 실행 중인 상태에서, 각 AI 도구가 이 프록시를 통해 API를 호출하도록 설정합니다.

### 기본 원리

| 호환 방식 | 환경 변수 |
|-----------|-----------|
| OpenAI 호환 도구 | `OPENAI_BASE_URL=http://localhost:8787/v1` |
| Anthropic 호환 도구 | `ANTHROPIC_BASE_URL=http://localhost:8787` |

### 도구별 연동 예시

| 도구 | 명령어 |
|------|--------|
| Open Code (OpenClaude) | `OPENAI_BASE_URL=http://localhost:8787/v1 openclaude` |
| DeepSeek V4 Pro | `OPENAI_BASE_URL=http://localhost:8787/v1 deepseek` |
| Cursor | `OPENAI_BASE_URL=http://localhost:8787/v1 cursor` |
| Claude Code | `ANTHROPIC_BASE_URL=http://localhost:8787 claude` |
| Codex CLI | `OPENAI_BASE_URL=http://localhost:8787/v1 codex` |
| Aider | `OPENAI_BASE_URL=http://localhost:8787/v1 aider` |
| Copilot CLI | `OPENAI_BASE_URL=http://localhost:8787/v1 copilot` |
| Continue | 설정 파일에 `OPENAI_BASE_URL=http://localhost:8787/v1` 입력 |

> **💡 영구 설정 팁:** `~/.bashrc` 또는 `~/.zshrc`에 아래 라인 추가
> ```bash
> export OPENAI_BASE_URL=http://localhost:8787/v1
> ```

---

## 4. DeepSeek V4 Pro + Open Code 환경에서 사용하기

### 단계별 실행

**1단계: 헤드룸 프록시 실행**

```bash
headroom proxy --port 8787
```

**2단계: Open Code를 프록시를 통해 실행**

```bash
OPENAI_BASE_URL=http://localhost:8787/v1 openclaude
```

DeepSeek V4 Pro를 직접 호출하는 경우:

```bash
OPENAI_BASE_URL=http://localhost:8787/v1 deepseek-v4-pro --model deepseek-v4-pro
```

**3단계: 정상 작동 확인**

- Open Code에서 일반적인 코딩 질문을 입력
- 헤드룸 프록시 터미널에 압축 통계(줄어든 토큰 수) 표시됨
- `headroom stats` 명령어로 누적 절감량 확인 가능

> **✅ 호환성 보장:** 헤드룸은 프록시 레벨에서 동작하므로 DeepSeek V4 Pro의 고유한 API 형식이나 Open Code의 통신 방식을 전혀 침해하지 않습니다.

---

## 5. 헤드룸의 다른 사용 방법

### 5.1 Agent Wrap (에이전트 래핑) — 가장 간편

```bash
headroom wrap openclaude
headroom wrap cursor
```

이후 `openclaude` 실행 시 자동으로 헤드룸이 적용됩니다.

> Quick Win: `pip install "headroom-ai[all]"` 후 `headroom wrap claude`

### 5.2 MCP 서버 (Model Context Protocol)

여러 MCP 클라이언트를 사용한다면 이 방법이 효율적입니다.

```bash
headroom mcp install
```

제공되는 MCP 도구:

| 도구 | 설명 |
|------|------|
| `headroom_compress` | 텍스트 압축 요청 |
| `headroom_retrieve` | 압축된 컨텍스트 검색 |
| `headroom_stats` | 통계 조회 |

### 5.3 Python 라이브러리

```python
from headroom import compress

compressed = compress(
    text="매우 긴 로그 파일 내용...",
    model="deepseek-v4-pro"  # 모델 지정 가능
)
```

### 5.4 멀티 에이전트 환경

Claude + Codex를 병렬 운용하는 경우, SharedContext로 자동 중복 제거된 공통 압축 컨텍스트 스토어를 공유할 수 있습니다.

---

## 6. 유용한 명령어 및 팁

| 명령어 | 설명 |
|--------|------|
| `headroom stats` | 지금까지 절감한 토큰/비용 통계 출력 |
| `headroom reset` | 통계 초기화 |
| `headroom proxy --help` | 프록시 옵션 전체 보기 |
| `headroom config` | 설정 파일 편집 (압축 수준 등 조정 가능) |

### 압축 수준 조정 (config.yaml)

```yaml
compression:
  level: "balanced"  # "aggressive" | "balanced" | "conservative"
  cache_alignment: true
```

### 빠른 시작 (원라이너)

```bash
# 설치 + 프록시 실행
pip install "headroom-ai[proxy]" && headroom proxy --port 8787

# 다른 터미널에서
OPENAI_BASE_URL=http://localhost:8787/v1 openclaude
```

---

## 7. 문제 해결 (Troubleshooting)

**Q: 프록시 서버가 실행되지 않아요.**

- 포트 충돌 확인: `lsof -i :8787` → 다른 포트 사용 시 `--port 8788` 등으로 변경
- 헤드룸 재설치: `pip install --upgrade "headroom-ai[proxy]"`

**Q: 도구에서 "Connection refused" 오류가 나요.**

- 프록시 서버가 먼저 실행되어 있는지 확인
- 환경 변수의 포트 번호 일치 여부 확인 (`http://localhost:8787`)

**Q: DeepSeek V4 Pro 특정 파라미터가 안 먹혀요.**

- 헤드룸은 파라미터를 무조건 통과시키므로, 도구 자체의 문제일 가능성이 높음
- 헤드룸 없이 먼저 테스트 후 비교

**Q: 절감 효과가 거의 없어요.**

- `headroom stats`로 실제 압축률 확인
- 컨텍스트가 이미 작다면 압축 효과가 미미할 수 있음

---

## 8. 레퍼런스 및 주요 링크

### 공식 리소스

| 리소스 | URL |
|--------|-----|
| 🏠 공식 홈페이지 | [headroomlabs.ai](https://headroomlabs.ai/) |
| 📦 GitHub 저장소 | [github.com/chopratejas/headroom](https://github.com/chopratejas/headroom) |
| 📚 공식 문서 (docs/) | [github.com/chopratejas/headroom/tree/main/docs](https://github.com/chopratejas/headroom/tree/main/docs) |
| 🐍 PyPI 패키지 | [pypi.org/project/headroom-ai](https://pypi.org/project/headroom-ai/) |

### 통합 가이드 (공식 문서)

| 가이드 | URL |
|--------|-----|
| LangChain 연동 | [docs/langchain.md](https://github.com/chopratejas/headroom/blob/main/docs/langchain.md) |
| CCR (가역 압축) 가이드 | [docs/ccr.md](https://github.com/chopratejas/headroom/blob/main/docs/ccr.md) |
| Metrics & Monitoring | [docs/metrics.md](https://github.com/chopratejas/headroom/blob/main/docs/metrics.md) |

### 참고 아티클

| 제목 | URL |
|------|-----|
| Building Cost-Efficient Agents with Headroom (Medium) | [subratpati.medium.com](https://subratpati.medium.com/building-cost-efficient-agents-with-headroom-context-compression-for-llm-applications-b665128153b6) |
| Headroom: Cut LLM Token Usage by Up to 95% (DEV.to) | [dev.to/arshtechpro](https://dev.to/arshtechpro/headroom-cut-your-llm-token-usage-by-up-to-95-without-changing-your-answers-5g06) |
| Headroom Token Compression 실전 가이드 (Build This Now) | [buildthisnow.com](https://www.buildthisnow.com/blog/tools/extensions/headroom-token-compression) |

### 관련 기술 참고

| 자료 | 설명 |
|------|------|
| Phil Schmid — Context Engineering 원칙 | 헤드룸 철학의 기반: "Raw > Compaction > Summarization" 우선순위 |
| Anthropic Prompt Caching 문서 | CacheAligner 이해를 위한 배경지식 |
| OpenAI Compatible API 스펙 | Proxy 모드 BASE_URL 연동 기반 |

---

> **버전 정보:** 이 문서는 Headroom v0.22 기준으로 작성되었습니다 (2026년 6월 기준).  
> Apache 2.0 License | 개발자: Tejas Chopra (Netflix Senior Engineer)
