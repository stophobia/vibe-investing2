"""§T2E-O — Personalized brag cards (사회적 증거 핵심).

Auto-generates a shareable PNG image when a user reaches a milestone:
  tier_promotion   tier 승급 (bronze→silver, silver→gold, etc.)
  streak_accuracy  N일 연속 예측 정답
  bet_profit       단일 일 베팅 수익률 +500 P 이상
  staking_size     스테이킹 규모 (premium tier)

Card layout (1080×1080, square — Twitter/X + Instagram + Telegram preview friendly):
  Top-left:    증권당 logo + brand
  Top-right:   tier badge (color-coded)
  Center:      large headline number/text (the "wow" stat)
  Mid:         sub-stats (3-up grid)
  Bottom:      QR + invite link

Generated to Blob `share-cards/<user_short>/<card_uuid>.png`. Public URL
returned so the Mini App can <img src> + <a download>.

Pillow is the only runtime dep; no fonts shipped — uses default Pillow font
(might look plain but renders on every platform). For nicer typography, ship
a Korean-friendly TTF in the repo.
"""

from __future__ import annotations

import io
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from azure.core.exceptions import ResourceExistsError
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logger = logging.getLogger(__name__)

CONTAINER = "share-cards"


# ─────────────────────────────────────────────────────────────
# Tier color palette (matches Mini App / dashboard)
# ─────────────────────────────────────────────────────────────

TIER_COLORS = {
    "bronze":   ("#cd7f32", "#8b5a2b"),
    "silver":   ("#c0c0c0", "#808080"),
    "gold":     ("#f7931a", "#b8690a"),
    "platinum": ("#74b9ff", "#4090c0"),
    "diamond":  ("#fd79a8", "#c0497d"),
}


@dataclass
class BragCard:
    card_id: str
    user_id: str
    kind: str           # tier_promotion | streak_accuracy | bet_profit | staking_size
    title: str
    headline: str       # the "wow" number/text
    sub_stats: list[tuple[str, str]]   # [(label, value), ...] up to 3
    tier: str
    nickname: str
    invite_link: str
    blob_path: str
    public_url: str
    generated_at: str


def _palette_for_kind(kind: str) -> tuple[str, str]:
    return {
        "tier_promotion":  ("#1a1a2e", "#3a2a4c"),   # dark purple gradient
        "streak_accuracy": ("#1a2e1a", "#2a4a2a"),   # dark green
        "bet_profit":      ("#2e2e1a", "#4c4c1a"),   # dark gold
        "staking_size":    ("#1a1a3e", "#2a2a6c"),   # dark blue
    }.get(kind, ("#1a1a2e", "#3a3a4c"))


