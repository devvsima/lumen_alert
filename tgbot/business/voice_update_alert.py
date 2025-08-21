from database.connect import async_session
from database.services.tg_users import TgUser
from tgbot.keyboards.inline.alert import ds_link_ikb
from tgbot.loader import bot
from utils.logging import logger


async def send_join_alert(text: str):
    """Отправляет уведомления о присоединении к голосовому каналу"""
    try:
        async with async_session() as session:
            user_ids = await TgUser.get_users_for_join_alerts(session)

            for user_id in user_ids:
                await bot.send_message(
                    chat_id=user_id, text=text, reply_markup=ds_link_ikb(), parse_mode="HTML"
                )
                logger.info(f"Join alert sent to {user_id} | {text}")
    except Exception as e:
        logger.error(f"Error in send_join_alert: {e}")


async def send_leave_alert(text: str):
    """Отправляет уведомления о покидании голосового канала"""
    try:
        async with async_session() as session:
            user_ids = await TgUser.get_users_for_leave_alerts(session)

            for user_id in user_ids:
                await bot.send_message(
                    chat_id=user_id, text=text, reply_markup=ds_link_ikb(), parse_mode="HTML"
                )
                logger.info(f"Leave alert sent to {user_id} | {text}")
    except Exception as e:
        logger.error(f"Error in send_leave_alert: {e}")


async def send_switch_alert(text: str):
    """Отправляет уведомления о переключении между голосовыми каналами"""
    try:
        async with async_session() as session:
            user_ids = await TgUser.get_users_for_switch_alerts(session)

            for user_id in user_ids:
                await bot.send_message(
                    chat_id=user_id, text=text, reply_markup=ds_link_ikb(), parse_mode="HTML"
                )
                logger.info(f"Switch alert sent to {user_id} | {text}")
    except Exception as e:
        logger.error(f"Error in send_switch_alert: {e}")


# Для обратной совместимости
async def send_alert_to_users(text: str):
    """Отправляет уведомления всем пользователям (для обратной совместимости)"""
    await send_join_alert(text)
