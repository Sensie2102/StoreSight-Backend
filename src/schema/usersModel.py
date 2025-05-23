from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict
from typing import Dict, Optional
from typing_extensions import Self

class User(BaseModel):
    id: UUID
    email: EmailStr
    password: Optional[str] = None
    google_oauth: Optional[str] = None
    platforms_connected: Dict[str,str] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)
    
    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        password = self.password
        google_oauth = self.google_oauth
        
        if not password and not google_oauth:
            raise ValueError("Either password or google_oauth token must be provided")
        
        return self

    