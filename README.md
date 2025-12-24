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
  - `__init__.py` Package marker.
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
    - `__init__.py` Router aggregation.
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
