from datetime import datetime
from typing import Literal

from sqlalchemy import update

from app.database.models import User, async_session
from app.database.repository import (
    get_admin_ids as repo_get_admin_ids,
    get_or_create_user as repo_get_or_create_user,
    get_user as repo_get_user,
    get_user_by_invoice as repo_get_user_by_invoice,
)


PaymentStatus = Literal["pending", "receipt_sent", "paid", "expired", "failed"]
PaidMethod = Literal["rub", "crypto"]


def _set_payment_pending(user: User, paid_method: PaidMethod, invoice_id: str | None) -> None:
    user.invoice_id = invoice_id
    user.paid_method = paid_method
    user.is_paid = False
    user.payment_status = "pending"
    user.paid_at = None
    user.decision_by = None
    user.decision_at = None


def _set_payment_status(user: User, status: PaymentStatus) -> None:
    user.is_paid = status == "paid"
    user.payment_status = status


async def set_user(user_id: int) -> None:
    async with async_session() as session:
        _, created = await repo_get_or_create_user(session, user_id)
        if created:
            await session.commit()


async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        return await repo_get_user(session, user_id)


async def is_user_banned(user_id: int) -> bool:
    async with async_session() as session:
        user = await repo_get_user(session, user_id)
        return bool(user and user.is_banned)


async def is_user_admin(user_id: int) -> bool:
    async with async_session() as session:
        user = await repo_get_user(session, user_id)
        return bool(user and user.is_admin)


async def set_invoice(user_id: int, invoice_id: str, paid_method: PaidMethod) -> None:
    async with async_session() as session:
        user, _ = await repo_get_or_create_user(session, user_id)
        _set_payment_pending(user, paid_method, str(invoice_id))
        await session.commit()


async def set_rub_pending(user_id: int) -> None:
    async with async_session() as session:
        user, _ = await repo_get_or_create_user(session, user_id)
        _set_payment_pending(user, "rub", None)
        await session.commit()


async def add_admin(user_id: int) -> User:
    async with async_session() as session:
        user, _ = await repo_get_or_create_user(session, user_id)
        user.is_admin = True
        await session.commit()
        return user


async def remove_admin(user_id: int) -> User | None:
    async with async_session() as session:
        user = await repo_get_user(session, user_id)
        if not user:
            return None
        user.is_admin = False
        await session.commit()
        return user


async def get_admin_ids() -> list[int]:
    async with async_session() as session:
        return await repo_get_admin_ids(session)


async def ban_user(user_id: int) -> User:
    async with async_session() as session:
        user, _ = await repo_get_or_create_user(session, user_id)
        user.is_banned = True
        await session.commit()
        return user


async def unban_user(user_id: int) -> User | None:
    async with async_session() as session:
        user = await repo_get_user(session, user_id)
        if not user:
            return None
        user.is_banned = False
        await session.commit()
        return user


async def mark_rub_receipt_sent(user_id: int) -> User | None:
    async with async_session() as session:
        user = await repo_get_user(session, user_id)
        if not user:
            return None
        if user.paid_method is None:
            user.paid_method = "rub"
        _set_payment_status(user, "receipt_sent")
        await session.commit()
        return user


async def mark_paid_by_invoice(invoice_id: str, paid_method: PaidMethod) -> User | None:
    async with async_session() as session:
        user = await repo_get_user_by_invoice(session, invoice_id)
        if not user:
            return None
        _set_payment_status(user, "paid")
        user.paid_method = paid_method
        user.paid_at = datetime.utcnow()
        await session.commit()
        return user


async def approve_by_staff(user_id: int, staff_id: int, paid_method: PaidMethod) -> User | None:
    async with async_session() as session:
        paid_at = datetime.utcnow()
        result = await session.execute(
            update(User)
            .where(
                User.user_id == user_id,
                User.decision_at.is_(None),
                User.payment_status.in_(["pending", "receipt_sent"]),
            )
            .values(
                is_paid=True,
                payment_status="paid",
                paid_method=paid_method,
                paid_at=paid_at,
                decision_by=staff_id,
                decision_at=paid_at,
            )
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None
        await session.commit()
        return user


async def mark_expired_by_invoice(invoice_id: str) -> User | None:
    async with async_session() as session:
        user = await repo_get_user_by_invoice(session, invoice_id)
        if not user:
            return None
        _set_payment_status(user, "expired")
        user.paid_at = None
        await session.commit()
        return user


async def mark_failed_by_invoice(invoice_id: str) -> User | None:
    async with async_session() as session:
        user = await repo_get_user_by_invoice(session, invoice_id)
        if not user:
            return None
        _set_payment_status(user, "failed")
        user.paid_at = None
        await session.commit()
        return user


async def mark_failed_by_user(user_id: int, paid_method: PaidMethod | None = None) -> User | None:
    async with async_session() as session:
        user, _ = await repo_get_or_create_user(session, user_id)
        _set_payment_status(user, "failed")
        user.paid_at = None
        if paid_method is not None:
            user.paid_method = paid_method
        await session.commit()
        return user


async def deny_by_staff(user_id: int, staff_id: int, paid_method: PaidMethod | None = None) -> User | None:
    async with async_session() as session:
        values = {
            "is_paid": False,
            "payment_status": "failed",
            "paid_at": None,
            "invoice_id": None,
            "decision_by": staff_id,
            "decision_at": datetime.utcnow(),
        }
        if paid_method is not None:
            values["paid_method"] = paid_method
        result = await session.execute(
            update(User)
            .where(
                User.user_id == user_id,
                User.decision_at.is_(None),
                User.payment_status.in_(["pending", "receipt_sent"]),
            )
            .values(**values)
            .returning(User)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None
        await session.commit()
        return user
