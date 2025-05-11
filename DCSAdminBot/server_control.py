import subprocess
import psutil
from config_loader import load_config

config = load_config()

def control_dcs_instance(instance, action):
    info = config['SERVERS'].get(instance)
    if not info:
        return False
    try:
        result = subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", "scripts/DCSManage.ps1",
            "-Action", action,
            "-Target", info['name']
        ])
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def is_instance_running(name):
    for proc in psutil.process_iter(['name', 'cmdline']):
        if proc.info['name'] == "DCS_server.exe" and f"-w {name}" in " ".join(proc.info['cmdline']):
            return True
    return False
