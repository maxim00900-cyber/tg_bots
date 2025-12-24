from app.config import get_settings
from app.text_keys import TEXT_OVERRIDE_KEYS

_settings = get_settings()

PRICE_RUB = _settings.price_rub



PRICE_CURRENCY = _settings.price_currency

PRICE_TEXT = f"{PRICE_RUB} {PRICE_CURRENCY}"

PRICE_USDT = _settings.price_usdt

PRICE_USDT_TEXT = f"{PRICE_USDT} USDT"

WELCOME_TEXT = (
    "Привет! 👋\n"
    "Здесь ты получишь доступ к сервису, который предоставляет:\n\n"
    "✅ Рабочие аудио/видео-звонки в Telegram и WhatsApp\n"
    "✅ YouTube и Roblox без ограничений\n"
    "✅ Быстрый мобильный интернет — где бы ты ни находился\n\n"
    f"💰 Стоимость доступа: {PRICE_TEXT}\n"
    "Нажми кнопку ниже, чтобы продолжить 👇"
)

HELP_TEXT = (
    "Здесь ты можешь получить доступ к сервису без ограничений.\n"
    "Для продолжения выбери действие с помощью кнопок ниже 👇"
)

PAID_TEXT = f"💳 Получить доступ — {PRICE_TEXT}"

SUPPORT_TEXT = (
    "Если у тебя есть вопросы, напиши администратору 💬\n"
    f"{_settings.support_contact}"
)

PAY_RUB_QR_TEXT = (
    "Чтобы оплатить доступ в рублях, нажми кнопку ниже👇\n\n"
    f"Сумма к оплате: {PRICE_TEXT}\n"
    "После оплаты отправь чек в этот чат и нажми кнопку «Я отправил чек»."
)

PAY_USDT_TEXT = (
    "Чтобы оплатить доступ криптовалютой, нажми кнопку ниже👇\n\n"
    f"Сумма к оплате: {PRICE_USDT_TEXT}\n"
    "После оплаты нажми кнопку «Проверить оплату»."
)

ACCESS_TEXT = (
    "✅ Оплата подтверждена!\n\n"
    "Теперь переходи и устанавливай сервис:\n"
    "@rsconnect_bot"
)

PAYMENT_PENDING_TEXT = "Доступ еще не оплачен. Попробуй проверить чуть позже."

PAYMENT_EXPIRED_TEXT = "Платеж истек. Создай новый счет."

PAYMENT_FAILED_TEXT = "Платеж не прошел. Попробуй создать новый счет."

PAYMENT_ERROR_TEXT = "Не удалось проверить оплату. Попробуй позже."

PAYMENT_RUB_DISABLED_TEXT = "Оплата в рублях временно недоступна. Попробуй позже."

RECEIPT_RECEIVED_TEXT = "Чек получен. Нажми кнопку «Я отправил чек»."

RECEIPT_SENT_TEXT = "Спасибо! Чек отправлен администратору. Ожидай подтверждения."

DEFAULT_TEXT = "Для работы с ботом используй кнопки ниже 👇"

ADMIN_WELCOME_TEXT = "Добро пожаловать в админ панель"

ADMIN_ONLY_TEXT = "Команда доступна только администратору."

APPROVE_USAGE_TEXT = "Использование: /approve <user_id>"

DENY_USAGE_TEXT = "Использование: /deny <user_id>"

ADMIN_ALREADY_HANDLED_TEXT = "Запрос уже обработан."

ADMIN_BANNED_USER_TEXT = "Пользователь заблокирован, доступ выдать нельзя."

ADMIN_ADD_USAGE_TEXT = "Использование: /admin_add <user_id>"
ADMIN_REMOVE_USAGE_TEXT = "Использование: /admin_remove <user_id>"
ADMIN_ADDED_TEXT = "Администратор добавлен."
ADMIN_REMOVED_TEXT = "Администратор удален."

APPROVE_SUCCESS_TEXT = "Доступ выдан."

DENY_SUCCESS_TEXT = "Оплата отклонена."

USER_APPROVED_TEXT = (
    "✅ Оплата подтверждена!\n\n"
    "Теперь переходи и устанавливай сервис:\n"
    "@rsconnect_bot"
)

USER_DENIED_TEXT = "❌ Оплата отклонена. Если это ошибка, напиши в поддержку."

USER_NOT_FOUND_TEXT = "Пользователь не найден."

BAN_USAGE_TEXT = "Использование: /ban <user_id>"
UNBAN_USAGE_TEXT = "Использование: /unban <user_id>"
BAN_SUCCESS_TEXT = "Пользователь заблокирован."
UNBAN_SUCCESS_TEXT = "Пользователь разблокирован."
BANNED_TEXT = "Доступ ограничен. Обратись в поддержку."


BUTTON_PAY = f"💳 Оплатить {PRICE_TEXT}"

BUTTON_SUPPORT = "💬 Поддержка"

BUTTON_INFO = "ℹ️ Получить доступ"

BUTTON_APPROVE = "Разрешить доступ"

BUTTON_DENY = "Отклонить доступ"

BUTTON_BAN = "Забанить"

BUTTON_ADMIN_APPROVE_HELP = "Выдать доступ"
BUTTON_ADMIN_DENY_HELP = "Отклонить доступ"
BUTTON_ADMIN_BAN_HELP = "Забанить пользователя"
BUTTON_ADMIN_UNBAN_HELP = "Разбанить пользователя"

BUTTON_ADMIN_ADD_HELP = "Добавить админа"
BUTTON_ADMIN_REMOVE_HELP = "Снять админа"

PLACEHOLDER = "Выберите пункт меню..."

INLINE_PAY_RUB = "💰 В рублях"

INLINE_PAY_USDT = "🪙 В криптовалюте"

INLINE_CHECK_PAYMENT = "✅ Проверить оплату"

INLINE_PAY_QR = "📲 Оплатить по СБП"

INLINE_SENT_RECEIPT = "✅ Я отправил чек"

INLINE_PAY_CRYPTO = "💳 Оплатить"


_TEXT_OVERRIDES = _settings.text_overrides


def _apply_overrides() -> None:
    for key in TEXT_OVERRIDE_KEYS:
        override = _TEXT_OVERRIDES.get(key)
        if override is not None:
            globals()[key] = override


__OVERRIDES_APPLIED__ = True
_apply_overrides()
