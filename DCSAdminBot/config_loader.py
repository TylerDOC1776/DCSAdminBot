import os
import json
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    with open("config/servers.json") as f:
        servers = json.load(f)["instances"]
    with open("config/config.json") as f:
        extra = json.load(f)

    sample_log_path = next(iter(servers.values()))["log"]
    base_path = os.path.abspath(os.path.join(sample_log_path, "..", "..", ".."))

    return {
        "DISCORD_BOT_TOKEN": extra.get("discord_bot_token", os.getenv("DISCORD_BOT_TOKEN")),
        "ERROR_WEBHOOK_URL": extra.get("discord_webhook"),
        "COMMAND_CHANNEL_ID": int(extra["command_channel_id"]),
        "SERVERS": servers,
        "DCS_SAVED_GAMES": base_path,
        "DCS_ACTIVE_MISSIONS": os.path.join(base_path, "Active Missions")
    }
