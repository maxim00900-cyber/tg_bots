import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import get_settings, log_missing_settings
from app.routers import router
from app.database.models import async_main
from app.cryptobot import close_crypto_bot_client


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main() -> None:
    settings = get_settings()
    if not settings.token:
        raise RuntimeError("TOKEN env var is not set")
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL env var is not set")
    log_missing_settings(settings)

    _setup_logging()
    await async_main()

    bot: Bot | None = None
    dp = Dispatcher()
    dp.include_router(router)
    try:
        bot = Bot(settings.token)
        await dp.start_polling(bot)
    finally:
        if bot:
            await bot.session.close()
        await close_crypto_bot_client()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
