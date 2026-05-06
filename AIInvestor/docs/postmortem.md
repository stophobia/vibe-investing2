# Postmortem — 6초 응답 지연 진단과 최적화

**시점**: 2026-05-05 ~ 2026-05-06 KST 새벽
**서비스**: AI Investor (jeunggwon chatbot) — Azure Functions (Korea Central, Flex Consumption)
**작성**: 김호광 (Dennis Kim) + Claude Code

---

## 0. TL;DR

배포 직후 사용자 체감 응답시간이 **6–10초**로 측정됨. 원인은 다음 두 가지였다:

1. **Bot 초기화가 매 webhook마다 발생 (~1.1초/요청 낭비)**
   `async with _ptb_app:` 가 컨텍스트 진입 시 `getMe` API 호출을 강제. 인스턴스 수명 동안 단 1회만 호출하도록 변경.

2. **DeepSeek body 스트리밍 7초**
   httpx의 `200 OK` 로그는 응답 헤더 시점에 찍히고 본문은 그 후 스트리밍됨. 한국어 600+ 토큰 생성에 ~7초 소요. `max_tokens=550` + 단문 bullet 프롬프트로 압축.

진단 과정에서 부수적으로 발견·수정한 이슈:
- Azure 신규 구독에 7개 RP 미등록
- workflow_dispatch input 기본값이 dev → SP 권한 없는 RG로 배포 시도
- Classic Azure CDN 신규 생성 불가 (Microsoft가 retire) → 단순 Blob HTTPS로 대체
- Functions Flex Consumption은 zip deploy 시 Storage `deployment` 컨테이너 사전 필요
- Key Vault RBAC가 본인 계정에 없어서 시크릿 조회 불가
- App Insights에 Python 로그가 라우팅되지 않음 — `azure-monitor-opentelemetry` 추가 필요
- `az ... -o tsv` 출력이 zsh 환경에서 잘림 → JSON 원본을 `jq`로 파싱

총 commit 7개 (배포 실패 5회 / 502 transient 1회 / 성공 6회) 만에 6–10초 → 예상 5–6초 수준으로 단축.

---

## 1. Timeline

