from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, nullable=False,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    orders_count = Column(Integer)
    total_spent = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
