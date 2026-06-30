# Qwen 로컬 LLM 설치 가이드 & 주의사항 (개정본)

> 검증 기준일: 2026-06-30 / 원문(Qwen2.5·초기 Qwen3 시점)을 현재 라인업·하드웨어 기준으로 갱신하고 레퍼런스를 부기함.
> 핵심 원칙: VRAM(또는 통합 메모리)은 하드 제약이다 — 웨이트가 안 들어가면 실행 자체가 안 된다. 양자화·context·KV cache를 함께 계산할 것. [R7][R10]

## Qwen(퀜) 개요
Qwen(중국어: 千问, ‘쿤’으로 발음)은 알리바바 그룹이 개발한 대규모 언어 모델(LLM) 및 대규모 멀티모달 모델 제품군이다. 첫 버전은 2023년 4월 베타 형태로 공개되었으며, 현재 세계 최대 오픈소스 AI 생태계 중 하나로 성장했습니다. 2026년 3월 알리바바는 AI 브랜드를 ‘Qwen(퀜) 대모델’로 통일하여 이전의 혼란을 해소했다.

## 주요 기능
Qwen은 다양한 멀티모달 및 언어 작업을 수행할 수 있다.

자연어 이해 및 텍스트 생성

시각 이해(이미지, 비디오)

오디오 이해 및 처리

도구 호출 및 AI 에이전트(Agent) 기능

역할극 및 다중 대화

모델은 대규모 다국어·멀티모달 데이터로 사전 훈련되었으며, 고품질 데이터로 미세 조정되어 인간의 선호도에 부합하도록 설계함.

## 기술 구조 및 특징
이중 모드 아키텍처(사고 모드 / 비사고 모드)
Qwen3의 핵심 혁신은 하나의 모델에 ‘사고 모드’와 ‘비사고 모드’를 동시에 탑재하여 효율을 높임

모드	적용 상황
사고 모드	복잡한 논리 추론, 수학, 프로그래밍 등 심층 사고가 필요한 작업
비사고 모드	빠른 응답이 필요한 일반 대화
모델은 ‘사고 예산(thinking budget)’ 메커니즘을 통해 문제 복잡도를 동적으로 평가하고 계산 자원을 자동 배분

모델 구조
Dense 모델과 MoE(Mixture of Experts) 모델 병존: 0.6B부터 235B까지 다양한 규모 제공

Qwen3-Next는 고희소도 MoE 아키텍처 적용: 총 파라미터 800억, 추론 시 약 30억 파라미터(약 3.75%)만 활성화하여 효율성 대폭 향상

Qwen3-Max는 총 파라미터 1조(1T) 이상, 사전 훈련에 36T tokens 사용

훈련 전략
3단계 사전 훈련: 언어 기반 구축 → 추론 능력 강화 → 장문 텍스트 능력 확장

4단계 사후 훈련: 장사고 사슬 콜드 스타트, 추론 강화 학습, 모드 융합 등 포함

‘대모델이 소모델을 육성’하는 증류 방식: 대모델 데이터로 소모델 훈련

## 주요 버전 및 모델

Qwen 3.5
2026년 2월	플래그십 모델
총 397B(활성 17B)
262K 네이티브 컨텍스트(1M 확장 가능)
201개 언어 지원, Apache 2.0 오픈소스

Qwen3.7-Max	
2026년 5월	에이전트 특화
35시간 이상의 초장기 복잡 작업을 완전 자율 수행 가능

Qwen3-Max	
2025년 9월	총 파라미터 1T 이상, LMArena 랭킹 세계 3위

오픈소스 모델은 Qwen, Qwen1.5, Qwen2, Qwen2.5 시리즈 등이 있으며, 0.5B~110B까지 다양
또한 전용 비전 언어 모델(Qwen-VL), 오디오 모델(Qwen-Audio), 코드 모델(Qwen-Coder), 추론 모델(QwQ) 등이 있음.

# 적용 분야
Qwen은 다양한 분야에서 활용 가능.

소프트웨어 개발: 코드 생성, 디버깅, 리뷰, 50개 이상의 프로그래밍 언어 지원

콘텐츠 제작: 장문 작성, SEO, 소셜 미디어, 번역(201개 언어)

