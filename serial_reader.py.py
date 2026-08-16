import serial
import requests
import re

# --------------------------
# CHANGE THIS TO YOUR COM PORT
# --------------------------
ser = serial.Serial("COm20", 115200, timeout=1)

url = "http://127.0.0.1:5000/receive"


latest = {
    "temperature": 0,
    "bark_frequency": 0,
    "bark_amplitude": 0,
    "restlessness": 0,
    "risk_level": "SAFE",
    "latitude": 0,
    "longitude": 0
}


print("Reading ESP32...")

while True:

    try:
        line = ser.readline().decode(errors="ignore").strip()

        if not line:
            continue

        print(line)

        # ---------------- MICROPHONE AMPLITUDE ----------------

        if line.startswith("AMP="):
            latest["bark_amplitude"] = float(line.split("=")[1].strip())

        # ---------------- GPS ----------------

        if line.startswith("Latitude"):
            value = line.split(":")[1].strip()
            if value != "Waiting...":
                latest["latitude"] = float(value)

        elif line.startswith("Longitude"):
            value = line.split(":")[1].strip()
            if value != "Waiting...":
                latest["longitude"] = float(value)
            print(latest)

        # ---------------- RESTLESSNESS ----------------

        elif line.startswith("RS:"):
            latest["restlessness"] = float(line.split(":")[1].strip())

        # ---------------- BARK ----------------

        elif "BARK FREQUENCY" in line:
            m = re.search(r'(\d+)', line)
            if m:
                latest["bark_frequency"] = int(m.group(1))

        # ---------------- RISK ----------------

        rs = latest["restlessness"]

        if rs < 35:
            latest["risk_level"] = "SAFE"

        elif rs < 70:
            latest["risk_level"] = "MEDIUM"

        else:
            latest["risk_level"] = "HIGH"

        # ---------------- SEND ----------------

        requests.post(url, json=latest, timeout=1)
    except Exception as e:
        print(e)