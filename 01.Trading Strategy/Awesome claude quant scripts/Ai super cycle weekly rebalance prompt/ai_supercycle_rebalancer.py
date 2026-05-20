#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Super Cycle — Weekly Dynamic Rebalancer
==========================================

AI Super Cycle Prompt (kr/en/cn) 의 자매(sister) 실행 엔진.

역할 분담
---------
- "AI Super Cycle Prompt"      : 어떤 종목을 어느 Layer 에 넣을지 (분류·점수화)
- "ai_supercycle_rebalancer"   : 그 Layer 들을 매주 어떻게 사고팔지 (위상 라벨링 + 동적 비중)

핵심 로직
---------
1) 위상 라벨링 (PhaseLabeler)
   - capex 2차미분(가속/감속) + HBM 리드타임/현물가 + NVDA 매출 QoQ·재고
   - 결과: ACCEL(가속·저점) / NEUTRAL(중립) / PEAK(정점) / DOWN(하강)

2) NVDA 동적 목표 비중 (NVDA 주기 + HBM 주기로 밴드 내에서 연속 조절)
   - 밴드: 저점/가속 40%  ~  정점 25%  ~  '시장 안 좋을 때(STRESS)' 35% 강제 캡
   - HBM 사이클이 식을수록(리드타임↓, 현물가↓) NVDA 비중을 추가로 끌어내림

3) 정점·하강 → 축소분을 L2(MSFT,GOOGL) → L3(전력/냉각/네트워크) 로 분산 (규칙 C)

4) 하강·바닥 + 급락(-30/-45%) → 단계적 매수 (규칙 B)
   - 단, capex 명백한 감소 초입에는 발동 보류 (떨어지는 칼날 방지)

5) STRESS(시장 악화) 시 → NVDA 35% 캡 + 현금성 자산(CASH) 비중 상향

면책: 본 코드는 정보·연구 목적의 시뮬레이션이며 투자 자문이 아닙니다.
실제 매매 결정과 책임은 사용자 본인에게 있습니다.

저자 매핑: vibe-investing / Awesome Claude Quant Scripts 시리즈 자매 파일
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
import json


# ---------------------------------------------------------------------------
# 0. 자산 / Layer 정의
# ---------------------------------------------------------------------------

class Layer(str, Enum):
    L1 = "L1_Foundation"        # 반도체·HBM·스토리지 (선행·정점, 변동성 최상)
    L2 = "L2_Infrastructure"    # 하이퍼스케일러 (중간·구조적)
    L3 = "L3_Enablers"          # 전력·냉각·네트워크 (구조적 우상향, 평탄화)
    L4 = "L4_Application"        # 애플리케이션 (후행) — 여기선 지수(QQQ)로 대체
    CASH = "Cash"               # 현금성 자산 (MMF/단기채/SGOV류)


class Phase(str, Enum):
    ACCEL = "ACCEL"     # 가속 · 저점 탈출
    NEUTRAL = "NEUTRAL" # 중립
    PEAK = "PEAK"       # 정점
    DOWN = "DOWN"       # 하강 (바닥 다지기 포함)


# 보유/후보 종목 → Layer 매핑 (사용자 포트폴리오 + 신규 편입)
TICKER_LAYER: Dict[str, Layer] = {
    "NVDA": Layer.L1,   # GPU — 사이클의 심장
    "SNDK": Layer.L1,   # 샌디스크 (NAND/스토리지)
    "INTC": Layer.L1,   # 인텔 (사이클·정책주)
    "MSFT": Layer.L2,   # 신규 편입 — Azure AI 현금흐름
    "GOOGL": Layer.L2,  # 신규 편입 — GCP+TPU (TPU 리스크 자연 헤지)
    "QQQ":  Layer.L4,   # 나스닥100 — L4 애플리케이션 간접 노출
    "VRT":  Layer.L3,   # (선택) 전력·냉각 — 규칙 C 분산처 예시
    "CASH": Layer.CASH, # 현금성 자산
}


# ---------------------------------------------------------------------------
# 1. 주간 입력 데이터 컨테이너
# ---------------------------------------------------------------------------

