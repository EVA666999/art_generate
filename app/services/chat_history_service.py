from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from app.models.chat_history import ChatHistory
from app.models.user import Users


class ChatHistoryService:
    """Сервис для управления историей чата."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_message(
        self, 
        user_id: int, 
        character_name: str, 
        message_type: str, 
        message_content: str,
        session_id: str = "default",
        image_url: Optional[str] = None,
        image_filename: Optional[str] = None
    ) -> ChatHistory:
        """
        Сохраняет сообщение в историю чата.
        Автоматически удаляет старые сообщения, оставляя только последние 20.
        """
        # Проверяем права пользователя на сохранение истории
        from app.models.user import Users
        from sqlalchemy.orm import selectinload
        stmt_user = select(Users).options(selectinload(Users.subscription)).filter(Users.id == user_id)
        result_user = await self.db.execute(stmt_user)
        user = result_user.scalar_one_or_none()
        
        if not user or not user.subscription:
            raise ValueError("Пользователь не найден или не имеет подписки")
        
        # Проверяем тип подписки
        subscription_type = user.subscription.subscription_type.value.lower()
        if subscription_type == 'base':
            raise ValueError("Пользователи с подпиской Base не могут сохранять историю чата")
        
        # Создаем новое сообщение
        chat_message = ChatHistory(
            user_id=user_id,
            character_name=character_name,
            session_id=session_id,
            message_type=message_type,
            message_content=message_content,
            image_url=image_url,
            image_filename=image_filename
        )
        
        self.db.add(chat_message)
        await self.db.flush()  # Получаем ID нового сообщения
        
        # Удаляем старые сообщения, оставляя только последние 20 для этого персонажа
        await self._cleanup_old_messages(user_id, character_name)
        
        await self.db.commit()
        return chat_message
    
    async def get_chat_history(
        self, 
        user_id: int, 
        character_name: str, 
        limit: int = 20
    ) -> List[ChatHistory]:
        """
        Получает историю чата для конкретного персонажа.
        Возвращает последние сообщения в хронологическом порядке.
        """
        stmt = (
            select(ChatHistory)
            .filter(
                ChatHistory.user_id == user_id,
                ChatHistory.character_name == character_name
            )
            .order_by(ChatHistory.created_at.asc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        return list(messages)
    
    async def get_characters_with_history(self, user_id: int) -> List[str]:
        """
        Получает список персонажей, с которыми у пользователя есть история чата.
        """
        stmt = (
            select(ChatHistory.character_name)
            .filter(ChatHistory.user_id == user_id)
            .distinct()
        )
        
        result = await self.db.execute(stmt)
        characters = result.scalars().all()
        
        return list(characters)
    
    async def clear_chat_history(self, user_id: int, character_name: str) -> bool:
        """
        Очищает историю чата для конкретного персонажа.
        """
        try:
            stmt = (
                select(ChatHistory)
                .filter(
                    ChatHistory.user_id == user_id,
                    ChatHistory.character_name == character_name
                )
            )
            
            result = await self.db.execute(stmt)
            messages_to_delete = result.scalars().all()
            
            deleted_count = len(messages_to_delete)
            for message in messages_to_delete:
                await self.db.delete(message)
            
            await self.db.commit()
            return deleted_count > 0
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_history_stats(self, user_id: int) -> dict:
        """
        Получает статистику истории чата пользователя.
        """
        # Получаем пользователя с подпиской (загружаем подписку явно)
        from app.models.user import Users
        from sqlalchemy.orm import selectinload
        stmt_user = select(Users).options(selectinload(Users.subscription)).filter(Users.id == user_id)
        result_user = await self.db.execute(stmt_user)
        user = result_user.scalar_one_or_none()
        
        if not user:
            return {
                "total_messages": 0,
                "characters_with_history": 0,
                "can_save_history": False
            }
        
        # Проверяем подписку пользователя
        can_save_history = False
        if user.subscription:
            subscription_type = user.subscription.subscription_type.value.lower()
            can_save_history = subscription_type != 'base'
        
        # Подсчитываем общее количество сообщений
        stmt_total = select(ChatHistory).filter(ChatHistory.user_id == user_id)
        result_total = await self.db.execute(stmt_total)
        total_messages = len(result_total.scalars().all())
        
        # Получаем количество персонажей с историей
        characters_count = len(await self.get_characters_with_history(user_id))
        
        return {
            "total_messages": total_messages,
            "characters_with_history": characters_count,
            "can_save_history": can_save_history
        }
    
    async def _cleanup_old_messages(self, user_id: int, character_name: str, keep_count: int = 20):
        """
        Удаляет старые сообщения, оставляя только последние keep_count сообщений.
        """
        # Получаем все сообщения для этого персонажа, отсортированные по дате
        stmt = (
            select(ChatHistory)
            .filter(
                ChatHistory.user_id == user_id,
                ChatHistory.character_name == character_name
            )
            .order_by(desc(ChatHistory.created_at))
        )
        
        result = await self.db.execute(stmt)
        all_messages = result.scalars().all()
        
        # Если сообщений больше чем нужно, удаляем лишние
        if len(all_messages) > keep_count:
            messages_to_delete = all_messages[keep_count:]
            for message in messages_to_delete:
                await self.db.delete(message)
