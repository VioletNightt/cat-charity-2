from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, obj_id: int, session: AsyncSession
                  ) -> Optional[ModelType]:
        return await session.get(self.model, obj_id)

    async def get_all(self, session: AsyncSession) -> List[ModelType]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        commit: bool = True,
        **kwargs: Dict[str, Any],
    ) -> ModelType:
        obj_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_data, **kwargs)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        else:
            await session.flush()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        await session.delete(db_obj)
        await session.commit()
        return db_obj