@dataclass
class WeeklySignals:
    """매주 사람이 채워넣거나 데이터 파이프라인이 채우는 관측치."""
    # --- capex 신호 (빅4 합산 가이던스) ---
    capex_yoy_growth: float          # 올해 합산 capex YoY 성장률 (%) 예: 67.0
    capex_yoy_growth_prev: float     # 직전 관측치 (2차미분 계산용)

    # --- HBM 사이클 신호 ---
    hbm_leadtime_weeks: float        # HBM 리드타임(주). 길수록 타이트(=강세)
    hbm_leadtime_prev: float         # 직전 관측치
    hbm_spot_mom: float              # HBM 현물가 MoM 변화율(%). +면 강세

    # --- NVDA 자체 신호 ---
    nvda_dc_qoq: float               # NVDA 데이터센터 매출 QoQ(%) 예: 22.0
    nvda_dc_qoq_prev: float          # 직전 분기 QoQ(%)
    nvda_inventory_mom: float        # 채널/자체 재고 MoM(%). +면 재고 증가(정점 경고)
    nvda_gpu_asp_qoq: float          # GPU ASP QoQ(%). -5% 이하면 정점 신호

    # --- 시장/거시 스트레스 ---
    market_stress: bool              # 시장 악화(조정/약세장) 여부
    fed_hiking: bool                 # 연준 금리 인상 전환 여부

    # --- 가격(급락 매수 규칙용) ---
    nvda_drawdown_from_high: float   # NVDA 고점대비 낙폭(%) 예: -32.0
    hbm_proxy_drawdown: float        # 메모리 대표(예: 마이크론) 고점대비 낙폭(%)

    # --- 현재 보유 비중 (합계 100 기준, %) ---
    current_weights: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 2. 위상 라벨러
# ---------------------------------------------------------------------------

class PhaseLabeler:
    """capex 2차미분 + HBM + NVDA 신호를 점수화해 4위상으로 라벨링."""

    def label(self, s: WeeklySignals) -> (Phase, Dict[str, float]):
        score = 0.0
        detail = {}

        # (a) capex 2차미분: 성장률이 가속하면 +, 감속하면 -
        capex_accel = s.capex_yoy_growth - s.capex_yoy_growth_prev
        c = self._clip(capex_accel / 10.0, -1, 1)   # 10%p 변화당 만점
        detail["capex_2nd_deriv"] = round(c, 3)
        score += 1.4 * c   # 가장 신뢰도 높은 선행지표 → 가중치 최대

        # (b) HBM 리드타임 추세 + 현물가
        hbm_lead = self._clip((s.hbm_leadtime_weeks - s.hbm_leadtime_prev) / 4.0, -1, 1)
        hbm_spot = self._clip(s.hbm_spot_mom / 10.0, -1, 1)
        hbm = 0.6 * hbm_lead + 0.4 * hbm_spot
        detail["hbm_cycle"] = round(hbm, 3)
        score += 1.0 * hbm

        # (c) NVDA 매출 QoQ 추세
        nvda_trend = self._clip((s.nvda_dc_qoq - s.nvda_dc_qoq_prev) / 10.0, -1, 1)
        detail["nvda_qoq_trend"] = round(nvda_trend, 3)
        score += 0.8 * nvda_trend

        # (d) 재고 증가 + ASP 하락 = 정점 경고 (음의 기여)
        warn = 0.0
        if s.nvda_inventory_mom > 5:
            warn -= self._clip((s.nvda_inventory_mom - 5) / 15.0, 0, 1)
        if s.nvda_gpu_asp_qoq <= -5:
            warn -= self._clip((-5 - s.nvda_gpu_asp_qoq) / 10.0, 0, 1)
        detail["peak_warning"] = round(warn, 3)
        score += 1.0 * warn

        detail["composite_score"] = round(score, 3)

        # 점수 → 위상 (임계값 보정: 중립 구간을 넓혀 과민 반응 완화)
        if s.market_stress and score < -0.6:
            phase = Phase.DOWN
        elif score >= 0.6:
            phase = Phase.ACCEL
        elif score >= -0.6:
            phase = Phase.NEUTRAL
        elif score >= -1.8:
            phase = Phase.PEAK
        else:
            phase = Phase.DOWN

        return phase, detail

    @staticmethod
    def _clip(x, lo, hi):
        return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# 3. 목표 비중 산출 (동적)
# ---------------------------------------------------------------------------

