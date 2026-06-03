"""
volume_normalization.py  -- 거래량 정규화 모듈 (c)
====================================================
주식과 가상자산은 거래량의 '단위/주기/품질'이 근본적으로 다르므로,
같은 매매 규칙을 적용하려면 거래량을 정규화(normalize)해야 한다.

핵심 차이
---------
                  주식 (Stock)                 가상자산 (Crypto)
  단위            주(shares)                    코인 수량 or 호가통화 금액
  주기            세션 기반(장중 U자 계절성)    24/7 연속(주간/요일 계절성)
  리셋            일 단위 세션 리셋             세션 없음(rolling/anchored)
  품질            거래소 보고 일관성 높음       wash trading 오염 가능
  비교가능성      종목 간 절대량 비교 곤란       거래소 간 분절(fragmented)

전략: 절대 거래량(raw volume)을 직접 쓰지 않고
  1) Dollar/Quote Volume 으로 금액 환산(자산 간 비교)
  2) Relative Volume(RVOL) 또는 Z-score 로 자기 기준 정규화(레짐 비교)
  3) 시장별 계절성 제거(주식=장중 시간대, 크립토=요일/시간)
  4) (크립토) wash-trade 완화 필터
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class VolumeNormalizer:
    """시장 유형에 따라 거래량 정규화 방식을 분기하는 클래스.

    Parameters
    ----------
    market_type : {"stock", "crypto"}
        정규화 로직 분기 기준.
    rvol_lookback : int
        Relative Volume / Z-score 산출 시 기준이 되는 과거 봉 개수.
    use_log : bool
        거래량 분포는 우측 꼬리(right-skew)가 심하므로 log1p 변환 적용 여부.
    """

    def __init__(
        self,
        market_type: str = "stock",
        rvol_lookback: int = 20,
        use_log: bool = True,
    ) -> None:
        if market_type not in ("stock", "crypto"):
            raise ValueError("market_type must be 'stock' or 'crypto'")
        self.market_type = market_type
        self.rvol_lookback = rvol_lookback
        self.use_log = use_log

    # ------------------------------------------------------------------ #
    # 1) 금액 환산 — 자산 간 비교 가능성 확보
    # ------------------------------------------------------------------ #
    @staticmethod
    def dollar_volume(df: pd.DataFrame) -> pd.Series:
        """체결 금액 기준 거래량 = 대표가격 * 거래량.

        주식: 주 * 가격 = 거래대금
        크립토: 코인수량 * 가격 = quote-currency(USD/USDT) 거래대금
        서로 다른 가격대의 자산을 동일 축에서 비교할 수 있게 한다.
        """
        typical = (df["high"] + df["low"] + df["close"]) / 3.0
        return typical * df["volume"]

    # ------------------------------------------------------------------ #
    # 2) 자기 기준 정규화 — Relative Volume & Z-score
    # ------------------------------------------------------------------ #
    def relative_volume(self, df: pd.DataFrame, volume_col: str = "volume") -> pd.Series:
        """RVOL = 현재 거래량 / 과거 평균 거래량.

        레짐/종목과 무관하게 '평소 대비 몇 배인가'를 측정 → 승인 게이트 핵심값.
        RVOL >= 1.5 면 통상 '거래량 팽창'으로 본다.
        """
        vol = df[volume_col].astype(float)
        if self.use_log:
            base = np.log1p(vol)
            avg = base.rolling(self.rvol_lookback, min_periods=self.rvol_lookback).mean()
            return np.expm1(base) / np.expm1(avg)
        avg = vol.rolling(self.rvol_lookback, min_periods=self.rvol_lookback).mean()
        return vol / avg

    def volume_zscore(self, df: pd.DataFrame, volume_col: str = "volume") -> pd.Series:
        """거래량 Z-score = (V - rolling_mean) / rolling_std.

        RVOL이 '배수' 개념이라면 Z-score는 '통계적 이탈 정도'.
        Z >= 2.0 이면 통계적으로 유의한 거래량 급증.
        """
        vol = df[volume_col].astype(float)
        if self.use_log:
            vol = np.log1p(vol)
        mean = vol.rolling(self.rvol_lookback, min_periods=self.rvol_lookback).mean()
        std = vol.rolling(self.rvol_lookback, min_periods=self.rvol_lookback).std(ddof=0)
        return (vol - mean) / std.replace(0, np.nan)

    # ------------------------------------------------------------------ #
    # 3) 계절성 제거 — 시장별 분기
    # ------------------------------------------------------------------ #
    def seasonal_adjusted_rvol(self, df: pd.DataFrame) -> pd.Series:
        """계절성 제거 RVOL.

        주식: 장중 U자(개장/마감 거래량 폭증) → '같은 시간대' 평균으로 정규화.
        크립토: 요일+시간(주말 저조) → '같은 요일·시간' 평균으로 정규화.
        DatetimeIndex 가 필요하다.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("seasonal_adjusted_rvol requires a DatetimeIndex")

        vol = df["volume"].astype(float)
        if self.market_type == "stock":
            # 시간(HH:MM) 버킷별 기대 거래량 프로파일
            bucket = df.index.strftime("%H:%M")
        else:
            # 요일-시간 버킷 (0=월 ... 6=일)
            bucket = df.index.dayofweek.astype(str) + "_" + df.index.strftime("%H")

        bucket = pd.Series(bucket, index=df.index)
        expected = vol.groupby(bucket).transform("mean")
        return vol / expected.replace(0, np.nan)

    # ------------------------------------------------------------------ #
    # 4) (크립토 전용) wash-trade 완화 필터
    # ------------------------------------------------------------------ #
    def washtrade_filter(
        self,
        df: pd.DataFrame,
        trade_count_col: str | None = "trade_count",
        min_vol_per_trade_pctl: float = 0.99,
    ) -> pd.Series:
        """건당 거래량(volume / trade_count)이 비정상적으로 큰 봉을 의심 표시.

        wash trading은 소수 대량 체결로 거래량을 부풀리는 경향이 있어,
        '건당 거래량'이 상위 극단값이면 신호 신뢰도를 낮춘다.
        반환: True = 정상(신뢰), False = 의심(거래량 신호 기각 권장).
        trade_count 가 없으면 전부 True 로 통과시킨다(주식 등).
        """
        if self.market_type != "crypto" or trade_count_col not in df.columns:
            return pd.Series(True, index=df.index)
        per_trade = df["volume"] / df[trade_count_col].replace(0, np.nan)
        threshold = per_trade.quantile(min_vol_per_trade_pctl)
        return per_trade <= threshold

    # ------------------------------------------------------------------ #
    # 통합 진입점
    # ------------------------------------------------------------------ #
    def normalize(self, df: pd.DataFrame, seasonal: bool = False) -> pd.DataFrame:
        """모든 정규화 컬럼을 한 번에 부착해 반환.

        추가 컬럼:
          dollar_volume, rvol, vol_z, [seasonal_rvol], vol_trustworthy
        """
        out = df.copy()
        out["dollar_volume"] = self.dollar_volume(out)
        out["rvol"] = self.relative_volume(out)
        out["vol_z"] = self.volume_zscore(out)
        if seasonal and isinstance(out.index, pd.DatetimeIndex):
            out["seasonal_rvol"] = self.seasonal_adjusted_rvol(out)
        out["vol_trustworthy"] = self.washtrade_filter(out)
        return out


if __name__ == "__main__":
    # 간단 자가 점검
    idx = pd.date_range("2024-01-01", periods=200, freq="1h")
    rng = np.random.default_rng(0)
    demo = pd.DataFrame(
        {
            "high": 100 + rng.normal(0, 2, 200).cumsum(),
            "low": 99 + rng.normal(0, 2, 200).cumsum(),
            "close": 99.5 + rng.normal(0, 2, 200).cumsum(),
            "volume": rng.lognormal(10, 1, 200),
            "trade_count": rng.integers(50, 500, 200),
        },
        index=idx,
    )
    for mt in ("stock", "crypto"):
        n = VolumeNormalizer(market_type=mt)
        res = n.normalize(demo, seasonal=True)
        print(f"[{mt}] cols:", [c for c in res.columns if c not in demo.columns])
        print(res[["rvol", "vol_z", "vol_trustworthy"]].dropna().head(2).round(3))
