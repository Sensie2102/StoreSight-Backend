from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class User(Base):
    __tablename__ = 'users'

    email = Column(String, primary_key=True)
    password = Column(String, nullable=True)
    google_oauth_token = Column(String, nullable=True)
    connected_platforms = Column(JSONB, nullable=True)