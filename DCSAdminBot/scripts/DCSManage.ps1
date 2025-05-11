param (
    [string]$Action = "start",
    [string]$Target = "all"
)

# Define dynamic paths relative to this script
$BasePath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ConfigPath = Join-Path $BasePath "..\config\servers.json"
$ConfigJsonPath = Join-Path $BasePath "..\config\config.json"
$LogFile = Join-Path $BasePath "..\Logs\restart_log.txt"

# Load configs
$servers = (Get-Content $ConfigPath | ConvertFrom-Json).instances
$Config = Get-Content $ConfigJsonPath | ConvertFrom-Json
$WebhookUrl = $Config.discord_webhook

function Write-Log {
    param (
        [string]$Action,
        [string]$Target
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$timestamp] [$Action] $Target"
}

function Send-DiscordAlert {
    param (
        [string]$Message,
        [string]$WebhookUrl
    )
    try {
        $payload = @{ content = $Message } | ConvertTo-Json -Depth 1 -Compress
        $utf8Payload = [System.Text.Encoding]::UTF8.GetBytes($payload)
        Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body $utf8Payload -ContentType 'application/json; charset=utf-8'
        Write-Log "alert_sent" $Message
    } catch {
        Write-Log "alert_failed" $_
    }
}

function Sanitize-MissionScripting {
    foreach ($key in $servers.PSObject.Properties.Name) {
        $SavedGamesPath = "$env:USERPROFILE\Saved Games\$($servers.$key.name)\Scripts\MissionScripting.lua"
        if (Test-Path $SavedGamesPath) {
            $lines = Get-Content $SavedGamesPath
            $output = @()
            foreach ($line in $lines) {
                if ($line -match '^\s*sanitizeModule\(' -and $line -notmatch '^\s*--') {
                    $output += '--' + $line
                } else {
                    $output += $line
                }
            }
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $output += "-- Last sanitized: $timestamp"
            $output | Set-Content $SavedGamesPath -Force
            Write-Log "sanitized" $SavedGamesPath
        }
    }
}

function Minimize-DCSWindows {
    Start-Sleep -Seconds 10
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class WinAPI {
            [DllImport("user32.dll")]
            public static extern int ShowWindow(IntPtr hWnd, int nCmdShow);
        }
"@
    $DCSProcesses = Get-Process -Name "DCS_server" -ErrorAction SilentlyContinue
    foreach ($proc in $DCSProcesses) {
        $hWnd = $proc.MainWindowHandle
        if ($hWnd -ne [IntPtr]::Zero) {
            [WinAPI]::ShowWindow($hWnd, 6)  # 6 = Minimize
            Write-Log "minimized" $proc.Id
        }
    }
}

function Start-SingleDCS {
    param ([string]$key)
    $name = $servers.$key.name
    $exe = $servers.$key.exe
    if (-not (Test-Path $exe)) {
        Write-Log "exe_not_found" $exe
        return
    }
    try {
        Start-Process -FilePath $exe -ArgumentList "-w $name" -PassThru
        Start-Sleep -Seconds 5
        Minimize-DCSWindows
        Write-Log "started" $name
        Send-DiscordAlert "✅ $name started successfully." $WebhookUrl
    } catch {
        Write-Log "start_failed" $_
        Send-DiscordAlert "❌ Failed to start $name." $WebhookUrl
    }
}

function Stop-SingleDCS {
    param ([string]$key)
    $name = $servers.$key.name
    try {
        $processes = Get-CimInstance Win32_Process | Where-Object {
            $_.Name -eq "DCS_server.exe" -and $_.CommandLine -match "-w $name"
        }
        if ($processes) {
            $processes | ForEach-Object {
                Stop-Process -Id $_.ProcessId -Force
                Write-Log "stopped" $name
                Send-DiscordAlert "🛑 $name stopped." $WebhookUrl
            }
        } else {
            Write-Log "not_running" $name
            Send-DiscordAlert "⚠️ No running instance of $name found." $WebhookUrl
        }
    } catch {
        Write-Log "stop_failed" $_
        Send-DiscordAlert "❌ Failed to stop $name." $WebhookUrl
    }
}

function Restart-DCS {
    param ([string]$target = "all")
    $matchedKey = $servers.PSObject.Properties.Name | Where-Object {
        $servers.$_.name -eq $target
    }
    if (-not $matchedKey) {
        Write-Log "invalid_restart_target" $target
        Send-DiscordAlert "❌ Invalid instance name: $target" $WebhookUrl
        return
    }
    Stop-SingleDCS $matchedKey
    Start-Sleep -Seconds 5
    Start-SingleDCS $matchedKey
}

switch ($Action.ToLower()) {
    "start"   { Start-SingleDCS $Target }
    "stop"    { Stop-SingleDCS $Target }
    "restart" { Restart-DCS $Target }
    default   { Write-Log "unknown_action" $Action; exit 1 }
}
