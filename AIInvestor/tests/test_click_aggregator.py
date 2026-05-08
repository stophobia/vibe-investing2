"""Tests for §5 click rate-limiter (pure function, no Azure)."""

from __future__ import annotations

import time

import pytest

from services.click_aggregator import (
    _RECENT_CLICKS,
    _click_log_path,
    is_rate_limited,
)
from datetime import datetime, timezone


@pytest.fixture(autouse=True)
def _clear_state():
    _RECENT_CLICKS.clear()
    yield
    _RECENT_CLICKS.clear()


class TestRateLimit:
    def test_first_click_allowed(self) -> None:
        assert not is_rate_limited("v1", "p1")

    def test_second_click_blocked(self) -> None:
        is_rate_limited("v1", "p1")
        assert is_rate_limited("v1", "p1")

    def test_different_viewer_allowed(self) -> None:
        is_rate_limited("v1", "p1")
        assert not is_rate_limited("v2", "p1")

    def test_different_prediction_allowed(self) -> None:
        is_rate_limited("v1", "p1")
        assert not is_rate_limited("v1", "p2")

    def test_after_window_allowed(self) -> None:
        # Manually expire by mutating monotonic-style stamp
        is_rate_limited("v1", "p1")
        _RECENT_CLICKS[("v1", "p1")] = time.monotonic() - 31  # past 30s window
        assert not is_rate_limited("v1", "p1")


class TestClickLogPath:
    def test_format(self) -> None:
        ts = datetime(2026, 5, 8, 14, 30, tzinfo=timezone.utc)
        assert _click_log_path(ts) == "clicks/2026/05/08/14.ndjson"

    def test_uses_now_when_omitted(self) -> None:
        # Just verify the structure
        path = _click_log_path()
        parts = path.split("/")
        assert parts[0] == "clicks"
        assert len(parts) == 5
        assert parts[-1].endswith(".ndjson")
