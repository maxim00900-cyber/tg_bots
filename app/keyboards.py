from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app import texts


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=texts.BUTTON_PAY)],
        [KeyboardButton(text=texts.BUTTON_SUPPORT)],
    ],
    resize_keyboard=True,
    input_field_placeholder=texts.PLACEHOLDER,
)

payment_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=texts.INLINE_PAY_RUB, callback_data="pay_rub")],
        [InlineKeyboardButton(text=texts.INLINE_PAY_USDT, callback_data="pay_usdt")],
    ]
)

def check_payment_kb(invoice_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.INLINE_CHECK_PAYMENT,
                    callback_data=f"check_invoice:{invoice_id}",
                )
            ]
        ]
    )