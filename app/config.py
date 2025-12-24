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
    text_keys = [
        "WELCOME_TEXT",
        "HELP_TEXT",
        "PAID_TEXT",
        "SUPPORT_TEXT",
        "PAY_RUB_QR_TEXT",
        "PAY_USDT_TEXT",
        "ACCESS_TEXT",
        "PAYMENT_PENDING_TEXT",
        "PAYMENT_EXPIRED_TEXT",
        "PAYMENT_FAILED_TEXT",
        "PAYMENT_ERROR_TEXT",
        "PAYMENT_RUB_DISABLED_TEXT",
        "RECEIPT_RECEIVED_TEXT",
        "RECEIPT_SENT_TEXT",
        "DEFAULT_TEXT",
        "ADMIN_WELCOME_TEXT",
        "ADMIN_ONLY_TEXT",
        "APPROVE_USAGE_TEXT",
        "DENY_USAGE_TEXT",
        "ADMIN_ALREADY_HANDLED_TEXT",
        "APPROVE_SUCCESS_TEXT",
        "DENY_SUCCESS_TEXT",
        "USER_APPROVED_TEXT",
        "USER_DENIED_TEXT",
        "USER_NOT_FOUND_TEXT",
        "BAN_USAGE_TEXT",
        "UNBAN_USAGE_TEXT",
        "BAN_SUCCESS_TEXT",
        "UNBAN_SUCCESS_TEXT",
        "BANNED_TEXT",
        "ADMIN_ADD_USAGE_TEXT",
        "ADMIN_REMOVE_USAGE_TEXT",
        "ADMIN_ADDED_TEXT",
        "ADMIN_REMOVED_TEXT",
        "BUTTON_PAY",
        "BUTTON_SUPPORT",
        "BUTTON_INFO",
        "BUTTON_APPROVE",
        "BUTTON_DENY",
        "BUTTON_BAN",
        "BUTTON_ADMIN_APPROVE_HELP",
        "BUTTON_ADMIN_DENY_HELP",
        "BUTTON_ADMIN_BAN_HELP",
        "BUTTON_ADMIN_UNBAN_HELP",
        "BUTTON_ADMIN_ADD_HELP",
        "BUTTON_ADMIN_REMOVE_HELP",
        "PLACEHOLDER",
        "INLINE_PAY_RUB",
        "INLINE_PAY_USDT",
        "INLINE_CHECK_PAYMENT",
        "INLINE_PAY_QR",
        "INLINE_SENT_RECEIPT",
        "INLINE_PAY_CRYPTO",
    ]
    text_overrides = {
        key: value for key in text_keys if (value := os.getenv(key))
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
