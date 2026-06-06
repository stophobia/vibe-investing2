"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_token: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str
    default_persona: str
    user_id_salt: str
    sqlite_path: str
    storage_backend: str  # 'sqlite' (1차 / dev) or 'blob' (2차 / Azure)
    storage_account_name: str
    log_level: str
    finnhub_key: str
    cf_ingest_url: str
    ingest_secret: str
    alphavantage_key: str

    @staticmethod
    def load() -> "Config":
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

        if not telegram_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Check your .env file.")
        if not deepseek_api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set. Check your .env file.")

        return Config(
            telegram_token=telegram_token,
            deepseek_api_key=deepseek_api_key,
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip(),
            default_persona=os.getenv("DEFAULT_PERSONA", "buffett").lower(),
            user_id_salt=os.getenv("USER_ID_SALT", "ai-investor-default-salt-change-me"),
            sqlite_path=os.getenv("SQLITE_PATH", "./data/aiinvestor.db"),
            storage_backend=os.getenv("STORAGE_BACKEND", "sqlite").lower(),
            storage_account_name=os.getenv("STORAGE_ACCOUNT_NAME", "").strip(),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            finnhub_key=os.getenv("FINNHUB_KEY", "").strip(),
            cf_ingest_url=os.getenv("CF_INGEST_URL", "").strip(),
            ingest_secret=os.getenv("INGEST_SECRET", "").strip(),
            alphavantage_key=os.getenv("ALPHAVANTAGE_KEY", "").strip(),
        )


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
