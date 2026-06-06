"""§Vibe — API 메모리 캐시.

기존 AIInvestor 정책과 동일 패턴:
  - module-level dict 에 (timestamp, payload) 저장
  - TTL 내 hit 면 Blob round-trip 생략
  - cron 이 Blob 쓰기 → endpoint 가 읽기 — 단방향 흐름

instance scaling 시 instance 별 별도 캐시 (stampede 무해, worst case Blob 1회/5분).
"""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable


class _Memo:
    __slots__ = ("ttl_s", "_t", "_payload", "hits", "misses")

    def __init__(self, ttl_s: float) -> None:
        self.ttl_s = float(ttl_s)
        self._t = 0.0
        self._payload: Any = None
        self.hits = 0     # per-instance 누적 (재시작 시 리셋)
        self.misses = 0

    def is_fresh(self) -> bool:
        return self._payload is not None and (time.monotonic() - self._t) < self.ttl_s

    def get(self) -> Any:
        return self._payload

    def set(self, payload: Any) -> None:
        self._t = time.monotonic()
        self._payload = payload

    def invalidate(self) -> None:
        self._t = 0.0
        self._payload = None

    def record_hit(self) -> None:
        self.hits += 1

    def record_miss(self) -> None:
        self.misses += 1


# Endpoint-별 memo 인스턴스. 키 = blob path.
_MEMOS: dict[str, _Memo] = {}


def memo_for(path: str, ttl_s: float = 60.0) -> _Memo:
    """경로별 싱글톤 _Memo. 첫 호출에 ttl 결정 (이후 재사용)."""
    m = _MEMOS.get(path)
    if m is None:
        m = _Memo(ttl_s)
        _MEMOS[path] = m
    return m


async def cached_blob_read(
    account_name: str,
    path: str,
    ttl_s: float = 60.0,
    *,
    default: Any = None,
) -> Any:
    """Blob JSON 을 memo 통해 캐싱. fresh → memo, else → Blob fetch + memo set."""
    from . import blob_state

    memo = memo_for(path, ttl_s)
    if memo.is_fresh():
        memo.record_hit()
        return memo.get()
    memo.record_miss()
    payload = await blob_state.load_json(account_name, path, default=default)
    if payload is not None:
        memo.set(payload)
    return payload


def get_cache_stats() -> dict[str, Any]:
    """Per-path hit/miss counter + ratio. Dashboard 통계 섹션이 폴링."""
    paths: list[dict[str, Any]] = []
    total_hits = 0
    total_misses = 0
    for path, memo in _MEMOS.items():
        h, m = memo.hits, memo.misses
        total = h + m
        ratio = (h / total) if total else 0.0
        paths.append({
            "path": path,
            "hits": h,
            "misses": m,
            "ratio": round(ratio, 4),
            "ttl_s": memo.ttl_s,
            "is_fresh": memo.is_fresh(),
        })
        total_hits += h
        total_misses += m
    total = total_hits + total_misses
    return {
        "paths": paths,
        "total_hits": total_hits,
        "total_misses": total_misses,
        "total_ratio": round((total_hits / total) if total else 0.0, 4),
    }
