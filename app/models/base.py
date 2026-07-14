from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

from app.core.constants import DEFAULT_FULLY_INVESTED, DEFAULT_INVESTED_AMOUNT
from app.core.db import Base


class BaseModel(Base):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('invested_amount >= 0',
                        name='invested_amount_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    invested_amount = Column(Integer, default=DEFAULT_INVESTED_AMOUNT)
    fully_invested = Column(Boolean, default=DEFAULT_FULLY_INVESTED)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime, nullable=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
