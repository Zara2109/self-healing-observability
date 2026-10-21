
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import json
import os
import requests

app = Flask(__name__)

RECOVERY_TOKEN = os.environ.get("RECOVERY_TOKEN", "")
RECOVERY_URL = os.environ.get(
    "RECOVERY_URL",
    "http://recovery:5002/recover"
)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/alerts", methods=["POST"])
def receive_alerts():
    payload = request.get_json(silent=True) or {}
    alerts = payload.get("alerts", [])

    print(json.dumps({
        "received_at": datetime.now(timezone.utc).isoformat(),
        "receiver": payload.get("receiver"),
        "status": payload.get("status"),
        "alerts": alerts
    }), flush=True)

    recovery_results = []

    for alert in alerts:
        labels = alert.get("labels", {})

        if (
            alert.get("status") == "firing"
            and labels.get("alertname") == "ApplicationDown"
        ):
            if not RECOVERY_TOKEN:
                print("Recovery skipped: token is not configured.", flush=True)
                recovery_results.append({"status": "skipped"})
                continue

            try:
                response = requests.post(
                    RECOVERY_URL,
                    json={"alertname": "ApplicationDown"},
                    headers={"X-Recovery-Token": RECOVERY_TOKEN},
                    timeout=100
                )

                print(json.dumps({
                    "event": "recovery_response",
                    "http_status": response.status_code,
                    "response": response.text
                }), flush=True)

                recovery_results.append({
                    "status": "requested",
                    "http_status": response.status_code
                })

            except requests.RequestException as exc:
                print(
                    f"Recovery request failed: {type(exc).__name__}",
                    flush=True
                )
                recovery_results.append({"status": "request_failed"})

    return jsonify({
        "status": "received",
        "recovery_results": recovery_results
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