@dataclass
class BandConfig:
    # NVDA 단일 종목 비중 밴드 (%)
    nvda_floor: float = 25.0     # 정점/하강 시 하한 목표
    nvda_ceiling: float = 40.0   # 저점/가속 시 상한 목표
    nvda_stress_cap: float = 35.0  # 시장 악화 시 강제 상한 캡

    # L2(MSFT+GOOGL) 목표 밴드 (%)
    l2_min: float = 15.0
    l2_max: float = 25.0
    msft_split: float = 0.55     # L2 내 MSFT 비중 (나머지는 GOOGL)

    # L1 기타(SNDK/INTC) 합 목표 (%)
    l1_other: float = 12.0

    # L3 분산처 상한 (%)
    l3_max: float = 10.0

    # 현금성 자산 밴드 (%)
    cash_base: float = 5.0       # 평상시 최소 현금
    cash_stress: float = 20.0    # 시장 악화 시 현금 목표
    cash_down: float = 12.0      # 하강 국면 현금 목표

    # 단계적 매수 트리거 (NVDA 고점대비 낙폭 %)
    buy_trigger_1: float = -30.0
    buy_trigger_2: float = -45.0
    buy_step_pct: float = 3.0    # 트리거당 매수 비중(%p)


class TargetAllocator:
    def __init__(self, cfg: BandConfig = BandConfig()):
        self.cfg = cfg

    def nvda_target(self, phase: Phase, s: WeeklySignals) -> float:
        """위상 + HBM 사이클 강도로 NVDA 목표 비중을 밴드 내 연속 산출."""
        cfg = self.cfg
        # 기본 앵커: 위상별
        anchor = {
            Phase.ACCEL:   cfg.nvda_ceiling,        # 40
            Phase.NEUTRAL: (cfg.nvda_ceiling + cfg.nvda_floor) / 2,  # 32.5
            Phase.PEAK:    cfg.nvda_floor + 3,      # 28
            Phase.DOWN:    cfg.nvda_floor,          # 25
        }[phase]

        # HBM 사이클 보정: 식을수록(리드타임 단축, 현물가 하락) NVDA 추가 축소
        hbm_cool = 0.0
        if s.hbm_leadtime_weeks < s.hbm_leadtime_prev:
            hbm_cool += 2.0
        if s.hbm_spot_mom < 0:
            hbm_cool += 2.0
        target = anchor - hbm_cool

        # 정점 경고(ASP 하락) 추가 축소
        if s.nvda_gpu_asp_qoq <= -5:
            target -= 3.0

        # 밴드 클립
        target = max(cfg.nvda_floor, min(cfg.nvda_ceiling, target))

        # 시장 악화 시 강제 캡 35%
        if s.market_stress or s.fed_hiking:
            target = min(target, cfg.nvda_stress_cap)

        return round(target, 1)

    def cash_target(self, phase: Phase, s: WeeklySignals) -> float:
        cfg = self.cfg
        if s.market_stress:
            return cfg.cash_stress
        if phase == Phase.DOWN:
            return cfg.cash_down
        if phase == Phase.PEAK:
            return (cfg.cash_base + cfg.cash_down) / 2
        return cfg.cash_base

    def full_targets(self, phase: Phase, s: WeeklySignals) -> Dict[str, float]:
        """전체 자산 목표 비중(합계 100). 단순·투명하게 규칙 기반 배분."""
        cfg = self.cfg
        nvda = self.nvda_target(phase, s)
        cash = self.cash_target(phase, s)

        # L2: 위상이 정점·하강일수록 상단(분산 강화)
        if phase in (Phase.PEAK, Phase.DOWN):
            l2 = cfg.l2_max
        elif phase == Phase.NEUTRAL:
            l2 = (cfg.l2_min + cfg.l2_max) / 2
        else:
            l2 = cfg.l2_min
        msft = round(l2 * cfg.msft_split, 1)
        googl = round(l2 - msft, 1)

        # L3: 정점·하강에서만 채움
        l3 = cfg.l3_max if phase in (Phase.PEAK, Phase.DOWN) else 0.0

        l1_other = cfg.l1_other  # SNDK + INTC 합

        # 나머지는 L4(QQQ)로 흡수해 합계 100 맞춤
        used = nvda + l1_other + l2 + l3 + cash
        qqq = round(max(0.0, 100.0 - used), 1)

        return {
            "NVDA": nvda,
            "L1_other(SNDK+INTC)": l1_other,
            "MSFT": msft,
            "GOOGL": googl,
            "L3(VRT 등)": l3,
            "QQQ": qqq,
            "CASH": cash,
        }


