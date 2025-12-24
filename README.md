## Overview

Telegram bot for paid access with two payment paths:
- Crypto payments via CryptoBot API (USDT invoices).
- Ruble payments via external URL + manual receipt approval by staff.

The bot uses aiogram, SQLite by default, and env-based configuration.

## Project Structure

root/
- `main.py` Entry point. Loads settings, sets up logging, runs polling, initializes DB.
- `requirements.txt` Python dependencies.
- `.env.example` Template for required environment variables.
- `db.sqlite3` Default SQLite DB (local development).
- `app/` Main package.
  - `config.py` Loads env config and validates required settings.
  - `text_keys.py` Single source of truth for all text override keys.
  - `texts.py` All user-facing texts + override application.
  - `keyboards.py` Reply/inline keyboards for users and admins.
  - `cryptobot.py` CryptoBot API client (create/check invoices).
  - `services/`
    - `payments.py` Payment workflow logic (crypto and ruble flows).
    - `user_access.py` Unified helpers for user IDs and access checks.
    - `user_handlers.py` High-level handlers used by routers.
  - `routers/`
    - `common.py` User commands and main menu flow.
    - `crypto.py` Crypto payment callbacks.
    - `rub.py` Ruble payment callbacks and receipt uploads.
    - `admin.py` Admin commands and callbacks (approve/deny/ban/admins).
    - `admin_utils.py` Admin/staff checks and admin list helpers.
  - `database/`
    - `models.py` SQLAlchemy models and async engine/session.
    - `repository.py` Basic CRUD helpers (get/create users, get by invoice).
    - `requests.py` Business-level DB operations (mark paid/failed, ban, etc).

## Core Logic (High Level)

1) User starts bot:
   - `common.py` -> `user_handlers.handle_start()`
   - User is created in DB if new.
   - If admin/staff, shows admin keyboard.
   - If banned, shows banned text.
   - If paid, shows access text.
   - Otherwise shows welcome text and payment options.

2) Crypto payments (USDT):
   - `crypto.py` -> `user_handlers.handle_pay_usdt()`
   - Creates invoice via CryptoBot. If already active, returns pay link.
   - User checks status with "check_invoice".
   - Paid -> access granted; expired/failed -> user informed.

3) Ruble payments:
   - `rub.py` -> `user_handlers.handle_pay_rub()`
   - Returns pay URL and instructions.
   - User uploads receipt -> forwarded to staff.
   - User confirms "receipt sent" -> staff gets approval buttons.

4) Admin flow:
   - Owner (from `.env`) can add/remove admins.
   - Staff can approve/deny/bans via commands or inline buttons.
   - Decisions are stored with `decision_by` and `decision_at`.

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python main.py
```

## Admin Commands

```
/approve <user_id>      выдача доступа
/deny <user_id>         отказ
/ban <user_id>          бан
/unban <user_id>        разбан
/admin_add <user_id>    добавить админа (owner only)
/admin_remove <user_id> снять админа (owner only)
```

## Deployment Notes

- For simple hosting: run `python main.py` from the project directory.
- For production: use `systemd` and keep `.env` on the server.

Example `systemd` unit (`/etc/systemd/system/telegram-bot.service`):

```
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/telegram-bot
EnvironmentFile=/opt/telegram-bot/.env
ExecStart=/opt/telegram-bot/.venv/bin/python /opt/telegram-bot/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:
```
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo journalctl -u telegram-bot -f
```

## Database Schema (users)

- `id` Internal PK.
- `user_id` Telegram ID (unique).
- `is_paid` Access flag.
- `is_admin` Staff/admin flag (added by owner).
- `is_banned` Ban flag.
- `payment_status` `pending|receipt_sent|paid|expired|failed`.
- `paid_method` `rub|crypto`.
- `paid_at` UTC timestamp for payment.
- `invoice_id` CryptoBot invoice ID (unique).
- `decision_by` Admin who approved/denied.
- `decision_at` UTC time of decision.

## Environment Variables

Required for production:
- `TOKEN` Telegram bot token.
- `ADMIN_CHAT_ID` or `ADMIN_CHAT_IDS` Owner/admin list.
- `CRYPTOBOT_TOKEN` CryptoBot API token (for crypto payments).
- `RUB_PAY_URL` URL for ruble payments.
- `SUPPORT_CONTACT` Support contact text (shown to users).

Optional:
- `DATABASE_URL` Defaults to `sqlite+aiosqlite:///db.sqlite3`.
- `PRICE_RUB`, `PRICE_USDT`, `PRICE_CURRENCY` Price config.
- Text overrides: see `app/text_keys.py`.

Example `.env`:
```bash
TOKEN=
CRYPTOBOT_TOKEN=
RUB_PAY_URL=
ADMIN_CHAT_ID=
ADMIN_CHAT_IDS=
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
PRICE_RUB=269
PRICE_USDT=3.0
PRICE_CURRENCY=₽
SUPPORT_CONTACT=@support
```

## Text Overrides

You can override any text by setting env variables listed in `app/text_keys.py`.
Example:

```bash
WELCOME_TEXT=Custom welcome text\nSecond line
PAY_USDT_TEXT=Custom crypto payment text
```

---

## README (RU)

### Обзор