연구 및 데이터 분석: 문헌 검토, 차트 해석, 과학 추론, 의료 분석

기업 업무: 고객 서비스 챗봇, 문서 처리, 지식 베이스 질의응답

벤치마크 테스트에서 Qwen 3.5는 SWE-Bench Verified에서 76.4점을 기록, GPT-5.2 및 Claude Opus 4.5와 동등한 수준입니다.

## 사용 방법
오픈소스 모델: Apache 2.0 라이선스로 무료 사용 가능, Ollama, llama.cpp, LM Studio 등으로 로컬 실행 지원

API 서비스: 알리바바 클라우드 DashScope API를 통해 호출

무료 체험: Qwen Chat 공식 웹사이트(chat.qwen.ai)에서 대화 가능

기업 서비스: 전 세계 29만 개 이상의 기업 고객에게 제공

---

## 0. 먼저 알아야 할 버전 정리 (문서 업데이트)

원문은 `qwen2.5` / `qwen3` / 산발적 `qwen3.5:4b`만 다루지만, 2026-06 기준 라인업은 아래와 같이 확장되어 있다.

| 세대 | 출시 | 구성 | 멀티모달 | 지원 언어 | 라이선스 | 로컬 가능 |
|---|---|---|---|---|---|---|
| Qwen3 | 2025-04 | dense 0.6B~32B + MoE 30B-A3B, 235B-A22B | 텍스트 | 119개 | Apache-2.0 | O [R2][R7] |
| Qwen3.5 | 2026-02 | Small 0.8B/2B/4B/9B + 27B / 35B-A3B / 122B-A10B / 397B-A17B | vision(네이티브) | 201개 | Apache-2.0 | O [R1][R9] |
| Qwen3.6 | 2026-04~05 | 27B(dense) / 35B-A3B(MoE), 코딩·에이전트 강화 | vision | — | Apache-2.0 | O [R11][R12] |
| Qwen3.7-Max | 2026-05-20 | 독점 API 전용, 오픈웨이트 미공개 | — | — | 비공개 | **X (로컬 불가)** [R7] |

주의:
- 본 가이드는 **오픈웨이트 모델만** 대상으로 한다. `*-Max`, `*-Plus` 등 API 전용 모델은 로컬 설치 대상이 아니다. [R7][R12]
- 2025-07~08 "2507" 리프레시에서 Qwen3는 하이브리드(토글) 방식에서 **thinking / instruct 분리 체크포인트**로 갈라졌다. 다운로드 시 어떤 변형인지 확인할 것. [R7]

---

## 1. 설치 방법 선택

| 방법 | 특징 | 추천 대상 |
|---|---|---|
| Ollama | 명령어 한 줄 설치/실행, 가장 간편 | LLM 초보자, 빠른 테스트 |
| LM Studio | GUI 기반, 클릭 몇 번. MLX·GGUF 지원 | 코딩 없이 쓰고 싶은 분 |
| Hugging Face Transformers | Python 코드로 세부 제어 | 개발자, 커스터마이징 |

---

## 2. Ollama 설치 (가장 간편)

### 2.1 Ollama 설치 [R8]

Windows
```powershell
irm https://ollama.com/install.ps1 | iex
```
또는 공식 사이트(ollama.com)에서 설치파일 다운로드.

macOS
```bash
brew install ollama
```

Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2.2 실행
```bash
ollama serve   # 수동 시작 (보통 설치 후 자동 실행)
```

### 2.3 모델 다운로드 및 실행 [R8][R16]
```bash
# 현행 권장 — Qwen3 계열
ollama run qwen3:8b            # 기본/입문, 약 5GB
ollama run qwen3:4b            # 경량
ollama run qwen3:14b           # 약 9GB
ollama run qwen3:32b           # dense 상위
ollama run qwen3:30b-a3b       # MoE: 30B 품질·8B급 속도(VRAM은 전체분 필요)

# Qwen3.5 계열 (멀티모달)
ollama run qwen3.5:9b          # 8GB 카드 권장 기본값, 약 6.6GB
ollama run qwen3.5:4b          # 경량, 약 3.4GB(파일)

# 구버전
ollama run qwen2.5:7b
```

