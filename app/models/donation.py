from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Donation(BaseModel):
    __tablename__ = "donation"

    comment = Column(Text, nullable=True)
    full_amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="donations")
