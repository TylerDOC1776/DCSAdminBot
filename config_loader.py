import os
import json
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    with open("config/servers.json") as f:
        servers = json.load(f)["instances"]
    with open("config/config.json") as f:
        extra = json.load(f)
    return {
        "DISCORD_BOT_TOKEN": extra.get("discord_bot_token", os.getenv("DISCORD_BOT_TOKEN")),
        "ERROR_WEBHOOK_URL": extra.get("discord_webhook"),
        "COMMAND_CHANNEL_ID": int(extra["command_channel_id"]),
        "SERVERS": servers
    }
