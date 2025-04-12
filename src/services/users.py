from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.database.models import User


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Ініціалізація сервісу для роботи з користувачами.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Створює нового користувача.

        Створює аватар для користувача за допомогою Gravatar, а потім створює
        користувача в базі даних.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Отримує користувача за ID.

        Аргументи:
            user_id: ID користувача.

        Повертає:
            User або None: Знайдений користувач або None, якщо користувача не знайдено.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Отримує користувача за username.

        Аргументи:
            username: Ім'я користувача.

        Повертає:
            User або None: Знайдений користувач або None, якщо користувача не знайдено.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Отримує користувача за email.

        Аргументи:
            email: Адреса електронної пошти користувача.

        Повертає:
            User або None: Знайдений користувач або None, якщо користувача не знайдено.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Підтверджує email користувача.

        Аргументи:
            email: Адреса електронної пошти користувача.

        Повертає:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Оновлює URL аватара користувача.

        Аргументи:
            email: Адреса електронної пошти користувача.
            url: Новий URL для аватара.

        Повертає:
            User: Оновлений користувач.
        """
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Скидає пароль користувача.

        Аргументи:
            user_id: ID користувача.
            password: Новий пароль для користувача.

        Повертає:
            User: Оновлений користувач.
        """
        # Скидання пароля користувача
        return await self.repository.reset_password(user_id, password)
