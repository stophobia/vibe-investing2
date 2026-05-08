"""§7 P2 — referrer_milestones pure-function tests.

Schedule + payout require Azure Blob; covered in §8 e2e.
"""

from __future__ import annotations

import pytest

from services.referrer_milestones import (
    HOLDING_DAYS,
    MILESTONES,
    donation_tier,
    is_supporter_or_higher,
)


class TestMilestoneTable:
    def test_four_milestones(self) -> None:
        assert set(MILESTONES.keys()) == {100, 500, 1000, 5000}

    def test_amount_progression(self) -> None:
        """Higher milestone → higher P payout."""
        prev = 0
        for ms in sorted(MILESTONES.keys()):
            assert MILESTONES[ms] > prev
            prev = MILESTONES[ms]

    def test_holding_period_30_days(self) -> None:
        assert HOLDING_DAYS == 30


class TestDonationTier:
    def test_zero_is_none(self) -> None:
        assert donation_tier(0) == "none"

    def test_below_one_is_none(self) -> None:
        assert donation_tier(0.5) == "none"

    def test_one_is_supporter(self) -> None:
        assert donation_tier(1) == "supporter"

    def test_500_is_patron(self) -> None:
        assert donation_tier(500) == "patron"

    def test_1000_is_benefactor(self) -> None:
        assert donation_tier(1000) == "benefactor"

    def test_5000_is_champion(self) -> None:
        assert donation_tier(5000) == "champion"
        assert donation_tier(99999) == "champion"


class TestIsSupporterOrHigher:
    def test_zero_false(self) -> None:
        assert not is_supporter_or_higher(0)

    def test_one_true(self) -> None:
        assert is_supporter_or_higher(1.0)

    def test_below_one_false(self) -> None:
        assert not is_supporter_or_higher(0.99)

    def test_large_true(self) -> None:
        assert is_supporter_or_higher(10000)
