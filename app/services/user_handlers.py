from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app import keyboards as kb
from app import texts
from app.routers.admin_utils import get_staff_ids
from app.services.user_access import (
    get_message_user_id,
    is_banned_user,
    is_owner_user,
    is_paid_user,
    is_staff_user,
)
import app.database.requests as rq
from app.services.payments import (
    CryptoCheckStatus,
    CryptoInvoiceStatus,
    RubPaymentStatus,
    RubReceiptSentStatus,
    RubReceiptUploadStatus,
    build_rub_receipt_sent,
    check_crypto_invoice,
    check_rub_receipt_upload,
    create_crypto_invoice,
    start_rub_payment,
)


async def _reply_admin(message: Message, user_id: int | None) -> bool:
    if user_id is None:
        return False
    if await is_staff_user(user_id):
        reply_kb = kb.admin_kb_owner if is_owner_user(user_id) else kb.admin_kb_staff
        await message.answer(texts.ADMIN_WELCOME_TEXT, reply_markup=reply_kb)
        return True
    return False


async def _reply_banned(message: Message, user_id: int | None) -> bool:
    if user_id is None:
        return False
    if await is_banned_user(user_id):
        await message.answer(texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return True
    return False


async def handle_start(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    await rq.set_user(user_id)
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    if await is_paid_user(user_id):
        await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    await message.answer(texts.WELCOME_TEXT, reply_markup=kb.user_kb(False))


async def handle_help(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    is_paid = await is_paid_user(user_id)
    await message.answer(texts.HELP_TEXT, reply_markup=kb.user_kb(is_paid))


async def handle_pay_button(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    if await is_paid_user(user_id):
        await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    await message.answer(texts.PAID_TEXT, reply_markup=kb.payment_kb)


async def handle_support(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    is_paid = await is_paid_user(user_id)
    await message.answer(texts.SUPPORT_TEXT, reply_markup=kb.user_kb(is_paid))


async def handle_info(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    if not await is_paid_user(user_id):
        await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.user_kb(False))
        return
    await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))


async def handle_any_message(message: Message) -> None:
    user_id = get_message_user_id(message)
    if user_id is None:
        return
    if await _reply_admin(message, user_id):
        return
    if await _reply_banned(message, user_id):
        return
    is_paid = await is_paid_user(user_id)
    await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.user_kb(is_paid))


async def _safe_answer(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message is None:
        return
    await callback.message.answer(text, reply_markup=reply_markup)


async def handle_pay_usdt(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    result = await create_crypto_invoice(callback.from_user.id, texts.PRICE_USDT)
    if result.status == CryptoInvoiceStatus.PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    if result.status == CryptoInvoiceStatus.ERROR:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status == CryptoInvoiceStatus.ACTIVE and result.invoice_id and result.pay_url:
        await _safe_answer(
            callback,
            texts.PAY_USDT_TEXT,
            reply_markup=kb.check_payment_kb(result.invoice_id, result.pay_url),
        )
        return
    if (
        result.status != CryptoInvoiceStatus.CREATED
        or not result.invoice_id
        or not result.pay_url
    ):
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    await _safe_answer(
        callback,
        texts.PAY_USDT_TEXT,
        reply_markup=kb.check_payment_kb(result.invoice_id, result.pay_url),
    )


async def handle_check_invoice(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    invoice_id = callback.data.split(":", 1)[1]
    result = await check_crypto_invoice(callback.from_user.id, invoice_id)
    if result.status == CryptoCheckStatus.INVALID_USER:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status in {CryptoCheckStatus.ERROR, CryptoCheckStatus.NOT_FOUND}:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status == CryptoCheckStatus.PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    if result.status == CryptoCheckStatus.EXPIRED:
        await _safe_answer(callback, texts.PAYMENT_EXPIRED_TEXT)
        return
    if result.status == CryptoCheckStatus.FAILED:
        await _safe_answer(callback, texts.PAYMENT_FAILED_TEXT)
        return
    await _safe_answer(callback, texts.PAYMENT_PENDING_TEXT)


def _format_sender_info(message: Message) -> str:
    user = message.from_user
    if not user:
        return "Чек от неизвестного пользователя."
    name = " ".join(part for part in [user.first_name, user.last_name] if part)
    username = f"@{user.username}" if user.username else "без username"
    return (
        "Чек от пользователя:\n"
        f"{name} ({username})\n"
        f"ID: {user.id}"
    )


async def handle_pay_rub(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    result = await start_rub_payment(callback.from_user.id)
    if result.status == RubPaymentStatus.ALREADY_PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT)
        return

    if result.status == RubPaymentStatus.DISABLED or not result.pay_url:
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    await _safe_answer(
        callback,
        texts.PAY_RUB_QR_TEXT,
        reply_markup=kb.rub_payment_kb(result.pay_url),
    )


async def handle_rub_receipt_sent(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    result = build_rub_receipt_sent(
        callback.from_user.id,
        callback.from_user.first_name,
        callback.from_user.last_name,
        callback.from_user.username,
    )
    staff_ids = await get_staff_ids()
    if result.status == RubReceiptSentStatus.DISABLED or not staff_ids:
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    await rq.mark_rub_receipt_sent(callback.from_user.id)

    for staff_id in staff_ids:
        await callback.bot.send_message(
            staff_id,
            result.message or "",
            reply_markup=kb.admin_action_kb(callback.from_user.id),
        )
    await _safe_answer(callback, texts.RECEIPT_SENT_TEXT)


async def handle_receipt_message(message: Message) -> None:
    if await rq.is_user_banned(message.from_user.id):
        await message.answer(texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    result = await check_rub_receipt_upload(message.from_user.id)
    if result.status == RubReceiptUploadStatus.IGNORED:
        return

    staff_ids = await get_staff_ids()
    if result.status == RubReceiptUploadStatus.DISABLED or not staff_ids:
        await message.answer(texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    for staff_id in staff_ids:
        await message.bot.send_message(staff_id, _format_sender_info(message))
        await message.copy_to(staff_id)
    await message.answer(texts.RECEIPT_RECEIVED_TEXT, reply_markup=kb.receipt_sent_kb())
