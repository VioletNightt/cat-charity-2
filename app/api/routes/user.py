from fastapi import APIRouter

from app.core.constants import TAG_AUTH, TAG_USERS
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=f"/{TAG_AUTH}/jwt",
    tags=[TAG_AUTH],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"/{TAG_AUTH}",
    tags=[TAG_AUTH],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.name not in {"users:delete_user", "users:delete_current_user"}
]
router.include_router(
    users_router,
    prefix=f"/{TAG_USERS}",
    tags=[TAG_USERS],
)