# ---------------------------------------------------------------------------
# 4. 주간 액션 생성기 (규칙 A/B/C 통합)
# ---------------------------------------------------------------------------

@dataclass
class Action:
    asset: str
    side: str        # BUY / SELL / HOLD
    delta_pct: float # 이번 주 조정 %p (포트폴리오 대비)
    reason: str


class WeeklyEngine:
    def __init__(self, cfg: BandConfig = BandConfig()):
        self.labeler = PhaseLabeler()
        self.alloc = TargetAllocator(cfg)
        self.cfg = cfg

    def run(self, s: WeeklySignals) -> Dict:
        phase, detail = self.labeler.label(s)
        targets = self.alloc.full_targets(phase, s)
        cur = s.current_weights or {}

        actions: List[Action] = []

        # --- 규칙 A: 밴드 리밸런싱 (이탈분의 1/3만) ---
        cur_nvda = cur.get("NVDA", 0.0)
        tgt_nvda = targets["NVDA"]
        gap = tgt_nvda - cur_nvda
        if abs(gap) >= 1.0:
            step = round(gap / 3.0, 1)   # 1/3 분할
            side = "BUY" if step > 0 else "SELL"
            actions.append(Action(
                "NVDA", side, step,
                f"위상 {phase.value}: NVDA 목표 {tgt_nvda}% vs 현재 {cur_nvda}% "
                f"→ 이탈분 {round(gap,1)}%p 중 1/3({step}%p) 조정"
            ))
        else:
            actions.append(Action("NVDA", "HOLD", 0.0,
                f"NVDA 목표 밴드 내({cur_nvda}%≈{tgt_nvda}%) → 유지"))

        # --- 규칙 C: NVDA 축소분을 L2(MSFT,GOOGL)→L3 로 분산 ---
        # 어느 위상이든 NVDA를 줄이면 그 자금의 행선지를 명시해야 실행 가능.
        # 정점·하강일수록 L3 까지 확장, 그 외에는 L2(미달분)만 채움.
        if gap < 0:
            freed = abs(round(gap / 3.0, 1))
            cur_l2 = cur.get("MSFT", 0.0) + cur.get("GOOGL", 0.0)
            tgt_l2 = targets["MSFT"] + targets["GOOGL"]
            l2_need = max(0.0, tgt_l2 - cur_l2)
            to_l2 = min(freed, l2_need)
            for tk, w in (("MSFT", self.cfg.msft_split), ("GOOGL", 1 - self.cfg.msft_split)):
                add = round(to_l2 * w, 1)
                if add > 0:
                    actions.append(Action(tk, "BUY", add,
                        f"규칙C: NVDA 축소분을 L2 인프라({tk})로 분산 "
                        f"(MSFT=현금흐름 완충 / GOOGL=TPU 점유율 헤지)"))
            # L2 채우고 남은 자금은 정점·하강 시 L3 로
            leftover = round(freed - to_l2, 1)
            if leftover > 0 and phase in (Phase.PEAK, Phase.DOWN):
                actions.append(Action("L3(VRT 등)", "BUY", leftover,
                    "규칙C: L2 충족 후 잔여분을 L3(전력·냉각·네트워크)로 분산 — 사이클 평탄화"))
            elif leftover > 0:
                actions.append(Action("CASH", "BUY", leftover,
                    "규칙C: L2 충족 후 잔여분은 현금성 자산으로 대기 (가속국면 추격매수 자제)"))

        # --- 규칙 B: 하강·바닥 + 급락 시 단계적 매수 ---
        if phase == Phase.DOWN and not self._falling_knife(s):
            if s.nvda_drawdown_from_high <= self.cfg.buy_trigger_2:
                actions.append(Action("NVDA", "BUY", self.cfg.buy_step_pct,
                    f"규칙B 2차: NVDA {s.nvda_drawdown_from_high}% 급락 → {self.cfg.buy_step_pct}%p 매수"))
            elif s.nvda_drawdown_from_high <= self.cfg.buy_trigger_1:
                actions.append(Action("NVDA", "BUY", self.cfg.buy_step_pct,
                    f"규칙B 1차: NVDA {s.nvda_drawdown_from_high}% 급락 → {self.cfg.buy_step_pct}%p 매수"))
        elif phase == Phase.DOWN and self._falling_knife(s):
            actions.append(Action("NVDA", "HOLD", 0.0,
                "규칙B 보류: capex 명백한 감소 초입 → 떨어지는 칼날 방지, 바닥 신호 대기"))

        # --- 현금성 자산 목표 안내 ---
        cur_cash = cur.get("CASH", 0.0)
        tgt_cash = targets["CASH"]
        if abs(tgt_cash - cur_cash) >= 1.0:
            side = "BUY" if tgt_cash > cur_cash else "SELL"
            actions.append(Action("CASH", side, round((tgt_cash - cur_cash) / 2, 1),
                f"현금성 자산 목표 {tgt_cash}% vs 현재 {cur_cash}% (위상 {phase.value})"))

        return {
            "phase": phase.value,
            "phase_detail": detail,
            "targets": targets,
            "actions": [asdict(a) for a in actions],
            "notes": self._notes(phase, s),
        }

    def _falling_knife(self, s: WeeklySignals) -> bool:
        """capex 가 명백히 감소 중인 하강 초입인지."""
        return (s.capex_yoy_growth < s.capex_yoy_growth_prev - 15) or s.fed_hiking

    def _notes(self, phase: Phase, s: WeeklySignals) -> List[str]:
        notes = []
        if s.fed_hiking:
            notes.append("연준 인상 전환 감지: NVDA 35% 캡 + 현금 버퍼 우선. capex 채권조달 부담 주의.")
        if s.market_stress:
            notes.append("시장 악화: NVDA 35% 강제 캡 적용, 현금성 자산 상향.")
        if s.nvda_gpu_asp_qoq <= -5:
            notes.append("GPU ASP 분기 -5%↓: 정점 신호. L1 듀레이션 노출 축소 가속.")
        notes.append("본 산출물은 정보·연구 목적이며 투자자문이 아닙니다. 매매 결정과 책임은 본인에게 있습니다.")
        return notes


