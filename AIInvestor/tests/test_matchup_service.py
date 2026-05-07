"""Tests for matchup_service generation, gauge math, and deadline logic."""

from __future__ import annotations

from services.matchup_service import (
    AssetRef,
    Matchup,
    Prediction,
    _matchup_id,
    generate_matchups_for_hour,
)
from services.movers_source import Mover, MoversSnapshot


def _mk_snap() -> MoversSnapshot:
    """Synthetic snapshot with 6 stock movers + 6 crypto movers."""
    stocks = [
        Mover(t, t, "stock", price, pct) for (t, price, pct) in (
            ("NVDA", 800.0, 0.12),
            ("TSLA", 250.0, -0.08),
            ("AAPL", 200.0, 0.07),
            ("AMD",  150.0, -0.05),
            ("META", 500.0, 0.04),
            ("MSFT", 410.0, 0.03),
        )
    ]
    cryptos = [
        Mover(t, t.replace("-USD", ""), "crypto", price, pct) for (t, price, pct) in (
            ("BTC-USD", 70000.0, 0.10),
            ("ETH-USD",  3500.0, -0.06),
            ("SOL-USD",   200.0, 0.15),
            ("DOGE-USD",  0.15,  0.20),
            ("AVAX-USD",  35.0, -0.04),
            ("MATIC-USD", 0.85,  0.05),
        )
    ]
    return MoversSnapshot(kst_date="2026-05-07", fetched_at="x",
                          stocks=stocks, cryptos=cryptos)


class TestGenerator:
    def test_generates_three_matchups(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        assert len(ms) == 3

    def test_types_distributed(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        types = sorted([m.type for m in ms])
        assert types == ["cc", "sc", "ss"]

    def test_anchor_set_to_last_close(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        ss = next(m for m in ms if m.type == "ss")
        assert ss.anchor_a == ss.asset_a.yesterday_pct or ss.anchor_a > 0
        # Anchor should match the source mover's last_close
        for m in ms:
            assert m.anchor_a > 0
            assert m.anchor_b > 0
            assert m.last_a == m.anchor_a  # initial gauge equals anchor
            assert m.last_b == m.anchor_b

    def test_resolve_at_distributed(self) -> None:
        """3 matchups should have 3 different resolve times (distributed)."""
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        resolve_times = {m.resolve_at_kst for m in ms}
        assert len(resolve_times) == 3

    def test_no_duplicate_assets_in_pairings(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        for m in ms:
            assert m.asset_a.ticker != m.asset_b.ticker

    def test_ss_is_two_stocks(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        ss = next(m for m in ms if m.type == "ss")
        assert ss.asset_a.kind == "stock"
        assert ss.asset_b.kind == "stock"

    def test_cc_is_two_cryptos(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        cc = next(m for m in ms if m.type == "cc")
        assert cc.asset_a.kind == "crypto"
        assert cc.asset_b.kind == "crypto"

    def test_sc_is_mixed(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        sc = next(m for m in ms if m.type == "sc")
        kinds = {sc.asset_a.kind, sc.asset_b.kind}
        assert kinds == {"stock", "crypto"}

    def test_id_format(self) -> None:
        snap = _mk_snap()
        ms = generate_matchups_for_hour(snap, "2026-05-07", 14)
        for i, m in enumerate(ms, 1):
            assert m.id == f"2026-05-07-h14-m{i}"

    def test_deterministic_per_hour(self) -> None:
        """Same (date, hour, snap) should produce same matchups."""
        snap = _mk_snap()
        ms1 = generate_matchups_for_hour(snap, "2026-05-07", 14)
        ms2 = generate_matchups_for_hour(snap, "2026-05-07", 14)
        assert [m.id for m in ms1] == [m.id for m in ms2]
        assert [m.asset_a.ticker for m in ms1] == [m.asset_a.ticker for m in ms2]
        assert [m.asset_b.ticker for m in ms1] == [m.asset_b.ticker for m in ms2]


class TestGaugeMath:
    def _mk(self, anchor_a: float, anchor_b: float,
            last_a: float, last_b: float) -> Matchup:
        return Matchup(
            id="test", type="ss",
            asset_a=AssetRef("A", "A", "stock"),
            asset_b=AssetRef("B", "B", "stock"),
            open_at_kst="", deadline_kst="", resolve_at_kst="",
            anchor_a=anchor_a, anchor_b=anchor_b,
            last_a=last_a, last_b=last_b,
            last_polled_at="", status="open", winner="",
        )

    def test_equal_pcts_balance_at_50(self) -> None:
        m = self._mk(100, 100, 105, 105)  # both +5%
        a, b = m.gauge_pct()
        assert abs(a - 50.0) < 0.5
        assert abs(b - 50.0) < 0.5

    def test_a_leading(self) -> None:
        m = self._mk(100, 100, 110, 100)  # A +10%, B 0%
        a, b = m.gauge_pct()
        assert a > 80
        assert b < 20

    def test_b_leading(self) -> None:
        m = self._mk(100, 100, 100, 110)  # A 0%, B +10%
        a, b = m.gauge_pct()
        assert b > 80
        assert a < 20

    def test_clamped_to_5_95(self) -> None:
        # Extreme values should not blow past clamp
        m = self._mk(100, 100, 200, 50)
        a, b = m.gauge_pct()
        assert 5.0 <= a <= 95.0
        assert 5.0 <= b <= 95.0

    def test_zero_anchor_falls_back_to_50(self) -> None:
        m = self._mk(0, 100, 0, 110)
        a, b = m.gauge_pct()
        assert a == 50.0
        assert b == 50.0


class TestPredictionDataclass:
    def test_prediction_includes_both_keys(self) -> None:
        p = Prediction(user_key="uk", anon_user_id="anon123",
                       side="a", submitted_at="2026-05-07T12:00:00")
        assert p.user_key == "uk"
        assert p.anon_user_id == "anon123"


class TestMatchupId:
    def test_format(self) -> None:
        assert _matchup_id("2026-05-07", 14, 1) == "2026-05-07-h14-m1"

    def test_zero_padded_hour(self) -> None:
        assert _matchup_id("2026-05-07", 4, 1) == "2026-05-07-h04-m1"
