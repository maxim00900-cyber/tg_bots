from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    token: str | None
    cryptobot_token: str | None
    database_url: str
    admin_chat_id: int | None
    rub_pay_url: str | None


def _parse_admin_chat_id(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        logging.error("ADMIN_CHAT_ID is not a valid integer")
        return None


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        token=os.getenv("TOKEN"),
        cryptobot_token=os.getenv("CRYPTOBOT_TOKEN"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3"),
        admin_chat_id=_parse_admin_chat_id(os.getenv("ADMIN_CHAT_ID")),
        rub_pay_url=os.getenv("RUB_PAY_URL"),
    )
