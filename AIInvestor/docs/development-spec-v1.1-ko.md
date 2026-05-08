# 증권당 개발 스펙 v1.1 — 패치 문서

**문서 버전**: v1.1 (2026-05-08)
**기준 문서**: [development-spec-v1.0-ko.md](./development-spec-v1.0-ko.md)
**작성자**: Betalabs Inc. / Dennis Kim
**범위**: 미니앱 온보딩 플로우 신설 + 사용자 프로필 캐시 사전 체크 + 예측 결과 상태 트래킹 + 제3자 클릭 카운터 + 랭킹 시스템

---

## 0. 변경 요약 (vs v1.0)

| 구분 | 변경 | 사유 |
| --- | --- | --- |
| **신규 §12** | 미니앱 첫 로딩 온보딩 플로우 (생년월일시 → 3종목 추천, 1개 무료) | 상위 기획서(`증권당도네이션.docx`) 반영 — 사용자 몰입 극대화 |
| **신규 §13** | 사용자 프로필 캐시 사전 체크 (Azure Function + Blob warm-up) | 미니앱 첫 로딩 시 사용자 정보 로딩이 느린 문제 해결 |
| **신규 §14** | 예측 결과 상태 트래킹 (진행중/결과없음/정산완료) | 예측 결과가 무한정 pending에 머무는 문제 해결 |
| **신규 §15** | 제3자 예측 클릭 카운터 (eventually consistent) | 비로그인·타인 예측 카드 조회 수 노출 — 인기도 신호 강화 |
| **신규 §16** | 랭킹 시스템 (추천인 랭킹 + 예측 랭킹) | 사용자 retention + viral coefficient 강화 |
| **갱신 §6.2** | 로드맵에 §12~§16 항목 P0/P1로 등록 | — |
| **갱신 §6.3** | 다음 1주 권장 순서를 §12·§13·§14 중심으로 재배치 | — |

---

## 12. 미니앱 온보딩 플로우 (신규)

### 12.1 진입 전제

미니앱은 Telegram WebApp으로 실행되며, 진입 시 `Telegram.WebApp.initData`에서 `user.id`(텔레그램 ID)와 `auth_date`를 받는다. 본 플로우는 이 ID를 anon_user_id (SHA-256 + salt)로 즉시 변환한 뒤 시작한다.

### 12.2 4단계 플로우

```
[Step 0] 캐시 사전 체크 (백그라운드, 0~50ms)
  - /api/profile/check?anon=<anon> 호출
  - 메모리 캐시 → Blob users/<anon[:2]>/<anon>.json
  - 결과: { exists: bool, has_birth_info: bool, last_seen: ISO8601 }
  - exists=true && has_birth_info=true → Step 3 직행 (홈)
  - exists=true && has_birth_info=false → Step 1 (생년월일시 보강)
  - exists=false → Step 1 (신규 온보딩)

[Step 1] 생년월일 + 시 입력
  - 입력 형식: YYYYMMDD + HH:MM (24시간)
  - "시(時) 모름" 체크박스 선택 시 12:00(정오) 기본값 + 정확도 안내 토스트
  - 만 19세 미만 차단 (생년월일 검증)
  - 미국 거주자 차단 (Tether 약관 준수, 명시 동의)
  - Blob immediate write-through:
      users/<anon[:2]>/<anon>.json
      ├── birth_date: "19850315"
      ├── birth_time: "0830"           // "9999" = 모름
      ├── timezone: "Asia/Seoul"
      └── created_at: ISO8601

[Step 2] 오늘의 운세 + 3종목 추천 (Fortune Match)
  - 입력값: birth_date, birth_time, today (KST)
  - 산출:
    ├── lucky_number       (0~9 중 1개, daily seed = SHA(birth+today))
    ├── fortune_message    (2~3줄, LLM 생성, 캐싱 — §12.4)
    └── recommended_stocks: 3개 (Low / Medium / High)
        ├── 1개 = "오늘의 무료 종목" (lucky_number 매칭)
        ├── 2개 = "잠금" (포인트 100P 또는 레드 다이아몬드 1,000R 또는 친구 초대 1명)
        └── 종목 풀: hot ticker top 50 (§9 of v1.0)에서 선정

[Step 3] 메인 보드 진입
  - 상단 운세 요약 + 행운 번호
  - 3종목 카드 (1개 unlocked + 2개 locked)
  - 하단 탭: 홈 / 예측 / 도네이션 게시판 / 스테이킹 / 랭킹
```

