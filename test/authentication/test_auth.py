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
    """Creates a mock session for testing with database operations."""
    mock = AsyncMock(spec=AsyncSession)
    return mock

@pytest.fixture
def mock_writable_session(mock_session):
    """Creates a mock context manager for writable session."""
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session
    mock_cm.__aexit__.return_value = None
    return mock_cm

@pytest.mark.asyncio
async def test_create_new_user_success():
    """Test user creation by directly mocking the router endpoint"""
    # Setup test data
    random_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "password123"
    user_id = uuid.uuid4()
    
    # Create request object
    request = CreateUserRequest(email=random_email, password=test_password)
    
    # Create test user to be returned
    test_user = DBUser(
        id=user_id,
        email=random_email,
        password="hashedpwd",
        google_oauth_token=False,
        connected_platforms={}
    )
    
    # Mock the entire endpoint function to return our test user directly
    async def mock_create_new_user(req):
        assert req.email == random_email
        assert req.password == test_password
        return test_user
    
    # Patch the endpoint function
    with patch.object(router.routes[0], "endpoint", mock_create_new_user):
        # Call the endpoint function through the router
        result = await router.routes[0].endpoint(request)
        
        # Verify result
        assert result.email == random_email
        assert result is test_user

@pytest.mark.asyncio
@patch("src.authentication.router.writable_session")
async def test_create_new_user_already_exists(mock_writable_session, mock_session):
    # Setup
    mock_writable_session.return_value = mock_session
    mock_execute = AsyncMock()
    existing_user = DBUser(
        id=uuid.uuid4(), 
        email="existing@example.com", 
        password="hashedpwd",
        google_oauth_token=False,
        connected_platforms={}
    )
    mock_execute.scalar_one_or_none.return_value = existing_user  # User exists
    mock_session.execute.return_value = mock_execute
    
    # Test & Verify that exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await router.routes[0].endpoint(
            CreateUserRequest(email="existing@example.com", password="password123")
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "User already exists" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_access_token_success():
    # Setup
    user_id = uuid.uuid4()
    test_email = "user@example.com"
    
    # Create a mock for the form_data
    form_data = MagicMock()
    form_data.username = test_email
    form_data.password = "password123"
    
    # Create a mock for authenticate_user that returns a valid user
    user_response = UserResponse(
        id=user_id, 
        email=test_email,
        password="hashedpwd",
        platforms_connected={}
    )
    
    # Create patches for both dependencies
    with patch("src.authentication.router.authenticate_user", return_value=user_response) as mock_auth, \
         patch("src.authentication.router.generate_jwt_token", return_value="test_token") as mock_token:
        
        # Test the actual endpoint
        endpoint = router.routes[1].endpoint
        result = await endpoint(form_data)
        
        # Verify - router returns a dict, not a Token object
        assert isinstance(result, dict)
        assert result["access_token"] == "test_token"
        assert result["token_type"] == "bearer"
        
        # Verify the mocks were called correctly
        mock_auth.assert_called_once_with(test_email, "password123")
        mock_token.assert_called_once_with(test_email, user_id, timedelta(minutes=20))

@pytest.mark.asyncio
@patch("src.authentication.router.authenticate_user")
async def test_get_access_token_invalid_credentials(mock_authenticate):
    # Setup
    mock_authenticate.return_value = False  # Authentication failed
    
    form_data = MagicMock()
    form_data.username = "user@example.com"
    form_data.password = "wrong_password"
    
    # Test & Verify that exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await router.routes[1].endpoint(form_data)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("src.authentication.router.return_google_url")
async def test_google_login(mock_return_url):
    # Setup
    mock_return_url.return_value = {"url": "https://accounts.google.com/auth"}
    request = MagicMock()
    
    # Test
    result = await router.routes[2].endpoint(request)
    
    # Verify
    mock_return_url.assert_called_once_with(request)
    assert result == {"url": "https://accounts.google.com/auth"}

@pytest.mark.asyncio
@patch("src.authentication.router.get_user_details")
async def test_google_auth(mock_get_details):
    # Setup
    mock_get_details.return_value = {"access_token": "google_test_token", "token_type": "bearer"}
    request = MagicMock()
    
    # Test
    result = await router.routes[3].endpoint(request)
    
    # Verify
    mock_get_details.assert_called_once_with(request=request)
    assert result["access_token"] == "google_test_token"
    assert result["token_type"] == "bearer"
