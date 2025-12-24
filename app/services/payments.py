import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import aiohttp

from app.config import get_settings
from app.cryptobot import get_shared_crypto_bot_client
from app.database.models import User
import app.database.requests as rq

CRYPTOBOT_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError)


class CryptoInvoiceStatus(str, Enum):
    PAID = "paid"
    ACTIVE = "active"
    CREATED = "created"
    ERROR = "error"


class CryptoCheckStatus(str, Enum):
    PAID = "paid"
    EXPIRED = "expired"
    FAILED = "failed"
    PENDING = "pending"
    INVALID_USER = "invalid_user"
    NOT_FOUND = "not_found"
    ERROR = "error"


class RubPaymentStatus(str, Enum):
    ALREADY_PAID = "already_paid"
    DISABLED = "disabled"
    READY = "ready"


class RubReceiptSentStatus(str, Enum):
    DISABLED = "disabled"
    READY = "ready"


class RubReceiptUploadStatus(str, Enum):
    IGNORED = "ignored"
    DISABLED = "disabled"
    FORWARDED = "forwarded"


@dataclass(slots=True)
class CryptoInvoiceResult:
    status: CryptoInvoiceStatus
    invoice_id: str | None = None
    pay_url: str | None = None


@dataclass(slots=True)
class CryptoCheckResult:
    status: CryptoCheckStatus


@dataclass(slots=True)
class RubPaymentResult:
    status: RubPaymentStatus
    pay_url: str | None = None


@dataclass(slots=True)
class RubReceiptSentResult:
    status: RubReceiptSentStatus
    admin_chat_ids: tuple[int, ...] | None = None
    message: str | None = None


@dataclass(slots=True)
class RubReceiptUploadResult:
    status: RubReceiptUploadStatus
    admin_chat_ids: tuple[int, ...] | None = None


async def create_crypto_invoice(user_id: int, price: float) -> CryptoInvoiceResult:
    user = await rq.get_user(user_id)
    if user and (user.payment_status == "paid" or user.is_paid):
        return CryptoInvoiceResult(status=CryptoInvoiceStatus.PAID)

    if user and user.invoice_id and user.payment_status in (None, "pending"):
        existing = await _fetch_crypto_invoice(user.invoice_id)
        if existing:
            status = existing.get("status")
            if status == "paid":
                await rq.mark_paid_by_invoice(user.invoice_id, "crypto")
                return CryptoInvoiceResult(
                    status=CryptoInvoiceStatus.PAID,
                    invoice_id=str(user.invoice_id),
                )
            if status == "active":
                pay_url = existing.get("pay_url")
                if pay_url:
                    return CryptoInvoiceResult(
                        status=CryptoInvoiceStatus.ACTIVE,
                        invoice_id=str(user.invoice_id),
                        pay_url=pay_url,
                    )
            if status == "expired":
                await rq.mark_expired_by_invoice(user.invoice_id)
            if status == "failed":
                await rq.mark_failed_by_invoice(user.invoice_id)

    invoice = await _create_crypto_invoice(user_id, price)
    if not invoice:
        await rq.mark_failed_by_user(user_id, paid_method="crypto")
        return CryptoInvoiceResult(status=CryptoInvoiceStatus.ERROR)

    await rq.set_invoice(user_id, invoice["invoice_id"], "crypto")
    return CryptoInvoiceResult(
        status=CryptoInvoiceStatus.CREATED,
        invoice_id=invoice["invoice_id"],
        pay_url=invoice["pay_url"],
    )


async def check_crypto_invoice(user_id: int, invoice_id: str) -> CryptoCheckResult:
    user = await rq.get_user(user_id)
    if not user or user.invoice_id != str(invoice_id):
        return CryptoCheckResult(status=CryptoCheckStatus.INVALID_USER)

    invoice = await _fetch_crypto_invoice(invoice_id)
    if invoice is None:
        await rq.mark_failed_by_invoice(invoice_id)
        return CryptoCheckResult(status=CryptoCheckStatus.ERROR)
    if not invoice:
        await rq.mark_failed_by_invoice(invoice_id)
        return CryptoCheckResult(status=CryptoCheckStatus.NOT_FOUND)

    status = invoice.get("status")
    if status == "paid":
        await rq.mark_paid_by_invoice(invoice_id, "crypto")
        return CryptoCheckResult(status=CryptoCheckStatus.PAID)
    if status == "expired":
        await rq.mark_expired_by_invoice(invoice_id)
        return CryptoCheckResult(status=CryptoCheckStatus.EXPIRED)
    if status == "failed":
        await rq.mark_failed_by_invoice(invoice_id)
        return CryptoCheckResult(status=CryptoCheckStatus.FAILED)
    return CryptoCheckResult(status=CryptoCheckStatus.PENDING)


