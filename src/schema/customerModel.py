from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CustomerCreate(BaseModel):
    external_id: str
    platform: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    orders_count: Optional[int]
    total_spent: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class CustomerResponse(CustomerCreate):
    id: UUID

