# 🎮 DCS Admin Bot

Manage your DCS World server instances via Discord commands with live monitoring and auto-restart capabilities.

---

## 📁 Project Structure

```
DCSAdminBot/
├── DCS_admin_bot.py          # Main entry point
├── bot_core.py               # Bot event and startup logic
├── commands.py               # All Discord bot commands
├── config_loader.py          # Loads bot and server config
├── log_monitor.py            # Crash monitoring
├── server_control.py         # PowerShell interface
├── requirements.txt
├── README.md
├── Scripts/
│   └── DCSManage.ps1         # PowerShell control script
├── Logs/
│   └── bot_actions.log       # Activity logs
└── config/
    ├── config.json           # Discord token, webhook, channel
    └── servers.json          # DCS instance definitions
```

---

## 🧩 Prerequisites

- ✅ Python 3.10+ installed
- ✅ DCS World servers installed and configured
- ✅ A Discord bot application created at [discord.com/developers](https://discord.com/developers)
- ✅ `MESSAGE CONTENT INTENT` enabled in the bot settings

---

## 🧱 Step 1: Clone the Repo

```bash
git clone https://github.com/TylerDOC1776/DCSAdminBot.git
cd DCSAdminBot
```
Or download and extract the ZIP.

---

## ⚙️ Step 2: Configure Settings

### `config/config.json` (Create this)

```json
{
  "command_channel_id": 123456789012345678,
  "discord_webhook": "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN",
  "discord_bot_token": "YOUR_DISCORD_BOT_TOKEN"
}
```

💡 To get your channel ID:
- Enable Developer Mode in Discord (User Settings > Advanced)
- Right-click your channel → **Copy ID**

---

### `config/servers.json` (One or more instances)

```json
{
  "instances": {
    "southern": {
      "name": "Servername",
      "exe": "C:\\Program Files\\Eagle Dynamics\\DCS World Server\\bin\\DCS_server.exe",
      "log": "C:/Users/YOUR_USERNAME/Saved Games/Servername/Logs/dcs.log"
    }
  }
}
```

Add more entries like `"memphis"`, `"smokey"` as needed.

---

## 📦 Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Step 4: Run the Bot

```bash
python DCS_admin_bot.py
```

---

## 🖥️ Step 5 (Optional): Auto-Start on Boot

You can use `start_bot.bat` or the included `DCSAdminBot_Task.xml`.

**Recommended Task Scheduler Settings:**
- **Action:** `python C:\DCSAdminBot\DCS_admin_bot.py`
- **Run with highest privileges**
- **Trigger on user logon**

---

## 💬 Discord Commands

| Command                  | Description                            |
|--------------------------|----------------------------------------|
| `!start <server>`        | Start a specific DCS instance          |
| `!stop <server>`         | Stop a specific instance               |
| `!restart <server|all>`  | Restart a server or all instances      |
| `!status`                | Show current running status            |
| `!clear`                 | Delete bot messages                    |
| `!loadmiz <server>`      | Upload and load a `.miz` mission       |
| `!resetpersist <server>` | Reset Foothold persistence files       |
| `!resetstats <server>`   | Archive and reset player stats         |
| `!listmissions`          | View available `.miz` files            |
| `!choose <num> <server>` | Load a listed mission                  |
| `!help`                  | Display all commands                   |

---

## 🧠 Crash Detection & Auto-Restart

- Scans `dcs.log` for critical errors (e.g., access violations)
- Watches processes to detect crashes
- Auto-restarts the affected server
- Logs everything to `Logs/bot_actions.log`

---

## ⚙️ Task Scheduler Auto-Start (Optional)

The `DCSAdminBot_Task.xml` automates startup:

- Launches both the bot and your PowerShell instance startup
- Set to "Run with highest privileges"
- Triggered on user login

To import:

1. Open **Task Scheduler**
2. Choose **Import Task**
3. Select `DCSAdminBot_Task.xml`
4. Set it to run as your user

---

## 📜 License

MIT License (or customize for your internal use)
