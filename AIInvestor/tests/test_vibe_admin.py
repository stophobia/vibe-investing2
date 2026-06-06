"""§Vibe P5(수정) — admin stats: 캐시 hit/miss + cron status + endpoint 카운터."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from services.vibe import admin_stats, api_cache


@pytest.fixture(autouse=True)
def _reset_state():
    api_cache._MEMOS.clear()
    admin_stats._endpoint_counters.clear()
    yield
    api_cache._MEMOS.clear()
    admin_stats._endpoint_counters.clear()


# ──────────────────────────────────────────────────────────────────────────────
# Cache hit/miss counters
# ──────────────────────────────────────────────────────────────────────────────
class TestCacheStats:
    def test_initial_empty(self) -> None:
        stats = api_cache.get_cache_stats()
        assert stats == {"paths": [], "total_hits": 0,
                          "total_misses": 0, "total_ratio": 0.0}

    def test_miss_then_hit_counts(self) -> None:
        async def fake_load(account, path, *, default=None, credential=None):
            return {"x": 1}

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load):
            # 첫 호출: miss
            asyncio.run(api_cache.cached_blob_read("a", "p.json", ttl_s=60.0))
            # 두 번째: hit (TTL 내)
            asyncio.run(api_cache.cached_blob_read("a", "p.json", ttl_s=60.0))
            asyncio.run(api_cache.cached_blob_read("a", "p.json", ttl_s=60.0))

        stats = api_cache.get_cache_stats()
        assert len(stats["paths"]) == 1
        path_stat = stats["paths"][0]
        assert path_stat["path"] == "p.json"
        assert path_stat["misses"] == 1
        assert path_stat["hits"] == 2
        assert path_stat["ratio"] == pytest.approx(2 / 3, abs=0.001)
        assert stats["total_hits"] == 2
        assert stats["total_misses"] == 1

    def test_ratio_zero_when_only_misses(self) -> None:
        async def fake_load(account, path, *, default=None, credential=None):
            return None  # None 응답 → 캐시 안 됨

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load):
            asyncio.run(api_cache.cached_blob_read("a", "missing.json", ttl_s=60.0))
            asyncio.run(api_cache.cached_blob_read("a", "missing.json", ttl_s=60.0))

        stats = api_cache.get_cache_stats()
        assert stats["paths"][0]["ratio"] == 0.0

    def test_multiple_paths_separately_tracked(self) -> None:
        async def fake_load(account, path, *, default=None, credential=None):
            return {"path": path}

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load):
            asyncio.run(api_cache.cached_blob_read("a", "p1.json", ttl_s=60.0))
            asyncio.run(api_cache.cached_blob_read("a", "p1.json", ttl_s=60.0))
            asyncio.run(api_cache.cached_blob_read("a", "p2.json", ttl_s=60.0))

        stats = api_cache.get_cache_stats()
        by_path = {p["path"]: p for p in stats["paths"]}
        assert by_path["p1.json"]["hits"] == 1
        assert by_path["p1.json"]["misses"] == 1
        assert by_path["p2.json"]["hits"] == 0
        assert by_path["p2.json"]["misses"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Endpoint counters
# ──────────────────────────────────────────────────────────────────────────────
class TestEndpointCounters:
    def test_record_increments(self) -> None:
        admin_stats.record_endpoint_hit("dashboard")
        admin_stats.record_endpoint_hit("dashboard")
        admin_stats.record_endpoint_hit("market")
        out = admin_stats.get_endpoint_counters()
        assert out == {"dashboard": 2, "market": 1}

    def test_returns_copy(self) -> None:
        admin_stats.record_endpoint_hit("a")
        d = admin_stats.get_endpoint_counters()
        d["a"] = 999
        # 원본은 변경 안 됨
        assert admin_stats.get_endpoint_counters()["a"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Cron status — Blob roundtrip
# ──────────────────────────────────────────────────────────────────────────────
class TestCronStatus:
    def test_record_cron_run_persists(self) -> None:
        saved: list[tuple] = []

        async def fake_load(account, path, *, default=None, credential=None):
            return default

        async def fake_save(account, path, payload, credential=None):
            saved.append((path, payload))

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load), \
             patch("services.vibe.blob_state.save_json", side_effect=fake_save):
            asyncio.run(admin_stats.record_cron_run(
                "acct", "market_snapshot", {"risk": 55, "gainers": 10},
            ))

        assert len(saved) == 1
        path, payload = saved[0]
        assert path == admin_stats.CRON_STATUS_PATH
        assert "market_snapshot" in payload["crons"]
        assert payload["crons"]["market_snapshot"]["result"]["risk"] == 55

    def test_record_cron_run_merges_with_existing(self) -> None:
        existing = {"crons": {"daily_signals": {"ts": "old", "result": {"ok": True}}}}
        saved: list[tuple] = []

        async def fake_load(account, path, *, default=None, credential=None):
            return existing

        async def fake_save(account, path, payload, credential=None):
            saved.append((path, payload))

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load), \
             patch("services.vibe.blob_state.save_json", side_effect=fake_save):
            asyncio.run(admin_stats.record_cron_run(
                "acct", "market_snapshot", {"risk": 60},
            ))

        payload = saved[0][1]
        # 기존 daily_signals 유지 + 새 market_snapshot 추가
        assert "daily_signals" in payload["crons"]
        assert "market_snapshot" in payload["crons"]

    def test_record_cron_run_swallows_save_failure(self) -> None:
        async def fake_load(account, path, *, default=None, credential=None):
            return None

        async def failing_save(account, path, payload, credential=None):
            raise RuntimeError("blob down")

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load), \
             patch("services.vibe.blob_state.save_json", side_effect=failing_save):
            # 예외 raise 안 되어야 함
            asyncio.run(admin_stats.record_cron_run(
                "acct", "market_snapshot", {"risk": 55},
            ))


# ──────────────────────────────────────────────────────────────────────────────
# build_admin_stats — aggregate
# ──────────────────────────────────────────────────────────────────────────────
class TestBuildAdminStats:
    def test_aggregates_all_sources(self) -> None:
        admin_stats.record_endpoint_hit("dashboard")
        admin_stats.record_endpoint_hit("market")
        admin_stats.record_endpoint_hit("market")

        async def fake_load(account, path, *, default=None, credential=None):
            if path == admin_stats.CRON_STATUS_PATH:
                return {"crons": {"market_snapshot": {"ts": "t1",
                                                       "result": {"risk": 55}}}}
            if path == "signals/latest.json":
                return {"as_of": "2026-06-06T00:00:00Z",
                        "ards": {"complex": [{"ticker": "AAPL"}]}}
            if path == "market/latest.json":
                return {"ts": "2026-06-06T18:00:00Z"}
            if path == "news/summary-latest.json":
                return {"ts": "2026-06-06T12:00:00Z",
                        "items": [{"id": "1"}, {"id": "2"}]}
            return default

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load):
            result = asyncio.run(admin_stats.build_admin_stats("acct"))

        assert result["endpoints"] == {"dashboard": 1, "market": 2}
        assert "market_snapshot" in result["crons"]
        assert result["artifacts"]["signals_size"] == 1
        assert result["artifacts"]["news_items"] == 2
        assert result["artifacts"]["market_ts"] == "2026-06-06T18:00:00Z"
        assert "cache" in result

    def test_handles_missing_artifacts(self) -> None:
        async def fake_load(account, path, *, default=None, credential=None):
            return default

        with patch("services.vibe.blob_state.load_json", side_effect=fake_load):
            result = asyncio.run(admin_stats.build_admin_stats("acct"))

        assert result["artifacts"]["signals_ts"] is None
        assert result["artifacts"]["news_items"] == 0
        assert result["crons"] == {}
