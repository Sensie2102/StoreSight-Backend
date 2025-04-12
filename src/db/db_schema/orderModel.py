from .base import Base
from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    email = Column(String)
    financial_status = Column(String)
    fulfillment_status = Column(String)
    total_price = Column(DECIMAL(10, 2))
    currency = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, nullable=False,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"))
    quantity = Column(Integer)
    price = Column(DECIMAL(10, 2))
    title = Column(String)
    sku = Column(String)
    platform = Column(String, nullable=False)