사용 가능 크기(예): qwen2.5 0.5/1.5/3/7/14/32/72B, qwen3 0.6~32B + 30B-A3B/235B-A22B, qwen3.5 0.8/2/4/9/27/35/122/397B 계열. [R1][R2][R10]

주의:
- Ollama 태그에 `instruct`가 없어도 chat용 모델인 경우가 많으나, Qwen3 2507 이후로는 thinking/instruct 변형이 별도 배포되므로 **태그를 직접 확인**할 것. (원문의 "모두 Instruct" 단정은 현행 기준 부정확) [R7]
- `qwen3.5:4b`의 "3.4GB"는 **GGUF 파일 크기**이지 런타임 RAM이 아니다. 실제로는 + KV cache + context 오버헤드를 더해야 한다. [R7][R14]

### 2.4 자체 GGUF 파일 사용 (Modelfile) [R8]
```text
FROM qwen2.5-7b-instruct-q5_0.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER repeat_penalty 1.05
PARAMETER top_k 20
```
```bash
ollama create my-qwen -f Modelfile
ollama run my-qwen
```

주의: Qwen3.5 같은 **멀티모달 GGUF는 vision(mmproj) 파일 분리** 이슈로 Ollama 직접 임포트가 제한될 수 있다. 이 경우 llama.cpp 계열 백엔드나 LM Studio를 권장한다. (Ollama 라이브러리 태그로 받는 경우는 정상 동작) [R9]

---

## 3. LM Studio 설치 (GUI)

1. 공식 사이트에서 macOS/Windows/Linux 설치파일 다운로드 후 설치.
2. 앱 실행 → `Cmd+Shift+M`(Mac) / `Ctrl+Shift+M`(PC)로 모델 검색.
3. "Qwen" 검색 → 하드웨어에 맞는 모델 Download.
4. Hugging Face 모델 카드의 "Use this model → LM Studio"로 직접 연결 가능.
5. 멀티모달/Thinking 토글은 모델별 yaml 설정이 필요할 수 있으며, CLI로 `lms import <경로>` 수동 임포트 지원. [R9]

Apple Silicon은 **MLX 포맷**을 지원하는 LM Studio 사용 시 성능 이점이 크다. [R9][R11]

---

## 4. Hugging Face Transformers (개발자용)

### 4.1 사전 준비
```bash
pip install transformers torch accelerate
pip install modelscope   # 중국 지역에서 다운로드 빠름
```

### 4.2 로드 및 실행
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen3-30B-A3B"   # 또는 Qwen/Qwen3-8B 등

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",   # GPU/CPU 자동 할당, 부족 시 CPU 오프로드
)

messages = [{"role": "user", "content": "Qwen, 한국어로 자기소개 해줘."}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True,   # 사고 모드(Qwen3 이상)
)

outputs = model.generate(
    **tokenizer([text], return_tensors="pt").to(model.device),
    max_new_tokens=200,
)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

`enable_thinking=True`는 복잡한 추론에 유리하나 응답이 느려진다. 일상 대화는 `False` 권장. [R2][R8]

설치 전 VRAM 적합성 점검 팁 — 다운로드 없이 헤더만 읽어 메모리 추정: [R18]
```bash
uvx hf-mem --model-id Qwen/Qwen3-8B --experimental --max-model-len 8192
```

---

## 5. 모델 선택 가이드 (하드웨어별 · Q4_K_M 기준)

VRAM 수치는 Q4_K_M GGUF 기준이며, 4K context KV cache로 **+1~2GB**를 더해 잡을 것. VRAM 부족 시 Ollama/llama.cpp가 system RAM으로 자동 오프로드하나 속도가 크게 떨어진다(10~20배 느린 메모리 대역폭). [R13][R18]

