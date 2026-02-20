#!/usr/bin/env python3
import psutil
import json
import datetime
import os
import sys
import time
from colorama import Fore, Style, init
from gpu_monitor import get_gpu_info

# Initialize colorama
init(autoreset=True)

# -----------------------------
# Load config
# -----------------------------
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading config.json: {e}")
    sys.exit(1)

# Read check up values
LOG_FILE = config["log_path"]
JSON_FILE = config.get("json_path", "logs/latest.json")

CPU_LIMIT = config["cpu_limit"]
MEM_LIMIT = config["memory_limit"]
TEMP_LIMIT = config["temp_limit"]

ROTATE = config["rotate_logs"]
MAX_SIZE_KB = config["max_log_size_kb"]

COLOR = config["enable_color_output"]

# Process Limit for security check
CPU_PROCESS_LIMIT = config.get("cpu_process_limit", 20)
MEM_PROCESS_LIMIT = config.get("mem_process_limit_mb", 300)

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Suspicious process names (basic threat signatures)
SUSPICIOUS_PROCESSES = [
    "nc.exe",
    "ncat.exe",
    "xmrig.exe",
    "cryptominer.exe",
    "meterpreter.exe",
    "mimikatz.exe",
    "cobaltstrike.exe"
]

# Processes that are suspicious ONLY if they have network connections
SUSPICIOUS_WITH_NETWORK = [
    "powershell",
    "cmd",
    "wscript",
    "cscript",
    "regsvr32",
    "mshta"
]

# Remove generic Windows processes from simple name-match
# Always ignore these (system/known safe)
PROCESS_WHITELIST = [
    "system idle process",
    "system",
    "registry",
    "memcompression",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "dwm.exe",
    "explorer.exe",
    "shellexperiencehost.exe",
    "startmenuexperiencehost.exe",
    "phonexperiencehost.exe",
    "shellhost.exe",
    "openconsole.exe",
    "dashost.exe",
    "adobecollabsync.exe",
    "msmpeng.exe",    # Windows Defender
    "searchhost.exe",
    "runtimebroker.exe",
    "taskhostw.exe",
    "fontdrvhost.exe",
    "audiodg.exe",
    "spoolsv.exe",
    "searchindexer.exe",
]

