import discord
from discord.ext import commands

from data.config import discord_bot
from database.connect import async_session
from database.services.sources import DiscordSource

intents = discord.Intents.default()
intents.voice_states = True

dsbot = commands.Bot(command_prefix="!", intents=intents)


@dsbot.event
async def on_ready():
    for guild in dsbot.guilds:
        async with async_session() as session:
            await DiscordSource.sync_guild(
                session,
                guild.id,
                guild.name,
                [channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)],
            )
        dsbot.tree.copy_global_to(guild=guild)
        await dsbot.tree.sync(guild=guild)
