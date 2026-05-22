import discord
from discord.ext import commands
import os
from config import TOKEN, PREFIX

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

# Carrega as cogs
async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())