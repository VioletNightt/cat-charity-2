from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import invest_available_funds

router = APIRouter()


@router.get("/", response_model=list[CharityProjectDB])
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех проектов (доступно всем, включая анонимных пользователей).
    """
    projects = await charity_project_crud.get_all(session)
    return projects


@router.post("/", response_model=CharityProjectDB)
async def create_project(
    project_in: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    """
    Создаёт новый проект (только для суперпользователя).
    """
    existing = await charity_project_crud.get_by_name(project_in.name, session)
    if existing:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Project with this name already exists.",
        )

    new_project = await charity_project_crud.create(
        project_in, session, commit=False
    )

    open_projects = await charity_project_crud.get_open_projects(session)
    open_donations = await donation_crud.get_open_donations(session)

    if new_project not in open_projects:
        open_projects.append(new_project)
        open_projects.sort(key=lambda p: p.create_date)

    invest_available_funds(open_projects, open_donations)

    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.patch("/{project_id}", response_model=CharityProjectDB)
async def update_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    """
    Обновляет проект (только для суперпользователя).
    """
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Cannot update a fully invested project.",
        )

    if project_in.full_amount is not None:
        if project_in.full_amount < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Full amount cannot be less than already invested.",
            )

    if project_in.name is not None and project_in.name != project.name:
        existing = await charity_project_crud.get_by_name(
            project_in.name, session
        )
        if existing:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Project with this name already exists.",
            )

    updated_project = await charity_project_crud.update(
        project, project_in, session
    )

    if updated_project.invested_amount >= updated_project.full_amount:
        updated_project.fully_invested = True
        updated_project.close_date = datetime.now()
        session.add(updated_project)
        await session.commit()
        await session.refresh(updated_project)

    return updated_project


@router.delete("/{project_id}", response_model=CharityProjectDB)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
):
    """
    Удаляет проект (только для суперпользователя).
    """
    project = await charity_project_crud.get(project_id, session)
    if not project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Cannot delete a fully invested project.",
        )

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Cannot delete a project with investments.",
        )

    deleted_project = await charity_project_crud.delete(project, session)
    return deleted_project