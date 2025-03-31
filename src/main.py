from fastapi import FastAPI,HTTPException,status,Depends
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware 
from src.authentication.router import router
from src.authentication.utils import get_current_user


app = FastAPI()

app.include_router(router)

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