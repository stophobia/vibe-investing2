"""§T2E-M — Telegram notification throttle.

Caps daily push messages per user × event-kind so that gamification
loops (invite landing, bet wins, mission completes) don't degenerate
into spam → user mute → bot block.

Limits chosen by event class:
  invite_landing      3 / day   noisy when going viral
  bet_win             10 / day  big wins should still notify
  bet_loss            0         silent on losses (negative reinforcement)
  matchup_win         5
  prediction_correct  5
  mission_complete    5
  tier_up             ∞         rare, positive
  referral_milestone  ∞         rare, positive
  donation_received   ∞         operator gratitude — always send
  system_critical     ∞         abuse penalty, security notice
  general             5         default fallback

When the cap is hit, the message is dropped silently and the function
returns False — caller can log telemetry but should NOT retry.
"""

from __future__ import annotations

import logging
from typing import Optional

from .blob_counter import increment_daily_counter_etag

logger = logging.getLogger(__name__)


NOTIFICATION_LIMITS: dict[str, float] = {
    "invite_landing":      3,
    "bet_win":             10,
    "bet_loss":            0,
    "matchup_win":         5,
    "prediction_correct":  5,
    "mission_complete":    5,
    "tier_up":             float("inf"),
    "referral_milestone":  float("inf"),
    "donation_received":   float("inf"),
    "menu_unlocked":       float("inf"),
    "system_critical":     float("inf"),
    "general":             5,
}


async def send_telegram_message_throttled(
    bot,
    chat_id: int | str,
    text: str,
    notification_key: str = "general",
    max_per_day: Optional[float] = None,
    parse_mode: Optional[str] = None,
    reply_markup=None,
    account_name: Optional[str] = None,
) -> bool:
    """Send a Telegram message respecting the per-user/per-kind daily cap.

    Args:
      bot:               python-telegram-bot Bot instance
      chat_id:           Telegram chat_id (raw integer is fine — counters
                         are keyed under the bot's perspective, not anon)
      text:              message body
      notification_key:  enum from NOTIFICATION_LIMITS
      max_per_day:       override the default cap (None = use default)
      parse_mode:        "HTML" / "Markdown" / None (plain)
      reply_markup:      InlineKeyboardMarkup or None
      account_name:      Storage account name (defaults to env)

    Returns:
      True  if sent
      False if throttled, blocked, or send failed
    """
    cap = max_per_day if max_per_day is not None else NOTIFICATION_LIMITS.get(notification_key, 5)

    if cap == 0:
        return False  # explicitly disabled
    if cap == float("inf"):
        return await _send_raw(bot, chat_id, text, parse_mode, reply_markup)

    counter_name = f"notifications:{chat_id}:{notification_key}"
    try:
        count = await increment_daily_counter_etag(counter_name, account_name=account_name)
    except Exception:
        logger.exception("counter failed for %s — failing safe (no send)", counter_name)
        return False

    if count > cap:
        logger.info("throttled chat=%s key=%s count=%d cap=%s",
                    chat_id, notification_key, count, cap)
        return False

    return await _send_raw(bot, chat_id, text, parse_mode, reply_markup)


async def _send_raw(bot, chat_id, text: str, parse_mode, reply_markup) -> bool:
    try:
        await bot.send_message(
            chat_id=chat_id, text=text,
            parse_mode=parse_mode, reply_markup=reply_markup,
        )
        return True
    except Exception:
        logger.exception("telegram send failed chat=%s", chat_id)
        return False
