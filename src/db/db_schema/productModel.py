from .base import Base  
from sqlalchemy import Column, String,TIMESTAMP, ForeignKey, Text, DECIMAL, Integer
from sqlalchemy.dialects.postgresql import UUID



class Product(Base):
    __tablename__ = "products"

    id = Column(String, nullable=False,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    title = Column(String)
    description = Column(Text)
    vendor = Column(String)
    product_type = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class Variant(Base):
    __tablename__ = "variants"

    id = Column(String, nullable=False,primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    platform = Column(String, nullable=False)
    title = Column(String)
    sku = Column(String)
    price = Column(DECIMAL(10, 2))
    inventory_quantity = Column(Integer)