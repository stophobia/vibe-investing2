"""§News — pure helper + orchestration tests for news_service.

IO seams (_fetch_finnhub_news, _load_processed_ids_for_date, _save_processed_ids,
_summarize_with_deepseek, _post_to_cf_worker) are monkey-patched per test —
no real Finnhub / DeepSeek / Blob / CF round-trip ever occurs.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from datetime import datetime
from types import SimpleNamespace

import pytest

from services import news_service as ns


# ──────────────────────────────────────────────────────────────────────────────
# Pure-helper tests
# ──────────────────────────────────────────────────────────────────────────────
class TestSignPayload:
    def test_deterministic(self) -> None:
        a = ns._sign_payload("secret", "1700000000", b'{"a":1}')
        b = ns._sign_payload("secret", "1700000000", b'{"a":1}')
        assert a == b
        # Round-trip against stdlib for absolute correctness
        expected = hmac.new(b"secret", b"1700000000." + b'{"a":1}',
                            hashlib.sha256).hexdigest()
        assert a == expected

    def test_changes_with_ts(self) -> None:
        a = ns._sign_payload("secret", "1700000000", b'{"a":1}')
        b = ns._sign_payload("secret", "1700000001", b'{"a":1}')
        assert a != b

    def test_changes_with_body(self) -> None:
        a = ns._sign_payload("secret", "1700000000", b'{"a":1}')
        b = ns._sign_payload("secret", "1700000000", b'{"a":2}')
        assert a != b

    def test_changes_with_secret(self) -> None:
        a = ns._sign_payload("s1", "1700000000", b'{"a":1}')
        b = ns._sign_payload("s2", "1700000000", b'{"a":1}')
        assert a != b


class TestProcessedBlobPath:
    def test_format(self) -> None:
        assert ns._processed_blob_path("2026-05-07") == "processed/2026-05-07.json"


class TestKstDateStr:
    def test_explicit_dt(self) -> None:
        # UTC midnight = KST 09:00 same date
        dt = datetime(2026, 5, 7, 0, 0, 0, tzinfo=ns.KST)
        assert ns._kst_date_str(dt) == "2026-05-07"


class TestParseSummaryJson:
    def test_valid(self) -> None:
        out = ns._parse_summary_json('{"market_summary":"ok","items":[{"id":"1"}]}')
        assert out["market_summary"] == "ok"
        assert out["items"] == [{"id": "1"}]

    def test_malformed_returns_empty_shell(self) -> None:
        out = ns._parse_summary_json("not json {{{")
        assert out == {"market_summary": "", "items": []}

    def test_non_dict_returns_empty_shell(self) -> None:
        out = ns._parse_summary_json("[1,2,3]")
        assert out == {"market_summary": "", "items": []}

    def test_missing_items_key_filled(self) -> None:
        out = ns._parse_summary_json('{"market_summary":"x"}')
        assert out["items"] == []

    def test_items_not_list_replaced(self) -> None:
        out = ns._parse_summary_json('{"items":"oops"}')
        assert out["items"] == []


class TestBuildUserPrompt:
    def test_includes_schema_keywords(self) -> None:
        prompt = ns._build_user_prompt([
            {"id": "abc", "headline": "Fed pauses", "summary": "Powell said...",
             "source": "Reuters", "category": "general", "related": "SPY"},
        ])
        assert "market_summary" in prompt
        assert "title_ko" in prompt
        assert "summary_ko" in prompt
        # Category vocabulary explicitly named
        assert "거시경제" in prompt and "반도체" in prompt
        # No-opinion clause
        assert "투자조언" in prompt
        # Item rendered as JSON line
        assert "Fed pauses" in prompt
        assert "abc" in prompt

    def test_truncates_long_headline_and_summary(self) -> None:
        big_headline = "X" * 1000
        big_summary = "Y" * 2000
        prompt = ns._build_user_prompt([
            {"id": "1", "headline": big_headline, "summary": big_summary},
        ])
        # 240 cap on headline, 600 on summary
        assert prompt.count("X") <= 240
        assert prompt.count("Y") <= 600


class TestMergeSummaryWithOriginals:
    def _orig(self, rid: str, **extra) -> dict:
        return {"id": rid, "datetime": 1700000000, "source": "Reuters",
                "url": "https://x", **extra}

    def test_keeps_matching_ids(self) -> None:
        originals = {"1": self._orig("1"), "2": self._orig("2")}
        summary = {"items": [
            {"id": "1", "title_ko": "T1", "summary_ko": "S1",
             "category": "거시경제", "tickers": ["SPY"]},
            {"id": "2", "title_ko": "T2", "summary_ko": "S2",
             "category": "AI", "tickers": []},
        ]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert len(out) == 2
        assert out[0]["id"] == "1"
        assert out[0]["title_ko"] == "T1"
        assert out[0]["source"] == "Reuters"
        assert out[0]["ts"] == 1700000000

    def test_drops_invented_ids(self) -> None:
        originals = {"1": self._orig("1")}
        summary = {"items": [
            {"id": "1", "title_ko": "T1", "summary_ko": "S1",
             "category": "AI", "tickers": []},
            {"id": "hallucinated", "title_ko": "X", "summary_ko": "X",
             "category": "AI", "tickers": []},
        ]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert len(out) == 1
        assert out[0]["id"] == "1"

    def test_invalid_category_falls_back_to_기타(self) -> None:
        originals = {"1": self._orig("1")}
        summary = {"items": [{"id": "1", "title_ko": "T", "summary_ko": "S",
                              "category": "WeirdMade UpCat", "tickers": []}]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert out[0]["category"] == "기타"

    def test_tickers_clamped_to_8(self) -> None:
        originals = {"1": self._orig("1")}
        summary = {"items": [{"id": "1", "title_ko": "T", "summary_ko": "S",
                              "category": "AI",
                              "tickers": [f"T{i}" for i in range(20)]}]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert len(out[0]["tickers"]) == 8

    def test_non_list_tickers_becomes_empty(self) -> None:
        originals = {"1": self._orig("1")}
        summary = {"items": [{"id": "1", "title_ko": "T", "summary_ko": "S",
                              "category": "AI", "tickers": "NVDA"}]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert out[0]["tickers"] == []

    def test_skips_non_dict_items(self) -> None:
        originals = {"1": self._orig("1")}
        summary = {"items": ["junk", None, {"id": "1", "title_ko": "T",
                                            "summary_ko": "S", "category": "AI",
                                            "tickers": []}]}
        out = ns._merge_summary_with_originals(summary, originals)
        assert len(out) == 1


# ──────────────────────────────────────────────────────────────────────────────
# Orchestration tests (monkey-patch IO seams)
# ──────────────────────────────────────────────────────────────────────────────
def _mk_config(**overrides) -> SimpleNamespace:
    base = dict(
        finnhub_key="finn-key",
        cf_ingest_url="https://w.example.workers.dev/ingest",
        ingest_secret="secret",
        storage_account_name="acct",
        deepseek_api_key="dk",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_model="deepseek-chat",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _mk_item(rid: str, headline: str = "h", ts: int = 1700000000) -> dict:
    return {"id": rid, "headline": headline, "summary": "s", "source": "Reuters",
            "url": f"https://x/{rid}", "category": "general", "related": "",
            "datetime": ts}


class _IOTracker:
    """Captures which IO seams were exercised, with what arguments."""

    def __init__(self) -> None:
        self.fetched: bool = False
        self.loaded_dates: list[str] = []
        self.saved: list[tuple[str, set[str]]] = []
        self.deepseek_called: bool = False
        self.cf_calls: list[dict] = []


@pytest.fixture
def io_patch(monkeypatch):
    """Returns (tracker, configure) — configure(...) wires the seams."""
    tracker = _IOTracker()

    def configure(*, fetch_items: list[dict], processed_today: set[str] | None = None,
                  processed_yesterday: set[str] | None = None,
                  summary: dict | None = None, cf_status: int = 200,
                  fetch_raises: bool = False, deepseek_raises: bool = False,
                  cf_raises: bool = False) -> None:
        processed_today = processed_today or set()
        processed_yesterday = processed_yesterday or set()

        async def fake_fetch(api_key):
            tracker.fetched = True
            if fetch_raises:
                raise RuntimeError("simulated finnhub failure")
            return fetch_items

        async def fake_load(account, date_str):
            tracker.loaded_dates.append(date_str)
            # Last loaded date in list is typically yesterday; just pick by membership
            if date_str == tracker.loaded_dates[0]:  # first call = today
                return set(processed_today)
            return set(processed_yesterday)

        async def fake_save(account, date_str, ids):
            tracker.saved.append((date_str, set(ids)))

        async def fake_deepseek(api_key, base_url, model, items):
            tracker.deepseek_called = True
            if deepseek_raises:
                raise RuntimeError("simulated deepseek failure")
            if summary is not None:
                return summary
            # Default: echo back every item with all required LLM-side fields
            return {"market_summary": "오늘은 별 일 없었다.", "items": [
                {"id": str(it["id"]), "title_ko": "제목", "summary_ko": "요약",
                 "category": "AI", "tickers": []}
                for it in items
            ]}

        async def fake_post(url, secret, payload):
            tracker.cf_calls.append({"url": url, "payload": payload})
            if cf_raises:
                raise RuntimeError("simulated cf failure")
            return cf_status, "ok"

        monkeypatch.setattr(ns, "_fetch_finnhub_news", fake_fetch)
        monkeypatch.setattr(ns, "_load_processed_ids_for_date", fake_load)
        monkeypatch.setattr(ns, "_save_processed_ids", fake_save)
        monkeypatch.setattr(ns, "_summarize_with_deepseek", fake_deepseek)
        monkeypatch.setattr(ns, "_post_to_cf_worker", fake_post)

    return tracker, configure


class TestOrchestrator:
    def test_skips_when_missing_config(self) -> None:
        result = asyncio.run(ns.collect_and_post_news(_mk_config(finnhub_key="")))
        assert result == {"skipped": "missing-config"}

    def test_skips_when_missing_storage(self) -> None:
        result = asyncio.run(ns.collect_and_post_news(_mk_config(storage_account_name="")))
        assert result == {"skipped": "missing-storage"}

    def test_no_new_items_short_circuits(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a"), _mk_item("b")],
                  processed_today={"a", "b"})
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["new"] == 0
        assert result["skipped"] == "no-new-items"
        assert tracker.fetched
        # Cost guards: DeepSeek + CF never touched
        assert not tracker.deepseek_called
        assert tracker.cf_calls == []
        assert tracker.saved == []

    def test_yesterday_dedup_prevents_midnight_double_send(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a"), _mk_item("b")],
                  processed_yesterday={"a", "b"})
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["skipped"] == "no-new-items"
        assert not tracker.deepseek_called

    def test_full_flow_success_saves_processed(self, io_patch) -> None:
        tracker, configure = io_patch
        items = [_mk_item("a"), _mk_item("b"), _mk_item("c")]
        configure(fetch_items=items, cf_status=200)
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["new"] == 3
        assert result["sent"] == 3
        assert result["cf_status"] == 200
        assert "error" not in result
        assert len(tracker.cf_calls) == 1
        sent = tracker.cf_calls[0]["payload"]
        assert sent["market_summary"]
        assert len(sent["items"]) == 3
        assert "ts" in sent
        assert len(tracker.saved) == 1
        saved_date, saved_ids = tracker.saved[0]
        assert saved_ids == {"a", "b", "c"}
        assert saved_date == tracker.loaded_dates[0]

    def test_cf_non_2xx_does_not_save(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a")], cf_status=500)
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["cf_status"] == 500
        assert result["error"] == "cf-500"
        assert tracker.saved == []  # critical: no save → next cron retries

    def test_finnhub_failure_reported_no_save(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[], fetch_raises=True)
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["error"] == "finnhub-fetch"
        assert not tracker.deepseek_called
        assert tracker.cf_calls == []

    def test_deepseek_failure_reported_no_save(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a")], deepseek_raises=True)
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["error"] == "deepseek-failed"
        assert tracker.cf_calls == []
        assert tracker.saved == []

    def test_empty_llm_output_skips_cf(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a")],
                  summary={"market_summary": "", "items": []})
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["skipped"] == "empty-summary"
        assert tracker.cf_calls == []
        assert tracker.saved == []

    def test_cf_call_exception_reported_no_save(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a")], cf_raises=True)
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["error"] == "cf-post"
        assert tracker.saved == []

    def test_payload_only_includes_known_categories(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(
            fetch_items=[_mk_item("a")],
            summary={"market_summary": "x", "items": [
                {"id": "a", "title_ko": "T", "summary_ko": "S",
                 "category": "Politics", "tickers": []},
            ]},
        )
        asyncio.run(ns.collect_and_post_news(_mk_config()))
        sent = tracker.cf_calls[0]["payload"]
        assert sent["items"][0]["category"] == "기타"

    def test_only_processes_unseen(self, io_patch) -> None:
        tracker, configure = io_patch
        configure(fetch_items=[_mk_item("a"), _mk_item("b"), _mk_item("c")],
                  processed_today={"a"}, processed_yesterday={"c"})
        result = asyncio.run(ns.collect_and_post_news(_mk_config()))
        assert result["new"] == 1
        sent = tracker.cf_calls[0]["payload"]
        assert {it["id"] for it in sent["items"]} == {"b"}
        # Save adds the new ID to the existing today set (a + b)
        assert tracker.saved[0][1] == {"a", "b"}
