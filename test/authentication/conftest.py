import pytest_asyncio
from sqlalchemy import text
from src.db.utils import writable_session
from test.utils.seed_data import seed_test_users

@pytest_asyncio.fixture(scope="function")
async def test_user():
    users = await seed_test_users(count=1)
    user = users[0]
    print(f"Seeded test user: {user.email}")
    yield user
    try:
        async with writable_session() as session:
            await session.execute(text(f"DELETE FROM users WHERE email = '{user.email}'"))
            await session.commit()
    except Exception as cleanup_error:
        if "send" in str(cleanup_error) or "Event loop is closed" in str(cleanup_error):
            print("Cleanup error (ignored):", cleanup_error)
        else:
            raise cleanup_error