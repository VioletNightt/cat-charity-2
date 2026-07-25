from fastapi import APIRouter

from app.api.endpoints import charity_project_router, donation_router
from app.core.constants import TAG_AUTH, TAG_USERS
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

auth_router = APIRouter()

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=f"/{TAG_AUTH}/jwt",
    tags=[TAG_AUTH],
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"/{TAG_AUTH}",
    tags=[TAG_AUTH],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.name not in {"users:delete_user", "users:delete_current_user"}
]
auth_router.include_router(
    users_router,
    prefix=f"/{TAG_USERS}",
    tags=[TAG_USERS],
)

main_router = APIRouter()
main_router.include_router(
    charity_project_router,
    prefix="/charity_project",
    tags=["Charity Projects"],
)
main_router.include_router(
    donation_router,
    prefix="/donation",
    tags=["Donations"],
)
main_router.include_router(auth_router)
