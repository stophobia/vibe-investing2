# Changelog — 증권당 / AI Investor

본 변경 이력은 `docs/work-priority-and-prompts-v1.0-ko.md`의 우선순위
체크리스트와 1:1 매핑됩니다.

---

## [v1.1] — 2026-05-08

### Added — work-priority §2~§7 (P0+P1+P2)

**§2 P0 — Profile pre-warm cache** (`a22b192`)
- `services/user_profile_blob.py` — anon-keyed 5min in-process cache
  (별도 dict, slim {exists, has_birth_info, last_seen} 페이로드)
- `GET /api/profile/check?anon=<16-hex>` — 미니앱 콜드스타트용 lightweight probe
- `function_app.py:_warmup_miniapp_profile` — Telegram 웹훅 fire-and-forget warmup
- 미니앱 `localStorage` anon 캐시 + IIFE pre-warm probe
- 7 신규 단위 테스트 (cache hit/miss/evict/TTL)

**§3 P0 — Fortune onboarding 1무료 + 2잠금** (`344a4ae` + `4781f56`)
- `services/fortune_match.py` — 결정론적 `select_daily_free_stock()`
  (SHA-256 시드 → lucky_number 0~9 + 1 free + 2 locked)
- `services/fortune_service.py` — risk pool 로딩 + 만 19세 검증 + 멱등 unlock
- `data/risk_pools.json` — 3-tier 수기 큐레이션 (low 24 / medium 23 / high 22)
- 3 신규 엔드포인트:
  - `POST /api/profile/onboard` — 생년월일시 + 3 동의(만19세, 미국 비거주, 약관)
  - `GET /api/fortune/today` — 1 free + 2 locked (마스킹 ***)
  - `POST /api/fortune/unlock` — 100 P 차감 (멱등 same-day)
- 미니앱 홈 탭 상단 §FORTUNE 섹션 (날짜 입력 + 동의 체크박스 + 3 카드)
- 30 신규 단위 테스트

**§4 P0 — Generic ticker prediction** (`8999d88`)
- `services/prediction_repo.py` — `Prediction` dataclass + Blob repo
  (predictions/<anon[:2]>/<anon>/<id>.json)
- `services/prediction_settler.py` — settle (KST 16:00 cron) + expire (7일 cron)
- 2 신규 엔드포인트:
  - `POST /api/predictions/create` — 임의 ticker + up/down + 자동 next_trading_day
  - `GET /api/predictions/mine` — status 필터 + 50건 페이지
- 2 timer trigger:
  - `0 0 7 * * 1-5` (KST 16:00 평일) → settle pending predictions
  - `0 30 17 * * *` (KST 02:30 매일) → expire 7일 경과 pending
- 10 신규 단위 테스트 (next_trading_day weekend skip + Prediction.new factory)

**§5 P1 — Third-party click counter** (`fe0bf09`)
- `services/click_aggregator.py` — append-only NDJSON + 15분 aggregator
- `POST /api/predictions/{id}/click` — 인증 없음, viewer는 anon|IP hash
- 동일 viewer × prediction 30s rate-limit (in-memory dict, 5k cap)
- Timer `0 */15 * * * *` — 24h NDJSON 윈도우 → unique viewer 카운트 monotonic 갱신
- 7 신규 단위 테스트 (rate limit edges + log path 포맷)

**§6 P1 — Multi-axis ranking + rewards** (`fe0bf09`)
- `services/ranking_builder.py` — Wilson lower-bound (z=1.96)
  + build_prediction_ranking + build_referrer_ranking
- `services/ranking_rewards.py` — Top 1-10 P 적립 (daily/weekly/monthly)
  - prediction: 1=500/200/100, weekly 4×, monthly 20×
  - referrer: prediction × 2
  - 멱등: rankings/rewards_paid/<kind>/<period>/<KST>.json
- `GET /api/rankings/{predictions|referrers}?period=&anon=`
- Timer `0 0 18 * * *` (KST 03:00) — daily rebuild + payout
- 15 신규 단위 테스트 (Wilson 5 케이스, cutoff 3 period, reward 테이블 invariants)

**§7 P2 — Donation/Invite channels + reroll** (`7ef4484`)
- `unlock_via_donation` — `donation-intents/` 스캔 → confirmed 한 건이라도 있으면 자격
- `unlock_via_invite` — `invite_validated_count >= 1` 검증
- `reroll_fortune` — 10 P 차감
- `POST /api/fortune/reroll` 신규
- 6 신규 단위 테스트

### v1.1 final batch (다음 커밋) — §7 잔여 + §8 + Mini App UI
- §7 services/referrer_milestones.py — schedule/payout + 30d holding +
  donation_tier (none/supporter/patron/benefactor/champion)
- §7 donation_service.confirm_intent — donation_total_usdt 누적 + milestone
  자동 schedule
- §7 fortune_service.reroll_fortune — Supporter+ 1회/일 free
- §7 timer "0 0 19 * * *" (KST 04:00) — 30d 도래 milestone payout
- §7 user_profile schema +3 필드: donation_total_usdt, fortune_reroll_count_today,
  fortune_reroll_date_kst
- §8 docs/monitoring/v1.1.kql — 9 KQL 쿼리 (probe latency, settler runs,
  click aggregator, ranking rebuild, milestone payouts, etc.)
- §8 tests/integration/test_e2e_onboarding_to_ranking.py — 5건 E2E 경로 검증
- UI Predict 탭: 내 예측 (티커별) — pending/settled/no_data 필터 + 색상 카드 +
  click_count "👀 N명 조회" 표시
- UI Rank 탭: 리더보드 본격 — kind 토글 (예측/추천인) + period (일간/주간/월간) +
  내 순위 sticky bar + 🥇🥈🥉 메달
- UI Fortune 카드: 🎲 다시 뽑기 (10 P, Supporter+ 1회 무료) 버튼
- UI 클릭 트래킹: IntersectionObserver로 prediction-id가 보이면 자동
  POST /api/predictions/{id}/click

### 통계 (최종)
- 316 tests passing (+103 신규)
- 7 신규 service 모듈 + referrer_milestones 추가 = 8 모듈
- 13 신규 HTTP 엔드포인트 + 5 신규 timer trigger
- 5 신규 Blob 컨테이너 (predictions/, rankings/, logs/clicks/,
  donation-intents/, referrer-rewards/)

---

## [v1.0] — 이전 (Phase 1-4)

기존 README의 Phase 1-4 작업 히스토리 참조 — Saju 엔진, 매치업 예측,
USDT 도네이션, persona 캐싱 등.
