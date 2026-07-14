from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.user import User

SECRET = settings.secret_key
ALGORITHM = settings.algorithm

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_db():
    async with AsyncSessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)


fastapi_users = FastAPIUsers[User, int](
    get_user_db,
    [auth_backend],
)

# Зависимости для текущего пользователя и суперпользователя
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)