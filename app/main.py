from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import charity_project, donation
from app.core.db import Base, engine
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="QRKot",
    description="Фонд поддержки котиков",
    version="1.0.0"
)

app.include_router(charity_project.router,
                   prefix="/charity_project", tags=["Charity Projects"])
app.include_router(donation.router, prefix="/donation", tags=["Donations"])
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if route.name not in {"users:delete_user", "users:delete_current_user"}
]
app.include_router(users_router, prefix="/users", tags=["users"])
