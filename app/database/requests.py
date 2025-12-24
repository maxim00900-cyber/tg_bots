from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, async_session


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


def _set_payment_status(user: User, status: str) -> None:
    user.is_paid = status == "paid"
    user.payment_status = status


async def set_user(user_id: int) -> None:
    async with async_session() as session:
        _, created = await _get_or_create_user(session, user_id)
        if created:
            await session.commit()


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


async def mark_paid_by_user(user_id: int, paid_method: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return None
        _set_payment_status(user, "paid")
        user.paid_method = paid_method
        user.paid_at = datetime.utcnow()
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


async def reset_payment(user_id: int, paid_method: str | None = None) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return None
        _set_payment_status(user, "failed")
        user.paid_at = None
        user.invoice_id = None
        if paid_method is not None:
            user.paid_method = paid_method
        await session.commit()
        return user


async def get_pending_users(limit: int = 10) -> list[User]:
    async with async_session() as session:
        result = await session.scalars(
            select(User)
            .where(User.payment_status == "pending")
            .order_by(User.id.desc())
            .limit(limit)
        )
        return list(result)
