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

paid_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=texts.BUTTON_INFO)],
        [KeyboardButton(text=texts.BUTTON_SUPPORT)],
    ],
    resize_keyboard=True,
    input_field_placeholder=texts.PLACEHOLDER,
)

def user_kb(is_paid: bool) -> ReplyKeyboardMarkup:
    return paid_kb if is_paid else main_kb

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=texts.BUTTON_APPROVE)],
        [KeyboardButton(text=texts.BUTTON_DENY)],
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


def rub_payment_kb(pay_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts.INLINE_PAY_QR, url=pay_url)],
            [
                InlineKeyboardButton(
                    text=texts.INLINE_SENT_RECEIPT,
                    callback_data="rub_receipt_sent",
                )
            ],
        ]
    )


def check_payment_kb(invoice_id: str, pay_url: str | None = None) -> InlineKeyboardMarkup:
    buttons = []
    if pay_url:
        buttons.append([InlineKeyboardButton(text=texts.INLINE_PAY_CRYPTO, url=pay_url)])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *buttons,
            [
                InlineKeyboardButton(
                    text=texts.INLINE_CHECK_PAYMENT,
                    callback_data=f"check_invoice:{invoice_id}",
                )
            ],
        ]
    )


def admin_action_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=texts.BUTTON_APPROVE,
                    callback_data=f"admin_approve:{user_id}",
                ),
                InlineKeyboardButton(
                    text=texts.BUTTON_DENY,
                    callback_data=f"admin_deny:{user_id}",
                ),
            ]
        ]
    )
