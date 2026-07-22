from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase[Donation, DonationCreate, None]):
    async def get_by_user(
        self, user_id: int, session: AsyncSession
    ) -> List[Donation]:
        result = await session.execute(
            select(Donation)
            .where(Donation.user_id == user_id)
            .order_by(Donation.create_date)
        )
        return result.scalars().all()

    async def get_open_donations(self, session: AsyncSession
                                 ) -> List[Donation]:
        result = await session.execute(
            select(Donation)
            .where(Donation.fully_invested.is_(False))
            .where(Donation.invested_amount < Donation.full_amount)
            .order_by(Donation.create_date)
        )
        return result.scalars().all()


donation_crud = CRUDDonation(Donation)
