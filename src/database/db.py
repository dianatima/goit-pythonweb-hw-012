import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Клас для управління асинхронними сесіями бази даних.

    - _engine (AsyncEngine): Асинхронний двигун для підключення до бази даних.
    - _session_maker (async_sessionmaker): Фабрика для створення сесій.

    """
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Контекстний менеджер для створення і управління сесією бази даних.

        Піднімає:
        - Exception: Якщо фабрика сесій не ініціалізована.
        - SQLAlchemyError: У разі виникнення помилок під час роботи із сесією.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Генератор для отримання сесії бази даних у залежностях FastAPI.

    Приклад використання:
    ```
    @router.get("/")
    async def example_endpoint(db: AsyncSession = Depends(get_db)):
        # Використовуйте db для роботи з базою даних
    ```
    """
    async with sessionmanager.session() as session:
        yield session
