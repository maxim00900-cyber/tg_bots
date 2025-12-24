from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
import os

from dotenv import load_dotenv

from app.text_keys import TEXT_OVERRIDE_KEYS


@dataclass(frozen=True)
class Settings:
    token: str | None
    cryptobot_token: str | None
    database_url: str
    admin_chat_ids: tuple[int, ...]
    rub_pay_url: str | None
    price_rub: int
    price_usdt: float
    price_currency: str
    support_contact: str
    text_overrides: dict[str, str]


def _parse_admin_chat_ids(value: str | None, fallback: str | None) -> tuple[int, ...]:
    raw = value or fallback
    if not raw:
        return ()
    result: list[int] = []
    for part in raw.split(","):
        item = part.strip()
        if not item:
            continue
        try:
            result.append(int(item))
        except ValueError:
            logging.error("ADMIN_CHAT_IDS contains invalid value: %s", item)
    return tuple(result)


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    text_overrides = {
        key: value for key in TEXT_OVERRIDE_KEYS if (value := os.getenv(key))
    }
    return Settings(
        token=os.getenv("TOKEN"),
        cryptobot_token=os.getenv("CRYPTOBOT_TOKEN"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3"),
        admin_chat_ids=_parse_admin_chat_ids(
            os.getenv("ADMIN_CHAT_IDS"),
            os.getenv("ADMIN_CHAT_ID"),
        ),
        rub_pay_url=os.getenv("RUB_PAY_URL"),
        price_rub=int(os.getenv("PRICE_RUB", "269")),
        price_usdt=float(os.getenv("PRICE_USDT", "3.0")),
        price_currency=os.getenv("PRICE_CURRENCY", "₽"),
        support_contact=os.getenv("SUPPORT_CONTACT", "@sergei_kk"),
        text_overrides=text_overrides,
    )
