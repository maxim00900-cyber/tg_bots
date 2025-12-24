from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.services.user_handlers import handle_check_invoice, handle_pay_usdt

router = Router()


@router.callback_query(F.data == "pay_usdt")
async def callback_usdt(callback: CallbackQuery) -> None:
    await handle_pay_usdt(callback)


@router.callback_query(F.data.startswith("check_invoice:"))
async def callback_check_invoice(callback: CallbackQuery) -> None:
    await handle_check_invoice(callback)
