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

LOG_FILE = config["log_path"]
JSON_FILE = config.get("json_path", "logs/latest.json")
CPU_LIMIT = config["cpu_limit"]
MEM_LIMIT = config["memory_limit"]
TEMP_LIMIT = config["temp_limit"]
GPU_LIMIT = config["gpu_limit"]
ROTATE = config["rotate_logs"]
MAX_SIZE_KB = config["max_log_size_kb"]
COLOR = config["enable_color_output"]

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# -----------------------------
# Functions
# -----------------------------
def rotate_logs_if_needed():
    if not ROTATE:
        return

    if os.path.exists(LOG_FILE):
        size_kb = os.path.getsize(LOG_FILE) / 1024
        if size_kb > MAX_SIZE_KB:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            os.rename(LOG_FILE, f"{LOG_FILE}.{ts}.old")


def get_temperature():
    try:
        import wmi
        w = wmi.WMI(namespace="root\\wbem")
        temps = w.MSAcpi_ThermalZoneTemperature()
        if temps:
            # Convert from tenths of Kelvin to Celsius
            return (temps[0].CurrentTemperature / 10.0) - 273.15
    except Exception:
        pass

    # Fallback: try psutil (works on Linux/Mac)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if "cpu" in name.lower() or "core" in name.lower():
                    return entries[0].current
    except Exception:
        pass

    return None

def colorize(value, limit):
    if not COLOR:
        return str(value)
    if value > limit:
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    if value > (limit * 0.8):
        return f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
    return f"{Fore.GREEN}{value}{Style.RESET_ALL}"

# -----------------------------
# Main Loop
# -----------------------------
print(f"{Fore.CYAN}Starting System Monitor... (Press Ctrl+C to stop){Style.RESET_ALL}")

try:
    while True:
        # 1. Collect Data
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        temp = get_temperature()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_temp = round(temp, 1) if temp is not None else None
        display_temp = safe_temp if safe_temp is not None else "N/A"

        # 2. Prepare Log Line
        gpu = get_gpu_info()
        gpu_name = gpu["gpu_name"]

        log_line = (
             f"{timestamp} | "
             f"CPU: {cpu}% | "
             f"MEM: {mem}% | "
             f"TEMP: {display_temp} C | "
             f"GPU: {gpu_name}\n"
        )

        # 3. Write to Log File
        rotate_logs_if_needed()
        with open(LOG_FILE, "a") as f:
            f.write(log_line)

        # 4. Write to JSON (For Dashboard)
        # Get GPU info
        gpu = get_gpu_info()

        dashboard_data = {
            "timestamp": timestamp,
            "cpu": cpu,
            "memory": mem,
            "temperature": display_temp,

            "gpu_name": gpu["gpu_name"],
            "gpu_status": gpu["status"],
            "gpu_usage": gpu["gpu_usage"],

            "cpu_alert": cpu > CPU_LIMIT,
            "mem_alert": mem > MEM_LIMIT,
            "temp_alert": safe_temp is not None and safe_temp > TEMP_LIMIT
        }

        with open(JSON_FILE, "w") as f:
            json.dump(dashboard_data, f)

        # 5. Print to Console
        print(f"{timestamp} | CPU: {colorize(cpu, CPU_LIMIT)}% | MEM: {colorize(mem, MEM_LIMIT)}% | TEMP: {colorize(safe_temp, TEMP_LIMIT) if safe_temp is not None else 'N/A'}C | GPU_INFO: {gpu['gpu_name']} | GPU_USAGE: {colorize(gpu['gpu_usage'], GPU_LIMIT) if gpu['gpu_usage'] is not None else 'N/A'}")

        # 6. Wait before next check (2 seconds)
        time.sleep(2)

except KeyboardInterrupt:
    print(f"\n{Fore.RED}Stopping monitor.{Style.RESET_ALL}")