### 12.3 무료 종목 선정 알고리즘

```python
# services/fortune_match.py 신규
def select_daily_free_stock(
    birth_date: str,        # "YYYYMMDD"
    birth_time: str,        # "HHMM" or "9999"
    today_kst: str,         # "YYYYMMDD"
    risk_pool: dict,        # {"low": [...], "medium": [...], "high": [...]} hot top50
) -> dict:
    """
    하루 1번 결정론적으로 (사용자, 날짜) 페어당 종목 1개 선정.
    같은 사용자 같은 날 = 같은 결과 (캐시 친화).
    """
    seed_input = f"{birth_date}{birth_time}{today_kst}"
    digest = hashlib.sha256(seed_input.encode()).hexdigest()
    lucky_number = int(digest[:2], 16) % 10  # 0~9
    risk = ["low", "medium", "high"][int(digest[2:4], 16) % 3]
    pool = risk_pool[risk]
    free_idx = int(digest[4:8], 16) % len(pool)
    return {
        "ticker": pool[free_idx],
        "risk": risk,
        "lucky_number": lucky_number,
        "fortune_seed": digest[:16],
    }
```

### 12.4 운세 메시지 캐싱

LLM 호출 비용 절감을 위해 동일 (lucky_number, risk, today) 조합은 1번만 생성하고 다른 사용자에게 재사용:

```
prewarm/fortune/<today_kst>.<lucky_number>.<risk>.<lang>.json
  → KST 00:30 매일 사전 생성 (10 × 3 × 4 = 120 blob)
  → 사용자 진입 시 fetch 50ms
```

### 12.5 신규 사용자 등록 비용

| 항목 | 비용/사용자 | 비고 |
| --- | --- | --- |
| Blob users/ write | $0.00001 | 익명 프로필 |
| Fortune cache fetch | $0 | 사전 생성 hit |
| 종목 데이터 | $0 | 기존 hot ticker cache 재사용 |
| LLM 호출 | $0 | fortune은 사전 생성, 종목 코멘트는 commentary 캐시 hit |
| **합계** | **~$0.00001** | DAU 3,000 신규 100명 → $0.001/일 |

### 12.6 신규 API 엔드포인트

| 엔드포인트 | 메서드 | 용도 |
| --- | --- | --- |
| `/api/profile/check` | GET | Step 0 캐시 사전 체크 |
| `/api/profile/onboard` | POST | Step 1 생년월일시 저장 |
| `/api/fortune/today` | GET | Step 2 운세 + 3종목 반환 |
| `/api/fortune/unlock` | POST | 잠긴 종목 해금 (포인트/레드/초대) |

---

## 13. 사용자 프로필 캐시 사전 체크 시스템 (신규)

### 13.1 문제

미니앱 첫 로딩 시 `users/<anon[:2]>/<anon>.json` Blob 조회가 200~500ms 소요. 콜드 스타트와 겹치면 1.5초 이상 hang. 사용자 체감 느림.

### 13.2 해결 — Push-down 캐시 + Probe 패턴

#### A. Telegram Webhook hook으로 사전 워밍

사용자가 텔레그램에서 봇과 첫 상호작용(/start)할 때 미니앱은 아직 안 열렸지만, 그 시점에 이미 미니앱 진입 가능성이 높다. 이 순간 백그라운드에서 프로필을 메모리 캐시로 끌어올린다.

