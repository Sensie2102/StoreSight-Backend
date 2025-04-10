from fastapi import APIRouter, Depends, Request, HTTPException
from .shopify_integerations import  shopify_callback,authorize_shopify,get_shopify_credentials
from ..authentication.utils import get_current_user
from ..schema import UserResponse
integrations_router = APIRouter(prefix="/integrations",tags=["integrations"])

@integrations_router.post("/integrations/shopify/auth")
async def shopify_auth(current_user: UserResponse = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await authorize_shopify(current_user.id)

@integrations_router.post("/integrations/shopify/callback")
async def shopify_callback(request:Request):
    return await shopify_callback(request)

@integrations_router.post("/integrations/shopify/credentials")
async def shopify_credentials(current_user: UserResponse = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await get_shopify_credentials(current_user.id)
