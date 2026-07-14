from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationCreateResponse,
    DonationDB,
    DonationUserResponse,
)
from app.services.investment import invest_available_funds

router = APIRouter()


@router.get("/", response_model=list[DonationDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    """
    Возвращает список всех пожертвований (только для суперпользователя).
    """
    donations = await donation_crud.get_all(session)
    return donations


@router.post("/", response_model=DonationCreateResponse)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Создаёт новое пожертвование (только для аутентифицированных пользователей).
    Поле user_id заполняется автоматически из текущего пользователя.
    """
    new_donation = await donation_crud.create(
        donation_in, session, commit=False, user_id=user.id
    )

    open_projects = await charity_project_crud.get_open_projects(session)
    open_donations = await donation_crud.get_open_donations(session)

    if new_donation not in open_donations:
        open_donations.append(new_donation)
        open_donations.sort(key=lambda d: d.create_date)

    invest_available_funds(open_projects, open_donations)

    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get("/my", response_model=list[DonationUserResponse])
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Возвращает все пожертвования текущего пользователя.
    Доступно только для аутентифицированных пользователей.
    """
    donations = await donation_crud.get_by_user(user.id, session)
    return donations