# -----------------------------
# Alert Engine
# -----------------------------
def generate_alert(alert_type, level, message):
    return {
        "type": alert_type,
        "level": level,
        "message": message,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def check_alerts(cpu, mem, temp, gpu):
    alerts = []

    if cpu > CPU_LIMIT:
        alerts.append(generate_alert(
            "CPU",
            "WARNING",
            f"High CPU usage: {cpu}%"
        ))

    if mem > MEM_LIMIT:
        alerts.append(generate_alert(
            "MEMORY",
            "WARNING",
            f"High Memory usage: {mem}%"
        ))

    if temp is not None and temp > TEMP_LIMIT:
        alerts.append(generate_alert(
            "TEMPERATURE",
            "CRITICAL",
            f"High Temperature: {temp}C"
        ))

    if gpu["status"] == "detected":
        alerts.append(generate_alert(
            "GPU",
            "INFO",
            f"GPU detected: {gpu['gpu_name']}"
        ))

    return alerts


# -----------------------------
# Log Rotation
# -----------------------------
def rotate_logs_if_needed():
    if not ROTATE:
        return

    if os.path.exists(LOG_FILE):
        size_kb = os.path.getsize(LOG_FILE) / 1024
        if size_kb > MAX_SIZE_KB:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            os.rename(LOG_FILE, f"{LOG_FILE}.{ts}.old")


# -----------------------------
# Temperature
# -----------------------------
def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None

        for name, entries in temps.items():
            if "cpu" in name.lower() or "core" in name.lower():
                return entries[0].current

        return list(temps.values())[0][0].current

    except:
        return None


# -----------------------------
# Activity Detection
# -----------------------------
# Global dictionary to track previous CPU readings
# Track already-alerted PIDs to avoid duplicates
process_cpu_cache = {}
_alerted_pids = set()

def detect_suspicious_processes():
    alerts = []
    seen_pids = set()

    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cmdline']):
        try:
            pid = proc.pid
            name = proc.info['name'] or "unknown"
            name_lower = name.lower()

            # Skip whitelisted processes
            if name_lower in PROCESS_WHITELIST:
                continue

            # Skip duplicates
            if pid in seen_pids:
                continue
            seen_pids.add(pid)

            mem = proc.info['memory_info'].rss / (1024 * 1024)

            # CPU tracking
            if pid not in process_cpu_cache:
                process_cpu_cache[pid] = proc.cpu_percent(interval=None)
                continue

            cpu = proc.cpu_percent(interval=None)

            # Direct suspicious name match
            for bad in SUSPICIOUS_PROCESSES:
                if bad in name_lower:
                    alerts.append({
                        "type": "PROCESS",
                        "level": "CRITICAL",
                        "message": f"Known malicious process detected: {name} (PID {pid})"
                    })

            # CPU threshold (skip System Idle Process via Whitelist)
            if cpu > CPU_PROCESS_LIMIT and name_lower not in PROCESS_WHITELIST:
                alerts.append({
                    "type": "PROCESS",
                    "level": "WARNING",
                    "message": f"High CPU process: {name} using {cpu:.1f}% CPU (PID {pid})"
                })

            # Memory threshold
            if mem > MEM_PROCESS_LIMIT:
                alerts.append({
                    "type": "PROCESS",
                    "level": "WARNING",
                    "message": f"High Memory process: {name} using {mem:.1f} MB (PID {pid})"
                })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return alerts


def get_top_processes(limit=5):
    """Get top processes using cached CPU values (accurate, non-blocking)"""
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            pid  = proc.pid
            name = proc.info['name'] or 'unknown'
            mem  = proc.info['memory_info'].rss / (1024 * 1024)
            cpu  = process_cpu_cache.get(pid, 0)  # ← reuse existing cache

            processes.append({
                'pid':    pid,
                'name':   name,
                'cpu':    cpu,
                'memory': mem
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_memory = sorted(processes, key=lambda x: x['memory'], reverse=True)[:limit]
    top_cpu    = sorted(processes, key=lambda x: x['cpu'],    reverse=True)[:limit]

    return {'top_memory': top_memory, 'top_cpu': top_cpu}


# -----------------------------
# Console coloring
# -----------------------------
def colorize(value, limit):
    if not COLOR:
        return str(value)
    if value > limit:
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    if value > limit * 0.8:
        return f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
    return f"{Fore.GREEN}{value}{Style.RESET_ALL}"

# -----------------------------
# Main Loop
# -----------------------------
print(f"{Fore.CYAN}Starting System Monitor with Alert Engine...{Style.RESET_ALL}")

# Warms up CPU percent cache for all processes
for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except:
        pass

time.sleep(1)  # Collect baseline readings

try:
    while True:

        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        temp = get_temperature()
        gpu = get_gpu_info()
        safe_temp = temp if temp is not None else 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # System-level alerts (basic cpu, memo, temp and gpu)
        alerts = check_alerts(cpu, mem, temp, gpu)

        # Process-level alerts (suspicious files)
        process_alerts = detect_suspicious_processes()
        for alert in process_alerts:
            alert["timestamp"] = timestamp
            alerts.append(alert)

        # -------------------------
        # Write log file
        # -------------------------
        rotate_logs_if_needed()

        log_line = f"{timestamp} | CPU:{cpu}% MEM:{mem}% TEMP:{safe_temp}C GPU:{gpu['gpu_name']}\n"

        with open(LOG_FILE, "a") as f:
            f.write(log_line)

            for alert in alerts:
                f.write(f"[ALERT] {alert['level']} {alert['type']} - {alert['message']}\n")

        # Get top processes
        top_procs = get_top_processes(5)

        # -------------------------
        # JSON write (Dashboard)
        # -------------------------
        dashboard_data = {

            "timestamp": timestamp,

            "cpu": cpu,
            "memory": mem,
            "temperature": safe_temp,

            "gpu_name": gpu["gpu_name"],
            "gpu_status": gpu["status"],
            "gpu_usage": gpu.get("usage"),

            "top_processes": top_procs,

            "alerts": alerts

        }

        with open(JSON_FILE, "w") as f:
            json.dump(dashboard_data, f, indent=4)


        # -------------------------
        # Console output
        # -------------------------
        print(f"{timestamp} | CPU:{colorize(cpu,CPU_LIMIT)}% MEM:{colorize(mem,MEM_LIMIT)}% TEMP:{colorize(safe_temp,TEMP_LIMIT)}C GPU:{gpu['gpu_name']}")

        for alert in alerts:
            print(f"{Fore.RED}[ALERT] {alert['level']} - {alert['message']}{Style.RESET_ALL}")

        time.sleep(2)

except KeyboardInterrupt:
    print(f"\n{Fore.RED}Monitor stopped.{Style.RESET_ALL}")
