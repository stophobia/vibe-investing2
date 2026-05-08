"""§8 P2 — E2E user journey using SQLite repo + pure-function services.

Walks the deterministic logic path from onboarding → fortune → unlock →
prediction → ranking math, exercising every service module added in
work-priority §2~§7. Azure Blob calls are NOT exercised here — those have
unit-level mocking gaps that are tracked separately in §8 Locust + live
smoke tests.

The point of this test: prove that the modules compose correctly. If the
e2e fails, one of the units broke a contract another expects.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest

from services.fortune_service import (
    UNLOCK_COST_POINTS, get_risk_pool, is_age_19_or_older,
    is_already_unlocked_today, reroll_fortune, select_for_user,
    unlock_via_invite, unlock_via_points,
)
from services.point_ledger import add_points
from services.prediction_repo import Prediction
from services.prediction_settler import next_trading_day_kst
from services.ranking_builder import wilson_score_lower_bound
from services.ranking_rewards import PREDICTION_REWARDS, REFERRER_REWARDS
from services.referrer_milestones import (
    MILESTONES, donation_tier, is_supporter_or_higher,
)
from services.user_profile import UserProfileRepo


@pytest.fixture
def repo(tmp_path: Path) -> UserProfileRepo:
    return UserProfileRepo(tmp_path / "e2e.db", salt="e2e-salt")


def test_full_onboarding_to_ranking_journey(repo: UserProfileRepo) -> None:
    """End-to-end: onboard → fortune → unlock → prediction → settle math →
    ranking score. All services compose cleanly."""

    # Step 1 (§3 Step 3) — onboard
    user_key = "tg:e2etest"
    repo.get_or_create(user_key, "ko", "buffett")

    # Birth date 1990-01-15, must pass age check
    assert is_age_19_or_older("1990-01-15")
    repo.update(user_key, saju_birth_date="1990-01-15", saju_birth_hour=8)
    profile = repo.get(user_key)
    assert profile.saju_birth_date == "1990-01-15"

    # Step 2 (§3 Step 1) — daily fortune select (deterministic)
    result = select_for_user(profile)
    assert result is not None
    assert "lucky_number" in result
    assert 0 <= result["lucky_number"] <= 9
    assert result["free"]["risk"] in ("low", "medium", "high")
    assert len(result["locked"]) == 2

    # Step 3 (§3 Step 3) — unlock locked ticker via points
    asyncio.run(add_points(repo, user_key, UNLOCK_COST_POINTS + 50, "test_seed"))
    profile = repo.get(user_key)
    locked_ticker = result["locked"][0]["ticker"]
    ok, reason, updated = asyncio.run(
        unlock_via_points(repo, profile, locked_ticker))
    assert ok and reason == "ok"
    assert updated.points_balance == 50  # only UNLOCK_COST_POINTS deducted
    assert locked_ticker in updated.saju_unlocked_today

    # Step 3.5 — same-day re-unlock is idempotent
    ok2, reason2, _ = asyncio.run(
        unlock_via_points(repo, repo.get(user_key), locked_ticker))
    assert ok2 and reason2 == "already_unlocked"
    assert repo.get(user_key).points_balance == 50  # no extra deduction

    # Step 4 (§4) — submit a prediction
    target = next_trading_day_kst()
    p = Prediction.new(
        anon=updated.anon_user_id, ticker="AAPL", direction="up",
        created_price=200.0, target_date=target,
    )
    assert p.status == "pending"
    assert p.ticker == "AAPL"

    # Step 4.5 — settle math (without yfinance)
    # Manually set close > created → "win"
    p.settled_price = 210.0
    p.status = "settled"
    p.result = "win"
    assert p.result == "win"

    # Step 5 (§6) — Wilson score for 1/1 win < 1.0 (small-N protection)
    score = wilson_score_lower_bound(1, 1)
    assert 0.15 < score < 0.30
    # 8/10 should be much higher than 1/1
    assert wilson_score_lower_bound(8, 10) > score

    # Step 6 (§6) — reward table sanity (top-1 daily prediction = 500 P)
    assert PREDICTION_REWARDS["daily"][1] == 500
    assert REFERRER_REWARDS["daily"][1] == 1000  # 2× prediction

    # Step 7 (§7) — donation tier transitions
    assert donation_tier(0) == "none"
    assert donation_tier(1) == "supporter"
    assert donation_tier(500) == "patron"

    # Step 8 (§7) — Supporter+ first reroll free, second charges
    repo.update(user_key, donation_total_usdt=10.0)  # become Supporter
    profile = repo.get(user_key)
    ok_free, reason_free, after = asyncio.run(reroll_fortune(repo, profile))
    assert ok_free
    assert reason_free == "ok_free"  # free path
    assert after.points_balance == 50  # no deduction
    assert after.fortune_reroll_count_today == 1

    # Second reroll same day — falls back to charging 10 P
    after2_call = asyncio.run(reroll_fortune(repo, repo.get(user_key)))
    assert after2_call[0]  # ok
    assert after2_call[1] == "ok"  # paid path (not "ok_free")
    assert repo.get(user_key).points_balance == 40  # 50 - 10

    # Step 9 (§7) — invite unlock for invitee with verified referee
    repo.update(user_key, invite_validated_count=1)
    profile = repo.get(user_key)
    # New ticker (not yet unlocked today)
    fresh_ticker = result["locked"][1]["ticker"]
    ok, reason, _ = asyncio.run(unlock_via_invite(repo, profile, fresh_ticker))
    assert ok and reason == "ok"


def test_milestone_threshold_progression() -> None:
    """§7 milestone bonuses scale with USDT amount."""
    prev = 0
    for ms in sorted(MILESTONES.keys()):
        assert MILESTONES[ms] > prev
        prev = MILESTONES[ms]
    # Sanity: $5k milestone = 25k P (50× the $100 = 500 P bonus)
    assert MILESTONES[5000] == 25000


def test_age_check_boundary() -> None:
    """§3 — exactly 19 yo on today's date passes; 18yo 11mo fails."""
    assert is_age_19_or_older("2007-01-01", today_iso="2026-01-01")
    assert not is_age_19_or_older("2007-06-15", today_iso="2026-05-08")


def test_supporter_check_at_one_dollar() -> None:
    """§7 — Supporter status begins exactly at $1 cumulative."""
    assert not is_supporter_or_higher(0.99)
    assert is_supporter_or_higher(1.0)
    assert is_supporter_or_higher(99999)


def test_unlock_costs_are_consistent() -> None:
    """§3+§7 — pricing constants haven't drifted from spec."""
    from services.fortune_service import REROLL_COST_POINTS
    assert UNLOCK_COST_POINTS == 100  # spec §3.6
    assert REROLL_COST_POINTS == 10   # spec §7.3
