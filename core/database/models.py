import os

from sqlalchemy import BigInteger, String, LargeBinary, Boolean, TIMESTAMP, DATETIME, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import  load_dotenv
from sqlalchemy.sql import text

load_dotenv()

engine = create_async_engine(url=os.getenv('DATABASE_URL'))

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserState(Base):
    __tablename__ = 'user_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)
    datetime = mapped_column(TIMESTAMP(timezone=True))
    action = mapped_column(String(1024)) # увеличенный лимит для сохранения сообщения пользователя

class TimeState(Base):
    __tablename__ = 'time_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)

    action = mapped_column(String(1024)) # увеличенный лимит для сохранения сообщения пользователя

    time_delta = mapped_column(BigInteger) # записываем время ответа от модели в секундах

class EstimateState(Base):
    __tablename__ = 'est_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id = mapped_column(BigInteger)




    est = mapped_column(String(50)) # оценки good\bad




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        await conn.commit()