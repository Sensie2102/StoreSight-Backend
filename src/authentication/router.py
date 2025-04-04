from fastapi import APIRouter,status,HTTPException, Depends, Request
from src.db import writable_session, User
from src.schema import UserResponse
from sqlalchemy import select
from .jwtAuth import generate_jwt_token,authenticate_user
from .utils import  add_user_to_db, CreateUserRequest,Token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from .googleOauth import return_google_url, get_user_details

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


#Authenticate username and password
@router.post("/signup",status_code=status.HTTP_200_OK,response_model=UserResponse)
async def create_new_user(request: CreateUserRequest):
    async with writable_session() as session:
        existing = await session.execute(select(User).where(User.email == request.email))
        existing = existing.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists")
        
        return await add_user_to_db(session=session,email=request.email,password=request.password)

#Get access token for username and password request 
@router.post("/token",status_code=status.HTTP_200_OK,response_model=Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username,form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = generate_jwt_token(user.email,user.id,timedelta(minutes=20))
    
    return {"access_token":token,"token_type":"bearer"}
            
#Google Oauth Process
@router.get("/google/login")
async def google_login(request:Request):
    return await return_google_url(request)

@router.get("/google/callback",response_model=Token)
async def google_auth(request: Request):
    return await get_user_details(request=request)