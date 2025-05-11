import os
import subprocess
import json
import re

DCS_MANAGE_PS1 = r"C:\DCSAdminBot\scripts\DCSManage.ps1"
SERVERS_JSON = r"C:\DCSAdminBot\config\servers.json"

def get_instance_name(key):
    try:
        with open(SERVERS_JSON, "r") as f:
            servers = json.load(f)
            return servers["instances"].get(key.lower(), {}).get("name", key)
    except Exception:
        return key

def get_upload_path():
    return os.path.join(os.environ["USERPROFILE"], "Saved Games", "Active Missions")

def update_mission_list(instance_name, miz_path):
    settings_path = os.path.join(
        os.environ["USERPROFILE"],
        "Saved Games",
        instance_name,
        "Config",
        "serverSettings.lua"
    )

    if not os.path.exists(settings_path):
        return False, f"❌ Could not find serverSettings.lua for `{instance_name}`"

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Normalize and double-escape for Lua
        normalized_path = os.path.normpath(miz_path)
        escaped_path = normalized_path.replace("\\", "\\\\\\\\")
        new_line = f'[1] = "{escaped_path}",'

        pattern = r'\[1\]\s*=\s*".*?"[,]?'
        if re.search(pattern, content):
            content = re.sub(pattern, new_line, content)
        else:
            content += f'\n["missionList"] = \n{{\n\t{new_line}\n}}, -- end of ["missionList"]\n'

        # DEBUG
        #print("DEBUG escaped_path:", repr(escaped_path))
        #print("DEBUG written content:\n", content)

        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True, "✅ missionList[1] updated"
    except Exception as e:
        return False, f"❌ Failed to update missionList: {e}"

def upload_and_load_mission(file_name, file_bytes, instance_key):
    instance_name = get_instance_name(instance_key)
    upload_path = get_upload_path()
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, file_name)

    with open(file_path, 'wb') as miz_file:
        miz_file.write(file_bytes)

    success, msg = update_mission_list(instance_name, file_path)
    if not success:
        return False, msg

    try:
        subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", DCS_MANAGE_PS1,
            "-Action", "restart",
            "-Target", instance_name
        ], check=True)

        return True, f"✅ Mission `{file_name}` uploaded, set as active, and `{instance_name}` restarted."
    except subprocess.CalledProcessError as e:
        return False, f"❌ PowerShell restart failed: {e}"
