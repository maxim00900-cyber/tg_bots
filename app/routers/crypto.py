import asyncio
import logging
from typing import Any

import aiohttp
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.cryptobot import get_shared_crypto_bot_client

router = Router()
NETWORK_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError)
API_ERRORS = (RuntimeError,)


async def _send_existing_invoice(callback: CallbackQuery, invoice_id: str) -> bool:
    client = get_shared_crypto_bot_client()
    try:
        invoice = await client.get_invoice(invoice_id)
    except NETWORK_ERRORS as exc:
        logging.exception("CryptoBot get_invoice network failure: %s", exc)
        return False
    except API_ERRORS as exc:
        logging.exception("CryptoBot get_invoice API failure: %s", exc)
        return False

    if not invoice:
        return False

    status = invoice.get("status")
    if status == "paid":
        await _handle_paid_invoice(callback, invoice_id)
        return True
    if status == "active":
        return await _send_payment_link_if_available(callback, invoice_id, invoice)
    return False


async def _safe_answer(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message is None:
        return
    await callback.message.answer(text, reply_markup=reply_markup)


async def _handle_paid_invoice(callback: CallbackQuery, invoice_id: str) -> None:
    await rq.mark_paid_by_invoice(invoice_id, "crypto")
    await _safe_answer(callback, texts.ACCESS_TEXT)


async def _send_payment_link_if_available(
    callback: CallbackQuery,
    invoice_id: str,
    invoice: dict[str, Any],
) -> bool:
    pay_url = invoice.get("pay_url")
    if not pay_url:
        return False
    await _safe_answer(
        callback,
        texts.PAY_USDT_TEXT,
        reply_markup=kb.check_payment_kb(invoice_id, pay_url),
    )
    return True


@router.callback_query(F.data == "pay_usdt")
async def callback_usdt(callback: CallbackQuery) -> None:
    await callback.answer()
    user = await rq.get_user(callback.from_user.id)
    if user and user.is_paid:
        await _safe_answer(callback, texts.ACCESS_TEXT)
        return

    if user and user.invoice_id:
        if await _send_existing_invoice(callback, user.invoice_id):
            return

    client = get_shared_crypto_bot_client()
    try:
        invoice = await client.create_invoice(
            amount=texts.PRICE_USDT,
            asset="USDT",
            description="Доступ к сервису",
            payload=str(callback.from_user.id),
        )
    except NETWORK_ERRORS as exc:
        logging.exception("CryptoBot create_invoice network failure: %s", exc)
        await _safe_answer(callback, texts.PAYMENT_NETWORK_ERROR_TEXT)
        return
    except API_ERRORS as exc:
        logging.exception("CryptoBot create_invoice API failure: %s", exc)
        await _safe_answer(callback, texts.PAYMENT_API_ERROR_TEXT)
        return

    await rq.set_invoice(callback.from_user.id, invoice["invoice_id"], "crypto")
    pay_url = invoice["pay_url"]
    await _safe_answer(
        callback,
        texts.PAY_USDT_TEXT,
        reply_markup=kb.check_payment_kb(invoice["invoice_id"], pay_url),
    )


@router.callback_query(F.data.startswith("check_invoice:"))
async def callback_check_invoice(callback: CallbackQuery) -> None:
    await callback.answer()
    invoice_id = callback.data.split(":", 1)[1]
    user = await rq.get_user(callback.from_user.id)
    if not user or user.invoice_id != str(invoice_id):
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return

    client = get_shared_crypto_bot_client()
    try:
        invoice = await client.get_invoice(invoice_id)
    except NETWORK_ERRORS as exc:
        logging.exception("CryptoBot get_invoice network failure: %s", exc)
        await _safe_answer(callback, texts.PAYMENT_NETWORK_ERROR_TEXT)
        return
    except API_ERRORS as exc:
        logging.exception("CryptoBot get_invoice API failure: %s", exc)
        await _safe_answer(callback, texts.PAYMENT_API_ERROR_TEXT)
        return

    if not invoice:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return

    status = invoice.get("status")
    if status == "paid":
        await _handle_paid_invoice(callback, invoice_id)
        return
    if status == "expired":
        await _safe_answer(callback, texts.PAYMENT_EXPIRED_TEXT)
        return
    await _safe_answer(callback, texts.PAYMENT_PENDING_TEXT)
