# Quivr: Open Source Second Brain Powered by Generative AI

## 1. 개요

Quivr는 오픈소스 RAG(Retrieval-Augmented Generation) 플랫폼으로, 개인 또는 기업의 데이터를 지능형 AI 어시스턴트로 전환해주는 "두 번째 두뇌(Second Brain)"입니다. 사용자는 단순히 문서를 업로드하고 자연어로 질문하는 것만으로 방대한 정보를 손쉽게 검색하고 활용할 수 있습니다.

Quivr는 38,000개 이상의 GitHub 스타를 보유하며 전 세계 개발자들의 주목을 받고 있으며, 50,000명 이상의 사용자와 6,000개 이상의 기업이 Quivr를 활용 중입니다. Y Combinator의 지원을 받는 이 프로젝트는 20년 지기 세 명의 프랑스 친구들이 설립했습니다.

---

## 2. 왜 Quivr인가? (Pain Point & Solution)

기업 환경에서 업무 시간의 약 20%는 단순히 정보를 찾는 데 소비됩니다. 직원들은 다음과 같은 어려움을 반복적으로 겪습니다:

- 휴가 중인 동료에게 긴급 정보를 요청해야 하는 상황
- 같은 정보를 반복해서 묻고 답하는 비효율
- 필요한 정보가 어디에 있는지, 심지어 존재하는지조차 알지 못함

Quivr는 이러한 문제를 해결하기 위해 기업의 모든 도구, 문서, API, 데이터베이스를 연결하고 이들과 대화할 수 있는 AI 오픈소스 플랫폼을 제공합니다. Quivr는 다음과 같은 작업을 자동화합니다:

- 방대한 문서를 요약하여 핵심만 추출
- 데이터베이스에서 실행 가능한 정보 추출
- 문맥을 고려한 이메일 자동 작성

---

## 3. 핵심 특징

### 3.1 Opinionated RAG (최적화된 RAG 워크플로우)

Quivr는 사전 설계된 최적화된 RAG 워크플로우를 제공하여, 개발자가 RAG 파이프라인을 처음부터 구축할 필요가 없도록 합니다. 속도와 효율성을 핵심으로 설계되어 생산 환경에서 즉시 사용 가능합니다.

### 3.2 모든 파일 포맷 지원

다양한 파일 형식을 지원하며, 필요시 커스텀 파서를 추가할 수 있습니다:

- 텍스트 파일 (.txt)
- PDF 문서
- 마크다운 (.md)
- 프레젠테이션 (.ppt, .pptx)
- 스프레드시트 (.csv, .xlsx)
- Word 문서
- 오디오 및 비디오 파일

### 3.3 멀티 LLM 지원

Quivr는 다양한 LLM(Large Language Model)을 지원하여 벤더 종속성을 방지합니다:

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Mistral
- Google (Gemma)
- Groq
- 로컬 모델 (Ollama) — 완전한 데이터 프라이버시 보장

### 3.4 커스터마이징 가능한 RAG 워크플로우

YAML 설정 파일을 통해 다음과 같은 요소를 세밀하게 조정할 수 있습니다:

- 리랭커(reranker) 모델 및 설정
- 히스토리 깊이(대화 맥락 반영 범위)
- LLM 온도(temperature) 및 최대 입력 토큰 수
- 검색 청크(chunk) 크기 및 개수

### 3.5 도구 통합 및 인터넷 검색

Quivr는 정적 문서 지식을 넘어, 인터넷 검색 및 외부 도구/API와 연결하여 동적 정보 수집과 실시간 인텔리전스를 구현할 수 있습니다.

### 3.6 Megaparse 통합

동일한 QuivrHQ에서 개발한 Megaparse는 대규모 문서를 효율적으로 파싱하는 도구로, 수천 개의 파일을 전처리하여 Quivr의 "Brain"에 직접 연결할 수 있습니다.

### 3.7 프라이버시 및 자체 호스팅

데이터 프라이버시가 중요한 기업 및 개발자를 위해 로컬 배포 및 자체 호스팅을 지원합니다. 데이터는 사용자의 통제 아래 유지되며, 외부 API 호출 없이도 완전한 온프레미스 환경에서 동작 가능합니다.

### 3.8 기술 스택

| 계층 | 기술 | 특징 |
|------|------|------|
| 프론트엔드 | Next.js + Vercel | SSR 기반, 자동 배포 |
| 백엔드 API | FastAPI | Python 기반 고성능 API 프레임워크 |
| 비동기 작업 | Celery + Queue | 대용량 파일 임베딩 및 인덱싱 처리 |
| 벡터 저장소 | PGVector / FAISS | 고성능 의미 검색 |
| 인증/DB | Supabase | 오픈소스 Firebase 대체제 |

---

## 4. 개발자를 위한 장점

### 4.1 빠른 시작 (30초면 OK)

```bash
pip install quivr-core
# 단 5줄의 코드로 RAG 시스템 구축 완료
```

### 4.2 풍부한 API 지원

Quivr는 RESTful API를 제공하며, Swagger 문서를 통해 쉽게 탐색하고 테스트할 수 있습니다. API 키 기반 인증을 지원하여 애플리케이션에 쉽게 통합 가능합니다.

### 4.3 확장 가능한 아키텍처

- 커스텀 파일 파서 추가 가능
- RAG 워크플로우 노드 확장 가능
- 벡터 저장소 교체 가능
- 다양한 임베딩 모델 지원 (LangChain 통합)

