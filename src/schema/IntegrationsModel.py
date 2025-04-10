from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class IntegrationBase(BaseModel):
    platform: str
    store_name: Optional[str]
    refresh_token: str
    marketplace_id: Optional[str]
    shop_url: Optional[str]
    access_token_expires_at: Optional[datetime]
    last_synced_at: Optional[datetime]
    is_active: Optional[bool] = True

class IntegrationCreate(IntegrationBase):
    user_id: UUID

class IntegrationRead(IntegrationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True  # needed to convert SQLAlchemy objects into Pydantic
