from uuid import UUID
from typing import Generic, Sequence, Optional, Type, TypeVar, Protocol, cast
from contextlib import asynccontextmanager

from icecream import ic  # noqa: F401

from sqlalchemy import delete, select, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel


class ModelProtocol(Protocol):
    __tablename__: object


SQLAlchemyModel = TypeVar("SQLAlchemyModel", bound=ModelProtocol)  # type: ignore
PydanticSchema = TypeVar("PydanticSchema", bound=BaseModel)


class SnippetException(Exception):
    """Base exception for repository operations"""

    pass


class IntegrityConflictException(SnippetException):
    """Exception raised when integrity constraints are violated"""

    pass


class NotFoundException(SnippetException):
    """Exception raised when entity is not found"""

    pass


class CrudMeta(type):
    # def __new__(mcs, name, bases, namespace, **kwargs):
    #     if name == "AsyncCrud":
    #         return super().__new__(mcs, name, bases, namespace)

    #     model_class = kwargs.get("model_class")
    #     if model_class is None:
    #         raise TypeError("Crud class must be initialized with 'model_class'")

    #     namespace["model_class"] = model_class

    #     cls = super().__new__(mcs, name, bases, namespace)
    #     return cls
    pass


class AsyncCrud(Generic[SQLAlchemyModel], metaclass=CrudMeta):
    model_class: Type[SQLAlchemyModel]

    def __init__(self, model: Type[SQLAlchemyModel]):
        self.model_class = model

    @classmethod
    @asynccontextmanager
    async def transaction(cls, session: AsyncSession):
        """Context manager for handling transactions with proper rollback on exception"""
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            if isinstance(e, IntegrityError):
                raise IntegrityConflictException(
                    f"{cls.model_class.__tablename__} conflicts with existing data: {e}"
                ) from e
            raise SnippetException(f"Transaction failed: {e}") from e

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: PydanticSchema,
    ) -> SQLAlchemyModel:
        """Create a single entity"""
        try:
            db_model = cls.model_class(**data.model_dump(exclude_unset=True))
            session.add(db_model)
            await session.commit()
            await session.refresh(db_model)
            return db_model
        except IntegrityError as e:
            await session.rollback()
            raise IntegrityConflictException(
                f"{cls.model_class.__tablename__} conflicts with existing data: {e}",
            ) from e
        except Exception as e:
            await session.rollback()
            raise SnippetException(f"Failed to create {cls.model_class.__tablename__}: {e}") from e

    @classmethod
    async def create_many(
        cls,
        session: AsyncSession,
        data: list[PydanticSchema],
        return_models: bool = False,
    ) -> list[SQLAlchemyModel] | bool:
        """Create multiple entities at once"""
        db_models = [cls.model_class(**d.model_dump(exclude_unset=True)) for d in data]

        try:
            async with cls.transaction(session):
                session.add_all(db_models)

            if not return_models:
                return True

            for m in db_models:
                await session.refresh(m)

            return db_models
        except Exception as e:
            if not isinstance(e, SnippetException):
                raise SnippetException(f"Failed to create multiple {cls.model_class.__tablename__}: {e}") from e
            raise

    @classmethod
    async def get_one_by_id(
        cls,
        session: AsyncSession,
        id_: str | UUID,
        column: str = "id",
    ) -> SQLAlchemyModel:
        """Get single entity by id or other column"""
        try:
            q = select(cls.model_class).where(getattr(cls.model_class, column) == id_)
        except AttributeError as e:
            raise SnippetException(
                f"Column {column} not found on {cls.model_class.__tablename__}: {e}",
            ) from e

        result = await session.execute(q)
        entity = result.unique().scalar_one_or_none()

        if entity is None:
            raise NotFoundException(f"{cls.model_class.__tablename__} with {column}={id_} not found")

        return entity

    @classmethod
    async def get_many_by_ids(
        cls,
        session: AsyncSession,
        ids: list[str | UUID],
        column: str = "id",
    ) -> Sequence[SQLAlchemyModel]:
        """Get multiple entities by list of ids"""
        q = select(cls.model_class)
        if ids:
            try:
                q = q.where(getattr(cls.model_class, column).in_(ids))
            except AttributeError as e:
                raise SnippetException(
                    f"Column {column} not found on {cls.model_class.__tablename__}: {e}",
                ) from e

        rows = await session.execute(q)
        return rows.unique().scalars().all()

    @classmethod
    async def get_many_by_value(
        cls,
        session: AsyncSession,
        value: str | UUID | int | float | bool,
        column: str,
    ) -> Sequence[SQLAlchemyModel]:
        """Get entities by matching value in a specific column"""
        q = select(cls.model_class)

        try:
            q = q.where(getattr(cls.model_class, column) == value)
        except AttributeError as e:
            raise SnippetException(
                f"Column {column} not found on {cls.model_class.__tablename__}: {e}",
            ) from e

        rows = await session.execute(q)
        return rows.unique().scalars().all()

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        offset: int = 0,
        limit: Optional[int] = 100,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> tuple[Sequence[SQLAlchemyModel], int]:
        """Get all entities with pagination support and total count"""
        # Query for data with pagination
        q = select(cls.model_class)

        # Add ordering if specified
        if order_by:
            try:
                order_column = getattr(cls.model_class, order_by)
                q = q.order_by(order_column.desc() if desc else order_column)
            except AttributeError as e:
                raise SnippetException(
                    f"Column {order_by} not found on {cls.model_class.__tablename__}: {e}",
                ) from e

        # Apply pagination
        if limit is not None:
            q = q.offset(offset).limit(limit)

        # Execute query
        rows = await session.execute(q)

        # Get total count
        count_q = select(func.count()).select_from(cls.model_class)
        count_result = await session.execute(count_q)
        total = count_result.scalar_one()

        return rows.unique().scalars().all(), total

    @classmethod
    async def update_by_id(
        cls,
        session: AsyncSession,
        data: PydanticSchema,
        id_: str | UUID,
        column: str = "id",
    ) -> SQLAlchemyModel:
        """Update entity by id and return the updated model"""
        try:
            # First check if entity exists
            await cls.get_one_by_id(session, id_, column)

            # Update values using update statement
            q = (
                update(cls.model_class)
                .where(getattr(cls.model_class, column) == id_)
                .values(**data.model_dump(exclude_unset=True))
                .returning(cls.model_class)
            )

            result = await session.execute(q)
            await session.commit()

            # Get the updated entity
            updated_entity = result.scalar_one()
            return updated_entity
        except IntegrityError as e:
            await session.rollback()
            raise IntegrityConflictException(
                f"{cls.model_class.__tablename__} {column}={id_} conflict with existing data: {e}",
            ) from e
        except Exception as e:
            await session.rollback()
            if not isinstance(e, SnippetException):
                raise SnippetException(f"Failed to update {cls.model_class.__tablename__}: {e}") from e
            raise

    @classmethod
    async def remove_by_id(
        cls,
        session: AsyncSession,
        id_: str | UUID,
        column: str = "id",
        raise_not_found: bool = False,
    ) -> int:
        """Remove entity by id"""
        try:
            query = delete(cls.model_class).where(getattr(cls.model_class, column) == id_)
        except AttributeError as e:
            raise SnippetException(
                f"Column {column} not found on {cls.model_class.__tablename__}: {e}",
            ) from e

        try:
            result = await session.execute(query)
            await session.commit()

            if result.rowcount == 0 and raise_not_found:
                raise NotFoundException(f"{cls.model_class.__tablename__} with {column}={id_} not found")

            return result.rowcount
        except Exception as e:
            await session.rollback()
            if not isinstance(e, SnippetException):
                raise SnippetException(f"Failed to remove {cls.model_class.__tablename__}: {e}") from e
            raise

    @classmethod
    async def remove_many_by_ids(
        cls,
        session: AsyncSession,
        ids: list[str | UUID],
        column: str = "id",
    ) -> int:
        """Remove multiple entities by ids"""
        try:
            query = delete(cls.model_class).where(getattr(cls.model_class, column).in_(ids))
        except AttributeError as e:
            raise SnippetException(
                f"Column {column} not found on {cls.model_class.__tablename__}: {e}",
            ) from e

        try:
            result = await session.execute(query)
            await session.commit()
            return result.rowcount
        except Exception as e:
            await session.rollback()
            raise SnippetException(f"Failed to remove multiple {cls.model_class.__tablename__}: {e}") from e

    @classmethod
    async def count(
        cls,
        session: AsyncSession,
        filters: dict[str, str] | None = None,
    ) -> int:
        """Count entities with optional filtering"""
        q = select(func.count()).select_from(cls.model_class)

        if filters:
            for column_name, value in filters.items():
                try:
                    q = q.where(getattr(cls.model_class, column_name) == value)
                except AttributeError as e:
                    raise SnippetException(
                        f"Column {column_name} not found on {cls.model_class.__tablename__}: {e}",
                    ) from e

        result = await session.execute(q)
        return result.scalar_one()


def crud_factory(model_class: Type[SQLAlchemyModel]) -> Type[AsyncCrud[SQLAlchemyModel]]:
    if model_class is None:
        raise TypeError("Crud class must be initialized with 'model_class'")

    new_class_name = f"{model_class.__name__}Crud"

    new_cls = CrudMeta(new_class_name, (AsyncCrud,), {"model_class": model_class})
    return cast(Type[AsyncCrud[SQLAlchemyModel]], new_cls)


# class Lol:
#     __tablename__: int = 123
#     pass


# test_crud = crud_factory(Lol)
