"""Donation intent + verification service.

Flow:
  1. User picks an amount tier and a chain (TON | TRON).
  2. We create a DonationIntent (blob-persisted) with:
       - TON: a unique short comment string (memo) the user includes in the TX
       - TRON: an amount fingerprint (e.g. 50.000731 — last 6 fractional
               digits encode the intent_id), since TRC20 has no native memo
  3. UI shows the wallet address + memo / fingerprint-amount + QR.
  4. A 5-min cron polls both wallets for new incoming TXs and matches them
     against pending intents. On match → credit points + mark confirmed.

Wallet addresses (immutable, set in code so users see the same address every time):
  - TON  USDT (Jetton USD₮): UQBt20bDOUdAyTYPi-L3rsEj7wBf95yBq0Bo5MjRGE-3ScqV
  - TRON USDT (TRC20):       TJBgCbnCog8KugCrc6Mb8wwTbDPowK18rc

USDT amount tiers and corresponding point credits.
The 1-USDT entry exists so first-time donors can verify the flow cheaply.
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
WALLET_TON = "UQBt20bDOUdAyTYPi-L3rsEj7wBf95yBq0Bo5MjRGE-3ScqV"
WALLET_TRON = "TJBgCbnCog8KugCrc6Mb8wwTbDPowK18rc"

# 1 USDT = 100 P (matches §gamification scale: hourly_bet = 30 P, premium_1d = 1000 P)
POINTS_PER_USDT = 100

# Allowed amount tiers per spec
AMOUNT_TIERS = (1, 10, 50, 100, 500, 1000)

# Intent expires after 24h if unmatched
INTENT_TTL_HOURS = 24

# Polling cadence — every 5 min
POLL_INTERVAL_MIN = 5

CONTAINER = "donation-intents"

Chain = Literal["ton", "tron"]


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class DonationIntent:
    intent_id: str           # 8-char base32 (e.g. "K3F7A2QM")
    user_key: str            # internal — for credit
    anon_user_id: str        # for telemetry
    amount_usdt: float       # face amount user picks (1, 10, ...)
    expected_amount: float   # what we look for on-chain (TON=face, TRON=fingerprint)
    chain: Chain
    wallet_address: str
    memo: str                # TON: comment string user must include; TRON: ""
    fingerprint_suffix: str  # TRON: last fractional digits; TON: ""
    points_to_credit: int
    status: str              # "pending" | "confirmed" | "expired"
    created_at: str
    expires_at: str
    confirmed_tx_hash: str = ""
    confirmed_at: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def points_for(amount_usdt: float) -> int:
    return int(round(amount_usdt * POINTS_PER_USDT))


def _gen_intent_id() -> str:
    """8-char URL-safe id, uppercase letters + digits (no I/O/0/1)."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))


def _intent_to_fingerprint(intent_id: str) -> str:
    """Map an intent_id to a 4-digit numeric fingerprint suffix for TRON.

    Range 0001..9999 → adds at most $0.009999 to the face amount (negligible
    cost, easy to display, and still ≥9000 simultaneous open intents).
    """
    import hashlib
    h = hashlib.sha256(intent_id.encode()).hexdigest()
    n = (int(h[:8], 16) % 9999) + 1
    return f"{n:04d}"


def _fingerprint_to_amount(amount_usdt: float, fingerprint_suffix: str) -> float:
    """Combine a face amount with the fingerprint as 6-decimal USDT.

    e.g. (50, "0731") → 50.000731  (suffix lives in the last 4 of 6 decimals).
    """
    return round(amount_usdt + int(fingerprint_suffix) / 1_000_000, 6)