### 4.4 활발한 오픈소스 커뮤니티

- GitHub에서 38k+ 스타, 활발한 기여
- 정기적인 업데이트 및 기능 개선
- 이슈 대응 및 PR 리뷰 활발

### 4.5 개발 생산성 향상

- RAG의 복잡한 내부 구조를 추상화하여 비즈니스 로직에 집중 가능
- YAML 기반 설정으로 코드 변경 없이 RAG 전략 실험 가능
- 다양한 예제 코드 제공 (Chainlit, Streamlit 통합)

---

## 5. 설치 및 사용 방법

### 5.1 Python 패키지 설치 (Quick Start)

가장 빠르게 시작하려면 quivr-core 패키지를 설치하세요.

```bash
# Step 1: 패키지 설치
pip install quivr-core

# 설치 확인
python -c "import quivr_core; print('Quivr installed!')"
```

### 5.2 기본 사용 예시

```python
from quivr_core import Brain

# 1. 문서로 Brain 생성하기
brain = Brain.from_files(
    name="my_smart_brain",
    file_paths=["./my_document.pdf", "./my_notes.txt"]
)

# 2. Brain에게 질문하기
answer = brain.ask("이 문서의 핵심 내용을 요약해줘")
print(answer.answer)

# 3. 대화형 인터페이스 실행
while True:
    question = input("질문: ")
    if question.lower() == "exit":
        break
    response = brain.ask(question)
    print(f"답변: {response.answer}")
```

### 5.3 Docker 기반 로컬 배포 (Self-Hosted)

데이터 프라이버시가 중요하거나 완전한 기능을 활용하려면:

```bash
# Step 1: 저장소 클론
git clone https://github.com/quivrhq/quivr.git && cd quivr

# Step 2: 환경 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# Step 3: Docker로 실행
docker compose pull
docker compose up

# Step 4: 접속
# 웹 UI: http://localhost:3000
# API 문서: http://localhost:5050/docs
```

### 5.4 커스텀 RAG 워크플로우 설정하기

YAML 파일로 RAG 전략을 커스터마이즈할 수 있습니다:

```yaml
# custom_rag.yaml
workflow_config:
  name: "advanced_rag"
  max_history: 10
  reranker_config:
    supplier: "cohere"
    model: "rerank-multilingual-v3.0"
    top_n: 5
  llm_config:
    max_input_tokens: 4000
    temperature: 0.3
```

```python
from quivr_core import Brain
from quivr_core.config import RetrievalConfig

brain = Brain.from_files(
    name="custom_brain",
    file_paths=["./data/*.pdf"]
)

config = RetrievalConfig.from_yaml("./custom_rag.yaml")
answer = brain.ask("질문", retrieval_config=config)
```

### 5.5 Chainlit으로 채팅 UI 만들기

```bash
cd examples/chatbot
rye sync
rye run chainlit run chainlit.py
```

### 5.6 API 키 발급 및 사용

```bash
# 1. Quivr 웹앱에 로그인
# 2. /user 페이지에서 API 키 생성
# 3. API 호출 시 Bearer 토큰 사용

curl -X GET https://api.quivr.app/brains/ \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 6. 'Brain' 개념 이해하기

Quivr의 핵심 개념은 "Brain"(두뇌)입니다. Brain은 사용자의 지식을 저장하고 처리하는 기본 컴포넌트입니다.

- 하나의 Brain에는 여러 문서를 연결할 수 있음
- 각 Brain은 고유한 RAG 설정과 LLM을 가질 수 있음
- Public/Private 설정 가능 (공유 또는 비공개)
- Brain Marketplace를 통해 다른 사용자의 Brain도 활용 가능

---

## 7. 참고 자료 (References)

### 공식 문서

- 공식 홈페이지: https://quivr.app
- Core 문서: https://core.quivr.com
- API Swagger 문서: https://api.quivr.app/docs

### GitHub 저장소

- QuivrHQ/quivr: https://github.com/quivrhq/quivr (38k+ stars)
- Megaparse (문서 파싱 도구): https://github.com/quivrhq/megaparse

### 빠른 링크

- Quick Start: https://core.quivr.com/en/stable/
- Brain API 가이드: POST /brains/ 엔드포인트로 Brain 생성 가능
- 채팅 API: GET /chat/{chat_id}/history로 대화 기록 조회 가능

### 커뮤니티

- Product Hunt: https://www.producthunt.com/products/quivr
- Y Combinator Launch: https://www.ycombinator.com/launches/KPF-quivr

---

## 8. 결론

Quivr는 단순한 RAG 도구를 넘어, 개발자 친화적인 AI 프레임워크로 설계되었습니다. 간결함(simplicity)과 확장성(extensibility)을 최우선으로 하여, 개인 개발자부터 대규모 AI 팀까지 생산성 향상에 기여하고 있습니다.

Quivr를 선택해야 하는 이유:

- 오픈소스로 완전한 투명성과 자유로운 커스터마이징
- 30초 설치, 5줄 코드로 즉시 사용 가능
- 데이터 프라이버시 — 온프레미스 배포 지원
- 벤더 종속성 없음 — 모든 주요 LLM과 호환
- 활발한 커뮤니티와 지속적인 업데이트

"아이디어는 Obsidian과 같지만, AI 기능으로 한층 강화된 것"이라는 표현처럼, Quivr는 지식 관리의 새로운 패러다임을 제시합니다. 지금 바로 Quivr로 당신만의 '두 번째 두뇌'를 구축해보세요.
