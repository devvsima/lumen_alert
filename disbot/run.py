import asyncio

from data.config import DS_SERVER_ID, DS_TOKEN
from loader import discord_client
from tgbot.handlers.bot_utils import send_telegram_message
from utils.logging import logger


@discord_client.event
async def on_voice_state_update(member, before, after):
    # Проверяем, если before.channel был None (не был в голосовом канале), а after.channel не None (теперь в канале)
    if member.guild.id != DS_SERVER_ID:
        return
    if before.channel is None and after.channel is not None:
        text = (
            f"<code>{member.name}</code> присоединился к голосовому каналу - {after.channel.name}"
        )

        await send_telegram_message(text)


async def start_discord_bot():
    await discord_client.start(DS_TOKEN)
