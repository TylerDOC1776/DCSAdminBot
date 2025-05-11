import asyncio
import discord
from discord.ext import commands
from config_loader import load_config
from log_monitor import background_task
from commands import register_commands

config = load_config()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    channel = bot.get_channel(config['COMMAND_CHANNEL_ID'])
    if channel:
        await channel.send("📡 DCS Admin Bot is online and ready.")

def run_bot():
    register_commands(bot)
    asyncio.run(main())

async def main():
    asyncio.create_task(background_task(bot))
    await bot.start(config['DISCORD_BOT_TOKEN'])