# ─────────────────────────────────────────────────────────────────────────────
# Intent creation
# ─────────────────────────────────────────────────────────────────────────────
def build_intent(*, user_key: str, anon_user_id: str,
                 amount_usdt: float, chain: Chain) -> DonationIntent:
    if amount_usdt not in AMOUNT_TIERS:
        raise ValueError(f"amount must be one of {AMOUNT_TIERS}")
    if chain not in ("ton", "tron"):
        raise ValueError(f"chain must be 'ton' or 'tron'")

    intent_id = _gen_intent_id()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=INTENT_TTL_HOURS)

    if chain == "ton":
        memo = f"vinv-{intent_id}"
        wallet = WALLET_TON
        expected = float(amount_usdt)
        fingerprint = ""
    else:
        # TRC20 has no memo — fingerprint via amount fractional digits
        fingerprint = _intent_to_fingerprint(intent_id)
        expected = _fingerprint_to_amount(amount_usdt, fingerprint)
        wallet = WALLET_TRON
        memo = ""

    return DonationIntent(
        intent_id=intent_id,
        user_key=user_key,
        anon_user_id=anon_user_id,
        amount_usdt=float(amount_usdt),
        expected_amount=expected,
        chain=chain,
        wallet_address=wallet,
        memo=memo,
        fingerprint_suffix=fingerprint,
        points_to_credit=points_for(amount_usdt),
        status="pending",
        created_at=now.isoformat(timespec="seconds"),
        expires_at=expires.isoformat(timespec="seconds"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Repo
# ─────────────────────────────────────────────────────────────────────────────
def _blob_path(intent_id: str) -> str:
    return f"{intent_id}.json"


class DonationIntentRepo:
    """Blob-backed donation intent store."""

    def __init__(self, account_name: str, credential=None) -> None:
        self._account = account_name
        self._credential = credential
        self._memory: dict[str, DonationIntent] = {}

    async def put(self, intent: DonationIntent) -> None:
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = self._credential or DefaultAzureCredential()
        body = json.dumps(asdict(intent), ensure_ascii=False).encode("utf-8")
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
                bc = container.get_blob_client(_blob_path(intent.intent_id))
                await bc.upload_blob(body, overwrite=True)
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()
        self._memory[intent.intent_id] = intent

    async def get(self, intent_id: str) -> DonationIntent | None:
        if intent_id in self._memory:
            return self._memory[intent_id]
        from azure.core.exceptions import ResourceNotFoundError
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = self._credential or DefaultAzureCredential()
        try:
            async with BlobServiceClient(
                account_url=f"https://{self._account}.blob.core.windows.net",
                credential=creds,
            ) as svc:
                bc = svc.get_blob_client(CONTAINER, _blob_path(intent_id))
                try:
                    body = await (await bc.download_blob()).readall()
                except ResourceNotFoundError:
                    return None
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()
        d = json.loads(body)
        intent = DonationIntent(**d)
        self._memory[intent_id] = intent
        return intent

    async def list_pending(self) -> list[DonationIntent]:
        """List all currently-pending intents (scan)."""
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = self._credential or DefaultAzureCredential()
        out: list[DonationIntent] = []
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
                async for blob in container.list_blobs():
                    bc = container.get_blob_client(blob.name)
                    body = await (await bc.download_blob()).readall()
                    intent = DonationIntent(**json.loads(body))
                    if intent.status == "pending":
                        out.append(intent)
        finally:
            if self._credential is None and hasattr(creds, "close"):
                await creds.close()
        return out


# ─────────────────────────────────────────────────────────────────────────────
# Verification (matching incoming TXs to pending intents)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class IncomingTx:
    tx_hash: str
    amount_usdt: float       # parsed amount (handles 6-decimal USDT)
    memo: str                # extracted comment (TON only — TRON empty)
    chain: Chain
    seen_at: str             # ISO


def amount_matches(intent: DonationIntent, tx_amount: float) -> bool:
    """For TON: face amount within ±0.001. For TRON: exact fingerprint match (±0.000_001)."""
    if intent.chain == "ton":
        return abs(tx_amount - intent.expected_amount) <= 0.001
    # TRON: must match to the 6th decimal
    return abs(tx_amount - intent.expected_amount) <= 0.000_002


def memo_matches(intent: DonationIntent, tx_memo: str) -> bool:
    if intent.chain != "ton":
        return True  # TRON doesn't use memo — amount fingerprint is the key
    return intent.memo.strip().lower() in (tx_memo or "").strip().lower()


def find_match(pending: list[DonationIntent], tx: IncomingTx) -> DonationIntent | None:
    """Return the first matching intent or None."""
    candidates = [i for i in pending if i.chain == tx.chain]
    if tx.chain == "ton":
        # Prefer memo match
        for i in candidates:
            if memo_matches(i, tx.memo) and amount_matches(i, tx.amount_usdt):
                return i
        return None
    # TRON: amount-fingerprint
    for i in candidates:
        if amount_matches(i, tx.amount_usdt):
            return i
    return None


async def check_intent_now(repo: "DonationIntentRepo", profile_repo,
                           intent: DonationIntent,
                           *, ton_client=None, tron_client=None,
                           tx_hash: str = "",
                           usage_logger=None) -> dict:
    """Manually trigger verification for ONE intent. Bypasses the 5-min cron.

    If `tx_hash` is provided, relaxes the matching rules:
      - We confirm the intent if a recent incoming-USDT TX to our wallet has
        that exact tx_hash (memo / fingerprint mismatches are tolerated).
      - This is the user's escape hatch when TRON fingerprint or TON memo
        was forgotten / mistyped.
    Without `tx_hash`, the standard memo + amount (TON) or fingerprint-amount
    (TRON) matching applies — same as the cron path.

    Returns dict: {"success": bool, "reason": str, "points_credited"?: int,
                   "balance"?: int, "tx_hash"?: str}.
    """
    if intent.status == "confirmed":
        return {"success": True, "reason": "already_confirmed",
                "tx_hash": intent.confirmed_tx_hash}
    if intent.status == "expired":
        return {"success": False, "reason": "expired"}

    # Pull recent TXs for this chain only
    txs: list["IncomingTx"] = []
    try:
        if intent.chain == "ton" and ton_client is not None:
            txs = await ton_client.recent_incoming_usdt(WALLET_TON, limit=50)
        elif intent.chain == "tron" and tron_client is not None:
            txs = await tron_client.recent_incoming_usdt(WALLET_TRON, limit=50)
    except Exception:
        logger.exception("check_intent_now fetch failed")
        return {"success": False, "reason": "chain_fetch_failed"}

    if not txs:
        return {"success": False, "reason": "no_txs_seen_yet"}

    # Locate the tx that should credit this intent
    matching_tx = None
    if tx_hash:
        # User-supplied hash — exact match wins, regardless of memo/fingerprint
        h = tx_hash.strip().lower()
        for tx in txs:
            if tx.tx_hash.lower() == h:
                matching_tx = tx
                break
        if matching_tx is None:
            return {"success": False, "reason": "tx_not_found_on_chain"}
        # Anti-double-claim: refuse if another intent already used this hash
        if await _is_tx_hash_used(repo, h, exclude_intent_id=intent.intent_id):
            return {"success": False, "reason": "tx_already_claimed"}
    else:
        # Standard matching (same logic as cron find_match)
        for tx in txs:
            if find_match([intent], tx) is intent:
                matching_tx = tx
                break
        if matching_tx is None:
            return {"success": False, "reason": "no_matching_tx_yet"}

    # Confirm + credit
    confirmed = await confirm_intent(repo, profile_repo, intent,
                                     matching_tx.tx_hash,
                                     usage_logger=usage_logger,
                                     storage_account_name=repo._account)
    if not confirmed:
        return {"success": False, "reason": "credit_failed"}
    return {
        "success": True, "reason": "ok",
        "points_credited": intent.points_to_credit,
        "tx_hash": matching_tx.tx_hash,
    }


async def _is_tx_hash_used(repo: "DonationIntentRepo", tx_hash: str,
                           *, exclude_intent_id: str = "") -> bool:
    """Scan all intents for an existing confirmed_tx_hash collision."""
    try:
        from azure.identity.aio import DefaultAzureCredential
        from azure.storage.blob.aio import BlobServiceClient
        creds = repo._credential or DefaultAzureCredential()
        h = tx_hash.strip().lower()
        try:
            async with BlobServiceClient(
                account_url=f"https://{repo._account}.blob.core.windows.net",
                credential=creds,
            ) as svc:
                container = svc.get_container_client(CONTAINER)
                async for blob in container.list_blobs():
                    if blob.name.endswith(".json") and not blob.name[:-5].startswith(exclude_intent_id):
                        bc = container.get_blob_client(blob.name)
                        try:
                            body = await (await bc.download_blob()).readall()
                            d = json.loads(body)
                            if (d.get("confirmed_tx_hash") or "").lower() == h:
                                return True
                        except Exception:
                            continue
        finally:
            if repo._credential is None and hasattr(creds, "close"):
                await creds.close()
    except Exception:
        logger.exception("_is_tx_hash_used scan failed")
    return False


async def confirm_intent(repo: DonationIntentRepo, profile_repo,
                         intent: DonationIntent, tx_hash: str,
                         *, usage_logger=None,
                         storage_account_name: str | None = None) -> bool:
    """Mark intent confirmed, credit points, update donation_total_usdt,
    and schedule referrer milestone bonuses (30d holding)."""
    from .point_ledger import add_points
    if intent.status != "pending":
        return False
    intent.status = "confirmed"
    intent.confirmed_tx_hash = tx_hash
    intent.confirmed_at = _now_iso()
    await repo.put(intent)
    try:
        new_profile = await add_points(
            profile_repo, intent.user_key, intent.points_to_credit,
            reason="donation", ref=f"{intent.chain}:{intent.intent_id}",
            usage_logger=usage_logger,
        )
    except Exception:
        logger.exception("donation credit failed for %s", intent.intent_id)
        intent.status = "pending"
        intent.confirmed_tx_hash = ""
        intent.confirmed_at = ""
        await repo.put(intent)
        return False

    # §7 — bump donation_total_usdt + check referrer milestone
    try:
        old_total = float(getattr(new_profile, "donation_total_usdt", 0) or 0)
        new_total = round(old_total + float(intent.amount_usdt), 4)
        update_call = profile_repo.update(
            intent.user_key, donation_total_usdt=new_total,
        )
        updated = (await update_call if hasattr(update_call, "__await__")
                   else update_call)

        # Schedule referrer milestone if referee has an inviter
        if storage_account_name and getattr(updated, "invited_by_anon", ""):
            from .referrer_milestones import schedule_for_donation
            try:
                referrer_user_key = await _resolve_referrer_user_key(
                    profile_repo, storage_account_name,
                    updated.invited_by_anon,
                )
                if referrer_user_key:
                    await schedule_for_donation(
                        storage_account_name, updated, referrer_user_key,
                        new_total_usdt=new_total, old_total_usdt=old_total,
                    )
            except Exception:
                logger.warning("referrer milestone schedule failed",
                               exc_info=True)
    except Exception:
        logger.warning("donation_total_usdt update failed (non-fatal)",
                       exc_info=True)
    return True


async def _resolve_referrer_user_key(profile_repo, account_name: str,
                                     anon_short: str) -> str | None:
    """Find the referrer's user_key from their 8-char anon prefix.
    Used by milestone scheduling. O(N) blob scan, MVP-acceptable."""
    from azure.identity.aio import DefaultAzureCredential
    from azure.storage.blob.aio import BlobServiceClient
    creds = DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client("users")
            async for blob in container.list_blobs(name_starts_with=f"{anon_short[:2]}/"):
                if not blob.name.endswith(".json"):
                    continue
                try:
                    body = await (await container.get_blob_client(blob.name)
                                  .download_blob()).readall()
                    d = json.loads(body)
                    if (d.get("anon_user_id") or "").startswith(anon_short):
                        return d.get("user_key") or None
                except Exception:
                    continue
    finally:
        if hasattr(creds, "close"):
            await creds.close()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Cron tick (called by Timer)
# ─────────────────────────────────────────────────────────────────────────────
async def verify_tick(repo: DonationIntentRepo, profile_repo,
                      *, ton_client=None, tron_client=None,
                      usage_logger=None) -> dict:
    """One verification pass. Returns {confirmed: int, expired: int, scanned_tx: int}."""
    pending = await repo.list_pending()
    if not pending:
        return {"confirmed": 0, "expired": 0, "scanned_tx": 0}

    # Expire stale intents first
    now = datetime.now(timezone.utc)
    expired = 0
    for intent in pending:
        try:
            if datetime.fromisoformat(intent.expires_at) <= now:
                intent.status = "expired"
                await repo.put(intent)
                expired += 1
        except ValueError:
            pass
    active = [i for i in pending if i.status == "pending"]

    # Fetch recent TXs from each chain
    txs: list[IncomingTx] = []
    if ton_client is not None and any(i.chain == "ton" for i in active):
        try:
            txs.extend(await ton_client.recent_incoming_usdt(WALLET_TON))
        except Exception:
            logger.exception("ton fetch failed")
    if tron_client is not None and any(i.chain == "tron" for i in active):
        try:
            txs.extend(await tron_client.recent_incoming_usdt(WALLET_TRON))
        except Exception:
            logger.exception("tron fetch failed")

    confirmed = 0
    for tx in txs:
        match = find_match(active, tx)
        if match is None:
            continue
        if await confirm_intent(repo, profile_repo, match, tx.tx_hash,
                                usage_logger=usage_logger,
                                storage_account_name=repo._account):
            confirmed += 1
            active.remove(match)

    return {"confirmed": confirmed, "expired": expired, "scanned_tx": len(txs)}