def _render_card_png(card: BragCard) -> bytes:
    """Render the brag card as PNG bytes. Pure Pillow, no external assets."""
    from PIL import Image, ImageDraw, ImageFont

    W = H = 1080
    bg_top, bg_bot = _palette_for_kind(card.kind)
    img = Image.new("RGB", (W, H), bg_bot)
    draw = ImageDraw.Draw(img)

    # Vertical gradient (top → bottom)
    top_rgb = tuple(int(bg_top[i:i+2], 16) for i in (1, 3, 5))
    bot_rgb = tuple(int(bg_bot[i:i+2], 16) for i in (1, 3, 5))
    for y in range(H):
        ratio = y / H
        r = int(top_rgb[0] * (1 - ratio) + bot_rgb[0] * ratio)
        g = int(top_rgb[1] * (1 - ratio) + bot_rgb[1] * ratio)
        b = int(top_rgb[2] * (1 - ratio) + bot_rgb[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Try to load a system font (Pillow's default font is tiny + bitmap-only)
    def _font(size: int):
        for path in (
            # Try common system fonts (Linux Azure Functions container)
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc",
        ):
            try:
                return ImageFont.truetype(path, size=size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    f_brand    = _font(40)
    f_tier     = _font(32)
    f_title    = _font(48)
    f_headline = _font(140)
    f_sub_lbl  = _font(28)
    f_sub_val  = _font(56)
    f_nickname = _font(36)
    f_footer   = _font(24)

    # ── Top: brand left, tier badge right ─────────────────────
    draw.text((60, 60), "증권당 · 投資の戦場", font=f_brand, fill=(247, 147, 26))

    tier_color = TIER_COLORS.get(card.tier, ("#888", "#555"))[0]
    tier_color_rgb = tuple(int(tier_color[i:i+2], 16) for i in (1, 3, 5))
    badge_text = f" {card.tier.upper()} "
    bbox = draw.textbbox((0, 0), badge_text, font=f_tier)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = W - 60 - bw - 30, 60
    draw.rounded_rectangle((bx, by - 10, bx + bw + 30, by + bh + 10),
                           radius=12, fill=tier_color_rgb)
    draw.text((bx + 15, by), card.tier.upper(), font=f_tier, fill=(20, 20, 30))

    # ── Center: title + giant headline + sub stats ────────────
    cy = 320
    draw.text((60, cy), card.title, font=f_title, fill=(220, 220, 220))
    cy += 80

    # Headline (centered horizontally)
    bbox = draw.textbbox((0, 0), card.headline, font=f_headline)
    hw = bbox[2] - bbox[0]
    draw.text(((W - hw) // 2, cy), card.headline, font=f_headline, fill=(247, 147, 26))
    cy += 220

    # Sub stats (3-up grid)
    if card.sub_stats:
        col_w = (W - 120) // max(len(card.sub_stats), 1)
        for i, (lbl, val) in enumerate(card.sub_stats[:3]):
            x = 60 + col_w * i + col_w // 2
            bbox = draw.textbbox((0, 0), lbl, font=f_sub_lbl)
            draw.text((x - (bbox[2] - bbox[0]) // 2, cy), lbl,
                      font=f_sub_lbl, fill=(180, 180, 180))
            bbox = draw.textbbox((0, 0), val, font=f_sub_val)
            draw.text((x - (bbox[2] - bbox[0]) // 2, cy + 40), val,
                      font=f_sub_val, fill=(255, 255, 255))

    # ── Bottom: nickname + invite link ────────────────────────
    fy = H - 200
    bbox = draw.textbbox((0, 0), card.nickname, font=f_nickname)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, fy), card.nickname,
              font=f_nickname, fill=(247, 147, 26))

    fy += 60
    invite_text = card.invite_link.replace("https://", "")
    bbox = draw.textbbox((0, 0), invite_text, font=f_footer)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, fy), invite_text,
              font=f_footer, fill=(160, 160, 160))

    fy += 40
    cta = "👆 친구도 가입하면 200 P · AI 페르소나 챗봇"
    bbox = draw.textbbox((0, 0), cta, font=f_footer)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, fy), cta,
              font=f_footer, fill=(140, 140, 140))

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ─────────────────────────────────────────────────────────────
# Card builders for each kind
# ─────────────────────────────────────────────────────────────

def build_tier_promotion_card(*, nickname: str, tier: str, season_points: int,
                               next_threshold: int | None, rank: int | None,
                               invite_link: str, user_id: str) -> BragCard:
    next_pts = (next_threshold - season_points) if next_threshold else 0
    sub = [
        ("이번 시즌", f"{season_points:,} P"),
    ]
    if next_threshold:
        sub.append(("다음 등급까지", f"{next_pts:,} P"))
    if rank:
        sub.append(("시즌 순위", f"{rank}위"))
    return BragCard(
        card_id=uuid.uuid4().hex[:12],
        user_id=user_id,
        kind="tier_promotion",
        title="🏆 티어 승급",
        headline=tier.upper(),
        sub_stats=sub,
        tier=tier, nickname=nickname,
        invite_link=invite_link,
        blob_path="", public_url="",
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def build_streak_accuracy_card(*, nickname: str, tier: str, streak_days: int,
                                accuracy_pct: float, percentile: int | None,
                                invite_link: str, user_id: str) -> BragCard:
    sub = [
        ("정확도", f"{accuracy_pct:.1f}%"),
        ("연속", f"{streak_days}일"),
    ]
    if percentile:
        sub.append(("상위", f"{percentile}%"))
    return BragCard(
        card_id=uuid.uuid4().hex[:12],
        user_id=user_id,
        kind="streak_accuracy",
        title="🎯 예측 streak 갱신",
        headline=f"{streak_days}일 연속 ✓",
        sub_stats=sub,
        tier=tier, nickname=nickname,
        invite_link=invite_link,
        blob_path="", public_url="",
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def build_bet_profit_card(*, nickname: str, tier: str, profit_p: int,
                           win_count: int, total_bets: int,
                           invite_link: str, user_id: str) -> BragCard:
    return BragCard(
        card_id=uuid.uuid4().hex[:12],
        user_id=user_id,
        kind="bet_profit",
        title="💰 베팅 수익",
        headline=f"+{profit_p:,} P",
        sub_stats=[
            ("승", f"{win_count}건"),
            ("총 베팅", f"{total_bets}건"),
            ("승률", f"{(win_count/max(total_bets,1)*100):.0f}%"),
        ],
        tier=tier, nickname=nickname,
        invite_link=invite_link,
        blob_path="", public_url="",
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def build_staking_size_card(*, nickname: str, tier: str, total_usdt: float,
                             daily_p: int, total_yield_p: int,
                             invite_link: str, user_id: str) -> BragCard:
    return BragCard(
        card_id=uuid.uuid4().hex[:12],
        user_id=user_id,
        kind="staking_size",
        title="🪙 USDT 스테이킹",
        headline=f"${int(total_usdt):,}",
        sub_stats=[
            ("일일 적립", f"{daily_p:,} P"),
            ("누적 수령", f"{total_yield_p:,} P"),
            ("티어", tier.upper()),
        ],
        tier=tier, nickname=nickname,
        invite_link=invite_link,
        blob_path="", public_url="",
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


# ─────────────────────────────────────────────────────────────
# Upload + retrieval
# ─────────────────────────────────────────────────────────────

async def render_and_upload(
    card: BragCard,
    storage_account_name: str,
    *,
    credential=None,
) -> BragCard:
    """Generate PNG, upload to Blob, populate card.public_url."""
    png_bytes = _render_card_png(card)
    user_short = card.user_id.replace("tg:", "")[:8] or "anon"
    blob_path = f"{user_short}/{card.kind}/{card.card_id}.png"
    creds = credential or DefaultAzureCredential()
    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            try:
                await container.create_container()
            except ResourceExistsError:
                pass
            client = svc.get_blob_client(CONTAINER, blob_path)
            from azure.storage.blob import ContentSettings
            cs = ContentSettings(content_type="image/png", cache_control="public, max-age=86400")
            await client.upload_blob(png_bytes, overwrite=True, content_settings=cs)
            # Also write the metadata sidecar (JSON) for replay/audit
            meta_path = blob_path.replace(".png", ".json")
            meta = {**card.__dict__}
            await svc.get_blob_client(CONTAINER, meta_path).upload_blob(
                json.dumps(meta, ensure_ascii=False).encode(),
                overwrite=True, content_type="application/json",
            )
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    card.blob_path = blob_path
    # Public URL works because the storage account allowBlobPublicAccess is
    # enabled OR the SAS pattern. For Free Trial we serve via Function App proxy
    # at /api/share-card/{path} (defined in function_app.py).
    card.public_url = f"/api/share-card/{blob_path}"
    return card


async def list_user_cards(
    storage_account_name: str,
    user_key: str,
    *,
    credential=None,
    limit: int = 20,
) -> list[dict]:
    """Return up to `limit` of the user's cards (most recent first)."""
    user_short = user_key.replace("tg:", "")[:8] or "anon"
    creds = credential or DefaultAzureCredential()
    items: list[dict] = []
    try:
        async with BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=creds,
        ) as svc:
            container = svc.get_container_client(CONTAINER)
            async for blob in container.list_blobs(name_starts_with=f"{user_short}/"):
                if not blob.name.endswith(".json"):
                    continue
                try:
                    client = container.get_blob_client(blob.name)
                    stream = await client.download_blob()
                    body = await stream.readall()
                    items.append(json.loads(body))
                except Exception:
                    continue
    except Exception:
        logger.exception("list_user_cards failed")
    finally:
        if credential is None and hasattr(creds, "close"):
            await creds.close()

    items.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
    return items[:limit]
