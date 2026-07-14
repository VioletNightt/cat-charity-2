from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectUpdate)


class CRUDCharityProject(CRUDBase[
        CharityProject, CharityProjectCreate, CharityProjectUpdate]):
    async def get_by_name(
        self, name: str, session: AsyncSession
    ) -> Optional[CharityProject]:
        result = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return result.scalars().first()

    async def get_open_projects(self, session: AsyncSession
                                ) -> List[CharityProject]:
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .where(CharityProject.invested_amount < CharityProject.full_amount)
            .order_by(CharityProject.create_date)
        )
        return result.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