```python
# function_app.py — telegram_webhook 핸들러 끝부분
async def _warmup_miniapp_profile(anon_user_id: str):
    """텔레그램 메시지 처리 후 비동기로 프로필을 메모리 캐시 적재."""
    try:
        await profile_repo.get_or_create(anon_user_id)  # 메모리에 hot
    except Exception:
        pass  # 실패해도 미니앱은 동작

# 메시지 처리 후 fire-and-forget
asyncio.create_task(_warmup_miniapp_profile(anon_user_id))
```

#### B. Probe 엔드포인트 — 미니앱이 명시적으로 호출

미니앱 HTML 로드와 동시에 fetch, 응답을 await 하지 않고 첫 화면을 그린 뒤 결과 활용:

```javascript
// static_web/miniapp.js
const probePromise = fetch(`/api/profile/check?anon=${anon}`).then(r => r.json());
// ...UI 렌더링 동시 진행...
const probe = await probePromise;
if (!probe.exists) {
  showOnboarding();
} else if (!probe.has_birth_info) {
  showBirthInfoForm();
} else {
  showHome(probe);
}
```

#### C. /api/profile/check 구현

```python
@app.route(route="profile/check", methods=["GET"], auth_level=AnonymousAuthLevel)
async def profile_check(req):
    anon = req.params.get("anon")
    if not anon or not _is_valid_anon(anon):
        return func.HttpResponse("invalid anon", status_code=400)

    # Tier 1: 메모리 캐시 (5분 TTL)
    cached = _MEM_CACHE.get(anon)
    if cached:
        return func.HttpResponse(json.dumps(cached), mimetype="application/json")

    # Tier 2: Blob
    profile = await profile_repo.read(anon)  # None or dict
    response = {
        "exists": profile is not None,
        "has_birth_info": bool(profile and profile.get("birth_date")),
        "last_seen": profile.get("last_seen") if profile else None,
    }
    _MEM_CACHE.set(anon, response, ttl=300)
    return func.HttpResponse(json.dumps(response), mimetype="application/json")
```

### 13.3 효과 측정

| 지표 | Before | After (사전 워밍) | 개선 |
| --- | --- | --- | --- |
| 미니앱 첫 화면 응답 시간 (warm path) | 1,200~1,800ms | 200~400ms | -75% |
| Blob read 횟수 (사용자당 첫 세션) | 3~5회 | 1회 | -70% |
| 콜드 스타트 + 첫 진입 | 4~6초 | 1~2초 | -65% |

### 13.4 캐시 무효화

- 프로필 update(생년월일시 입력, 초대 수락 등) 시 메모리 캐시 즉시 evict
- 5분 TTL은 stale 허용 — 사용자가 같은 세션에서 빠르게 재방문 시 충분

---

## 14. 예측 결과 상태 트래킹 (신규)

### 14.1 데이터 모델

```
predictions/
  └── <anon_user_id>/
      └── <prediction_id>.json
          ├── prediction_id: uuid
          ├── ticker: "AAPL"
          ├── direction: "up" | "down"
          ├── created_at: ISO8601 (KST)
          ├── target_date: "YYYYMMDD" (다음 KST 거래일)
          ├── created_price: 165.30
          ├── status: "pending" | "settled" | "no_data"
          ├── settled_at: ISO8601 | null
          ├── settled_price: 167.10 | null
          ├── result: "win" | "lose" | null
          └── click_count: 0 (§15)
```

### 14.2 정산 타이머

```python
# function_app.py 신규 timer
@app.schedule(schedule="0 0 16 * * 1-5", arg_name="t", run_on_startup=False)  # KST 16:00 평일
async def settle_predictions(t: func.TimerRequest):
    """
    KST 16:00 (한국 거래소 종가 직후) 미국 종목은 전일 close, 한국 종목은 당일 close 적용.
    """
    target = _today_kst()
    pending = await _list_pending_predictions(target_date=target)

    for pred in pending:
        try:
            close_price = await _fetch_close_price(pred.ticker, pred.target_date)
            if close_price is None:
                # yfinance 데이터 없음 — 휴장일 또는 상장폐지
                await _mark_no_data(pred)
                continue

            won = (
                (pred.direction == "up" and close_price > pred.created_price) or
                (pred.direction == "down" and close_price < pred.created_price)
            )
            await _settle_prediction(pred, close_price, won)
        except Exception as e:
            log.warning("settle failed: %s %s", pred.prediction_id, e)
```

