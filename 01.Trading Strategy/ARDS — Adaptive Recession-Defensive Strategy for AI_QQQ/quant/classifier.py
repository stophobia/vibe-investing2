# -*- coding: utf-8 -*-
"""
ARDS-X — Regime Classifier (핵심 의사결정 엔진)
===============================================
2-축 레짐 맵으로 현재 국면을 분류한다.

  X축 = 거시 침체 축 (Macro)   : 5-Factor Recession Composite (실데이터)  0~100
  Y축 = 가격 구조 축 (Price)    : 드로다운 깊이 + 추세 붕괴 정도            0~100
  오버레이 = 단기 과매도 (Oversold) : RSI / Bollinger / ATR 이탈           0~100

판정 우선순위 (위에서 아래로):

  1. RECESSION_REBALANCE (침체 리밸런싱)
       거시 ≥ 55 AND (지수 드로다운 ≤ -5% OR 추세 붕괴)
       → 단순 조정이 아니라 매크로가 주도하는 하락. ARDS/ARDS-Defense 방어 전환.

  2. DOWNTREND_DISTRIBUTION (하락 / 분배)
       추세 붕괴(200일선 이탈·데드크로스·폭 약화) AND 드로다운 ≤ -12%, 거시는 아직 침체 아님
       → '조정'이 아니라 구조적 하락 추세. 저점매수 금지, 리스크 축소.

  3. OVERSOLD_BOUNCE (단기 과매도 → 기술적 반등 후보)
       과매도 점수 높음 AND 추세 대체로 유지 → 전술적 반등 트레이드 영역(AMQS DIP_BUY).

  4. CORRECTION (조정)
       드로다운 -5%~-12%, 추세 유지, 거시 양호 → 상승추세 내 건강한 눌림.

  5. UPTREND_HEALTHY (정상 상승)
       드로다운 < -5%, 200일선 위, 거시 양호.
"""

import config


def _pick_index(rows_by_ticker, ticker):
    return rows_by_ticker.get(ticker)


def classify(macro, index_rows, complex_rows, complex_agg):
    D = config.DECISION
    T = config.TECH
    M = macro["composite"]

    by_t = {r["ticker"]: r for r in index_rows}
    gspc = _pick_index(by_t, "^GSPC")
    ndx = _pick_index(by_t, "^NDX")
    idx_list = [r for r in (gspc, ndx) if r]

    # --- 대표 가격 지표 -----------------------------------------------------
    # 테이프 드로다운: 두 지수 중 더 깊은 쪽 (보수적)
    tape_dd = min([r["dd_from_high"] for r in idx_list]) if idx_list else 0.0
    # 나스닥100 을 테크 테이프 대표로
    tech_ref = ndx or gspc
    breadth = complex_agg.get("breadth_above_200dma", 100.0)
    complex_dd = complex_agg.get("avg_dd_from_high", 0.0)

    # 추세 붕괴 여부 (지수 또는 복합체 기준)
    idx_below_200 = any(not r["above_200dma"] for r in idx_list)
    idx_deadcross = any(not r["golden_cross"] for r in idx_list)
    breadth_weak = breadth < T["breadth_weak"]
    trend_broken = (idx_below_200 or idx_deadcross or breadth_weak)

    # 구조적 하락 점수 / 과매도 점수
    decline_score = max(
        complex_agg.get("avg_decline_score", 0.0),
        tech_ref["decline_score"] if tech_ref else 0.0,
    )
    oversold_score = max(
        complex_agg.get("avg_oversold_score", 0.0),
        tech_ref["oversold_score"] if tech_ref else 0.0,
    )
    idx_rsi = min([r["rsi14"] for r in idx_list]) if idx_list else 50.0

    # --- Y축(가격 스트레스) 0~100 합성 ------------------------------------
    price_stress = round(min(100.0, 0.6 * decline_score + 0.4 * min(100, -tape_dd / T["dd_bear"] * 100)), 1)

    # --- 분류 우선순위 -----------------------------------------------------
    is_oversold = (oversold_score >= 55) or (idx_rsi < T["rsi_oversold"])

    if M >= D["macro_recession"] and (tape_dd <= -T["dd_correction"] or trend_broken):
        state, kr, action = "RECESSION_REBALANCE", "자산 리밸런싱 (침체)", "DEFENSIVE_ARDS"
    elif trend_broken and tape_dd <= -T["dd_deep"]:
        state, kr, action = "DOWNTREND_DISTRIBUTION", "하락 / 분배", "REDUCE"
    elif tape_dd <= -T["dd_correction"]:
        if is_oversold:
            state, kr, action = "OVERSOLD_BOUNCE", "단기 과매도 (반등 후보)", "BUY_DIP_TACTICAL"
        else:
            state, kr, action = "CORRECTION", "조정", "HOLD_ACCUMULATE"
    elif is_oversold:
        state, kr, action = "OVERSOLD_BOUNCE", "단기 과매도 (반등 후보)", "BUY_DIP_TACTICAL"
    else:
        state, kr, action = "UPTREND_HEALTHY", "정상 상승추세", "RISK_ON"

    # --- 신뢰도: 거시축과 가격축의 합치도 + 신호 극단성 ---------------------
    macro_high = M >= D["macro_recession"]
    price_high = price_stress >= 50
    agree = (macro_high == price_high)
    confidence = 55
    confidence += 18 if agree else -5
    confidence += min(15, abs(M - 50) / 50 * 15)
    confidence += min(12, abs(price_stress - 40) / 60 * 12)
    if macro["n_missing"] >= 2:
        confidence -= 12          # 데이터 결측 시 신뢰도 하향
    confidence = int(max(20, min(95, confidence)))

    # --- 헤드라인 & 핸드오프 ----------------------------------------------
    headline, handoff = _narrative(state, M, macro, tape_dd, breadth, complex_dd,
                                   idx_rsi, oversold_score, trend_broken)

    return {
        "state": state,
        "state_kr": kr,
        "action": action,
        "confidence": confidence,
        "headline": headline,
        "handoff": handoff,
        "axes": {
            "macro": M,
            "macro_phase": macro["phase"],
            "macro_phase_kr": macro["phase_kr"],
            "price_stress": price_stress,
            "decline_score": round(decline_score, 1),
            "oversold_score": round(oversold_score, 1),
        },
        "evidence": {
            "tape_drawdown": round(tape_dd, 1),
            "complex_avg_drawdown": round(complex_dd, 1),
            "breadth_above_200dma": breadth,
            "index_min_rsi14": round(idx_rsi, 1),
            "trend_broken": trend_broken,
            "idx_below_200dma": idx_below_200,
            "idx_deadcross": idx_deadcross,
            "breadth_weak": breadth_weak,
            "is_oversold": is_oversold,
        },
    }


