"""Tests for donation_service intent creation, matching, and parsing."""

from __future__ import annotations

import pytest

from services.chain_clients import _parse_ton_jetton_events, _parse_tron_trc20
from services.donation_service import (
    AMOUNT_TIERS,
    POINTS_PER_USDT,
    WALLET_TON,
    WALLET_TRON,
    DonationIntent,
    IncomingTx,
    _fingerprint_to_amount,
    _intent_to_fingerprint,
    amount_matches,
    build_intent,
    find_match,
    memo_matches,
    points_for,
)


class TestPointsConversion:
    def test_one_usdt(self) -> None:
        assert points_for(1) == POINTS_PER_USDT

    def test_thousand_usdt(self) -> None:
        assert points_for(1000) == 1000 * POINTS_PER_USDT


class TestBuildIntent:
    def test_ton_intent_has_memo(self) -> None:
        i = build_intent(user_key="uk", anon_user_id="a1",
                         amount_usdt=10, chain="ton")
        assert i.chain == "ton"
        assert i.wallet_address == WALLET_TON
        assert i.memo.startswith("vinv-")
        assert i.fingerprint_suffix == ""
        assert i.expected_amount == 10.0

    def test_tron_intent_has_fingerprint(self) -> None:
        i = build_intent(user_key="uk", anon_user_id="a1",
                         amount_usdt=50, chain="tron")
        assert i.chain == "tron"
        assert i.wallet_address == WALLET_TRON
        assert i.memo == ""
        assert len(i.fingerprint_suffix) == 4
        assert i.expected_amount > 50.0
        assert i.expected_amount < 50.01  # 4-digit suffix → max $0.009999 added

    def test_invalid_amount_rejected(self) -> None:
        with pytest.raises(ValueError):
            build_intent(user_key="uk", anon_user_id="a1",
                         amount_usdt=7, chain="ton")

    def test_invalid_chain_rejected(self) -> None:
        with pytest.raises(ValueError):
            build_intent(user_key="uk", anon_user_id="a1",
                         amount_usdt=10, chain="eth")

    def test_unique_intent_ids(self) -> None:
        ids = {build_intent(user_key="uk", anon_user_id="a1",
                            amount_usdt=10, chain="ton").intent_id
               for _ in range(100)}
        assert len(ids) >= 95  # very high uniqueness expected from 32^8

    def test_all_tiers_supported(self) -> None:
        for tier in AMOUNT_TIERS:
            i = build_intent(user_key="uk", anon_user_id="a1",
                             amount_usdt=tier, chain="ton")
            assert i.amount_usdt == float(tier)
            assert i.points_to_credit == tier * POINTS_PER_USDT


class TestFingerprint:
    def test_fingerprint_is_4_digits(self) -> None:
        f = _intent_to_fingerprint("ABCD1234")
        assert len(f) == 4
        assert f.isdigit()

    def test_fingerprint_deterministic(self) -> None:
        assert _intent_to_fingerprint("X") == _intent_to_fingerprint("X")

    def test_fingerprint_to_amount(self) -> None:
        assert _fingerprint_to_amount(50, "0731") == 50.000731

    def test_fingerprint_avoids_zero(self) -> None:
        # Just check that varying inputs give >0 fingerprints
        for s in ("A", "B", "C", "D", "E"):
            assert int(_intent_to_fingerprint(s)) > 0


