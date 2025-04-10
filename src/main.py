from fastapi import FastAPI,HTTPException,status,Depends
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware 
from src.authentication.router import router
from src.authentication.utils import get_current_user
from starlette.middleware.sessions import SessionMiddleware
import os
from src.authentication.utils import verify_password,DeleteUserRequest
from src.db import writable_session, User
from src.schema import UserResponse
from src.integrations.integrations_router import integrations_router
from src.analysis.pipeline_router import pipeline_router
app = FastAPI()

app.include_router(router)

app.include_router(integrations_router)

app.include_router(pipeline_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_dependency = Annotated[dict,Depends(get_current_user)]

@app.get("/",status_code=status.HTTP_200_OK)
async def authenticate(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return {"User": user}

#Delete User request
@router.delete("/",status_code=status.HTTP_200_OK)
async def delete_user(request: DeleteUserRequest, current_user:  Annotated[UserResponse, Depends(get_current_user)]):
    if not verify_password(request.password,current_user.password):
        raise HTTPException(status_code=403, detail="Incorrect password")
    async with writable_session() as session:
        user_to_delete = await session.get(User, current_user.id)    
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        await session.delete(user_to_delete)
        await session.commit()
    
    return {"message":"User successfully deleted!"}