| 하드웨어 | 추천 모델 | 대략 VRAM/RAM | 비고 |
|---|---|---|---|
| 구형 노트북 (RAM 4~8GB) | qwen3.5:4b / qwen2.5:3b | 3~4GB(파일) | CPU-only 가능, 저속 |
| 일반 데스크톱 (RAM 16GB) | qwen3:8b / qwen3.5:9b | 약 5~6.6GB | CPU-only 가능 [R13][R14] |
| GPU VRAM 8GB | qwen3.5:9b(Q4) / qwen3:7~8b | 약 5.5~6.6GB | RTX 3060/4060급 [R13][R14] |
| GPU VRAM 12GB | qwen3:14b(Q4) | 약 9~9.5GB | Q6_K 여유 [R13][R14] |
| GPU VRAM 16~24GB | qwen3:32b / qwen3.6:27b(약 17GB) | 17~20GB | 24GB서 Q4_K_M 쾌적 [R12][R14] |
| GPU VRAM 24GB | qwen3.6:35b-a3b(UD-Q4 약 22GB) | 약 22GB | context 과하게 잡지 말 것 [R12][R14] |
| 멀티 GPU / 서버 | qwen2.5:72b / 235B-A22B / 397B-A17B | 수십~수백 GB | tensor-parallel 필요 [R16][R19] |

MoE 함정: `30B-A3B`, `35B-A3B`, `80B-A3B` 등은 **활성 파라미터가 3B여도 전체 웨이트를 VRAM에 적재**해야 한다. "3B 활성 = 3B 메모리"가 아니다. 예: Qwen3-Next-80B-A3B는 비양자화 시 약 160GB VRAM. [R14][R19]

---

## 6. 주의사항 및 팁

### 6.1 저장 공간
- 7B ≈ 5GB, 14B ≈ 9GB, 27B ≈ 17GB, 32B ≈ 20GB, 35B-A3B ≈ 22GB(Q4 기준). [R13][R14]
- Ollama 기본 저장 경로: `~/.ollama/models`. 여유 공간 확보. [R8]

### 6.2 양자화(Quantization) [R13][R16][R18]
- Q4_K_M: 대부분의 기본값. VRAM 약 75% 절감, 품질 손실 최소.
- Q5_K_M: ~60% 절감, Q4보다 약간 고품질.
- Q8_0: 최고 품질 양자화. VRAM 여유 있을 때.
- NVFP4: Blackwell(RTX 5060 Ti/5090) 네이티브, Q4보다 효율적.
- 명시 지정 예: `ollama run qwen3:8b-q4_K_M`
- 경고: **Q2_K는 한국어/중국어 등 CJK 출력 품질이 눈에 띄게 저하**된다. CJK 작업은 Q4_K_M을 최소선으로. [R13]

### 6.3 GPU 사용
- NVIDIA: CUDA 드라이버 필요.
- Apple Silicon(M1~M4): 통합 메모리로 대형 모델에 유리. MLX 포맷 + LM Studio 권장. (예: M3 Max 64GB로 qwen3:32b ~22 tok/s) [R13]
- VRAM 부족 시 `device_map="auto"`로 CPU 오프로드되나, 10~20%를 넘기면 체감 속도 급락 — 더 작은 모델 권장. [R18]

### 6.4 한국어 사용
- Qwen3 계열 119개 언어, Qwen3.5 이후 201개 언어 지원. 한국어 성능 우수, 한국어 프롬프트 그대로 사용 가능. [R2][R9]

### 6.5 Thinking Mode (Qwen3 이상)
- CLI: `ollama run qwen3 --think` / `--no-think` [R8]
- API: `{"model":"qwen3","think":false,...}` 또는 `{"thinking":{"budget_tokens":1024}}`로 추론 예산 상한 설정 [R8]
- 프롬프트 내 `/think`, `/no_think` 토글도 일부 변형에서 지원.
- 권장: 요약·드래프트는 no-think, 코드 디버깅·수학·논리는 think.

### 6.6 Context / KV cache 주의 (원문 누락 보강)
- Qwen3.5/3.6은 네이티브 256K(262,144) context, YaRN으로 ~1M 확장 가능. [R12][R17]
- context를 길게 잡을수록 KV cache가 VRAM을 크게 잠식한다. "최소 VRAM" 표는 단/중 context 기준이며, 128K~256K를 실제로 쓰려면 여유를 크게 확보해야 한다. [R12]

### 6.7 네트워크
- 최초 다운로드 시 인터넷 필요(수 GB~수십 GB). 이후 완전 오프라인 사용 가능. [R8]

### 6.8 라이선스
- Qwen3/3.5/3.6 오픈웨이트는 Apache-2.0 — 상업적 사용 가능. (단 `*-Max` API 모델은 별도 약관) [R7]

