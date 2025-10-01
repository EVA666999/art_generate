"""
Сервис для работы с монетами пользователей.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import Users


class CoinsService:
    """Сервис для работы с монетами пользователей."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_coins(self, user_id: int) -> Optional[int]:
        """Получает количество монет пользователя."""
        result = await self.db.execute(
            select(Users.coins).where(Users.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def can_user_send_message(self, user_id: int) -> bool:
        """Проверяет, может ли пользователь отправить сообщение (стоимость: 2 монеты)."""
        coins = await self.get_user_coins(user_id)
        return coins is not None and coins >= 2
    
    async def can_user_generate_photo(self, user_id: int) -> bool:
        """Проверяет, может ли пользователь сгенерировать фото (стоимость: 30 монет)."""
        coins = await self.get_user_coins(user_id)
        return coins is not None and coins >= 30
    
    async def spend_coins_for_message(self, user_id: int) -> bool:
        """Тратит 2 монеты за отправку сообщения."""
        try:
            await self.db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(coins=Users.coins - 2)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка траты монет за сообщение: {e}")
            await self.db.rollback()
            return False
    
    async def spend_coins_for_photo(self, user_id: int) -> bool:
        """Тратит 30 монет за генерацию фото."""
        try:
            await self.db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(coins=Users.coins - 30)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка траты монет за фото: {e}")
            await self.db.rollback()
            return False
    
    async def add_coins(self, user_id: int, amount: int) -> bool:
        """Добавляет монеты пользователю."""
        try:
            await self.db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(coins=Users.coins + amount)
            )
            await self.db.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка добавления монет: {e}")
            await self.db.rollback()
            return False
