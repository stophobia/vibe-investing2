"""§6 P1 — Tests for Wilson score + ranking helpers (pure functions only)."""

from __future__ import annotations

import pytest

from services.ranking_builder import (
    RankingRow,
    _cutoff_iso,
    wilson_score_lower_bound,
)
from services.ranking_rewards import (
    PREDICTION_REWARDS,
    REFERRER_REWARDS,
)


class TestWilsonScore:
    def test_zero_total(self) -> None:
        assert wilson_score_lower_bound(0, 0) == 0.0

    def test_one_of_one(self) -> None:
        # 95% CI lower bound of 1/1 should be ~0.21 — much less than 100%
        s = wilson_score_lower_bound(1, 1)
        assert 0.15 < s < 0.30

    def test_eight_of_ten(self) -> None:
        s = wilson_score_lower_bound(8, 10)
        assert 0.45 < s < 0.55

    def test_eighty_of_hundred(self) -> None:
        s = wilson_score_lower_bound(80, 100)
        assert 0.70 < s < 0.75

    def test_higher_total_outranks_one_of_one(self) -> None:
        """Wilson core property: large sample beats small sample at same %."""
        small = wilson_score_lower_bound(1, 1)       # 100%
        large = wilson_score_lower_bound(10, 10)     # 100%
        assert large > small

    def test_perfect_score_caps_below_1(self) -> None:
        """Wilson lower bound never reaches 1.0 — protects vs. small-N hype."""
        assert wilson_score_lower_bound(100, 100) < 1.0

    def test_zero_wins_returns_low(self) -> None:
        s = wilson_score_lower_bound(0, 10)
        assert s < 0.10


class TestCutoffIso:
    def test_daily_within_24h(self) -> None:
        from datetime import datetime, timezone, timedelta
        now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
        cutoff = _cutoff_iso("daily", now_utc=now)
        assert cutoff.startswith("2026-05-07T12:00:00")

    def test_weekly_within_7d(self) -> None:
        from datetime import datetime, timezone
        now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
        cutoff = _cutoff_iso("weekly", now_utc=now)
        assert cutoff.startswith("2026-05-01T12:00:00")

    def test_monthly_within_30d(self) -> None:
        from datetime import datetime, timezone
        now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
        cutoff = _cutoff_iso("monthly", now_utc=now)
        assert cutoff.startswith("2026-04-08T12:00:00")


class TestRewardTables:
    def test_prediction_daily_top_pays_500(self) -> None:
        assert PREDICTION_REWARDS["daily"][1] == 500

    def test_prediction_weekly_top_pays_2000(self) -> None:
        assert PREDICTION_REWARDS["weekly"][1] == 2000

    def test_prediction_monthly_top_pays_10000(self) -> None:
        assert PREDICTION_REWARDS["monthly"][1] == 10000

    def test_referrer_doubles_prediction(self) -> None:
        for period in ("daily", "weekly", "monthly"):
            for rank in range(1, 11):
                assert REFERRER_REWARDS[period][rank] == \
                    PREDICTION_REWARDS[period][rank] * 2

    def test_ranks_2_3_pay_more_than_4_10(self) -> None:
        for period in ("daily", "weekly", "monthly"):
            for rank in range(4, 11):
                assert PREDICTION_REWARDS[period][2] > PREDICTION_REWARDS[period][rank]
                assert PREDICTION_REWARDS[period][3] > PREDICTION_REWARDS[period][rank]

    def test_only_top_10_pay(self) -> None:
        for period in ("daily", "weekly", "monthly"):
            assert max(PREDICTION_REWARDS[period].keys()) == 10
            assert min(PREDICTION_REWARDS[period].keys()) == 1


class TestRankingRow:
    def test_default_values(self) -> None:
        r = RankingRow(rank=1, anon_short="abc12345", score=0.5)
        assert r.wins == 0
        assert r.total == 0
        assert r.win_rate == 0.0
        assert r.referees == 0
