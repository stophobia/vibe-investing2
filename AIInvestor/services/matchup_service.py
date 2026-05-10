"""Matchup prediction engine.

Each KST hour we generate ≥3 matchups from yesterday's biggest movers:
  - "ss" stock vs stock     (top 2 stock movers)
  - "cc" coin vs coin       (top 2 crypto movers)
  - "sc" stock vs coin      (3rd stock × 3rd coin, mixed)

Each matchup has:
  - anchor_a / anchor_b   prices captured at open
  - last_a  / last_b      polled every 30 min for the gauge
  - resolve_at_kst        when winner is determined
                          (distributed +1 / +2 / +3 hours after open)

A user submits {matchup_id, side: "a"|"b"} before the deadline. At resolve
time the side with the larger pct change vs anchor wins. Correct predictors
get points credited via point_ledger.add_points.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal

from .movers_source import (
    CRYPTO_NAMES,
    Mover,
    MoversSnapshot,
    get_or_fetch_movers,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
MATCHUPS_PER_HOUR_FREE = 3           # visible to all users
MATCHUPS_PER_HOUR_PREMIUM = 10       # additional 7 require Premium subscription
MATCHUPS_PER_HOUR = MATCHUPS_PER_HOUR_PREMIUM  # generator creates the full 10
PREDICT_DEADLINE_MINUTES = 55        # picks lock 5 min before next hour rolls in
RESOLVE_OFFSET_HOURS = (1, 2, 3)     # rotate so result times are spread
PARTICIPATION_POINTS = 1
CORRECT_POINTS = 30                  # winner reward (single side)
GAUGE_TTL_MINUTES = 30               # how often we refresh gauge prices
CONTAINER = "matchups"


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────
MatchupType = Literal["ss", "cc", "sc"]
Side = Literal["a", "b"]


@dataclass
class AssetRef:
    ticker: str
    name: str
    kind: str            # "stock" | "crypto"
    yesterday_pct: float = 0.0


@dataclass
class Prediction:
    user_key: str        # internal — for crediting via point_ledger
    anon_user_id: str    # for display/leaderboard (no PII)
    side: Side
    submitted_at: str    # ISO UTC


@dataclass
class Matchup:
    id: str              # e.g. "2026-05-07-h14-m1"
    type: MatchupType
    asset_a: AssetRef
    asset_b: AssetRef
    open_at_kst: str     # ISO local KST timestamp
    deadline_kst: str
    resolve_at_kst: str
    anchor_a: float
    anchor_b: float
    last_a: float
    last_b: float
    last_polled_at: str  # ISO UTC; "" before first gauge poll
    status: str          # "open" | "resolved" | "void"
    winner: str          # "a" | "b" | "tie" | ""
    predictions: list[Prediction] = field(default_factory=list)
    created_at: str = ""
    resolved_at: str = ""
    premium_only: bool = False  # if True, only Supporter+ users can see/predict

    def gauge_pct(self) -> tuple[float, float]:
        """Return (gauge_a_pct, gauge_b_pct) summing to 100 (clamped 5..95)."""
        if self.anchor_a <= 0 or self.anchor_b <= 0:
            return 50.0, 50.0
        pa = (self.last_a - self.anchor_a) / self.anchor_a
        pb = (self.last_b - self.anchor_b) / self.anchor_b
        diff = pa - pb
        # Map ±5% spread to ±45 points around 50
        gauge_a = max(5.0, min(95.0, 50.0 + diff * 900.0))
        return gauge_a, 100.0 - gauge_a


# ─────────────────────────────────────────────────────────────────────────────
# Time helpers
# ─────────────────────────────────────────────────────────────────────────────
def _kst_now() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=9)


def _kst_today_iso() -> str:
    return _kst_now().date().isoformat()


def _kst_iso(dt: datetime) -> str:
    return dt.replace(tzinfo=None).isoformat(timespec="seconds")


# ─────────────────────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────────────────────
def _matchup_id(kst_date: str, hour: int, slot: int) -> str:
    return f"{kst_date}-h{hour:02d}-m{slot}"


def _seeded_rng(kst_date: str, hour: int) -> random.Random:
    h = hashlib.sha256(f"{kst_date}|{hour}".encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def _to_assetref(m: Mover) -> AssetRef:
    return AssetRef(
        ticker=m.ticker, name=m.name, kind=m.kind,
        yesterday_pct=m.pct_change,
    )


def generate_matchups_for_hour(snap: MoversSnapshot, kst_date: str,
                               hour: int) -> list[Matchup]:
    """Build up to 10 matchups for the given KST hour from a movers snapshot.

    First 3 (free for all): SS / CC / SC — rotates through top-6 movers per pool
    Next 7 (premium_only):
      - 4 SS pairs from stock pool (deeper rotation)
      - 2 CC pairs from crypto pool
      - 1 extra SC mixed pair

    All slots use deterministic seeded RNG so the same (date, hour) input
    yields the same matchups (so timer re-runs are idempotent).
    """
    rng = _seeded_rng(kst_date, hour)
    open_dt = _kst_now().replace(hour=hour, minute=0, second=0, microsecond=0)
    deadline_dt = open_dt + timedelta(minutes=PREDICT_DEADLINE_MINUTES)

    stock_pool = snap.stocks[:30]   # widened from 20 → 30 for premium variety
    crypto_pool = snap.cryptos[:25]
    if len(stock_pool) < 8 or len(crypto_pool) < 6:
        logger.warning("insufficient movers — stocks=%d cryptos=%d",
                       len(stock_pool), len(crypto_pool))

    used_tickers: set[str] = set()

    def _pair_distinct(pool: list[Mover], seed_offset: int
                       ) -> tuple[Mover, Mover] | None:
        """Pick 2 unused movers from pool (skips already-used tickers)."""
        if len(pool) < 2:
            return None
        candidates = [m for m in pool if m.ticker not in used_tickers]
        if len(candidates) < 2:
            return None
        rng2 = random.Random(rng.random() + seed_offset)
        idxs = list(range(len(candidates)))
        rng2.shuffle(idxs)
        return candidates[idxs[0]], candidates[idxs[1]]

    pairings: list[tuple[Mover, Mover, MatchupType, bool]] = []  # last = premium

    # ── 3 free slots ────────────────────────────────────────────────
    ss = _pair_distinct(stock_pool, 1)
    if ss:
        pairings.append((ss[0], ss[1], "ss", False))
        used_tickers.add(ss[0].ticker); used_tickers.add(ss[1].ticker)
    cc = _pair_distinct(crypto_pool, 2)
    if cc:
        pairings.append((cc[0], cc[1], "cc", False))
        used_tickers.add(cc[0].ticker); used_tickers.add(cc[1].ticker)
    if stock_pool and crypto_pool:
        # Mixed: pick mid-rank stock × mid-rank crypto
        sidx = (hour * 3) % min(len(stock_pool), 8)
        cidx = (hour * 5) % min(len(crypto_pool), 8)
        while sidx < len(stock_pool) and stock_pool[sidx].ticker in used_tickers:
            sidx += 1
        while cidx < len(crypto_pool) and crypto_pool[cidx].ticker in used_tickers:
            cidx += 1
        if sidx < len(stock_pool) and cidx < len(crypto_pool):
            s_m, c_m = stock_pool[sidx], crypto_pool[cidx]
            pairings.append((s_m, c_m, "sc", False))
            used_tickers.add(s_m.ticker); used_tickers.add(c_m.ticker)

    # ── 7 premium-only slots ───────────────────────────────────────────
    # 4 deeper SS, 2 deeper CC, 1 extra SC — all use unused tickers
    for i in range(4):
        ss_p = _pair_distinct(stock_pool, 10 + i)
        if ss_p is None:
            break
        pairings.append((ss_p[0], ss_p[1], "ss", True))
        used_tickers.add(ss_p[0].ticker); used_tickers.add(ss_p[1].ticker)
    for i in range(2):
        cc_p = _pair_distinct(crypto_pool, 20 + i)
        if cc_p is None:
            break
        pairings.append((cc_p[0], cc_p[1], "cc", True))
        used_tickers.add(cc_p[0].ticker); used_tickers.add(cc_p[1].ticker)
    # 1 more mixed
    if stock_pool and crypto_pool:
        s_avail = [m for m in stock_pool if m.ticker not in used_tickers]
        c_avail = [m for m in crypto_pool if m.ticker not in used_tickers]
        if s_avail and c_avail:
            rng3 = random.Random(rng.random() + 30)
            s_m = s_avail[rng3.randrange(len(s_avail))]
            c_m = c_avail[rng3.randrange(len(c_avail))]
            pairings.append((s_m, c_m, "sc", True))
            used_tickers.add(s_m.ticker); used_tickers.add(c_m.ticker)

    matchups: list[Matchup] = []
    for i, (a_m, b_m, mtype, premium) in enumerate(pairings):
        offset = RESOLVE_OFFSET_HOURS[i % len(RESOLVE_OFFSET_HOURS)]
        resolve_dt = open_dt + timedelta(hours=offset)
        m = Matchup(
            id=_matchup_id(kst_date, hour, i + 1),
            type=mtype,
            asset_a=_to_assetref(a_m),
            asset_b=_to_assetref(b_m),
            open_at_kst=_kst_iso(open_dt),
            deadline_kst=_kst_iso(deadline_dt),
            resolve_at_kst=_kst_iso(resolve_dt),
            anchor_a=a_m.last_close,
            anchor_b=b_m.last_close,
            last_a=a_m.last_close,
            last_b=b_m.last_close,
            last_polled_at="",
            status="open",
            winner="",
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            premium_only=premium,
        )
        matchups.append(m)

    return matchups


# ─────────────────────────────────────────────────────────────────────────────
# Repo
# ─────────────────────────────────────────────────────────────────────────────
def _blob_path(kst_date: str, matchup_id: str) -> str:
    return f"{kst_date}/{matchup_id}.json"


def _summary_path(kst_date: str) -> str:
    return f"{kst_date}/__summary.json"


async def _write_summary(svc, kst_date: str, matchups: list[Matchup]) -> None:
    """Rewrite the day's aggregate summary blob (single-roundtrip read path)."""
    payload = {
        "kst_date": kst_date,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "matchups": [_matchup_to_dict(m) for m in matchups],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    container = svc.get_container_client(CONTAINER)
    try:
        await container.create_container()
    except Exception:
        pass
    bc = container.get_blob_client(_summary_path(kst_date))
    try:
        await bc.upload_blob(body, overwrite=True)
    except Exception:
        logger.exception("matchup summary write failed for %s", kst_date)


async def _splice_into_summary(svc, kst_date: str, m: Matchup) -> None:
    """Read existing summary, replace/insert this matchup, write back.
    Used by single-matchup writes (predictions, individual gauge updates) so
    we don't clobber unrelated entries with a memory-only rebuild."""
    from azure.core.exceptions import ResourceNotFoundError
    bc = svc.get_blob_client(CONTAINER, _summary_path(kst_date))
    existing: list[dict] = []
    try:
        body = await (await bc.download_blob()).readall()
        existing = json.loads(body).get("matchups", [])
    except ResourceNotFoundError:
        pass
    except Exception:
        logger.warning("summary read failed (will re-create) for %s", kst_date)

    # Replace by id, or append
    target_id = m.id
    found = False
    new_entry = _matchup_to_dict(m)
    for i, e in enumerate(existing):
        if e.get("id") == target_id:
            existing[i] = new_entry
            found = True
            break
    if not found:
        existing.append(new_entry)

    payload = {
        "kst_date": kst_date,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "matchups": existing,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        await bc.upload_blob(body, overwrite=True)
    except Exception:
        logger.exception("matchup summary splice failed for %s/%s", kst_date, target_id)


def _matchup_to_dict(m: Matchup) -> dict:
    d = asdict(m)
    return d


def _dict_to_matchup(d: dict) -> Matchup:
    preds = [Prediction(**p) for p in d.get("predictions", [])]
    asset_a = AssetRef(**d["asset_a"])
    asset_b = AssetRef(**d["asset_b"])
    d2 = {**d, "predictions": preds, "asset_a": asset_a, "asset_b": asset_b}
    return Matchup(**d2)


class MatchupRepo:
    """Blob-backed matchup repo. Layout: matchups/<kst_date>/<id>.json."""

    def __init__(self, account_name: str, credential=None) -> None:
        self._account = account_name
        self._credential = credential
        self._memory: dict[str, Matchup] = {}  # id → matchup (warm cache)

    async def _client(self):
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = self._credential or DefaultAzureCredential()
        return BlobServiceClient(
            account_url=f"https://{self._account}.blob.core.windows.net",
            credential=creds,
        ), creds

    async def list_for_date(self, kst_date: str) -> list[Matchup]:
        """List all matchups for a KST date.

        Fast path: read the single `__summary.json` aggregate blob (one round-trip).
        Slow path (legacy / inconsistent state): list_blobs + parallel download
        every individual matchup file, then refresh the summary.
        """
        from azure.core.exceptions import ResourceNotFoundError
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = self._credential or DefaultAzureCredential()
        results: list[Matchup] = []
        try:
            async with BlobServiceClient(
                account_url=f"https://{self._account}.blob.core.windows.net",
                credential=creds,
            ) as svc:
                # Tier 1 — single summary blob (~50ms)
                summary_client = svc.get_blob_client(CONTAINER, _summary_path(kst_date))
                try:
                    body = await (await summary_client.download_blob()).readall()
                    arr = json.loads(body).get("matchups", [])
                    for d in arr:
                        results.append(_dict_to_matchup(d))
                    if results:
                        for m in results:
                            self._memory[m.id] = m
                        return results
                except ResourceNotFoundError:
                    pass  # Fall through to slow path

                # Tier 2 — parallel scan of individual blobs
                container = svc.get_container_client(CONTAINER)
                try:
                    await container.create_container()
                except Exception:
                    pass
                blob_names: list[str] = []
                async for blob in container.list_blobs(name_starts_with=f"{kst_date}/"):
                    if blob.name.endswith("__summary.json"):
                        continue
                    blob_names.append(blob.name)

                async def _fetch(name: str) -> Matchup | None:
                    try:
                        bc = container.get_blob_client(name)
                        body = await (await bc.download_blob()).readall()
                        return _dict_to_matchup(json.loads(body))
                    except Exception:
                        return None

                # Bounded parallel — 8 concurrent reads
                sem = asyncio.Semaphore(8)
                async def _bounded(name: str) -> Matchup | None:
                    async with sem:
                        return await _fetch(name)
                fetched = await asyncio.gather(*[_bounded(n) for n in blob_names])
                results = [m for m in fetched if m is not None]

                # Rewrite the summary so next read uses Tier 1
                if results:
                    await _write_summary(svc, kst_date, results)
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()
        for m in results:
            self._memory[m.id] = m
        return results

    async def get(self, matchup_id: str) -> Matchup | None:
        if matchup_id in self._memory:
            return self._memory[matchup_id]
        from azure.core.exceptions import ResourceNotFoundError
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        kst_date = matchup_id.split("-h")[0]  # "2026-05-07-h14-m1" → "2026-05-07"
        creds = self._credential or DefaultAzureCredential()
        try:
            async with BlobServiceClient(
                account_url=f"https://{self._account}.blob.core.windows.net",
                credential=creds,
            ) as svc:
                bc = svc.get_blob_client(CONTAINER, _blob_path(kst_date, matchup_id))
                try:
                    body = await (await bc.download_blob()).readall()
                except ResourceNotFoundError:
                    return None
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()
        m = _dict_to_matchup(json.loads(body))
        self._memory[m.id] = m
        return m

    async def put(self, matchup: Matchup, *, refresh_summary: bool = True) -> None:
        """Persist a single matchup. By default also refreshes the day's
        __summary.json aggregate so the read path stays at one blob.

        Pass refresh_summary=False when bulk-writing (caller flushes summary
        once at the end via put_many())."""
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        kst_date = matchup.id.split("-h")[0]
        body = json.dumps(_matchup_to_dict(matchup), ensure_ascii=False).encode("utf-8")
        creds = self._credential or DefaultAzureCredential()
        try:
            async with BlobServiceClient(
                account_url=f"https://{self._account}.blob.core.windows.net",
                credential=creds,
            ) as svc:
                container = svc.get_container_client(CONTAINER)
                try:
                    await container.create_container()
                except Exception:
                    pass
                bc = container.get_blob_client(_blob_path(kst_date, matchup.id))
                await bc.upload_blob(body, overwrite=True)
                self._memory[matchup.id] = matchup
                if refresh_summary:
                    # Read-modify-write: keeps summary consistent without
                    # depending on in-memory completeness across processes.
                    await _splice_into_summary(svc, kst_date, matchup)
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()


# ─────────────────────────────────────────────────────────────────────────────
# Generator entrypoint (timer-callable)
# ─────────────────────────────────────────────────────────────────────────────
async def ensure_matchups_for_hour(repo: MatchupRepo, account_name: str,
                                   kst_date: str | None = None,
                                   hour: int | None = None,
                                   credential=None) -> list[Matchup]:
    """If matchups for this hour already exist, return them. Else generate + persist."""
    if kst_date is None:
        kst_date = _kst_today_iso()
    if hour is None:
        hour = _kst_now().hour

    existing = [m for m in await repo.list_for_date(kst_date)
                if m.id.startswith(_matchup_id(kst_date, hour, 0)[:-1])]
    if len(existing) >= MATCHUPS_PER_HOUR:
        return existing[:MATCHUPS_PER_HOUR]

    snap = await get_or_fetch_movers(account_name, credential=credential)
    new_ms = generate_matchups_for_hour(snap, kst_date, hour)
    for m in new_ms:
        await repo.put(m)
    return new_ms


# ─────────────────────────────────────────────────────────────────────────────
# Submit
# ─────────────────────────────────────────────────────────────────────────────
async def submit_prediction(repo: MatchupRepo, matchup_id: str,
                            user_key: str, anon_user_id: str,
                            side: Side, *,
                            is_premium: bool = False) -> tuple[bool, str]:
    """Submit a prediction. Returns (ok, reason).

    Reasons: "ok" | "not_found" | "deadline_passed" | "already_submitted" |
             "invalid_side" | "premium_only"
    """
    if side not in ("a", "b"):
        return False, "invalid_side"

    m = await repo.get(matchup_id)
    if m is None:
        return False, "not_found"
    if m.status != "open":
        return False, "deadline_passed"

    # Premium gate: free users cannot submit on premium-only matchups
    if m.premium_only and not is_premium:
        return False, "premium_only"

    try:
        deadline = datetime.fromisoformat(m.deadline_kst)
        now_naive_kst = _kst_now().replace(tzinfo=None)
        if now_naive_kst >= deadline:
            return False, "deadline_passed"
    except ValueError:
        return False, "deadline_passed"

    if any(p.user_key == user_key for p in m.predictions):
        return False, "already_submitted"

    m.predictions.append(Prediction(
        user_key=user_key,
        anon_user_id=anon_user_id,
        side=side,
        submitted_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    ))
    await repo.put(m)
    return True, "ok"


# ─────────────────────────────────────────────────────────────────────────────
# Gauge update
# ─────────────────────────────────────────────────────────────────────────────
async def _fetch_spot(ticker: str) -> float | None:
    """Fetch latest spot price via yfinance (sync, wrapped)."""
    def _sync() -> float | None:
        import yfinance as yf
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1d", interval="5m", auto_adjust=False)
            if len(hist) > 0:
                return float(hist["Close"].iloc[-1])
            info = t.info
            for k in ("regularMarketPrice", "currentPrice", "previousClose"):
                v = info.get(k)
                if isinstance(v, (int, float)) and v > 0:
                    return float(v)
        except Exception:
            return None
        return None
    return await asyncio.to_thread(_sync)


async def update_gauges(repo: MatchupRepo, kst_date: str | None = None) -> int:
    """Refresh `last_a`/`last_b` for every open matchup. Returns count updated."""
    if kst_date is None:
        kst_date = _kst_today_iso()
    matchups = await repo.list_for_date(kst_date)
    open_ms = [m for m in matchups if m.status == "open"]
    if not open_ms:
        return 0

    # Dedup tickers across matchups
    tickers = {m.asset_a.ticker for m in open_ms} | {m.asset_b.ticker for m in open_ms}
    sem = asyncio.Semaphore(4)
    prices: dict[str, float] = {}

    async def _one(t: str) -> None:
        async with sem:
            p = await _fetch_spot(t)
            if p is not None and p > 0:
                prices[t] = p

    await asyncio.gather(*[_one(t) for t in tickers])

    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated = 0
    for m in open_ms:
        a = prices.get(m.asset_a.ticker)
        b = prices.get(m.asset_b.ticker)
        if a is None or b is None:
            continue
        m.last_a = a
        m.last_b = b
        m.last_polled_at = now_iso
        await repo.put(m)
        updated += 1
    return updated


# ─────────────────────────────────────────────────────────────────────────────
# Resolve
# ─────────────────────────────────────────────────────────────────────────────
async def resolve_due_matchups(
    repo: MatchupRepo,
    profile_repo,
    *,
    kst_date: str | None = None,
    usage_logger=None,
) -> dict[str, int]:
    """Resolve matchups whose resolve_at_kst is in the past. Returns
    {matchup_id: winners_credited}.
    """
    from .point_ledger import add_points
    if kst_date is None:
        kst_date = _kst_today_iso()
    now_naive_kst = _kst_now().replace(tzinfo=None)

    matchups = await repo.list_for_date(kst_date)
    due = []
    for m in matchups:
        if m.status != "open":
            continue
        try:
            if datetime.fromisoformat(m.resolve_at_kst) <= now_naive_kst:
                due.append(m)
        except ValueError:
            continue

    summary: dict[str, int] = {}
    for m in due:
        # Get final spot prices
        a = await _fetch_spot(m.asset_a.ticker)
        b = await _fetch_spot(m.asset_b.ticker)
        if a is not None and a > 0:
            m.last_a = a
        if b is not None and b > 0:
            m.last_b = b

        pa = (m.last_a - m.anchor_a) / m.anchor_a if m.anchor_a > 0 else 0
        pb = (m.last_b - m.anchor_b) / m.anchor_b if m.anchor_b > 0 else 0
        if abs(pa - pb) < 1e-6:
            m.winner = "tie"
        else:
            m.winner = "a" if pa > pb else "b"
        m.status = "resolved"
        m.resolved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        # Credit correct predictors
        winners = 0
        if m.winner in ("a", "b"):
            for p in m.predictions:
                if p.side == m.winner:
                    try:
                        await add_points(
                            profile_repo, p.user_key, CORRECT_POINTS,
                            reason="matchup_correct", ref=m.id,
                            usage_logger=usage_logger,
                        )
                        winners += 1
                    except Exception:
                        logger.exception("credit failed for %s on %s",
                                         p.anon_user_id, m.id)
        await repo.put(m)
        summary[m.id] = winners
    return summary
