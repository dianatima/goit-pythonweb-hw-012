from datetime import date, timedelta
from typing import List
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Отримати список контактів користувача з можливістю фільтрації.
        """
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(Contact.name.contains(name))
            .where(Contact.surname.contains(surname))
            .where(Contact.email.contains(email))
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Отримати контакт за ID, прив'язаний до конкретного користувача.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Створити новий контакт для користувача.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact | None:
        """
        Оновити існуючий контакт користувача.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Видалити контакт користувача за ID.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def is_contact_exists(self, email: str, phone: str, user: User) -> bool:
        """
        Перевірити, чи існує контакт з вказаним email або телефоном для користувача.
        """
        query = (
            select(Contact)
            .filter_by(user=user)
            .where((Contact.email == email) | (Contact.phone == phone))
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None

    async def get_upcoming_birthdays(self, days: int, user: User) -> list[Contact]:
        """
        Отримати список контактів з днями народження, які наближаються.
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        query = (
            select(Contact)
            .filter_by(user=user)
            .where(
                or_(
                    func.date_part("day", Contact.birthday).between(
                        func.date_part("day", today), func.date_part("day", end_date)
                    ),
                    and_(
                        func.date_part("day", end_date) < func.date_part("day", today),
                        or_(
                            func.date_part("day", Contact.birthday)
                            >= func.date_part("day", today),
                            func.date_part("day", Contact.birthday)
                            <= func.date_part("day", end_date),
                        ),
                    ),
                )
            )
            .order_by(func.date_part("day", Contact.birthday).asc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()
