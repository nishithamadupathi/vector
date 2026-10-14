
from flask import Flask, jsonify, request
from datetime import datetime
import random

app = Flask(__name__)

reading_history = []

# Demo thresholds only; adjust for the species and farming conditions.
THRESHOLDS = {
    "oxygen_min": 5.0,
    "ph_min": 6.5,
    "ph_max": 8.5,
    "temperature_max": 30.0
}


def generate_readings(scenario="normal"):
    """Generate simulated readings for the demo."""

    readings = {
        "temperature": round(random.uniform(26, 29), 1),
        "ph": round(random.uniform(7.0, 8.0), 2),
        "oxygen": round(random.uniform(6.0, 8.0), 1),
        "turbidity": round(random.uniform(10, 60), 1),
        "ammonia": round(random.uniform(0.005, 0.05), 3)
    }

    # Reproducible demo scenarios
    if scenario == "low_oxygen":
        readings["oxygen"] = 3.5

    elif scenario == "abnormal_ph":
        readings["ph"] = 9.0

    elif scenario == "high_temperature":
        readings["temperature"] = 32.0

    elif scenario == "multiple_risks":
        readings["oxygen"] = 3.0
        readings["ph"] = 9.0
        readings["temperature"] = 32.0

    return readings


def assess_risk(readings):
    """Apply transparent rule-based demo thresholds."""

    alerts = []

    if readings["oxygen"] < THRESHOLDS["oxygen_min"]:
        alerts.append({
            "parameter": "Dissolved oxygen",
            "value": readings["oxygen"],
            "message": "Low dissolved oxygen",
            "action": "Check aeration and verify the reading."
        })

    if not (
        THRESHOLDS["ph_min"]
        <= readings["ph"]
        <= THRESHOLDS["ph_max"]
    ):
        alerts.append({
            "parameter": "pH",
            "value": readings["ph"],
            "message": "pH outside demo range",
            "action": "Verify the reading and seek aquaculture guidance."
        })

    if readings["temperature"] > THRESHOLDS["temperature_max"]:
        alerts.append({
            "parameter": "Temperature",
            "value": readings["temperature"],
            "message": "High water temperature",
            "action": "Recheck the measurement and assess pond conditions."
        })

    status = "Warning" if alerts else "Normal"

    if len(alerts) >= 3:
        status = "Critical"

    return status, alerts


@app.route("/")
def home():
    return jsonify({
        "project": "AquaDrone",
        "message": "Backend is running",
        "data_source": "Simulated data"
    })


@app.route("/api/readings")
def get_readings():
    scenario = request.args.get("scenario", "normal")

    allowed_scenarios = {
        "normal",
        "low_oxygen",
        "abnormal_ph",
        "high_temperature",
        "multiple_risks"
    }

    if scenario not in allowed_scenarios:
        return jsonify({
            "error": "Unknown scenario",
            "allowed_scenarios": sorted(allowed_scenarios)
        }), 400

    readings = generate_readings(scenario)
    status, alerts = assess_risk(readings)

    result = {
        **readings,
        "time": datetime.now().isoformat(timespec="seconds"),
        "source": "Simulated data",
        "scenario": scenario,
        "status": status,
        "alerts": alerts
    }

    reading_history.append(result)

    # Keep only the latest 50 readings
    if len(reading_history) > 50:
        reading_history.pop(0)

    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "project": "AquaDrone",
        "data_source": "Simulated data"
    })

@app.route("/api/history")
def get_history():
    return jsonify(reading_history)

if __name__ == "__main__":
    app.run(debug=True)
