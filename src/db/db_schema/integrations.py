from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .base import Base
import uuid

class Integrations(Base):
    __tablename__ = 'integrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    platform = Column(String(50), nullable=False)  
    store_name = Column(String(255), nullable=True)

    refresh_token = Column(Text, nullable=False)
    access_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    marketplace_id = Column(String(100), nullable=True)  
    shop_url = Column(String(255), nullable=True)        

    # metadata = Column(JSONB, nullable=True)  

    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Integration(platform={self.platform}, user_id={self.user_id})>"
