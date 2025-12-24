from datetime import datetime

from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    role: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    paid_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    decision_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    decision_at: Mapped[datetime | None] = mapped_column(nullable=True)


async def async_main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
