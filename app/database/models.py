from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    paid_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
