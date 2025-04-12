from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    external_id: str
    platform: str
    title: Optional[str]
    description: Optional[str]
    vendor: Optional[str]
    product_type: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class ProductResponse(ProductCreate):
    id: UUID
    model_config = ConfigDict(arbitrary_types_allowed=True)


class VariantCreate(BaseModel):
    external_id: str
    platform: str
    product_id: str
    title: Optional[str]
    sku: Optional[str]
    price: Optional[float]
    inventory_quantity: Optional[int]

class VariantResponse(VariantCreate):
    id: UUID
    model_config = ConfigDict(arbitrary_types_allowed=True)

