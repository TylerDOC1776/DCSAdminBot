# DCS Admin Bot

This bot manages your DCS World server instances via Discord commands and background monitoring.

---

## 📁 Project Structure

```
DCSAdminBot/
├── DCS_admin_bot.py            # Entry point
├── bot_core.py
├── commands.py
├── config_loader.py
├── log_monitor.py
├── server_control.py
├── requirements.txt
├── README.md
├── Scripts/
│   └── DCSManage.ps1           # PowerShell controller
├── Logs/
│   └── bot_actions.log         # Bot command + error logs
└── config/
    ├── config.json             # Token, webhook, channel ID
    └── servers.json            # Instance names and paths
```

---

## 🧩 Prerequisites

- ✅ Python 3.10 or newer installed
- ✅ DCS World servers already installed and working
- ✅ A Discord bot application created at [discord.com/developers](https://discord.com/developers)
- ✅ Your bot has `MESSAGE CONTENT INTENT` enabled

---

## 🧱 1. Clone or Download the Project

```bash
git clone https://github.com/yourusername/DCSAdminBot.git
cd DCSAdminBot
```

Or extract the ZIP.

---

## ⚙️ 2. Configure Your Settings

### `config/config.json`
```json
{
  "command_channel_id": 123456789012345678,
  "discord_webhook": "https://discord.com/api/webhooks/...",
  "discord_bot_token": "YOUR_DISCORD_BOT_TOKEN"
}
```

To get your Discord channel ID:
- Enable Developer Mode (Discord > Settings > Advanced)
- Right-click the channel > "Copy ID"

---

### `config/servers.json`

```json
{
  "instances": {
    "southern": {
      "name": "SouthernBBQ",
      "exe": "C:\\Program Files\\Eagle Dynamics\\DCS World Server\\bin\\DCS_server.exe",
      "log": "C:/Users/YOUR_USERNAME/Saved Games/SouthernBBQ/Logs/dcs.log"
    }
  }
}
```

---

## 📦 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 4. Run the Bot

```bash
python DCS_admin_bot.py
```

---

## 💻 5. Optional: Auto-start with Windows

Use `start_bot.bat` or Windows Task Scheduler:
```bash
python C:\DCSAdminBot\DCS_admin_bot.py
```
✅ Make sure “Run with highest privileges” is enabled.

---

## 📟 Discord Bot Commands

| Command                | Description                                         |
|------------------------|-----------------------------------------------------|
| `!start <server>`      | Start a specific server instance                    |
| `!stop <server>`       | Stop a specific server                              |
| `!restart <server|all|windows>` | Restart server(s) or reboot the machine    |
| `!status`              | Show running status of all configured servers       |
| `!clear`               | Delete bot responses and command messages           |
| `!help`                | Show available commands                             |

---

## 🧠 Crash Detection & Auto-Restart

The bot will:
- Monitor each instance’s `dcs.log` for fatal errors (e.g., `Access violation`)
- Watch active processes for unexpected shutdowns
- Auto-restart any failed server
- Log all actions to `Logs/bot_actions.log`

---

## 📜 License

MIT License (or customize for your usage)


---

## ⚙️ Auto-Start Task Scheduler Setup

A prebuilt XML file (`DCSAdminBot_Task.xml`) is included in the repo.

It is configured to:
- Launch `start_bot.bat` on user logon
- Run with elevated privileges
- Start both the PowerShell script (to start and sanitize all DCS instances) and the Python bot

To import it:
1. Open Task Scheduler
2. Choose "Import Task"
3. Select `DCSAdminBot_Task.xml`
4. Set it to run as your user with highest privileges

