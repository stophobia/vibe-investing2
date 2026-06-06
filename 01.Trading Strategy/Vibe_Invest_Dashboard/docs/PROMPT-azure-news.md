# 작업 프롬프트 — AIInvestor에 "뉴스 요약 → CF ingest" Azure Function 추가

> VS Code의 **AIInvestor** 프로젝트(Python 3.11, Azure Functions v2)에서 Claude Code에 그대로 붙여넣어 사용.
> 이 문서의 **§ingest 계약**은 Vibe Investing 대시보드의 CF Worker `POST /api/ingest/news` 와
> 양쪽이 **동일하게** 지켜야 하는 단일 기준이다. (Worker 쪽은 대시보드 repo에서 이 계약대로 구현)

---

## 복사용 프롬프트 (아래 전체를 VS Code Claude Code에 붙여넣기)

```
역할: 이 AIInvestor Azure Functions 앱(Python 3.11, v2 데코레이터 모델)에 "미국 경제 뉴스
수집 → DeepSeek 한국어 요약 → 외부 Cloudflare Worker로 전송"하는 Timer 트리거 함수를 추가한다.
별도 앱을 만들지 말고 **기존 앱·기존 패턴을 재사용**한다. 기존 24개 함수 동작을 깨뜨리지 말 것.

【0단계 — 먼저 읽고 관례를 파악 (필수)】
다음 파일을 읽고 기존 컨벤션을 그대로 따른다. 새로 발명 금지:
  - function_app.py        : @app.timer_trigger 등록 패턴, await _bootstrap() 싱글톤 부트스트랩
  - config.py              : Config 데이터클래스가 env를 로드/검증하는 방식 (deepseek_* 키 포함)
  - services/persona_engine.py : AsyncOpenAI(DeepSeek) 클라이언트 생성·호출 패턴
  - services/usage_logger.py   : BlobServiceClient + DefaultAzureCredential 로 Blob 읽기/쓰기 패턴
  - .env.example, host.json, requirements.txt
정확한 base_url/model/시크릿 키 이름·Blob 접근 방식은 위 파일에서 확인해 동일하게 쓴다.

【목표 산출물】
1) services/news_service.py  (신규)
   - Finnhub 뉴스 수집 + 중복 제거 + DeepSeek 요약 + CF Worker POST 를 담당하는 서비스 클래스.
   - PersonaEngine 과 같은 방식으로 AsyncOpenAI 클라이언트를 주입받는다(또는 _config 로 직접 생성).
2) function_app.py 에 Timer 함수 1개 등록 (아래 스케줄). await _bootstrap() 후 위 서비스 호출.
3) config.py 에 신규 env 추가: FINNHUB_KEY(필수), CF_INGEST_URL(필수), INGEST_SECRET(필수),
   ALPHAVANTAGE_KEY(선택). 기존 deepseek_* 는 재사용.
4) .env.example 에 위 신규 키 템플릿 추가.
5) tests/test_news_service.py (신규): Finnhub·DeepSeek·Blob·CF POST 를 모두 모킹한 단위 테스트.
   - 신규 뉴스 0건이면 DeepSeek 호출/POST 를 스킵하는지
   - HMAC 서명 base string 과 헤더가 계약(아래)과 일치하는지
   - 중복 ID 가 두 번 처리되지 않는지
6) requirements.txt 에 필요한 패키지만 추가(httpx 또는 aiohttp 중 기존에 쓰는 것 재사용. openai·
   azure-storage-blob·azure-identity 는 이미 있음).

【스케줄 — 1일 9회 KST, UTC NCRONTAB(6필드: 초 분 시 일 월 요일)】
  schedule="0 0 1,3,6,9,12,14,18,21,23 * * *"   # UTC 시각 정각. KST=UTC+9.
  run_on_startup=False, use_monitor=True
  (KST 03/06/08/10/12/15/18/21/23시에 해당. Azure 타이머 기본 UTC 가정, WEBSITE_TIME_ZONE 의존 금지.)

【처리 절차】
  a. Finnhub GET https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}
     (선택: Alpha Vantage NEWS_SENTIMENT 도 ALPHAVANTAGE_KEY 있으면 병합)
     - Finnhub item: {id:int, datetime:unix, headline, summary, source, url, category, related}
  b. 중복 제거: 직전 처리한 뉴스 id 집합을 Blob 에 보관하고 신규만 추출.
     - 컨테이너 "news", blob "processed/<YYYY-MM-DD>.json" 에 그날 처리한 id 배열을 누적 저장.
     - 최근 2일치를 읽어 dedup (자정 경계 대비). usage_logger.py 의 Blob 접근 패턴 재사용.
  c. 신규 0건 → 즉시 종료(비용 가드: DeepSeek 호출/POST 안 함). 로그만 남김.
  d. 신규가 있으면 DeepSeek 요약 1회 호출 (아래 프롬프트). max_tokens 상한으로 비용 통제.
  e. 결과를 CF Worker 로 POST (아래 ingest 계약). 2xx 아니면 에러 로깅 + 다음 회차 재시도(이번 회차는
     처리 id 를 저장하지 말 것 → 다음 회차에 재포함되도록). 2xx 면 처리 id 를 Blob 에 저장.

【DeepSeek 호출】 — 기존 deepseek_* 설정(api_key/base_url/model) 재사용
  system: "당신은 금융 뉴스 요약기입니다. 의견·전망·투자조언을 생성하지 마세요. 사실만 요약합니다."
  user:   "다음 뉴스들을 한국어로 요약하세요. 각 항목당 1문장, 전체 시장 요약 2문장.
           JSON만 출력: {\"market_summary\":\"...\",\"items\":[{\"id\",\"title_ko\",\"summary_ko\",
           \"category\",\"tickers\":[]}]}
           카테고리: 거시경제|실적|반도체|AI|금리|지정학|기타
           --- 뉴스 원문 ---\n{news_json}"
  파라미터: temperature 0.3~0.5, max_tokens 800, timeout 30s, response_format JSON 가능하면 사용.
  주의: DeepSeek 가 JSON 외 텍스트를 섞어도 깨지지 않게 파싱(코드펜스 제거 후 json.loads, 실패 시 1회 재시도).
  id 는 반드시 입력 뉴스의 원본 id 를 보존(요약기가 새로 만들지 않게 프롬프트/후처리로 강제).

【ingest 계약 — Cloudflare Pages Function POST /api/ingest/news (양쪽 동일 준수)】
  요청:
    POST {CF_INGEST_URL}        # 예: https://vibe-investing.pages.dev/api/ingest/news  (Cloudflare Pages Function)
    Content-Type: application/json; charset=utf-8
    X-Timestamp: <현재 unix epoch 초, 정수 문자열>
    X-Signature: <hex(HMAC_SHA256(key=INGEST_SECRET, msg=f"{X-Timestamp}.{raw_body}"))>
      - raw_body 는 실제 전송하는 바이트 그대로(서명 후 재직렬화 금지). hmac.new(...).hexdigest().
  body(JSON):
    {
      "ts": "<ISO8601 UTC, 이 배치 생성시각>",
      "market_summary": "<전체 2문장 요약>",
      "items": [
        {
          "id": "<뉴스 원본 id, 문자열>",
          "ts": "<ISO8601 UTC, 뉴스 datetime>",
          "title_ko": "...", "summary_ko": "...",
          "category": "거시경제|실적|반도체|AI|금리|지정학|기타",
          "tickers": ["NVDA", ...],
          "source": "Finnhub", "url": "https://..."
        }
      ]
    }
  응답: 200 {"ok":true,"ingested":<n>} / 검증 실패 401. 401·5xx 면 이번 회차 처리 id 저장 안 함.
  서버(Worker) 검증: |now - X-Timestamp| ≤ 300초, 서명 일치. → 통과 시 D1 news_summary 에 item upsert,
  market_summary(id=1) 갱신. (이 검증은 대시보드 repo 에서 구현됨. 본 함수는 위 형식만 정확히 맞추면 됨.)

【시크릿/배포】
  - 키는 절대 하드코딩·커밋 금지. config.py 를 통해 env 로만 읽는다. .env.example 만 업데이트.
  - 프로덕션은 Key Vault → 앱 설정 동기화 구조(기존 deploy-aiinvestor.yml 참고). FINNHUB_KEY·
    INGEST_SECRET·CF_INGEST_URL 을 Key Vault/GitHub secret 에 추가해야 함은 **주석/README 로 안내만**
    하고, 인프라(Bicep)·CI 변경은 이번 작업 범위에서 제외(별도 단계). INGEST_SECRET 은 CF Worker 와
    공유하는 동일 값이어야 한다고 명시.

【제약/수용 기준】
  - 모든 I/O 는 async. 기존 _bootstrap() 싱글톤·로깅·예외처리 스타일을 따른다.
  - 외부 호출은 타임아웃·예외 가드. 한 소스 실패가 전체를 죽이지 않게(부분 성공 허용).
  - 비용 가드: 신규 0건 스킵, max_tokens 상한, 회차당 DeepSeek 1회.
  - `pytest -q` 통과. 기존 테스트 무손상.
  - 마지막에: 추가/변경 파일 목록, 등록한 함수 이름·스케줄, 신규 env 키, Key Vault 에 넣어야 할 값,
    그리고 CF Worker 쪽에서 맞춰야 할 ingest 계약 요약을 출력.

먼저 0단계로 관련 파일을 읽고, 계획을 3~5줄로 보고한 뒤 구현을 시작하라.
```

---

## 참고: 이 작업으로 가이드 대비 바뀌는 점
- 가이드 §2.2 는 **별도 Node 20 `azure-news/` 앱**을 상정했으나, 실제로는 이미 배포된 **AIInvestor
  (Python)** 앱에 Timer 함수로 통합한다. → 대시보드 repo 의 `azure-news/` 폴더는 미사용(이 결정 기록용).
- DeepSeek/Blob/Key Vault/배포 파이프라인을 재사용하므로 새 인프라가 거의 없음.
- 양쪽 합의 지점은 **위 ingest 계약 1개**뿐. Pages Function `/api/ingest/news`(이미 구현·테스트 완료)가 이 계약을 검증한다.
