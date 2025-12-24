import asyncio
import logging

import aiohttp
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.cryptobot import get_shared_crypto_bot_client

router = Router()


async def _send_existing_invoice(callback: CallbackQuery, invoice_id: str) -> bool:
    client = get_shared_crypto_bot_client()
    try:
        invoice = await client.get_invoice(invoice_id)
    except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as exc:
        logging.exception("CryptoBot get_invoice failed: %s", exc)
        return False

    if not invoice:
        return False

    status = invoice.get("status")
    if status == "paid":
        await rq.mark_paid_by_invoice(invoice_id, "crypto")
        await callback.message.answer(texts.ACCESS_TEXT)
        return True
    if status == "active":
        pay_url = invoice.get("pay_url")
        if pay_url:
            await callback.message.answer(
                texts.PAY_USDT_TEXT,
                reply_markup=kb.check_payment_kb(invoice_id, pay_url),
            )
            return True
    return False


@router.callback_query(F.data == "pay_usdt")
async def callback_usdt(callback: CallbackQuery) -> None:
    await callback.answer()
    user = await rq.get_user(callback.from_user.id)
    if user and user.is_paid:
        await callback.message.answer(texts.ACCESS_TEXT)
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
    except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as exc:
        logging.exception("CryptoBot create_invoice failed: %s", exc)
        await callback.message.answer(texts.PAYMENT_ERROR_TEXT)
        return

    await rq.set_invoice(callback.from_user.id, invoice["invoice_id"], "crypto")
    pay_url = invoice["pay_url"]
    await callback.message.answer(
        texts.PAY_USDT_TEXT,
        reply_markup=kb.check_payment_kb(invoice["invoice_id"], pay_url),
    )


@router.callback_query(F.data.startswith("check_invoice:"))
async def callback_check_invoice(callback: CallbackQuery) -> None:
    await callback.answer()
    invoice_id = callback.data.split(":", 1)[1]
    user = await rq.get_user(callback.from_user.id)
    if not user or user.invoice_id != str(invoice_id):
        await callback.message.answer(texts.PAYMENT_ERROR_TEXT)
        return

    client = get_shared_crypto_bot_client()
    try:
        invoice = await client.get_invoice(invoice_id)
    except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as exc:
        logging.exception("CryptoBot get_invoice failed: %s", exc)
        await callback.message.answer(texts.PAYMENT_ERROR_TEXT)
        return

    if not invoice:
        await callback.message.answer(texts.PAYMENT_ERROR_TEXT)
        return

    status = invoice.get("status")
    if status == "paid":
        await rq.mark_paid_by_invoice(invoice_id, "crypto")
        await callback.message.answer(texts.ACCESS_TEXT)
    elif status == "expired":
        await callback.message.answer(texts.PAYMENT_EXPIRED_TEXT)
    else:
        await callback.message.answer(texts.PAYMENT_PENDING_TEXT)
