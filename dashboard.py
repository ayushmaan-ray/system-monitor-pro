from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Path to the JSON file created by monitor.py
JSON_FILE = "logs/latest.json"
LOG_FILE = "logs/system.log"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/metrics')
def metrics():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
            return jsonify(data)
        except:
            return jsonify({"error": "Error reading data"}), 500
    else:
        return jsonify({
            "timestamp": "Waiting...",
            "cpu": 0,
            "memory": 0,
            "temperature": 0,
            "gpu_name": "Unknown",
            "gpu_status": "unknown",
            "gpu_usage": None
        })

@app.route('/api/logs')
def logs():
    # Return last 10 lines of logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return jsonify(lines[-10:])
    return jsonify([])

if __name__ == '__main__':
    # Listen on all interfaces so you can view it from Windows
    app.run(host='0.0.0.0', port=5000, debug=True)
