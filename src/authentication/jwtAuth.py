from datetime import timedelta, datetime, timezone
from jose import jwt
from uuid import UUID
import os
from src.schema import UserResponse
from typing import Union
from src.db import readonly_session, User
from sqlalchemy import select
from src.authentication.utils import verify_password



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def generate_jwt_token(email:str, id: UUID,expires_delta: timedelta):
    payload = {'sub':email,'id':str(id)}
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({'exp': expires})
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)


async def authenticate_user(email:str,password:str) -> Union[bool,UserResponse]:
    async with readonly_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and verify_password(password,user.password):
            return UserResponse.model_validate(user)
        return False
        

    