from uuid import UUID
from typing import TypeAlias, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.database import Base

SnippetModel: TypeAlias = Base  # type: ignore
SnippetSchema: TypeAlias = BaseModel


class SnippetException(Exception):
    pass


class IntegrityConflictException(Exception):
    pass


class NotFoundException(Exception):
    pass


def crud_factory(model: SnippetModel):
    class AsyncCrud:
        model: SnippetModel = None

        @classmethod
        async def create(
            cls,
            session: AsyncSession,
            data: SnippetSchema,
        ) -> SnippetModel:
            try:
                db_model = model(**data.model_dump())
                session.add(db_model)
                await session.commit()
                await session.refresh(db_model)
                return db_model
            except IntegrityError as e:
                raise IntegrityConflictException(
                    f"{model.__tablename__} conflicts with existing data. {e}",
                )
            except Exception as e:
                raise SnippetException(f"Unknown error occurred: {e}") from e

        @classmethod
        async def create_many(
            cls,
            session: AsyncSession,
            data: list[SnippetSchema],
            return_models: bool = False,
        ) -> list[SnippetModel] | bool:
            db_models = [model(**d.model_dump()) for d in data]
            try:
                session.add_all(db_models)
                await session.commit()
            except IntegrityError as e:
                raise IntegrityConflictException(
                    f"{model.__tablename__} conflict with existing data. {e}",
                )
            except Exception as e:
                raise SnippetException(f"Unknown error occurred: {e}") from e

            if not return_models:
                return True

            for m in db_models:
                await session.refresh(m)

            return db_models

        @classmethod
        async def get_one_by_id(
            cls,
            session: AsyncSession,
            id_: str | UUID,
            column: str = "id",
        ) -> SnippetModel:
            try:
                q = select(model).where(getattr(model, column) == id_)
            except AttributeError as e:
                raise SnippetException(
                    f"Column {column} not found on {model.__tablename__}. {e}",
                )

            results = await session.execute(q)
            return results.unique().scalar_one_or_none()

        @classmethod
        async def get_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            column: str = "id",
        ) -> Sequence[SnippetModel]:
            q = select(model)
            if ids:
                try:
                    q = q.where(getattr(model, column).in_(ids))
                except AttributeError as e:
                    raise SnippetException(
                        f"Column {column} not found on {model.__tablename__}. {e}",
                    )

            rows = await session.execute(q)
            return rows.unique().scalars().all()

        @classmethod
        async def get_many_by_value(
            cls,
            session: AsyncSession,
            value: str | UUID,
            column: str,
        ) -> Sequence[SnippetModel]:
            q = select(model)

            try:
                q = q.where(getattr(model, column) == value)
            except AttributeError as e:
                raise SnippetException(
                    f"Column {column} not found on {model.__tablename__}. {e}",
                )
            rows = await session.execute(q)
            return rows.unique().scalars().all()

        @classmethod
        async def get_all(
            cls,
            session: AsyncSession,
        ) -> Sequence[SnippetModel]:
            q = select(model)
            rows = await session.execute(q)
            return rows.unique().scalars().all()

        @classmethod
        async def update_by_id(
            cls,
            session: AsyncSession,
            data: SnippetSchema,
            id_: str | UUID,
            column: str = "id",
        ) -> SnippetModel:
            q = (
                update(model)
                .where(getattr(model, column) == id_)
                .values(**data.model_dump(exclude_unset=True))
                .returning(model)
            )

            try:
                db_model = await session.execute(q)
                await session.commit()
                return db_model
            except IntegrityError as e:
                raise IntegrityConflictException(
                    f"{model.__tablename__} {column}={id_} conflict with existing data. {e}",
                )

        @classmethod
        async def remove_by_id(
            cls,
            session: AsyncSession,
            id_: str | UUID,
            column: str = "id",
        ) -> int:
            try:
                query = delete(model).where(getattr(model, column) == id_)
            except AttributeError as e:
                raise SnippetException(
                    f"Column {column} not found on {model.__tablename__}. {e}",
                )

            rows = await session.execute(query)
            await session.commit()
            return rows.rowcount

        @classmethod
        async def remove_many_by_ids(
            cls,
            session: AsyncSession,
            ids: list[str | UUID],
            column: str = "id",
        ) -> int:
            if not ids:
                raise SnippetException("No ids provided.")

            try:
                query = delete(model).where(getattr(model, column).in_(ids))
            except AttributeError as e:
                raise SnippetException(
                    f"Column {column} not found on {model.__tablename__}. {e}",
                )

            rows = await session.execute(query)
            await session.commit()
            return rows.rowcount

    AsyncCrud.model = model
    return AsyncCrud
