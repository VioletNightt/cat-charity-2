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


class DonationCreateResponse(BaseModel):
    id: int
    full_amount: int
    comment: Optional[str] = None
    create_date: datetime

    class Config:
        from_attributes = True


class DonationDB(DonationBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]
    user_id: int

    class Config:
        from_attributes = True


class DonationUserResponse(BaseModel):
    id: int
    comment: Optional[str] = None
    full_amount: int
    create_date: datetime

    class Config:
        from_attributes = True