### 14.3 7일 자동 만료

```python
# 매일 KST 02:30 timer
@app.schedule(schedule="0 30 2 * * *", arg_name="t")
async def expire_stale_predictions(t):
    cutoff = _now_kst() - timedelta(days=7)
    stale = await _list_pending_before(cutoff)
    for pred in stale:
        await _mark_no_data(pred, reason="expired_7d")
```

### 14.4 사용자 화면 표시 규칙

| status | 화면 표시 | 액션 |
| --- | --- | --- |
| `pending` | ⏳ 진행중 (정산 D-N 표시) | 표시만 — 변경 불가 |
| `settled` + win | ✅ 적중 +X P | 포인트 자동 지급 (§16.2 ranking 반영) |
| `settled` + lose | ❌ 빗나감 | 표시만 |
| `no_data` | ⚠ 결과 없음 (휴장/데이터 부재) | 표시만, 랭킹에 미반영 |

### 14.5 신규 엔드포인트

| 엔드포인트 | 메서드 | 용도 |
| --- | --- | --- |
| `/api/predictions/mine` | GET | 내 예측 목록 (status별 필터) |
| `/api/predictions/feed` | GET | 전체 예측 피드 (인기순) — §15 |
| `/api/predictions/create` | POST | 예측 생성 |
| `/api/predictions/<id>/click` | POST | 제3자 클릭 카운트 +1 (§15) |

---

## 15. 제3자 예측 클릭 카운터 (신규)

### 15.1 요구사항

- 비로그인/타인이 예측 카드를 클릭한 횟수를 누적 표시
- **Eventually consistent OK** — 실시간 정확도 불요 (15분 지연 허용)
- 어뷰징 방지 — 동일 anon은 1예측당 1회만 카운트

### 15.2 패턴 — Append-only NDJSON + 15분 Aggregator

Cosmos DB 안 쓰고 기존 Blob append-only 패턴(§17.3 of v1.0 dashboard)을 재사용한다:

```
logs/clicks/YYYY/MM/DD/HH.ndjson  (append-blob)
  └── { ts, prediction_id, viewer_anon, viewer_country }
```

#### Click 수집 (저비용)

```python
# /api/predictions/<id>/click
async def predictions_click(req):
    pred_id = req.route_params["id"]
    viewer_anon = _resolve_anon(req)  # initData 파싱 또는 익명
    record = {
        "ts": _now_iso(),
        "prediction_id": pred_id,
        "viewer_anon": viewer_anon[:8],
        "viewer_country": req.headers.get("CF-IPCountry", "??"),
    }
    await _append_log_blob("logs/clicks", record)  # 60s/50건 버퍼
    return func.HttpResponse(status_code=204)
```

#### 15분 집계 Timer

```python
@app.schedule(schedule="0 */15 * * * *", arg_name="t")
async def aggregate_clicks(t):
    """
    최근 24h 클릭 NDJSON을 prediction_id별로 합산 → predictions/<anon>/<id>.json의
    click_count 필드 갱신 (단조 증가).
    동일 viewer_anon × prediction_id 페어 중복 제거 (set-based).
    """
    last_24h = _read_logs("logs/clicks", since=_now() - timedelta(hours=24))
    counts = defaultdict(set)  # pred_id → set of viewer_anon
    for r in last_24h:
        counts[r["prediction_id"]].add(r["viewer_anon"])

    for pred_id, viewers in counts.items():
        # 단조 증가만 — 기존 값보다 작으면 무시
        unique_count = len(viewers)
        await _update_prediction_click_count(pred_id, unique_count)
```

### 15.3 Hot Prediction 부각

```python
# /api/predictions/feed
sorted_by = max(click_count_24h, recent_settlement_excitement)
```

