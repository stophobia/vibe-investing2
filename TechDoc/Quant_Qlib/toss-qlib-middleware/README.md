# toss-qlib-middleware

> 토스증권 Open API의 인증(OAuth2)과 시세 데이터 조회를 [Microsoft Qlib](https://github.com/microsoft/qlib) 파이프라인에 연결하는 Node.js/TypeScript 미들웨어. Redis를 토큰 캐시·시세 캐시로 사용한다.
>
> English version: [README_EN.md](README_EN.md)

전체 설계 배경, 아키텍처, Redis 캐싱 전략은 상위 문서를 함께 참고할 것:
[`../Qlib-getting-started-KR.md`](../Qlib-getting-started-KR.md) 7.4절.

토스 Open API 자체에 대한 더 깊은 분석(엔드포인트 20개 전체 목록, 활용 시나리오, 설계 제약)은 저장소의 [`Toss/`](../../../Toss) 프로젝트를 참고했다:

- [`Toss/GUIDE.md`](../../../Toss/GUIDE.md) — 실제 동작하는 토스 Open API 연동 대시보드의 설치·연동 가이드
- [`Toss/src/toss.js`](../../../Toss/src/toss.js) — 인증·시세 클라이언트 실 구현 (이 미들웨어의 엔드포인트 경로·필드 파싱 방식의 근거)
- [`Toss/docs/Toss_OpenAPI_Guide.md`](../../../Toss/docs/Toss_OpenAPI_Guide.md) — 20개 엔드포인트 전체 목록, 인증/토큰 정책, 활용 시나리오, 설계 제약

**이 미들웨어의 범위는 인증과 시세/종목 데이터 조회까지다. 주문 생성·정정·취소 같은 실거래(트레이딩) 기능은 의도적으로 포함하지 않았다.** 이유와 확장 방법은 [`src/trading/README.md`](src/trading/README.md) 참고.

---

## 왜 필요한가

Qlib는 Python 프레임워크지만 Qlib가 실제로 요구하는 것은 "정해진 CSV 형식의 데이터"뿐이다. 이 미들웨어는 토스증권 Open API에서 시세를 받아와 Qlib의 CSV 관례(`date,open,high,low,close,volume,symbol,factor`)로 정규화하고 `dump_bin.py`에 바로 넘길 수 있게 한다.

```
TOSS Open API  --OAuth2-->  [Node.js/TS 미들웨어]  --CSV(csv_kr/*.csv)-->  scripts/dump_bin.py  -->  ~/.qlib/qlib_data/kr_data
                                   |
                                 Redis (토큰 캐시 + 시세 캐시)
```

## 인증 (확인된 사양)

| 항목 | 내용 |
| :--- | :--- |
| 방식 | OAuth2 Client Credentials Grant |
| 토큰 발급 | `POST {TOSS_BASE_URL}/oauth2/token` — `grant_type`, `client_id`, `client_secret`을 **form-urlencoded 바디**로 전송 (Basic Auth 아님) |
| 유효기간 | 86,400초(24시간), **refresh token 없음** — 만료 전 client_secret으로 직접 재발급해야 함 |
| 호출 헤더 | `Authorization: Bearer {access_token}` |
| 계좌/주문 API | `X-Tossinvest-Account` 헤더 추가 필요 (이 미들웨어는 호출하지 않음) |

`scripts/setup.sh`로 `.env`를 만들면서 실제로 토큰 발급을 즉시 테스트해볼 수 있다 (아래 빠른 시작 참고).

## 빠른 시작

```bash
cd TechDoc/Quant_Qlib/toss-qlib-middleware
npm install
npm run setup       # 대화형으로 .env 생성 + 원하면 토큰 발급 테스트까지 수행
npm run typecheck
npm test             # Redis 서버 없이도 통과 (인메모리 어댑터로 로직 검증)
npm run dev            # http://localhost:4000, 실제 Redis 필요
```

`npm run setup` 없이 수동으로 하려면:

```bash
cp .env.example .env   # TOSS_CLIENT_ID / TOSS_CLIENT_SECRET 채우기
chmod 600 .env
```

## Redis 캐싱 전략

| 캐시 대상 | 키 | TTL | 이유 |
| :--- | :--- | :--- | :--- |
| Access Token | `toss:access_token` | `86400 - 안전마진(기본 1시간)` | refresh token이 없으므로 만료 훨씬 전에 선제 재발급 |
| 토큰 재발급 락 | `toss:access_token:lock` | 10초 (`SET NX`) | 여러 요청이 동시에 재발급하지 않도록 thundering herd 방지 |
| 확정된 과거 캔들 | `toss:candles:{symbol}:{interval}:{start}:{end}` | 하루 | 마감된 캔들은 값이 바뀌지 않음 |
| 당일(미확정) 캔들 | 위와 동일 키 | 30초(기본) | 장중에는 값이 계속 갱신됨 |
| 현재가 | `toss:price:{symbol}` | 5초(기본) | 실시간성 필요, 종목 단위로 캐시해 배치 요청 재사용 |

401 응답을 받으면 캐시를 즉시 비우고 한 번 재시도하며, 429(rate limit)는 `Retry-After` 헤더를 보고 backoff 후 재시도한다.

## API 및 캔들 페이지네이션

토스 캔들 API는 요청당 최대 200개(`count`)만 반환하고 `start`/`end` 필터가 없다. 이 미들웨어는 최신 캔들부터 `before` 커서로 역순 페이지네이션하며 목표 시작일에 도달하면 멈추고, 결과를 오름차순으로 정렬해 반환한다 (`Toss/src/toss.js`의 `fetchCandles`와 동일한 전략).

| 메서드 | 경로 | 설명 |
| :--- | :--- | :--- |
| GET | `/health` | 헬스체크 |
| GET | `/api/candles/:symbol?start=&end=&interval=day` | 정규화된 캔들 JSON 조회 (Redis 캐시 경유, `before` 페이지네이션 내장) |
| GET | `/api/prices?symbols=005930,000660` | 현재가 배치 조회 (콤마 구분, 최대 200개씩 청크) |
| POST | `/api/export/qlib` `{symbols, start, end, outDir?}` | 여러 종목을 조회해 `csv_kr/{symbol}.csv` 생성 |

서버 없이 바로 CSV만 뽑고 싶으면:

```bash
npm run export:qlib -- --symbols 005930,000660 --start 2020-01-01 --end 2026-07-01
```

생성된 CSV는 Qlib 가이드 7.2절의 변환 명령으로 그대로 넘긴다:

```bash
python scripts/dump_bin.py dump_all \
    --csv_path ./csv_kr \
    --qlib_dir ~/.qlib/qlib_data/kr_data \
    --include_fields open,close,high,low,volume,factor \
    --date_field_name date --symbol_field_name symbol
```

## 트레이딩(주문 실행)은 왜 포함하지 않았는가

인증과 시세 조회는 누구에게나 거의 동일하게 필요한 공통 기반이라 미들웨어로 만들 가치가 있다. 반면 주문 로직(상태 관리, 재시도 시 중복 주문 방지, 리스크 한도, 체결 확인)은 각자의 전략·리스크 허용도에 따라 완전히 달라지므로 범용으로 만드는 것 자체가 위험하다고 판단했다. 확장 방법은 [`src/trading/README.md`](src/trading/README.md) 참고.

## 프로젝트 구조

```
src/
  config.ts              환경변수 로딩 (지연 평가)
  types.ts                토스 응답/Qlib CSV 타입
  cache/
    redisPort.ts          Redis 의존성 추상 인터페이스
    ioredisAdapter.ts      프로덕션 구현 (ioredis)
    memoryAdapter.ts        테스트/로컬용 인메모리 구현
  auth/tokenService.ts     OAuth2 토큰 발급 + Redis 캐시 + 재발급 락
  market/
    tossClient.ts          인증 붙은 HTTP 클라이언트 (401/429 처리)
    marketDataService.ts    캔들 조회 + before 페이지네이션 + Redis 캐시
    priceService.ts        현재가 배치 조회 + 종목별 캐시
    qlibExport.ts          Qlib CSV 관례로 저장
  trading/README.md         주문 실행 확장 지점 (미구현)
  server.ts / index.ts / cli.ts
scripts/setup.sh            대화형 .env 생성 + 토큰 발급 테스트
test/                       node:test 기반 단위 테스트 (Redis 불필요)
llms.txt                    AI 에이전트/검색용 요약 인덱스
```

## 테스트

```bash
npm test
```

Redis 서버 없이도 인메모리 어댑터로 토큰 캐싱/재발급 락, 캔들 페이지네이션·정렬, 현재가 캐싱, Qlib CSV 포맷을 검증한다.

## 한계 및 주의

- **투자 권유가 아니다.** 시세 조회 미들웨어일 뿐이며 투자 판단과 그 책임은 사용자에게 있다.
- 토스 Open API는 2026년 6월 기준 사전 신청 단계이며 정식 오픈일이 미정이다(`Toss/docs/Toss_OpenAPI_Guide.md` 참고). 엔드포인트 경로·응답 스키마가 바뀔 수 있어 전부 환경변수로 뺐다.
- 캔들 응답의 정확한 필드명(OHLC/거래량)은 공식 OpenAPI 스펙 원문을 직접 대조하지 못해 여러 후보 키를 모두 허용하는 방어적 파싱을 쓴다. 실제 응답을 받으면 `src/types.ts`의 `RawTossCandle`/`RawTossPrice`를 좁혀서 정리할 것을 권장한다.
- Rate limit 정확한 수치는 미확인 — 429 응답 발생 시 `Retry-After` 기준 backoff만 구현되어 있다.

---

**Qlib 원본 가이드**: [`../Qlib-getting-started-KR.md`](../Qlib-getting-started-KR.md) · **토스 Open API 참고 프로젝트**: [`Toss/`](../../../Toss) · MIT License
