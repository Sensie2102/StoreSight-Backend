import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy_utils import database_exists
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SYNC_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_sync_engine():
    return create_engine(SYNC_DATABASE_URL)

def validate_database_exists():
    sync_engine = create_engine(SYNC_DATABASE_URL)
    if not database_exists(sync_engine.url):
        raise ConnectionError(f"Database '{DB_NAME}' not found at {DB_HOST}:{DB_PORT}")


validate_database_exists()
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
