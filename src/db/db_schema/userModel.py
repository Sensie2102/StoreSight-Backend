from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
import uuid

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True)
    password = Column(String, nullable=True)
    google_oauth_token = Column(Boolean, default=False)
    connected_platforms = Column(JSONB, nullable=True)