from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.constants import MIN_FULL_AMOUNT


class DonationBase(BaseModel):
    comment: Optional[str] = None
    full_amount: int = Field(..., gt=MIN_FULL_AMOUNT)


class DonationCreate(DonationBase):
    class Config:
        extra = "forbid"


class DonationDB(BaseModel):
    id: int
    full_amount: int
    comment: Optional[str] = None
    create_date: datetime

    class Config:
        from_attributes = True


class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
