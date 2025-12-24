from datetime import datetime

from sqlalchemy import select

from app.database.models import User, async_session


async def _get_user(session, user_id: int) -> User | None:
    return await session.scalar(select(User).where(User.user_id == user_id))


async def _get_or_create_user(session, user_id: int) -> tuple[User, bool]:
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
    user.paid_at = None


async def set_user(user_id):
    async with async_session() as session:
        _, created = await _get_or_create_user(session, user_id)
        if created:
            await session.commit()


async def get_user(user_id):
    async with async_session() as session:
        return await _get_user(session, user_id)


async def set_invoice(user_id, invoice_id, paid_method):
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        _set_payment_pending(user, paid_method, str(invoice_id))
        await session.commit()


async def set_rub_pending(user_id):
    async with async_session() as session:
        user, _ = await _get_or_create_user(session, user_id)
        _set_payment_pending(user, "rub", None)
        await session.commit()


async def mark_paid_by_invoice(invoice_id, paid_method):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.invoice_id == str(invoice_id)))
        if not user:
            return None
        user.is_paid = True
        user.paid_method = paid_method
        user.paid_at = datetime.utcnow()
        await session.commit()
        return user
