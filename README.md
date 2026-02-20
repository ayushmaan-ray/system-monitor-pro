# 🛡️ Security Monitor Pro

A professional-grade **host-based security monitoring tool** that tracks system performance, detects suspicious processes, and provides real-time threat alerts through a modern SOC-style web dashboard.

> Built with Python, Flask, and Chart.js — runs on Windows and Linux.

---

## 🚀 Features

### 🔍 Security & Threat Detection
- **Suspicious Process Detection** — identifies known malicious process signatures (reverse shells, crypto miners, RATs)
- **Behavioral Analysis** — flags processes with abnormally high CPU or memory consumption
- **Alert Engine** — real-time alerts with severity levels: `CRITICAL`, `WARNING`, `INFO`
- **Process Whitelisting** — reduces false positives by ignoring known safe system processes

### 📊 System Monitoring
- **Real-time Metrics** — CPU usage, RAM usage, CPU temperature, GPU utilization
- **Top Process Tables** — live view of top 5 memory and CPU consumers with visual bars
- **GPU Detection** — supports NVIDIA, AMD, and Intel GPUs (prefers dedicated GPU on dual-GPU systems)
- **Automated Log Rotation** — prevents disk overflow with configurable size limits

### 🖥️ Web Dashboard
- **SOC-style UI** — terminal-aesthetic dark dashboard built with Chart.js
- **Live Performance Timeline** — rolling 20-reading CPU and memory graph
- **Security Alerts Panel** — color-coded alerts (red = CRITICAL, amber = WARNING, blue = INFO)
- **REST API** — JSON endpoints for metrics, alerts, and logs

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Collection | Python, `psutil` |
| GPU Monitoring | PowerShell (Windows), `lspci` (Linux) |
| Web Server | Flask |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Logging | Python `logging` with rotation |
| Config | JSON |
| Automation | Bash / PowerShell |

---

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayushmaan-ray/system-monitor-pro.git
   cd system-monitor-pro
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Usage

Run both components in **separate terminals**:

**Terminal 1 — Start the monitor (data collector + alert engine):**
```bash
# Windows
python monitor.py

# Linux
./monitor.sh
```

**Terminal 2 — Start the web dashboard:**
```bash
python dashboard.py
```

**Open in browser:** [http://localhost:5000](http://localhost:5000)

---

## ⚙️ Configuration

Edit `config.json` to adjust thresholds:

```json
{
  "cpu_limit": 80,
  "memory_limit": 75,
  "temp_limit": 70,
  "gpu_limit": 50,
  "log_path": "logs/system.log",
  "json_path": "logs/latest.json",
  "max_log_size_kb": 500,
  "rotate_logs": true,
  "enable_color_output": true
}
```

| Field | Description |
|---|---|
| `cpu_limit` | CPU % threshold before WARNING alert |
| `memory_limit` | RAM % threshold before WARNING alert |
| `temp_limit` | Temperature (°C) threshold before CRITICAL alert |
| `max_log_size_kb` | Max log file size before rotation |

---

## 🔐 Detection Logic

### Suspicious Process Detection
The monitor maintains a signature list of known malicious process names:
```
nc.exe, ncat.exe, xmrig.exe, mimikatz.exe, meterpreter.exe, cobaltstrike.exe ...
```
Any process matching these signatures triggers a `CRITICAL` alert immediately.

### Behavioral Detection
Processes are also flagged by behavior:
- **High CPU** — any process exceeding the configured `CPU_PROCESS_LIMIT` threshold
- **High Memory** — any process exceeding the configured `MEM_PROCESS_LIMIT` (MB)
- **Whitelisted** — known safe Windows/Linux system processes are excluded to reduce noise

### Alert Severity Levels
| Level | Color | Trigger |
|---|---|---|
| `CRITICAL` | 🔴 Red | Malicious process signature match |
| `WARNING` | 🟡 Amber | High resource usage, threshold breach |
| `INFO` | 🔵 Blue | System events (GPU detected, etc.) |

---

## 📁 Project Structure

```
system-monitor-pro/
├── monitor.py          # Core loop: data collection + alert engine + process detection
├── dashboard.py        # Flask web server + REST API
├── gpu_monitor.py      # GPU detection (NVIDIA/AMD/Intel, Windows + Linux)
├── config.json         # Thresholds and settings
├── requirements.txt    # Python dependencies
├── monitor.sh          # Linux startup script
├── logs/
│   ├── system.log      # Auto-generated log file (with rotation)
│   └── latest.json     # Latest metrics snapshot for dashboard
└── templates/
    └── index.html      # SOC-style web dashboard UI
```

---

## 📝 Notes

- **Temperature** — requires WMI on Windows. If your BIOS doesn't expose thermal sensors, temperature shows as `0°C`. This is expected on some machines and is not an error.
- **GPU Usage** — read via PowerShell performance counters on Windows. On dual-GPU systems (integrated + dedicated), the dedicated GPU is preferred automatically.
- **First cycle** — CPU process readings may show `0%` on the very first cycle. This is normal — psutil needs two readings to calculate CPU usage. Values stabilize from the second cycle onward.
- **Logs folder** — created automatically on first run. Do not delete `latest.json` while the dashboard is running.

---

## 🔮 Roadmap

- [ ] Network connection monitoring (detect suspicious outbound connections)
- [ ] File Integrity Monitoring (detect unauthorized file changes)
- [ ] Historical data charts (trends over time)
- [ ] Email / desktop notification alerts
- [ ] Linux systemd service packaging