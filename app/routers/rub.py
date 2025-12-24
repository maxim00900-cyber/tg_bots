from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.services.user_handlers import (
    handle_pay_rub,
    handle_receipt_message,
    handle_rub_receipt_sent,
)

router = Router()


@router.callback_query(F.data == "pay_rub")
async def callback_rub(callback: CallbackQuery) -> None:
    await handle_pay_rub(callback)


@router.callback_query(F.data == "rub_receipt_sent")
async def callback_rub_receipt_sent(callback: CallbackQuery) -> None:
    await handle_rub_receipt_sent(callback)


@router.message(F.photo | F.document)
async def receipt_message(message: Message) -> None:
    await handle_receipt_message(message)
