import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    engine = create_engine(DATABASE_URL)
    if not database_exists(engine.url):
        raise ConnectionError(f"{DB_NAME} not found at {DB_HOST}:{DB_PORT}")
    return engine

def get_session():
    try:
        engine = get_engine()
        session = sessionmaker(bind=engine)
        return session
    except ConnectionError as e:
        print("Could not create a session",str(e))
        return None