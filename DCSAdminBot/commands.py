from discord.ext import commands
from server_control import control_dcs_instance, is_instance_running
from config_loader import load_config
from load_miz import upload_and_load_mission
from datetime import datetime
from config_loader import load_config
import os
import subprocess
import psutil
import asyncio
import shutil

config = load_config()

LOG_DIR = "C:\\DCSAdminBot\\Logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "bot_actions.log")

FATAL_KEYWORDS = ["Access violation", "Unhandled exception"]
DCS_PROCESS_NAME = "DCS_server"
last_known_state = {k: True for k in config["SERVERS"]}

def log_bot_action(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def resolve_instance_name(key):
    return config["SERVERS"].get(key, {}).get("name")

async def monitor_dcs_logs(bot):
    for key, info in config["SERVERS"].items():
        try:
            with open(info["log"], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-50:]
                for line in lines:
                    if any(fatal in line for fatal in FATAL_KEYWORDS):
                        await notify_and_restart(bot, key, line.strip())
                        return
        except Exception as e:
            log_bot_action(f"[ERROR] Reading log for {key}: {e}")

async def monitor_processes(bot):
    for key, info in config["SERVERS"].items():
        expected = info["name"]
        is_running = any(expected in ' '.join(p.info['cmdline']) for p in psutil.process_iter(['name', 'cmdline']) if p.info['name'] == DCS_PROCESS_NAME)
        if last_known_state[key] and not is_running:
            await notify_and_restart(bot, key, "Process exited unexpectedly")
        last_known_state[key] = is_running

async def notify_and_restart(bot, server_key, reason):
    channel = bot.get_channel(config['COMMAND_CHANNEL_ID'])
    msg = f"❌ `{server_key}` crashed or had a fatal error: {reason}\n♻️ Attempting restart..."
    if channel:
        await channel.send(msg)
    log_bot_action(msg)
    os.system(f'powershell -ExecutionPolicy Bypass -File "Scripts/DCSManage.ps1" -Action restart -Target {server_key}')

async def background_task(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await monitor_dcs_logs(bot)
            await monitor_processes(bot)
        except Exception as e:
            log_bot_action(f"[LOG MONITOR ERROR] {e}")
        await asyncio.sleep(60)

def register_commands(bot):
    user_mission_selection = {}
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
        if not resolve_instance_name(target):
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

        command_keywords = [
            "!start", "!stop", "!restart", "!status", "!clear", "!help",
            "!loadmiz", "!resetpersist", "!resetstats", "!listmissions", "!choose"
        ]

        emoji_keywords = ["✅", "🛑", "📦", "♻️", "📊", "📄", "🧾", "🪟", "📱", "❌", "🩾"]

        async for msg in ctx.channel.history(limit=200):
            if (
                msg.author == bot.user or
                any(msg.content.startswith(cmd) for cmd in command_keywords) or
                any(sym in msg.content for sym in emoji_keywords)
            ):
                try:
                    await msg.delete()
                    deleted += 1
                except Exception as e:
                    print(f"⚠️ Could not delete message: {e}")

        await ctx.send(f"✅ Cleared {deleted} bot-related messages.")
        log_bot_action(f"{ctx.author} ran !clear and removed {deleted} messages")


    @bot.command()
    async def loadmiz(ctx, instance: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return
        if not resolve_instance_name(instance):
            await ctx.send(f"❌ Unknown server: `{instance}`")
            return
        if not ctx.message.attachments:
            await ctx.send("❌ Please attach a `.miz` file.")
            return
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.miz'):
            await ctx.send("❌ Invalid file type. Only `.miz` files are accepted.")
            return
        try:
            file_bytes = await attachment.read()
            success, msg = upload_and_load_mission(attachment.filename, file_bytes, instance)
            await ctx.send(f"✅ {msg}" if success else f"❌ {msg}")
            log_bot_action(f"{ctx.author} uploaded and loaded mission `{attachment.filename}` to {instance}")
        except Exception as e:
            await ctx.send(f"❌ Failed to process file: {e}")
            log_bot_action(f"[ERROR] {ctx.author} failed !loadmiz: {e}")

    @bot.command()
    async def resetpersist(ctx, instance: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        full_name = resolve_instance_name(instance)
        if not full_name:
            await ctx.send(f"❌ Unknown server: `{instance}`")
            return

        try:
            save_dir = os.path.join(
                config["DCS_SAVED_GAMES"],
                full_name,
                "Missions",
                "Saves"
            )

            if not os.path.exists(save_dir):
                await ctx.send(f"❌ Save folder not found: `{save_dir}`")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_dir = os.path.join(save_dir, f"Backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)

            count = 0
            for file in os.listdir(save_dir):
                if file.lower().endswith((".json", ".lua", ".csv")):
                    shutil.move(os.path.join(save_dir, file), os.path.join(backup_dir, file))
                    count += 1

            await ctx.send(f"♻️ `{instance}` persistence reset. {count} file(s) backed up to `Backup_{timestamp}`.")
            log_bot_action(f"{ctx.author} reset persistence for {instance}, moved {count} files to backup.")

        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
            log_bot_action(f"[ERROR] {ctx.author} failed !resetpersist: {e}")

    @bot.command()
    async def resetstats(ctx, instance: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        full_name = resolve_instance_name(instance)
        if not full_name:
            await ctx.send(f"❌ Unknown server: `{instance}`")
            return

        try:
            save_dir = os.path.join(
                config["DCS_SAVED_GAMES"],
                full_name,
                "EasyStatsPlus",
                "MyMission"
            )

            if not os.path.exists(stats_dir):
                await ctx.send(f"❌ Stats directory not found: `{stats_dir}`")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = stats_dir + "_backup_" + timestamp
            os.rename(stats_dir, backup_dir)

            await ctx.send(f"📊 `{instance}` stats reset. Original folder renamed to `{backup_dir}`.")
            log_bot_action(f"{ctx.author} reset stats for {instance}, renamed to {backup_dir}")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
            log_bot_action(f"[ERROR] {ctx.author} failed !resetstats: {e}")

    @bot.command()
    async def listmissions(ctx):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        folder = config["DCS_ACTIVE_MISSIONS"]
        try:
            miz_files = [f for f in os.listdir(folder) if f.endswith(".miz")]
            if not miz_files:
                await ctx.send("📭 No `.miz` files found in Active Missions.")
                return

            numbered = "\n".join([f"{i+1}. {name}" for i, name in enumerate(miz_files)])
            msg = await ctx.send(f"📄 **Available Missions:**\n```{numbered}```\nReply with `!choose <number> <server>` to load one.")
            user_mission_selection[ctx.author.id] = {"missions": miz_files, "msg_id": msg.id}

            
        except Exception as e:
            await ctx.send(f"❌ Error reading missions: {e}")

    @bot.command()
    async def choose(ctx, number: int, server: str):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return

        if ctx.author.id not in user_mission_selection:
            await ctx.send("❌ You must run `!listmissions` first.")
            return

        if not resolve_instance_name(server):
            await ctx.send(f"❌ Unknown server: `{server}`")
            return

        try:
            selection = user_mission_selection[ctx.author.id]
            missions = selection["missions"]
            if number < 1 or number > len(missions):
                await ctx.send("❌ Invalid mission number.")
                return

            selected_file = missions[number - 1]
            from_path = os.path.join(config["DCS_ACTIVE_MISSIONS"], selected_file)

            with open(from_path, "rb") as f:
                data = f.read()
                success, msg = upload_and_load_mission(selected_file, data, server)

            del user_mission_selection[ctx.author.id]
            # Try to delete the old mission list message
            try:
                old_msg = await ctx.channel.fetch_message(selection["msg_id"])
                await old_msg.delete()
            except Exception as e:
                print(f"⚠️ Could not delete mission list message: {e}")


            await ctx.send(f"📦 Selected mission: `{selected_file}`\n{msg}")
            log_bot_action(f"{ctx.author} used !choose to load {selected_file} into {server}")
        except Exception as e:
            await ctx.send(f"❌ Failed to switch mission: {e}")

    @bot.command()
    async def help(ctx):
        if ctx.channel.id != config['COMMAND_CHANNEL_ID']:
            return
        help_text = """🩾 **DCS Admin Bot Commands:**

`!start <server>` - Start a DCS instance
`!stop <server>` - Stop a DCS instance
`!restart <server|all|windows>` - Restart a DCS instance, all, or reboot the system
`!loadmiz <server>` - Upload and load a `.miz` mission file
`!resetpersist <server>` - Backup and delete persistence files for fresh mission start
`!resetstats <server>` - Rename EasyStatsPlus stats folder for a clean start
`!listmissions` - List available `.miz` missions from the Active Missions folder
`!choose <number> <server>` - Load one of the listed missions onto a server
`!status` - Show current server status
`!clear` - Delete all previous bot messages
`!help` - Show this help message"""
        await ctx.send(help_text)
        log_bot_action(f"{ctx.author} ran !help")