def _narrative(state, M, macro, tape_dd, breadth, complex_dd, idx_rsi, oversold, trend_broken):
    p = macro["phase_kr"]
    if state == "RECESSION_REBALANCE":
        h = (f"거시 침체 신호(Composite {M:.0f}, {p})가 가격 하락을 주도. "
             f"지수 고점 대비 {tape_dd:.1f}%, 200일선 위 종목 {breadth:.0f}%. "
             f"단순 조정이 아니라 **자산 리밸런싱(침체) 국면**.")
        ho = ("➡️ ARDS / ARDS-Defense 방어 포트폴리오로 전환 권고 "
              "(Tier 1 방어섹터 · Tier 2 국채/금 · Tier 4 헤지 활성화). "
              "저점매수보다 자본보존 우선.")
    elif state == "DOWNTREND_DISTRIBUTION":
        h = (f"추세가 깨졌다(200일선 이탈/데드크로스/폭 약화) + 고점 대비 {tape_dd:.1f}%. "
             f"거시(Composite {M:.0f})는 아직 침체 임계 미만이나, **구조적 하락/분배**로 분류.")
        ho = ("➡️ '조정'으로 보지 말 것. 신규 저점매수 보류, 리스크 축소·헤지. "
              "거시 Composite 가 55 를 넘으면 침체 리밸런싱으로 격상.")
    elif state == "OVERSOLD_BOUNCE":
        h = (f"단기 과매도(과매도 점수 {oversold:.0f}, 지수 RSI {idx_rsi:.0f}). "
             f"고점 대비 {tape_dd:.1f}%이나 추세는 대체로 유지 → **기술적 반등 후보**.")
        ho = ("➡️ AMQS DIP_BUY 영역. 전술적·소규모 분할매수 + 타이트한 손절. "
              "추세 붕괴 신호가 추가되면 즉시 하락 모드로 재분류.")
    elif state == "CORRECTION":
        h = (f"상승추세 내 건강한 눌림(고점 대비 {tape_dd:.1f}%, 200일선 위 {breadth:.0f}%). "
             f"거시(Composite {M:.0f}) 양호 → **조정**.")
        ho = ("➡️ 보유 유지 + 우량 빅테크/AI 인프라 분할매수. "
              "RSI 과매도 진입 시 OVERSOLD_BOUNCE 로 전환되어 매수 강도↑.")
    else:  # UPTREND_HEALTHY
        h = (f"정상 상승추세(고점 대비 {tape_dd:.1f}%, 200일선 위 {breadth:.0f}%, "
             f"거시 Composite {M:.0f}/{p}). 하락·침체 신호 없음.")
        ho = "➡️ 리스크온 유지. AMQS 모멘텀 전략 비중 정상."
    return h, ho
