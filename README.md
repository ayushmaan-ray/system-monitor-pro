# 📊 System Monitor Pro

A professional-grade system monitoring tool that tracks CPU, Memory, GPU, and Temperature metrics in real-time. Features a background data collector and a modern web dashboard for visualization.

## 🚀 Features

- **Real-time Monitoring:** Tracks CPU usage, RAM usage, GPU usage, and CPU temperature.
- **Web Dashboard:** Modern, responsive UI with live updating charts (Chart.js).
- **REST API:** JSON endpoints for metrics (`/api/metrics`) and logs (`/api/logs`).
- **Alert System:** Color-coded visual indicators in terminal and dashboard when thresholds are breached.
- **GPU Support:** Detects and monitors Intel, NVIDIA, and AMD GPUs on Windows and Linux.
- **Logging:** Automated logging with file rotation to prevent disk overflow.
- **Cross-platform:** Works on Windows and Linux.

## 🛠️ Tech Stack

- **Python:** Core logic and data collection (`psutil`, `wmi` on Windows).
- **Flask:** Web server and API.
- **HTML/JS:** Frontend dashboard with `Chart.js`.
- **Bash/PowerShell:** Automation and service wrapping.

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ayushmaan-ray/system-monitor-pro.git
   cd system-monitor-pro
   ```

2. Create a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. *(Windows only)* Install WMI for temperature support:
   ```bash
   pip install wmi
   ```

## 🖥️ Usage

1. **Start the Monitor** (collects and logs data):
   ```bash
   # Windows
   python monitor.py

   # Linux
   ./monitor.sh
   ```

2. **Start the Dashboard** (in a separate terminal):
   ```bash
   python dashboard.py
   ```

3. **Open in Browser:** Go to [http://localhost:5000](http://localhost:5000)

## ⚙️ Configuration

Edit `config.json` to adjust thresholds and settings:

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

## 📝 Notes

- Temperature monitoring requires WMI on Windows. If your device's BIOS doesn't expose thermal data, temperature will display as `N/A` — this is expected behaviour on some machines.
- GPU usage is read via PowerShell's performance counters on Windows and `lspci` on Linux.

## 📁 Project Structure

```
system-monitor-pro/
├── monitor.py        # Data collection loop
├── dashboard.py      # Flask web server
├── gpu_monitor.py    # GPU detection and usage
├── config.json       # Thresholds and settings
├── requirements.txt  # Python dependencies
├── monitor.sh        # Linux startup script
└── templates/
    └── index.html    # Web dashboard UI
```