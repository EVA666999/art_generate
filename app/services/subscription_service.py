"""
Сервис для работы с подписками пользователей.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.subscription import UserSubscription, SubscriptionType, SubscriptionStatus
from app.models.user import Users
from app.schemas.subscription import SubscriptionStatsResponse, SubscriptionInfoResponse


class SubscriptionService:
    """Сервис для управления подписками."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Получает подписку пользователя."""
        query = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_subscription(self, user_id: int, subscription_type: str) -> UserSubscription:
        """Создает подписку для пользователя."""
        print(f"🔍 DEBUG: Создание подписки для пользователя {user_id}, тип: {subscription_type}")
        
        # Определяем параметры подписки
        if subscription_type.lower() == "base":
            monthly_credits = 100
            monthly_photos = 10
            max_message_length = 100
        elif subscription_type.lower() == "standard":
            monthly_credits = 2000
            monthly_photos = 0  # Убираем генерации фото
            max_message_length = 200
        elif subscription_type.lower() == "premium":
            monthly_credits = 6000
            monthly_photos = 50  # Добавляем генерации фото для Premium
            max_message_length = 300
        else:
            print(f"[ERROR] DEBUG: Неподдерживаемый тип подписки: {subscription_type}")
            raise ValueError(f"Неподдерживаемый тип подписки: {subscription_type}")
        
        print(f"[OK] DEBUG: Параметры подписки - кредиты: {monthly_credits}, фото: {monthly_photos}, длина: {max_message_length}")
        
        # Проверяем, есть ли уже подписка
        existing_subscription = await self.get_user_subscription(user_id)
        if existing_subscription:
            print(f"🔍 DEBUG: Найдена существующая подписка: {existing_subscription.subscription_type.value}, активна: {existing_subscription.is_active}")
            
            # Если подписка активна и того же типа, возвращаем её
            if existing_subscription.is_active and existing_subscription.subscription_type.value == subscription_type.lower():
                print(f"[OK] DEBUG: Подписка того же типа уже активна, возвращаем существующую")
                return existing_subscription
            
            # Обновляем существующую подписку (независимо от статуса)
            print(f"🔄 DEBUG: Обновляем существующую подписку на {subscription_type}")
            existing_subscription.subscription_type = SubscriptionType(subscription_type.lower())
            existing_subscription.status = SubscriptionStatus.ACTIVE
            existing_subscription.monthly_credits = monthly_credits
            existing_subscription.monthly_photos = monthly_photos
            existing_subscription.max_message_length = max_message_length
            existing_subscription.used_credits = 0
            existing_subscription.used_photos = 0
            existing_subscription.activated_at = datetime.utcnow()
            existing_subscription.expires_at = datetime.utcnow() + timedelta(days=30)
            existing_subscription.last_reset_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing_subscription)
            
            # Переводим средства на баланс пользователя
            await self.add_credits_to_user_balance(user_id, monthly_credits)
            
            return existing_subscription
        
        # Создаем новую подписку
        subscription = UserSubscription(
            user_id=user_id,
            subscription_type=SubscriptionType(subscription_type.lower()),
            status=SubscriptionStatus.ACTIVE,
            monthly_credits=monthly_credits,
            monthly_photos=monthly_photos,
            max_message_length=max_message_length,
            used_credits=0,
            used_photos=0,
            activated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            last_reset_at=datetime.utcnow()
        )
        
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        
        # Переводим средства на баланс пользователя
        await self.add_credits_to_user_balance(user_id, monthly_credits)
        
        return subscription
    
    async def add_credits_to_user_balance(self, user_id: int, credits: int) -> bool:
        """Добавляет кредиты на баланс пользователя."""
        try:
            # Получаем пользователя
            user_query = select(Users).where(Users.id == user_id)
            result = await self.db.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Обновляем баланс пользователя
            user.coins += credits
            await self.db.commit()
            await self.db.refresh(user)
            
            return True
        except Exception as e:
            print(f"Ошибка добавления кредитов на баланс: {e}")
            return False
    
    async def create_base_subscription(self, user_id: int) -> UserSubscription:
        """Создает базовую подписку для пользователя (для обратной совместимости)."""
        return await self.create_subscription(user_id, "base")
    
    async def get_subscription_stats(self, user_id: int) -> Dict[str, Any]:
        """Получает статистику подписки пользователя."""
        subscription = await self.get_user_subscription(user_id)
        
        if not subscription:
            # Если подписки нет, возвращаем значения по умолчанию
            return {
                "subscription_type": "none",
                "status": "inactive",
                "monthly_credits": 0,
                "monthly_photos": 0,
                "used_credits": 0,
                "used_photos": 0,
                "credits_remaining": 0,
                "photos_remaining": 0,
                "days_left": 0,
                "is_active": False,
                "expires_at": None,
                "last_reset_at": None
            }
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        return {
            "subscription_type": subscription.subscription_type.value,
            "status": subscription.status.value,
            "monthly_credits": subscription.monthly_credits,
            "monthly_photos": subscription.monthly_photos,
            "used_credits": subscription.used_credits,
            "used_photos": subscription.used_photos,
            "credits_remaining": subscription.credits_remaining,
            "photos_remaining": subscription.photos_remaining,
            "days_left": subscription.days_until_expiry,
            "is_active": subscription.is_active,
            "expires_at": subscription.expires_at,
            "last_reset_at": subscription.last_reset_at
        }
    
    async def can_user_send_message(self, user_id: int, message_length: int = 0) -> bool:
        """Проверяет, может ли пользователь отправить сообщение."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        # Проверяем длину сообщения
        if not subscription.can_send_message(message_length):
            return False
        
        # Для сообщений требуется 2 кредита
        return subscription.can_use_credits(2)
    
    async def can_user_generate_photo(self, user_id: int) -> bool:
        """Проверяет, может ли пользователь сгенерировать фото."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        return subscription.can_generate_photo()
    
    async def use_message_credits(self, user_id: int) -> bool:
        """Тратит кредиты за отправку сообщения."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        # Тратим 2 кредита за сообщение
        success = subscription.use_credits(2)
        if success:
            await self.db.commit()
            await self.db.refresh(subscription)
        
        return success
    
    async def use_photo_generation(self, user_id: int) -> bool:
        """Тратит генерацию фото."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        success = subscription.use_photo_generation()
        if success:
            await self.db.commit()
            await self.db.refresh(subscription)
        
        return success
    
    async def get_subscription_info(self, user_id: int) -> Optional[SubscriptionInfoResponse]:
        """Получает полную информацию о подписке пользователя."""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return None
        
        # Проверяем, нужно ли сбросить месячные лимиты
        if subscription.should_reset_limits():
            subscription.reset_monthly_limits()
            await self.db.commit()
            await self.db.refresh(subscription)
        
        return SubscriptionInfoResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            subscription_type=subscription.subscription_type.value,
            status=subscription.status.value,
            monthly_credits=subscription.monthly_credits,
            monthly_photos=subscription.monthly_photos,
            used_credits=subscription.used_credits,
            used_photos=subscription.used_photos,
            credits_remaining=subscription.credits_remaining,
            photos_remaining=subscription.photos_remaining,
            activated_at=subscription.activated_at,
            expires_at=subscription.expires_at,
            last_reset_at=subscription.last_reset_at,
            is_active=subscription.is_active,
            days_until_expiry=subscription.days_until_expiry
        )
