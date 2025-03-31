from passlib.context import CryptContext
from typing import Annotated
import os
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer


ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

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
    