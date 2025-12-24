from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app import keyboards as kb
from app import texts
import app.database.requests as rq

router = Router()


@router.message(CommandStart())
async def command_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(texts.WELCOME_TEXT, reply_markup=kb.main_kb)


@router.message(Command(commands="help"))
async def command_help(message: Message):
    await message.answer(texts.HELP_TEXT, reply_markup=kb.main_kb)


@router.message(F.text == texts.BUTTON_PAY)
async def paid(message: Message):
    await message.answer(texts.PAID_TEXT, reply_markup=kb.payment_kb)


@router.message(F.text == texts.BUTTON_SUPPORT)
async def help_contact(message: Message):
    await message.answer(texts.SUPPORT_TEXT, reply_markup=kb.main_kb)


@router.message(F.text)
async def any_message(message: Message):
    await message.answer(texts.DEFAULT_TEXT, reply_markup=kb.main_kb)
