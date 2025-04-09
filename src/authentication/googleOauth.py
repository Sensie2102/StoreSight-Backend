from authlib.integrations.starlette_client import OAuth
from fastapi.responses import RedirectResponse
from fastapi import HTTPException,status
import os
from src.db import writable_session, User
from sqlalchemy import select
from .utils import add_user_to_db
from .jwtAuth import generate_jwt_token
from datetime import timedelta
from authlib.integrations.base_client import OAuthError

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

async def return_google_url(request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def get_user_details(request):    
    try:
        user_info = await oauth.google.authorize_access_token(request)     
    except OAuthError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
    
    email = user_info.get("userinfo").get("email")

    name = user_info.get("userinfo").get("name")

    async with writable_session() as session:
        existing_user = await session.execute(select(User).where(User.email == email))
        existing_user = existing_user.scalar_one_or_none()
        
        if not existing_user:
            existing_user = await add_user_to_db(session=session,email=email)
        
        token = generate_jwt_token(existing_user.email, existing_user.id, timedelta(minutes=20))
    
    return RedirectResponse(url=f"http://localhost:5173/auth/google/callback?access_token={token}")
    
    
            
    