from contextlib import asynccontextmanager
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.inspection import inspect
from sqlalchemy.schema import Table
from sqlalchemy.future import select
from errors.sql import NotAValidForeignKey, ElementAlreadyExists
from utils.utils import get_env_variable


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models. It includes methods for database initialization,
    session management, and insertion of initial data into tables. It also provides
    utilities for foreign key and unique key handling.
    """

    _db_url = get_env_variable("POSTGRES_URI")
    _engine = create_async_engine(_db_url, echo=True)
    _AsyncSessionLocal = async_sessionmaker(
        bind=_engine, class_=AsyncSession, expire_on_commit=False
    )
    _models_dict: dict[Table, str] = {}
    models_to_insert_initially: dict[Table, list[dict]] = {}

    @asynccontextmanager
    @classmethod
    async def get_async_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """
        Provides an async transactional scope around a series of operations.
        Ensures that changes are committed after the operation is complete, or
        rolled back if an error occurs.

        Yields:
            AsyncSession: An SQLAlchemy session object for interacting with the database.
        """
        async with cls._AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()  # Commit changes after yield
            except Exception as e:
                await session.rollback()  # Rollback if exception occurs
                raise e

    @classmethod
    async def __insert_initial_data(cls) -> None:
        """
        Inserts initial data into the tables for models specified in
        `models_to_insert_initially`. Each model is associated with a list
        of dictionaries representing rows to be inserted.
        """
        for model_to_insert, rows_to_insert in cls.models_to_insert_initially.items():
            model_to_insert.insert_many(rows_to_insert)

    @classmethod
    async def init_db(cls) -> None:
        """
        Initializes the database by creating tables and inserting initial data.
        The tables are created using SQLAlchemy's `metadata.create_all` method,
        and the initial data is inserted via the `__insert_initial_data` method.
        """
        import_all_sql_models()
        async with cls._engine.begin() as conn:
            await conn.run_sync(cls.metadata.create_all)  # Ensure tables exist
            await cls.__insert_initial_data()  # Insert initial data

    @classmethod
    def __get_foreign_keys(cls) -> list[tuple[str, Table, str]]:
        """
        Retrieves all foreign key relationships for the class. It returns
        a list of tuples containing the column name, the related table, and
        the related table's column name.

        Returns:
            list[tuple]: A list of tuples containing foreign key information.
        """
        mapper = inspect(cls)
        return [
            (column.name, fk.column.table, fk.column.name)
            for column in mapper.columns
            for fk in column.foreign_keys
        ]

    @classmethod
    def __get_unique_keys(cls):
        """
        Retrieves a list of columns that have a unique constraint in the class.

        Returns:
            list: A list of column names that have unique constraints.
        """
        mapper = inspect(cls)
        return [column.name for column in mapper.columns if column.unique]

    @classmethod
    async def __data_check(cls, data: dict, session: AsyncSession) -> "Base":
        """
        Checks the validity of the data by verifying foreign keys and unique keys.
        If the data passes validation, it is used to create a new instance of
        the class. If any validation error occurs (e.g., invalid foreign key,
        duplicate unique key), an exception is raised.

        Args:
            data (dict): The data to be validated and inserted.
            session (AsyncSession): The session object used to query the database.

        Returns:
            Base: An instance of the class with the provided data.

        Raises:
            NotAValidForeignKey: If a foreign key is invalid.
            ElementAlreadyExists: If an element with a unique constraint already exists.
        """
        fk_keys = cls.__get_foreign_keys()
        unique_keys = cls.__get_unique_keys()

        for column_name, related_table, related_table_column in fk_keys:
            foreign_key_attr = cls._models_dict[related_table]
            foreign_key_value = data[foreign_key_attr]

            if foreign_key_value:
                stmt = select(related_table).filter_by(
                    **{foreign_key_attr: foreign_key_value}
                )
                result = await session.execute(stmt)
                matching_record = result.scalar_one_or_none()

                if not matching_record:
                    raise NotAValidForeignKey()

                data[column_name] = getattr(matching_record, related_table_column)
                del data[foreign_key_attr]  # Remove the key used for the query
            else:
                data[column_name] = None

        for col in unique_keys:
            if data[col]:
                stmt = select(cls.__table__).filter_by(**{col: data[col]})
                result = await session.execute(stmt)
                matching_record = result.scalar_one_or_none()
                if matching_record:
                    raise ElementAlreadyExists()

        return cls(**data)

    async def insert(self, data: dict) -> None:
        """
        Inserts a new record into the database after validating the provided data.

        Args:
            data (dict): The data to be inserted into the table.
        """
        async with self.get_async_session() as session:
            obj = await self.__data_check(data, session)
            session.add(obj)

    @classmethod
    async def insert_many(cls, data: list[dict]) -> None:
        """
        Inserts multiple records into the database after validating the provided data.

        Args:
            data (list): A list of dictionaries containing the data to be inserted.
        """
        objects_to_insert = []
        async with cls.get_async_session() as session:
            for dictionary in data:
                obj = await cls.__data_check(dictionary, session)
                await session.flush([obj])
                objects_to_insert.append(obj)
            session.add_all(objects_to_insert)


def get_app_config():
    from .app_config import AppConfig

    return AppConfig


def get_function():
    from .function import Function

    return Function


def get_level():
    from .level import Level

    return Level


def get_mm_function_role():
    from .mm_role_function import MmFunctionRoles

    return MmFunctionRoles


def get_player():
    from .player import Player

    return Player


def get_role():
    from .role import Role

    return Role


def get_transactions():
    from .transactions import Transaction

    return Transaction


def get_user():
    from .user import User

    return User


def import_all_sql_models():
    get_app_config()
    get_function()
    get_role()
    get_mm_function_role()
    get_level()
    get_user()
    get_player()
    get_transactions()