async def start_rub_payment(user_id: int) -> RubPaymentResult:
    user = await rq.get_user(user_id)
    if user and (user.payment_status == "paid" or user.is_paid):
        return RubPaymentResult(status=RubPaymentStatus.ALREADY_PAID)

    rub_pay_url = _get_rub_pay_url()
    if not rub_pay_url:
        return RubPaymentResult(status=RubPaymentStatus.DISABLED)

    await rq.set_rub_pending(user_id)
    return RubPaymentResult(status=RubPaymentStatus.READY, pay_url=rub_pay_url)


def build_rub_receipt_sent(
    user_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
) -> RubReceiptSentResult:
    admin_chat_ids = _get_admin_chat_ids()
    if not admin_chat_ids:
        return RubReceiptSentResult(status=RubReceiptSentStatus.DISABLED)

    name = " ".join(part for part in [first_name, last_name] if part)
    username_display = f"@{username}" if username else "\u0431\u0435\u0437 username"
    message = (
        "\u041d\u043e\u0432\u0430\u044f \u043e\u043f\u043b\u0430\u0442\u0430 \u0432 \u0440\u0443\u0431\u043b\u044f\u0445.\n"
        f"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c: {name} ({username_display})\n"
        f"ID: {user_id}\n"
        "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043d\u0430\u0436\u0430\u043b \u00ab\u042f \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u043b \u0447\u0435\u043a\u00bb."
    )
    return RubReceiptSentResult(
        status=RubReceiptSentStatus.READY,
        admin_chat_ids=admin_chat_ids,
        message=message,
    )


async def check_rub_receipt_upload(user_id: int) -> RubReceiptUploadResult:
    user = await rq.get_user(user_id)
    if not _user_needs_rub_receipt(user):
        return RubReceiptUploadResult(status=RubReceiptUploadStatus.IGNORED)

    admin_chat_ids = _get_admin_chat_ids()
    if not admin_chat_ids:
        return RubReceiptUploadResult(status=RubReceiptUploadStatus.DISABLED)

    return RubReceiptUploadResult(
        status=RubReceiptUploadStatus.FORWARDED,
        admin_chat_ids=admin_chat_ids,
    )


async def _create_crypto_invoice(user_id: int, price: float) -> dict[str, Any] | None:
    client = get_shared_crypto_bot_client()
    try:
        return await client.create_invoice(
            amount=price,
            asset="USDT",
            description="\u0414\u043e\u0441\u0442\u0443\u043f \u043a \u0441\u0435\u0440\u0432\u0438\u0441\u0443",
            payload=str(user_id),
        )
    except CRYPTOBOT_ERRORS as exc:
        logging.exception("CryptoBot create_invoice failed: %s", exc)
        return None


async def _fetch_crypto_invoice(invoice_id: str) -> dict[str, Any] | None:
    client = get_shared_crypto_bot_client()
    try:
        return await client.get_invoice(invoice_id)
    except CRYPTOBOT_ERRORS as exc:
        logging.exception("CryptoBot get_invoice failed: %s", exc)
        return None


def _get_admin_chat_ids() -> tuple[int, ...]:
    settings = get_settings()
    if not settings.admin_chat_ids:
        logging.error("ADMIN_CHAT_ID is not configured")
    return settings.admin_chat_ids


def _get_rub_pay_url() -> str | None:
    settings = get_settings()
    if not settings.rub_pay_url:
        logging.error("RUB_PAY_URL is not configured")
    return settings.rub_pay_url


def _user_needs_rub_receipt(user: User | None) -> bool:
    if not user or user.paid_method != "rub":
        return False
    status = user.payment_status
    return bool(not user.is_paid and status in (None, "pending"))
