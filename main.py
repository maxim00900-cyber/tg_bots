import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.routers import router
from app.database.models import async_main
from app.cryptobot import close_crypto_bot_client


async def main():
    load_dotenv()

    token = os.getenv("TOKEN")
    if not token:
        raise RuntimeError("TOKEN env var is not set")

    logging.basicConfig(level=logging.INFO)

    await async_main()

    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await close_crypto_bot_client()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
