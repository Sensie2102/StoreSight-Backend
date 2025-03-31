import os
import pytest_asyncio
import pytest
from uuid import uuid4
from datetime import timedelta
from jose import jwt
from src.authentication.jwtAuth import generate_jwt_token, authenticate_user
from src.schema import UserResponse
from unittest.mock import AsyncMock, patch
from test.utils.seed_data import seed_test_users  
from src.db.utils import writable_session
from sqlalchemy import delete
from src.db.db_schema import User

# Set up environment variables
@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "5ed841ebbe3bcfbad95a3c87c7f59bbb1d0813a55f704c5d92d61cda4d93800b")
    monkeypatch.setenv("ALGORITHM", "HS256")


@pytest_asyncio.fixture(scope="function")
async def test_user():
    # Seed one test user (with a unique email and fixed password "test123")
    users = await seed_test_users(count=1)
    user = users[0]
    print(f"Seeded test user: {user.email}")
    yield user
    # Cleanup: attempt to delete the test user; ignore errors if the event loop is closed
    try:
        async with writable_session() as session:
            await session.execute(delete(User).where(User.email == user.email))
            await session.commit()
    except Exception as cleanup_error:
        error_msg = str(cleanup_error)
        if "send" in error_msg or "Event loop is closed" in error_msg:
            print("Cleanup error (ignored):", cleanup_error)
        else:
            raise cleanup_error

# Test for generating a valid JWT token
def test_generate_jwt_token_valid():
    token = generate_jwt_token("test@example.com", uuid4(), timedelta(minutes=15))
    decoded = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    assert decoded["sub"] == "test@example.com"
    assert "id" in decoded
    assert "exp" in decoded

# Test for successful authentication using the seeded user
@pytest.mark.asyncio
@patch("src.authentication.jwtAuth.readonly_session")
async def test_authenticate_user_success(mock_session, test_user):
    mock_user = {
        "id": test_user.id,
        "email": test_user.email,
        "password": test_user.password,  # This is the hashed password from seed_test_users
        "google_oauth_token": test_user.google_oauth_token,
        "connected_platforms": test_user.connected_platforms,
    }

    class FakeResult:
        def scalar_one_or_none(self):
            return mock_user

    fake_session = AsyncMock()
    fake_session.execute.return_value = FakeResult()
    mock_session.return_value.__aenter__.return_value = fake_session

    # Call authenticate_user with attribute access, not subscripting
    result = await authenticate_user(test_user.email, "test123")
    assert isinstance(result, UserResponse)
    assert result.email == test_user.email

# Test for no user found (non-existent user)
@pytest.mark.asyncio
@patch("src.authentication.jwtAuth.readonly_session")
async def test_authenticate_user_no_user_found(mock_session):
    class FakeResult:
        def scalar_one_or_none(self):
            return None

    fake_session = AsyncMock()
    fake_session.execute.return_value = FakeResult()
    mock_session.return_value.__aenter__.return_value = fake_session

    result = await authenticate_user("nonexistent@example.com", "password")
    assert result is False
