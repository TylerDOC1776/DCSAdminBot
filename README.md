> [!WARNING]
> **This project is deprecated and no longer maintained.**
> It has been replaced by [dcs-bullseye](https://github.com/TylerDOC1776/dcs-bullseye), a full rewrite with a proper REST API, RBAC, slash commands, multi-host support, and a hardened security model.
> Please use that instead.

---

# 🎮 DCS Admin Bot

Control and monitor your DCS World servers via Discord. Start, stop, update, or restart servers, manage missions, reset persistence/stats, and detect crashes — all from a bot.

---

## 📁 Project Structure

```
DCSAdminBot/
├── DCS_admin_bot.py         # Entrypoint
├── core.py                  # Bot startup and background loop
├── commands.py              # All bot command logic
├── config_loader.py         # Loads .env and servers.json
├── globals.py               # Shared config + state
├── load_miz.py              # Upload/load `.miz` files
├── server_control.py        # PowerShell integration
├── Scripts/
│   └── DCSManage.ps1        # REQUIRED for server control
├── Logs/
│   └── bot_actions.log      # Bot activity log
├── config/
│   └── servers.json         # Defines instance paths
├── .env                     # Discord token + webhook + channel
├── requirements.txt
└── DCSAdminBot_Task.xml     # Optional autostart via Task Scheduler
```

---

## 🧩 Requirements

- ✅ Python 3.10+
- ✅ DCS World server(s) installed
- ✅ PowerShell script `Scripts/DCSManage.ps1` present and working
- ✅ `.env` file with valid Discord bot token and webhook
- ✅ Bot has `MESSAGE CONTENT INTENT` enabled on [Discord Developer Portal](https://discord.com/developers)

---

## 🧱 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/YourUser/DCSAdminBot.git
cd DCSAdminBot
```

---

### 2. Configure the `.env` file

Create a `.env` file in the root folder:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy
COMMAND_CHANNEL_ID=123456789012345678
```

---

### 3. Configure `config/servers.json`

```json
{
  "instances": {
    "alpha": {
      "name": "AlphaInstance",
      "exe": "C:\DCS\AlphaInstance\bin\DCS_server.exe",
      "log": "C:/Users/YourUser/Saved Games/AlphaInstance/Logs/dcs.log"
    },
    "bravo": {
      "name": "BravoInstance",
      "exe": "C:\DCS\BravoInstance\bin\DCS_server.exe",
      "log": "C:/Users/YourUser/Saved Games/BravoInstance/Logs/dcs.log"
    }
  }
}
```

---

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Run the Bot

```bash
python DCS_admin_bot.py
```

---

## ⚙️ Optional: Auto-Start on Boot

Import `DCSAdminBot_Task.xml` into Task Scheduler:

- Action: `start_bot.bat` or direct `python DCS_admin_bot.py`
- Run with highest privileges
- Trigger: At user logon

---

## 💬 Available Commands

| Command                             | Description                                              |
|-------------------------------------|----------------------------------------------------------|
| `!start <server>`                   | Start a DCS instance                                     |
| `!stop <server>`                    | Stop a DCS instance                                      |
| `!restart <server>` / `!restart all` / `!restart windows` | Restart one, all, or reboot the system |
| `!changepass <server>` / `!changepass all` | Change the password for one or all servers        |
| `!loadmiz` _(with file attached)_   | Upload a `.miz` file to the Active Missions folder      |
| `!listmissions`                     | List `.miz` files in the Active Missions folder         |
| `!choose <number> <server>`         | Load selected mission onto a server                     |
| `!delete <number>`                  | Backup and remove a mission from the list               |
| `!resetpersist <server>`            | Backup & clear persistence save files                   |
| `!resetstats <server>`              | Backup EasyStatsPlus stats and reset                    |
| `!status`                           | Show server status, port, mission, and uptime           |
| `!clear`                            | Delete prior bot messages                               |
| `!help`                             | Show this command list                                  |

---

## 🧠 Features

- Detects DCS server crashes via log monitoring
- Auto-restarts crashed servers
- Reports errors to Discord via webhook
- Tracks uptime and mission status
- Fully controlled with `DCSManage.ps1`

---

## 📜 License

MIT or internal use. Attribution appreciated if public.
