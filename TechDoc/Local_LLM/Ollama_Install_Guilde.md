# Ollama 설치 및 기초 사용방법 — 토큰 거지를 위한 로컬 LLM 환경 구축해보기

ChatGPT나 Claude 같은 고성능 AI 모델을 사용하려면 매번 API 비용이 부담되시나요? 인터넷 연결 없이도, 비용 걱정 없이, 내 컴퓨터에서 직접 LLM을 실행할 수 있다면 어떨까요? 이 문서는 **Ollama**를 활용해 토큰 비용 없이 나만의 로컬 LLM 환경을 구축하는 방법을 단계별로 안내합니다. 문서 후반부에서는 최신 오픈소스 LLM 모델들의 특징과 장단점도 함께 소개하니, 내 PC 사양에 맞는 최적의 모델을 찾아보세요.

> **Ollama**는 로컬 컴퓨터에서 Llama, Mistral, Gemma 등 다양한 오픈소스 LLM을 마치 Docker 컨테이너처럼 쉽게 실행할 수 있게 해주는 도구입니다.


## 목차

- [1. Ollama란?](#1-ollama란)
- [2. Ollama 설치하기](#2-ollama-설치하기)
- [3. Ollama 기본 사용법](#3-ollama-기본-사용법)
- [4. 주요 LLM 모델 비교 (장단점 & 특징)](#4-주요-llm-모델-비교-장단점-특징)
- [5. 내 PC에 맞는 모델 선택 가이드](#5-내-pc에-맞는-모델-선택-가이드)
- [6. 함께 보면 좋은 팁과 도구](#6-함께-보면-좋은-팁과-도구)
- [7. 참고 자료](#7-참고-자료)


## 1. Ollama란?

Ollama는 **대규모 언어 모델(LLM)을 로컬 환경에서 쉽게 실행하고 관리할 수 있는 오픈소스 프레임워크**입니다. Docker가 컨테이너로 애플리케이션을 패키징하듯, Ollama는 모델 가중치와 설정을 하나로 묶어 간편하게 실행할 수 있게 해줍니다. 설치 후 몇 줄의 명령어만으로 Meta의 Llama, Mistral의 Mistral, Google의 Gemma 등 다양한 LLM을 내 컴퓨터에서 구동할 수 있습니다.

### 왜 Ollama를 써야 할까? (토큰 거지 탈출기)

| 장점 | 설명 |
|------|------|
| **비용 제로** | API 호출당 요금이 전혀 없습니다. 무제한으로 질문해도 과금 걱정 ❌ |
| **완벽한 프라이버시** | 모든 데이터가 내 컴퓨터에 머무릅니다. 민감한 문서도 안심하고 분석할 수 있습니다. |
| **오프라인 작동** | 모델만 다운로드받았다면 인터넷 없이도 어디서든 사용 가능합니다. |
| **빠른 응답** | 네트워크 지연이 없어 즉각적인 응답을 받을 수 있습니다. |
| **자유로운 실험** | 다양한 모델을 마음껏 바꿔가며 테스트할 수 있습니다. |
| **뛰어난 확장성** | REST API, Python 연동, IDE 확장 등 다양한 도구와 통합됩니다. |


## 2. Ollama 설치하기

### 사전 요구사항 (하드웨어 체크)

Ollama는 모든 최신 OS에서 작동하지만, 모델을 원활하게 실행하려면 **최소 8GB RAM** (권장 16GB) 이상을 준비하는 것이 좋습니다. 참고로, **Q4_K_M 양자화된 70억(7B) 파라미터 모델**은 약 **4~6GB** 메모리를 필요로 합니다.

| 모델 크기 | Q4 양자화 기준 필요 메모리 (추정) |
|-----------|--------------------------------|
| 3B ~ 8B (소형) | 4GB ~ 6GB |
| 13B ~ 20B (중형) | 8GB ~ 16GB |
| 32B ~ 40B (대형) | 20GB ~ 32GB |
| 70B 이상 (초대형) | 40GB 이상 |

GPU가 있다면 더 빠른 추론 속도를 경험할 수 있지만, 필수는 아닙니다. 일반 CPU만으로도 70억(7B) 파라미터 모델 기준 초당 약 5~15개의 토큰을 생성할 수 있습니다.

---

### Windows

1. [Ollama 공식 다운로드 페이지](https://ollama.com/download)에서 Windows용 설치 파일(`OllamaSetup.exe`)을 다운로드합니다.
2. 다운로드받은 파일을 실행하여 설치를 완료합니다.
3. 설치가 완료되면 **PowerShell 또는 명령 프롬프트(CMD)** 를 열어 아래 명령어로 정상 설치를 확인합니다.

   ```bash
   ollama --version
   ```

---

### MacOS

- **공식 설치 파일 이용**
  [ollama.com](https://ollama.com)에서 macOS용 파일을 다운로드하여 설치합니다.
- **Homebrew 이용 (권장)**
  ```bash
  brew install ollama
  ```

---

### Linux

터미널에서 아래 명령어를 실행합니다. Ubuntu, Debian, Fedora, CentOS 등 대부분의 배포판을 지원합니다.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

### Docker (선택 사항)

컨테이너 기반 배포를 원한다면 Docker 이미지를 사용할 수 있습니다.

```bash
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

> `11434`는 Ollama API의 기본 포트 번호입니다.

### 설치 확인하기

아래 명령어로 Ollama 서비스가 정상적으로 실행 중인지 확인합니다.

```bash
ollama serve   # 서버가 실행 중인지 확인
```

`http://localhost:11434`에서 Ollama 서버가 실행 중임을 나타내는 출력을 볼 수 있습니다.


## 3. Ollama 기본 사용법

### 첫 모델 실행하기 — 가장 간단한 방법

```bash
ollama run llama3.2
```

이 명령어 한 줄이면 끝입니다! 만약 해당 모델이 로컬에 없으면 자동으로 다운로드한 후 대화형 프롬프트가 실행됩니다.

```
>>> 안녕? 너는 누구니?
저는 Meta의 Llama 3.2 모델입니다. 무엇을 도와드릴까요?
```

### 모델 관리 명령어

| 명령어 | 설명 |
|--------|------|
| `ollama list` | 다운로드된 모델 목록 확인 |
| `ollama pull <모델명>` | 모델만 다운로드 (실행하지 않음) |
| `ollama run <모델명>` | 모델 다운로드 + 대화 실행 |
| `ollama rm <모델명>` | 모델 삭제 |
| `ollama cp <모델명> <새이름>` | 모델 복사 |
| `ollama show <모델명>` | 모델 상세 정보 확인 |

### 한 가지 팁 — 모델 태그 활용하기

모델명 뒤에 `:latest` 또는 특정 태그를 붙이면 원하는 버전을 지정할 수 있습니다. 단, `:latest`가 항상 가장 좋은 성능의 모델을 가리키지는 않으므로 가능하면 구체적인 태그를 사용하는 것이 좋습니다.

```bash
# 예시: 특정 크기와 양자화 버전 지정
ollama run llama3.1:8b-q4_K_M
```

### Python에서 Ollama 사용하기

Ollama는 REST API를 제공하므로, Python 등 다양한 언어에서 쉽게 연동할 수 있습니다.

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.2", "prompt": "안녕, 반가워!", "stream": False}
)

print(response.json()["response"])
```


## 4. 주요 LLM 모델 비교 (장단점 & 특징)

Ollama는 500개 이상의 모델을 지원합니다. 여기서는 2025~2026년 기준 가장 주목받는 주요 모델들의 장단점과 특징을 정리했습니다.

### Llama 4 시리즈 (Meta)

| 구분 | Llama 4 Scout | Llama 4 Maverick |
|------|---------------|------------------|
| **구조** | 170억 활성 파라미터, 16개 MoE 전문가 | 170억 활성 파라미터, 128개 MoE 전문가 |
| **특징** | **업계 최고 수준의 1,000만(10M) 토큰** 컨텍스트 창 | 1,000만(10M) 토큰 컨텍스트, 이미지+텍스트 완전 기본 지원 |
| **주요 벤치마크** | MMLU Pro 74.3 / GPQA Diamond 57.2 | MMLU Pro 80.5 / GPQA Diamond 69.8 |
| **추정 하드웨어** | 단일 H100 GPU (Int4 양자화 기준) | 단일 H100 호스트 |
| **효율성(추정)** | ~$0.19–$0.49 / 백만(1M) 토큰 | ~$0.19–$0.49 / 백만(1M) 토큰 |

> **Llama 4는 최초로 공개된 완전 기본(natively) 멀티모달 오픈웨이트 모델**로, 이미지와 텍스트를 동시에 이해할 수 있습니다.

**장점**
- **압도적인 1,000만(10M) 컨텍스트**: 소설 한 권 전체를 한 번에 넣고 분석 가능.
- **뛰어난 멀티모달 성능**: 이미지 인식 및 분석에 강함.
- **Mixture-of-Experts(MoE) 구조**: 활성화 파라미터를 최적화해 효율적.

**단점**
- 고사양 하드웨어 필요 (특히 비디오 메모리(VRAM)).
- 초기 다운로드 용량이 큼.
- 완전 오프라인 활용을 위해서는 최적화된 양자화 버전 필요.

---

### Mistral Small 3.1 (Mistral AI)

| 구분 | 상세 |
|------|------|
| **파라미터** | 240억(24B) |
| **컨텍스트** | 12.8만(128k) 토큰 |
| **추론 속도(추정)** | 150 토큰/초 |
| **멀티모달** | 텍스트 + 이미지 입력 지원 |
| **라이선스** | Apache 2.0 (완전 개방) |

> Apache 2.0 라이선스는 상업적 사용, 수정, 재배포가 모두 자유로운 매우 개방적인 라이선스입니다.

**장점**
- **Apache 2.0 완전 개방 라이선스**: 상업적 활용도 자유로움.
- **뛰어난 속도와 성능 균형**: 240억(24B) 파라미터임에도 빠른 추론 속도.
- **다국어 지원 강점**: 한국어를 포함한 다양한 언어 지원.

**단점**
- 240억(24B) 파라미터 모델을 원활히 실행하려면 고사양 하드웨어 필요. 일부 테스트에서는 256GB 램(RAM)과 듀얼 A100 환경에서도 긴 컨텍스트 처리 시 병목 현상이 보고됨.
- 이론적 최대 속도(150토큰/초)는 실제 로컬 환경에서 달성하기 어려울 수 있음.

---

### Gemma 4 / Gemma 3 시리즈 (Google)

| 모델 | 파라미터 | 필요 비디오 메모리(VRAM) (추정) | 특징 |
|------|----------|-------------------|------|
| Gemma 4 E2B / E4B | 20억~40억(B) ~ 40억(B) (추정) | 15GB 내외 | 작고 효율적인 모델, **수학(Math) 및 과학(ARC) 벤치마크 강세** |
| Gemma 4 26B-A4B | 260억(26B) | 48GB 내외 | MoE 구조로 추론 및 코딩 능력 우수 |
| Gemma 3 4B | 40억(4B) | ~3-5GB | **초경량**, 비용 효율성 극대화 |

> 2026년 연구에 따르면 Gemma 모델은 ARC(과학적 추론)와 Math(수학) 영역에서 특히 두각을 나타냈습니다.

**장점**
- **경량화에 최적화**: 적은 컴퓨팅 자원으로 뛰어난 성능.
- **과학적 추론 능력**: 수학·논리 문제에 강함.
- **Gemma 3 4B는 가성비 최강**: 초당 비용이 경쟁 모델 대비 약 12배 저렴한 수준.

**단점**
- 코딩 분야에서는 같은 크기 대비 Qwen 대비 다소 약할 수 있음.
- 최대 성능을 위해선 적절한 프롬프트 전략 필요 (Few-shot CoT 등).

---

### Phi-4 (Microsoft)

**장점**
- **TruthfulQA(사실성) 벤치마크 최강**: 사실에 기반한 정확한 답변 생성에 탁월.
- **추론 전용 모델 강세**: Phi-4-mini-reasoning 등 추론에 특화된 변형 존재.
- 합리적인 자원 요구량.

**단점**
- 프롬프트 방식에 따른 성능 편차가 큼. 특히 Few-shot CoT(소수샷 사고사슬) 방식에서 급격한 성능 저하 사례 보고됨.
- 일반 대화보다는 특수 목적(추론, 사실 확인)에 특화.

---

### Qwen 2.5 / Qwen 3 시리즈 (Alibaba)

| 모델 | 파라미터 | 필요 비디오 메모리(VRAM) (추정) | 주요 벤치마크 |
|------|----------|-------------------|----------|
| Qwen2.5 7B | 70억(7B) | ~6GB | 6개 과제에서 Gemma 3 4B에 우세 |
| Qwen2.5-Coder 32B | 320억(32B) | ~20GB | **HumanEval 92.7% (GPT-4o 수준)** |
| Qwen2.5 32B | 320억(32B) | ~20GB | MMLU 83.2 |
| Qwen3 30B-A3B | 300억(30B) | 30-40GB | MoE 구조로 최신 추론 능력 |

> Qwen2.5 7B Instruct는 8개 공유 벤치마크 중 **6개 분야에서 Gemma 3 4B를 능가**하는 성능을 보여줍니다.

**장점**
- **코딩 분야 최강자**: Qwen2.5-Coder 32B는 HumanEval 92.7%로 GPT-4o에 필적.
- **뛰어난 다국어 성능**: 중국어는 물론, 영어와 다양한 언어 지원.
- **광범위한 크기 라인업**: 7B에서 320억(32B), 700억(70B) 이상까지 선택지 다양.

**단점**
- 일부 작은 모델(예: 7B)은 출력 길이 제한이 있을 수 있음 (Gemma 3 4B는 출력도 128k 지원 반면, Qwen2.5 7B Instruct는 8192토큰으로 제한).
- 최상위 성능을 위해선 상대적으로 고사양 하드웨어 필요.

---

### Llama 3.3 70B (Meta)

**장점**
- **2026년 기준 전반적 품질 1위 (MMLU 86.0)** 
- 4,050억(405B) 모델 대비 효율적이면서도 유사한 성능 제공.
- 대규모 워크로드(합성 데이터 생성 등)에 적합.

**단점**
- **필요 비디오 메모리(VRAM) 약 40GB** 이상 필요로 매우 높은 사양 요구.
- 일반 사용자보다는 기업/전문가용.
- 다운로드 용량이 큼 (수십 GB).

---

### 모델 비교 요약표

| 모델 | 적정 비디오 메모리(VRAM) (추정) | 최고 분야 | 장점 | 단점 |
|------|--------------------------|----------|------|------|
| **Llama 4 Scout** | ~H100 GPU | 장문 분석 | 1,000만(10M) 컨텍스트, 멀티모달 | 고사양 필요 |
| **Llama 4 Maverick** | ~H100 호스트 | 종합 멀티모달 | 높은 성능, 이미지 이해 | 고사양 필요 |
| **Mistral Small 3.1** | 24GB+ | 다국어 대화 | 속도/품질 균형, 완전 개방 | 긴 컨텍스트 처리 시 과부하 |
| **Gemma 4 / 3** | 4GB~48GB | 수리·과학 추론 | 경량화/효율성, 저비용 | 코딩 성능 상대적 약세 |
| **Phi-4** | ~16GB+ | 사실 기반 QA | TruthfulQA 강세 | 프롬프트 편차 있음 |
| **Qwen 2.5/3** | 6GB~40GB | **코딩** (최강) | 코딩 능력 GPT-4o급, 크기 다양 | 일부 모델 출력 제한 |
| **Llama 3.3 70B** | ~40GB+ | 종합 품질 (MMLU 최고) | 압도적 성능 | 매우 높은 사양 요구 |


## 5. 내 PC에 맞는 모델 선택 가이드

자신의 하드웨어 사양에 따라 다음 모델들을 추천합니다.

### 💻 저사양 (8GB 램(RAM) / 4GB 비디오 메모리(VRAM) 이하)

| 추천 모델 | 설치 명령어 | 특징 |
|-----------|-------------|------|
| **Llama 3.2 3B** | `ollama pull llama3.2` | Meta 최신 소형 모델, 범용 대화에 적합 |
| **Gemma 3 4B** | `ollama pull gemma3:4b` | 가성비 최강, 과학적 추론에 강함 |
| **Phi-4-mini** | `ollama pull phi4-mini` | 사실성 높은 응답 |

### 중간 사양 (16GB 램(RAM) / 8GB 비디오 메모리(VRAM))

| 추천 모델 | 설치 명령어 | 특징 |
|-----------|-------------|------|
| **Llama 3.1 8B** | `ollama pull llama3.1:8b` | 가장 대중적인 모델, 범용성 최고 |
| **Qwen2.5 7B** | `ollama pull qwen2.5:7b` | 코딩/다국어 강세 |
| **Mistral 7B** | `ollama pull mistral` | 검증된 7B 모델 |

### 고사양 (24GB 비디오 메모리(VRAM) 이상)

| 추천 모델 | 설치 명령어 | 특징 |
|-----------|-------------|------|
| **Qwen2.5-Coder 32B** | `ollama pull qwen2.5-coder:32b` | **코딩 최강자** (HumanEval 92.7%) |
| **Qwen2.5 32B** | `ollama pull qwen2.5:32b` | 최고의 중형 올라운더 (MMLU 83.2) |
| **Mistral Small 22B** | `ollama pull mistral-small:22b` | 다국어 특화 |

### 초고사양 (48GB 비디오 메모리(VRAM) 이상)

| 추천 모델 | 설치 명령어 | 특징 |
|-----------|-------------|------|
| **Llama 3.3 70B** | `ollama pull llama3.3:70b` | **종합 품질 1위** (MMLU 86.0) |
| **DeepSeek R1 Distill 70B** | `ollama pull deepseek-r1:70b` | 추론 특화 모델 |

### 모델 선택 팁
- **"항상 가장 큰 모델이 정답은 아닙니다"** : 내 PC에 맞는 적절한 크기의 모델이 오히려 더 쾌적한 경험을 제공합니다.
- **양자화 버전(Q4_K_M 등)을 적극 활용하세요** : 약간의 정확도 희생으로 메모리 사용량을 대폭 줄일 수 있습니다.
- `:latest` 태그보다는 구체적인 태그를 사용하세요 (예: `qwen2.5-coder:32b`).


## 6. 함께 보면 좋은 팁과 도구

### Open WebUI — Ollama용 웹 인터페이스

터미널이 불편하다면, 아래 명령어로 ChatGPT 스타일의 웹 인터페이스를 구축할 수 있습니다.

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### VS Code 확장 프로그램 — Continue

Continue 확장 프로그램을 설치하면 VS Code 내에서 Ollama 모델을 코딩 어시스턴트로 활용할 수 있습니다.

### LangChain + Ollama 통합

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2")
response = llm.invoke("안녕, LLM의 세계에 오신 것을 환영합니다!")
print(response.content)
```

### 환경 변수로 성능 최적화

추론 속도와 메모리 관리를 위해 다음 환경 변수를 설정해보세요.

```bash
export OLLAMA_NUM_PARALLEL=4      # 병렬 요청 수 (기본값: 1)
export OLLAMA_MAX_LOADED_MODELS=2 # 최대 동시 로드 모델 수
export OLLAMA_HOST=0.0.0.0        # 모든 인터페이스에서 API 접근 허용
```

### 모델 저장 위치 변경

기본적으로 `~/.ollama/models`에 저장됩니다. 변경하려면 환경 변수를 설정하세요.

```bash
export OLLAMA_MODELS=/path/to/your/models
```


## 7. 참고 자료

- **Ollama 공식 홈페이지** — [https://ollama.com](https://ollama.com)
- **Ollama GitHub 저장소** — [https://github.com/ollama/ollama](https://github.com/ollama/ollama)
- **Ollama 공식 문서** — [https://docs.ollama.com](https://docs.ollama.com)
- **Ollama 모델 라이브러리** — [https://ollama.com/library](https://ollama.com/library)
- **Meta Llama 4 공식 블로그** — [https://ai.meta.com/blog/llama-4-multimodal-intelligence/](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
- **Mistral Small 3.1 발표** — [https://mistral.ai/news/mistral-small-3-1](https://mistral.ai/news/mistral-small-3-1)
- **Gemma 4 / Phi-4 / Qwen3 성능 비교 논문 (arXiv:2604.07035)** — [https://arxiv.org/abs/2604.07035](https://arxiv.org/abs/2604.07035)
- **Gemma 3 vs Qwen2.5 벤치마크 비교** — [https://llm-stats.com](https://llm-stats.com)
- **Ollama 설치 가이드 (SitePoint, 2026)** — [https://www.sitepoint.com/ollama-setup-guide-2026/](https://www.sitepoint.com/ollama-setup-guide-2026/)
- **Ollama 완벽 가이드 (DEV Community)** — [https://dev.to/ajitkumar/the-complete-guide-to-ollama-run-large-language-models-locally-2mge](https://dev.to/ajitkumar/the-complete-guide-to-ollama-run-large-language-models-locally-2mge)


지금까지 **Ollama 설치 및 주요 LLM 모델 비교** 문서를 살펴보았습니다. 이제 토큰 비용 걱정 없이 내 컴퓨터에서 마음껏 LLM을 실행해보세요. API 비용은 0원, 프라이버시는 완벽하게 보호됩니다. 행복한 로컬 AI 구축 되시길 바랍니다! 🚀
