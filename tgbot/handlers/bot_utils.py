from database.connect import async_session
from database.services.tg_users import TgUser
from tgbot.keyboards.inline.alert import ds_link_ikb
from tgbot.loader import bot
from utils.logging import logger


async def send_telegram_message(text):
    try:
        async with async_session() as session:
            user_ids = await TgUser.get_alert_user_ids(session)

            for user_id in user_ids:
                await bot.send_message(chat_id=user_id, text=text, reply_markup=ds_link_ikb())
                logger.info(f"Message sent to {user_id} | {text}")
    except Exception as e:
        logger.error(f"Error in send_telegram_message: {e}")
