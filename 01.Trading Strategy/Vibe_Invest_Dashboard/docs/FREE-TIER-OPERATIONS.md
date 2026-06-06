# Cloudflare + Azure 무료 티어로 서비스하기 — 가용성 · 성능 운영 문서

> **버전** v1.0 · 2026-06-06 · 현재 구현 아키텍처(Pages + Pages Functions + Cron Worker) 기준.
> **원칙**: ① 오직 무료 티어만(DeepSeek 제외, 비용 가드 필수) ② 주기 데이터는 미리 계산·저장 →
> CDN 엣지 캐시로 origin 연산 0 에 수렴 ③ 빈 화면 금지(stale 폴백).
> 한도 수치는 2026-06 기준이며 변동 가능 — 분기마다 재확인.

---

## 1. 아키텍처 (무료 구성)

```
사용자 ── HTTPS ──▶ Cloudflare 엣지(CDN, 글로벌)
                     ├─ Pages (정적 프론트, 엣지 캐시)
                     └─ Pages Functions  /api/*   (D1·R2 바인딩, 동일 오리진)
                                  ▲ 읽기(미리 계산된 데이터) + s-maxage 엣지 캐시
        Cron Worker ──쓰기──▶ D1 + R2  ◀──읽기── Pages Functions
        (10분 / 일1회 스케줄)
        AIInvestor (Azure Functions, Python) ──POST /api/ingest/news (HMAC)──▶ Pages Function
          └─ Finnhub 뉴스 + DeepSeek 요약 (1일 9회 KST)
```

| 레이어 | 서비스 | 역할 | 티어 |
|---|---|---|---|
| 프론트 | Cloudflare **Pages** | 정적 SPA 서빙(엣지) | 무료 |
| API | **Pages Functions** | `/api/*` (읽기+ingest) | 무료(Workers 한도 공유) |
| 스케줄 | **Cron Worker** | 시세/시그널 선계산 | 무료(Workers Cron) |
| DB | **D1** (SQLite) | 시그널·요약·집계 | 무료 |
| 객체 | **R2** | 시세 스냅샷 JSON | 무료 |
| 캐시 | **CDN / Cache API** | 엣지 응답 캐시 | 무료 |
| 뉴스 | **Azure Functions**(AIInvestor) | 수집+요약 타이머 | 무료(Consumption) |
| 뉴스 상태 | **Azure Blob** | 처리한 뉴스 id | 무료 한도 |
| LLM | **DeepSeek** | 한국어 뉴스 요약 | **유료**(비용 가드) |
| 데이터 | Stooq CSV / FRED CSV / Finnhub | 일봉·거시·뉴스 | 무료 |

---

## 2. 무료 티어 한도 & 예상 사용량

| 서비스 | 무료 한도(2026-06) | 본 프로젝트 예상 | 여유 |
|---|---|---|---|
| Pages 빌드 | 500 빌드/월, 1 동시 | 배포 시에만(수십/월) | ◎ |
| Pages 정적 요청·대역폭 | 무제한 | — | ◎ |
| Pages Functions(=Workers) | **100K req/day**, 10ms CPU/req | 캐시 미스만 origin 도달 → DAU 수천도 여유 | ◎ |
| Cron Trigger | 무료 포함 | `*/10`=4,320/월 + 일1회 | ◎ |
| D1 | 5GB · 읽기 5M행/day · **쓰기 100K행/day** | 쓰기: 크론 ~1K/day + 검색로그 | ○ (쓰기 감시) |
| R2 | 10GB · Class A 1M/월 | 스냅샷 수십 MB · 쓰기 4,320/월 | ◎ |
| Cache API | 무료(엣지 저장) | 적극 사용 | ◎ |
| Azure Functions | 월 100만 실행 + 400K GB-s | 타이머 ~4,320/월 + 뉴스 9/day | ◎ |
| Azure Blob | 5GB LRS 등(구독별) | 뉴스 id 로그 수 MB | ◎ |
| DeepSeek | **유료** (Claude 대비 ~1/35, 캐시 할인) | 1일 9회 × ~20건 요약 | 월 수백 원 미만(가드 시) |
| Finnhub | 60 calls/min | 뉴스/시세 충분 | ◎ |
| FRED CSV | 무료(키 불필요) | 일1회 7시리즈 | ◎ |
| Stooq CSV | 무료 | 일1회 일봉 | ○ (rate 주의) |

