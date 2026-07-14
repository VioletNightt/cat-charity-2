from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.core.constants import (MIN_FULL_AMOUNT,
                                PROJECT_DESCRIPTION_MIN_LENGTH,
                                PROJECT_NAME_MAX_LENGTH,
                                PROJECT_NAME_MIN_LENGTH)


class CharityProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=PROJECT_NAME_MIN_LENGTH,
        max_length=PROJECT_NAME_MAX_LENGTH)
    description: str = Field(..., min_length=PROJECT_DESCRIPTION_MIN_LENGTH)
    full_amount: Annotated[int, Field(gt=MIN_FULL_AMOUNT)]


class CharityProjectCreate(CharityProjectBase):
    class Config:
        extra = "forbid"


class CharityProjectUpdate(BaseModel):
    name: Optional[Annotated[str, Field(
        min_length=PROJECT_NAME_MIN_LENGTH,
        max_length=PROJECT_NAME_MAX_LENGTH)]] = None
    description: Optional[Annotated[
        str, Field(min_length=PROJECT_DESCRIPTION_MIN_LENGTH)]] = None
    full_amount: Optional[Annotated[int, Field(gt=MIN_FULL_AMOUNT)]] = None

    class Config:
        extra = "forbid"


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        from_attributes = True
