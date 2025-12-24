from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app import texts
from app.services.user_handlers import (
    handle_any_message,
    handle_help,
    handle_info,
    handle_pay_button,
    handle_start,
    handle_support,
)

router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await handle_start(message)


@router.message(Command(commands="help"))
async def command_help(message: Message) -> None:
    await handle_help(message)


@router.message(F.text == texts.BUTTON_PAY)
async def paid(message: Message) -> None:
    await handle_pay_button(message)


@router.message(F.text == texts.BUTTON_SUPPORT)
async def help_contact(message: Message) -> None:
    await handle_support(message)


@router.message(F.text == texts.BUTTON_INFO)
async def info_repeat(message: Message) -> None:
    await handle_info(message)


@router.message(F.text)
async def any_message(message: Message) -> None:
    await handle_any_message(message)
