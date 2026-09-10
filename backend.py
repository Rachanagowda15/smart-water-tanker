from flask import Flask, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import os

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

# Allow Vercel frontend to access Render backend
CORS(app)


# =========================================================
# MQTT SETTINGS
# =========================================================

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC = "smart_water_tanker/ruchitha"


# =========================================================
# DATABASE
# =========================================================

DATABASE = "smart_tanker.db"


# =========================================================
# LATEST SENSOR DATA
# =========================================================

latest_data = {
    "water_level": 0,
    "water_used": 0,
    "flow_rate": 0,
    "latitude": 0,
    "longitude": 0,
    "road_status": "UNKNOWN",
    "sprinkler": "OFF",
    "leakage": "NO",
    "timestamp": ""
}


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            water_level REAL,
            water_used REAL,
            flow_rate REAL,
            latitude REAL,
            longitude REAL,
            road_status TEXT,
            sprinkler TEXT,
            leakage TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

    print("Database initialized")


# =========================================================
# SAVE SENSOR DATA
# =========================================================

def save_data(data):

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensor_data
            (
                water_level,
                water_used,
                flow_rate,
                latitude,
                longitude,
                road_status,
                sprinkler,
                leakage,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            data.get("water_level", 0),

            data.get("water_used", 0),

            data.get("flow_rate", 0),

            data.get("latitude", 0),

            data.get("longitude", 0),

            data.get("road_status", "UNKNOWN"),

            data.get("sprinkler", "OFF"),

            data.get("leakage", "NO"),

            data.get(
                "timestamp",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        ))

        conn.commit()
        conn.close()

        print("Sensor data saved")

    except Exception as e:

        print("Database error:", e)


# =========================================================
# MQTT CONNECT
# =========================================================

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to HiveMQ MQTT broker")

        client.subscribe(TOPIC)

        print("Subscribed to:", TOPIC)

    else:

        print("MQTT connection failed. Code:", rc)


# =========================================================
# MQTT MESSAGE
# =========================================================

def on_message(client, userdata, msg):

    global latest_data

    try:

        payload = msg.payload.decode()

        print("----------------------------------")
        print("MQTT MESSAGE RECEIVED")
        print(payload)
        print("----------------------------------")

        data = json.loads(payload)

        # Update latest values
        latest_data.update(data)

        # Add timestamp if ESP32 does not send one
        if not latest_data.get("timestamp"):

            latest_data["timestamp"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # Save to SQLite
        save_data(latest_data)

    except json.JSONDecodeError:

        print("Invalid JSON received from ESP32")

    except Exception as e:

        print("MQTT message error:", e)


# =========================================================
# MQTT CLIENT
# =========================================================

mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


# =========================================================
# CONNECT MQTT
# =========================================================

try:

    mqtt_client.connect(
        BROKER,
        PORT,
        60
    )

    mqtt_client.loop_start()

    print("MQTT client started")

except Exception as e:

    print("MQTT connection error:", e)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "project": "Smart Water Tanker",
        "status": "Backend is running",
        "mqtt": "HiveMQ",
        "message": "Flask backend connected successfully"
    })


# =========================================================
# TEST
# =========================================================

@app.route("/test")
def test():

    return "Smart Water Tanker Flask Backend is working!"


# =========================================================
# LIVE DATA
# =========================================================

@app.route("/data")
def get_data():

    return jsonify(latest_data)


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def get_history():

    try:

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()

        conn.close()

        history = []

        for row in rows:

            history.append(dict(row))

        return jsonify(history)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# DATABASE COUNT
# =========================================================

@app.route("/database_count")
def database_count():

    try:

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM sensor_data
        """)

        count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "count": count
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

init_db()


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )