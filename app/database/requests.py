from datetime import datetime
from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select


async def set_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))

        if not user:
            session.add(User(user_id=user_id))
            await session.commit()


async def get_user(user_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.user_id == user_id))


async def set_invoice(user_id, invoice_id, paid_method):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            user = User(user_id=user_id)
            session.add(user)
        user.invoice_id = str(invoice_id)
        user.paid_method = paid_method
        user.is_paid = False
        user.paid_at = None
        await session.commit()

async def set_rub_pending(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if not user:
            user = User(user_id=user_id)
            session.add(user)
        user.invoice_id = None
        user.paid_method = "rub"
        user.is_paid = False
        user.paid_at = None
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