class TestMatching:
    def _ton_intent(self) -> DonationIntent:
        return build_intent(user_key="uk", anon_user_id="a1",
                            amount_usdt=10, chain="ton")

    def _tron_intent(self) -> DonationIntent:
        return build_intent(user_key="uk", anon_user_id="a1",
                            amount_usdt=50, chain="tron")

    def test_amount_matches_ton_face(self) -> None:
        i = self._ton_intent()
        assert amount_matches(i, 10.0)
        assert amount_matches(i, 10.0005)
        assert not amount_matches(i, 10.5)

    def test_amount_matches_tron_fingerprint(self) -> None:
        i = self._tron_intent()
        assert amount_matches(i, i.expected_amount)
        # Wrong fingerprint → no match
        assert not amount_matches(i, 50.0)
        assert not amount_matches(i, 50.123456)

    def test_memo_matches_ton(self) -> None:
        i = self._ton_intent()
        assert memo_matches(i, i.memo)
        assert memo_matches(i, f"  {i.memo.upper()}  ")
        assert not memo_matches(i, "different-memo")

    def test_memo_ignored_for_tron(self) -> None:
        i = self._tron_intent()
        assert memo_matches(i, "")
        assert memo_matches(i, "anything")

    def test_find_match_ton_picks_correct_intent(self) -> None:
        i1 = self._ton_intent()
        i2 = self._ton_intent()
        tx = IncomingTx(tx_hash="0xa", amount_usdt=10.0,
                        memo=i2.memo, chain="ton", seen_at="")
        assert find_match([i1, i2], tx) is i2

    def test_find_match_tron_amount_only(self) -> None:
        i1 = self._tron_intent()
        i2 = self._tron_intent()
        tx = IncomingTx(tx_hash="0xb", amount_usdt=i2.expected_amount,
                        memo="", chain="tron", seen_at="")
        assert find_match([i1, i2], tx) is i2

    def test_find_match_returns_none_when_no_amount_match(self) -> None:
        i = self._ton_intent()
        tx = IncomingTx(tx_hash="0xc", amount_usdt=999.0,
                        memo=i.memo, chain="ton", seen_at="")
        assert find_match([i], tx) is None

    def test_find_match_skips_other_chain(self) -> None:
        ton_i = self._ton_intent()
        tron_tx = IncomingTx(tx_hash="0xd", amount_usdt=10.0,
                             memo="", chain="tron", seen_at="")
        assert find_match([ton_i], tron_tx) is None


class TestTonParser:
    def test_parses_jetton_transfer(self) -> None:
        wallet = WALLET_TON
        sample = {
            "events": [{
                "event_id": "0xeventA",
                "timestamp": 1715050800,
                "actions": [{
                    "type": "JettonTransfer",
                    "JettonTransfer": {
                        "sender": {"address": "0:abc"},
                        "recipient": {"address": wallet},
                        "amount": "10000000",  # 10 USDT
                        "comment": "vinv-K3F7A2QM",
                    },
                }],
            }]
        }
        out = _parse_ton_jetton_events(sample, wallet)
        assert len(out) == 1
        assert out[0].amount_usdt == 10.0
        assert out[0].memo == "vinv-K3F7A2QM"
        assert out[0].chain == "ton"
        assert out[0].tx_hash == "0xeventA"

    def test_skips_non_jetton_actions(self) -> None:
        sample = {
            "events": [{
                "event_id": "0xX",
                "timestamp": 0,
                "actions": [{"type": "TonTransfer"}],
            }]
        }
        assert _parse_ton_jetton_events(sample, WALLET_TON) == []

    def test_handles_empty_events(self) -> None:
        assert _parse_ton_jetton_events({}, WALLET_TON) == []
        assert _parse_ton_jetton_events({"events": []}, WALLET_TON) == []


class TestTronParser:
    def test_parses_trc20_transfer(self) -> None:
        wallet = WALLET_TRON
        sample = {
            "data": [{
                "transaction_id": "0xtxA",
                "value": "50000731",  # 50.000731 USDT
                "to": wallet,
                "block_timestamp": 1715050800000,
            }]
        }
        out = _parse_tron_trc20(sample, wallet)
        assert len(out) == 1
        assert out[0].amount_usdt == 50.000731
        assert out[0].chain == "tron"
        assert out[0].tx_hash == "0xtxA"
        assert out[0].memo == ""

    def test_handles_empty(self) -> None:
        assert _parse_tron_trc20({}, WALLET_TRON) == []
        assert _parse_tron_trc20({"data": []}, WALLET_TRON) == []

    def test_skips_non_target_recipient(self) -> None:
        wallet = WALLET_TRON
        sample = {
            "data": [{
                "transaction_id": "0xZ",
                "value": "1000000",
                "to": "TOtherAddress12345",
                "block_timestamp": 0,
            }]
        }
        assert _parse_tron_trc20(sample, wallet) == []
