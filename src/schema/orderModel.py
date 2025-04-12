from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class OrderCreate(BaseModel):
    external_id: str
    platform: str
    customer_id: Optional[str]
    email: Optional[str]
    financial_status: Optional[str]
    fulfillment_status: Optional[str]
    total_price: Optional[float]
    currency: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class OrderResponse(OrderCreate):
    id: UUID



class OrderItemCreate(BaseModel):
    external_id: str
    platform: str
    order_id: str
    product_id: Optional[str]
    variant_id: Optional[str]
    quantity: Optional[int]
    price: Optional[float]
    title: Optional[str]
    sku: Optional[str]

class OrderItemResponse(OrderItemCreate):
    id: UUID