> **유일한 유료 = DeepSeek.** §6 비용 가드로 월 상한을 강제한다.

---

## 3. 가용성 (Availability)

### 3.1 구조적 가용성
- **엣지 분산**: Pages·CDN 은 Cloudflare 글로벌 PoP 에서 서빙 → 단일 서버 장애 개념 없음. 정적/캐시 응답은
  origin(Functions)·DB 가 죽어도 **엣지 캐시로 계속 제공**(`stale-while-revalidate`).
- **읽기/쓰기 분리**: 사용자 트래픽(읽기)은 Pages Functions+캐시가, 데이터 갱신(쓰기)은 Cron Worker 가 담당.
  크론이 멈춰도 **마지막 스냅샷은 계속 노출**(데이터가 늙을 뿐, 다운 아님).

### 3.2 폴백 사다리 (빈 화면 절대 금지)
1. **엣지 캐시 적중** → origin 무접촉 (정상).
2. **캐시 만료 + origin 정상** → 재계산 없이 D1/R2 의 선계산 데이터 반환.
3. **origin/DB 일시 장애** → `stale-while-revalidate` 로 직전 캐시 제공 + 상단 `⚠ 데이터 지연` 배너.
4. **데이터 소스 장애** (Finnhub/Stooq/FRED): 크론이 **직전 스냅샷 유지**(덮어쓰지 않음) + stale 표시.
   - ARDS 거시축은 FRED 막히면 **yfinance/시장 프록시로 자동 대체**(macro.py·rates.py 의 proxy 경로 포팅).
   - 부분 성공 허용: 한 소스 실패가 전체 파이프라인을 죽이지 않게 try/except 격리.
5. **뉴스(Azure) 장애**: ingest 안 오면 D1 의 직전 뉴스 유지. ingest 2xx 아니면 Azure 가 다음 회차 재시도
   (처리 id 미저장).

### 3.3 단일 장애점(SPOF)과 완화
| SPOF | 영향 | 완화 |
|---|---|---|
| Cron Worker 중단 | 데이터 신선도 저하(다운 아님) | CF 대시보드 크론 로그 주1회 확인 + `last_update` 기반 stale 배너 |
| D1 (단일 DB) | 시그널/집계 읽기 실패 | 핵심 시세는 **R2 스냅샷에도 저장** → D1 장애 시 R2 폴백 가능하게 설계 |
| Azure/DeepSeek | 뉴스 요약 정지 | 시세·시그널과 독립 → 뉴스 섹션만 stale, 나머지 정상 |
| 외부 데이터 API | 갱신 실패 | 직전값 유지 + 프록시 폴백 |

### 3.4 신선도 표기(신뢰성 핵심)
- 모든 응답 envelope 에 `updated_at`. 프론트는 `last_update` 20분 경과 시 앰버 `⚠ 데이터 지연 중`.
- 시그널 배지에 산출일 병기(`매수 · 06/05 기준`) — 오래된 데이터를 새것처럼 보이지 않게.

---

## 4. 성능 (Performance)

### 4.1 핵심 전략 — "요청당 origin 연산 0"
- 주기 갱신 데이터(대시보드/시세/급등락/뉴스/랭킹)는 **크론이 미리 계산해 D1·R2 에 저장**.
- 읽기 API 는 **연산 없이 반환** + `Cache-Control: public, s-maxage=N, stale-while-revalidate=2N`
  (`shared/http.ts` jsonResponse). → 대부분의 요청은 **엣지 캐시에서 즉시** 응답(origin 미접촉).
- 권장 TTL: dashboard 60s · movers/rankings/news 300s · 검색/track 캐시 금지(no-store).

### 4.2 지연(latency) 목표
| 경로 | 예상 | 비고 |
|---|---|---|
| 엣지 캐시 적중 | ~10–40ms TTFB | 사용자 대다수 |
| 캐시 미스 → Pages Function + D1 읽기 | ~30–120ms | D1 단순 SELECT |
| R2 스냅샷 서빙 | ~수십 ms | 대용량 JSON 은 R2 직접 + 캐시 |
| Cron 일1회 시그널 산출 | 초~수십초(백그라운드) | 사용자 경로 아님 |

