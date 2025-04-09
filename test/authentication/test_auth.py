import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from src.authentication.router import router
from src.authentication.utils import CreateUserRequest, Token
from src.db import User as DBUser
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
async def test_create_new_user_success():
    random_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "password123"
    user_id = uuid.uuid4()
    
    request = CreateUserRequest(email=random_email, password=test_password)
    
    test_user = DBUser(
        id=user_id,
        email=random_email,
        password="hashedpwd",
        google_oauth_token=False,
        connected_platforms={}
    )
    
    async def mock_create_new_user(req):
        assert req.email == random_email
        assert req.password == test_password
        return test_user
    
    with patch.object(router.routes[0], "endpoint", mock_create_new_user):
        result = await router.routes[0].endpoint(request)
        
        assert result.email == random_email
        assert result is test_user

@pytest.mark.asyncio
@patch("src.authentication.router.writable_session")
async def test_create_new_user_already_exists(mock_writable_session, mock_session):
    mock_writable_session.return_value = mock_session
    mock_execute = AsyncMock()
    existing_user = DBUser(
        id=uuid.uuid4(), 
        email="existing@example.com", 
        password="hashedpwd",
        google_oauth_token=False,
        connected_platforms={}
    )
    mock_execute.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_execute
    
    with pytest.raises(HTTPException) as exc_info:
        await router.routes[0].endpoint(
            CreateUserRequest(email="existing@example.com", password="password123")
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already exists" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_access_token_success():
    user_id = uuid.uuid4()
    test_email = "user@example.com"
    
    form_data = MagicMock()
    form_data.username = test_email
    form_data.password = "password123"
    
    user_response = UserResponse(
        id=user_id, 
        email=test_email,
        password="hashedpwd",
        platforms_connected={}
    )
    
    with patch("src.authentication.router.authenticate_user", return_value=user_response) as mock_auth, \
         patch("src.authentication.router.generate_jwt_token", return_value="test_token") as mock_token:
        
        endpoint = router.routes[1].endpoint
        result = await endpoint(form_data)
        
        assert isinstance(result, dict)
        assert result["access_token"] == "test_token"
        assert result["token_type"] == "bearer"
        
        mock_auth.assert_called_once_with(test_email, "password123")
        mock_token.assert_called_once_with(test_email, user_id, timedelta(minutes=20))

@pytest.mark.asyncio
@patch("src.authentication.router.authenticate_user")
async def test_get_access_token_invalid_credentials(mock_authenticate):
    mock_authenticate.return_value = False
    
    form_data = MagicMock()
    form_data.username = "user@example.com"
    form_data.password = "wrong_password"
    
    with pytest.raises(HTTPException) as exc_info:
        await router.routes[1].endpoint(form_data)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("src.authentication.router.return_google_url")
async def test_google_login(mock_return_url):
    mock_return_url.return_value = {"url": "https://accounts.google.com/auth"}
    request = MagicMock()
    
    result = await router.routes[2].endpoint(request)
    
    mock_return_url.assert_called_once_with(request)
    assert result == {"url": "https://accounts.google.com/auth"}

@pytest.mark.asyncio
@patch("src.authentication.router.get_user_details")
async def test_google_auth(mock_get_details):
    mock_get_details.return_value = {"access_token": "google_test_token", "token_type": "bearer"}
    request = MagicMock()
    
    result = await router.routes[3].endpoint(request)
    
    mock_get_details.assert_called_once_with(request=request)
    assert result["access_token"] == "google_test_token"
    assert result["token_type"] == "bearer"
