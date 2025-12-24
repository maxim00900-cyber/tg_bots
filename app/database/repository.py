from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.scalar(select(User).where(User.user_id == user_id))


async def get_or_create_user(session: AsyncSession, user_id: int) -> tuple[User, bool]:
    user = await get_user(session, user_id)
    if user:
        return user, False
    user = User(user_id=user_id)
    session.add(user)
    return user, True


async def get_user_by_invoice(session: AsyncSession, invoice_id: str) -> User | None:
    return await session.scalar(select(User).where(User.invoice_id == str(invoice_id)))


async def get_admin_ids(session: AsyncSession) -> list[int]:
    result = await session.scalars(select(User.user_id).where(User.is_admin.is_(True)))
    return list(result)