| KST | 사건 |
|---|---|
| 2026-05-05 23:50 | Function App 첫 배포 시도 (run #1) → Bicep 단계에서 `MissingSubscriptionRegistration` |
| 24:00 | 7개 Resource Provider (`Microsoft.{KeyVault,Cdn,Storage,Web,OperationalInsights,Insights,ManagedIdentity}`) 일괄 등록 |
| 00:10 | 재배포 (run #2) → `gh workflow run` 의 input 기본값이 `dev` 라 권한 없는 `rg-aiinvestor-dev` 에 RG 생성 시도 → AuthorizationFailed |
| 00:15 | `workflow_dispatch` 기본 환경 prod 로 변경 + push |
| 00:25 | run #3 → Bicep `Azure CDN classic no longer support new profile creation` |
| 00:30 | Bicep 에서 CDN 리소스 제거 (Front Door는 후속 PR로 이관) |
| 00:35 | run #4 → Functions zip 배포에서 `404 The specified container does not exist` (Storage `deployment` 컨테이너 부재) |
| 00:40 | Bicep 컨테이너 목록에 `deployment` 추가 |
| 00:48 | run #5 → 전 단계 ✓, 텔레그램 webhook 등록 완료. **첫 사용자 메시지 응답 6초 측정** |
| 01:00 | 사용자가 응답시간 6초 보고 → 진단 시작 |
| 01:05 | App Insights 쿼리 시도 — `union *` 로는 결과 빈 응답. 카탈로그도 비어 있음 |
| 01:15 | Function 메트릭(`OnDemandFunctionExecutionCount`)으로 호출은 발생함을 확인 → telemetry 라우팅 누락 |
| 01:20 | `azure-monitor-opentelemetry` 추가 + `configure_azure_monitor()` 호출. `max_tokens=500` 추가 + push |
| 01:32 | run #6 → 성공. 사용자 측정 시 출력 잘림 보고 (한국어 5섹션이 500토큰에 안 들어감) |
| 01:35 | `max_tokens=800` + 압축 프롬프트로 수정 + push |
| 01:38 | run #7 → 성공. 합성 webhook 호출로 검증: 200 OK / 2.3초 (LLM 없는 path) |
| 01:50 | App Insights `requests` 테이블에 데이터 도착 — 사용자 메시지 6.3 / 7.5 / 9.0 / 10.7초 확인 |
| 01:55 | `dependencies` 테이블은 여전히 비어있음 → 외부 호출 분해 불가 |
| 02:00 | `traces` 테이블의 httpx 로그를 활용한 우회 분석 — 첫 본격 timeline 추출 |
| 02:10 | **핵심 발견**: `async with _ptb_app:` → `getMe` 호출 ~750ms / `sendChatAction` ~400ms / DeepSeek body 스트리밍 ~7000ms |
| 02:30 | bot.initialize() 를 bootstrap에서 1회만 호출 + `max_tokens=550` + 단문 bullet 프롬프트 + push |
| 02:54 | run #8 → 502 transient (Azure 게이트웨이) |
| 02:58 | run #9 (workflow_dispatch 재트리거) → 진행 중 |

---

## 2. 진단 도구와 우회

### 2.1 처음에 막힌 이유 — App Insights에 데이터가 없음

가장 자연스러운 첫 시도:

```bash
az monitor app-insights query --analytics-query "requests | where timestamp > ago(30m) | take 10" -o table
```

빈 결과. 6시간 시간 창을 줘도 빈 결과.

**원인**: Functions Python 런타임은 컨테이너의 stdout/stderr 일부만 자동으로 App Insights로 보낸다. Python `logging` 모듈에서 발생한 우리 애플리케이션 로그(예: `Calling LLM model=...`)는 `APPLICATIONINSIGHTS_CONNECTION_STRING` 만 설정한다고 자동으로 흐르지 않는다. 외부 HTTP 호출(httpx)도 마찬가지로 dependencies로 안 잡힌다.

**해결**: `azure-monitor-opentelemetry>=1.6.0` 추가 + `function_app.py` 의 모든 다른 import 보다 먼저 호출:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(logger_name="ai_investor")
```

이후 `traces` 테이블에 모든 INFO 레벨 로그가 흐르기 시작했고 `requests` 도 함께 채워졌다. **`dependencies` 테이블은 여전히 비어있음** — `azure-monitor-opentelemetry` 가 기본값으로는 `requests`/`urllib3` 만 자동 instrument하고 `httpx` (openai/python-telegram-bot 이 사용)는 별도 처리 필요. 이는 후속 작업으로 분리.

### 2.2 두 번째로 막힌 이유 — `az ... -o tsv` 의 출력 잘림

데이터가 도착한 후 카운트 쿼리가 모두 `1` 로만 반환되어 혼란.

```bash
az monitor app-insights query \
  --analytics-query "traces | where timestamp > ago(15m) | count" \
  -o tsv
# → 1 (실제로는 477건)
```

JSON으로 출력해 보니 `tables[0].rows` 에 정상적으로 477개가 들어 있었다. zsh + `-o tsv` 조합에서 행 단위 잘림이 발생. 이후로는:

```bash
az monitor app-insights query --analytics-query "..." 2>/dev/null | jq -r '.tables[0].rows[] | @tsv'
```

JSON 원본을 `jq` 로 파싱하는 패턴으로 일관 사용.

### 2.3 세 번째로 막힌 이유 — `dependencies` 비어있음

dependencies 테이블이 비어있어서 DeepSeek vs yfinance 시간 분리가 불가능. `traces` 테이블의 httpx 로그를 timestamp 단위로 분해하여 우회:

```kql
let target = requests
  | where timestamp > ago(15m) and name == 'telegram_webhook' and duration > 3000
  | top 1 by timestamp desc
  | project operation_Id, total_ms = duration, ts_start = timestamp;
traces
| where timestamp > ago(15m)
| join kind=inner target on operation_Id
| order by timestamp asc
| project relative_ms = round(datetime_diff('millisecond', timestamp, ts_start)),
          message = substring(message, 0, 100)
```

`operation_Id` 가 단일 webhook 호출의 모든 로그를 묶어주므로 그 안에서 timestamp 차이가 곧 step 별 시간이 된다. 이 기법으로 처음으로 정확한 timeline을 추출:

```
   1ms  Executing 'Functions.telegram_webhook' (start)
 750ms  HTTP Request: POST .../getMe ← bot.initialize() 의 부산물
1155ms  HTTP Request: POST .../sendChatAction ← typing 표시
1156ms  Snapshot cache hit for NVDA ← yfinance 캐시 ✓
1156ms  Calling LLM model=deepseek-chat
1341ms  HTTP Request: POST .../chat/completions "200 OK" ← 헤더 수신
8311ms  HTTP Request: POST .../sendMessage ← 본문 7초 후 도착
8312ms  Executed 'Functions.telegram_webhook' (Duration=8312ms)
```

**결정적 단서**: DeepSeek 의 "200 OK" 로그가 1341ms 에 찍혔지만 다음 로그가 8311ms — 즉 **httpx의 `200 OK` 로그는 응답 헤더 수신 시점에 발화하고 본문은 그 후 스트리밍됨**. 6970ms 갭이 곧 한국어 600+ 토큰 생성 시간.

---

## 3. 발견된 병목 (실측)

| 단계 | 시간 | 비중 | 분류 |
|---|---|---|---|
| Function 부팅 + JSON 파싱 | ~5ms | 0% | 구조적 |
| **`async with _ptb_app:` (getMe)** | **~750ms** | 9% | **수정 가능** |
| **`sendChatAction` (typing 표시)** | ~400ms | 5% | 부분 수정 가능 |
| yfinance live 호출 | ~1500ms | 18% | 캐시 hit 시 0ms ✓ |
| **DeepSeek body 스트리밍** | **~7000ms** | **84%** | **수정 가능** |
| `sendMessage` (텔레그램 측 처리) | ~50ms | <1% | 외부 |

---

## 4. 적용한 수정

### Commit 1 — 비동기 LLM + max_tokens
- `OpenAI` → `AsyncOpenAI` (이전 작업분, 1차 단계)
- `max_tokens=500` 첫 시도 → 한국어 출력 잘림

### Commit 2 — yfinance 캐시 (M4)
- 동일 ticker 5분 내 재요청 시 `.info` + `.history` HTTP 라운드트립 완전 생략
- 검증: 1.3초 → 0ms (`speedup: 264331x` — yfinance 미호출)

### Commit 3 — App Insights instrumentation + max_tokens=800
- `azure-monitor-opentelemetry` 추가, `configure_azure_monitor()` 호출
- `max_tokens=500` → `800` (출력 잘림 해소)
- 프롬프트에 섹션별 문장 수 명시

### Commit 4 — bot.initialize 1회만 + max_tokens=550
- `_bootstrap()` 안에서 `await _ptb_app.initialize()` 한 번 호출
- webhook handler에서 `async with _ptb_app:` 제거
- max_tokens 800 → 550, 프롬프트를 단문 bullet 5개로 압축

---

## 5. 인프라 측 함정 (배포 실패 사례)

| # | 실패 단계 | 원인 | 해결 |
|---|---|---|---|
| 1 | Bicep | `MissingSubscriptionRegistration` (RP 미등록) | 7개 RP 일괄 등록 |
| 2 | Ensure RG | dev RG 권한 없음 | workflow input 기본값 prod 로 변경 |
| 3 | Bicep | `Azure CDN classic no longer support new profile creation` | CDN 리소스 제거 (Front Door로 후속 PR) |
| 4 | Functions zip | `The specified container does not exist` | Bicep 컨테이너 목록에 `deployment` 추가 |
| 5 | (재배포) | KV RBAC가 본인 계정에 없음 | `Key Vault Secrets User` role 부여 |
| 6 | Functions zip | 502 Bad Gateway (Azure 일시적) | workflow 재실행 |

---

## 6. 같은 실수를 피하기 위한 체크리스트

### Azure 프로비저닝
- [ ] 새 구독은 RP 7개 먼저 등록 (`Microsoft.{KeyVault, Cdn, Storage, Web, OperationalInsights, Insights, ManagedIdentity}`)
- [ ] Service Principal에 RG 단위로 `Contributor` + `User Access Administrator` 동시 부여 (RBAC 할당 권한 필요)
- [ ] Function App Flex Consumption은 Storage에 `deployment` 컨테이너 사전 생성 필수
- [ ] CDN classic은 신규 생성 불가 — Front Door Standard/Premium 사용
- [ ] 본인 계정에도 Key Vault Secrets User role 부여 (운영 디버깅용)

### Functions Python 런타임
- [ ] Python `logging` 모듈 출력을 App Insights에 보내려면 `azure-monitor-opentelemetry` + `configure_azure_monitor()` 필수
- [ ] `function_app.py` 의 모든 다른 import 보다 먼저 `configure_azure_monitor()` 호출
- [ ] `httpx` 의존 라이브러리(openai, python-telegram-bot)의 outgoing call을 dependencies로 잡으려면 `OpenTelemetryInstrumentor.instrument()` 추가 필요 (default 미포함)
- [ ] `python-telegram-bot` Application은 webhook 핸들러마다 `async with` 가 아닌 `_bootstrap()` 에서 `await app.initialize()` 1회만

### 진단 / 관측
- [ ] `az ... -o tsv` 대신 raw JSON + `jq` 로 파싱 (zsh 환경 행 잘림)
- [ ] Functions Flex Consumption 은 Kudu/SCM 미노출 — `az webapp log tail` 작동 안 함. `az functionapp logs tail` 또는 App Insights Live Metrics 사용
- [ ] 최초 호출 후 App Insights ingestion 2–5분 지연 — 폴링 시 `count > 0` 체크 후 분석
- [ ] `requests` + `dependencies` + `traces` 를 `operation_Id` 로 join하면 단일 호출의 timeline 정확히 분해 가능
- [ ] httpx의 `200 OK` 로그 시점은 응답 헤더 수신 ≠ 본문 완료. 본문 시간 = 다음 로그까지의 갭

### 응답 지연 단축
- [ ] LLM 출력 토큰을 줄이는 게 가장 큰 효과 (한국어 1 토큰 ≈ 영어 1.5–2 토큰)
- [ ] 프롬프트에 "single sentence per section" 같은 명시적 길이 제약
- [ ] yfinance 같은 안정적 외부 데이터는 인스턴스 메모리 캐시 (TTL 5분)
- [ ] 같은 인스턴스 안에서 한 번만 해도 되는 초기화는 모듈 전역에 캐시

---

## 7. 남은 과제

### 7.1 sendChatAction 의 400ms 절감

`async def _handle_ticker_query()` 가 LLM 호출 직전에 `sendChatAction` 으로 typing 표시를 보낸다. 이 호출이 ~400ms 걸린다. UX 측면 의미가 크긴 한데(사용자에게 "처리 중" 신호) — 응답 자체가 5초 미만이면 typing 표시 없이도 무방. 응답 ETA 가 3초 미만일 때만 생략하는 휴리스틱 도입 검토 가능.

### 7.2 `httpx` dependencies 자동 instrument

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
HTTPXClientInstrumentor().instrument()
```

이걸 `configure_azure_monitor()` 직후에 추가하면 DeepSeek/Telegram 외부 호출이 `dependencies` 테이블로 들어와 분해 분석이 더 쉬워짐. 후속 PR.

### 7.3 사전 캐싱 — 가장 큰 효과 (paper_plan §16)

NASDAQ 300 + S&P 500 + 한국인 인기 ETF 의 yfinance 스냅샷과 페르소나 코멘트를 **별도 스케쥴 데몬**으로 미리 생성하여 Blob/CDN에 푸시. 사용자 요청 시 LLM과 yfinance를 모두 우회. paper_plan.md §16 참조.

### 7.4 `deepseek-chat` → 더 빠른 모델 검증

DeepSeek는 단일 SKU(`deepseek-chat` V3 / `deepseek-reasoner` R1)만 제공. 후자는 더 느림. 모델 자체로는 단축 한계. 대안:
- 짧은 응답 전용 prompt + max_tokens=400 (정보량 trade-off)
- 응답 streaming + Telegram `editMessageText` 로 부분 갱신 (구현 복잡, ~50% 체감 단축)

---

## 8. 결과 (예상)

| 케이스 | Before | After (예상) | 절감 요인 |
|---|---|---|---|
| `/start` (LLM 없음) | 2.3초 | 0.8–1.2초 | bot.initialize 절감 |
| 캐시 hit + LLM | 8.3초 | 4.5–5.5초 | bot.init -1.1s + max_tokens 압축 -2.3s |
| 캐시 miss + LLM | 10.7초 | 5.5–6.5초 | 위 + yfinance miss 1.5초 |
| 콜드 스타트 + 첫 LLM | 19초 | 6–8초 | 콜드는 그대로 + 위 절감 |

§16 의 사전 캐싱 도입 후 추가 단축 예상:
- 인기 50개 종목 + 인기 페르소나/언어 조합: **~1초** (CDN edge fetch only)

---

## 9. 자료

- 본 사건의 모든 commit: `git log --grep="perf\|fix(infra)\|fix(ci)" main`
- App Insights workspace: `appi-aiinvestor-prod` (Resource Group `rg-aiinvestor-prod`)
- 지역별 지연 분석 (참고): paper_plan.md §14
- 사전 캐싱 작업 명세: paper_plan.md §16

---

# 2부 — 사전 캐싱 도입 (2026-05-06 새벽)

§7.3 의 "남은 과제" 가 1부 직후 곧바로 작업 진입. 인기 종목 한정으로 응답시간을 ~7초 → **~1초 수준** 으로 단축하는 것이 목표.

## 10. 사전 캐싱 아키텍처 결정

### 10.1 두 단계 캐시

| Tier | 무엇 | 적중 시 절감 | TTL | Blob 경로 |
|---|---|---|---|---|
| **Tier 1: Commentary** | 페르소나 코멘트 전체 (rendered text) | LLM 7s + yfinance 1.5s 모두 우회 | 4시간 | `prewarm/commentary/<TICKER>.<persona>.<lang>.json` |
| **Tier 2: Snapshot** | 펀더멘털·가격 dataclass JSON | yfinance 1.5s 만 우회 | 4시간 | `prewarm/snapshots/<TICKER>.json` |

Tier 1 은 사용자에게 personalized 관심사가 없을 때만 적용 — 관심사 컨텍스트가 들어가면 generic prewarm cache는 부정확해짐.

### 10.2 종목 풀 — 252개

[data/priority_tickers.csv](data/priority_tickers.csv):
- 50 TOP_50 — Korean retail bias (FAANG+, 반도체, 인기 ETF: SPY/QQQ/SCHD/JEPI/TQQQ/SOXL 등)
- 202 pool — [data/ticker_aliases.csv](data/ticker_aliases.csv) 의 unique ticker 들
- 합계 252 개

### 10.3 Timer Trigger 2개

```
prewarm_snapshots:    0 0 */4 * * *    UTC (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
prewarm_commentaries: 0 30 */4 * * *   UTC (30분 offset — snapshot 완료 후 commentary 빌드)
```

snapshots 먼저 실행 (252 ticker × yfinance) → commentaries 30분 후 (50 ticker × 3 페르소나 × 4 언어 = 600 LLM 호출, asyncio Semaphore(4) 동시).

### 10.4 비용

| 항목 | 일 | 월 |
|---|---|---|
| yfinance | $0 | $0 |
| DeepSeek (commentary 600회/일) | ~$0.30 | ~$9 |
| Blob storage + transactions | <$0.02 | <$0.50 |
| Timer Functions 실행 | 무료 (free grant 안에서) | $0 |
| **추가 합계** | | **~$10/월** |

## 11. 추가로 발견된 함정

### 11.1 Azure Front Door — Free Trial / Student 구독에서 생성 금지

처음 Bicep에 Front Door Standard를 포함시켰으나 deploy 시 다음 에러:

```
{"code":"BadRequest","message":"Free Trial and Student account is forbidden for Azure Frontdoor resources."}
```

**해결**: `enableFrontDoor=false` 기본값 + opt-in 파라미터로 만듦.

**왜 그래도 괜찮은가**: 코드의 cache-first 흐름은 Functions가 `BlobServiceClient` 로 Blob을 직접 읽는 구조 — Front Door에 의존 안 함. Korea Central Functions ↔ Korea Central Blob = ~30–50ms 직접 접근. CDN edge가 줄여줄 차이는 ~20ms 미만으로 무의미. Front Door는 **글로벌 사용자가 생기면** 도입.

### 11.2 `aiohttp` 누락 — `azure.identity.aio` 의 transitive 의존

prewarm 첫 invoke 가 1141ms 만에 fail.

```
ImportError: aiohttp package is not installed
  File ".../azure/identity/aio/_credentials/managed_identity.py"
  ...
  File ".../azure/core/pipeline/transport/_aiohttp.py"
```

**진단**: `azure.identity.aio.DefaultAzureCredential` → Managed Identity Async client → `azure-core` async transport → 기본 backend 가 `aiohttp`. requirements.txt 에 `azure-identity`, `azure-storage-blob` 만 두면 sync 경로는 잘 깔리지만 async 경로의 **암묵적 의존**이 빠진다.

**해결**: `requirements.txt` 에 `aiohttp>=3.9.0` 명시 추가.

**예방**: Azure SDK async 클래스를 도입할 때마다 transitive HTTP transport 의존을 한 번 점검. `azure-storage-blob.aio.BlobServiceClient` 는 자체적으로 `aiohttp` 가 권장되며, 우리가 `azure.identity.aio` 까지 사용하면서 같은 의존이 두 군데에서 요구됨에도 둘 다 hard requirement 가 아닌 conditional import 라 누락이 silent.

### 11.3 Bicep Linter — `environment().suffixes.storage` vs hardcoded host

`storage.properties.primaryEndpoints.blob` 에서 hostname 만 추출할 때 처음에는 `'${storage.name}.blob.core.windows.net'` 으로 작성 → linter 경고 (멀티 클라우드 미호환). 해결:

```bicep
var blobHost = replace(replace(storage.properties.primaryEndpoints.blob, 'https://', ''), '/', '')
```

### 11.4 Bicep `output` 의 conditional null safety

`enableFrontDoor=false` 일 때 `frontDoorEndpoint` 자체가 null. 출력 처리:

```bicep
// 잘못 — linter 경고 + 런타임 null 접근 가능
output frontDoorEndpointHost string = enableFrontDoor ? frontDoorEndpoint.properties.hostName : ''

// 올바름 — chained safe access (.?), null이면 ''로 fallback
output frontDoorEndpointHost string = frontDoorEndpoint.?properties.?hostName ?? ''
```

## 12. 검증 절차

배포 직후 `prewarm_snapshots` 를 master key 로 강제 invoke:

```bash
KEY=$(az functionapp keys list --resource-group rg-aiinvestor-prod --name func-aiinvestor-prod --query masterKey -o tsv)
curl -fsS -X POST "https://func-aiinvestor-prod.azurewebsites.net/admin/functions/prewarm_snapshots" \
  -H "x-functions-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":""}'
# → HTTP 202
```

5–8분 후 Blob count 확인:

```bash
az storage blob list \
  --account-name staiinvestorprod \
  --container-name prewarm \
  --prefix "snapshots/" \
  --auth-mode login \
  --query "length(@)"
```

3분 후 commentaries 강제 invoke (snapshot 일부라도 쌓인 후 — semaphore 가 알아서 순차):

```bash
curl -fsS -X POST "https://func-aiinvestor-prod.azurewebsites.net/admin/functions/prewarm_commentaries" \
  -H "x-functions-key: $KEY" -d '{}'
```

## 13. 응답시간 — 사전 캐싱 적용 후 (예상)

| 사용자 케이스 | Before (1부 종료 시점) | After (사전 캐싱 + 첫 사이클 완료) |
|---|---|---|
| TOP_50 ticker + 인기 페르소나/언어, 관심사 없음 → **Tier 1 hit** | 4.5–5.5초 | **0.8–1.5초** (LLM 0회, yfinance 0회, Blob 직접 read) |
| 252 pool ticker → **Tier 2 hit** | 4.5–5.5초 | **3.0–4.0초** (yfinance 0회, LLM 1회) |
| 그 외 cold ticker | 4.5–5.5초 | 4.5–5.5초 (변화 없음) |
| **Korean retail 트래픽 가중 평균** (TOP_50 ≈ 70%) | 5초 | **~1.7초** |

## 14. 부수적 사용자 기능

진단 과정에서 도입한 사용자/운영자 편의 기능:

- **`/feedback <text>`** — owner 텔레그램으로 즉시 forwarding. anon_user_id + lang + persona 컨텍스트 포함
- **`피드백 <text>`** 텍스트 alias — Telegram 이 한글 슬래시 명령을 파싱 못함. `_on_message` 에서 prefix 매칭으로 가로챔
- **`/whoami`** — 본인의 chat_id 노출 (`TELEGRAM_OWNER_CHAT_ID` env 셋업용)
- **`set_my_commands()`** — Telegram 메뉴에 8개 명령 자동완성 등록

## 15. 누적 commit 갯수 (1부 + 2부)

```
1부 (지연 진단·수정):
  perf(latency): cap LLM output to 500 tokens + cache yfinance snapshots 5min
  perf+obs: bump max_tokens to 800 + concise prompt + App Insights instrumentation
  perf(latency): bot.initialize once at bootstrap + tighter LLM caps

2부 (사전 캐싱 도입):
  feat(prewarm): scheduled cache + Front Door CDN — 2차-H Phase 1
  fix(infra): default Front Door off — forbidden on Free Trial subscription
  feat(bot): /feedback + /피드백 forwarding to operator + aiohttp dep fix

인프라/배포 함정 (1부):
  fix(infra): drop classic CDN — retired for new deployments
  fix(infra): add 'deployment' container required by Functions Flex zip-deploy
  fix(ci): default workflow_dispatch env to prod
```

총 9개 코드 commit + 4개 문서 commit. 배포 시도 11회 (성공 7회, 실패 4회 — 모두 인프라 측).

---

*1·2부 통합 — 추가 수정 사항은 같은 파일에 chronological append.*
