/**
 * 히스테리시스 N일 확인 상태머신 — 원본 quant/run.py _apply_hysteresis 1:1.
 * 새 raw 레짐이 confirm_days 연속 유지돼야 공식 committed 전환 (휩쏘 방지).
 * state 는 호출 간 영속화 대상(D1/R2). 이 함수는 state 를 변형하고 반환한다.
 */
import { HYSTERESIS } from "./config";

export interface HystState {
  committed: string | null;
  since: string | null;
  candidate: string | null;
  count: number;
}

export interface HystConfirm {
  raw: string;
  committed: string;
  pending: boolean;
  candidate: string | null;
  count: number;
  confirm_days: number;
  since: string | null;
}

export function freshState(): HystState {
  return { committed: null, since: null, candidate: null, count: 0 };
}

export function applyHysteresis(
  raw: string,
  state: HystState,
  today: string,
): { committed: string; confirm: HystConfirm; state: HystState } {
  const H = HYSTERESIS;
  let committed = state.committed;
  if (committed === null) {
    committed = raw;
    state.committed = committed;
    state.since = today;
    state.candidate = null;
    state.count = 0;
    return {
      committed,
      confirm: { raw, committed, pending: false, candidate: null, count: 0, confirm_days: H.confirm_days, since: today },
      state,
    };
  }
  let pending: boolean;
  if (raw === committed) {
    state.candidate = null;
    state.count = 0;
    pending = false;
  } else {
    if (raw === state.candidate) state.count = (state.count ?? 0) + 1;
    else {
      state.candidate = raw;
      state.count = 1;
    }
    if (state.count >= H.confirm_days) {
      committed = raw;
      state.committed = committed;
      state.since = today;
      state.candidate = null;
      state.count = 0;
      pending = false;
    } else {
      pending = true;
    }
  }
  return {
    committed,
    confirm: {
      raw,
      committed,
      pending,
      candidate: state.candidate,
      count: state.count ?? 0,
      confirm_days: H.confirm_days,
      since: state.since,
    },
    state,
  };
}
