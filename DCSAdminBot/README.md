# DCS Admin Bot

This Discord bot allows you to start, stop, and reboot multiple DCS World server instances using Discord commands.

## 🚀 Features
- Command-based control via Discord
- Reboot individual instances or the entire system
- Tracks logs and restarts servers on fatal errors

## 🔧 Setup Instructions

1. Clone this repo
2. Create a `.env` file using the `.env.example`
3. Edit `config/servers.json` to match your server paths
4. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the bot:
   ```
   python admin_bot.py
   ```

## 📄 Commands
- `!start <server>`
- `!stop <server>`
- `!reboot <server|windows>`
- `!status`
- `!clear`
- `!help`
