from database.connect import async_session
from database.services.users import User
from sqlalchemy.ext.asyncio import async_sessionmaker
from utils.logging import logger

from tgbot.keyboards.inline.alert import ds_link_ikb
from tgbot.loader import bot


async def send_telegram_message(text):
    print("Sending message to Telegram...")
    logger.info("Attempting to create a database session...")
    async with async_session() as session:
        logger.info("Database session created successfully.")
        user_ids = await User.get_alert_user_ids(session)
        logger.info(f"Fetched user IDs: {user_ids}")
        if not user_ids:
            logger.warning("No users with is_alert == True found.")
        for i in user_ids:
            try:
                await bot.send_message(chat_id=i, text=text, reply_markup=ds_link_ikb())
                logger.info(f"Message sent to {i} | {text}")
            except Exception as e:
                logger.error(f"Failed to send message to {i}: {e}")