### 4.3 콜드스타트
- **Pages Functions/Worker**: V8 isolate 모델 → 콜드스타트 사실상 무시(~0ms). 유리.
- **Azure Functions(Consumption)**: 콜드스타트 수백 ms~수초 가능. 뉴스는 사용자 동기 경로가 아니라 타이머라
  체감 영향 없음. (AIInvestor 는 prewarm 인스턴스 1개 운영 — 텔레그램 웹훅용.)

### 4.4 CPU 10ms 제약 대응
- Pages Functions 요청당 CPU 10ms 제한 → **무거운 연산(시그널 계산·집계)은 절대 요청 경로에서 안 함**.
  전부 Cron Worker 가 선계산. 요청은 읽기+직렬화만.
- 시그널 엔진(`shared/`)은 Cron Worker 컨텍스트에서 실행(일1회) → 10ms 제약과 무관.

### 4.5 프론트 성능
- 단일 esbuild 번들(minify) + 차트는 경량 SVG 직접 렌더(차트 라이브러리 무거움 회피).
- 로딩은 스켈레톤(스피너 금지), 섹션 staggered fade 1회, `prefers-reduced-motion` 존중.
- 정적 자산은 Pages 엣지 캐시(불변 자산 해시 파일명 권장).

---

## 5. 데이터 파이프라인의 연산 절약 설계
- **10분 크론**: 미 장외 시간(UTC 13:00–21:30 밖)이면 핸들러 첫 줄에서 조기 return → API 호출·연산 절약.
- **일1회 크론**: 미 장마감 직후 1회만 일봉 수집 + 시그널 산출 → D1 기록.
- **중복 억제**: 뉴스는 직전 처리 id 와 비교해 신규만 DeepSeek 호출. 시세는 변경분만 D1 upsert.
- **쓰기 최소화**: 검색 로그는 D1 쓰기 80% 도달 시 샘플링 전환(§7).

---

## 6. 비용 가드 (유일한 유료 = DeepSeek)
1. 신규 뉴스 0건이면 DeepSeek 호출/POST **스킵**.
2. `max_tokens` 상한(요약 800 수준) + 회차당 1회 호출.
3. (선택) 미 장중 시간대에만 요약 실행.
4. DeepSeek 프롬프트 캐시 활용(반복 시스템 프롬프트 할인).
5. 월 비용 알림 상한 설정(운영 체크리스트).

---

## 7. 한도 도달 신호 & 대응 (스케일업)
| 신호 | 임계 | 대응 |
|---|---|---|
| D1 쓰기 | 일 80K행(80%) | 검색 로그 샘플링/배치 집계 전환 |
| Pages Functions req | 80K/day(80%) | 캐시 TTL 상향, 정적화 가능한 응답 분리 |
| Pages 빌드 | 400/월 | 배포 묶기(불필요한 재배포 억제) |
| Azure 실행 | 80만/월 | 타이머 주기 완화, 불필요 타이머 정리 |
| DeepSeek 비용 | 월 상한 80% | 요약 빈도/대상 축소, 장중 한정 |
| R2 Class A | 80만/월 | 스냅샷 묶기, 히스토리 보존주기 단축 |

---

## 8. 모니터링 체크리스트 (주1회)
- [ ] CF 대시보드: Pages Functions 에러율 + Cron 실행 로그
- [ ] D1 쓰기량(80% 경보) · R2 사용량
- [ ] Azure Functions 실행 횟수 무료 한도
- [ ] DeepSeek 월 비용(상한 알림)
- [ ] `last_update` stale 여부(데이터 신선도)
- [ ] Finnhub/Stooq/FRED 파싱 실패 → 직전값 유지 동작 확인
- [ ] (첫 한 달) 시그널 결과 vs 기존 Python 주간 대조
- [ ] Cloudflare Web Analytics(보조 지표) 활성

---

## 9. 비용 요약 (정상 운영 시)
- Cloudflare(Pages/Functions/D1/R2/Cron/CDN): **$0**
- Azure(Functions/Blob, 무료 한도 내): **$0**
- DeepSeek: 가드 적용 시 **월 수백 원 미만** 예상
- 도메인(선택, 2단계): `vibe-invest.com` CF Registrar 원가 ~$10.46/년 (1단계는 `*.pages.dev` 무료)
- **합계: 사실상 도메인 비용만.**