Telegram-бот для платного доступа с двумя вариантами оплаты:
- Крипто-оплата через CryptoBot (инвойсы USDT).
- Оплата в рублях через внешний URL + ручная проверка чека админом.

Бот построен на aiogram, по умолчанию использует SQLite и конфигурацию через `.env`.

### Структура проекта

root/
- `main.py` Точка входа. Загружает настройки, настраивает логирование, запускает polling, инициализирует БД.
- `requirements.txt` Зависимости Python.
- `.env.example` Шаблон переменных окружения.
- `db.sqlite3` SQLite БД для локальной разработки.
- `app/` Основной пакет.
  - `config.py` Загрузка настроек из `.env`, проверка обязательных параметров.
  - `text_keys.py` Единый список ключей для текстовых overrides.
  - `texts.py` Все тексты бота + применение overrides.
  - `keyboards.py` Клавиатуры для пользователей и админов.
  - `cryptobot.py` Клиент CryptoBot API.
  - `services/`
    - `payments.py` Логика оплат (crypto и rub).
    - `user_access.py` Единые проверки доступа и user_id.
    - `user_handlers.py` Высокоуровневые обработчики (используются роутерами).
  - `routers/`
    - `common.py` Основные команды и меню пользователя.
    - `crypto.py` Коллбеки крипто-оплаты.
    - `rub.py` Коллбеки рублевой оплаты и загрузки чеков.
    - `admin.py` Админские команды и коллбеки.
    - `admin_utils.py` Проверки прав админов и список staff.
  - `database/`
    - `models.py` SQLAlchemy модели и async engine/session.
    - `repository.py` CRUD помощники (получение/создание пользователя, поиск по инвойсу).
    - `requests.py` Бизнес-операции с БД (оплаты, бан, админы).

### Логика (кратко)

1) Старт:
   - `common.py` -> `user_handlers.handle_start()`
   - Пользователь создается в БД.
   - Админ/сотрудник видит админ-меню.
   - Забаненный получает сообщение о бане.
   - Оплативший получает доступ.
   - Остальные получают приветствие и кнопки оплаты.

2) Крипто-оплата (USDT):
   - `crypto.py` -> `user_handlers.handle_pay_usdt()`
   - Создается инвойс, пользователю выдается ссылка.
   - Кнопка проверки статуса "check_invoice".
   - При оплате доступ выдается, при ошибке/истечении показывается сообщение.

3) Оплата в рублях:
   - `rub.py` -> `user_handlers.handle_pay_rub()`
   - Пользователь получает ссылку на оплату и инструкцию.
   - Чек отправляется админам, пользователь подтверждает отправку.

4) Админы:
   - Owner из `.env` может добавлять/удалять админов.
   - Staff может approve/deny/ban через команды или кнопки.
   - Решения пишутся в поля `decision_by` и `decision_at`.

### Быстрый старт

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python main.py
```

### Команды админа

```
/approve <user_id>      выдать доступ
/deny <user_id>         отказать
/ban <user_id>          забанить
/unban <user_id>        разбанить
/admin_add <user_id>    добавить админа (только owner)
/admin_remove <user_id> снять админа (только owner)
```

### Деплой

- Для простого запуска: `python main.py` из директории проекта.
- Для продакшена: использовать `systemd` и `.env` на сервере.

Пример `systemd` unit (`/etc/systemd/system/telegram-bot.service`):

```
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/telegram-bot
EnvironmentFile=/opt/telegram-bot/.env
ExecStart=/opt/telegram-bot/.venv/bin/python /opt/telegram-bot/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Включение и запуск:
```
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo journalctl -u telegram-bot -f
```

### База данных (users)

- `id` внутренний PK.
- `user_id` Telegram ID (уникальный).
- `is_paid` флаг доступа.
- `is_admin` админ/сотрудник.
- `is_banned` флаг бана.
- `payment_status` `pending|receipt_sent|paid|expired|failed`.
- `paid_method` `rub|crypto`.
- `paid_at` время оплаты (UTC).
- `invoice_id` инвойс CryptoBot.
- `decision_by` админ, принявший решение.
- `decision_at` время решения (UTC).

### Переменные окружения

Обязательные:
- `TOKEN` токен бота.
- `ADMIN_CHAT_ID` или `ADMIN_CHAT_IDS` список владельцев/админов.
- `CRYPTOBOT_TOKEN` токен CryptoBot.
- `RUB_PAY_URL` ссылка для оплаты в рублях.
- `SUPPORT_CONTACT` контакт поддержки.

Опционально:
- `DATABASE_URL` (по умолчанию `sqlite+aiosqlite:///db.sqlite3`).
- `PRICE_RUB`, `PRICE_USDT`, `PRICE_CURRENCY`.
- Переопределения текстов: см. `app/text_keys.py`.

Пример `.env`:
```bash
TOKEN=
CRYPTOBOT_TOKEN=
RUB_PAY_URL=
ADMIN_CHAT_ID=
ADMIN_CHAT_IDS=
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
PRICE_RUB=269
PRICE_USDT=3.0
PRICE_CURRENCY=₽
SUPPORT_CONTACT=@support
```

### Переопределение текстов

Можно переопределять любые тексты через `.env`, список ключей в `app/text_keys.py`.
