import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from src.integrations.integrations_router import integrations_router
from src.authentication.utils import get_current_user
from src.schema import UserResponse

@pytest.fixture
def mock_session():
    mock = AsyncMock(spec=AsyncSession)
    return mock

@pytest.fixture
def mock_writable_session(mock_session):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_shopify_auth_success():
    user_id = uuid.uuid4()
    test_user = UserResponse(
        id=user_id,
        email="test@example.com",
        password="hashedpwd",
        platforms_connected={}
    )
    
    mock_auth_url = "https://test-shop.myshopify.com/admin/oauth/authorize"
    
    with patch("src.integrations.integrations_router.get_current_user", return_value=test_user), \
         patch("src.integrations.integrations_router.authorize_shopify", return_value=mock_auth_url):
        
        endpoint = integrations_router.routes[0].endpoint
        result = await endpoint(test_user)
        
        assert result == mock_auth_url

@pytest.mark.asyncio
async def test_shopify_auth_unauthorized():
    with patch("src.integrations.integrations_router.get_current_user", side_effect=HTTPException(status_code=401, detail="Unauthorized")):
        with pytest.raises(HTTPException) as exc_info:
            await integrations_router.routes[0].endpoint(None)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in exc_info.value.detail

@pytest.mark.asyncio
async def test_shopify_callback_success():
    request = MagicMock()
    mock_credentials = {
        "access_token": "test_token",
        "shop": "test-shop.myshopify.com"
    }
    
    with patch("src.integrations.integrations_router.shopify_callback", return_value=mock_credentials):
        endpoint = integrations_router.routes[1].endpoint
        result = await endpoint(request)
        
        assert result == mock_credentials

@pytest.mark.asyncio
async def test_shopify_callback_error():
    request = MagicMock()
    
    with patch("src.integrations.integrations_router.shopify_callback", side_effect=HTTPException(status_code=400, detail="Invalid callback")):
        endpoint = integrations_router.routes[1].endpoint
        
        with pytest.raises(HTTPException) as exc_info:
            await endpoint(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_shopify_credentials_success():
    user_id = uuid.uuid4()
    test_user = UserResponse(
        id=user_id,
        email="test@example.com",
        password="hashedpwd",
        platforms_connected={}
    )
    
    mock_credentials = {
        "access_token": "test_token",
        "shop": "test-shop.myshopify.com"
    }
    
    with patch("src.integrations.integrations_router.get_current_user", return_value=test_user), \
         patch("src.integrations.integrations_router.get_shopify_credentials", return_value=mock_credentials):
        
        endpoint = integrations_router.routes[2].endpoint
        result = await endpoint(test_user)
        
        assert result == mock_credentials

@pytest.mark.asyncio
async def test_shopify_credentials_unauthorized():
    with patch("src.integrations.integrations_router.get_current_user", side_effect=HTTPException(status_code=401, detail="Unauthorized")):
        with pytest.raises(HTTPException) as exc_info:
            await integrations_router.routes[2].endpoint(None)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in exc_info.value.detail

@pytest.mark.asyncio
async def test_shopify_credentials_not_found():
    user_id = uuid.uuid4()
    test_user = UserResponse(
        id=user_id,
        email="test@example.com",
        password="hashedpwd",
        platforms_connected={}
    )
    
    with patch("src.integrations.integrations_router.get_current_user", return_value=test_user), \
         patch("src.integrations.integrations_router.get_shopify_credentials", side_effect=HTTPException(status_code=404, detail="Shopify credentials not found")):
        
        endpoint = integrations_router.routes[2].endpoint
        
        with pytest.raises(HTTPException) as exc_info:
            await endpoint(test_user)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
