from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import invest_available_funds

router = APIRouter()


@router.get("/", response_model=list[DonationFullInfoDB])
async def get_all_donations(
    user: User = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех пожертвований.
    В ответе содержатся все поля, включая `invested_amount` и `fully_invested`.
    """
    donations = await donation_crud.get_all(session)
    return donations


@router.get("/my", response_model=list[DonationDB])
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_by_user(user.id, session)


@router.post("/", response_model=DonationDB)
async def create_donation(
    donation_in: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Создаёт новое пожертвование.
    После сохранения запускается механизм распределения средств
    между открытыми проектами.
    Фиксация транзакции происходит только после завершения инвестирования.
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
