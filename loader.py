from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import tg_token
from app.middlewares.i18n import setup_middleware

storage = MemoryStorage()
from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.voice_states = True  # Для работы с состоянием голосовых каналов

# Создаем экземпляры ботов
discord_client = commands.Bot(command_prefix='!', intents=intents)
tgbot = Bot(tg_token, parse_mode="html")
dp = Dispatcher(bot=tgbot, storage=storage)

i18n = setup_middleware(dp)
_ = i18n.gettext