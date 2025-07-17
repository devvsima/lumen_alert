import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.voice_states = True

dsbot = commands.Bot(command_prefix="!", intents=intents)
