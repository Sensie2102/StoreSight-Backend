import uuid
from typing import List
from src.db import User
from src.db.utils import writable_session
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_test_users(count: int = 10) -> List[User]:
    
    users = [
        User(
            id=uuid.uuid4(),
            email=f"user{i}_{uuid.uuid4()}@example.com",
            password=bcrypt_context.hash("test123"),
            google_oauth_token=None,
            connected_platforms={"amazon": f"token{i}"}
        )
        for i in range(count)
    ]

    async with writable_session() as session:
        session.add_all(users)
        await session.commit()


    return users
