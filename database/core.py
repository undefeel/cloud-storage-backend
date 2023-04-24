from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import Config

engine = create_async_engine(Config.database_url)

Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_sessiom() -> AsyncSession:
    local_session = Session()
    try:
        yield local_session
    finally:
        await local_session.close()


class Base(DeclarativeBase):
    pass
