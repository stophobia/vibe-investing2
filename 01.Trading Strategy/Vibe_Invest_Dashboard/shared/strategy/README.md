# shared/strategy — 시그널 엔진 (TS 포팅)

룰 기반 시그널 엔진을 원본 Python 에서 TS 로 충실 포팅. **상수·룰 변경 금지**(원본이 최종 권위),
모든 포팅은 **Python 결과 골든 fixture 와 대조 검증**한다(가이드 §6.3 step 6).

## 파일
| 파일 | 내용 | 원본 |
|---|---|---|
| `types.ts` | 데이터 인터페이스(PriceSeries, DataProvider), 시그널 enum | — |
| `series.ts` | 수치 primitive (std ddof·ewm adjust=False·pct_change·cummax·pyRound …) | pandas/numpy 시맨틱 |
| `amqs.ts` | **AMQS-AI-Infra** 엔진 (4팩터 z·5차원 100점·레짐·Top-N·사이징) | `…/AMQS for AI Infra/script/strategy.py` |
| `ards/` | **ARDS-X** 엔진 (config·technical·macro·rates·classifier·hysteresis·index) | `…/ARDS … for AI_QQQ/quant/*.py` |

## 검증 상태
- ✅ **AMQS** — `test/strategy/amqs.test.ts` 가 20종목 골든(지표·점수·시그널·가중치·레짐) 전수 대조. 일치.
- ✅ **ARDS** — `test/strategy/ards.test.ts` 가 macro(5팩터)·rate(4성분)·기술지표(20종목)·measure·분류·
  verdict(한국어 narrative 포함)·히스테리시스 시퀀스 전수 대조. 일치.
  히스테리시스 상태(`HystState`)는 호출 간 영속화 대상 → Cron Worker 가 D1/R2 에 저장(다음 단계 #9).
- ⏸ MU_Hynix — 1차 제외(Phase 2).

## 골든 fixture 재생성
```bash
python3 test/fixtures/gen_amqs_fixture.py   # numpy/pandas 필요. amqs_golden.json 갱신
python3 test/fixtures/gen_ards_fixture.py   # ards_golden.json 갱신
npx vitest run test/strategy
```
> 결정적 입력(seed 42) + 입력 배열을 fixture 에 함께 저장 → TS 가 동일 배열로 실행해 대조.
> 부동소수 합산 순서차 흡수 위해 tol = 1e-6 + 1e-6·|x|.

## 사용 (예: Cron Worker)
```ts
import { runAmqs, AI_INFRA_TICKERS } from "shared/strategy/amqs";
const { regime, metrics } = runAmqs(inputs, { qqqCloses, vixCloses, marketCaps });
// metrics[i].signal(CENTER/SATELLITE/…) → toDashboardSignal() → D1 signals
```
