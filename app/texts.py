from app.config import get_settings
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


def _override(name, value):
    return _TEXT_OVERRIDES.get(name, value)


__OVERRIDES_APPLIED__ = True
WELCOME_TEXT = _override('WELCOME_TEXT', WELCOME_TEXT)
HELP_TEXT = _override('HELP_TEXT', HELP_TEXT)
PAID_TEXT = _override('PAID_TEXT', PAID_TEXT)
SUPPORT_TEXT = _override('SUPPORT_TEXT', SUPPORT_TEXT)
PAY_RUB_QR_TEXT = _override('PAY_RUB_QR_TEXT', PAY_RUB_QR_TEXT)
PAY_USDT_TEXT = _override('PAY_USDT_TEXT', PAY_USDT_TEXT)
ACCESS_TEXT = _override('ACCESS_TEXT', ACCESS_TEXT)
PAYMENT_PENDING_TEXT = _override('PAYMENT_PENDING_TEXT', PAYMENT_PENDING_TEXT)
PAYMENT_EXPIRED_TEXT = _override('PAYMENT_EXPIRED_TEXT', PAYMENT_EXPIRED_TEXT)
PAYMENT_FAILED_TEXT = _override('PAYMENT_FAILED_TEXT', PAYMENT_FAILED_TEXT)
PAYMENT_ERROR_TEXT = _override('PAYMENT_ERROR_TEXT', PAYMENT_ERROR_TEXT)
PAYMENT_RUB_DISABLED_TEXT = _override('PAYMENT_RUB_DISABLED_TEXT', PAYMENT_RUB_DISABLED_TEXT)
RECEIPT_RECEIVED_TEXT = _override('RECEIPT_RECEIVED_TEXT', RECEIPT_RECEIVED_TEXT)
RECEIPT_SENT_TEXT = _override('RECEIPT_SENT_TEXT', RECEIPT_SENT_TEXT)
DEFAULT_TEXT = _override('DEFAULT_TEXT', DEFAULT_TEXT)
ADMIN_WELCOME_TEXT = _override('ADMIN_WELCOME_TEXT', ADMIN_WELCOME_TEXT)
ADMIN_ONLY_TEXT = _override('ADMIN_ONLY_TEXT', ADMIN_ONLY_TEXT)
APPROVE_USAGE_TEXT = _override('APPROVE_USAGE_TEXT', APPROVE_USAGE_TEXT)
DENY_USAGE_TEXT = _override('DENY_USAGE_TEXT', DENY_USAGE_TEXT)
ADMIN_ALREADY_HANDLED_TEXT = _override('ADMIN_ALREADY_HANDLED_TEXT', ADMIN_ALREADY_HANDLED_TEXT)
APPROVE_SUCCESS_TEXT = _override('APPROVE_SUCCESS_TEXT', APPROVE_SUCCESS_TEXT)
DENY_SUCCESS_TEXT = _override('DENY_SUCCESS_TEXT', DENY_SUCCESS_TEXT)
USER_APPROVED_TEXT = _override('USER_APPROVED_TEXT', USER_APPROVED_TEXT)
USER_DENIED_TEXT = _override('USER_DENIED_TEXT', USER_DENIED_TEXT)
USER_NOT_FOUND_TEXT = _override('USER_NOT_FOUND_TEXT', USER_NOT_FOUND_TEXT)
BAN_USAGE_TEXT = _override('BAN_USAGE_TEXT', BAN_USAGE_TEXT)
UNBAN_USAGE_TEXT = _override('UNBAN_USAGE_TEXT', UNBAN_USAGE_TEXT)
BAN_SUCCESS_TEXT = _override('BAN_SUCCESS_TEXT', BAN_SUCCESS_TEXT)
UNBAN_SUCCESS_TEXT = _override('UNBAN_SUCCESS_TEXT', UNBAN_SUCCESS_TEXT)
BANNED_TEXT = _override('BANNED_TEXT', BANNED_TEXT)
BUTTON_PAY = _override('BUTTON_PAY', BUTTON_PAY)
BUTTON_SUPPORT = _override('BUTTON_SUPPORT', BUTTON_SUPPORT)
BUTTON_INFO = _override('BUTTON_INFO', BUTTON_INFO)
BUTTON_APPROVE = _override('BUTTON_APPROVE', BUTTON_APPROVE)
BUTTON_DENY = _override('BUTTON_DENY', BUTTON_DENY)
BUTTON_BAN = _override('BUTTON_BAN', BUTTON_BAN)
BUTTON_ADMIN_APPROVE_HELP = _override('BUTTON_ADMIN_APPROVE_HELP', BUTTON_ADMIN_APPROVE_HELP)
BUTTON_ADMIN_DENY_HELP = _override('BUTTON_ADMIN_DENY_HELP', BUTTON_ADMIN_DENY_HELP)
BUTTON_ADMIN_BAN_HELP = _override('BUTTON_ADMIN_BAN_HELP', BUTTON_ADMIN_BAN_HELP)
BUTTON_ADMIN_UNBAN_HELP = _override('BUTTON_ADMIN_UNBAN_HELP', BUTTON_ADMIN_UNBAN_HELP)
PLACEHOLDER = _override('PLACEHOLDER', PLACEHOLDER)
INLINE_PAY_RUB = _override('INLINE_PAY_RUB', INLINE_PAY_RUB)
INLINE_PAY_USDT = _override('INLINE_PAY_USDT', INLINE_PAY_USDT)
INLINE_CHECK_PAYMENT = _override('INLINE_CHECK_PAYMENT', INLINE_CHECK_PAYMENT)
INLINE_PAY_QR = _override('INLINE_PAY_QR', INLINE_PAY_QR)
INLINE_SENT_RECEIPT = _override('INLINE_SENT_RECEIPT', INLINE_SENT_RECEIPT)
INLINE_PAY_CRYPTO = _override('INLINE_PAY_CRYPTO', INLINE_PAY_CRYPTO)