# ---------------------------------------------------------------------------
# 5. 데모: 2026-05 현재 위상 라벨링 (실데이터 근사)
# ---------------------------------------------------------------------------

def demo_current_week() -> Dict:
    """
    2026-05 실데이터 근사:
      - 빅4 capex 2026 ~$700B, YoY +60~67%대, 직전 추정 대비 상향 (가속 지속)
      - NVDA FY26Q4 DC매출 QoQ +22%, 가이던스 상향, 공급제약(병목)
      - HBM 타이트 지속 (리드타임 길고 현물 강세)
      - ASP 하락/재고증가 신호 없음, 시장 스트레스/인상 없음
    """
    s = WeeklySignals(
        capex_yoy_growth=67.0, capex_yoy_growth_prev=62.0,   # 가속
        hbm_leadtime_weeks=20.0, hbm_leadtime_prev=18.0,     # 타이트↑
        hbm_spot_mom=4.0,                                    # 현물 강세
        nvda_dc_qoq=22.0, nvda_dc_qoq_prev=22.0,             # 고성장 유지
        nvda_inventory_mom=2.0,                              # 재고 안정
        nvda_gpu_asp_qoq=1.0,                                # ASP 견조
        market_stress=False, fed_hiking=False,
        nvda_drawdown_from_high=-8.0,
        hbm_proxy_drawdown=-10.0,
        current_weights={
            # 사용자 현재 추정 비중 (NVDA 과집중 상태)
            "NVDA": 52.0, "L1_other(SNDK+INTC)": 16.0,
            "MSFT": 0.0, "GOOGL": 0.0, "QQQ": 12.0, "CASH": 0.0,
            # (TIGER 나스닥100 등 국내분은 QQQ 군으로 합산 가정)
        },
    )
    engine = WeeklyEngine()
    return engine.run(s)


if __name__ == "__main__":
    result = demo_current_week()
    print(json.dumps(result, ensure_ascii=False, indent=2))
