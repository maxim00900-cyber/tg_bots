PRICE_RUB = 269
PRICE_CURRENCY = "₽"
PRICE_TEXT = f"{PRICE_RUB} {PRICE_CURRENCY}"
PRICE_USDT = 3.0
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
    "@sergei_kk"
)

PAY_RUB_TEXT = "Вы выбрали оплату в рублях"
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
    "@rsconnect_vpn"
)

PAYMENT_PENDING_TEXT = "Доступ еще не оплачен. Попробуй проверить чуть позже."
PAYMENT_EXPIRED_TEXT = "Платеж истек. Создай новый счет."
PAYMENT_ERROR_TEXT = "Не удалось проверить оплату. Попробуй позже."
PAYMENT_RUB_DISABLED_TEXT = "Оплата в рублях временно недоступна. Попробуй позже."
RECEIPT_RECEIVED_TEXT = "Чек получен. Нажми кнопку «Я отправил чек»."
RECEIPT_SENT_TEXT = "Спасибо! Чек отправлен администратору. Ожидай подтверждения."

DEFAULT_TEXT = "Для работы с ботом используй кнопки ниже 👇"

ADMIN_ONLY_TEXT = "Команда доступна только администратору."
APPROVE_USAGE_TEXT = "Использование: /approve <user_id>"
DENY_USAGE_TEXT = "Использование: /deny <user_id>"
APPROVE_SUCCESS_TEXT = "Доступ выдан."
DENY_SUCCESS_TEXT = "Оплата отклонена."
USER_APPROVED_TEXT = "✅ Оплата подтверждена. Доступ выдан."
USER_DENIED_TEXT = "❌ Оплата отклонена. Если это ошибка, напиши в поддержку."
USER_NOT_FOUND_TEXT = "Пользователь не найден."

BUTTON_PAY = f"💳 Оплатить {PRICE_TEXT}"
BUTTON_SUPPORT = "💬 Поддержка"
PLACEHOLDER = "Выберите пункт меню..."

INLINE_PAY_RUB = "💰 В рублях"
INLINE_PAY_USDT = "🪙 В криптовалюте"
INLINE_CHECK_PAYMENT = "✅ Проверить оплату"
INLINE_PAY_QR = "📲 Оплатить по СБП"
INLINE_SENT_RECEIPT = "✅ Я отправил чек"
INLINE_PAY_CRYPTO = "💳 Оплатить"
PAYMENT_FAILED_TEXT = "\u041f\u043b\u0430\u0442\u0435\u0436 \u043d\u0435 \u043f\u0440\u043e\u0448\u0435\u043b. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439 \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u043d\u043e\u0432\u044b\u0439 \u0441\u0447\u0435\u0442."

ADMIN_WELCOME_TEXT = "Админ-режим: используй кнопки ниже."
BUTTON_APPROVE = "\u0420\u0430\u0437\u0440\u0435\u0448\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f"
BUTTON_DENY = "\u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f"
BUTTON_INFO = "\u2139\ufe0f \u041f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f"
ADMIN_QUEUE_HEADER_TEXT = "Очередь ожидающих оплат:"
ADMIN_QUEUE_EMPTY_TEXT = "Нет ожидающих оплат."
