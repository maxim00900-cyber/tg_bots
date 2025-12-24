import logging

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app import keyboards as kb
from app import texts
from app.config import get_settings
import app.database.requests as rq

router = Router()


def _is_admin(message: Message) -> bool:
    if message.from_user is None:
        return False
    settings = get_settings()
    return settings.admin_chat_id == message.from_user.id


def _parse_target_user_id(message: Message) -> int | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


async def _notify_user(message: Message, user_id: int, text: str) -> None:
    try:
        await message.bot.send_message(user_id, text)
    except Exception as exc:
        logging.exception("Failed to notify user %s: %s", user_id, exc)


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await rq.set_user(message.from_user.id)
    await message.answer(texts.WELCOME_TEXT, reply_markup=kb.main_kb)


@router.message(Command(commands="help"))
async def command_help(message: Message) -> None:
    await message.answer(texts.HELP_TEXT, reply_markup=kb.main_kb)


@router.message(F.text == texts.BUTTON_PAY)
async def paid(message: Message) -> None:
    await message.answer(texts.PAID_TEXT, reply_markup=kb.payment_kb)


@router.message(F.text == texts.BUTTON_SUPPORT)
async def help_contact(message: Message) -> None:
    await message.answer(texts.SUPPORT_TEXT, reply_markup=kb.main_kb)


@router.message(Command(commands="approve"))
async def approve_payment(message: Message) -> None:
    if not _is_admin(message):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.APPROVE_USAGE_TEXT)
        return

    user = await rq.mark_paid_by_user(user_id, "rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_APPROVED_TEXT)
    await message.answer(texts.APPROVE_SUCCESS_TEXT)


@router.message(Command(commands="deny"))
async def deny_payment(message: Message) -> None:
    if not _is_admin(message):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.DENY_USAGE_TEXT)
        return

    user = await rq.reset_payment(user_id, paid_method="rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_DENIED_TEXT)
    await message.answer(texts.DENY_SUCCESS_TEXT)


@router.message(F.text)
async def any_message(message: Message) -> None:
    await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.main_kb)
