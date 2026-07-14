from sqlalchemy import Column, Integer, String, Text

from app.core.constants import PROJECT_NAME_MAX_LENGTH
from app.models.base import BaseModel


class CharityProject(BaseModel):
    __tablename__ = "charityproject"

    name = Column(String(PROJECT_NAME_MAX_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    full_amount = Column(Integer, nullable=False)
