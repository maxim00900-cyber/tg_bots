from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.routers.admin_utils import is_staff

router = Router()


async def _reply_admin(message: Message) -> bool:
    if await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_WELCOME_TEXT, reply_markup=kb.admin_kb)
        return True
    return False


async def _is_paid(user_id: int) -> bool:
    user = await rq.get_user(user_id)
    return bool(user and (user.payment_status == "paid" or user.is_paid))


async def _is_banned(user_id: int) -> bool:
    return await rq.is_user_banned(user_id)


async def _reply_banned(message: Message) -> bool:
    if await _is_banned(message.from_user.id):
        await message.answer(texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return True
    return False


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await rq.set_user(message.from_user.id)
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    if await _is_paid(message.from_user.id):
        await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    await message.answer(texts.WELCOME_TEXT, reply_markup=kb.user_kb(False))


@router.message(Command(commands="help"))
async def command_help(message: Message) -> None:
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    is_paid = await _is_paid(message.from_user.id)
    await message.answer(texts.HELP_TEXT, reply_markup=kb.user_kb(is_paid))


@router.message(F.text == texts.BUTTON_PAY)
async def paid(message: Message) -> None:
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    if await _is_paid(message.from_user.id):
        await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    await message.answer(texts.PAID_TEXT, reply_markup=kb.payment_kb)


@router.message(F.text == texts.BUTTON_SUPPORT)
async def help_contact(message: Message) -> None:
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    is_paid = await _is_paid(message.from_user.id)
    await message.answer(texts.SUPPORT_TEXT, reply_markup=kb.user_kb(is_paid))


@router.message(F.text == texts.BUTTON_INFO)
async def info_repeat(message: Message) -> None:
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    if not await _is_paid(message.from_user.id):
        await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.user_kb(False))
        return
    await message.answer(texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))


@router.message(F.text)
async def any_message(message: Message) -> None:
    if await _reply_admin(message):
        return
    if await _reply_banned(message):
        return
    is_paid = await _is_paid(message.from_user.id)
    await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.user_kb(is_paid))
