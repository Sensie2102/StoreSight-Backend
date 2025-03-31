from fastapi import APIRouter,status,HTTPException, Depends
from pydantic import BaseModel
from src.db import writable_session, User
from src.schema import UserResponse
from sqlalchemy import select
from src.authentication.jwtAuth import generate_jwt_token,authenticate_user
from src.authentication.utils import create_hash, verify_password
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from datetime import timedelta



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

class CreateUserRequest(BaseModel):
    email: str
    password: str

class DeleteUserRequest(BaseModel):
    password: str
    

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/signup",status_code=status.HTTP_200_OK,response_model=UserResponse)
async def create_new_user(request: CreateUserRequest):
    async with writable_session() as session:
        existing = await session.execute(select(User).where(User.email == request.email))
        existing = existing.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists")
        
        hashed_password = create_hash(request.password)
        new_user = User(
            email=request.email,
            password=hashed_password
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    return UserResponse.model_validate(new_user)

@router.post("/token",status_code=status.HTTP_200_OK,response_model=Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username,form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = generate_jwt_token(user.email,user.id,timedelta(minutes=20))
    
    return {"access_token":token,"token_type":"bearer"}
    

@router.delete("/",status_code=status.HTTP_200_OK)
async def delete_user(request: DeleteUserRequest, current_user: UserResponse):
    if not verify_password(request.password,current_user.password):
        raise HTTPException(status_code=403, detail="Incorrect password")
    async with writable_session() as session:
        user_to_delete = await session.get(User, current_user.id)    
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        await session.delete(user_to_delete)
        await session.commit()
    
    return {"message":"User successfully deleted!"}
            
            
        