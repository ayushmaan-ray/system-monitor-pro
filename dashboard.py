from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

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
    return jsonify({})


@app.route('/api/alerts')
def alerts():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data.get("alerts", []))

    return jsonify([])


@app.route('/api/logs')
def logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return jsonify(lines[-20:])

    return jsonify([])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