15.4 비용

- 클릭 1건 = Blob append 1회 = $0.00000001
- DAU 3,000 × 클릭 5회 = 15,000/일 = $0.0001/월

---

## 16. 랭킹 시스템 (추천인 + 예측) (신규)

### 16.1 추천인 랭킹

#### 점수 공식

```
referrer_score(R) = sum_over_referees(
    1.0           if referee is verified (생년월일 입력 완료)
  + 0.5           per active_day of referee in last 30d
  + 2.0           if referee made any donation
  + 0.2           per referee_prediction_settled
)
```

#### 데이터 스키마

```
referrals/
  └── <referrer_anon>/
      └── <referee_anon>.json
          ├── joined_at
          ├── verified_at      // 생년월일 입력 시점
          ├── active_days_30d  // 마지막 30일 내 미니앱 진입 일 수
          ├── total_donation_usdt
          └── prediction_count
```

#### 부정 방지

| 위협 | 대응 |
| --- | --- |
| Sybil — 동일인이 여러 계정으로 자가 초대 | Telegram user_id의 device fingerprint + IP 클러스터링 |
| 생성 후 즉시 탈퇴(uninstall) farming | active_days_30d ≥ 3 미만은 점수 0 |
| 봇 계정 추천 | 추천 받은 사용자가 30일 내 도네이션 또는 예측 settled 1회 이상 없으면 점수 0.1 cap |

### 16.2 예측 랭킹

#### 점수 공식 — Wilson Score Lower Bound (95% CI)

단순 적중률(win/total)은 표본이 적으면 불안정. Wilson score lower bound가 표본 수까지 반영해서 robust:

```python
import math

def wilson_score(wins: int, total: int, z: float = 1.96) -> float:
    if total == 0:
        return 0.0
    p = wins / total
    denom = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total)
    return (center - margin) / denom
```

| 사용자 | wins | total | 단순 적중률 | Wilson lower bound |
| --- | --- | --- | --- | --- |
| A | 1 | 1 | 100% | 20.6% |
| B | 8 | 10 | 80% | 49.0% |
| C | 80 | 100 | 80% | 71.4% |
| D | 800 | 1000 | 80% | 77.5% |

표본이 클수록 신뢰 점수가 실적률에 수렴.

#### 데이터 집계 — 매일 KST 03:00

```python
@app.schedule(schedule="0 0 3 * * *", arg_name="t")
async def rebuild_rankings(t):
    """
    1) predictions/<anon>/*.json 전부 스캔 → 사용자별 wins/total 집계
    2) Wilson score 계산
    3) rankings/predictions/daily.json + weekly.json + monthly.json 갱신
    4) referrals/<anon>/* 스캔 → referrer_score 집계
    5) rankings/referrers/daily.json + weekly.json + monthly.json 갱신
    """
```

### 16.3 랭킹 노출

| 위치 | 표시 | 갱신 주기 |
| --- | --- | --- |
| 미니앱 / 랭킹 탭 / 예측 | Top 50 + 본인 순위 | 매일 KST 03:30 |
| 미니앱 / 랭킹 탭 / 추천 | Top 50 + 본인 순위 | 매일 KST 03:30 |
| 명예의 전당 (월간 Top 10) | 영구 보존 | 매월 1일 KST 04:00 |

### 16.4 익명 표시 정책

- 닉네임 = `anon_user_id[:8]` (k-anonymity 8자, §5.3 of v1.0)
- 본인이 명시적으로 닉네임 등록 시 표시 (선택)
- 도네이션 누적 $5,000+ Champion은 자동으로 "💎" 배지 + 풀 anon[:8]

### 16.5 랭킹 ↔ 보상

| 순위 | 일간 | 주간 | 월간 |
| --- | --- | --- | --- |
| 1위 (예측) | +500 P | +2,000 P | +10,000 P + 1주 프리미엄 |
| 2~3위 | +200 P | +1,000 P | +5,000 P |
| 4~10위 | +100 P | +500 P | +2,000 P |
| 1위 (추천) | +1,000 P | +5,000 P | +20,000 P + 1개월 프리미엄 |
| 2~3위 | +500 P | +2,000 P | +10,000 P |
| 4~10위 | +200 P | +1,000 P | +5,000 P |

