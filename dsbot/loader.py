import discord
from discord.ext import commands

from data.config import discord_bot

intents = discord.Intents.default()
intents.voice_states = True

dsbot = commands.Bot(command_prefix="!", intents=intents)


@dsbot.event
async def on_ready():
    if discord_bot.SERVER_ID is None:
        return
    guild = discord.Object(id=discord_bot.SERVER_ID)
    dsbot.tree.copy_global_to(guild=guild)
    await dsbot.tree.sync(guild=guild)
