from fastapi import FastAPI,HTTPException,status,Depends
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",status_code=status.HTTP_200_OK)
def authenticate():
    return {"message": "Hello World"}