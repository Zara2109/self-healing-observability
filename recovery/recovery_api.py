
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import os
import subprocess
import threading
import time

app = Flask(__name__)

RECOVERY_TOKEN = os.environ.get("RECOVERY_TOKEN", "")
COOLDOWN_SECONDS = 120
last_recovery = 0
recovery_lock = threading.Lock()


@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.post("/recover")
def recover():
    global last_recovery

    if not RECOVERY_TOKEN:
        return jsonify({"error": "Recovery token is not configured"}), 503

    supplied_token = request.headers.get("X-Recovery-Token", "")
    if supplied_token != RECOVERY_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    if payload.get("alertname") != "ApplicationDown":
        return jsonify({"error": "Alert is not approved for recovery"}), 400

    with recovery_lock:
        now = time.monotonic()
        if now - last_recovery < COOLDOWN_SECONDS:
            return jsonify({"status": "cooldown", "message": "Recovery recently attempted"}), 429

        last_recovery = now
        print(jsonify({
            "status": "recovery_started",
            "alertname": "ApplicationDown",
            "time": datetime.now(timezone.utc).isoformat()
        }).get_data(as_text=True), flush=True)

        try:
            result = subprocess.run(
                ["ansible-playbook", "/workspace/recover-app.yml"],
                capture_output=True,
                text=True,
                timeout=90,
                check=False
            )
        except subprocess.TimeoutExpired:
            return jsonify({"status": "failed", "error": "Recovery timed out"}), 504

        print(result.stdout, flush=True)
        if result.stderr:
            print(result.stderr, flush=True)

        if result.returncode != 0:
            return jsonify({"status": "failed", "returncode": result.returncode}), 500

        return jsonify({"status": "recovery_completed"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
