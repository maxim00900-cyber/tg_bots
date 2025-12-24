from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, async_session
from app.config import get_settings


ROLE_ADMIN = "admin"
ROLE_MODERATOR = "moderator"
ROLE_USER = "user"


async def _get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.scalar(select(User).where(User.user_id == user_id))


async def _get_or_create_user(session: AsyncSession, user_id: int) -> tuple[User, bool]:
    user = await _get_user(session, user_id)
    if user:
        return user, False
    user = User(user_id=user_id)
    session.add(user)
    return user, True


def _set_payment_pending(user: User, paid_method: str, invoice_id: str | None) -> None:
    user.invoice_id = invoice_id
    user.paid_method = paid_method
    user.is_paid = False
    user.payment_status = "pending"
    user.paid_at = None
    user.decision_by = None
    user.decision_at = None


def _set_payment_status(user: User, status: str) -> None:
    user.is_paid = status == "paid"
    user.payment_status = status


async def set_user(user_id: int) -> None:
    async with async_session() as session:
        _, created = await _get_or_create_user(session, user_id)
        if created:
            await session.commit()


async def set_role(user_id: int, role: str) -> User:
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        user.role = role
        await session.commit()
        return user


async def get_role(user_id: int) -> str:
    async with async_session() as session:
        user = await _get_user(session, user_id)
        if not user or not user.role:
            return ROLE_USER
        return user.role


async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        return await _get_user(session, user_id)


async def set_invoice(user_id: int, invoice_id: str, paid_method: str) -> None:
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        _set_payment_pending(user, paid_method, str(invoice_id))
        await session.commit()


async def set_rub_pending(user_id: int) -> None:
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        _set_payment_pending(user, "rub", None)
        await session.commit()


async def mark_rub_receipt_sent(user_id: int) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return None
        if user.paid_method is None:
            user.paid_method = "rub"
        _set_payment_status(user, "receipt_sent")
        await session.commit()
        return user


async def mark_paid_by_invoice(invoice_id: str, paid_method: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.invoice_id == str(invoice_id)))
        if not user:
            return None
        _set_payment_status(user, "paid")
        user.paid_method = paid_method
        user.paid_at = datetime.utcnow()
        await session.commit()
        return user


async def approve_by_staff(user_id: int, staff_id: int, paid_method: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return None
        _set_payment_status(user, "paid")
        user.paid_method = paid_method
        user.paid_at = datetime.utcnow()
        user.decision_by = staff_id
        user.decision_at = datetime.utcnow()
        await session.commit()
        return user


async def mark_expired_by_invoice(invoice_id: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.invoice_id == str(invoice_id)))
        if not user:
            return None
        _set_payment_status(user, "expired")
        user.paid_at = None
        await session.commit()
        return user


async def mark_failed_by_invoice(invoice_id: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.invoice_id == str(invoice_id)))
        if not user:
            return None
        _set_payment_status(user, "failed")
        user.paid_at = None
        await session.commit()
        return user


async def mark_failed_by_user(user_id: int, paid_method: str | None = None) -> User | None:
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        _set_payment_status(user, "failed")
        user.paid_at = None
        if paid_method is not None:
            user.paid_method = paid_method
        await session.commit()
        return user


async def deny_by_staff(user_id: int, staff_id: int, paid_method: str | None = None) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return None
        _set_payment_status(user, "failed")
        user.paid_at = None
        user.invoice_id = None
        if paid_method is not None:
            user.paid_method = paid_method
        user.decision_by = staff_id
        user.decision_at = datetime.utcnow()
        await session.commit()
        return user


async def get_users_by_roles(roles: list[str]) -> list[User]:
    async with async_session() as session:
        result = await session.scalars(select(User).where(User.role.in_(roles)))
        return list(result)


async def get_staff_ids() -> list[int]:
    settings = get_settings()
    staff_ids = set(settings.admin_chat_ids)
    users = await get_users_by_roles([ROLE_ADMIN, ROLE_MODERATOR])
    for user in users:
        staff_ids.add(user.user_id)
    return sorted(staff_ids)


async def get_pending_users_page(limit: int = 10, offset: int = 0) -> list[User]:
    async with async_session() as session:
        result = await session.scalars(
            select(User)
            .where(User.payment_status == "receipt_sent", User.decision_at.is_(None))
            .order_by(User.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result)


async def count_pending_users() -> int:
    async with async_session() as session:
        return await session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.payment_status == "receipt_sent", User.decision_at.is_(None))
        )