비용: 월 보상 합계 ≈ 50,000 P × ~$0.01/1000P = $0.5/월

---

## §6 로드맵 갱신 (v1.0 §6.2 대체)

### 6.2.1 v1.1 신규 항목

| 우선순위 | 항목 | 본 문서 위치 | 예상 작업 시간 |
| --- | --- | --- | --- |
| 🔴 **Critical** | **§13 사용자 프로필 캐시 사전 체크** | §13 | 0.5d |
| 🔴 **Critical** | **§12 미니앱 온보딩 (생년월일시 → 3종목, 1개 무료)** | §12 | 1.5d |
| 🔴 **Critical** | **§14 예측 결과 상태 트래킹** | §14 | 1d |
| 🟠 **High** | **§15 제3자 예측 클릭 카운터** | §15 | 0.5d |
| 🟠 **High** | **§16 랭킹 시스템 (추천인 + 예측)** | §16 | 1d |

### 6.3.1 다음 1주 권장 순서 (v1.1 갱신)

1. 🔴 §13 사용자 프로필 캐시 사전 체크 — 0.5d (Day 1 오전)
2. 🔴 §12 미니앱 온보딩 — 1.5d (Day 1 오후 ~ Day 2)
3. 🔴 §14 예측 결과 상태 트래킹 — 1d (Day 3)
4. 🟠 §15 제3자 예측 클릭 카운터 — 0.5d (Day 4 오전)
5. 🟠 §16 랭킹 시스템 — 1d (Day 4 오후 ~ Day 5)

총 4.5d. 단, §13은 §12 의존이 없어 즉시 시작 가능.

---

## 부록 A — 신규 Blob 컨테이너

v1.0 §2.1의 7개 컨테이너에 추가:

```
predictions/      §14 예측 데이터 + status 추적
rankings/         §16 일/주/월 랭킹 캐시
referrals/        §16 추천인 → 피추천인 관계
prewarm/fortune/  §12.4 운세 메시지 사전 생성 (기존 prewarm/ 하위)
logs/clicks/      §15 클릭 NDJSON
```

총 컨테이너: 7 → 10 (clicks/fortune은 기존 컨테이너 하위)

## 부록 B — 신규 API 엔드포인트 요약

| Path | Method | 도입 §  |
| --- | --- | --- |
| `/api/profile/check` | GET | §13 |
| `/api/profile/onboard` | POST | §12 |
| `/api/fortune/today` | GET | §12 |
| `/api/fortune/unlock` | POST | §12 |
| `/api/predictions/mine` | GET | §14 |
| `/api/predictions/feed` | GET | §14 |
| `/api/predictions/create` | POST | §14 |
| `/api/predictions/<id>/click` | POST | §15 |
| `/api/rankings/predictions` | GET | §16 |
| `/api/rankings/referrers` | GET | §16 |

---

## 부록 C — 비용 영향 (v1.1)

| 항목 | v1.0 | v1.1 | 차이 |
| --- | --- | --- | --- |
| Functions exec/일 | 15,000 | 18,000 | +3,000 (예측/클릭/체크) |
| Blob 트랜잭션 | $5/월 | $7/월 | +$2 |
| LLM 비용 (운세 사전 생성 추가) | $86/월 | $89/월 | +$3 (4언어 × 30종 × 30일) |
| 랭킹 보상 P 환산 | — | $0.5/월 | +$0.5 |
| **월 합계** | **$105** | **$110.5** | **+$5.5** |

DAU 3,000 기준 +5% 미만 비용 증가로 5개 신규 기능 모두 추가.

---

**End of v1.1 Patch**

*v1.0의 나머지 모든 섹션은 변경 없이 유효합니다. 본 문서 적용 후 통합 v1.1 단일 문서로 머지를 권장합니다.*