---

## 7. 문제 해결 (Troubleshooting)

| 문제 | 해결 방법 |
|---|---|
| "CUDA out of memory" | 더 작은 모델 또는 더 낮은 양자화(Q4→Q3) / context 축소 [R12][R14] |
| Ollama가 모델을 못 찾음 | `ollama pull qwen3:8b`로 명시적 다운로드 [R8] |
| 응답이 너무 느림 | CPU-only면 소형 모델(0.6~4B), 또는 오프로드 비율 점검(>10~20%면 GPU 부족) [R18] |
| LM Studio에서 모델 안 보임 | `lms import <모델경로>` 수동 임포트 [R9] |
| 멀티모달 GGUF가 Ollama서 깨짐 | mmproj 분리 이슈 — llama.cpp/LM Studio 사용 [R9] |
| 다운로드 전 VRAM 적합성 확인 | `uvx hf-mem --model-id <repo> --experimental` [R18] |

---

## 참고문헌 (References)

- [R1] Ollama Library — qwen3.5 (tags, 사이즈/멀티모달/256K context). https://ollama.com/library/qwen3.5
- [R2] Ollama Library — qwen3 (dense+MoE, thinking framework). https://ollama.com/library/qwen3
- [R7] Local AI Master, "How to Run Qwen3 Locally (2026): Setup Guide" — 8모델 구성, 119언어, 2507 분리, Qwen3.7-Max API 전용 명시. https://localaimaster.com/blog/qwen-3-local-setup-guide
- [R8] Serverman, "Run Qwen3 on Ollama: All Sizes and Hardware Guide" — 설치/실행, --think 토글, KV/예산. https://www.serverman.co.uk/ai/ollama/how-to-run-qwen3-on-ollama/
- [R9] Unsloth Docs, "Qwen3.5 - How to Run Locally" — Small/대형 구성, Ollama GGUF mmproj 제한, LM Studio yaml 토글. https://unsloth.ai/docs/models/qwen3.5
- [R10] Ollama Library — qwen3.5 Tags (0.8b~122b 사이즈/용량). https://ollama.com/library/qwen3.5/tags
- [R11] Ollama Library — qwen3.6 (27B/35B, MLX, 코딩 강화). https://ollama.com/library/qwen3.6
- [R12] knightli, "Qwen3.6 VRAM Table" — 27B≈17GB, 35B-A3B≈22GB(UD-Q4), context/KV 주의. https://knightli.com/en/2026/05/01/qwen3-6-local-vram-quantization-table/
- [R13] PromptQuorum, "Qwen Local Deployment Guide 2026" — Q4_K_M VRAM 표, Q2_K CJK 저하 경고, Apple Silicon tok/s. https://www.promptquorum.com/local-llms/qwen-local-deployment-guide-2026
- [R14] InsiderLLM, "VRAM Cheat Sheet for Local LLMs" — qwen3.5 9B 6.6GB, vision 오버헤드, MoE 전체 웨이트 적재. https://insiderllm.com/guides/vram-requirements-local-llms/
- [R16] Compute Market, "Qwen 3 Hardware Guide 0.8B~72B" — 하드웨어 티어/가격, 양자화 포맷. https://www.compute-market.com/blog/qwen-3-local-hardware-guide-2026
- [R17] M. Chen (Medium), "Run Qwen3.6-35B-A3B on 6GB VRAM Using Llama.cpp" — 저사양 오프로드 사례. https://mychen76.medium.com/run-qwen3-6-35b-a3b-on-6gb-vram-using-llama-cpp-30-tps-a89032e5a60c
- [R18] ai.rs, "Will This LLM Fit My GPU?" — hf-mem 사전 점검, 오프로드 성능 손실. https://ai.rs/ai-developer/will-llm-fit-my-gpu-vram-requirements
- [R19] Hugging Face Discussion — Qwen3-Next-80B-A3B 메모리(비양자화 ≈160GB, MoE 전체 적재). https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct/discussions/7

> 면책: 모델 라인업·태그·용량은 업스트림(Ollama/HF/Unsloth)에서 수시로 갱신된다. 실제 설치 전 해당 라이브러리 페이지에서 최신 태그·파일 크기를 재확인할 것.
