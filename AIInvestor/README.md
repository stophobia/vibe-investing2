# AI Investor

LLM 기반 텔레그램 챗봇 — 유명 투자자 페르소나로 미국 시황(NASDAQ / S&P 500)을 해설합니다.

- **상태**: MVP 가동 중 ([@AI_vibe_investor_bot](https://t.me/AI_vibe_investor_bot)), Azure 서버리스 이전 준비
- **백엔드 LLM**: DeepSeek (`deepseek-chat` / `deepseek-reasoner`) — OpenAI 호환 엔드포인트
- **데이터**: Yahoo Finance (yfinance)
- **저장소**: 1차는 로컬 SQLite, 2차에서 Azure Cosmos DB (Serverless) + 일일 리포트 Azure CDN 사전 캐싱

OpenAI에서 DeepSeek로 전환한 이유: ChatGPT는 실시간 데이터성 미반영 + 가격. DeepSeek는 API 호환성 + 금융 도메인 강점 + 1/35 비용.

> **Disclaimer**: 본 봇은 투자 자문 서비스가 아닙니다. AI가 생성한 응답은 부정확하거나 환각이 있을 수 있으며, 모든 응답 끝에 면책 한 줄이 강제됩니다. 투자 판단의 책임은 사용자에게 있습니다.

---

## 📑 단일 진실원본

본 프로젝트의 **아키텍처 / 사용자 플로우 / 코드 리뷰 / 개발 로드맵 / 학술 데이터 수집 계획** 은 모두 한 문서에 통합되어 있습니다:

→ **[paper_plan.md — 아키텍처 및 개발 계획 (v2.0)](paper_plan.md)**

함께 보는 자료:
- [LLM cost analysis.md](LLM%20cost%20analysis.md) — DeepSeek vs OpenAI/Anthropic/Qwen 비용 비교
- [.env.example](.env.example) — 환경 변수 템플릿

---

## 빠른 시작 (로컬 개발)

1. Telegram 봇 토큰 발급 ([@BotFather](https://t.me/BotFather)).
2. DeepSeek API 키 발급 ([platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)).
3. 환경 설정:

   ```bash
   cd AIInvestor
   cp .env.example .env
   # .env 열어서 TELEGRAM_BOT_TOKEN, DEEPSEEK_API_KEY 채우기
   chmod 600 .env
   ```

4. 가상환경 + 의존성:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate         # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. 실행:

   ```bash
   python main.py
   ```

추론 모델로 바꾸려면 `.env` 의 `DEEPSEEK_MODEL=deepseek-reasoner`.

---

## 텔레그램 명령

| 명령 | 동작 |
|---|---|
| `/start` | 환영 + 현재 페르소나 |
| `/help` | 명령 목록 |
| `/personas` | 사용 가능한 페르소나 |
| `/persona <key>` | 페르소나 전환 (`buffett` / `dalio` / `wood`) |
| 일반 텍스트 | 티커로 간주 → yfinance 조회 → 페르소나 해설 |

이상의 명령은 MVP 현재 동작 기준이며, [paper_plan.md §6](paper_plan.md#6-사용자-플로우) 에 정의된 5단계 골든 패스(입장 → 설명 → 페르소나 → 오늘의 리포트 → 자유 질의)는 Phase 1에서 구현 예정입니다.

---

## 프로젝트 구조

```
AIInvestor/
├── main.py                       엔트리 포인트
├── config.py                     env 로딩 + 로깅
├── bot/
│   └── telegram_handler.py       명령/메시지 라우팅, 페르소나 상태
├── services/
│   ├── persona_engine.py         페르소나 + DeepSeek 호출
│   └── stock_service.py          yfinance 스냅샷 + 1년치 변동률
├── requirements.txt
├── .env.example
├── README.md                     (이 파일)
├── paper_plan.md                 ★ 아키텍처 / 로드맵 / 코드 리뷰 / 학술 계획
└── LLM cost analysis.md          비용 비교
```

---

## 페르소나 추가 방법

[services/persona_engine.py:22](services/persona_engine.py#L22) 의 `PERSONAS` dict에 한 줄 추가하면 자동으로 `/personas`/`/persona` 에 노출됩니다.

```python
"munger": Persona(
    key="munger",
    display_name="Charlie Munger",
    system_prompt="You are Charlie Munger. Brief, blunt, mental-models...",
),
```

---

## 안전 장치 (현행)

- 시스템 프롬프트가 **데이터 블록 외 수치 환각을 금지** (현행 Buffett/Dalio/Wood 모두)
- **명시적 매수/매도 권고 금지** — 'I'd be inclined to wait' 같은 stance 표현으로 우회
- 모든 응답 끝에 `This is not financial advice.` 한 줄 강제
- 잘못된 티커 입력 시 친화적 에러 메시지

상세 위협 모델·점검 결과는 [paper_plan.md §5.4](paper_plan.md#54-보안--컴플라이언스-점검) 참조.

---

## 개발 로드맵 요약

| 우선순위 | 목표 | 환경 |
|---|---|---|
| **🥇 1차** | 6단계 사용자 플로우 + 영속 메모리 — 인사 → 소개 → 페르소나 → 오늘의 리포트 → 관심사 획득 → 기억 기반 소통 + 페르소나 교체. 봇 재시작 후에도 페르소나·관심사 유지 (`UserProfileRepo` SQLite) | 로컬 / 단일 호스트 |
| **🥈 2차** | Azure Functions Flex Consumption + Webhook + Timer 일일 리포트 사전 생성 + Blob → CDN 캐싱. 사용자 프로필 SQLite → Cosmos DB 이전. GitHub Actions 자동 배포 | Azure |
| 🥉 후속 (3·4차) | 의미적 캐싱 + 텔레메트리(학술 데이터 수집), 모바일(iOS/Android) + 멀티턴 | Azure 확장 |

상세 작업 체크리스트는 [paper_plan.md §11](paper_plan.md#11-개발-로드맵) 에 1차/2차로 분리되어 정리되어 있습니다.

---

## 알려진 한계

- yfinance는 비공식 API — 일부 필드 누락 / 일시적 차단 가능 (백업 supplier 준비 중)
- 페르소나 상태가 인메모리 — 봇 재시작 시 소실 (Phase 2에서 Cosmos DB로 영속화)
- 동기 LLM 호출이 asyncio 이벤트 루프를 블록 — 동시 사용자 ≥ 2 시 지연 누적 (Phase 0에서 `AsyncOpenAI` 전환)
- 응답 스트리밍 미지원

---

## 주의

본 서비스는 Vibe Investing 프로젝트의 실증 테스트용이며, AI Quant 페르소나 연구의 개발 진행 결과물입니다. 따라서 AI의 환각 및 오류가 발생할 수 있습니다.
