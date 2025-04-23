from discord.ext import commands
from server_control import control_dcs_instance, is_instance_running
from config_loader import load_config
import os
import subprocess
import datetime

config = load_config()

LOG_DIR = "C:\\DCSAdminBot\\Logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "bot_actions.log")

def log_bot_action(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def register_commands(bot):
    @bot.command()
    async def start(ctx, target: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return
        if control_dcs_instance(target.lower(), "start"):
            await ctx.send(f"✅ `{target}` started.")
            log_bot_action(f"{ctx.author} ran !start {target}")
        else:
            await ctx.send(f"❌ Failed to start `{target}`.")
            log_bot_action(f"{ctx.author} failed to !start {target}")

    @bot.command()
    async def stop(ctx, target: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return
        if control_dcs_instance(target.lower(), "stop"):
            await ctx.send(f"🔝 `{target}` stopped.")
            log_bot_action(f"{ctx.author} ran !stop {target}")
        else:
            await ctx.send(f"❌ Failed to stop `{target}`.")
            log_bot_action(f"{ctx.author} failed to !stop {target}")
    
    @bot.command()
    async def restart(ctx, target: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        if target.lower() == "all":
            os.system(f'powershell -ExecutionPolicy Bypass -File "Scripts/DCSManage.ps1" -Action restart')
            await ctx.send("♻️ Restarted all DCS instances.")
            log_bot_action(f"{ctx.author} ran !restart all")
            return

        if target.lower() == "windows":
            await ctx.send("⚠️ Rebooting Windows in 5 seconds...")
            subprocess.run(["shutdown", "/r", "/t", "5"])
            log_bot_action(f"{ctx.author} triggered !restart windows")
            return

        if target.lower() not in config["SERVERS"]:
            await ctx.send(f"❌ Unknown server: `{target}`")
            return

        os.system(f'powershell -ExecutionPolicy Bypass -File "Scripts/DCSManage.ps1" -Action restart -Target {target}')
        await ctx.send(f"♻️ Restarted `{target}`.")
        log_bot_action(f"{ctx.author} ran !restart {target}")

    @bot.command()
    async def status(ctx):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        await ctx.send("📱 DCS Server Status:")
        for key, instance in config["SERVERS"].items():
            name = instance["name"]
            running = is_instance_running(name)
            status = "✅ Running" if running else "❌ Not Running"
            await ctx.send(f"`{name}`: {status}")
        log_bot_action(f"{ctx.author} ran !status")

    @bot.command()
    async def clear(ctx):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        await ctx.send("🪟 Clearing bot messages and commands...")
        deleted = 0
        command_keywords = ["!start", "!stop", "!restart", "!status", "!clear", "!help"]

        async for msg in ctx.channel.history(limit=200):
            if msg.author == bot.user or any(msg.content.startswith(cmd) for cmd in command_keywords):
                try:
                    await msg.delete()
                    deleted += 1
                except Exception as e:
                    print(f"⚠️ Could not delete message: {e}")

        await ctx.send(f"✅ Cleared {deleted} command/bot messages.")
        log_bot_action(f"{ctx.author} ran !clear and removed {deleted} messages")

    @bot.command()
    async def help(ctx):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        help_text = (
            "🩾 **DCS Admin Bot Commands:**\n"
            "`!start <server>` - Start a DCS instance\n"
            "`!stop <server>` - Stop a DCS instance\n"
            "`!restart <server|all|windows>` - Restart a DCS instance, all, or reboot the system\n"
            "`!status` - Show current server status\n"
            "`!clear` - Delete all previous bot messages\n"
            "`!help` - Show this help message"
        )
        await ctx.send(help_text)
        log_bot_action(f"{ctx.author} ran !help")
