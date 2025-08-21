"""
Временное решение для настроек уведомлений
Использует существующие поля базы данных для хранения настроек
"""
from sqlalchemy.ext.asyncio import AsyncSession
from database.services.tg_users import TgUser
from utils.logging import logger


class AlertSettings:
    """Класс для работы с настройками уведомлений через существующие поля"""
    
    @staticmethod
    def encode_settings(alert_on_join: bool = True, alert_on_leave: bool = False, alert_on_switch: bool = False) -> int:
        """Кодирует настройки в число для хранения в поле referral"""
        result = 0
        if alert_on_join:
            result |= 1  # бит 0
        if alert_on_leave:
            result |= 2  # бит 1
        if alert_on_switch:
            result |= 4  # бит 2
        return result
    
    @staticmethod
    def decode_settings(encoded: int) -> dict:
        """Декодирует настройки из числа"""
        return {
            'alert_on_join': bool(encoded & 1),
            'alert_on_leave': bool(encoded & 2),
            'alert_on_switch': bool(encoded & 4)
        }
    
    @staticmethod
    async def get_user_settings(session: AsyncSession, user_id: int) -> dict:
        """Получает настройки пользователя"""
        user = await TgUser.get_by_id(session, user_id)
        if not user:
            return {'alert_on_join': True, 'alert_on_leave': False, 'alert_on_switch': False}
        
        # Если у пользователя есть новые поля - используем их
        if hasattr(user, 'alert_on_join'):
            return {
                'alert_on_join': getattr(user, 'alert_on_join', True),
                'alert_on_leave': getattr(user, 'alert_on_leave', False),
                'alert_on_switch': getattr(user, 'alert_on_switch', False)
            }
        
        # Иначе используем поле referral для хранения битовой маски
        # Берем только последние 3 бита для настроек (остальные для реферралов)
        settings_bits = user.referral & 7  # 7 = 0b111 (последние 3 бита)
        return AlertSettings.decode_settings(settings_bits)
    
    @staticmethod
    async def update_user_settings(session: AsyncSession, user_id: int, **settings) -> bool:
        """Обновляет настройки пользователя"""
        try:
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                return False
            
            # Если у пользователя есть новые поля - используем их
            if hasattr(user, 'alert_on_join'):
                for key, value in settings.items():
                    if value is not None:
                        setattr(user, key, value)
            else:
                # Используем поле referral для хранения настроек
                current_settings = await AlertSettings.get_user_settings(session, user_id)
                current_settings.update({k: v for k, v in settings.items() if v is not None})
                
                # Кодируем новые настройки
                encoded_settings = AlertSettings.encode_settings(**current_settings)
                
                # Сохраняем количество рефералов (старшие биты) и новые настройки (младшие биты)
                referral_count = user.referral >> 3  # Сдвигаем на 3 бита влево
                user.referral = (referral_count << 3) | encoded_settings
            
            await session.commit()
            logger.info(f"Updated settings for user {user_id}: {settings}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating settings for user {user_id}: {e}")
            await session.rollback()
            return False
