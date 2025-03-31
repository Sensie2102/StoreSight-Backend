from .database import get_sync_engine
from contextlib import asynccontextmanager
from src.db import get_session
from .db_schema import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

def create_all_tables():
    engine = get_sync_engine()
    Base.metadata.create_all(engine)
    print("Tables created.")

@asynccontextmanager
async def readonly_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session

@asynccontextmanager
async def writable_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise