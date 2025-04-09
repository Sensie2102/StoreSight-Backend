from passlib.context import CryptContext
from typing import Annotated
import os
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from src.db import User
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    email: str
    password: str

class DeleteUserRequest(BaseModel):
    password: str
    

class Token(BaseModel):
    access_token: str
    token_type: str

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/google/callback')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(password: str,hash: str) -> bool:
    return bcrypt_context.verify(password, hash)

def create_hash(password: str) -> str:
    return bcrypt_context.hash(password)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return {"email": email, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired")
    
async def add_user_to_db(session, email: str, password: str = None):
    if password:
        hashed_password = create_hash(password)
    else:
        hashed_password = None 

    new_user = User(
        email=email,
        password=hashed_password,
        google_oauth_token=(password is None),  
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
