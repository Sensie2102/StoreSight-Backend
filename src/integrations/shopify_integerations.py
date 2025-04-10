import secrets
import urllib.parse
from fastapi import Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
import base64
import asyncio
import json
import os
import urllib
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import httpx
from sqlalchemy import select
from json.decoder import JSONDecodeError
from redis.exceptions import RedisError

from ..db.db_schema import Integrations 
from ..db.utils import writable_session
from .utils import generate_code_challenge,generate_code_verifier
from src.redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID=os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET=os.getenv("SHOPIFY_CLIENT_SECRET")
REDIRECT_URI=os.getenv("SHOPIFY_REDIRECT_URI")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise ValueError("Missing required Shopify environment variables")

encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

def build_auth_url(shop,scopes,code_challenge,state):
    if not shop or not scopes or not code_challenge or not state:
        raise ValueError("Missing required parameters for auth URL")
    
    base_url=f"https://{shop}/admin/oauth/authorize"
    params = {
        "client_id":CLIENT_ID,
        "scope":scopes,
        "redirect_uri":REDIRECT_URI,
        "state":state,
        "code_challenge":code_challenge,
        "code_challenge_method":"S256"
    }
    try:
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build auth URL: {str(e)}")

async def authorize_shopify(user_id,shop):
    if not user_id or not shop:
        raise HTTPException(status_code=400, detail="Missing user_id or shop")
        
    try:
        state_data = {
            'state':secrets.token_urlsafe(32),
            'user_id':str(user_id),
            'shop':shop
        }
        encoded_state=base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
        
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)
        
        scopes = ['read_orders','read_customers','read_products']
        
        auth_url = build_auth_url(shop," ".join(scopes),code_challenge, encoded_state)
        
        try:
            await asyncio.gather(
                add_key_value_redis(f'shopify_state:{user_id}:{shop}',json.dumps(state_data), expire=600),
                add_key_value_redis(f'shopify_verfier:{user_id}:{shop}',code_verifier,expire=600)
            )
        except RedisError as e:
            raise HTTPException(status_code=503, detail=f"Failed to store authorization data: {str(e)}")
        
        return auth_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authorization failed: {str(e)}")

async def shopify_callback(request: Request, session: AsyncSession = Depends(writable_session)):
    if request.query_params.get("error"):
        raise HTTPException(
            status_code=400,
            detail=request.query_params.get("error_description", "Unknown error during Shopify callback")
        )
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    shop = request.query_params.get('shop')
    
    if not code or not shop or not encoded_state:
        raise HTTPException(
            status_code=400,
            detail="Missing required OAuth parameters: code, shop, or state"
        )
    
    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
        original_state = state_data.get('state')
        user_id = UUID(state_data.get('user_id'))
    except (JSONDecodeError, ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid state parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process state: {str(e)}")

    try:
        saved_state_json, code_verifier = await asyncio.gather(
            get_value_redis(f'shopify_state:{user_id}:{shop}'),
            get_value_redis(f'shopify_verifier:{user_id}:{shop}')
        )
    except RedisError as e:
        raise HTTPException(status_code=503, detail=f"Failed to retrieve authorization data: {str(e)}")
    
    if not saved_state_json or not code_verifier:
        raise HTTPException(status_code=404, detail="Authorization data not found or expired")

    try:
        saved_state = json.loads(saved_state_json)
    except JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid saved state format: {str(e)}")

    if saved_state.get('state') != original_state:
        raise HTTPException(status_code=401, detail="Invalid state - possible CSRF attack")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'https://{shop}.myshopify.com/admin/oauth/access_token',
                json={
                    'grant_type' : 'authorization_code',
                    'code': code,
                    'redirect_uri' : REDIRECT_URI,
                    'client_id': CLIENT_ID,
                    'code_verifier': code_verifier,
                },
                timeout=10.0
            )
            response.raise_for_status()
            token_data = response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout while connecting to Shopify")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Shopify API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to obtain access token: {str(e)}")
    
    try:
        integration = Integrations(
            user_id=user_id,
            platform="shopify",
            refresh_token=token_data['access_token'],  
            shop_url=shop,
            is_active=True
        )
        
        session.add(integration)
        await session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save integration: {str(e)}")
    
    try:
        await asyncio.gather(
            delete_key_redis(f'shopify_state:{user_id}:{shop}'),
            delete_key_redis(f'shopify_verifier:{user_id}:{shop}')
        )
    except RedisError:
        # Log this error but don't fail the request as the integration is already saved
        pass
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_shopify_credentials(user_id,shop, session: AsyncSession = Depends(writable_session)):
    if not user_id or not shop:
        raise HTTPException(status_code=400, detail="Missing user_id or shop")

    try:
        credentials = await session.execute(
            select(Integrations).where(
                Integrations.user_id == user_id,
                Integrations.platform == 'shopify',
                Integrations.shop_url == shop
            )
        )
        credentials = credentials.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    if not credentials:
        raise HTTPException(status_code=404, detail='No credentials found for this shop.')
    
    if not credentials.is_active:
        raise HTTPException(status_code=403, detail='Shopify integration is not active.')
    
    return credentials.refresh_token
    