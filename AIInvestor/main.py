"""AI Investor — Telegram bot entry point."""

from __future__ import annotations

import logging

from bot.telegram_handler import BotDependencies, build_application
from config import Config, configure_logging
from services.market_report import MarketReportService
from services.persona_engine import PersonaEngine, get_persona
from services.profile_factory import build_repo
from services.stock_service import StockService

logger = logging.getLogger("ai_investor")


def main() -> None:
    config = Config.load()
    configure_logging(config.log_level)

    persona_engine = PersonaEngine(
        api_key=config.deepseek_api_key,
        model=config.deepseek_model,
        base_url=config.deepseek_base_url,
    )
    stock_service = StockService()
    profile_repo = build_repo(config)  # Blob (prod) or SQLite-async-wrapped (dev)
    market_report_service = MarketReportService(persona_engine=persona_engine)

    deps = BotDependencies(
        persona_engine=persona_engine,
        stock_service=stock_service,
        profile_repo=profile_repo,
        market_report_service=market_report_service,
        default_persona_key=get_persona(config.default_persona).key,
    )

    app = build_application(config.telegram_token, deps)

    logger.info(
        "AI Investor starting. persona=%s model=%s base_url=%s db=%s",
        deps.default_persona_key,
        config.deepseek_model,
        config.deepseek_base_url,
        config.sqlite_path,
    )
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
